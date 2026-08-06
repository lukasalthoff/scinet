# SciNet Release Data

Flat, self-contained CSV exports of the SciNet taxonomy and tasks.

## Files

| File | Description |
|------|-------------|
| `tasks.csv` | Every task in the hierarchy. Columns: `task`, `category`, `level`, `domain`, `field`, `subfield`, `expert_input`. Level is one of "universal" (applies to all researchers), "domain" (e.g. Social Sciences), "field" (e.g. Economics), or "subfield" (e.g. Labor Economics). Higher-level columns are empty when a task belongs to a broader level. `expert_input` names the researcher whose review produced the wording and is empty otherwise — the same flag the website shows as a gold seal. |
| `substeps.csv.gz` | How each task decomposes into the steps a researcher performs. Columns: `level`, `domain`, `field`, `subfield`, `task`, `substep_id`, `substep`. Gzipped; `pandas.read_csv` reads it directly. |
| `task_time.csv` | How long each task takes, estimated separately for every subfield it appears in. Columns: `task`, `level`, `domain`, `field`, `subfield`, `n_substeps`, `researcher_hours` (attended effort), `elapsed_hours` (including unattended waiting), `confidence`. |
| `task_ratings.csv` | Importance, reach, and frequency of each task, rated separately for every subfield it appears in, on O\*NET's scales. Columns: `task`, `level`, `domain`, `field`, `subfield`, `importance` (1–5), `pct_researchers` (0–100, share of researchers in the subfield who do it at least occasionally — this is O\*NET's "Relevance of Task" scale, which they publish as a 0–100 share), `frequency` (1 = yearly or less to 7 = hourly or more), `classification` (`Core` if `importance` ≥ 3 and `pct_researchers` ≥ 67, else `Supplemental`). |
| `task_prevalence.csv` | Observed share of a subfield's papers that perform each task, read from full text — the empirical yardstick for the ratings. Columns: `field`, `subfield`, `task`, `n_papers`, `n_involved`, `prevalence`. Subfield-level tasks in 316 subfields only. |
| `openalex_topic_subfield_mapping.csv` | Maps each OpenAlex topic to its display domain, field, and subfield. Columns: `topic_id`, `topic_name`, `domain`, `field`, `subfield`. |

Ratings are validated against O\*NET expert ratings (r = 0.66 / 0.63 / 0.75) and against
observed prevalence (rho = 0.56 / 0.61 / 0.53). The time estimates in `task_time.csv`
are **not** externally validated — see the Validation section of the top-level
[README](../README.md).
