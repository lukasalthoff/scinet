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

## The prompts

The three classifier prompts, verbatim. Placeholders in curly braces varied
per run: `{chunk file path}` and `{output file path}` pointed each classifier
at its own batch of 100 tasks, `{N}` was the batch size, and `{chunk id}` a
batch label.

<details>
<summary><b>Prompt 1 — mapping every task to its closest universal task</b></summary>

```
You are classifying task statements from a taxonomy of scientific research
tasks into 27 broad "universal" research tasks that apply to every
researcher. Work ONLY from the information in this prompt and the single
input file named below.

THE 27 UNIVERSAL TASKS (grouped by functional category):
== Data Gathering ==
U01: Acquire or access primary data sources relevant to research questions.
U06: Curate and manage datasets, ensuring proper documentation and version control.
U07: Design data collection protocols and instruments to ensure validity and reproducibility.
U19: Obtain ethical approvals and informed consent for studies involving human subjects.
== Data Analysis ==
U02: Apply statistical methods to test hypotheses and estimate effect sizes.
U04: Clean and preprocess raw data to prepare for statistical or computational analysis.
U09: Develop and validate computational models to simulate or predict phenomena.
U27: Visualize data and results using graphs, tables, and figures for interpretation.
== Ideation & Hypothesis Generation ==
U03: Brainstorm potential research directions through discussions with colleagues and peers.
U12: Generate hypotheses based on theoretical frameworks, observations, or preliminary data.
U13: Identify gaps in existing literature to formulate novel research questions.
U18: Observe real-world phenomena to identify patterns worthy of scientific investigation.
== Administration ==
U05: Coordinate with collaborators across institutions and disciplines.
U16: Maintain laboratory equipment, software systems, or research infrastructure.
U17: Manage research budgets, personnel, and project timelines.
== Mentorship & Teaching ==
U08: Develop and deliver course curricula in specialized research areas.
U22: Provide feedback on student theses, dissertations, and research proposals.
U26: Supervise graduate students and postdoctoral researchers on research projects.
== Writing & Communication ==
U10: Draft manuscripts describing research questions, methods, results, and interpretations.
U20: Prepare grant proposals to secure funding for research projects.
U21: Present research findings at conferences, seminars, and symposia.
U23: Respond to peer reviewer comments and revise manuscripts for publication.
== Peer Review & Service ==
U11: Evaluate manuscripts submitted to journals for scientific rigor and contribution.
U25: Serve on editorial boards, grant review panels, or professional committees.
== Reading & Knowledge Acquisition ==
U14: Keep up with new findings, methods, and debates relevant to the research area.
U15: Learn the concepts, methods, and tools needed to carry out the research.
U24: Review and synthesize the relevant literature to situate a research question within existing knowledge.

INPUT: read the CSV file at:
{chunk file path}
It has a header row (uid,task) and exactly {N} task statements.

FOR EACH of the {N} tasks, decide which ONE universal task it is the
closest specialization of: the universal task a researcher would say they
are performing when doing this specific task. Judge by the activity
performed (its steps, inputs, tools, and skills), not by discipline or
subject matter.
- "u": the closest universal task id ("U01".."U27"). Always give exactly
  one, even for poor fits.
- "fits": true if the task genuinely is a specialization of that universal
  task; false if the task does not really belong under ANY of the 27 and
  the closest one is a stretch.
- "note": ONLY when fits is false, one short clause saying what activity
  the task actually is. Omit the key otherwise.

OUTPUT: write a JSON file to:
{output file path}
with exactly this shape:
{"chunk": "{chunk id}", "results": [{"uid": "T0123", "u": "U04", "fits": true}, {"uid": "T0124", "u": "U16", "fits": false, "note": "..."}, ...]}
Every uid from the input file must appear exactly once, in input order.
Verify the results count equals {N} before writing the file.

Then report via structured output: chunk (the id "{chunk id}"), n_assigned
(must equal {N}), n_misfit (how many have fits=false), output_path.
```

After the three new universal tasks were added, the ~500 flagged tasks were
re-run through the identical prompt with the list extended to 30 (ids
"U01".."U30", the new Design & Development category block) and one added
sentence:

```
Note that U28 covers interpretive and qualitative analysis of sources
(including doctrinal legal reasoning, close reading, discourse and content
analysis); U29 covers formal theoretical work (proofs, theorems, formal
models, analytical derivations); U30 covers designing and building
artifacts (devices, software, systems, materials-as-products, creative
works) and evaluating designs against requirements.
```

</details>

<details>
<summary><b>Prompt 2 — filing each task into a cluster</b></summary>

Here `{BUCKET}` is the universal task id (e.g. `U01`) and `{cluster
definitions file}` is the file of cluster names, descriptions, and boundary
rules that Claude Fable drafted for that universal task.

```
You are filing task statements from a taxonomy of scientific research
tasks into SUB-FAMILIES of the broad universal research task {BUCKET}.
Work ONLY from the two files named below.

STEP 1: read the sub-family definition file at:
{cluster definitions file}
Use ONLY the section for bucket {BUCKET} (headings "## {BUCKET}.NN — ...").
Study each sub-family's statement, scope, exclusions, and the bucket's
boundary rules and reassignment notes if present.

STEP 2: read the CSV file at:
{chunk file path}
It has a header row (uid,task) and exactly {N} task statements, all
currently assigned to bucket {BUCKET}.

FOR EACH of the {N} tasks, decide by the activity performed (steps,
inputs, tools, skills -- not discipline or subject matter):
- Normal case: assign "sf" to the ONE best sub-family code
  ("{BUCKET}.01" etc.).
- Escape 1 -- wrong bucket: if the task's activity actually belongs under
  a DIFFERENT universal task entirely (the cards file's reassignment
  notes flag common cases, especially interpretive/qualitative work
  belonging in U28, formal theory in U29, design/building in U30,
  coding-scheme application in U04.06), set "sf" to "MOVE" and "to" to
  the target: a bucket id ("U28") or a specific sub-family ("U04.06")
  when the notes name one. Add a short "note".
- Escape 2 -- no fit: if the task belongs in bucket {BUCKET} but none of
  its sub-families fits, set "sf" to "NONE" with a short "note"
  describing the activity.
Use MOVE and NONE sparingly and only with genuine reason.

OUTPUT: write a JSON file to:
{output file path}
with exactly this shape:
{"chunk": "{chunk id}", "results": [{"uid": "T0123", "sf": "{BUCKET}.04"}, {"uid": "T0124", "sf": "MOVE", "to": "U28", "note": "..."}, {"uid": "T0125", "sf": "NONE", "note": "..."}, ...]}
Every uid from the input file must appear exactly once, in input order.
Verify the count equals {N} before writing.

Then report via structured output: chunk ("{chunk id}"), n_assigned (must
equal {N}), n_move, n_none, output_path.
```

Note: "sub-family" was the working name for what this release calls a task
cluster.

</details>

<details>
<summary><b>Prompt 3 — re-filing tasks that were moved between universal tasks</b></summary>

```
You are filing task statements from a taxonomy of scientific research
tasks into SUB-FAMILIES of the universal research task {BUCKET}. These
tasks were just re-routed into bucket {BUCKET} from other buckets. Work
ONLY from the two files named below.

STEP 1: read the sub-family definition file at:
{cluster definitions file}
Use ONLY the section for bucket {BUCKET} (headings "## {BUCKET}.NN — ...").
Study each sub-family's statement, scope, and exclusions.

STEP 2: read the CSV file at:
{chunk file path}
It has a header row (uid,task) and exactly {N} task statements.

FOR EACH task, assign "sf" to the ONE best sub-family code
("{BUCKET}.01" etc.), judging by the activity performed (steps, inputs,
tools, skills), not discipline. If none fits, set "sf" to "NONE" with a
short "note".

OUTPUT: write a JSON file to:
{output file path}
with exactly this shape:
{"chunk": "{chunk id}", "results": [{"uid": "T0123", "sf": "{BUCKET}.03"}, ...]}
Every uid must appear exactly once, in input order. Verify the count
equals {N} before writing.

Then report via structured output: chunk ("{chunk id}"), n_assigned (must
equal {N}), n_none, output_path.
```

</details>
