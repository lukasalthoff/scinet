# SciNET

Public replication data for **SciNET**: an O*NET-style task database for scientific research across OpenAlex topics, fields, and subfields.

**Repository:** [github.com/lukasalthoff/scinet](https://github.com/lukasalthoff/scinet)

## Overview

SciNET organizes research work into a hierarchy aligned with [OpenAlex](https://openalex.org/) (domains, fields, subfields, and topics). For each level, we generate O*NET-style task statements and assess **AI augmentation** (estimated time savings from generative AI) and **automation exposure** (T0–T4 tiers).

The files in [`data/`](data/) are released for replication and downstream research.

## Data files

All files are UTF-8. CSVs use comma separators; fields may contain quoted newlines (especially in `task_automation.csv`).

| File | Description |
|------|-------------|
| [`data/openalex_topics.csv`](data/openalex_topics.csv) | Topic metadata and hierarchy (topic → subfield → field → domain), keywords, summaries, Wikipedia links |
| [`data/generated_tasks.csv`](data/generated_tasks.csv) | Generated task statements with stable `task_id` and hierarchy labels |
| [`data/task_augmentation.csv`](data/task_augmentation.csv) | Per-task **augmentation_score** (0–100), interpreted as estimated percentage time savings from GenAI assistance |
| [`data/task_automation.csv`](data/task_automation.csv) | Per-task **automation_score** (T0–T4) and explanatory text |
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

**`task_augmentation.csv`**

| Column | Description |
|--------|-------------|
| `task_id`, `field`, `subfield`, `topic`, `task` | Keys and text |
| `augmentation_score` | Float in **0–100** (percentage time savings) |
| `error` | Empty if successful; otherwise error detail |

**`task_automation.csv`**

| Column | Description |
|--------|-------------|
| `task_id`, `task` | Keys and text |
| `automation_score` | **T0**–**T4** exposure tier |
| `explanation` | Model-generated rationale (may span lines inside quotes) |
| `error` | Empty if successful |

**Automation tiers (summary)**

| Tier | Meaning (summary) |
|------|-------------------|
| T0–T4 | Increasing automation exposure; see explanations in-file for precise definitions used in this release |

**`catalog.json`**

JSON document with keys such as `version`, aggregate counts (fields, subfields, topics, tasks), and nested structures for browsing (aligned with the public SciNET explorer). Schema may evolve across releases; inspect the file for the current shape.

## Methodology (brief)

1. **Hierarchy:** OpenAlex domains, fields, subfields, and topics define the taxonomy.
2. **Task generation:** Large language models produce O*NET-style task statements at field, subfield, and topic levels.
3. **Augmentation:** Each task receives an **augmentation_score** from 0–100.
4. **Automation:** Each task receives a **T0–T4** classification with a written rationale.

For full methodological detail and citations, see the research paper when available and the [Stanford project page](https://www.lukasalthoff.com) (updates linked from the authors).

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

- Initial public release: topic table, generated tasks, augmentation and automation scores, and `catalog.json`.
