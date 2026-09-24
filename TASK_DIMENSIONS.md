# Task dimensions

Every SciNet task is scored on a set of dimensions that describe what kind of work it is, whatever its subject: how it relates to knowledge, what it works with, how it investigates, how complex, physical, and regulated it is, what motivates the research it serves, how practical it would be to train an AI system on it, and how much education it requires.

## Files

| File | Contents |
|------|----------|
| [`data/task_dimensions.csv`](data/task_dimensions.csv) | One row per task, in the same order as `tasks.csv` |
| [`data/substep_dimensions.csv.gz`](data/substep_dimensions.csv.gz) | One row per substep, in the same order as `substeps.csv.gz`, for the dimensions scored step by step |
| [`data/work_activity_dimensions.csv`](data/work_activity_dimensions.csv) | One row per work activity: the average over its tasks |

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

### Years of education

`years_education`: the minimum formal education a research group would require to hire someone for the task, with reasonable on-the-job training, regardless of who performs it today. 12 high school, 14 associate degree, 16 bachelor's, 18 master's, 20 doctorate. Adapted from the Anthropic Economic Index.

### Other columns

`cdr_rl_source` is `substep_mean` wherever the complexity and AI-training values are averages over substeps, and empty for the 2 tasks without a breakdown. In `work_activity_dimensions.csv`, `pasteur_applies_share` is the share of the activity's tasks that count as research and `n_tasks_scored` the number of its tasks with complexity scores.

## How the scores were produced

All scores come from Claude Sonnet 5, one prompt per group of dimensions, given the task and where it sits in the taxonomy.

The complexity and AI-training groups were scored on every substep (90,520 in all) and averaged to the task, weighting each substep by its share of the task's researcher time. Universal tasks are broken down separately in each field, so their values are averaged across fields. The other groups were scored once for the whole task.

The prompts for the complexity and AI-training groups use the level definitions of the published papers. The education prompt is adapted from the Anthropic Economic Index; the other prompts were written for SciNet.

Missing values. The 2 subfield tasks without a breakdown have no complexity or AI-training scores. The model declined to score a few substeps, mostly steps involving pathogens or dosing: 89 for complexity and 75 for AI training, plus 3 whose answers could not be read. Those cells are empty and the task's average uses its scored substeps. A handful of tasks lack whole-task scores for the same reason.

## Check against O\*NET

The same prompts were run on O\*NET's own task statements and compared with O\*NET's measures. This checks the prompts, not the averaging over substeps.

| SciNet score | O\*NET measure | Correlation | Compared across |
|---|---|---|---|
| Physical deployment | Time spent using hands | 0.73 | 709 occupations |
| Cognitive complexity | Job Zone | 0.75 | 709 occupations |
| Years of education | Required education | 0.81 | 709 occupations |
| Regulatory restriction | Importance of professional certification | 0.60 | 430 occupations |
| The three AI-training scores | The index authors' own scores | 0.79 to 0.88 | about 2,560 tasks |

## Work activities

Work-activity values are simple averages over the tasks assigned to each activity in `task_activity_assignments.csv`. A task statement that appears in several subfields is averaged over those first, so each assigned task counts once.
