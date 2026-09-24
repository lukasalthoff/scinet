# Figures

All figures are in `paper/`. Paper-style PNGs (Palatino, no titles; captions live in the paper). The generator, `code/site/generate_public_figures.py`, lives in the main project repository and reads inputs that are not part of this release (OpenAlex field statistics, the Anthropic Economic Index extract, and the website's per-subfield verifiability values), so the figures cannot be rebuilt from this repository alone.

| Figure | Shows | Data | Generated |
|---|---|---|---|
| `paper/tasks_by_level.png` | Number of tasks at each hierarchy level (universal 30, domain 134, field 321, subfield 6,777). | `data/tasks.csv` | 2026-09-24 |
| `paper/tasks_by_category.png` | Number of tasks in each of the ten activity categories. | `data/tasks.csv` | 2026-09-24 |
| `paper/tasks_by_domain.png` | Number of domain-, field- and subfield-level tasks per research domain (six domains; universal tasks excluded). | `data/tasks.csv` | 2026-09-24 |
| `paper/papers_by_domain.png` | OpenAlex publications (all years, millions) per research domain. | OpenAlex topic paper counts mapped through `data/openalex_topic_subfield_mapping.csv` (4,481 topics) | 2026-09-24 |
| `paper/verifiability_by_domain.png` | Distribution of the subfield verifiability index within each domain (box plots; n = ranked subfields per domain, 316 in total). | Per-subfield verifiability index from the SciNet website data (paper-weighted from OpenAlex topic-level retraction, hedging and booster rates) | 2026-09-24 |
| `paper/verifiability_top_bottom.png` | The ten subfields with the lowest (left) and highest (right) verifiability index. | Same as above | 2026-09-24 |
| `paper/verifiability_highest.png` | Right panel of the previous figure: ten highest-verifiability subfields. | Same as above | 2026-09-24 |
| `paper/verifiability_lowest.png` | Left panel of the previous figure: ten lowest-verifiability subfields. | Same as above | 2026-09-24 |
| `paper/verifiability_components.png` | Paper-weighted mean of the three index components per domain: retractions per 10,000 papers, hedging words per 100 words, booster words per 100 words. | Same as above | 2026-09-24 |
| `paper/verifiability_retraction.png` | Retractions per 10,000 papers by domain (paper-weighted mean). | Same as above | 2026-09-24 |
| `paper/verifiability_hedging.png` | Hedging words per 100 abstract words by domain (paper-weighted mean). | Same as above | 2026-09-24 |
| `paper/verifiability_booster.png` | Booster words per 100 abstract words by domain (paper-weighted mean). | Same as above | 2026-09-24 |
| `paper/ai_mention_subfields.png` | The 20 subfields with the highest share of papers mentioning AI, 2023-2025, among subfields with at least 1,000 papers. | OpenAlex topic-year counts mapped through `data/openalex_topic_subfield_mapping.csv` | 2026-09-24 |
| `paper/ai_adoption_country.png` | Left: the 20 countries with the most AI-related papers, 2023-2025 (thousands). Right: the 20 countries with the highest field-adjusted AI share, in percentage points above the share expected from their field mix. Countries with at least 5,000 papers. | OpenAlex country rankings (`ai_rankings_country.csv`) | 2026-09-24 |
| `paper/ai_adoption_total.png` | Left panel of the previous figure: AI-related papers per country. | Same as above | 2026-09-24 |
| `paper/ai_adoption_adjusted.png` | Right panel of the previous figure: field-adjusted AI share per country (pp). | Same as above | 2026-09-24 |
| `paper/claude_vs_science.png` | Claude usage per-capita index against research papers per 1,000 working-age people, by country; bubble size is paper count. | Anthropic Economic Index (2025-08-04 to 2025-08-11) and OpenAlex country paper counts, countries with at least 1,000 papers | 2026-09-17 |
| `paper/claude_vs_science_loglog.png` | Same as `claude_vs_science.png` on log-log axes. | Same as above | 2026-09-17 |
| `paper/claude_vs_science_loglog_residual.png` | Same relationship after residualising log Claude usage and log papers per capita on log GDP per working-age person. | Same as above | 2026-09-17 |
| `paper/claude_vs_science_residual.png` | Same relationship after residualising Claude usage and papers per capita (levels) on GDP per working-age person. | Same as above | 2026-09-17 |
| `paper/claude_vs_ai_science.png` | Claude usage per-capita index against AI-related papers per 1,000 working-age people, 2023-2025; bubble size is AI paper count. | Same as above | 2026-09-17 |
| `paper/claude_vs_ai_science_loglog.png` | Same as `claude_vs_ai_science.png` on log-log axes. | Same as above | 2026-09-17 |
| `paper/claude_vs_ai_science_loglog_residual.png` | AI-paper version of the log-log GDP-residualised scatter. | Same as above | 2026-09-17 |
| `paper/claude_vs_ai_science_residual.png` | AI-paper version of the levels GDP-residualised scatter. | Same as above | 2026-09-17 |
