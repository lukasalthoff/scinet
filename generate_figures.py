"""
SciNet Data Overview — Figure Generator
========================================
Run from the public/ directory:
    python generate_figures.py

Outputs 9 PNG figures to figures/
Reads public data from data/ and private data from ../data/
"""

import json
import os
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
}

CATEGORY_SHORT = {
    "Ideation & Hypothesis Generation": "Ideation & Hypotheses",
    "Data Gathering":                   "Data Gathering",
    "Data Analysis":                    "Data Analysis",
    "Writing & Communication":          "Writing & Communication",
    "Peer Review & Service":            "Peer Review",
    "Mentorship & Teaching":            "Mentorship & Teaching",
    "Administration & Collaboration":   "Administration",
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


# Mapping from SciNet display field → research domain
FIELD_TO_DOMAIN = {
    "Agricultural Sciences":      "Life Sciences",
    "Biology":                    "Life Sciences",
    "Biomedical Sciences":        "Life Sciences",
    "Environmental Science":      "Life Sciences",
    "Anthropology":               "Social Sciences",
    "Arts":                       "Social Sciences",
    "Business & Management":      "Social Sciences",
    "Communication & Media Studies": "Social Sciences",
    "Economics":                  "Social Sciences",
    "Education":                  "Social Sciences",
    "Geography":                  "Social Sciences",
    "History":                    "Social Sciences",
    "Languages & Linguistics":    "Social Sciences",
    "Law":                        "Social Sciences",
    "Literature":                 "Social Sciences",
    "Philosophy":                 "Social Sciences",
    "Political Science":          "Social Sciences",
    "Psychology":                 "Social Sciences",
    "Religion":                   "Social Sciences",
    "Sociology":                  "Social Sciences",
    "Chemistry":                  "Physical Sciences",
    "Computer Science":           "Physical Sciences",
    "Earth & Planetary Sciences": "Physical Sciences",
    "Engineering":                "Physical Sciences",
    "Materials Science":          "Physical Sciences",
    "Mathematics":                "Physical Sciences",
    "Physics & Astronomy":        "Physical Sciences",
    "Statistics":                 "Physical Sciences",
    "Medicine & Clinical Sciences": "Health Sciences",
    "Neuroscience":               "Health Sciences",
}

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
    sf_stats = pd.read_csv(PRIV / "openalex" / "field_stats" / "subfield_stats.csv")
    domain_map = sf_stats[["subfield_name", "domain_name"]].drop_duplicates()

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
    sf_stats = pd.read_csv(PRIV / "openalex" / "field_stats" / "subfield_stats.csv")
    domain_map = sf_stats[["subfield_name", "domain_name"]].drop_duplicates()

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

    mapping = pd.read_csv(PUB / "openalex_topic_subfield_mapping.csv")
    mapping["topic_id"] = mapping["topic_id"].astype(str)
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
# 8. AI adoption by country (top 20 by adjusted share)
# ══════════════════════════════════════════════════════════════════════════════
def fig_ai_adoption_country():
    df = pd.read_csv(PRIV / "openalex" / "field_stats" / "ai_rankings_country.csv")
    df = df[df["paper_count"] >= 5000]
    top20 = df.nlargest(20, "adjusted_ai_share").sort_values("adjusted_ai_share")
    top20["adjusted_ai_share_pct"] = top20["adjusted_ai_share"] * 100

    fig, ax = plt.subplots(figsize=(8, 7))
    colors = [LABLUE if v >= 0 else LALIGHTBLUE for v in top20["adjusted_ai_share_pct"]]
    ax.barh(top20["country_name"], top20["adjusted_ai_share_pct"],
            color=colors, height=0.65)
    ax.axvline(0, color=GRAY2, linewidth=0.8, linestyle="--")
    ax.set_xlabel("Field-adjusted AI share (pp above/below expected)", color=GRAY1)
    ax.set_title("Top 20 Countries by Field-Adjusted AI Adoption\n(2023–2025)",
                 color=LABLUE, fontweight="bold", pad=10)
    ax.tick_params(colors=GRAY1, labelsize=9)
    save(fig, "ai_adoption_country.png")


# ══════════════════════════════════════════════════════════════════════════════
# 9. Publication volume by domain
# ══════════════════════════════════════════════════════════════════════════════
def fig_papers_by_domain():
    df = pd.read_csv(PRIV / "openalex" / "field_stats" / "domain_stats.csv")
    df = df.sort_values("paper_count")
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
