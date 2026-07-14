# SciNet

A task-level database of scientific research — a comprehensive map of what researchers actually do, broken down by domain, field, subfield, and topic. SciNet enables rigorous, task-level analysis of scientific work by mapping the granular activity structure of science across 5 domains, 34 fields, 320 subfields, and 4,516 topics, with 5,044 released task statements (27 universal, 45 domain, and 4,972 subfield-level).

**Website:** [anatomyofscience.com](https://www.anatomyofscience.com/) · **Repository:** [github.com/lukasalthoff/scinet](https://github.com/lukasalthoff/scinet)

## Overview

SciNet organizes research work into a hierarchy aligned with [OpenAlex](https://openalex.org/) (domains, fields, subfields, and topics). For each level, we use large language models to generate O\*NET-style task statements describing what researchers in that area regularly do.

The files in [`data/`](data/) are released for replication and downstream research.

## Data files

All files are UTF-8. CSVs use comma separators. See [`data/README.md`](data/README.md) for a standalone description.

| File | Description |
|------|-------------|
| [`data/tasks.csv`](data/tasks.csv) | Every task in the hierarchy (universal, domain, and subfield levels) with category labels |
| [`data/openalex_topic_subfield_mapping.csv`](data/openalex_topic_subfield_mapping.csv) | Maps each OpenAlex topic to its SciNet display domain, field, and subfield |

### Data dictionary

**`tasks.csv`**

| Column | Description |
|--------|-------------|
| `task` | Task statement text |
| `category` | Task category (e.g. "Ideation & Hypothesis Generation", "Data Gathering") |
| `level` | One of `universal`, `domain`, or `subfield` |
| `domain` | Domain name, e.g. "Social Sciences" (empty for universal tasks) |
| `field` | Display field name, e.g. "Economics" (empty for universal/domain tasks) |
| `subfield` | Display subfield name, e.g. "Labor Economics" (empty for universal/domain tasks) |

**`openalex_topic_subfield_mapping.csv`**

| Column | Description |
|--------|-------------|
| `topic_id` | OpenAlex topic identifier |
| `topic_name` | Topic display name |
| `domain` | SciNet display domain |
| `field` | SciNet display field |
| `subfield` | SciNet display subfield |

## Methodology

<p align="center"><img src="https://raw.githubusercontent.com/lukasalthoff/scinet/main/pipeline.svg" alt="SciNet pipeline diagram" width="680"/></p>

1. **Hierarchy:** OpenAlex domains, fields, subfields, and topics define the taxonomy.
2. **Task generation:** Large language models produce O\*NET-style task statements at field, subfield, and topic levels using a top-down hierarchical approach.

For a complete description of every pipeline step — including prompt design, coverage thresholds, O\*NET calibration results, and protocols.io validation — see **[METHODOLOGY.md](METHODOLOGY.md)**.

For visual summaries of the data — task distributions, verifiability rankings, AI adoption — see **[DATA_OVERVIEW.md](DATA_OVERVIEW.md)**.

For the research paper when available and project updates, see the [Stanford project page](https://www.lukasalthoff.com).

## Citation

If you use this dataset, please cite the SciNet project and this repository, for example:

```bibtex
@misc{scinet_data,
  title        = {SciNet: The Anatomy of Science},
  author       = {Althoff, Lukas},
  year         = {2026},
  howpublished = {\url{https://github.com/lukasalthoff/scinet}},
}
```

## License

Data and documentation in this repository are licensed under **CC BY 4.0** — see [LICENSE](LICENSE).

## Changelog

### 2026-07-13

- Refreshed `tasks.csv` to match the live site: **5,044 task statements** across
  **34 fields** and **320 subfields** (previously 4,981 / 30 / 315).
- Adds four fields that were introduced after the March release: **Public Health &
  Epidemiology**, **Nutrition & Dietetics**, **Veterinary Medicine**, and
  **Library & Information Science**.
- Corrected the headline counts in `README.md` and `DATA_OVERVIEW.md`, which still
  described the March hierarchy (and quoted a task count that included
  topic-level statements not present in `tasks.csv`).
- **Realigned the `domain` column with the site's five display domains.** Previously
  the released file used an older four-domain grouping in which Arts, History,
  Languages & Linguistics, Literature, Philosophy and Religion were labelled
  *Social Sciences*, and Neuroscience was labelled *Health Sciences* — neither
  matching what the website shows. All 34 fields now carry the same domain as
  [anatomyofscience.com](https://www.anatomyofscience.com/).

**Known gaps (not yet released):**

- **Arts & Humanities has no domain-level tasks.** The 45 domain tasks cover only
  four domains; the humanities fields currently inherit none. TODO: author them.

- **Substeps.** Each subfield-level task decomposes into substeps; these are not yet
  part of the public release. TODO: publish once the decomposition is regenerated.
- **Substeps for the four new fields.** The substep decomposition predates them, so
  Public Health & Epidemiology, Nutrition & Dietetics, Veterinary Medicine and
  Library & Information Science currently have no substeps. TODO: generate.

### 2026-03-20

- Replaced `generated_tasks.csv`, `openalex_topics.csv`, and `catalog.json` with two simpler files:
  - `tasks.csv`: flat task file with category, level, domain, field, and subfield columns.
  - `openalex_topic_subfield_mapping.csv`: maps OpenAlex topics to SciNet display domains, fields, and subfields.
- Added [`METHODOLOGY.md`](METHODOLOGY.md): full pipeline documentation covering taxonomy construction, hierarchical task generation, O\*NET-style rating and filtering, AI exposure scoring, O\*NET calibration, and protocols.io validation.
