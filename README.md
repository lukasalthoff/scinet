# SciNet

SciNet is a task-level database of scientific research. For every scientific discipline it lists the tasks that researchers perform, organised into 6 domains, 34 fields, and 318 subfields. The release contains 7,259 task statements: 27 that apply to research everywhere, 134 at the domain level, 321 at the field level, and 6,777 at the subfield level. Every task also comes with a breakdown into substeps, an estimate of how long it takes, and ratings of how important it is, what share of researchers do it, and how often they do it. Those ratings and time estimates are given separately for each subfield in which a task appears.

**Website:** [anatomyofscience.com](https://www.anatomyofscience.com/) · **Repository:** [github.com/lukasalthoff/scinet](https://github.com/lukasalthoff/scinet)

## Overview

Each task is filed at the level it belongs to. A universal task applies to research everywhere, a domain or field task applies to a whole domain or field, and a subfield task applies to one subfield. A subfield therefore inherits the broader tasks above it instead of repeating them.

Task statements are written by large language models and then measured against published papers. A model reads each paper and decides, task by task, whether the paper performed that task. The share of papers that did is the task's prevalence, released in `task_prevalence.csv`. A newly proposed task enters the taxonomy once it is performed in at least 5% of a subfield's papers.

The files in [`data/`](data/) are released for replication and downstream research.

## Data files

All files are UTF-8 and CSVs use comma separators. See [`data/README.md`](data/README.md) for a standalone description.

| File | Description |
|------|-------------|
| [`data/tasks.csv`](data/tasks.csv) | Every task in the hierarchy, at the universal, domain, field, and subfield levels, with category labels |
| [`data/substeps.csv.gz`](data/substeps.csv.gz) | How each task breaks down into the steps a researcher performs |
| [`data/task_time.csv`](data/task_time.csv) | How long each task takes, estimated separately for every subfield it appears in |
| [`data/task_ratings.csv`](data/task_ratings.csv) | How important each task is, what share of researchers do it, and how often, rated separately for every subfield it appears in |
| [`data/task_prevalence.csv`](data/task_prevalence.csv) | The share of a subfield's papers that perform each task, read from the papers themselves |
| [`data/openalex_topic_subfield_mapping.csv`](data/openalex_topic_subfield_mapping.csv) | Crosswalk from OpenAlex topics to SciNet subfields, used to assign a paper to a subfield. Topics are not a level of the taxonomy and carry no tasks of their own |

### Data dictionary

**`tasks.csv`**

| Column | Description |
|--------|-------------|
| `task` | Task statement text |
| `category` | Task category, for example "Ideation & Hypothesis Generation" or "Data Gathering" |
| `level` | One of `universal`, `domain`, `field`, or `subfield` |
| `domain` | Domain name, for example "Social Sciences". Empty for universal tasks |
| `field` | Field name, for example "Economics". Empty for universal and domain tasks |
| `subfield` | Subfield name, for example "Labor Economics". Empty for universal, domain, and field tasks |

**`openalex_topic_subfield_mapping.csv`**

| Column | Description |
|--------|-------------|
| `topic_id` | OpenAlex topic identifier |
| `topic_name` | Topic display name |
| `domain` | SciNet domain |
| `field` | SciNet field |
| `subfield` | SciNet subfield |

**`substeps.csv.gz`** is gzipped, 32 MB plain and 7 MB compressed. `pandas.read_csv` opens it directly.

| Column | Description |
|--------|-------------|
| `level` | Level the task is filed at |
| `domain`, `field`, `subfield` | Scope the breakdown was written for. A subfield task is broken down in its own subfield, a field or domain task once for that field or domain, and a universal task once per field |
| `task` | Task statement text |
| `substep_id` | `S1`, `S2`, and so on, in workflow order |
| `substep` | What the researcher does at this step |

**`task_time.csv`** has one row per task per subfield it appears in, because the same task is a different job in different subfields. Across the 140 tasks that reach five or more subfields, the median task varies by a factor of 2.5 in `researcher_hours` between its cheapest and its most expensive subfield, and by a factor of 4.1 in `elapsed_hours`.

| Column | Description |
|--------|-------------|
| `task` | Task statement text |
| `level` | Level the task is filed at |
| `domain`, `field`, `subfield` | Where this estimate applies |
| `n_substeps` | Number of substeps in the breakdown |
| `researcher_hours` | Attended human effort for one instance of the task, summed over substeps as repetitions times minutes |
| `elapsed_hours` | Calendar time for one instance, including unattended waiting such as incubations, cluster jobs, and review boards. Never less than `researcher_hours` |
| `confidence` | Most common per-substep confidence: `high`, `medium`, or `low` |

Both time columns are model estimates rather than measurements. They assume a competent researcher with the standard tools of the subfield and no generative AI assistant, so they describe the work as it was done before LLM assistance.

**`task_ratings.csv`** has one row per task per subfield it appears in. The three scales are taken from O\*NET, where they are called Importance, Relevance of Task, and Frequency of Task, so SciNet ratings can be compared against occupational data directly. O\*NET publishes Relevance as the share of workers for whom the task is part of the job. It is released here as `pct_researchers`, since in a research setting the population is researchers.

| Column | Description |
|--------|-------------|
| `task` | Task statement text |
| `level` | Level the task is filed at |
| `domain`, `field`, `subfield` | Subfield this rating was made for |
| `importance` | 1 = Not Important, 2 = Somewhat Important, 3 = Important, 4 = Very Important, 5 = Extremely Important |
| `pct_researchers` | Out of 100 researchers in the subfield, how many perform this task at least occasionally. Range 0 to 100 |
| `frequency` | 1 = Yearly or less, 2 = More than yearly, 3 = More than monthly, 4 = More than weekly, 5 = Daily, 6 = More than daily, 7 = Hourly or more |
| `classification` | `Core` if `importance` is at least 3 and `pct_researchers` is at least 67, otherwise `Supplemental`. This is O\*NET's rule |

**`task_prevalence.csv`** records what papers actually show researchers doing, and is the measure the ratings are compared against. Papers from each subfield were read and scored for whether each task was performed. The run covered 34 fields and 31,526 papers. It covers subfield-level tasks in 316 subfields. Field, domain, and universal tasks have no per-paper measurement.

| Column | Description |
|--------|-------------|
| `field`, `subfield` | Subfield the papers were drawn from |
| `task` | Task statement text |
| `n_papers` | Number of papers scored for this task |
| `n_involved` | Number of papers where the task was stated explicitly or clearly implied |
| `prevalence` | `n_involved` divided by `n_papers` |

## Validation

The ratings are checked against two sources outside SciNet.

**Against human experts.** O\*NET publishes the same three scales rated by people who hold each occupation. On 425 researcher-relevant task-occupation pairs across 40 scientific occupations, the SciNet ratings correlate with those human ratings at r = 0.66 for importance, 0.63 for share of researchers, and 0.75 for frequency. Mean bias is under 1 point on every scale, so the ratings sit at roughly the right level and not only in the right order.

**Against what papers show.** Comparing the ratings to `task_prevalence.csv` across 4,936 task-subfield cells and 31,526 papers gives rank correlations of 0.56 for importance, 0.61 for share of researchers, and 0.53 for frequency. These hold within subfields, so they are not driven by some fields being busier than others. The two measures are not the same quantity, since a task that every researcher does occasionally still appears in few papers, so rank agreement is the meaningful test rather than agreement in levels.

The `Core` and `Supplemental` split behaves as intended. Tasks marked `Core` appear in 20.6% of papers on average, against 4.4% for those marked `Supplemental`.

Two further checks. Importance and `pct_researchers` correlate with each other at 0.83, so they are close to a single measure and the two conditions in the `Core` rule are not independent screens. The ratings correlate negatively with the time estimates, at -0.32 between frequency and elapsed hours, which says that tasks many researchers do often are the short routine ones. Nothing in the rating prompt mentions duration, so that relationship is not built in.

**The time estimates are checked against published protocols.** protocols.io publishes laboratory protocols whose individual steps carry durations entered by the authors. Each SciNet substep was matched to protocol steps by embedding similarity and then verified by a model. On the 769 exact matches covering 383 substeps in wet-lab fields, the elapsed-time estimate correlates with the observed duration at r = 0.53 in logs.

That figure is best read against how well protocols.io agrees with itself. Taking the protocol steps matched to one substep and splitting them into one step and the rest, a single real protocol step predicts the rest at r = 0.44, while the SciNet estimate predicts them at r = 0.55. The estimate therefore forecasts how long a step takes at least as well as another real protocol does. Correcting for how noisy the benchmark is implies a correlation with the true duration of about 0.70.

Coverage is the main limitation. Protocol durations are timers on waiting rather than on hands-on work, only 14% of steps carry one, and the corpus is concentrated in wet-lab fields. The comparison therefore validates `elapsed_hours` in experimental settings and says little about theoretical or computational work.

## Methodology

<p align="center"><img src="https://raw.githubusercontent.com/lukasalthoff/scinet/main/pipeline.svg" alt="SciNet pipeline diagram" width="680"/></p>

This README describes what is in the release and how to read it. [METHODOLOGY.md](METHODOLOGY.md) describes how it was built, covering the taxonomy, the task-generation prompts and coverage thresholds, the paper-validation pipeline, the protocols.io matching, and the O\*NET calibration behind the ratings.

For the research paper when available and for project updates, see the [Stanford project page](https://www.lukasalthoff.com).

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
