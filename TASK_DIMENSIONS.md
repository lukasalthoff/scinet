# Task dimensions

Every SciNet task is scored on a set of dimensions that describe what kind of work it is, whatever its subject: how it relates to knowledge, what it works with, how it investigates, how complex, physical, and regulated it is, what motivates the research it serves, how practical it would be to train an AI system on it, and how much education it requires. A last column rates how likely one AI system, Claude Opus 5, is to complete the task.

## Files

| File | Contents |
|------|----------|
| [`data/task_dimensions.csv`](data/task_dimensions.csv) | One row per task, in the same order as `tasks.csv` |
| [`data/substep_dimensions.csv.gz`](data/substep_dimensions.csv.gz) | One row per substep, in the same order as `substeps.csv.gz`, for the dimensions scored step by step |
| [`data/work_activity_dimensions.csv`](data/work_activity_dimensions.csv) | One row per work activity: the average over its tasks |
| [`data/rl_index_subfields.csv`](data/rl_index_subfields.csv) | The RL feasibility index and its three scores per subfield, averaged over the hours a researcher spends on each task |
| [`data/rl_index_pca.json`](data/rl_index_pca.json) | The constants of the index, so it can be recomputed from `task_dimensions.csv` |

## The dimensions

### Relation to knowledge, medium, and mode of inquiry

For each of the three, the model splits 100 points across the options by the share of the task's effort each accounts for.

- **Relation to knowledge** (`relation_*`): *aggregate* (reading, reviewing the literature, learning methods), *evaluate* (peer review, refereeing, assessing), *produce* (hypotheses, data, experiments, analysis, derivations, artifacts), *communicate* (writing, presenting, visualizing), *support* (administration, funding, infrastructure, teaching, mentoring, service).
- **Medium** (`medium_*`): *information* (text, data, code, models, ideas), *materials* (physical materials, instruments, organisms, specimens, sites), *people* (participants, patients, students, colleagues).
- **Mode of inquiry** (`mode_*`): *theoretical* (models, proofs, derivations, frameworks), *quantitative* (numerical data, measurement, statistics, simulation), *qualitative* (texts, interviews, observation, cases), *design* (building devices, software, materials, systems, protocols), *none* (administration, teaching, most communication).

### Complexity, physical work, and regulation

From the CDR taxonomy of Parshall and Lopez-Luzuriaga (2026, [GWU CER WP 2026-005](https://www2.gwu.edu/~forcpgm/2026-005.pdf)). Each substep gets one level on each scale. A task's value is the average over its substeps, weighted by each substep's share of the task's time, so task values can fall between levels.

- **Cognitive complexity** (`cognitive_complexity`, 0–4): C0 self-evident; C1 procedural, a complete manual could be written; C2 contextual judgment, a manual gives guidelines and the worker decides; C3 expert synthesis, only a specialist can proceed; C4 discovery, the worker is writing the manual.
- **Physical deployment** (`physical_deployment`, 0–4): D0 purely digital; D1 sensing or moving about without handling things; D2 handling things in a structured, engineered workspace; D3 handling things in variable, unstructured settings; D4 fast, coordinated physical work under time pressure.
- **Regulatory restriction** (`regulatory_restriction`, 0–4), the barriers to an AI assisting the person: R0 none; R1 social or market norm; R2 professional standard or liability; R3 statute; R4 moral agency required.

### Pasteur's quadrant

After Stokes (1997). `pasteur_applies` says whether the task is part of doing research. Where it is, `pasteur_understanding` and `pasteur_use` (1–5) rate how far the research it serves seeks fundamental understanding and practical use. `pasteur_quadrant` is Bohr (understanding 4 or 5, use below 4), Edison (the reverse), Pasteur (both 4 or 5), neither (both below 4), or n.a. when the task is not research.

### Feasibility of training an AI by reinforcement learning

From the RL Feasibility Index of Moreira Tomei and Klein Teeselink (2026, [arXiv 2605.02598](https://arxiv.org/abs/2605.02598)). Reinforcement learning trains a system by trial and feedback, so it works best where success can be checked automatically and practice is cheap. Three of the index's eight dimensions are scored, each 1–10, plus its physical gate.

- `rl_physical_gate_pass`: whether the work can be done mainly by digital means (1 pass, 0 fail per substep; for a task, the share of its time in steps that pass). Unlike the original index, tasks that fail are still scored.
- `rl_verification`: 1 contested expert judgment with nothing inspectable, 10 a fully automatic check.
- `rl_simulability`: 1 needs live markets or real people with real stakes, 10 natively digital and cheap to replicate.
- `rl_feedback_density`: 1 rare, delayed, holistic signals, 10 continuous, immediate, per-step signals.

### RL feasibility index

`rl_index` combines the three RL scores into one number per task. Its columns sit in `task_dimensions.csv` right after the three scores, and `work_activity_dimensions.csv` averages them per work activity like every other score. It is the first principal component of `rl_verification`, `rl_simulability` and `rl_feedback_density`. The physical gate is not part of it: a task that fails the gate keeps its index, and `rl_physical_gate_pass` stays a separate measure. The original index of Moreira Tomei and Klein Teeselink instead sets a failing task to 0 and combines eight dimensions; this one uses only the three scored here.

How it is built:

1. Each of the three scores is standardized over the 7,262 rows of `task_dimensions.csv`: subtract its mean and divide by its standard deviation. Every row counts once, unweighted by hours.
2. A principal component analysis of the correlation matrix of the three standardized scores gives the weights of the first component. Its sign is set so that all three weights are positive.
3. The weighted sum is divided by its own standard deviation, so `rl_index` has mean 0 and standard deviation 1 over the tasks. A task at 1 is one standard deviation more feasible for RL training than the average task.

| | Verification | Simulability | Feedback density |
|---|---|---|---|
| Mean (1–10) | 5.985 | 7.026 | 5.737 |
| Standard deviation | 1.575 | 2.153 | 1.585 |
| Weight in the first component | 0.557 | 0.532 | 0.638 |
| Correlation with verification | 1 | 0.43 | 0.84 |
| Correlation with simulability | 0.43 | 1 | 0.77 |

The first component explains 79.2% of the variance of the three standardized scores (eigenvalues 2.376, 0.568 and 0.056), and its standard deviation before rescaling is 1.541. So

`rl_index = (0.557 z_verification + 0.532 z_simulability + 0.638 z_feedback_density) / 1.541`

where each `z` is a standardized score. `rl_index_pca.json` gives every constant at full precision, and the data files round the index to three decimals. `rl_index_equal` is the plain mean of the three standardized scores, without rescaling; it correlates 0.9999 with `rl_index` across tasks, so the weights hardly matter.

`rl_index_core` is the same index with the PCA fitted on core research tasks only: the 7,132 tasks whose every placement in `task_hours_per_year.csv` is a paper task (`task_type` is `paper`). The 123 general tasks and the 7 tasks that are paper tasks in some subfields and general in others are left out of the fit, but every task still gets a score from the core constants. `rl_index_core` has mean 0 and standard deviation 1 over the tasks in the fit. Because core tasks are 98% of all tasks, the constants barely change:

| Core fit | Verification | Simulability | Feedback density |
|---|---|---|---|
| Mean (1–10) | 5.981 | 7.062 | 5.746 |
| Standard deviation | 1.579 | 2.132 | 1.586 |
| Weight in the first component | 0.559 | 0.533 | 0.636 |

The first component explains 79.5% of the variance (eigenvalues 2.386, 0.557 and 0.056), and its standard deviation before rescaling is 1.545. `rl_index_core` correlates above 0.9999 with `rl_index` and differs from it by at most 0.017 for any task. The constants are under `core` in `rl_index_pca.json`.

Per subfield, `rl_index_subfields.csv` averages the task values over every task performed in the subfield, weighting each by `hours_per_year` from `task_hours_per_year.csv`. Universal, domain and field tasks count in each subfield where they are performed, and tasks with zero hours stay in with zero weight. The columns without a suffix use all of a researcher's hours, so they include teaching, administration and other general tasks; the `_paper` columns use only paper tasks (`task_type` is `paper`). Because general tasks take most of the hours and score low, every subfield's all-hours `rl_index` is below 0: the mean of 0 is over tasks, not over hours. The two versions correlate 0.76 across the 318 subfields. `rl_index_core` and `rl_index_core_paper` average the core index in the same two ways; the paper-task version differs from `rl_index_paper` by at most 0.009 in any subfield. The file also gives the hour-weighted mean of each of the three scores, on their 1–10 scale, and of `rl_physical_gate_pass`, the share of hours in steps that can be done digitally.

The index measures how practical it would be to train an AI system on a task by reinforcement learning, as the three scores judge it. It is not a measure of AI use or of productivity.

### Years of education

`years_education`: the minimum formal education a research group would require to hire someone for the task, with reasonable on-the-job training, regardless of who performs it today. 12 high school, 14 associate degree, 16 bachelor's, 18 master's, 20 doctorate. Adapted from the Anthropic Economic Index.

### Likelihood that an AI system completes the task

`elo_opus5`: how likely Claude Opus 5 is to complete the task, as an Elo rating against the other tasks; the higher the rating, the more likely. `elo_opus5_se`: its standard error. The ratings rank tasks and are not success rates. How they were made is described [below](#elo-ratings-for-claude-opus-5).

### Other columns

`cdr_rl_source` is `substep_mean`: the complexity and AI-training values of every task are averages over its substeps. In `work_activity_dimensions.csv`, `pasteur_applies_share` is the share of the activity's tasks that count as research and `n_tasks_scored` the number of its tasks with complexity scores.

## How the scores were produced

Except for the Elo rating, which is [described separately](#elo-ratings-for-claude-opus-5), the scores come from Claude Sonnet 5, one prompt per group of dimensions, given the task and where it sits in the taxonomy. Sonnet 5 declines some items about pathogens and dosing; those are scored with the same prompt by Claude Opus 5, or by Claude Haiku 4.5 where Opus 5 declines them too. This affects 105 of the 90,540 scored substeps (97 for the complexity group, 84 for the AI-training group) and 16 of the 7,262 tasks (8 for relation, medium, and mode; 9 for Pasteur's quadrant; 14 for education).

The complexity and AI-training groups were scored on 90,540 of the 90,583 substeps and averaged to the task, weighting each substep by its share of the task's researcher time. Universal tasks are broken down separately in each field, so their values are averaged across fields. The 43 steps of four universal task-field pairs (applying statistical methods in Mathematics and Philosophy, obtaining ethical approvals in Mathematics and in Physics & Astronomy) are not scored yet: their scores in `substep_dimensions.csv.gz` are empty, and the two tasks' values average the other 32 fields. The other groups were scored once for the whole task.

The prompts for the complexity and AI-training groups use the level definitions of the published papers. The education prompt is adapted from the Anthropic Economic Index; the other prompts were written for SciNet.

Missing values. Every task and every substep carries every score, except that `elo_opus5` and `elo_opus5_se` are empty for one task (see [Limits](#limits)). `pasteur_understanding` and `pasteur_use` are empty for the 313 tasks that are not research work (`pasteur_applies` is `no`), and `work_activity_dimensions.csv` leaves them empty for one activity, whose single task is of that kind.

## Check against O\*NET

The same prompts were run on O\*NET's own task statements and compared with O\*NET's measures. This checks the prompts, not the averaging over substeps.

| SciNet score | O\*NET measure | Correlation | Compared across |
|---|---|---|---|
| Physical deployment | Time spent using hands | 0.73 | 709 occupations |
| Cognitive complexity | Job Zone | 0.75 | 709 occupations |
| Years of education | Required education | 0.81 | 709 occupations |
| Regulatory restriction | Importance of professional certification | 0.60 | 430 occupations |
| The three AI-training scores | The index authors' own scores | 0.79 to 0.88 | about 2,560 tasks |

## Elo ratings for Claude Opus 5

How likely is an AI system to complete each SciNet task? `elo_opus5` ranks every task by that likelihood for one system, Claude Opus 5. A language model compared tasks two at a time, and a rating model turned its answers into one Elo rating per task: the higher the rating, the more likely Opus 5 is to succeed.

The ratings rank tasks. They are not success rates: no one ran Opus 5 on the tasks, and nothing here converts a rating into a probability of success.

### How the ratings were made

- **Units.** Tasks were rated where their steps are defined, the units of `substeps.csv.gz`: every subfield, field and domain task, and every universal task once in each of the 34 fields, 8,252 units in all. A universal task's `elo_opus5` is the mean of its 34 field ratings, and `elo_opus5_se` the standard error of that mean, which makes it much smaller (about 20 points) than for other tasks. The ratings are centred so that the 8,252 units average 1500.
- **Task cards.** Each unit is shown with its scope (subfield, field or domain), its statement, the hands-on hours a typical instance takes (from `task_time.csv`), and its steps (from `substeps.csv.gz`).
- **Judge.** Claude Haiku 5.5 sees two cards, each paired with Claude Opus 5, and says on which of the two tasks Opus 5 is more likely to succeed, with its confidence. Success means delivering the task's result to the standard a competent researcher in the field would accept, without a person fixing it. It covers the digital part of the task: a researcher supplies the data, samples or access the system asks for and carries out any physical work exactly as it specifies, and the system does the planning, analysis, coding, writing and judgment. It writes and runs code, reads and writes files, and searches the web. The judge considers a typical instance of each task.
- **Comparisons.** A first round pairs units at random; a second pairs units with close ratings, where the ranking is least certain. Ten percent of pairs are asked again with the two cards swapped. Thirty cards written in the same format for benchmark problems were rated in the same comparisons; they are not in the release. In all there are 95,040 comparisons, those of the benchmark cards included, and a median of 20 per unit.
- **Ratings.** A Bradley–Terry model with an advantage for the card shown first gives each card a rating. Ratings are on the Elo scale (400/ln 10, about 174 points per logit), so a gap of 400 points means the judge picks the higher-rated task ten times as often as the other. Standard errors come from 200 bootstrap resamples of the comparisons, keeping a swapped pair together.

### How consistent the ratings are

- Split in two random halves of the comparisons, the ratings correlate 0.87; for all comparisons together that implies a reliability of 0.93.
- On 8,646 pairs asked in both orders, the same task won both times in 72% of cases. The card shown first wins 59.5% of comparisons; the model accounts for this.
- Claude Opus 5.5, as a stronger judge, re-judged 2,000 pairs. On the 1,958 where both answered, it agreed with Haiku 5.5 on 70%: 76% of random pairs and 63% of close pairs. Where Haiku 5.5's confidence was 85 or more, the two agreed 82% of the time.
- Across the 8,252 units the ratings spread with a standard deviation of 459 points. The median standard error is 106 points, so neighbouring tasks are not reliably ordered, but tasks a few hundred points apart are.

### Limits

- The ratings are one model's judgment of another model's chances. They have not been checked against Opus 5 attempting the tasks.
- They describe Claude Opus 5 at one point in time. Another system may order tasks differently.
- The judge declined 52 comparisons, 51 of them involving one of three tasks that handle viruses, microbes or exposure agents. Preparing and formulating microbial preparations in Plant Pathology has no answered comparison and so no rating (the same task in Food Science & Technology is rated). Virus isolation in Virology & Medical Microbiology rests on 4 comparisons and preparing exposure agents in Physiology on 8, so both have large standard errors.
- A rating is relative: it says which tasks are harder for Opus 5 than others, not how likely Opus 5 is to complete any one of them.

## Work activities

Work-activity values are simple averages over the tasks assigned to each activity in `task_activity_assignments.csv`. A task statement that appears in several subfields is averaged over those first, so each assigned task counts once. `elo_opus5` is averaged the same way; its standard error is not carried over.
