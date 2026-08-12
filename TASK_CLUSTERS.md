# Task clusters

This page describes SciNet's two-level aggregation of the task database: 30
**universal tasks** at the top, and 139 **task clusters** underneath them.
Every domain-, field-, and subfield-level task in the database belongs to
exactly one cluster, and every cluster belongs to exactly one universal task.

## Why this exists

SciNet contains 7,262 tasks. That level of detail is right for describing what
researchers in a specific subfield do, but it is too fine for many uses: if
you classify some outside dataset against the tasks (say, matching each
conversation with an AI assistant to the research task it involves), most
tasks will match few or no observations. The database's own levels cannot
serve as the aggregation, because they are deliberately not nested: a
subfield task is not a subdivision of some field task, so keeping only the
higher-level tasks would drop activities instead of grouping them.

The task clusters solve this. They are an overlay on top of the database: no
task was changed or removed, every task simply also got a home in a cluster,
and every cluster a home under a universal task. You can work at whichever of
the three grains fits your data: 30 universal tasks, 139 clusters, or the
full 7,262 tasks.

## The files

| File | What it contains |
|---|---|
| [`data/task_clusters.csv`](data/task_clusters.csv) | One row per cluster: its id, name, a one-paragraph description, the universal task and category it sits under, and how many tasks it contains |
| [`data/task_cluster_assignments.csv`](data/task_cluster_assignments.csv) | One row per task: the task text, its level, and the cluster it belongs to |

Cluster ids look like `U01.04`: the part before the dot names the universal
task (U01 through U30, in [`tasks.csv`](data/tasks.csv) these are the
`universal`-level rows), the part after the dot numbers the cluster.
`.99` clusters collect the handful of tasks (28 in total) that fit their
universal task but none of its clusters. A few universal tasks, such as
writing grant proposals, have no specialized tasks below them at all; they
appear in the taxonomy but have no clusters.

## How the clusters were built

**1. Every task was mapped to its closest universal task.** We ran blind
classifiers (Claude Sonnet): each saw only the list of universal tasks and a
batch of one hundred task statements, nothing else, and picked for each task
the universal task a researcher would say they are performing when doing it.
The one instruction that matters: judge by the activity itself — its steps,
inputs, tools, and skills — never by the discipline. "Acquire medical imaging
data" and "collect sediment cores from the seafloor" are different sciences
but the same kind of activity: acquiring primary data.

**2. The tasks that fit nowhere told us the universal list was incomplete.**
About 500 tasks (7%) could not honestly be filed under any of the original 27
universal tasks. They were not noise: they clustered into three activities
that entire disciplines are built on, and that the original list simply did
not cover. So three universal tasks were added, bringing the list to 30:

* *Interpret texts, documents, artifacts, and other qualitative sources to
  construct evidence-based arguments* — the core method of the humanities,
  law, and qualitative social science.
* *Construct formal models, proofs, and derivations to establish theoretical
  results* — the core method of mathematics and theory.
* *Design, build, and iteratively refine artifacts such as devices, software,
  materials, systems, or creative works to meet specified requirements* — the
  core method of engineering and design, filed under a new ninth activity
  category, Design & Development.

Re-running the unmatched tasks against the expanded list left only 23 tasks
(0.3%) without a good home.

**3. Claude Fable grouped each universal task's tasks into clusters.** The
model read every task filed under a universal task — for the largest, more
than 1,500 statements — and grouped them by one criterion: two tasks belong
in the same cluster when doing them involves substantially the same steps,
tools, and skills, so that a technology able to automate one could automate
the other. Differences in subject matter alone do not separate tasks. Each
cluster got a name, a plain description, and boundary rules for the
ambiguous cases.

**4. Every task was then filed into a cluster.** A second round of
classifiers assigned each task to one of its universal task's clusters. They
could also flag a task as sitting in the wrong universal task altogether or
as fitting no cluster; those flags were reviewed, a few hundred tasks were
re-filed (mostly interpretive work that had been sitting in statistical
buckets), one missing cluster was added, and the rest of the flags were
resolved by hand.

## Things to know before using it

* The clusters were drafted and assigned by language models. The pipeline
  had review steps and consistency checks, but no task-by-task expert review
  has happened yet.
* A few near-twin clusters exist under different universal tasks (for
  example, sample preparation appears under both data acquisition and data
  cleaning) because the underlying task statements were written from
  different stages of the research pipeline. If you need strictly
  non-overlapping groups, merge the twins listed in the documentation of the
  build pipeline.
* [`task_ratings.csv`](data/task_ratings.csv) does not yet contain ratings
  for the three universal tasks added in August 2026.
