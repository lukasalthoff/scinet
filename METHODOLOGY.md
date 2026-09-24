# SciNet Methodology

This page outlines how SciNet was created and validated.

## Steps

1. **[Generating the taxonomy](#1-generating-the-taxonomy).** Prompting a language model to divide science into domains, fields, and subfields, then correcting the result based on expert feedback.
2. **[Initial task generation](#2-initial-task-generation).** Writing task statements in O\*NET's format, working down the hierarchy from tasks that apply to all researchers to tasks specific to one subfield.
3. **[Expanding the tasks with papers](#3-expanding-the-tasks-with-papers).** Reading published papers to find research activities the initial list had missed, and measuring how often each task appears in the literature.
4. **[Rating each task](#4-rating-each-task).** Estimating the importance, relevance, and frequency of every task in every subfield it appears in.
5. **[Substeps and time estimates](#5-substeps-and-time-estimates).** Breaking each task into the steps a researcher performs and estimating how long each one takes.
6. **[Validation](#6-validation).** Checking the ratings against O\*NET, the time estimates against laboratory protocols, and the task list against the papers themselves.

Beyond the task database itself, [TASK_DIMENSIONS.md](TASK_DIMENSIONS.md) documents the dimensions every task is scored on and [WORK_ACTIVITIES.md](WORK_ACTIVITIES.md) the two-level aggregation.

**Models.** Subfield task generation used Claude Opus 4.5. The paper expansion used Claude Sonnet 5 to draw, judge, elicit and score, and Claude Opus 5 to consolidate and raise. The ratings used Claude Opus 5. Substep decomposition and timing used Claude Opus 4.8. The task dimensions used Claude Sonnet 5.

---

## 1. Generating the taxonomy

SciNet organizes all scientific disciplines into three levels: 6 domains, 34 fields, and 318 subfields.

| Level | Count | Example |
|-------|-------|---------|
| Domain | 6 | Physical Sciences |
| Field | 34 | Physics & Astronomy |
| Subfield | 318 | Condensed Matter Physics |

The six domains are Formal Sciences, Physical Sciences, Life Sciences, Health Sciences, Social Sciences, and Arts & Humanities.

We generated the taxonomy by prompting Claude. For each field, the model was asked how a researcher working in that field would divide it into its major subfields, and to return divisions that researchers in the field would themselves recognize, that are roughly comparable in scope, and that cover the field without overlapping one another. Fields were then grouped into the six domains.

The prompt aims to build a map of how research communities are actually organized, so that a researcher in a given field would recognize the boundaries.

We then made manual corrections to the taxonomy, many of them in response to researchers who reviewed the parts of it covering their own areas. Those researchers are listed on the [contributors page](https://www.anatomyofscience.com/#/contributors).

---

## 2. Initial task generation

### 2.1 How a task statement is written

All SciNet tasks follow the [O\*NET](https://www.onetonline.org/) canonical task statement structure:

```
[Action Verb] + [Object] + [Modifiers] + [Purpose]
```

The writing rules are drawn from the instructions O\*NET gives its human analysts. A statement begins with a present-tense action verb such as *Analyze*, *Design*, or *Estimate*, names the object being acted on, adds optional modifiers, and ends with an optional purpose introduced by "to". Each carries one core action rather than a chain of steps, runs to roughly 8 to 18 words, and uses plain language.

Three reference statements from O\*NET:

> "Analyze data from research conducted to detect and measure physical phenomena."

> "Develop, implement, and evaluate methods of data collection, such as questionnaires or interviews."

> "Formulate recommendations, policies, or plans to solve economic problems or to interpret markets."

Tasks describe the work of a research team rather than of a single individual, and what a typical researcher in the area does rather than what they might occasionally do.

### 2.2 Working down the hierarchy

Task generation starts with the universal tasks that apply to every researcher, then works down. At each step the model is shown the tasks one level up and writes tasks for the narrower area. Every new task names the parent task it refines, and must add something the levels above do not already carry.

| Level | Scope | How it was written | Coverage threshold |
|-------|-------|--------------------|--------------------|
| Universal | All researchers | Model-drafted, researcher-reviewed | |
| Domain | e.g. Social Sciences | 69 model-drafted and researcher-reviewed, 65 raised from papers in [Section 3](#3-expanding-the-tasks-with-papers) | |
| Field | e.g. Economics | Raised from papers in [Section 3](#3-expanding-the-tasks-with-papers) | |
| Subfield | e.g. Labor Economics | Model-generated, then expanded from papers | 70% of subfield researchers |

The universal and domain levels anchor the whole hierarchy, so they were developed iteratively with a researcher in the loop.

The 30 universal tasks are organized into ten categories, which every task in the database inherits: Reading & Knowledge Acquisition, Ideation & Hypothesis Generation, Data Gathering, Data Analysis, Theoretical Analysis, Design & Development, Writing & Communication, Peer Review & Service, Mentorship & Teaching, and Administration. Three universal tasks and the Design & Development category were added in August 2026, after an audit showed the original list under-covered interpretive analysis of qualitative sources, formal theoretical work, and designing and building artifacts. Theoretical Analysis was split out of Data Analysis in September 2026 so that formal theory is not filed as data work.

The released taxonomy has four levels, carrying 30 universal, 134 domain, 321 field, and 6,777 subfield tasks. Field-level tasks are not written here. They arrive from below, in [Section 3](#3-expanding-the-tasks-with-papers), when the same activity recurs across many of a field's subfields and is filed once at the field level instead.

<details>
<summary>Subfield task generation prompt</summary>

```
You are generating task statements for researchers in {subfield_name}
(a subfield of {domain_name}).

INPUT: DOMAIN TASKS ({domain_name})
These are the domain-level tasks. Your job is to generate subfield-specific
refinements of these.

  {numbered domain-level tasks, each showing the universal task it refines}

CONTEXT: TOPICS IN {SUBFIELD_NAME}
  {up to 12 topics in the subfield}

OBJECTIVE
Generate subfield-specific refinements of the domain tasks above. Each
subfield task you generate should:
- Refine ONE specific domain task (specify which domain task number it refines)
- Be specific to {subfield_name} (would NOT apply to other subfields like
  Psychology or Political Science)
- Be common enough that 70%+ of {subfield_name} researchers do it regularly

REQUIREMENTS

1. CRITICAL 70% THRESHOLD: Only include tasks that the MAJORITY (70%+) of
   {subfield_name} researchers do regularly.
2. USE O*NET WRITING STYLE: Action verb + object + modifiers + purpose.
3. SUBSTANTIAL TASKS ONLY: Skip trivial steps.
4. CONSOLIDATE AGGRESSIVELY.
5. SKIP GENERIC TASKS: Teaching, mentoring, and admin tasks are covered at
   the universal and domain levels.
6. WATCH FOR OVERLAP.
7. AVOID HYPERSPECIFIC TASKS
8. AVOID EXAMPLES THAT ARE TOO SPECIFIC, such as hyperspecific methodologies
   or datasets.
9. Avoid excessive use of the format "Apply X to Y", or "do X in order to Y".

OUTPUT FORMAT
Return valid JSON. For each task, specify which domain task number it refines:

{
  "tasks": [
    {"l2_task_id": 1, "task": "Design field-specific measurement instruments
      to capture key outcomes and exposures."},
    ...
  ]
}
```

</details>

---

## 3. Expanding the tasks with papers
To check the existing tasks and find missing ones, we sampled about 100 papers per subfield. A language model judged which existing tasks each paper performed and, for 50 of the papers, what work the paper did that no task covered. Proposed tasks were kept only if enough papers showed them. Existing tasks were not removed on this basis. The steps:


**1. Draw.** We draw English-language journal articles from 2000 to 2020 that have a DOI, open-access full text, and at least one citation, weighting by citations and aiming for 100 usable papers per subfield. The topic mapping released as [`data/openalex_topic_subfield_mapping.csv`](data/openalex_topic_subfield_mapping.csv), widened by [`data/topic_frame_overlay.csv`](data/topic_frame_overlay.csv), decides which papers are eligible for a subfield. A model then reads each paper, confirms its subfield, and drops papers that are not research or belong elsewhere. 

**2. Judge.** For each paper and each task in its subfield, a model returns one of three verdicts: *stated explicitly*, with a verbatim quote, *clearly implied*, meaning the work required the task though the paper does not narrate it, or *not involved*. The average over the sample is that task's **prevalence**, released as [`data/task_prevalence.csv`](data/task_prevalence.csv).

**3. Elicit.** For 50 papers per subfield, a model lists the research work the paper performed, quoting the paper for each item. It is shown the existing tasks of the subfield, of its sibling subfields, and of the levels above, and marks each item as covered or not. Only uncovered items can become new tasks, so this step searches for gaps in the existing list rather than describing papers from scratch. 

**4. Referee.** Each proposal is refereed against the tasks that already exist, in the subfield, in sibling subfields, and at the field and domain levels. 

**5. Consolidate.** Surviving proposals are grouped into candidate tasks. A candidate is kept only if at least two papers, and at least 3% of the papers read, proposed it independently. 

**6. Score.** Each candidate is then measured the same way as the existing tasks and kept only if at least 5% of the subfield's papers perform it. The measurement reuses the subfield's sampled papers, including those the candidate came from, so the share is measured on the same sample that suggested it. A one-off comparison against a fresh sample gave shares 4.2 percentage points apart on average, correlated at 0.97. Papers are scored in batches of 25, 60, and 100, stopping early once it is clear whether the share will clear 5%; most candidates went to 100.

**7. Raise.** A task proposed across many subfields of a field, or many fields of a domain, is filed once at that higher level instead of repeatedly below it.

The expansion added 2,297 tasks: 1,905 at the subfield level, 327 at the field level, and 65 at the domain level. Later clean-up left 321 field-level tasks in the release.

---

## 4. Rating each task

Following [O\*NET](https://www.onetonline.org/), each task is rated on three scales, separately for every subfield it appears in:

- **Importance (1 to 5).** How important is this task to researchers in this area?
- **Relevance (0 to 100).** Out of 100 researchers in this area, how many perform this task at least occasionally?
- **Frequency (1 to 7).** How often is this task performed, from yearly or less to hourly or more?

O\*NET collects these by surveying workers in each occupation. We instead prompt a language model, Claude Opus 5, to answer as a researcher with ten or more years of experience in the subfield. Tasks are rated in groups, one call per subfield and level, so the ratings within a group share a scale. The release holds 26,803 ratings. The three universal tasks added in August 2026 were rated in a later run of the same prompt, with all 30 universal tasks in the group.

Tasks are then classified as **Core** when relevance is at least 67 and importance is at least 3, and **Supplemental** otherwise, which is O\*NET's own rule.

<details>
<summary>Task rating prompt</summary>

```
You are completing an occupational survey as a {occupation} with 10+ years of experience.

Rate each task below on THREE scales:

1. IMPORTANCE (IM): How important is this task to your occupation?
   Scale: 1=Not Important, 2=Somewhat Important, 3=Important, 4=Very Important, 5=Extremely Important
   Note: Most tasks should be rated 3-4; only a small minority receive 5.

2. PERCENT OF WORKERS (RT): Out of 100 workers in this occupation, how many perform this task at least occasionally?
   Scale: 0-100
   CRITICAL: 100 should be your most common answer - use it for ~30% of tasks. For this occupation, most of these tasks are done by all workers. Expected distribution: ~30% = 100, ~55% = 90-99, ~15% = below 90.

3. FREQUENCY (FT): How often is this task performed?
   Scale: 1=Yearly or less, 2=More than yearly, 3=More than monthly, 4=More than weekly, 5=Daily, 6=More than daily, 7=Hourly or more
   IMPORTANT: Expected distribution across all tasks: ~20% at 1-2 (yearly/monthly), ~45% at 3 (monthly-weekly), ~25% at 4 (weekly-daily), ~10% at 5-7 (daily+). Avoid overrating frequency.

TASKS:
{numbered task list}

Return your ratings as a JSON array with one object per task:
[
  {"task_num": 1, "im": <1-5>, "rt": <0-100>, "ft": <1-7>},
  ...
]

Return ONLY the JSON array, no other text.
```

`{occupation}` is filled with "researcher in <subfield>". This is the calibrated
prompt that produced the released ratings. An earlier uncalibrated version,
which instead told the model to be conservative about how many researchers
perform a task, was used for a January 2026 run that is not released.

</details>

The prompt tells the model roughly how answers are distributed in O\*NET for scientific occupations, for instance that about 30% of tasks are done by all researchers. Without this, models underestimate how many researchers do common tasks and overstate importance. These anchors were tuned on the same O\*NET tasks used to evaluate them in [Section 6.1](#61-onet-expert-ratings), so that evaluation is not independent.

---

## 5. Substeps and time estimates

Each task is broken into steps, and each step is timed, in two separate calls to Claude Opus 4.8. The first lists the steps in the order they are done, with no mention of time, and is shown the neighbouring tasks so that it does not repeat them.

The second estimates, for each step, how many times it is done in one instance of the task, the hands-on time of each repetition, and the elapsed time including waiting. The model is asked for a typical instance, a researcher of average skill, and no help from generative AI. The task totals in [`data/task_time.csv`](data/task_time.csv) add up the steps, so elapsed time assumes the steps happen one after another.

The same task can mean different work in different places, so time is estimated separately wherever the task is performed: subfield tasks in their subfield, field and domain tasks in each subfield where the model judges them to be performed (2,662 of 3,099 field placements and 6,335 of 7,387 domain placements), and universal tasks once per field, in 1,016 of the 1,020 task-field pairs (the rest the model judged not to apply in that field).

For a typical task timed in five or more subfields, the longest estimate is about 2.4 times the shortest for hands-on time and 3.6 times for elapsed time.

2 subfield tasks, in Physiology and Plant Pathology, have no steps or times.

---

## 6. Validation

SciNet is validated against three external sources: O\*NET's expert ratings of scientific occupations, laboratory protocols published by researchers, and the text of published papers.

### 6.1 O\*NET expert ratings

The rating prompt was benchmarked on 425 researcher-relevant O\*NET tasks from 40 scientific occupations, by rating them with the SciNet prompt and comparing the result to what O\*NET collected from workers in those occupations.

Claude Opus 5, which produced the released ratings, correlates with the O\*NET values at r = 0.66 on importance, r = 0.63 on relevance, and r = 0.75 on frequency.

### 6.2 Research protocols

Protocols are the most granular external source available, recording what a researcher does, in what order, action by action. From [protocols.io](https://www.protocols.io/) we assembled 26,404 protocols: roughly 20,600 through the site's public API, about 5,800 more through DOIs indexed in OpenAlex, and 15 through CrossRef under the protocols.io DOI prefix.

**Timing.** 4,790 of these protocols give durations for 47,009 steps. Each SciNet step in a wet-lab subfield was matched to the most similar protocol steps, and a model judged whether each pair describes the same action. On the 769 exact matches, covering 383 SciNet steps, our elapsed-time estimate correlates with the protocol's duration at r = 0.53.

Protocols also disagree with each other, because the same action takes different times in different laboratories. For steps matched to at least two protocols, one protocol's duration predicts the others at r = 0.44, and our estimate predicts them at r = 0.55. The difference is not statistically significant: our estimates agree with protocols about as well as protocols agree with each other.

### 6.3 Published papers

The prevalence measurement in [Section 3](#3-expanding-the-tasks-with-papers) also checks the task list against the literature: it reports the share of a subfield's papers that show the task being performed. For the tasks that existed before the expansion this is the judged share on a fixed sample; for the tasks the expansion added it is the share from the scoring step with the papers that proposed the task left out, marked `expansion` in the file. Released as [`data/task_prevalence.csv`](data/task_prevalence.csv), it is the counterpart to the relevance rating: one records what a model believes about a subfield, the other what its papers contain.

The quotes required at the judging step allow the judgments to be audited. In a check of 179 quotes from 52 papers, none was invented; the few mismatches came from our own text extraction merging footnotes into sentences.
