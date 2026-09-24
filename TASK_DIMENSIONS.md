# Task dimensions

Every SciNet task is scored on five families of dimensions that describe what
kind of work it is, independently of its subject matter: how it relates to
knowledge, what it acts on, what mode of inquiry it uses, how cognitively
complex, physical and regulated it is, what motivates the research it serves,
how feasible it would be to train an AI system on it by reinforcement
learning, and how much education it requires.

## The files

| File | What it contains |
|---|---|
| [`data/task_dimensions.csv`](data/task_dimensions.csv) | One row per task (same rows and order as `tasks.csv`), all dimensions |
| [`data/work_activity_dimensions.csv`](data/work_activity_dimensions.csv) | One row per work activity: the simple mean over its tasks |

## The dimensions

**Relation to knowledge, primary medium, mode of inquiry.** For each of the
three axes the model splits 100 points across the options according to the
share of the task's effort each accounts for.

- Relation to knowledge: *aggregate* (reading, reviewing the literature,
  learning methods), *evaluate* (peer review, refereeing, assessing),
  *produce* (hypotheses, data, experiments, analysis, derivations, artifacts),
  *communicate* (writing, presenting, visualizing), *support*
  (administration, funding, infrastructure, teaching, mentoring, service).
- Primary medium: *information* (text, data, code, models, ideas),
  *materials* (physical materials, instruments, organisms, specimens, sites),
  *people* (participants, patients, students, colleagues, stakeholders).
- Mode of inquiry: *theoretical* (formal models, proofs, derivations,
  frameworks), *quantitative* (numerical data, measurement, statistics,
  simulation), *qualitative* (texts, interviews, observation, artifacts,
  cases), *design* (building devices, software, materials, systems,
  protocols), *none* (administration, teaching, most communication).

**CDR taxonomy** (Parshall and Lopez-Luzuriaga, 2026, GWU CER WP 2026-005,
https://www2.gwu.edu/~forcpgm/2026-005.pdf). One level per axis.

- Cognitive complexity: C0 self-evident (no manual needed); C1 procedural (a
  complete manual could be written); C2 contextual judgment (a manual gives
  guidelines, the worker exercises judgment); C3 expert synthesis (only a
  specialist can proceed); C4 discovery (the worker is writing the manual).
- Physical deployment: D0 purely digital; D1 sensing or locomotion without
  manipulation; D2 structured manipulation in an engineered workspace; D3
  unstructured manipulation in variable environments; D4 dynamic multi-modal
  coordination under time pressure.
- Regulatory restriction (barriers to AI assisting the person, not replacing
  them): R0 none; R1 social or market norm; R2 professional standard or
  liability; R3 statute; R4 moral agency required.

**Pasteur's Quadrant** (Stokes, 1997). Whether the task is part of doing
research (*applies*), and if so how far the research it serves is driven by a
quest for fundamental *understanding* (1–5) and by considerations of practical
*use* (1–5). The quadrant is Bohr (understanding ≥ 4, use < 4), Edison (use
≥ 4, understanding < 4), Pasteur (both ≥ 4), or neither.

**RL Feasibility Index** (Moreira Tomei and Klein Teeselink, 2026,
https://arxiv.org/abs/2605.02598), three of its eight dimensions, each 1–10,
plus its physical gate (pass if the task can be done primarily by digital
means; unlike the original index, failing tasks are still scored).

- Verification method: 1 contested expert judgment with no inspectable
  artifact, 10 fully deterministic programmatic check.
- Environment simulability: 1 requires live markets or real humans with
  genuine stakes, 10 natively digital and trivially cheap to replicate.
- Feedback density: 1 rare, delayed, holistic signals, 10 continuous,
  immediate, per-step signals.

**Years of education** (0–20). The minimum formal education a research group
would require if hiring someone specifically to perform the task, with
reasonable on-the-job training, ignoring who typically performs it today
(high school 12, bachelor's 16, master's 18, doctorate 20). Adapted from the
Anthropic Economic Index education item.

## How the scores were produced

Each task was scored by Claude Sonnet 5 with one prompt per family, given the
task text and its field and subfield. The CDR and RL families were scored on
every substep in `data/substeps.csv.gz` (90,490 substeps at all four
levels; the per-substep scores are in `data/substep_dimensions.csv.gz`) and
averaged to the task with the substeps' shares of researcher time as weights,
the physical gate as the time-weighted share of substeps that pass. Universal
tasks are decomposed once per field and averaged across fields. The 2
tasks that have no decomposition in `substeps.csv.gz` have no CDR or RL
values (`cdr_rl_source` is empty); substeps the model declined to score
(92 of 90,490 for CDR, 75 for RL, in pathogen-handling and dosing tasks)
are left empty and the task mean is taken over the scored substeps. The
other families were scored once per task. The prompts for the CDR and RL families
use the published rubrics verbatim; the prompts for the other families are
ours. Until v1.4.2 the CDR and RL values were substep means for the 4,936
subfield tasks that had a decomposition at the time and direct task ratings
otherwise; v1.5.0 rescored every substep of the current decomposition.

The same prompts were run on O\*NET tasks to check them against O\*NET's own
occupation measures: physical deployment correlates 0.73 with O\*NET's "time
spent using your hands", cognitive complexity 0.75 with O\*NET Job Zone,
years of education 0.81 with O\*NET's required education, regulatory
restriction 0.60 with the importance of professional certification, and the
three RL dimensions 0.79–0.88, task by task, with the scores published by the
index's authors for the same O\*NET tasks.

Work-activity values are simple means over the tasks assigned to each
activity in `task_activity_assignments.csv`.
