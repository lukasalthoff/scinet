# SciNet

SciNet is a database of the tasks researchers perform, across all scientific disciplines. It is modeled on O\*NET, the US Department of Labor's database of the tasks performed in every occupation. It was generated mainly with large language models and checked against published papers, laboratory protocols, and O\*NET's own data on scientific occupations.

Disciplines are organized in three levels: 6 domains (for example Social Sciences), 34 fields (Economics), and 318 subfields (Labor Economics). A task can belong to any level, or apply to all research. *"Collecting biological specimens"* is a Life Sciences task; *"conducting field excavations to recover human skeletal remains"* belongs to the subfield Biological & Physical Anthropology. The release holds 7,262 tasks: 30 that apply to all research (the "universal" tasks), 134 at the domain level, 321 at the field level, and 6,777 at the subfield level.

For each task the data give:

- the steps a researcher goes through to perform it;
- how long it takes, and how many hours a year a researcher spends on it;
- how important it is, how often it is done, and what share of researchers do it;
- descriptive scores such as how complex it is and how much of it is physical work.

The release also counts the researchers active in each country, domain, field and subfield.

Current release: **v1.9.0**.

**Website:** [anatomyofscience.com](https://www.anatomyofscience.com/) · **Repository:** [github.com/lukasalthoff/scinet](https://github.com/lukasalthoff/scinet)

## Data files

All files are UTF-8, comma-separated CSV. [`data/README.md`](data/README.md) repeats the essentials for anyone who downloads only the data folder.

| File | Contents |
|------|----------|
| [`data/tasks.csv`](data/tasks.csv) | Every task, with its level, its place in the hierarchy, and its category |
| [`data/substeps.csv.gz`](data/substeps.csv.gz) | The steps each task breaks down into |
| [`data/task_time.csv`](data/task_time.csv) | How long each task takes, estimated separately in each subfield where it is performed |
| [`data/task_ratings.csv`](data/task_ratings.csv) | Importance, share of researchers, and frequency of each task, rated separately in each subfield |
| [`data/task_prevalence.csv`](data/task_prevalence.csv) | The share of published papers that show each task being performed: subfield tasks in their subfield; universal, domain, and field tasks by field, by domain, and for all of science |
| [`data/task_hours_per_year.csv`](data/task_hours_per_year.csv) | Hours a year a researcher spends on each task, in each subfield where it is performed. See [TIME_USE.md](TIME_USE.md) |
| [`data/task_dimensions.csv`](data/task_dimensions.csv) | Descriptive scores for every task. See [TASK_DIMENSIONS.md](TASK_DIMENSIONS.md) |
| [`data/substep_dimensions.csv.gz`](data/substep_dimensions.csv.gz) | The scores that are made step by step, for every substep |
| [`data/work_activities.csv`](data/work_activities.csv) | 140 work activities that group similar tasks. See [WORK_ACTIVITIES.md](WORK_ACTIVITIES.md) |
| [`data/task_activity_assignments.csv`](data/task_activity_assignments.csv) | The work activity each task belongs to |
| [`data/work_activity_dimensions.csv`](data/work_activity_dimensions.csv) | The descriptive scores averaged for each work activity |
| [`data/openalex_topic_subfield_mapping.csv`](data/openalex_topic_subfield_mapping.csv) | Maps the research topics of OpenAlex, an open catalogue of scholarly papers, to SciNet subfields. Used to decide which papers are sampled for a subfield |
| [`data/topic_frame_overlay.csv`](data/topic_frame_overlay.csv) | Extra topics used to find enough papers for some subfields |
| [`data/researchers.csv`](data/researchers.csv) | Researchers active in 2020, worldwide and by country, for every domain, field and subfield |

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

Every task has a step breakdown and a time estimate, in each place it is performed.

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

The share of published papers whose text shows a task being performed, judged by a language model reading each paper. One row per task and scope.

- **Subfield tasks** (scope `subfield`): the share of the subfield's sampled papers, judged by Claude Sonnet 5 on the first 20,000 characters of each paper. The `source` column says how the row was measured. `judged` rows are the tasks of the generated taxonomy, judged on a fixed sample of about 100 papers per subfield. `expansion` rows are the tasks that the paper-based expansion added (see the [methodology](METHODOLOGY.md)): their share comes from the expansion's own scoring of the subfield's papers, in batches of 25 to 100 with early stopping, leaving out the papers that proposed the task so that a task is not credited to the paper it was found in. An expansion task released under a wording shared by several subfields takes the scoring of its candidate in each of those subfields. Tasks that experts added to a subfield's list are judged on the same papers with the subfield's full task list.
- **Field tasks** (scope `field`, `domain`, or `all`): papers sampled per field from the subfield samples, each subfield counting in proportion to its share of the field's citations; 200 papers per field, each judged against all of its field's, domain's, and universal tasks at once by Claude Sonnet 5.5 on the first 20,000 characters of its text. Only the field tasks' shares come from this reading.
- **Domain and universal tasks** (scope `field`, `domain`, or `all`): the first half of each subfield's sampled papers (about 100 per field), judged by Claude Opus 5.5 on up to 50,000 characters of the text with the journal and year, and with an instruction to infer what producing and publishing the paper must have involved, because several of these tasks, such as drafting the manuscript or responding to reviewers, are rarely narrated in a paper. 45 papers that Opus declined to judge were judged by Claude Sonnet 5 with the same instructions.

A `field` row covers that field's papers; a `domain` or `all` row combines fields in proportion to their citations. Some universal tasks describe work that papers rarely reveal, such as teaching or serving on editorial boards; their shares are near zero and say little about how often researchers do them. Grant writing is understated: it is marked for 37% of the papers whose text acknowledges funding.

| Column | Description |
|--------|-------------|
| `task`, `level` | The task and its level: `subfield`, `field`, `domain`, or `universal` |
| `scope` | What the row covers: `subfield` (one subfield's papers), `field` (one field's papers), `domain` (the domain's fields combined), or `all` (all 34 fields combined) |
| `domain`, `field`, `subfield` | Where the row's papers come from; empty where the scope is wider |
| `n_papers` | Papers judged for this task within the scope |
| `n_involved` | Of those, papers in which the task was stated or clearly implied |
| `prevalence` | The share of papers performing the task. Subfield rows: `n_involved` divided by `n_papers`. Other rows are weighted by citations, so they can differ from that ratio |
| `se` | Standard error of `prevalence`: the binomial standard error for subfield rows, the standard error of the weighted share otherwise; 0 when all or none of the papers perform the task |
| `source` | `judged` or `expansion` (subfield tasks, see above); `judged` for all other rows |
| `judge` | The model that judged the papers: `Claude Sonnet 5` (subfield tasks), `Claude Sonnet 5.5` (field tasks), or `Claude Opus 5.5` (domain and universal tasks) |
| `text` | What the model read of each paper |

### `openalex_topic_subfield_mapping.csv`

| Column | Description |
|--------|-------------|
| `topic_id` | OpenAlex topic number (the id without its "T" prefix) |
| `topic_name` | Topic name in OpenAlex |
| `domain`, `field`, `subfield` | The SciNet subfield the topic maps to |

The 4,481 topics are those that map to a SciNet subfield; OpenAlex topics that do not are left out.

### `researchers.csv`

The number of researchers active in 2020, worldwide and in each of 226 countries, for all of research and for every SciNet domain, field and subfield. Counted from OpenAlex (January 2026 snapshot), an open catalogue of scholarly papers and their authors.

- **Active in 2020**: the researcher published at least one paper in or before 2020 and at least one in or after 2020.
- **Domain, field and subfield**: each paper is placed in the SciNet subfield of its OpenAlex primary topic, through [`openalex_topic_subfield_mapping.csv`](data/openalex_topic_subfield_mapping.csv). A researcher counts in the field where most of their papers fall, and in the most common subfield within that field; ties go to the field of their most recent paper. Researchers none of whose papers has a mapped topic are `Unclassified` (832,530 worldwide).
- **Country**: the most common country of the researcher's institutions on their 2016–2024 papers (on all their papers if none falls in those years). 3.27 million of the 17.64 million active researchers have no institution country; they count in `World` and in `Unknown`.
- **Fractional counts** split each researcher across fields (subfields) in proportion to their papers, so a researcher with three economics papers and one statistics paper adds 0.75 to Economics and 0.25 to Statistics. They are less sensitive to the main-field rule; domain rows sum the field rows.

| Column | Description |
|--------|-------------|
| `country_code` | ISO 3166-1 alpha-2 code; empty for `World` and `Unknown` |
| `country` | Country name, `World` (all researchers), or `Unknown` (researchers with no institution country) |
| `level` | `all` (every researcher of the country), `domain`, `field`, or `subfield` |
| `domain`, `field`, `subfield` | The row's place in the taxonomy; empty above the row's level |
| `researchers` | Active researchers whose main field (subfield) this is |
| `researchers_2plus_papers`, `researchers_5plus_papers`, `researchers_10plus_papers` | The same, counting only researchers with at least 2, 5 or 10 papers in their career |
| `researchers_fractional`, `researchers_5plus_papers_fractional` | Fractional counts, all researchers and researchers with at least 5 papers |

Within a country, the rows of each level sum to the `all` row; fractional counts agree up to rounding. Rows where every count is zero are left out.

OpenAlex counts everyone who publishes, so the totals are larger than employment-based statistics: country totals correlate with UNESCO's researcher headcounts at 0.94 (logs, 153 countries) and are 1.4 times as large at the median. Clinical medicine weighs heavily (Medicine & Clinical Sciences holds 30% of researchers but 16% of papers), because medical papers have many authors. Small cells are noisy: 18,550 of the 43,672 country-subfield rows with researchers count fewer than 10, and for a fifth of those the main-field and fractional counts differ by more than a factor of two. The 78 countries with at least 10,000 active researchers hold 98% of the researchers with a known country. OpenAlex sometimes merges different people into one author profile. The counts are built from the full OpenAlex snapshot and cannot be rebuilt from this repository.

## Documentation

- [METHODOLOGY.md](METHODOLOGY.md): how SciNet was built and validated.
- [TIME_USE.md](TIME_USE.md): hours a year per task; slides in [slides/time_use.pdf](slides/time_use.pdf).
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

## License

Data and documentation in this repository are licensed under CC BY 4.0. See [LICENSE](LICENSE).
