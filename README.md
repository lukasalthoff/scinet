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
| [`data/substep_dimensions.csv.gz`](data/substep_dimensions.csv.gz) | The scores that are made step by step, for every substep (empty for the 43 steps of four universal task-field pairs, see [TASK_DIMENSIONS.md](TASK_DIMENSIONS.md)) |
| [`data/work_activities.csv`](data/work_activities.csv) | 140 work activities that group similar tasks. See [WORK_ACTIVITIES.md](WORK_ACTIVITIES.md) |
| [`data/task_activity_assignments.csv`](data/task_activity_assignments.csv) | The work activity each task belongs to |
| [`data/work_activity_dimensions.csv`](data/work_activity_dimensions.csv) | The descriptive scores averaged for each work activity |
| [`data/rl_index.csv`](data/rl_index.csv) | The RL feasibility index of every task, one number combining the three RL scores, plus a version fitted on core research (paper) tasks only. See [TASK_DIMENSIONS.md](TASK_DIMENSIONS.md#rl-feasibility-index) |
| [`data/rl_index_subfields.csv`](data/rl_index_subfields.csv) | The RL feasibility index per subfield, averaged over the hours a researcher spends on each task, for all tasks and for paper tasks |
| [`data/rl_index_pca.json`](data/rl_index_pca.json) | The constants of the RL feasibility index |
| [`data/openalex_topic_subfield_mapping.csv`](data/openalex_topic_subfield_mapping.csv) | Maps the research topics of OpenAlex, an open catalogue of scholarly papers, to SciNet subfields. Used to decide which papers are sampled for a subfield |
| [`data/topic_frame_overlay.csv`](data/topic_frame_overlay.csv) | Extra topics used to find enough papers for some subfields |
| [`data/researchers.csv`](data/researchers.csv) | Researchers active in 2020 with at least 5 papers, worldwide and by country, for every domain, field and subfield, estimated from a sample whose papers a language model read |

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

The same task can mean different work in different subfields, so time is estimated separately for each subfield where the task is performed. Field and domain tasks are timed in every subfield of their field or domain (3,099 field and 7,387 domain placements); 1,489 of these are timed by Claude Opus 5.5 and scaled to the other times (see [METHODOLOGY.md](METHODOLOGY.md#5-substeps-and-time-estimates)). Universal tasks are timed once per field, in all 1,020 task-field pairs, so their `subfield` is empty; four of these pairs are broken down and timed by Claude Opus 5.5 and scaled the same way. For a typical task timed in five or more subfields, the longest estimate is about 2.5 times the shortest for researcher hours and 4.0 times for elapsed hours.

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

The number of researchers active in 2020 with at least 5 papers, worldwide and in each of 223 countries, for all of research and for every SciNet domain, field and subfield. The researchers come from OpenAlex (January 2026 snapshot), an open catalogue of scholarly papers and their authors. Each researcher's subfield is named by a language model that read their papers. The model reads a random sample of 746,517 of the 10.84 million researchers, drawn separately in each country, and the counts are estimated from it, with standard errors.

- **Researchers**: OpenAlex authors with at least 5 papers who published at least one paper in or before 2020 and at least one in or after 2020.
- **Subfield**: Claude Haiku 5.5 reads up to 40 of the researcher's papers, those nearest to 2020, with the year, journal and title of each, and names the one SciNet subfield that best describes the researcher's work. It was checked on 1,500 researchers whom Claude Sonnet 5.5 also labelled, with up to 100 papers each, including abstracts. Haiku names Sonnet's subfield for 74% of them and Sonnet's field for 85%. Sonnet itself gives the same subfield on a second run for 85%. Counting a researcher in the most common subfield of their papers, as placed by a text classifier of single papers, matches Sonnet's subfield for 62% and its field for 77%. Researchers whose papers the model judged to include no scholarly work (0.15%) are `Unclassified` at every level.
- **Country**: the country of the researcher's institutions on their papers nearest to 2020, the most common one if those papers name several. 571,466 researchers have no institution country on any paper; they are `Unknown`.
- **Sample**: each country, and `Unknown`, is sampled at random on its own, with a larger share of researchers in smaller countries. The `labelled_researchers` column of a country's `all` row gives its sample size.
- **Estimates**: a country's count for a subfield is its number of researchers times the share of its sampled researchers in that subfield. The standard error is that of simple random sampling without replacement within the country. `World` rows add up the countries, and their standard errors combine the countries' as independent. The standard errors cover sampling only, not errors of the model. Of the country-field rows with at least 1,000 researchers, 91% have a standard error below 10% of the estimate and over 99% below 20%. Of the country-subfield rows with at least 1,000 researchers, 54% are below 10% and 99% below 20%.
- **Left out**: Niue and Tuvalu (8 researchers), none of whose researchers has been labelled. A subfield in which none of a country's sampled researchers falls has no row for that country.

| Column | Description |
|--------|-------------|
| `country_code` | ISO 3166-1 alpha-2 code; empty for `World` and `Unknown` |
| `country` | Country name, `World` (all researchers), or `Unknown` (researchers with no institution country) |
| `level` | `all` (every researcher of the country), `domain`, `field`, or `subfield` |
| `domain`, `field`, `subfield` | The row's place in the taxonomy; empty above the row's level |
| `researchers` | Estimated number of researchers whose domain, field or subfield this is. In `all` rows, the exact number of the country's researchers |
| `se` | Standard error of `researchers`; 0 in `all` rows |
| `labelled_researchers` | Sampled researchers labelled in this row |

Up to rounding, the rows of each level sum to their country's `all` row, and the `World` rows sum the countries.

OpenAlex counts everyone who publishes, so the totals are larger than employment-based counts of researchers. It sometimes merges different people into one author profile, and some profiles are not researchers. In Panama about 40% of the profiles list mostly uploads to the Zenodo repository, such as photographs and 3D models of buildings and objects from many countries. The model leaves a little over half of them `Unclassified` and places most of the rest in Archaeology and the arts. Elsewhere such profiles are rare (0.07% of labelled researchers). Rows that rest on few labelled researchers are noisy, `se` shows how much, and 32 countries have fewer than 30 labelled researchers. The counts are built from the full OpenAlex snapshot and cannot be rebuilt from this repository.

## Documentation

- [METHODOLOGY.md](METHODOLOGY.md): how SciNet was built and validated.
- [TIME_USE.md](TIME_USE.md): hours a year per task; slides in [slides/time_use.pdf](slides/time_use.pdf).
- [TASK_DIMENSIONS.md](TASK_DIMENSIONS.md): the descriptive scores.
- [WORK_ACTIVITIES.md](WORK_ACTIVITIES.md): the work activities.
- [SURVEYS.md](SURVEYS.md): the questions of the researcher survey on the website.

For the research paper when available, and for project updates, see the [project page](https://www.lukasalthoff.com).

## Citation

If you use this dataset, please cite:

Lukas Althoff (2026): "Artificial Intelligence and Knowledge Production," Working Paper.

Cristian Alamos and Lukas Althoff (2026): "SciNet: The Anatomy of Science" [dataset], https://www.anatomyofscience.com.

```bibtex
@unpublished{althoff_ai_knowledge,
  title        = {Artificial Intelligence and Knowledge Production},
  author       = {Althoff, Lukas},
  year         = {2026},
  note         = {Working Paper},
}

@misc{scinet_data,
  title        = {SciNet: The Anatomy of Science},
  author       = {Alamos, Cristian and Althoff, Lukas},
  year         = {2026},
  howpublished = {\url{https://www.anatomyofscience.com}},
  note         = {Dataset},
}
```

## Funding

We thank Stanford Impact Labs and Anthropic for financial support that helped construct SciNet and make it publicly available.

## License

Data and documentation in this repository are licensed under CC BY 4.0. See [LICENSE](LICENSE).
