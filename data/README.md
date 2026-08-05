# SciNet Release Data

Flat, self-contained CSV exports of the SciNet taxonomy and tasks.

## Files

| File | Description |
|------|-------------|
| `tasks.csv` | Every task in the hierarchy. Columns: `task`, `category`, `level`, `domain`, `field`, `subfield`, `expert_input`. Level is one of "universal" (applies to all researchers), "domain" (e.g. Social Sciences), "field" (e.g. Economics), or "subfield" (e.g. Labor Economics). Higher-level columns are empty when a task belongs to a broader level. `expert_input` names the researcher whose review produced the wording and is empty otherwise — the same flag the website shows as a gold seal. |
| `substeps.csv.gz` | How each task decomposes into the steps a researcher performs. Columns: `level`, `domain`, `field`, `subfield`, `task`, `substep_id`, `substep`. Gzipped; `pandas.read_csv` reads it directly. |
| `task_time.csv` | How long each task takes, estimated separately for every subfield it appears in. Columns: `task`, `level`, `domain`, `field`, `subfield`, `n_substeps`, `researcher_hours` (attended effort), `elapsed_hours` (including unattended waiting), `confidence`. |
| `openalex_topic_subfield_mapping.csv` | Maps each OpenAlex topic to its display domain, field, and subfield. Columns: `topic_id`, `topic_name`, `domain`, `field`, `subfield`. |
