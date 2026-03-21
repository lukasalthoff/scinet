# SciNET

Public replication data for **SciNET**: an O\*NET-style task database for scientific research across OpenAlex topics, fields, and subfields.

**Repository:** [github.com/lukasalthoff/scinet](https://github.com/lukasalthoff/scinet)

## Overview

SciNET organizes research work into a hierarchy aligned with [OpenAlex](https://openalex.org/) (domains, fields, subfields, and topics). For each level, we use large language models to generate O\*NET-style task statements describing what researchers in that area regularly do.

The files in [`data/`](data/) are released for replication and downstream research.

## Data files

All files are UTF-8. CSVs use comma separators.

| File | Description |
|------|-------------|
| [`data/openalex_topics.csv`](data/openalex_topics.csv) | Topic metadata and hierarchy (topic → subfield → field → domain), keywords, summaries, Wikipedia links |
| [`data/generated_tasks.csv`](data/generated_tasks.csv) | Generated task statements with stable `task_id` and hierarchy labels |
| [`data/catalog.json`](data/catalog.json) | Aggregated catalog: version, counts, field/subfield/topic structure, and summary statistics used in the SciNET explorer |

### Data dictionary

**`openalex_topics.csv`**

| Column | Description |
|--------|-------------|
| `topic_id` | OpenAlex topic identifier |
| `old_topic_label`, `new_topic_label` | Topic labels (label refresh may differ) |
| `subfield_id`, `subfield_name` | OpenAlex subfield |
| `field_id`, `field_name` | OpenAlex field |
| `domain_id`, `domain_name` | OpenAlex domain |
| `keywords` | Semicolon-separated keywords |
| `summary` | Short topical summary |
| `wikipedia_url` | Related Wikipedia article when available |

**`generated_tasks.csv`**

| Column | Description |
|--------|-------------|
| `task_id` | Stable identifier (`task_######`) |
| `level` | One of `field`, `subfield`, `topic` |
| `field`, `subfield`, `topic` | Hierarchy labels (blank where not applicable) |
| `task` | Task statement text |
| `source_path` | Provenance path in the generation pipeline |

**`catalog.json`**

JSON document with keys such as `version`, aggregate counts (fields, subfields, topics, tasks), and nested structures for browsing (aligned with the public SciNET explorer). Schema may evolve across releases; inspect the file for the current shape.

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

- Removed `task_augmentation.csv` and `task_automation.csv` — AI exposure scores are not yet published.
- Added [`METHODOLOGY.md`](METHODOLOGY.md): full pipeline documentation covering taxonomy construction, hierarchical task generation, O\*NET-style rating and filtering, AI exposure scoring, O\*NET calibration, and protocols.io validation.
- Initial public release: topic table, generated tasks, and `catalog.json`.
