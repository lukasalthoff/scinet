# SciNet

SciNet is a database of the tasks researchers perform, across all scientific disciplines. It is modeled on O\*NET, the US Department of Labor's database of the tasks performed in every occupation. It was generated mainly with large language models and checked against published papers, laboratory protocols, and O\*NET's own data on scientific occupations.

Disciplines are organized in three levels: 6 domains (for example Social Sciences), 34 fields (Economics), and 318 subfields (Labor Economics). A task can belong to any level, or apply to all research. *"Collecting biological specimens"* is a Life Sciences task; *"conducting field excavations to recover human skeletal remains"* belongs to the subfield Biological & Physical Anthropology. The release holds 7,262 tasks: 30 that apply to all research (the "universal" tasks), 134 at the domain level, 321 at the field level, and 6,777 at the subfield level.

For each task the data give:

- the steps a researcher goes through to perform it;
- how long it takes;
- how important it is, how often it is done, and what share of researchers do it;
- descriptive scores such as how complex it is and how much of it is physical work.

Current release: **v1.6.1** ([changes](#changes)).

**Website:** [anatomyofscience.com](https://www.anatomyofscience.com/) · **Repository:** [github.com/lukasalthoff/scinet](https://github.com/lukasalthoff/scinet)

## Data files

All files are UTF-8, comma-separated CSV. [`data/README.md`](data/README.md) repeats the essentials for anyone who downloads only the data folder.

| File | Contents |
|------|----------|
| [`data/tasks.csv`](data/tasks.csv) | Every task, with its level, its place in the hierarchy, and its category |
| [`data/substeps.csv.gz`](data/substeps.csv.gz) | The steps each task breaks down into |
| [`data/task_time.csv`](data/task_time.csv) | How long each task takes, estimated separately in each subfield where it is performed |
| [`data/task_ratings.csv`](data/task_ratings.csv) | Importance, share of researchers, and frequency of each task, rated separately in each subfield |
| [`data/task_prevalence.csv`](data/task_prevalence.csv) | The share of a subfield's published papers that show the task being performed |
| [`data/task_dimensions.csv`](data/task_dimensions.csv) | Descriptive scores for every task. See [TASK_DIMENSIONS.md](TASK_DIMENSIONS.md) |
| [`data/substep_dimensions.csv.gz`](data/substep_dimensions.csv.gz) | The scores that are made step by step, for every substep |
| [`data/work_activities.csv`](data/work_activities.csv) | 140 work activities that group similar tasks. See [WORK_ACTIVITIES.md](WORK_ACTIVITIES.md) |
| [`data/task_activity_assignments.csv`](data/task_activity_assignments.csv) | The work activity each task belongs to |
| [`data/work_activity_dimensions.csv`](data/work_activity_dimensions.csv) | The descriptive scores averaged for each work activity |
| [`data/openalex_topic_subfield_mapping.csv`](data/openalex_topic_subfield_mapping.csv) | Maps the research topics of OpenAlex, an open catalogue of scholarly papers, to SciNet subfields. Used to decide which papers are sampled for a subfield |
| [`data/topic_frame_overlay.csv`](data/topic_frame_overlay.csv) | Extra topics used to find enough papers for some subfields |

## Data dictionary

### `tasks.csv`

| Column | Description |
|--------|-------------|
| `task` | The task statement |
| `category` | One of ten categories, for example "Data Gathering" or "Writing & Communication" |
| `level` | `universal`, `domain`, `field`, or `subfield` |
| `domain` | Domain name. Empty for universal tasks |
| `field` | Field name. Empty for universal and domain tasks |
| `subfield` | Subfield name. Empty for universal, domain, and field tasks |
| `expert_input` | The researcher whose review shaped this task, where one did. Empty otherwise |

Two subfield names, Political Economy and Educational Psychology, exist in two fields each, so always identify a subfield by its field and subfield together. 235 task statements appear in more than one subfield, with their own times and scores in each.

### `substeps.csv.gz`

Compressed (34.5 MB uncompressed, 7.8 MB compressed); `pandas.read_csv` opens it directly.

| Column | Description |
|--------|-------------|
| `level` | Level of the task |
| `domain`, `field`, `subfield` | Where the breakdown applies. A subfield task is broken down in its subfield, a field or domain task once for the field or domain, a universal task once per field. Columns that do not apply are empty |
| `task` | The task statement |
| `substep_id` | `S1`, `S2`, and so on, in the order the steps are done |
| `substep` | What the researcher does at this step |

### `task_time.csv`

The same task can mean different work in different subfields, so time is estimated separately for each subfield where the task is performed. Field and domain tasks are timed only where the model judges them to be performed, not in every subfield of their field or domain (2,662 of 3,099 field placements, 6,335 of 7,387 domain placements). Universal tasks are timed once per field, in 1,016 of the 1,020 task-field pairs (the rest the model judged not to apply in that field), so their `subfield` is empty. For a typical task timed in five or more subfields, the longest estimate is about 2.4 times the shortest for researcher hours and 3.6 times for elapsed hours.

| Column | Description |
|--------|-------------|
| `task`, `level`, `domain`, `field`, `subfield` | The task and the subfield (or field, for universal tasks) the estimate is for |
| `n_substeps` | Number of steps in the breakdown |
| `researcher_hours` | Hands-on work by the research team for one instance of the task |
| `elapsed_hours` | Calendar time for one instance, including waiting such as incubations, computing runs, or ethics review. Never less than `researcher_hours` |
| `confidence` | The model's confidence in the estimate: `high`, `medium`, or `low` |

Every task has steps and times except 2 subfield tasks, in Physiology and in Plant Pathology, which have no breakdown.

### `task_ratings.csv`

One row per task per subfield it appears in, on O\*NET's three scales. Each row is a single answer from a language model asked to rate as an experienced researcher in that subfield (see [METHODOLOGY](METHODOLOGY.md#4-rating-each-task)).

| Column | Description |
|--------|-------------|
| `task`, `level`, `domain`, `field`, `subfield` | The task and the subfield the rating is for |
| `importance` | 1 = Not Important, 2 = Somewhat Important, 3 = Important, 4 = Very Important, 5 = Extremely Important |
| `pct_researchers` | Out of 100 researchers in the subfield, how many perform this task at least occasionally |
| `frequency` | 1 = Yearly or less, 2 = More than yearly, 3 = More than monthly, 4 = More than weekly, 5 = Daily, 6 = More than daily, 7 = Hourly or more |
| `classification` | `Core` if `importance` is at least 3 and `pct_researchers` is at least 67, otherwise `Supplemental`. This is O\*NET's rule |

### `task_prevalence.csv`

The share of a subfield's sampled papers whose text shows the task being performed, judged by a language model reading each paper. The `source` column says how the row was measured. `judged` rows (tasks that existed before the paper-based expansion described in the methodology) come from a fixed sample of about 100 papers. `expansion` rows are the tasks that the expansion added: their share was measured on the same papers that suggested them, in batches of 25 to 100 with early stopping, so it runs a few points high. Tasks the expansion added but whose wording changed too much to be traced to a scored candidate have no row; nor do universal, domain, or field tasks.

| Column | Description |
|--------|-------------|
| `field`, `subfield` | The subfield the papers were drawn from |
| `task` | The task statement |
| `n_papers` | Papers judged for this task |
| `n_involved` | Papers in which the task was stated or clearly implied |
| `prevalence` | `n_involved` divided by `n_papers` |
| `source` | `judged` or `expansion`, see above |

### `openalex_topic_subfield_mapping.csv`

| Column | Description |
|--------|-------------|
| `topic_id` | OpenAlex topic number (the id without its "T" prefix) |
| `topic_name` | Topic name in OpenAlex |
| `domain`, `field`, `subfield` | The SciNet subfield the topic maps to |

The 4,481 topics are those that map to a SciNet subfield; OpenAlex topics that do not are left out.

## Documentation

- [METHODOLOGY.md](METHODOLOGY.md): how SciNet was built and validated.
- [TASK_DIMENSIONS.md](TASK_DIMENSIONS.md): the descriptive scores.
- [WORK_ACTIVITIES.md](WORK_ACTIVITIES.md): the work activities.
- [SURVEYS.md](SURVEYS.md): the questions of the researcher survey on the website.

For the research paper when available, and for project updates, see the [project page](https://www.lukasalthoff.com).

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

## Changes

| Version | Change |
|---------|--------|
| v1.6.1 | Prevalence rows added for 1,188 tasks from the paper-based expansion, marked `expansion` in a new `source` column. The 69 original domain-level tasks now appear on the website's subfield pages wherever they are performed, like every other task. |
| v1.6.0 | Ratings added for the three universal tasks that lacked them. Prevalence rebuilt so the two subfield names that exist in two fields are kept apart. Times re-estimated for the few rows that had been timed on a different breakdown. Universal tasks timed in the field-task pairs that were missing. Medium shares rescored where they did not sum to 100. Substep numbering made plain S1, S2, … throughout. Crosswalk restricted to topics that map to a live subfield. Figures regenerated. Documentation rewritten for plain reading. |
| v1.5.2 | Documentation corrected against the code and data; internal identifiers removed from the work-activity descriptions; crosswalk domains updated to the six-domain taxonomy |
| v1.5.1 | Work-activity averages count each task once |
| v1.5.0 | Complexity, physical-work, regulation, and AI-training scores recomputed step by step for every task; `substep_dimensions.csv.gz` added |
| v1.4.2 | Field-level tasks timed in every subfield where they are performed |
| v1.4.1 | Steps and times added for all domain-level and universal tasks |

## License

Data and documentation in this repository are licensed under CC BY 4.0. See [LICENSE](LICENSE).
