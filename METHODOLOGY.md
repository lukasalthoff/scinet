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

SciNet organizes all scientific disciplines into three levels, and currently contains 6 domains, 34 fields, and 318 subfields.

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

> "Plan, design, or conduct surveys using questionnaires, focus groups, or interviews."

> "Compile, analyze, and report data to explain economic phenomena and forecast trends."

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

The 30 universal tasks are organized into ten categories, which every task in the database inherits: Reading & Knowledge Acquisition, Ideation & Hypothesis Generation, Data Gathering, Data Analysis, Theoretical Analysis, Design & Development, Writing & Communication, Peer Review & Service, Mentorship & Teaching, and Administration. Three universal tasks and the Design & Development category were added in August 2026, after a systematic audit of the task database showed the original universal list under-covered three activities entire disciplines run on: interpretive analysis of qualitative sources, formal theoretical work, and designing and building artifacts. Theoretical Analysis was split out of Data Analysis in September 2026 so that formal theory, the core method of mathematics and theoretical fields, is not filed as data work; see [WORK_ACTIVITIES.md](WORK_ACTIVITIES.md) for the two work activities moved under it at the same time.

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
To validate existing tasks and fill in missing tasks, we randomly sampled 100 papers from each subfield and had an LLM determine whether (i) the existing tasks were performed by that paper and (ii) there were any tasks performed by the paper that are missing from the existing tasks. We then consolidated suggestions for new tasks and removed tasks that did not appear in a sufficient number of papers. The process is described in detail below.


**1. Draw.** We draw journal articles from 2000 to 2020. Papers need a DOI, are drawn weighted by citations, and are targeted at 100 usable papers per subfield. The crosswalk released as [`data/openalex_topic_subfield_mapping.csv`](data/openalex_topic_subfield_mapping.csv), widened by [`data/topic_frame_overlay.csv`](data/topic_frame_overlay.csv), defines which papers are eligible to be drawn for a subfield. The subfield is then assigned by a model reading the retrieved text, which also drops non-research and off-field papers. Papers must be in English, carry at least one citation, be typed as articles, and have open-access full text, which is truncated at 20,000 characters. 

**2. Judge.** For each paper and each task in its subfield, a model returns one of three verdicts: *stated explicitly*, with a verbatim quote, *clearly implied*, meaning the work required the task though the paper does not narrate it, or *not involved*. The average over the sample is that task's **prevalence**, released as [`data/task_prevalence.csv`](data/task_prevalence.csv).

**3. Elicit.** For 50 papers per subfield a model is asked what research work the paper performed, with a quote required for each claim. It is shown the subfield's current tasks, the tasks of sibling subfields, and the universal and domain tasks, and marks each activity it finds as covered by an existing task, covered by a task filed in another subfield, or uncovered. Only uncovered activities can become candidates. The elicitation is therefore not blind to the taxonomy: it is a search for gaps in it. 

**4. Referee.** Each proposal is refereed against the tasks that already exist, in the subfield, in sibling subfields, and at the field and domain levels. 

**5. Consolidate.** Survivors are clustered into candidate tasks, and a candidate is kept only if independent papers proposed it, with a floor of max(2, 3% of papers elicited). 

**6. Score.** Surviving candidates are measured with the same involvement prompt the listed tasks were measured with, and must clear a 5% adoption bar. Scoring reuses the subfield's existing corpus in the same seeded order, so the first wave overlaps the papers the candidate was elicited from and the adoption share is in-sample. A one-time check against a freshly drawn corpus gave a mean gap of 4.2 percentage points and a correlation of 0.97. Scoring runs in sequential waves of 25, 60, and 100 papers. After each wave a Beta-Binomial posterior gives the probability that the final share lands above the bar, and scoring stops once that probability is outside 2 to 98% and the standard error is small enough. Most runs went to 100 papers.

**7. Raise.** A task proposed across many subfields of a field, or many fields of a domain, is filed once at that higher level instead of repeatedly below it.

The run added 2,297 tasks as it finished: 1,905 at subfield level, 327 at field level, and 65 at domain level. After the later consolidation and retirement of two subfields, the release carries 321 field-level tasks.

---

## 4. Rating each task

Following [O\*NET](https://www.onetonline.org/), each task is rated on three scales, separately for every subfield it appears in:

- **Importance (1 to 5).** How important is this task to researchers in this area?
- **Relevance (0 to 100).** Out of 100 researchers in this area, how many perform this task at least occasionally?
- **Frequency (1 to 7).** How often is this task performed, from yearly or less to hourly or more?

O\*NET collects these from surveys of workers in each occupation. We replicate that instrument by prompting a language model to take the perspective of a researcher with ten or more years of experience in the target subfield, and to rate a group of that subfield's tasks in a single call, which keeps the ratings on a consistent scale within a session. Each subfield is rated in four calls, one for each level of task it carries, giving 1,272 requests. The released ratings were produced with Claude Opus 5 through the Batch API, covering 25,849 ratings. The three universal tasks added in August 2026 were added after the rating run and are not rated, so 27 of the 30 universal tasks carry ratings.

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

The prompt carries distribution anchors calibrated against O\*NET's own values for scientific occupations, for instance that 100 should be the most common relevance answer and should be used for around 30% of tasks. Without them a model understates how many researchers perform a common task and overstates how important tasks are. [Section 6.1](#61-onet-expert-ratings) reports how the calibrated prompt performs, on the same task-occupation pairs the anchors were tuned on, so that comparison is in-sample.

---

## 5. Substeps and time estimates

Each task is decomposed into the substeps a researcher performs, and each substep is timed. Both calls used Claude Opus 4.8. The two run as separate model calls. The first decomposes the task in workflow order, with no reference to time, and is shown the sibling and higher-level tasks it must not restate.

The second takes those fixed substeps and returns four primitives for each: how many times it is performed in one instance of the task, whether those repetitions overlap, the attended effort for a single pass, and the elapsed time for a single pass including unattended waiting. Unattended time is counted only when something named is being waited on. The model is asked for the expected value across instances, for a researcher of average expertise, and told not to assume generative AI assistance. The `researcher_hours` and `elapsed_hours` columns of [`data/task_time.csv`](data/task_time.csv) are computed in code from those primitives by summing over substeps, so elapsed time assumes substeps run one after another.

Timing is estimated separately for each scope a task is performed in, because the same task means different work in different places. Subfield tasks are timed in their own subfield. Field and domain tasks are timed in each subfield where the model judges the task to be performed, which is 2,662 of 3,099 field placements and 4,100 of 7,387 domain placements. Universal tasks are timed once per field rather than per subfield, in 1,013 of the 1,020 task-field pairs.

Across the 409 domain-, field- and subfield-level tasks timed in five or more subfields, the median task varies by a factor of 2.2 in `researcher_hours` and 3.2 in `elapsed_hours`, measured as the ratio of the largest to the smallest estimate.

Two subfield placements have no decomposition and no time: a Physiology task and a Plant Pathology task, both on preparing materials for experiments.

---

## 6. Validation

SciNet is validated against three external sources: O\*NET's expert ratings of scientific occupations, laboratory protocols published by researchers, and the text of published papers.

### 6.1 O\*NET expert ratings

The rating prompt was benchmarked on 425 researcher-relevant O\*NET tasks from 40 scientific occupations, by rating them with the SciNet prompt and comparing the result to what O\*NET collected from workers in those occupations.

Claude Opus 5, which produced the released ratings, correlates with the O\*NET values at r = 0.66 on importance, r = 0.63 on relevance, and r = 0.75 on frequency.

### 6.2 Research protocols

Protocols are the most granular external source available, recording what a researcher does, in what order, action by action. From [protocols.io](https://www.protocols.io/) we assembled 26,404 protocols: roughly 20,600 through the site's public API, about 5,800 more through DOIs indexed in OpenAlex, and 15 through CrossRef under the protocols.io DOI prefix.

OpenAlex classifies these protocols poorly, so a model routes each one instead: it checks the field against the title, abstract, and first three steps and corrects it, then picks a subfield, then a topic with a confidence score. Only protocols scoring 4 or 5 out of 5 are used.

**Coverage.** Each step is matched against the existing SciNet tasks. Steps are first classified as *placeholder*, meaning a pointer to a prior protocol, which is excluded, *prep*, or *substantive*. Coverage, the share of non-placeholder steps matched to a task, exceeds 85% for most protocols. Uncovered steps are grouped by topic, a model proposes O\*NET-style statements for them, and the proposals are deduplicated against existing tasks before being added.

**Timing.** Across 26,404 protocols carrying 47,009 author-timed steps, every SciNet substep is embedded against every timed step, the closest candidates retrieved, and a model judges each pair an exact, partial, or non-match. On the 769 exact matches covering 383 substeps in wet-lab fields, our elapsed-time estimate correlates with the observed duration at r = 0.53.

Read that against how well protocols.io agrees with itself, since the same action genuinely takes different amounts of time in different laboratories. One real protocol step predicts the others matched to the same substep at r = 0.44, while our estimate predicts those same steps at r = 0.55. Two real protocols agree with each other less than our estimate agrees with either.

### 6.3 Published papers

The prevalence measurement in [Section 3](#3-expanding-the-tasks-with-papers) is itself a validation of the task list, reporting for every task and subfield the share of that subfield's papers whose text shows the task being performed. Released as [`data/task_prevalence.csv`](data/task_prevalence.csv), it is the empirical counterpart to the relevance rating: one measures what a model believes about a subfield, the other what its papers contain.

The quotes required at the judge stage are the audit trail. Of those, 179 were checked against the papers' own text and none was invented, with the residual mismatches traced to our own PDF extraction splicing footnote text into sentences.
