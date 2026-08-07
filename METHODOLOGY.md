# SciNet Methodology

This page outlines how SciNet was created and validated.

## Steps

1. **[Generating the taxonomy](#1-generating-the-taxonomy).** Prompting a language model to divide science into domains, fields, and subfields, then correcting the result on expert feedback.
2. **[Initial task generation](#2-initial-task-generation).** Writing task statements in O\*NET's format, working down the hierarchy from tasks that apply to all researchers to tasks specific to one subfield.
3. **[Expanding the tasks with papers](#3-expanding-the-tasks-with-papers).** Reading published papers to find research activities the initial list had missed, and measuring how often each task appears in the literature.
4. **[Rating each task](#4-rating-each-task).** Estimating the importance, relevance, and frequency of every task in every subfield it appears in.
5. **[Substeps and time estimates](#5-substeps-and-time-estimates).** Breaking each task into the steps a researcher performs and estimating how long each one takes.
6. **[Validation](#6-validation).** Checking the ratings against O\*NET, the time estimates against laboratory protocols, and the task list against the papers themselves.

Three further sections cover the [indicators](#7-field-and-subfield-indicators) reported alongside the tasks, the [models](#8-models-and-infrastructure) each step was run with, and [work in progress](#9-ongoing-work).

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

The prompt aims at a map of how research communities are actually organized, rather than how journals, funders, or bibliographic databases classify published work. That is why fields are drawn where researchers recognize a boundary, so that Economics, Sociology, Political Science, and Psychology each stand as their own field rather than being folded together, and why a subfield is meant to correspond to a group of researchers who read each other's work and share a set of methods.

We then made manual corrections to the taxonomy, many of them in response to researchers who reviewed the parts of it covering their own areas. Those researchers are listed on the [contributors page](https://www.anatomyofscience.com/#/contributors).

---

## 2. Initial task generation

### 2.1 How a task statement is written

All SciNet tasks follow the [O\*NET](https://www.onetonline.org/) canonical task statement structure:

```
[Action Verb] + [Object] + [Modifiers] + [Purpose]
```

The writing rules are drawn from the instructions O\*NET gives its human analysts. A statement begins with a present-tense action verb such as *Analyze*, *Design*, or *Estimate*, names the object being acted on, adds optional modifiers specifying how or under what conditions, and ends with an optional purpose introduced by "to". Each statement carries one core action rather than a chain of steps, runs to roughly 8 to 18 words, and uses plain language. Three reference statements from O\*NET:

> "Analyze data from research conducted to detect and measure physical phenomena."

> "Plan, design, or conduct surveys using questionnaires, focus groups, or interviews."

> "Compile, analyze, and report data to explain economic phenomena and forecast trends."

Tasks describe the work of a research team rather than of a single individual, and what a typical researcher in the area does rather than what they might occasionally do.

### 2.2 Working down the hierarchy

Task generation runs top down. It starts with the universal tasks that apply to every researcher, then proceeds through progressively more specific levels. At each step the model receives every task already defined at the levels above and generates refinements of them, so a subfield task is a specialization of a domain task rather than a restatement of it. Each generated task records the parent task it refines, which makes the full chain traceable from any subfield task up to a universal task.

| Level | Scope | How it was written | Coverage threshold |
|-------|-------|--------------------|--------------------|
| Universal | All researchers | Model-drafted, researcher-reviewed | |
| Domain | e.g. Social Sciences | Model-drafted, researcher-reviewed | |
| Subfield | e.g. Labor Economics | Model-generated | 70% of subfield researchers |
| Topic | e.g. Labor Market and Education | Model-generated | 80% of topic researchers |

The universal and domain levels anchor the whole hierarchy, so they were developed iteratively with a researcher in the loop: the model drafted candidate tasks, a researcher reviewed them and flagged problems, and the model revised, repeating until the granularity and the boundaries between tasks were right.

The 27 universal tasks are organized into eight categories, which every task in the database inherits: Reading & Knowledge Acquisition, Ideation & Hypothesis Generation, Data Gathering, Data Analysis, Writing & Communication, Peer Review & Service, Mentorship & Teaching, and Administration. This level is what keeps grant writing, refereeing, and mentoring in every researcher's profile, since none of them is ever mentioned in a paper or a protocol.

Domain tasks capture practices characteristic of a whole domain that do not carry across domains, such as review board approval in the Social and Health Sciences, instrument calibration in the Physical Sciences, and biosafety procedure in the Life Sciences. All six domains carry a curated layer of them, ranging from 13 tasks in Formal Sciences to 28 in Arts & Humanities.

The topic level was generated but is not part of the public release, since topics are used only to route papers to a subfield. There is no field level in this stage either, because a task is only filed at the field level once it turns out to recur across the field's subfields, which happens in Section 3. The released taxonomy therefore has four levels, carrying 27 universal, 134 domain, 321 field, and 6,777 subfield tasks.

### 2.3 The prompt

<details>
<summary>Subfield task generation prompt</summary>

```
You are generating task statements for researchers in {subfield_name}
(a subfield of {domain_name}).

INPUT: DOMAIN TASKS ({domain_name})
These are the domain-level tasks. Your job is to generate subfield-specific
refinements of these.

  {numbered domain tasks, each showing the universal task it refines}

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

We iterated on this prompt to remove the mistakes the model made repeatedly. Controlling specificity is the central problem: left alone, the model writes tasks pinned to one method or one dataset, and writes several near-identical tasks where researchers would recognize a single activity. The rules against hyperspecific tasks and for aggressive consolidation address the first problem, and the coverage threshold addresses both, since a task that only a minority of the subfield performs is usually a task written too narrowly. The threshold also plays the role O\*NET's relevance rating plays, keeping the list to activities that are common and substantial.

---

## 3. Expanding the tasks with papers

The tasks in Section 2 were written from what a language model knows about a field. The obvious question is whether they match what researchers publish, and the obvious source for an answer is the papers themselves. This step both tests the existing list against published work and finds the activities it is missing, and in practice it is where a large share of the released tasks came from. The production run covered all 34 fields and 318 subfields over 31,576 papers.

Papers do not narrate their own procedures. A paper that plainly ran a difference-in-differences will rarely write "we constructed a panel dataset," because its readers already know what the method requires. Everything below is designed around that asymmetry, since a task can be missing from a paper's text and still be part of the work the paper reports.

**1. Draw.** A paper's subfield is the SciNet subfield of its OpenAlex primary topic, through a crosswalk released as [`data/openalex_topic_subfield_mapping.csv`](data/openalex_topic_subfield_mapping.csv). Routing on the project's own classification rather than on keywords matters: a keyword prototype scattered badly, producing an economic history pool that was 4% economic history and mostly development economics. We draw English journal articles from 2000 to 2020, which is before ChatGPT, so no method described was itself AI-assisted, carrying a DOI and at least one citation, weighted by citations, targeting 100 usable papers per subfield.

**2. Judge.** For each paper and each task in its subfield, a model returns one of three verdicts: *stated explicitly*, with a verbatim quote, *clearly implied*, meaning the work required the task though the paper does not narrate it, or *not involved*. The average over the sample is that task's **prevalence**, released as [`data/task_prevalence.csv`](data/task_prevalence.csv).

**3. Elicit.** For 50 papers per subfield a model is shown the paper but not the taxonomy, and asked what research work the paper performed, with a quote required for each claim. Withholding the taxonomy is deliberate, since showing it would invite matching against tasks that already exist, which stage 2 does properly. The point is to hear what the paper did in its own terms, so that a genuine gap can surface.

**4. Referee.** Each proposal is refereed against the tasks that already exist, in the subfield, in sibling subfields, and at the field and domain levels. The prompt errs towards rejection, because a proposal wrongly kept can reach the taxonomy, while one wrongly rejected only means a task the next run can still find.

**5. Consolidate.** Survivors are clustered into candidate tasks, and a candidate is kept only if independent papers proposed it, with a floor of max(2, 3% of papers elicited). One paper describing its own method is not evidence of a gap, while two papers arriving at the same activity independently is the weakest evidence worth measuring.

**6. Score.** Surviving candidates are measured on a fresh sample, exactly as the listed tasks were, and must clear a 5% adoption bar. Scoring runs in sequential waves of 25, 60, and 100 papers. After each wave a Beta-Binomial posterior gives the probability that the final share lands above the bar, and scoring stops once that probability is outside 2 to 98% and the standard error is small enough. Most candidates settle at 25 papers.

**7. Raise.** A task proposed across many subfields of a field, or many fields of a domain, is filed once at that higher level instead of repeatedly below it.

The run measured 5,405 candidate tasks, of which 4,642 cleared the 5% bar and 359 were withheld as already covered by an existing field or domain task. It added 2,297 tasks, counted once each at the highest level they qualify for: 1,905 at subfield level, 327 at field level, and 65 at domain level.

---

## 4. Rating each task

Following [O\*NET](https://www.onetonline.org/), each task is rated on three scales, separately for every subfield it appears in:

- **Importance (1 to 5).** How important is this task to researchers in this area?
- **Relevance (0 to 100).** Out of 100 researchers in this area, how many perform this task at least occasionally?
- **Frequency (1 to 7).** How often is this task performed, from yearly or less to hourly or more?

O\*NET collects these from surveys of workers in each occupation. We replicate that instrument by prompting a language model to take the perspective of a researcher with ten or more years of experience in the target subfield, and to rate all of that subfield's tasks in a single call, which keeps the ratings on a consistent scale within a session. The released ratings were produced with Claude Opus 5 through the Batch API, covering 25,849 ratings.

Tasks are then classified as **Core** when relevance is at least 67 and importance is at least 3, and **Supplemental** otherwise, which is O\*NET's own rule.

<details>
<summary>Task rating prompt</summary>

```
You are completing a SciNet occupational survey, modeled on O*NET. SciNet is
O*NET for scientific tasks. You are working in a research role in
{occupation}, with 10+ years of experience.

Rate each task below on THREE scales:

1. IMPORTANCE (IM): How important is this task to your research area?
   Scale: 1=Not Important, 2=Somewhat Important, 3=Important,
          4=Very Important, 5=Extremely Important

2. PERCENT OF WORKERS (RT): Out of 100 researchers in this area, how many
   perform this task at least occasionally?
CRITICAL: Be hard-nosed and think realistically about the percentage of
researchers who perform this task. If it involes a specific method or
dataset, it is likely to be performed by a small minority of researchers.
   Scale: 0-100

3. FREQUENCY (FT): How often is this task performed?
   Scale: 1=Yearly or less, 2=More than yearly, 3=More than monthly,
          4=More than weekly, 5=Daily, 6=More than daily, 7=Hourly or more

TASKS:
{numbered task list}

Return your ratings as a JSON array with one object per task:
[
  {"task_num": 1, "im": <1-5>, "rt": <0-100>, "ft": <1-7>},
  ...
]

Return ONLY the JSON array, no other text.
```

</details>

The prompt was calibrated against O\*NET's own distributions for scientific occupations, because an uncalibrated model understates how many researchers perform a common task and overstates how important tasks are. The calibrated version carries explicit distribution anchors, for instance that 100 should be the most common relevance answer and should be used for around 30% of tasks, and that most tasks belong at importance 3 or 4 with only a small minority at 5. Section 6.1 reports how the calibrated prompt performs against O\*NET.

---

## 5. Substeps and time estimates

Each task is decomposed into the substeps a researcher actually performs, and each substep is timed. The two jobs run as separate model calls, because asking one call to produce structure and timing together lets the timing instructions distort the structure. An earlier version capped any substep at 90 minutes and told the model to split anything longer, which turned a timing rule into a decomposition rule: only 13 distinct minute values appeared across 30,618 substeps, and 82% of them were one of the seven numbers the prompt itself had named.

The first pass decomposes the task into substeps in workflow order, with no reference to time. The second pass takes the task and its fixed substeps and returns three primitives for each substep: how many times it is performed in one instance of the task, the attended human effort for a single pass, and the elapsed time for a single pass including unattended waiting. Every total in [`data/task_time.csv`](data/task_time.csv) is computed in code from those primitives, which is what produces the two columns `researcher_hours` and `elapsed_hours`.

Separating attended effort from elapsed time is also what makes the estimates checkable. A protocol duration is a timer on waiting rather than on hands-on work, so it can be compared against the elapsed limb and says nothing about the effort limb. Section 6.2 reports that comparison.

Because the same task means different work in different subfields, timing is estimated separately for each subfield a task appears in. Across the 140 tasks that reach five or more subfields, the median task varies by a factor of 2.5 in `researcher_hours` and 4.1 in `elapsed_hours` across the subfields it appears in.

---

## 6. Validation

SciNet is validated against three external sources that document research activity independently of any language model: O\*NET's expert ratings of scientific occupations, laboratory protocols published by researchers, and the text of published papers.

### 6.1 O\*NET expert ratings

The rating prompt in Section 4 was benchmarked against 425 researcher-relevant O\*NET tasks drawn from 40 scientific occupations, by rating the O\*NET tasks with the SciNet prompt and comparing the result to the ratings O\*NET collected from workers in those occupations.

Claude Opus 5, which produced the released ratings, correlates with the O\*NET values at r = 0.66 on importance, r = 0.63 on relevance, and r = 0.75 on frequency. The earlier Claude Opus 4.5 pass scored 0.60, 0.63, and 0.76. The correlations are close to identical, but the level moved: Opus 4.5 under-reported relevance by 5.9 percentage points against O\*NET, while Opus 5 is within 0.9 points. Earlier releases lowered the Core threshold from 67 to 50 to offset that downward bias, and since the bias is gone the compensation has been removed.

### 6.2 Research protocols

Step-by-step research protocols are the most granular external source available, since they record exactly what a researcher does, in what order, at the level of individual actions. [Protocols.io](https://www.protocols.io/) is a platform where researchers publish laboratory and research protocols across a wide range of disciplines. We assembled a corpus of roughly 20,600 protocols from public protocols via the protocols.io API, unlisted protocols with DOIs indexed in OpenAlex, and further protocols found through CrossRef under the protocols.io DOI prefix.

Protocols carry DOIs, so most can be merged with OpenAlex, but we found OpenAlex's topic-level classification of protocols to be frequently wrong, so each protocol is routed to a SciNet field, subfield, and topic by a model instead. The model first checks the assigned field against the protocol's title, abstract, and first three steps and corrects it, which in pilot runs corrected roughly 70% of protocols, then selects a subfield, then selects a topic with a confidence score, and only protocols rated 4 or 5 out of 5 are used.

**Coverage.** Each procedure step is then checked against the existing SciNet tasks at topic, subfield, and field level. Steps are classified as *placeholder*, meaning an instruction to follow a prior protocol, which is excluded, *prep*, meaning a routine preparatory action, or *substantive*. Coverage is the share of non-placeholder steps matched to a SciNet task, and with correct field routing it exceeds 85% for most protocols. Uncovered steps are grouped by topic, a model proposes O\*NET-style statements to cover them, and the proposals are deduplicated against the existing tasks before being added.

**Timing.** Protocol steps carry author-marked durations, which is how the estimates in `task_time.csv` are checked. Across 26,404 protocols carrying 47,009 timed steps, every SciNet substep is embedded against every timed step, the closest candidates are retrieved, and a model judges each pair as an exact, partial, or non-match. On the 769 exact matches covering 383 substeps in wet-lab fields, our elapsed-time estimate correlates with the observed duration at r = 0.53.

That number is best read against how well protocols.io agrees with itself, because the same action genuinely takes different amounts of time in different laboratories, which puts a ceiling on how high any correlation with it can go. A single real protocol step predicts the other steps matched to the same substep at r = 0.44, while our estimate predicts those same steps at r = 0.55. Two real protocols therefore agree with each other less than our estimate agrees with either of them.

### 6.3 Published papers

The prevalence measurement in Section 3 is itself a validation of the task list: it reports, for every task and every subfield, the share of that subfield's papers whose text shows the task being performed. It is released as [`data/task_prevalence.csv`](data/task_prevalence.csv) and is the empirical counterpart to the relevance rating in Section 4, with one measuring what a model believes about a subfield and the other measuring what that subfield's papers actually contain.

The quotes required at the judge stage are the audit trail. Of those quotes, 179 were checked against the papers' own text and none was found to be invented, with the residual mismatches traced to our own PDF extraction splicing footnote text into sentences.

---

## 7. Field and subfield indicators

Alongside the tasks, the website reports indicators that characterize each field and subfield, computed from [OpenAlex](https://openalex.org/) and aggregated from topic-level data.

**Publication activity.** Total paper and citation counts per field and subfield, yearly counts of papers mentioning AI-related terms as a share of all papers in the field, and average days from submission to publication where available.

**Verifiability.** An index capturing the degree to which research outputs are presented in ways that support independent replication and scrutiny. It combines three topic-level components weighted by paper count: the share of papers retracted, the frequency of hedging words per 100 words of abstract text, such as "may", "suggest", and "appear", and the frequency of booster words, such as "clearly", "demonstrate", and "establish". Each subfield receives a percentile rank on the composite and on each component.

---

## 8. Models and infrastructure

| Component | Model |
|-----------|-------|
| Taxonomy drafting | Claude |
| Task generation | Claude Opus 4.5 |
| Paper expansion and prevalence | Claude Sonnet 5 |
| Task ratings | Claude Opus 5 |
| Substep decomposition and timing | Claude Opus 4.8 |
| Protocol routing and step matching | Claude Sonnet 4.5 |

All models are accessed through the Anthropic API. The large batch jobs, including topic-level task generation and the task ratings, run through the [Anthropic Batch API](https://docs.anthropic.com/en/docs/build-with-claude/message-batches). Prompt caching is used for system prompts and shared context blocks, and every long-running step checkpoints its results so that an interrupted run resumes without reprocessing what it has already done.

---

## 9. Ongoing work

Data collection continues on two fronts. Step-level coverage and timing now run over the full protocols.io corpus, and task generation from the steps that remain uncovered is ongoing. Full-text processing of papers is being extended to a larger sample of OpenAlex and arXiv, with particular attention to computational, theoretical, and social science fields.
