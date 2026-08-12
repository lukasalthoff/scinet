# SciNet

SciNet is a database documenting which tasks researchers perform across all scientific disciplines. It is modeled after O\*NET, the US Department of Labor's database of the tasks performed in every occupation in the US economy. It is generated primarily through large language models, and validated against published papers, laboratory protocols, and data on scientific occupations in O\*NET.

SciNet organizes all scientific disciplines hierarchically, with subfields (e.g. Labor Economics, Macroeconomics) grouped into fields (e.g. Economics) grouped into domains (e.g. Social Sciences). Currently, the database contains 6 domains, 34 fields, and 318 subfields. Tasks can correspond to any level of this hierarchy. For example, _"collecting biological specimens"_ is a domain-level task for the Life Sciences, while _"conducting field excavations to recover human skeletal remains"_ corresponds to the subfield of Biological & Physical Anthropology. This release contains 7,262 task statements: 30 that apply to research everywhere, 134 at the domain level, 321 at the field level, and 6,777 at the subfield level.

For each task, the data contain a list of all substeps required to perform that task, as well as an estimate of:
1. How long the task takes to perform
2. How important the task is
3. How frequently researchers perform a task
4. What share of researchers perform that task

**Website:** [anatomyofscience.com](https://www.anatomyofscience.com/) · **Repository:** [github.com/lukasalthoff/scinet](https://github.com/lukasalthoff/scinet)

## Data files

All files are UTF-8 and CSVs use comma separators. See [`data/README.md`](data/README.md) for a standalone description.

| File | Description |
|------|-------------|
| [`data/tasks.csv`](data/tasks.csv) | Every task in the hierarchy, at the universal, domain, field, and subfield levels, with category labels |
| [`data/substeps.csv.gz`](data/substeps.csv.gz) | How each task breaks down into the steps a researcher performs |
| [`data/task_time.csv`](data/task_time.csv) | How long each task takes, estimated separately for every subfield it appears in |
| [`data/task_ratings.csv`](data/task_ratings.csv) | How important each task is, what share of researchers do it, and how often, rated separately for every subfield it appears in |
| [`data/task_prevalence.csv`](data/task_prevalence.csv) | The share of a subfield's papers that perform each task, read from the papers themselves |
| [`data/task_clusters.csv`](data/task_clusters.csv) | The two-level aggregation of the database: 139 task clusters grouped under the 30 universal tasks, with names and descriptions. See [TASK_CLUSTERS.md](TASK_CLUSTERS.md) |
| [`data/task_cluster_assignments.csv`](data/task_cluster_assignments.csv) | Which cluster every domain-, field-, and subfield-level task belongs to |
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

**`task_time.csv`** has one row per task per subfield it appears in, because the same task can correspond to a different job in different subfields. Across the 140 tasks that reach five or more subfields, the median task varies by a factor of 2.5 in `researcher_hours` across all its corresponding subfields, and by a factor of 4.1 in `elapsed_hours`.

| Column | Description |
|--------|-------------|
| `task` | Task statement text |
| `level` | Level the task is filed at |
| `domain`, `field`, `subfield` | Where this estimate applies |
| `n_substeps` | Number of substeps in the breakdown |
| `researcher_hours` | Attended human effort for one instance of the task, summed over substeps as repetitions times minutes |
| `elapsed_hours` | Calendar time for one instance, including unattended waiting such as incubations, cluster jobs, and review boards. Never less than `researcher_hours` |
| `confidence` | Most common per-substep confidence: `high`, `medium`, or `low` |

**`task_ratings.csv`** has one row per task per subfield it appears in. The three scales are taken from O\*NET, where they are called Importance, Relevance of Task, and Frequency of Task.

| Column | Description |
|--------|-------------|
| `task` | Task statement text |
| `level` | Level the task is filed at |
| `domain`, `field`, `subfield` | Subfield this rating was made for |
| `importance` | 1 = Not Important, 2 = Somewhat Important, 3 = Important, 4 = Very Important, 5 = Extremely Important |
| `pct_researchers` | Out of 100 researchers in the subfield, how many perform this task at least occasionally. Range 0 to 100 |
| `frequency` | 1 = Yearly or less, 2 = More than yearly, 3 = More than monthly, 4 = More than weekly, 5 = Daily, 6 = More than daily, 7 = Hourly or more |
| `classification` | `Core` if `importance` is at least 3 and `pct_researchers` is at least 67, otherwise `Supplemental`. This is O\*NET's rule |

**`task_prevalence.csv`** records how often each task actually appears in the literature. We selected a sample of papers from each subfield and asked an LLM to verify whether each task was likely performed by the researchers when conducting their research.

| Column | Description |
|--------|-------------|
| `field`, `subfield` | Subfield the papers were drawn from |
| `task` | Task statement text |
| `n_papers` | Number of papers scored for this task |
| `n_involved` | Number of papers where the task was stated explicitly or clearly implied |
| `prevalence` | `n_involved` divided by `n_papers` |

## Methodology

[METHODOLOGY.md](METHODOLOGY.md) describes how SciNet was built and validated.

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
