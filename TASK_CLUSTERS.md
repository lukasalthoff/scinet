# Task clusters

This page describes SciNet's two-level aggregation of the task database: 30
**universal tasks** at the top, and 139 **task clusters** underneath them.
Every domain-, field-, and subfield-level task in the main database is mapped to
exactly one cluster, and every cluster belongs to exactly one universal task.

## Purpose of this aggregated taxonomy

SciNet contains 7,262 tasks. That level of detail is right for describing what
researchers in a specific subfield do, but it is too fine for many uses.


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

**1. Every task was mapped to its closest universal task.** We used Sonnet 5 to map every task at the domain, field, and subfield level to the universal task it is closest to

**2. We created 3 new universal tasks**
About 500 tasks (7%) could not be filed under any of the original 27
universal tasks. So three universal tasks were added, bringing the list to 30:

* *Interpret texts, documents, artifacts, and other qualitative sources to
  construct evidence-based arguments* — the core method of the humanities,
  law, and qualitative social science.
* *Construct formal models, proofs, and derivations to establish theoretical
  results* — the core method of mathematics and theory.
* *Design, build, and iteratively refine artifacts such as devices, software,
  materials, systems, or creative works to meet specified requirements* — the
  core method of engineering and design, filed under a new ninth activity
  category, Design & Development.

**3. Claude Fable grouped each universal task's tasks into clusters.** The
model read every task filed under a universal task and grouped them by one criterion: two tasks belong
in the same cluster when doing them involves substantially the same steps,
tools, and skills, so that a technology able to automate one could automate
the other. Differences in subject matter alone do not separate tasks. Each
cluster got a name, a plain description, and boundary rules for the
ambiguous cases.

**4. Every task was then filed into a cluster.** A second round of Sonnet 5
classifiers assigned each task to one of its universal task's clusters.
