# SciNet data

The files of the SciNet release. The [main README](../README.md) describes every column; [TASK_DIMENSIONS.md](../TASK_DIMENSIONS.md) and [WORK_ACTIVITIES.md](../WORK_ACTIVITIES.md) cover the scores and the work activities.

| File | Contents | Columns |
|------|----------|---------|
| `tasks.csv` | Every task (7,262 rows) | `task`, `category`, `level`, `domain`, `field`, `subfield`, `expert_input` |
| `substeps.csv.gz` | The steps of each task (90,520 rows, compressed) | `level`, `domain`, `field`, `subfield`, `task`, `substep_id`, `substep` |
| `task_time.csv` | Hours per task, per subfield where it is performed | `task`, `level`, `domain`, `field`, `subfield`, `n_substeps`, `researcher_hours`, `elapsed_hours`, `confidence` |
| `task_ratings.csv` | Importance (1–5), share of researchers (0–100), frequency (1–7), per subfield | `task`, `level`, `domain`, `field`, `subfield`, `importance`, `pct_researchers`, `frequency`, `classification` |
| `task_prevalence.csv` | Share of a subfield's papers that perform the task | `field`, `subfield`, `task`, `n_papers`, `n_involved`, `prevalence`, `source` (`judged`: fixed 100-paper sample; `expansion`: from the expansion's scoring, leaving out the papers that proposed the task) |
| `task_dimensions.csv` | Descriptive scores for every task, same rows and order as `tasks.csv` | See TASK_DIMENSIONS.md |
| `substep_dimensions.csv.gz` | The step-by-step scores, same rows and order as `substeps.csv.gz` | Keys as in `substeps.csv.gz`, plus the score columns |
| `work_activities.csv` | The 140 work activities | `activity_id`, `universal_task_id`, `universal_task`, `category`, `activity_name`, `activity_description`, `n_tasks` |
| `task_activity_assignments.csv` | The work activity of each task, one row per task statement and level (6,956 rows) | `task`, `level`, `activity_id`, `universal_task_id` |
| `work_activity_dimensions.csv` | The scores averaged per work activity | As `task_dimensions.csv`, plus `pasteur_applies_share` and `n_tasks_scored` |
| `openalex_topic_subfield_mapping.csv` | OpenAlex topics mapped to SciNet subfields (4,481 topics) | `topic_id`, `topic_name`, `domain`, `field`, `subfield` |
| `topic_frame_overlay.csv` | Extra topics used to find enough papers for some subfields | `field`, `subfield_slug`, `topic_id`, `topic_name`, `confidence`, `reason`, `n_papers` |

Things to know when joining the files:

- Identify a subfield by `field` and `subfield` together. Two subfield names exist in two fields each.
- 235 task statements appear in more than one subfield, with their own rows in every file. Match rows on `task`, `level`, `domain`, `field` and `subfield` together, or, for `task_dimensions.csv`, by row position.
- In `substeps.csv.gz` and `substep_dimensions.csv.gz`, `domain` is filled only for domain-level tasks, and `subfield` is empty for field-level and universal tasks, because those breakdowns apply to the whole field or domain.
- Universal tasks are timed once per field, so their rows in `task_time.csv` have an empty `subfield`.
- `topic_frame_overlay.csv` names subfields by a slug: lowercase, `&` written as `and`, other punctuation as `_`.
- Empty cells: 2 subfield tasks have no steps, times, or step-by-step scores; a few scores are missing where the model declined to answer.
