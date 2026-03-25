"""
SciNet Data Overview — Figure Generator
========================================
Run from the public/ directory:
    python generate_figures.py

Outputs 19 PNG figures to figures/
Reads public data from data/ and private data from ../data/
"""

import json
import os
import re
import unicodedata
import warnings
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")

# ── Paths ──────────────────────────────────────────────────────────────────────
HERE = Path(__file__).parent
PUB  = HERE / "data"
PRIV = HERE / ".." / "data"
OUT  = HERE / "figures"
OUT.mkdir(exist_ok=True)

# ── Colour palette ─────────────────────────────────────────────────────────────
LABLUE      = "#113563"
NEWBLUE     = "#2A65AB"
LALIGHTBLUE = "#4595F3"
GRAY1       = "#444441"
GRAY2       = "#666663"
GRAY3       = "#EDEDEA"

DOMAIN_COLORS = {
    "Social Sciences":   LALIGHTBLUE,
    "Life Sciences":     NEWBLUE,
    "Physical Sciences": LABLUE,
    "Health Sciences":   "#5B8FD4",
    "Arts & Humanities": "#9A6B57",
}

CATEGORY_SHORT = {
    "Reading & Knowledge Acquisition":      "Reading & Knowledge",
    "Ideation & Hypothesis Generation": "Ideation & Hypotheses",
    "Data Gathering":                   "Data Gathering",
    "Data Analysis":                    "Data Analysis",
    "Writing & Communication":          "Writing & Communication",
    "Peer Review & Service":            "Peer Review",
    "Mentorship & Teaching":            "Mentorship & Teaching",
    "Administration":                 "Administration",
}

# ── Shared style ───────────────────────────────────────────────────────────────
plt.rcParams.update({
    "font.family":      "sans-serif",
    "font.size":        11,
    "axes.spines.top":  False,
    "axes.spines.right":False,
    "axes.grid":        True,
    "axes.grid.axis":   "x",
    "grid.color":       GRAY3,
    "grid.linewidth":   0.8,
    "figure.dpi":       150,
})


def save(fig, name):
    fig.savefig(OUT / name, bbox_inches="tight", dpi=150)
    plt.close(fig)
    print(f"  saved: figures/{name}")


def save_loose(fig, name):
    fig.savefig(OUT / name, dpi=150)
    plt.close(fig)
    print(f"  saved: figures/{name}")


COUNTRY_NAME_OVERRIDES = {
    "united states of america": "united states",
    "republic of korea": "south korea",
    "korea republic of": "south korea",
    "democratic peoples republic of korea": "north korea",
    "democratic people s republic of korea": "north korea",
    "korea democratic peoples republic of": "north korea",
    "korea democratic people s republic of": "north korea",
    "russian federation": "russia",
    "viet nam": "vietnam",
    "iran islamic republic of": "iran",
    "syrian arab republic": "syria",
    "taiwan province of china": "taiwan",
    "czech republic": "czechia",
    "united kingdom of great britain and northern ireland": "united kingdom",
    "netherlands": "the netherlands",
    "congo": "republic of the congo",
    "bolivia plurinational state of": "bolivia",
    "brunei darussalam": "brunei",
    "cote d ivoire": "ivory coast",
    "lao peoples democratic republic": "laos",
    "lao people s democratic republic": "laos",
    "micronesia federated states of": "micronesia",
    "moldova republic of": "moldova",
    "palestine state of": "palestinian territory",
    "tanzania united republic of": "tanzania",
    "timor leste": "timor leste",
    "virgin islands british": "british virgin islands",
    "virgin islands u s": "u s virgin islands",
    "sint maarten dutch part": "sint maarten",
}

OPENALEX_COUNTRY_CODE_OVERRIDES = {
    "Namibia": "NA",
}

COUNTRY_DISPLAY_OVERRIDES = {
    "United States of America": "United States",
    "Korea, Republic of": "Korea",
    "Taiwan, Province of China": "Taiwan",
    "United Kingdom of Great Britain and Northern Ireland": "United Kingdom",
    "Palestine, State of": "Palestine",
    "Moldova, Republic of": "Moldova",
    "Tanzania, United Republic of": "Tanzania",
    "Viet Nam": "Vietnam",
    "Russian Federation": "Russia",
}

LOGLOG_LABEL_CODES = ["US", "GB", "DE", "FR", "IL", "CA", "JP", "KR", "TW", "CH", "AU"]

LOGLOG_LABEL_OFFSETS = {
    "US": (1.05, 0.96),
    "GB": (0.92, 1.06),
    "DE": (0.88, 0.95),
    "FR": (0.90, 1.10),
    "IL": (1.06, 1.10),
    "CA": (1.05, 1.02),
    "JP": (0.90, 0.92),
    "KR": (1.04, 0.94),
    "TW": (1.04, 1.10),
    "CH": (0.98, 1.08),
    "AU": (0.90, 1.02),
}

# OpenAlex currently lacks separate rows for these small territories in
# ai_rankings_country.csv. Keep the exceptions explicit so new crosswalk gaps do
# not slip through silently.
KNOWN_OPENALEX_COUNTRY_GAPS = {
    "comoros",
    "marshall islands",
    "nauru",
    "saint martin",
}


def normalize_country_name(name):
    if pd.isna(name):
        return None

    text = unicodedata.normalize("NFKD", str(name))
    text = text.encode("ascii", "ignore").decode("ascii").lower().strip()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return COUNTRY_NAME_OVERRIDES.get(text, text)


def load_claude_science_country_data():
    anthropic_file = PRIV / "anthropic" / "aei_enriched_claude_ai_2025-08-04_to_2025-08-11.csv"
    aei = pd.read_csv(anthropic_file)
    country = aei[(aei["geography"] == "country") & (aei["facet"] == "country")].copy()

    def get_var(var):
        return (country[country["variable"] == var][["geo_id", "geo_name", "value"]]
                .rename(columns={"value": var}))

    claude_idx = get_var("usage_per_capita_index")
    pop = get_var("working_age_pop")[["geo_id", "working_age_pop"]]
    gdp = get_var("gdp_per_working_age_capita")[["geo_id", "gdp_per_working_age_capita"]]

    claude = claude_idx.merge(pop, on="geo_id", how="left")
    claude = claude.merge(gdp, on="geo_id", how="left")
    claude.columns = [
        "iso3",
        "claude_name",
        "claude_index",
        "working_age_pop",
        "gdp_per_working_age_capita",
    ]
    claude["name_key"] = claude["claude_name"].map(normalize_country_name)

    oa = pd.read_csv(PRIV / "openalex" / "field_stats" / "ai_rankings_country.csv")
    oa["country_code"] = oa["country_code"].fillna(
        oa["country_name"].map(OPENALEX_COUNTRY_CODE_OVERRIDES)
    )
    oa["name_key"] = oa["country_name"].map(normalize_country_name)

    df = claude.merge(oa, on="name_key", how="left")

    unmatched = sorted(set(df.loc[df["paper_count"].isna(), "name_key"].dropna()))
    unexpected = sorted(set(unmatched) - KNOWN_OPENALEX_COUNTRY_GAPS)
    if unexpected:
        raise ValueError(
            "Unexpected Anthropic/OpenAlex country mismatches: "
            + ", ".join(unexpected)
        )

    df = df[df["paper_count"].notna()].copy()
    df["papers_per_capita"] = df["paper_count"] / df["working_age_pop"] * 1000
    df["ai_papers_per_capita"] = df["ai_paper_count"] / df["working_age_pop"] * 1000
    return df


def country_bubble_sizes(paper_count):
    sizes = (np.log10(paper_count) - 2) ** 2 * 30
    return sizes.clip(lower=10)


def add_country_bubble_legend(ax, examples=None, title="Paper count", color=LABLUE):
    if examples is None:
        examples = [(5000, "5k papers"), (50000, "50k"), (500000, "500k")]

    for papers, label in examples:
        s = (np.log10(papers) - 2) ** 2 * 30
        ax.scatter([], [], s=max(s, 10), c=color, alpha=0.55,
                   edgecolors=color, label=label)
    ax.legend(title=title, title_fontsize=8, fontsize=8,
              loc="upper left", framealpha=0.8)


def add_country_labels(ax, df, x_col, y_col):
    from adjustText import adjust_text

    texts = []
    for _, row in df.iterrows():
        is_us = row["country_code"] == "US"
        label = COUNTRY_DISPLAY_OVERRIDES.get(row["country_name"], row["country_name"])
        t = ax.text(
            row[x_col],
            row[y_col],
            label,
            fontsize=8.5 if is_us else 7.5,
            fontweight="bold" if is_us else "normal",
            color=GRAY1,
        )
        texts.append(t)

    adjust_text(texts, ax=ax,
                arrowprops=dict(arrowstyle="-", color=GRAY2, lw=0.6),
                expand=(1.3, 1.5), force_text=(0.4, 0.6),
                only_move={"text": "xy", "points": "y"})


def add_country_labels_simple(ax, df, x_col, y_col):
    for _, row in df.iterrows():
        is_us = row["country_code"] == "US"
        label = COUNTRY_DISPLAY_OVERRIDES.get(row["country_name"], row["country_name"])
        ax.text(
            row[x_col] * 1.03,
            row[y_col] * 1.03,
            label,
            fontsize=8.5 if is_us else 7.5,
            fontweight="bold" if is_us else "normal",
            color=GRAY1,
        )


def add_country_labels_loglog(ax, df, x_col, y_col):
    labels = df[df["country_code"].isin(LOGLOG_LABEL_CODES)].copy()
    for _, row in labels.iterrows():
        is_us = row["country_code"] == "US"
        label = COUNTRY_DISPLAY_OVERRIDES.get(row["country_name"], row["country_name"])
        dx, dy = LOGLOG_LABEL_OFFSETS.get(row["country_code"], (1.03, 1.03))
        ax.text(
            row[x_col] * dx,
            row[y_col] * dy,
            label,
            fontsize=8.5 if is_us else 7.5,
            fontweight="bold" if is_us else "normal",
            color=GRAY1,
        )


# Mapping from SciNet display field → research domain
FIELD_TO_DOMAIN = {
    "Anthropology":               "Social Sciences",
    "Business & Management":      "Social Sciences",
    "Communication & Media Studies": "Social Sciences",
    "Economics":                  "Social Sciences",
    "Education":                  "Social Sciences",
    "Geography":                  "Social Sciences",
    "Law":                        "Social Sciences",
    "Political Science":          "Social Sciences",
    "Psychology":                 "Social Sciences",
    "Sociology":                  "Social Sciences",
    "Statistics":                 "Social Sciences",
    "Agricultural Sciences":      "Life Sciences",
    "Biology":                    "Life Sciences",
    "Biomedical Sciences":        "Life Sciences",
    "Neuroscience":               "Life Sciences",
    "Chemistry":                  "Physical Sciences",
    "Computer Science":           "Physical Sciences",
    "Earth & Planetary Sciences": "Physical Sciences",
    "Engineering":                "Physical Sciences",
    "Environmental Science":      "Physical Sciences",
    "Materials Science":          "Physical Sciences",
    "Mathematics":                "Physical Sciences",
    "Physics & Astronomy":        "Physical Sciences",
    "Medicine & Clinical Sciences": "Health Sciences",
    "Arts":                       "Arts & Humanities",
    "History":                    "Arts & Humanities",
    "Languages & Linguistics":    "Arts & Humanities",
    "Literature":                 "Arts & Humanities",
    "Philosophy":                 "Arts & Humanities",
    "Religion":                   "Arts & Humanities",
}

DISPLAY_DOMAIN_ORDER = [
    "Social Sciences",
    "Life Sciences",
    "Physical Sciences",
    "Health Sciences",
    "Arts & Humanities",
]


def load_topic_mapping():
    mapping = pd.read_csv(PUB / "openalex_topic_subfield_mapping.csv")
    mapping["topic_id"] = mapping["topic_id"].astype(str)
    if "domain" not in mapping.columns:
        mapping["domain"] = mapping["field"].map(FIELD_TO_DOMAIN)
    return mapping


def load_subfield_domain_map():
    mapping = load_topic_mapping()
    return (
        mapping[["subfield", "field", "domain"]]
        .dropna(subset=["subfield", "field", "domain"])
        .drop_duplicates()
        .sort_values(["subfield", "field"])
        .drop_duplicates(subset=["subfield"], keep="first")
        .rename(
            columns={
                "subfield": "subfield_name",
                "field": "field_name",
                "domain": "domain_name",
            }
        )
    )

# ══════════════════════════════════════════════════════════════════════════════
# 1. Tasks by domain
# ══════════════════════════════════════════════════════════════════════════════
def fig_tasks_by_domain():
    df = pd.read_csv(PUB / "tasks.csv")

    # Derive domain for every task:
    #   - domain-level tasks already have `domain` filled
    #   - subfield-level tasks have `field` filled; derive domain via lookup
    #   - universal tasks are excluded (they belong to all domains)
    def get_domain(row):
        if pd.notna(row["domain"]) and row["domain"] != "":
            return row["domain"]
        if pd.notna(row["field"]) and row["field"] != "":
            return FIELD_TO_DOMAIN.get(row["field"])
        return None

    df["domain_resolved"] = df.apply(get_domain, axis=1)
    counts = (df[df["domain_resolved"].notna()]
                .groupby("domain_resolved")
                .size()
                .sort_values())

    colors = [DOMAIN_COLORS.get(d, LABLUE) for d in counts.index]
    fig, ax = plt.subplots(figsize=(7, 3.5))
    bars = ax.barh(counts.index, counts.values, color=colors, height=0.55)
    for bar, v in zip(bars, counts.values):
        ax.text(v + counts.values.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{v:,}", va="center", color=GRAY1, fontsize=10)
    ax.set_xlabel("Number of tasks", color=GRAY1)
    ax.set_title("Tasks by Research Domain", color=LABLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlim(0, counts.values.max() * 1.15)
    save(fig, "tasks_by_domain.png")


# ══════════════════════════════════════════════════════════════════════════════
# 2. Tasks by category
# ══════════════════════════════════════════════════════════════════════════════
def fig_tasks_by_category():
    df = pd.read_csv(PUB / "tasks.csv")
    counts = df.groupby("category").size().rename(index=CATEGORY_SHORT).sort_values()

    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.barh(counts.index, counts.values, color=LABLUE, height=0.55)
    for bar, v in zip(bars, counts.values):
        ax.text(v + counts.values.max() * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{v:,}", va="center", color=GRAY1, fontsize=10)
    ax.set_xlabel("Number of tasks", color=GRAY1)
    ax.set_title("Tasks by Activity Category", color=LABLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1)
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_xlim(0, counts.values.max() * 1.15)
    save(fig, "tasks_by_category.png")


# ══════════════════════════════════════════════════════════════════════════════
# 3. Tasks by level
# ══════════════════════════════════════════════════════════════════════════════
def fig_tasks_by_level():
    df = pd.read_csv(PUB / "tasks.csv")
    level_order = ["universal", "domain", "subfield"]
    level_labels = {"universal": "Universal", "domain": "Domain", "subfield": "Subfield"}
    counts = df.groupby("level").size().reindex(level_order).rename(index=level_labels)

    fig, ax = plt.subplots(figsize=(5, 3))
    colors = [LALIGHTBLUE, NEWBLUE, LABLUE]
    bars = ax.bar(counts.index, counts.values, color=colors, width=0.5)
    for bar, v in zip(bars, counts.values):
        ax.text(bar.get_x() + bar.get_width() / 2, v + counts.values.max() * 0.02,
                f"{v:,}", ha="center", color=GRAY1, fontsize=10)
    ax.set_ylabel("Number of tasks", color=GRAY1)
    ax.set_title("Tasks by Hierarchy Level", color=LABLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.set_ylim(0, counts.values.max() * 1.15)
    ax.grid(axis="y")
    ax.grid(axis="x", visible=False)
    save(fig, "tasks_by_level.png")


# ══════════════════════════════════════════════════════════════════════════════
# 4. Verifiability index by domain
# ══════════════════════════════════════════════════════════════════════════════
def fig_verifiability_by_domain():
    verif = pd.read_csv(PRIV / "verifiability" / "verifiability_index_by_subfield_3var.csv")
    domain_map = load_subfield_domain_map()

    merged = verif.merge(domain_map, on="subfield_name", how="left")
    merged = merged.dropna(subset=["domain_name"])

    # Domain order by median verifiability (ascending)
    domain_order = (merged.groupby("domain_name")["verifiability_index"]
                         .median().sort_values(ascending=True).index.tolist())

    fig, ax = plt.subplots(figsize=(7, 4))
    positions = range(len(domain_order))
    for i, domain in enumerate(domain_order):
        vals = merged[merged["domain_name"] == domain]["verifiability_index"].values
        bp = ax.boxplot(vals, positions=[i], widths=0.5, patch_artist=True,
                        medianprops=dict(color="white", linewidth=2),
                        boxprops=dict(facecolor=DOMAIN_COLORS.get(domain, LABLUE), alpha=0.85),
                        whiskerprops=dict(color=GRAY2),
                        capprops=dict(color=GRAY2),
                        flierprops=dict(marker="o", color=GRAY2, alpha=0.4, markersize=3))

    ax.set_xticks(list(positions))
    ax.set_xticklabels(domain_order, color=GRAY1)
    ax.set_ylabel("Verifiability index", color=GRAY1)
    ax.set_title("Verifiability Index by Research Domain", color=LABLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1)
    ax.grid(axis="y")
    ax.grid(axis="x", visible=False)
    save(fig, "verifiability_by_domain.png")


# ══════════════════════════════════════════════════════════════════════════════
# 5. Top and bottom subfields by verifiability
# ══════════════════════════════════════════════════════════════════════════════
def fig_verifiability_top_bottom():
    verif = pd.read_csv(PRIV / "verifiability" / "verifiability_index_by_subfield_3var.csv")
    verif = verif[verif["paper_count"] >= 100].copy()
    verif = verif.sort_values("verifiability_index")

    top10    = verif.nlargest(10, "verifiability_index").iloc[::-1]
    bottom10 = verif.nsmallest(10, "verifiability_index")

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))

    # Bottom (low verifiability)
    axes[0].barh(bottom10["subfield_name"], bottom10["verifiability_index"],
                 color=LALIGHTBLUE, height=0.6)
    axes[0].set_title("Lowest Verifiability", color=LABLUE, fontweight="bold")
    axes[0].set_xlabel("Verifiability index", color=GRAY1)
    axes[0].tick_params(colors=GRAY1, labelsize=9)

    # Top (high verifiability)
    axes[1].barh(top10["subfield_name"], top10["verifiability_index"],
                 color=LABLUE, height=0.6)
    axes[1].set_title("Highest Verifiability", color=LABLUE, fontweight="bold")
    axes[1].set_xlabel("Verifiability index", color=GRAY1)
    axes[1].tick_params(colors=GRAY1, labelsize=9)

    fig.suptitle("Top and Bottom Subfields by Verifiability Index",
                 color=LABLUE, fontweight="bold", fontsize=13, y=1.01)
    fig.tight_layout()
    save(fig, "verifiability_top_bottom.png")


# ══════════════════════════════════════════════════════════════════════════════
# 6. Verifiability components by domain
# ══════════════════════════════════════════════════════════════════════════════
def fig_verifiability_components():
    verif = pd.read_csv(PRIV / "verifiability" / "verifiability_index_by_subfield_3var.csv")
    domain_map = load_subfield_domain_map()

    merged = verif.merge(domain_map, on="subfield_name", how="left").dropna(subset=["domain_name"])

    # Paper-weighted means per domain
    def weighted_mean(grp, col):
        return np.average(grp[col], weights=grp["paper_count"])

    agg = (merged.groupby("domain_name")
                 .apply(lambda g: pd.Series({
                     "Retraction rate (%)":       weighted_mean(g, "retraction_rate"),
                     "Hedging words per 100w":    weighted_mean(g, "hedge_per_100w"),
                     "Booster words per 100w":    weighted_mean(g, "booster_per_100w"),
                 }))
                 .reset_index())
    agg["domain_name"] = pd.Categorical(
        agg["domain_name"],
        categories=DISPLAY_DOMAIN_ORDER,
        ordered=True,
    )
    agg = agg.sort_values("domain_name")

    components = ["Retraction rate (%)", "Hedging words per 100w", "Booster words per 100w"]
    colors_comp = [LALIGHTBLUE, NEWBLUE, LABLUE]

    domain_order = agg["domain_name"].tolist()
    x = np.arange(len(domain_order))
    width = 0.28

    fig, axes = plt.subplots(1, 3, figsize=(13, 4))
    for i, (comp, col) in enumerate(zip(components, colors_comp)):
        axes[i].bar(x, agg[comp], color=col, width=0.55)
        axes[i].set_xticks(x)
        axes[i].set_xticklabels(domain_order, rotation=15, ha="right",
                                color=GRAY1, fontsize=9)
        axes[i].set_title(comp, color=LABLUE, fontweight="bold", fontsize=10)
        axes[i].tick_params(colors=GRAY1)
        axes[i].grid(axis="y")
        axes[i].grid(axis="x", visible=False)

    fig.suptitle("Verifiability Components by Domain (paper-weighted means)",
                 color=LABLUE, fontweight="bold", fontsize=12, y=1.02)
    fig.tight_layout()
    save(fig, "verifiability_components.png")


# ══════════════════════════════════════════════════════════════════════════════
# 7. AI-mention rate by subfield (top 20)
# ══════════════════════════════════════════════════════════════════════════════
def fig_ai_mention_subfields():
    # Aggregate topic_yearly_counts (2023-2025) to subfield level
    tyc = pd.read_csv(PRIV / "openalex" / "field_stats" / "topic_yearly_counts.csv")
    tyc = tyc[tyc["year"].between(2023, 2025)]
    tyc_agg = tyc.groupby("topic_id")[["paper_count", "ai_paper_count"]].sum().reset_index()

    mapping = load_topic_mapping()
    tyc_agg["topic_id"]  = tyc_agg["topic_id"].astype(str)

    merged = tyc_agg.merge(mapping, on="topic_id", how="left").dropna(subset=["subfield"])
    sf_agg = (merged.groupby("subfield")[["paper_count", "ai_paper_count"]]
                    .sum().reset_index())
    sf_agg["ai_share"] = sf_agg["ai_paper_count"] / sf_agg["paper_count"] * 100
    sf_agg = sf_agg[sf_agg["paper_count"] >= 1000]

    top20 = sf_agg.nlargest(20, "ai_share").sort_values("ai_share")

    fig, ax = plt.subplots(figsize=(8, 7))
    ax.barh(top20["subfield"], top20["ai_share"], color=LABLUE, height=0.65)
    for i, (_, row) in enumerate(top20.iterrows()):
        ax.text(row["ai_share"] + 0.3, i,
                f"{row['ai_share']:.1f}%", va="center", color=GRAY1, fontsize=9)
    ax.set_xlabel("Share of papers mentioning AI (%)", color=GRAY1)
    ax.set_title("Top 20 Subfields by AI-Mention Rate\n(2023–2025)",
                 color=LABLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1, labelsize=9)
    ax.set_xlim(0, top20["ai_share"].max() * 1.18)
    save(fig, "ai_mention_subfields.png")


# ══════════════════════════════════════════════════════════════════════════════
# 8. AI adoption by country — two panels
# ══════════════════════════════════════════════════════════════════════════════
def fig_ai_adoption_country():
    df = pd.read_csv(PRIV / "openalex" / "field_stats" / "ai_rankings_country.csv")
    df = df[df["paper_count"] >= 5000].copy()
    df["adjusted_ai_share_pct"] = df["adjusted_ai_share"] * 100

    top20_vol = df.nlargest(20, "ai_paper_count").sort_values("ai_paper_count")
    top20_adj = df.nlargest(20, "adjusted_ai_share").sort_values("adjusted_ai_share")

    fig, axes = plt.subplots(1, 2, figsize=(15, 7))

    # Left: total AI papers
    axes[0].barh(top20_vol["country_name"], top20_vol["ai_paper_count"] / 1000,
                 color=LABLUE, height=0.65)
    for bar, v in zip(axes[0].patches, top20_vol["ai_paper_count"]):
        axes[0].text(bar.get_width() + top20_vol["ai_paper_count"].max() / 1000 * 0.01,
                     bar.get_y() + bar.get_height() / 2,
                     f"{v/1000:.0f}k", va="center", color=GRAY1, fontsize=8)
    axes[0].set_xlabel("AI-related papers (thousands, 2023–2025)", color=GRAY1)
    axes[0].set_title("Total AI Papers", color=LABLUE, fontweight="bold")
    axes[0].tick_params(colors=GRAY1, labelsize=9)
    axes[0].set_xlim(0, top20_vol["ai_paper_count"].max() / 1000 * 1.18)

    # Right: field-adjusted adoption rate
    colors = [LABLUE if v >= 0 else LALIGHTBLUE for v in top20_adj["adjusted_ai_share_pct"]]
    axes[1].barh(top20_adj["country_name"], top20_adj["adjusted_ai_share_pct"],
                 color=colors, height=0.65)
    axes[1].axvline(0, color=GRAY2, linewidth=0.8, linestyle="--")
    axes[1].set_xlabel("Field-adjusted AI share (pp above/below expected)", color=GRAY1)
    axes[1].set_title("Field-Adjusted AI Adoption Rate", color=LABLUE, fontweight="bold")
    axes[1].tick_params(colors=GRAY1, labelsize=9)

    fig.suptitle("Country-Level AI Adoption in Research (2023–2025)",
                 color=LABLUE, fontweight="bold", fontsize=13, y=1.01)
    fig.tight_layout()
    save(fig, "ai_adoption_country.png")


# ══════════════════════════════════════════════════════════════════════════════
# 9b. Claude usage vs. AI in science scatter (country-level)
# ══════════════════════════════════════════════════════════════════════════════
def fig_claude_vs_science_scatter():
    df = load_claude_science_country_data()
    df = df[(df["paper_count"] >= 1000) &
            (df["claude_index"] > 0) &
            (df["working_age_pop"] > 0)].copy()

    sizes = country_bubble_sizes(df["paper_count"])

    label_countries = pd.concat([
        df.nlargest(4, "claude_index"),
        df.nlargest(4, "papers_per_capita"),
        df[df["country_code"] == "US"],
    ]).drop_duplicates(subset="country_name")

    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.grid(False)  # no grid lines on scatter
    ax.scatter(df["claude_index"], df["papers_per_capita"],
               s=sizes, c=LABLUE, alpha=0.55, linewidths=0.4, edgecolors=LABLUE)

    # Ensure US is always in the label set
    add_country_labels_simple(ax, label_countries, "claude_index", "papers_per_capita")

    # Trend line + correlation
    mask = df["claude_index"].between(0.01, 20)
    if mask.sum() > 10:
        x, y = df.loc[mask, "claude_index"], df.loc[mask, "papers_per_capita"]
        coef = np.polyfit(x, y, 1)
        x_fit = np.linspace(x.min(), x.max(), 200)
        ax.plot(x_fit, np.polyval(coef, x_fit),
                color=LALIGHTBLUE, linewidth=1.5, linestyle="--", alpha=0.8)
        corr = np.corrcoef(x, y)[0, 1]
        ax.text(0.99, 0.02, f"Correlation: {corr:.2f}",
                transform=ax.transAxes, ha="right", va="bottom",
                fontsize=8, color=GRAY2)

    ax.set_xlabel("Claude usage per-capita index",
                  color=GRAY1, fontsize=10)
    ax.set_ylabel("Research Papers per 1,000 Capita\n(OpenAlex)",
                  color=GRAY1, fontsize=10)
    ax.set_title("Claude Usage and Research Output Per Capita",
                 color=LABLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1)

    add_country_bubble_legend(ax)

    save(fig, "claude_vs_science.png")


def fig_claude_vs_science_scatter_loglog():
    df = load_claude_science_country_data()
    df = df[(df["paper_count"] >= 1000) &
            (df["claude_index"] > 0) &
            (df["papers_per_capita"] > 0)].copy()

    sizes = country_bubble_sizes(df["paper_count"])

    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.grid(False)
    ax.scatter(df["claude_index"], df["papers_per_capita"],
               s=sizes, c=LABLUE, alpha=0.55, linewidths=0.4, edgecolors=LABLUE)

    log_x = np.log10(df["claude_index"])
    log_y = np.log10(df["papers_per_capita"])
    coef = np.polyfit(log_x, log_y, 1)
    x_fit = np.geomspace(df["claude_index"].min(), df["claude_index"].max(), 200)
    y_fit = 10 ** np.polyval(coef, np.log10(x_fit))
    ax.plot(x_fit, y_fit,
            color=LALIGHTBLUE, linewidth=1.5, linestyle="--", alpha=0.8)
    corr = np.corrcoef(log_x, log_y)[0, 1]
    ax.text(0.99, 0.02, f"Log correlation: {corr:.2f}",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, color=GRAY2)

    ax.set_xscale("log")
    ax.set_yscale("log")
    style_log_decimal_axes(ax)
    add_country_labels_loglog(ax, df, "claude_index", "papers_per_capita")
    ax.set_xlabel("Claude usage per-capita index\n(log scale)",
                  color=GRAY1, fontsize=10)
    ax.set_ylabel("Research Papers per 1,000 Capita\n(OpenAlex, log scale)",
                  color=GRAY1, fontsize=10)
    ax.set_title("Claude Usage and Research Output Per Capita (Log Scale)",
                 color=LABLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1)

    add_country_bubble_legend(ax)

    save_loose(fig, "claude_vs_science_loglog.png")


def residual_pct_formatter(value, _):
    pct = (10 ** value - 1) * 100
    if abs(pct) < 0.5:
        return "0%"
    return f"{pct:+.0f}%"


def log_decimal_formatter(value, _):
    if value <= 0:
        return ""
    return f"{value:g}"


def style_log_decimal_axes(ax):
    major_locator = mticker.LogLocator(base=10, subs=(1.0,))
    ax.xaxis.set_major_locator(major_locator)
    ax.yaxis.set_major_locator(major_locator)
    ax.xaxis.set_minor_locator(mticker.NullLocator())
    ax.yaxis.set_minor_locator(mticker.NullLocator())
    ax.xaxis.set_major_formatter(mticker.FuncFormatter(log_decimal_formatter))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(log_decimal_formatter))
    ax.xaxis.set_minor_formatter(mticker.NullFormatter())
    ax.yaxis.set_minor_formatter(mticker.NullFormatter())
    ax.tick_params(which="minor", bottom=False, left=False)


def fig_claude_vs_science_residual_scatter():
    df = load_claude_science_country_data()
    df = df[(df["paper_count"] >= 1000) &
            (df["claude_index"] > 0) &
            (df["papers_per_capita"] > 0) &
            (df["gdp_per_working_age_capita"] > 0)].copy()

    log_gdp = np.log10(df["gdp_per_working_age_capita"])
    log_claude = np.log10(df["claude_index"])
    log_papers = np.log10(df["papers_per_capita"])

    claude_coef = np.polyfit(log_gdp, log_claude, 1)
    papers_coef = np.polyfit(log_gdp, log_papers, 1)
    df["claude_gdp_resid"] = log_claude - np.polyval(claude_coef, log_gdp)
    df["papers_gdp_resid"] = log_papers - np.polyval(papers_coef, log_gdp)

    sizes = country_bubble_sizes(df["paper_count"])
    df["resid_score"] = (
        df["claude_gdp_resid"].abs() + df["papers_gdp_resid"].abs()
    )
    label_countries = pd.concat([
        df.nlargest(16, "resid_score"),
        df[df["paper_count"] >= 150000],
        df[df["country_code"] == "US"],
    ]).drop_duplicates(subset="country_name")

    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.grid(False)
    ax.axhline(0, color=GRAY2, linewidth=0.8, linestyle="--", alpha=0.7)
    ax.axvline(0, color=GRAY2, linewidth=0.8, linestyle="--", alpha=0.7)
    ax.scatter(df["claude_gdp_resid"], df["papers_gdp_resid"],
               s=sizes, c=LABLUE, alpha=0.55, linewidths=0.4, edgecolors=LABLUE)

    add_country_labels(ax, label_countries, "claude_gdp_resid", "papers_gdp_resid")

    coef = np.polyfit(df["claude_gdp_resid"], df["papers_gdp_resid"], 1)
    x_fit = np.linspace(df["claude_gdp_resid"].min(), df["claude_gdp_resid"].max(), 200)
    ax.plot(x_fit, np.polyval(coef, x_fit),
            color=LALIGHTBLUE, linewidth=1.5, linestyle="--", alpha=0.8)
    corr = np.corrcoef(df["claude_gdp_resid"], df["papers_gdp_resid"])[0, 1]
    ax.text(0.99, 0.02, f"Residual correlation: {corr:.2f}",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, color=GRAY2)

    formatter = mticker.FuncFormatter(residual_pct_formatter)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)

    ax.set_xlabel("Claude Usage\n(% above/below GDP-predicted level)",
                  color=GRAY1, fontsize=10)
    ax.set_ylabel("Research Output per 1,000 Capita\n(% above/below GDP-predicted level)",
                  color=GRAY1, fontsize=10)
    ax.set_title("Claude Usage and Research Output Per Capita (Log-Log Residualized)",
                 color=LABLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1)

    add_country_bubble_legend(ax)

    save(fig, "claude_vs_science_loglog_residual.png")


def fig_claude_vs_science_residual_scatter_levels():
    df = load_claude_science_country_data()
    df = df[(df["paper_count"] >= 1000) &
            (df["claude_index"] > 0) &
            (df["papers_per_capita"] > 0) &
            (df["gdp_per_working_age_capita"] > 0)].copy()

    gdp = df["gdp_per_working_age_capita"]
    claude_coef = np.polyfit(gdp, df["claude_index"], 1)
    papers_coef = np.polyfit(gdp, df["papers_per_capita"], 1)
    df["claude_gdp_resid"] = df["claude_index"] - np.polyval(claude_coef, gdp)
    df["papers_gdp_resid"] = df["papers_per_capita"] - np.polyval(papers_coef, gdp)

    sizes = country_bubble_sizes(df["paper_count"])
    df["resid_score"] = (
        df["claude_gdp_resid"].abs() / df["claude_gdp_resid"].std()
        + df["papers_gdp_resid"].abs() / df["papers_gdp_resid"].std()
    )
    label_countries = pd.concat([
        df.nlargest(16, "resid_score"),
        df[df["paper_count"] >= 150000],
        df[df["country_code"] == "US"],
    ]).drop_duplicates(subset="country_name")

    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.grid(False)
    ax.axhline(0, color=GRAY2, linewidth=0.8, linestyle="--", alpha=0.7)
    ax.axvline(0, color=GRAY2, linewidth=0.8, linestyle="--", alpha=0.7)
    ax.scatter(df["claude_gdp_resid"], df["papers_gdp_resid"],
               s=sizes, c=LABLUE, alpha=0.55, linewidths=0.4, edgecolors=LABLUE)

    add_country_labels(ax, label_countries, "claude_gdp_resid", "papers_gdp_resid")

    coef = np.polyfit(df["claude_gdp_resid"], df["papers_gdp_resid"], 1)
    x_fit = np.linspace(df["claude_gdp_resid"].min(), df["claude_gdp_resid"].max(), 200)
    ax.plot(x_fit, np.polyval(coef, x_fit),
            color=LALIGHTBLUE, linewidth=1.5, linestyle="--", alpha=0.8)
    corr = np.corrcoef(df["claude_gdp_resid"], df["papers_gdp_resid"])[0, 1]
    ax.text(0.99, 0.02, f"Residual correlation: {corr:.2f}",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, color=GRAY2)

    ax.set_xlabel("Claude Usage residual\n(index points vs GDP-predicted level)",
                  color=GRAY1, fontsize=10)
    ax.set_ylabel("Research Output per 1,000 Capita residual\n(vs GDP-predicted level)",
                  color=GRAY1, fontsize=10)
    ax.set_title("Claude Usage and Research Output Per Capita (Levels Residualized)",
                 color=LABLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1)

    add_country_bubble_legend(ax)

    save(fig, "claude_vs_science_residual.png")


def fig_claude_vs_ai_science_scatter():
    df = load_claude_science_country_data()
    # Keep the same country sample definition used elsewhere in the project:
    # countries need population data and at least 1,000 total papers.
    df = df[(df["paper_count"] >= 1000) &
            (df["claude_index"] > 0) &
            (df["working_age_pop"] > 0) &
            (df["ai_papers_per_capita"] > 0)].copy()

    sizes = country_bubble_sizes(df["ai_paper_count"])

    label_countries = pd.concat([
        df.nlargest(4, "claude_index"),
        df.nlargest(4, "ai_papers_per_capita"),
        df.nlargest(4, "ai_paper_count"),
        df[df["country_code"] == "US"],
    ]).drop_duplicates(subset="country_name")

    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.grid(False)
    ax.scatter(df["claude_index"], df["ai_papers_per_capita"],
               s=sizes, c=NEWBLUE, alpha=0.55, linewidths=0.4, edgecolors=NEWBLUE)

    add_country_labels_simple(ax, label_countries, "claude_index", "ai_papers_per_capita")

    mask = df["claude_index"].between(0.01, 20)
    if mask.sum() > 10:
        x, y = df.loc[mask, "claude_index"], df.loc[mask, "ai_papers_per_capita"]
        coef = np.polyfit(x, y, 1)
        x_fit = np.linspace(x.min(), x.max(), 200)
        ax.plot(x_fit, np.polyval(coef, x_fit),
                color=LALIGHTBLUE, linewidth=1.5, linestyle="--", alpha=0.8)
        corr = np.corrcoef(x, y)[0, 1]
        ax.text(0.99, 0.02, f"Correlation: {corr:.2f}",
                transform=ax.transAxes, ha="right", va="bottom",
                fontsize=8, color=GRAY2)

    ax.set_xlabel("Claude usage per-capita index",
                  color=GRAY1, fontsize=10)
    ax.set_ylabel("AI Research Papers per 1,000 Capita\n(OpenAlex)",
                  color=GRAY1, fontsize=10)
    ax.set_title("Claude Usage and AI Research Output Per Capita",
                 color=NEWBLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1)

    add_country_bubble_legend(
        ax,
        examples=[(100, "100 AI papers"), (1000, "1k"), (10000, "10k")],
        title="AI paper count",
        color=NEWBLUE,
    )

    save(fig, "claude_vs_ai_science.png")


def fig_claude_vs_ai_science_scatter_loglog():
    df = load_claude_science_country_data()
    df = df[(df["paper_count"] >= 1000) &
            (df["claude_index"] > 0) &
            (df["ai_papers_per_capita"] > 0)].copy()

    sizes = country_bubble_sizes(df["ai_paper_count"])

    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.grid(False)
    ax.scatter(df["claude_index"], df["ai_papers_per_capita"],
               s=sizes, c=NEWBLUE, alpha=0.55, linewidths=0.4, edgecolors=NEWBLUE)

    log_x = np.log10(df["claude_index"])
    log_y = np.log10(df["ai_papers_per_capita"])
    coef = np.polyfit(log_x, log_y, 1)
    x_fit = np.geomspace(df["claude_index"].min(), df["claude_index"].max(), 200)
    y_fit = 10 ** np.polyval(coef, np.log10(x_fit))
    ax.plot(x_fit, y_fit,
            color=LALIGHTBLUE, linewidth=1.5, linestyle="--", alpha=0.8)
    corr = np.corrcoef(log_x, log_y)[0, 1]
    ax.text(0.99, 0.02, f"Log correlation: {corr:.2f}",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, color=GRAY2)

    ax.set_xscale("log")
    ax.set_yscale("log")
    style_log_decimal_axes(ax)
    add_country_labels_loglog(ax, df, "claude_index", "ai_papers_per_capita")
    ax.set_xlabel("Claude usage per-capita index\n(log scale)",
                  color=GRAY1, fontsize=10)
    ax.set_ylabel("AI Research Papers per 1,000 Capita\n(OpenAlex, log scale)",
                  color=GRAY1, fontsize=10)
    ax.set_title("Claude Usage and AI Research Output Per Capita (Log Scale)",
                 color=NEWBLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1)

    add_country_bubble_legend(
        ax,
        examples=[(100, "100 AI papers"), (1000, "1k"), (10000, "10k")],
        title="AI paper count",
        color=NEWBLUE,
    )

    save_loose(fig, "claude_vs_ai_science_loglog.png")


def fig_claude_vs_ai_science_residual_scatter():
    df = load_claude_science_country_data()
    df = df[(df["paper_count"] >= 1000) &
            (df["claude_index"] > 0) &
            (df["ai_papers_per_capita"] > 0) &
            (df["gdp_per_working_age_capita"] > 0)].copy()

    log_gdp = np.log10(df["gdp_per_working_age_capita"])
    log_claude = np.log10(df["claude_index"])
    log_ai_papers = np.log10(df["ai_papers_per_capita"])

    claude_coef = np.polyfit(log_gdp, log_claude, 1)
    ai_papers_coef = np.polyfit(log_gdp, log_ai_papers, 1)
    df["claude_gdp_resid"] = log_claude - np.polyval(claude_coef, log_gdp)
    df["ai_papers_gdp_resid"] = log_ai_papers - np.polyval(ai_papers_coef, log_gdp)

    sizes = country_bubble_sizes(df["ai_paper_count"])
    df["resid_score"] = (
        df["claude_gdp_resid"].abs() + df["ai_papers_gdp_resid"].abs()
    )
    label_countries = pd.concat([
        df.nlargest(16, "resid_score"),
        df[df["ai_paper_count"] >= 25000],
        df[df["country_code"] == "US"],
    ]).drop_duplicates(subset="country_name")

    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.grid(False)
    ax.axhline(0, color=GRAY2, linewidth=0.8, linestyle="--", alpha=0.7)
    ax.axvline(0, color=GRAY2, linewidth=0.8, linestyle="--", alpha=0.7)
    ax.scatter(df["claude_gdp_resid"], df["ai_papers_gdp_resid"],
               s=sizes, c=NEWBLUE, alpha=0.55, linewidths=0.4, edgecolors=NEWBLUE)

    add_country_labels(ax, label_countries, "claude_gdp_resid", "ai_papers_gdp_resid")

    coef = np.polyfit(df["claude_gdp_resid"], df["ai_papers_gdp_resid"], 1)
    x_fit = np.linspace(df["claude_gdp_resid"].min(), df["claude_gdp_resid"].max(), 200)
    ax.plot(x_fit, np.polyval(coef, x_fit),
            color=LALIGHTBLUE, linewidth=1.5, linestyle="--", alpha=0.8)
    corr = np.corrcoef(df["claude_gdp_resid"], df["ai_papers_gdp_resid"])[0, 1]
    ax.text(0.99, 0.02, f"Residual correlation: {corr:.2f}",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, color=GRAY2)

    formatter = mticker.FuncFormatter(residual_pct_formatter)
    ax.xaxis.set_major_formatter(formatter)
    ax.yaxis.set_major_formatter(formatter)

    ax.set_xlabel("Claude Usage\n(% above/below GDP-predicted level)",
                  color=GRAY1, fontsize=10)
    ax.set_ylabel("AI Research Output per 1,000 Capita\n(% above/below GDP-predicted level)",
                  color=GRAY1, fontsize=10)
    ax.set_title("Claude Usage and AI Research Output Per Capita (Log-Log Residualized)",
                 color=NEWBLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1)

    add_country_bubble_legend(
        ax,
        examples=[(100, "100 AI papers"), (1000, "1k"), (10000, "10k")],
        title="AI paper count",
        color=NEWBLUE,
    )

    save(fig, "claude_vs_ai_science_loglog_residual.png")


def fig_claude_vs_ai_science_residual_scatter_levels():
    df = load_claude_science_country_data()
    df = df[(df["paper_count"] >= 1000) &
            (df["claude_index"] > 0) &
            (df["ai_papers_per_capita"] > 0) &
            (df["gdp_per_working_age_capita"] > 0)].copy()

    gdp = df["gdp_per_working_age_capita"]
    claude_coef = np.polyfit(gdp, df["claude_index"], 1)
    ai_papers_coef = np.polyfit(gdp, df["ai_papers_per_capita"], 1)
    df["claude_gdp_resid"] = df["claude_index"] - np.polyval(claude_coef, gdp)
    df["ai_papers_gdp_resid"] = df["ai_papers_per_capita"] - np.polyval(ai_papers_coef, gdp)

    sizes = country_bubble_sizes(df["ai_paper_count"])
    df["resid_score"] = (
        df["claude_gdp_resid"].abs() / df["claude_gdp_resid"].std()
        + df["ai_papers_gdp_resid"].abs() / df["ai_papers_gdp_resid"].std()
    )
    label_countries = pd.concat([
        df.nlargest(16, "resid_score"),
        df[df["ai_paper_count"] >= 25000],
        df[df["country_code"] == "US"],
    ]).drop_duplicates(subset="country_name")

    fig, ax = plt.subplots(figsize=(9, 6.5))
    ax.grid(False)
    ax.axhline(0, color=GRAY2, linewidth=0.8, linestyle="--", alpha=0.7)
    ax.axvline(0, color=GRAY2, linewidth=0.8, linestyle="--", alpha=0.7)
    ax.scatter(df["claude_gdp_resid"], df["ai_papers_gdp_resid"],
               s=sizes, c=NEWBLUE, alpha=0.55, linewidths=0.4, edgecolors=NEWBLUE)

    add_country_labels(ax, label_countries, "claude_gdp_resid", "ai_papers_gdp_resid")

    coef = np.polyfit(df["claude_gdp_resid"], df["ai_papers_gdp_resid"], 1)
    x_fit = np.linspace(df["claude_gdp_resid"].min(), df["claude_gdp_resid"].max(), 200)
    ax.plot(x_fit, np.polyval(coef, x_fit),
            color=LALIGHTBLUE, linewidth=1.5, linestyle="--", alpha=0.8)
    corr = np.corrcoef(df["claude_gdp_resid"], df["ai_papers_gdp_resid"])[0, 1]
    ax.text(0.99, 0.02, f"Residual correlation: {corr:.2f}",
            transform=ax.transAxes, ha="right", va="bottom",
            fontsize=8, color=GRAY2)

    ax.set_xlabel("Claude Usage residual\n(index points vs GDP-predicted level)",
                  color=GRAY1, fontsize=10)
    ax.set_ylabel("AI Research Output per 1,000 Capita residual\n(vs GDP-predicted level)",
                  color=GRAY1, fontsize=10)
    ax.set_title("Claude Usage and AI Research Output Per Capita (Levels Residualized)",
                 color=NEWBLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1)

    add_country_bubble_legend(
        ax,
        examples=[(100, "100 AI papers"), (1000, "1k"), (10000, "10k")],
        title="AI paper count",
        color=NEWBLUE,
    )

    save(fig, "claude_vs_ai_science_residual.png")


# ══════════════════════════════════════════════════════════════════════════════
# 9. Publication volume by domain
# ══════════════════════════════════════════════════════════════════════════════
def fig_papers_by_domain():
    mapping = load_topic_mapping()[["topic_id", "domain"]]
    topic_stats = pd.read_csv(PRIV / "openalex" / "field_stats" / "topic_stats.csv")
    topic_stats["topic_id"] = topic_stats["topic_id"].astype(str)
    df = (
        topic_stats.merge(mapping, on="topic_id", how="left")
        .dropna(subset=["domain"])
        .groupby("domain", as_index=False)["paper_count"]
        .sum()
        .rename(columns={"domain": "domain_name"})
        .sort_values("paper_count")
    )
    df["paper_count_M"] = df["paper_count"] / 1e6
    colors = [DOMAIN_COLORS.get(d, LABLUE) for d in df["domain_name"]]

    fig, ax = plt.subplots(figsize=(7, 3.5))
    bars = ax.barh(df["domain_name"], df["paper_count_M"], color=colors, height=0.55)
    for bar, v in zip(bars, df["paper_count_M"]):
        ax.text(v + df["paper_count_M"].max() * 0.01, bar.get_y() + bar.get_height() / 2,
                f"{v:.0f}M", va="center", color=GRAY1, fontsize=10)
    ax.set_xlabel("Publications (millions)", color=GRAY1)
    ax.set_title("Publication Volume by Research Domain\n(OpenAlex, all years)",
                 color=LABLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1)
    ax.set_xlim(0, df["paper_count_M"].max() * 1.15)
    save(fig, "papers_by_domain.png")


# ══════════════════════════════════════════════════════════════════════════════
# Run all
# ══════════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    print("Generating SciNet data overview figures...")
    fig_claude_vs_science_scatter()
    fig_claude_vs_science_scatter_loglog()
    fig_claude_vs_science_residual_scatter()
    fig_claude_vs_science_residual_scatter_levels()
    fig_claude_vs_ai_science_scatter()
    fig_claude_vs_ai_science_scatter_loglog()
    fig_claude_vs_ai_science_residual_scatter()
    fig_claude_vs_ai_science_residual_scatter_levels()
    fig_tasks_by_domain()
    fig_tasks_by_category()
    fig_tasks_by_level()
    fig_verifiability_by_domain()
    fig_verifiability_top_bottom()
    fig_verifiability_components()
    fig_ai_mention_subfields()
    fig_ai_adoption_country()
    fig_papers_by_domain()
    print(f"\nDone. All figures saved to {OUT}/")
