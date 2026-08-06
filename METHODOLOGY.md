# SciNet Methodology

SciNet is a task-level database of scientific research — a comprehensive map of what researchers actually do, broken down by domain, field, and subfield. The public release covers 7,259 task statements spanning 6 domains, 34 fields, and 318 subfields, from Microfinance and Financial Inclusion to Quantum Computing to Clinical Oncology. OpenAlex topics are used to route papers to a subfield; they are not a level of the taxonomy and carry no tasks of their own.

SciNet uses AI and information from thousands of laboratory protocols, published paper texts, and scientific expert input to map the anatomy of scientific work. These sources together capture both the tacit, hands-on dimensions of research and its more codified methodological conventions.

This document describes how SciNet was built.

<p align="center"><img src="https://raw.githubusercontent.com/lukasalthoff/scinet/main/pipeline.svg" alt="SciNet pipeline diagram" width="680"/></p>

---

## Table of Contents

1. [Taxonomy](#1-taxonomy)
2. [Task Statement Design](#2-task-statement-design)
3. [Task Generation](#3-task-generation)
4. [Ground Truth Data](#4-ground-truth-data)
5. [Data Enrichment](#5-data-enrichment)
6. [Models and Infrastructure](#6-models-and-infrastructure)
7. [Ongoing and Future Work](#7-ongoing-and-future-work)

---

## 1. Taxonomy

### 1.1 An independent taxonomy

SciNet's taxonomy is **not** derived from any existing classification. It was
constructed independently, to track disciplinary boundaries as researchers
themselves describe them, and has three levels:

| Level | Count | Example |
|-------|-------|---------|
| Domain | 6 | Physical Sciences |
| Field | 34 | Physics & Astronomy |
| Subfield | 318 | Condensed Matter Physics |

The six domains are Formal Sciences, Physical Sciences, Life Sciences, Health
Sciences, Social Sciences, and Arts & Humanities. Fields were defined to match
how research communities are actually organized — Economics, Sociology,
Political Science and Psychology are separate fields rather than one lump — and
the subfields within each field were then drafted by asking a language model how
a researcher in that field would organize its major subfields, and curated from
there.

The field-to-domain grouping is kept in a single canonical file
(`code/scinet/domains.json`) with a check script that fails the build if any
copy drifts from it. Six copies of that mapping once diverged, which shipped
Philosophy as a Social Science in the data while the website showed it under
Arts & Humanities.

### 1.2 Routing papers into subfields

Assigning a task hierarchy is separate from assigning *papers*. To count papers
per subfield, SciNet uses [OpenAlex](https://openalex.org/) topics purely as a
routing layer: each OpenAlex topic is mapped to the SciNet subfield it belongs
to, and a paper inherits the subfield of its topic. That crosswalk ships as
[`data/openalex_topic_subfield_mapping.csv`](data/openalex_topic_subfield_mapping.csv).

Topics are **not** a level of the SciNet taxonomy and carry no tasks of their
own. The mapping is two-pass: most topics map deterministically to a subfield,
and a language model classifies the ambiguous remainder given the topic's name,
keywords, and summary.

---

## 2. Task Statement Design

All SciNet tasks follow the [O\*NET](https://www.onetonline.org/) canonical task statement structure. The prompts used for task generation closely follow the instructions that [O\*NET](https://www.onetonline.org/) gives to human analysts:

```
[Action Verb] + [Object] + [Modifiers] + [Purpose]
```

**Writing rules (drawn from [O\*NET](https://www.onetonline.org/) analyst guidelines):**

- Begin with a present-tense action verb (e.g., *Analyze*, *Design*, *Develop*, *Estimate*, *Collect*)
- Include the object being acted on
- Add optional modifiers specifying how or under what conditions
- End with an optional purpose introduced by "to …"
- One core action per statement; avoid chained steps
- Approximately 8–18 words
- Plain language; avoid jargon unless necessary for precision
- Parallel structure across statements; mutual exclusivity encouraged

**Reference examples from [O\*NET](https://www.onetonline.org/):**

> "Analyze data from research conducted to detect and measure physical phenomena."

> "Plan, design, or conduct surveys using questionnaires, focus groups, or interviews."

> "Compile, analyze, and report data to explain economic phenomena and forecast trends."

Tasks are written at the level of a *research team*, not a single individual. Statements describe what a typical researcher in the field *does*, not what they might occasionally do.

### 2.1 Prompt design

Controlling specificity is the central design challenge. The prompt includes the [O\*NET](https://www.onetonline.org/) analyst instructions nearly verbatim, together with explicit constraints against over-specificity: "AVOID HYPERSPECIFIC TASKS," "AVOID EXAMPLES THAT ARE TOO SPECIFIC, such as hyperspecific methodologies or datasets," and "CONSOLIDATE AGGRESSIVELY — if multiple tasks require the same skills or are part of the same workflow, combine them into ONE task." Coverage thresholds (see [Section 3.4](#34-coverage-thresholds) below) push the model toward tasks that a *majority* of researchers in the area perform regularly, reinforcing the same principle.

---

## 3. Task Generation

SciNet uses a **top-down hierarchical generation** approach. Starting at the most general level (universal tasks common to all researchers), the pipeline works downward through progressively more specific levels. At each step, the language model receives all tasks already defined at parent levels and generates refinements — tasks that are genuine specializations of their parents, not repetitions of what has already been captured above. Every subfield task must map to a specific domain parent, and every topic task must map to a specific subfield parent, ensuring the full hierarchy is traceable from any topic-level task up to a universal task.

### 3.1 Level structure

| Level | Scope | Source | Coverage threshold |
|-------|-------|--------|--------------------|
| Universal | All researchers | LLM-generated, researcher-supervised | — |
| Domain | e.g., Social Sciences | LLM-generated, researcher-supervised | — |
| Field | e.g., Economics | — | — |
| Subfield | e.g., Labor Economics | LLM-generated (unsupervised) | ≥ 70% of subfield researchers |
| Topic | e.g., Labor Market and Education | LLM-generated (unsupervised) | ≥ 80% of topic researchers |

The topic level was generated but is **not part of the public release**: topics are used only to
route papers to a subfield. The released taxonomy has four levels — universal, domain, field, and
subfield — carrying 27, 134, 321, and 6,777 tasks respectively.

### 3.2 Supervised levels (Universal and Domain)

The universal and domain levels anchor the entire hierarchy and needed to be correct. Rather than writing these tasks from scratch, we developed them through an iterative process with Claude Opus: the model drafted candidate tasks, a researcher reviewed them, flagged issues, and the model revised — repeating until the tasks reflected the right level of granularity and mutual exclusivity. The result is LLM-generated content that has been carefully vetted.

**Universal tasks**

These tasks apply to virtually all researchers regardless of field, organized into eight categories: Reading & Knowledge Acquisition, Ideation & Hypothesis Generation, Data Gathering, Data Analysis, Writing & Communication, Peer Review & Service, Mentorship & Teaching, and Administration. Examples include "Review and synthesize the relevant literature to situate a research question within existing knowledge," "Identify gaps in existing literature to formulate novel research questions," and "Manage research budgets, personnel, and project timelines."

The universal level ensures that tasks like grant writing, peer review, and mentoring — which are never mentioned in papers or protocols — are still represented in every researcher's task profile.

**Domain tasks**

Domain tasks are domain-specific refinements of universal tasks, each explicitly linked to the universal task it refines. The public taxonomy is organized into six domains: Formal Sciences, Physical Sciences, Life Sciences, Health Sciences, Social Sciences, and Arts & Humanities. All six carry a curated domain-task layer, from 13 tasks in Formal Sciences to 28 in Arts & Humanities. These domain tasks capture practices characteristic of an entire research domain that would not apply across all domains — for example, IRB approval workflows in the Social Sciences and Health Sciences, instrument calibration procedures in the Physical Sciences, or biosafety protocols in the Life Sciences.

### 3.3 Unsupervised levels (Subfield and Topic)

From the subfield level downward, task generation is fully automated. The language model receives the parent-level tasks as numbered input and must produce refinements that each map to a specific parent:

**Subfield prompt (excerpt):**

> You are generating task statements for researchers in {subfield\_name} (a subfield of {domain\_name}).
>
> INPUT: DOMAIN TASKS ({domain\_name})
> These are the domain-level tasks. Your job is to generate subfield-specific refinements of these.
>
> OBJECTIVE: Generate subfield-specific refinements of the domain tasks above. Each subfield task you generate should:
> - Refine ONE specific domain task (specify which domain task number it refines)
> - Be specific to {subfield\_name} (would NOT apply to other subfields)
> - Be common enough that **70%+ of {subfield\_name} researchers** do it regularly

**Topic prompt (excerpt):**

> Each topic task you generate should:
> - Refine ONE specific subfield task (specify which subfield task number it refines)
> - You DO NOT need to have one topic task for each subfield task. You may skip some subfield tasks, and some subfield tasks may have multiple topic tasks.
> - Be specific to {topic\_name} (would NOT apply to other topics in {subfield\_name})
> - Be common enough that **80%+ of {topic\_name} researchers** do it regularly

Each generated task includes an explicit parent ID linking it to the domain task (for subfield tasks) or subfield task (for topic tasks) it refines, enabling full parent-chain tracing from any topic-level task up to the relevant universal task.

### 3.4 Coverage thresholds

The coverage thresholds (70% at the subfield level, 80% at the topic level) serve a dual purpose. They push the model toward tasks that represent common, substantial research activities — analogous to [O\*NET](https://www.onetonline.org/)'s concept of "relevance" — and they push against overly specific tasks (e.g., a particular niche dataset or one-off technique) that would inflate the task count without adding representational value. The tighter threshold at the topic level reflects that topic tasks should be highly characteristic of the specific research area.

**Execution:** Subfield tasks are generated in parallel using a thread pool. Topic tasks are generated via the [Anthropic Batch API](https://docs.anthropic.com/en/docs/build-with-claude/message-batches), which processes hundreds of topics concurrently.

### 3.5 Deduplication and quality control

- **Prompt-level:** The model is instructed to ensure mutual exclusivity across tasks and to avoid vague catch-all statements ("analyze data," "collect data"). Parent tasks are provided in the prompt explicitly so the model can avoid paraphrasing them.
- **Code-level:** After parsing model responses, a normalization function deduplicates tasks by exact string match after whitespace normalization.
- **Error handling:** If a model response cannot be parsed as valid JSON, a regex fallback extracts the task list from code blocks or raw text. Unparseable responses are logged as errors without discarding the run. All generation is checkpointed so interrupted runs can resume.

---

## 4. Ground Truth Data

A central question is whether the LLM-generated tasks actually reflect what researchers do in practice. We use two sources of external ground truth that document real research activity independently of any LLM — published **research protocols** and published **papers**. Each serves both to validate existing tasks and to surface activities that are missing.

### 4.1 Research Protocols

Detailed step-by-step research protocols are our most granular ground-truth source: they describe exactly what a researcher does, in what order, at the level of individual actions.

**[Protocols.io](https://www.protocols.io/)** is a platform where researchers publish laboratory and research protocols, covering a wide range of disciplines. We assembled a corpus of approximately 20,600 protocols from three sources: public protocols via the protocols.io API, unlisted protocols with DOIs indexed in [OpenAlex](https://openalex.org/), and additional protocols identified through CrossRef under the protocols.io DOI prefix (10.17504). Because protocols.io protocols carry DOIs, the vast majority can be merged with [OpenAlex](https://openalex.org/), giving us the field and — in principle — the topic each protocol belongs to. We found, however, that [OpenAlex](https://openalex.org/)'s topic-level classification for protocols was often inaccurate, so we built an LLM-based assignment pipeline to route each protocol to the correct SciNet field, subfield, and topic.

Each protocol is routed to the SciNet topic it best represents and then checked step by step for coverage against existing tasks:

1. **Field validation.** A language model checks whether the [OpenAlex](https://openalex.org/)-assigned field is correct given the protocol title, abstract, and first three steps, and corrects it if not. (In pilot runs, roughly 70% of protocols had incorrect [OpenAlex](https://openalex.org/) field assignments.)
2. **Subfield assignment.** Given the corrected field, the model selects the best subfield.
3. **Topic assignment.** The model selects the best-matching SciNet topic from candidates within the subfield, providing a confidence score (1–5). Only protocols with confidence ≥ 4 are used in downstream analysis.
4. **Step coverage.** For each procedure step, the model determines whether it is covered by any existing SciNet task at the topic, subfield, or field level. Steps are classified as *placeholder* (instructions to follow a prior protocol, excluded), *prep* (routine preparatory actions), or *substantive* (steps corresponding to meaningful research tasks). Coverage is the fraction of non-placeholder steps matched to a SciNet task.

With correct field routing, step coverage exceeds 85% for most protocols. Uncovered steps are not discarded: they are grouped by topic, a language model proposes new [O\*NET](https://www.onetonline.org/)-style task statements to cover them, and proposed tasks are deduplicated against existing SciNet tasks (sequence similarity threshold: 90%) before being added to the database.

**Timing.** Protocol steps also carry author-marked durations, which is how the time estimates in `task_time.csv` are checked. Across the full corpus (26,404 protocols, 47,009 steps carrying a duration), every SciNet substep is embedded against every timed step, the closest candidates are retrieved, and a model judges each as an exact, partial, or non-match. On the 769 exact matches covering 383 substeps in wet-lab fields, our elapsed-time estimate correlates with the observed duration at r = 0.53. Because a protocol duration is a timer on waiting rather than on hands-on work, and because the same action genuinely varies between labs, the right yardstick is how well protocols.io agrees with itself: a single real protocol step predicts the other matched steps at r = 0.44, while our estimate predicts them at r = 0.55.

### 4.2 Research Papers

Protocols narrate their steps; papers do not. A paper that plainly ran a
difference-in-differences will rarely write "we constructed a panel dataset."
That asymmetry drives the design below, which both **tests** the listed tasks
against papers and **finds what the list is missing**.

The production run covered all 34 fields and 318 subfields over 31,576 papers
(2026-07-31 to 2026-08-03).

**1. Draw.** A paper's subfield is the SciNet subfield of its OpenAlex primary
topic, through the crosswalk in §1.2 — the project's own classification, not a
keyword match. (A keyword prototype scattered badly: an economic-history pool
that was 4% economic history and mostly development economics.) We draw English
journal articles from **2000–2020** — pre-ChatGPT, so no method described was
itself AI-assisted — carrying a DOI and at least one citation, weighted by
citations, targeting 100 usable papers per subfield.

**2. Judge.** For each paper and each task in its subfield, a model returns one
of three verdicts: *stated explicitly* (with a verbatim quote), *clearly
implied* (the work required the task, though the paper does not narrate it), or
*not involved*. The average over the sample is that task's **prevalence**,
released as `task_prevalence.csv`. Quotes are the audit trail: 179 were checked
against the papers' own text and none was invented; the residual mismatch is our
own PDF extraction splicing footnote text into sentences.

**3. Elicit.** For 50 papers per subfield a model is shown the paper **but not
the taxonomy**, and asked what research work the paper performed, with a quote
required for each claim. Withholding the taxonomy is deliberate — showing it
would invite matching against tasks that already exist, which step 2 already
does properly. The point is to hear what the paper did in its own terms, so a
genuine gap can surface.

**4. Referee.** Each proposal is refereed against the tasks that already exist —
in the subfield, in sibling subfields, and at field and domain level. The prompt
errs towards rejection: a proposal wrongly kept can reach the taxonomy, while
one wrongly rejected only means a task the next run can still find.

**5. Consolidate.** Survivors are clustered into candidate tasks, and a
candidate is kept only if **independent papers** proposed it, with a floor of
max(2, 3% of papers elicited). One paper describing its own method is not
evidence of a gap; two papers arriving at the same activity independently is the
weakest evidence worth measuring.

**6. Score.** Surviving candidates are measured on a fresh sample, exactly as the
listed tasks were, and must clear a **5% adoption bar**. Scoring runs in
sequential waves of 25, 60 and 100 papers: after each wave a Beta–Binomial
posterior gives the probability that the final share lands above the bar, and
scoring stops once that probability is outside 2–98% and the standard error is
small enough. Most candidates settle at 25 papers.

**7. Raise.** A task proposed across many subfields of a field, or many fields of
a domain, is filed once at that higher level instead of repeatedly below it.

That run measured 5,405 candidate tasks, of which 4,642 cleared the 5% bar and
359 were withheld as already covered by an existing field- or domain-level task.
It added 2,297 tasks: 1,905 at subfield level, 327 at field level, 65 at domain
level, each counted once at the highest level it qualifies for.

---

## 5. Data Enrichment

Beyond the task statements themselves, SciNet enriches each field and subfield with additional data that characterize research communities and the scientific landscape more broadly. This enrichment falls into three categories: task-level ratings following [O\*NET](https://www.onetonline.org/) methodology, bibliometric characteristics drawn from [OpenAlex](https://openalex.org/), and measures of AI adoption across fields.

### 5.1 Task ratings (Importance, Relevance, Frequency)

Following [O\*NET](https://www.onetonline.org/) methodology, each task is rated on three scales to indicate how central it is to a research area:

- **Importance (IM, 1–5):** How important is this task to researchers in this area?
- **Relevance (RT, 0–100%):** What share of researchers in this area perform this task?
- **Frequency (FT, 1–7):** How often is this task performed? (1 = yearly or less, 7 = hourly or more)

We replicate the [O\*NET](https://www.onetonline.org/) incumbent worker survey by prompting a language model to adopt the perspective of a researcher with 10+ years of experience in the target area and to rate all tasks simultaneously in a single API call. This batched approach provides consistency within a rating session.

The prompt includes explicit distribution anchors calibrated against [O\*NET](https://www.onetonline.org/) ground truth for scientific occupations — for example, for Relevance: "100 should be your most common answer — use it for ~30% of tasks"; for Importance: "Most tasks should be rated 3–4; only a small minority receive 5." These anchors correct for a systematic tendency in LLMs to underestimate the share of researchers who perform common tasks and to overrate task importance. The calibrated prompt was validated against 425 researcher-relevant [O\*NET](https://www.onetonline.org/) tasks across 40 scientific occupations. The released ratings were produced with Claude Opus 5, which scores r = 0.66 (Importance), r = 0.63 (Relevance), and r = 0.75 (Frequency) on that benchmark; the earlier Opus 4.5 pass scored r = 0.60 / 0.63 / 0.76. Correlations are near-identical, but the *level* changed: Opus 4.5 under-reported Relevance by 5.9 percentage points against O\*NET, while Opus 5 is within 0.9 points.

Based on these ratings, tasks are classified as **Core** (Relevance ≥ 67% and Importance ≥ 3.0) or **Supplemental**, following [O\*NET](https://www.onetonline.org/)'s conventional rule. Earlier releases lowered the Relevance threshold to 50% to offset the downward bias in the Opus 4.5 ratings; that bias is gone, so the compensation was removed.

### 5.2 Bibliometric characteristics from OpenAlex

For each SciNet field and subfield, we compute a set of bibliometric indicators from [OpenAlex](https://openalex.org/) that describe the research community's publication activity and output quality:

- **Publication volume.** Total paper count and citation count per field and subfield, aggregated from topic-level data.
- **AI-mention trends.** Yearly counts of papers that mention AI-related terms (e.g., "artificial intelligence," "machine learning," "large language model") as a fraction of all papers in the field, tracking how rapidly AI is entering different research communities.
- **Publication delay.** Average number of days from journal submission to publication, where available, as a proxy for research pace and review intensity.

These indicators are computed at the subfield level by aggregating topic-level [OpenAlex](https://openalex.org/) data and are used to contextualize task profiles — for instance, a subfield with rapidly rising AI-mention rates may have a different distribution of AI-augmentable tasks than one where AI adoption is slow.

### 5.3 Verifiability and research quality indicators

We construct a verifiability index for each subfield, capturing the degree to which research outputs are presented in ways that facilitate independent replication and scrutiny. The index aggregates three component measures at the topic level, weighted by paper count:

- **Retraction rate.** The fraction of papers in the topic that have been retracted, as a signal of systematic quality failures.
- **Hedging language.** Frequency of hedging words per 100 words in abstracts (e.g., "may," "suggest," "appear"), reflecting epistemic caution in how findings are communicated.
- **Booster language.** Frequency of booster words per 100 words (e.g., "clearly," "demonstrate," "establish"), reflecting overstatement tendencies.

Each subfield receives a percentile rank on the composite index and on each component, enabling cross-field comparisons of research norms and output characteristics.

---

## 6. Models and Infrastructure

| Component | Model | Notes |
|-----------|-------|-------|
| Task generation | Claude Opus 4.5 | Hierarchical refinement, universal/domain researcher-supervised |
| Paper validation (judge, elicit, referee, score) | Claude Sonnet 5 | The 34-field production run |
| Task ratings | Claude Opus 5 | Importance / relevance / frequency, via the Batch API |
| Protocols.io routing and matching | Claude Sonnet 4.5 | Multi-phase routing and step-level coverage |
| Field/subfield classification | Claude Sonnet 4.5 | Taxonomy mapping |

All models are accessed via the Anthropic API. Topic-level task generation uses the [Anthropic Batch API](https://docs.anthropic.com/en/docs/build-with-claude/message-batches), which provides a 50% cost reduction and higher throughput. Prompt caching (ephemeral) is used for system prompts and shared context blocks. All long-running pipeline steps checkpoint results incrementally so that interrupted runs can resume without reprocessing completed items.

---

## 7. Ongoing and Future Work

The ground truth collection described in [Section 4](#4-ground-truth-data) is ongoing. Several components are in active development:

- **Expanded protocols.io coverage.** Step-level coverage and timing now run over the full corpus; further gap-driven task generation from the uncovered steps is ongoing.
- **Broader paper coverage.** Full-text processing is being extended to a larger sample of [OpenAlex](https://openalex.org/) and arXiv papers, with particular attention to computational, theoretical, and social science fields.
