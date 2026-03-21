# SciNET

Public replication data for **SciNET**: an O\*NET-style task database for scientific research across OpenAlex topics, fields, and subfields.

**Repository:** [github.com/lukasalthoff/scinet](https://github.com/lukasalthoff/scinet)

## Overview

SciNET organizes research work into a hierarchy aligned with [OpenAlex](https://openalex.org/) (domains, fields, subfields, and topics). For each level, we use large language models to generate O\*NET-style task statements describing what researchers in that area regularly do.

The files in [`data/`](data/) are released for replication and downstream research.

## Data files

All files are UTF-8. CSVs use comma separators. See [`data/README.md`](data/README.md) for a standalone description.

| File | Description |
|------|-------------|
| [`data/tasks.csv`](data/tasks.csv) | Every task in the hierarchy (universal, domain, and subfield levels) with category labels |
| [`data/openalex_topic_subfield_mapping.csv`](data/openalex_topic_subfield_mapping.csv) | Maps each OpenAlex topic to its SciNET display field and subfield |

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
| `field` | SciNET display field |
| `subfield` | SciNET display subfield |

## Methodology

1. **Hierarchy:** OpenAlex domains, fields, subfields, and topics define the taxonomy.
2. **Task generation:** Large language models produce O\*NET-style task statements at field, subfield, and topic levels using a top-down hierarchical approach.

For a complete description of every pipeline step — including prompt design, coverage thresholds, O\*NET calibration results, and protocols.io validation — see **[METHODOLOGY.md](METHODOLOGY.md)**.

For the research paper when available and project updates, see the [Stanford project page](https://www.lukasalthoff.com).

## Citation

If you use this dataset, please cite the SciNET project and this repository, for example:

```bibtex
@misc{scinet_data,
  title        = {SciNET: Task Database for Scientific Research (Replication Data)},
  author       = {Althoff, Lukas and collaborators},
  year         = {2026},
  howpublished = {\url{https://github.com/lukasalthoff/scinet}},
  note         = {Version matching release commit; see repository for file manifest}
}
```

Adjust author list and year when the official paper DOI is available.

## License

Data and documentation in this repository are licensed under **CC BY 4.0** — see [LICENSE](LICENSE).

## Changelog

### 2026-03-20

- Replaced `generated_tasks.csv`, `openalex_topics.csv`, and `catalog.json` with two simpler files:
  - `tasks.csv`: flat task file with category, level, domain, field, and subfield columns.
  - `openalex_topic_subfield_mapping.csv`: maps OpenAlex topics to SciNET display fields and subfields.
- Added [`METHODOLOGY.md`](METHODOLOGY.md): full pipeline documentation covering taxonomy construction, hierarchical task generation, O\*NET-style rating and filtering, AI exposure scoring, O\*NET calibration, and protocols.io validation.
