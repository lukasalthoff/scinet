# SciNET Methodology

SciNET is an O\*NET for science: a comprehensive, hierarchically organized database of research task statements covering approximately 4,500 research topics from [OpenAlex](https://openalex.org/), with assessments of AI augmentation and automation exposure for each task. This document describes every step of the pipeline, from taxonomy construction through task generation, quality filtering, AI exposure scoring, and external validation.

---

## Table of Contents

1. [Background and Motivation](#1-background-and-motivation)
2. [Taxonomy: The OpenAlex Hierarchy](#2-taxonomy-the-openalex-hierarchy)
3. [O\*NET-Style Task Statements](#3-onet-style-task-statements)
4. [Task Hierarchy and Generation](#4-task-hierarchy-and-generation)
5. [Task Rating and Filtering](#5-task-rating-and-filtering)
6. [AI Exposure Scoring](#6-ai-exposure-scoring)
7. [Validation](#7-validation)
8. [Models and Infrastructure](#8-models-and-infrastructure)
9. [Limitations](#9-limitations)

---

## 1. Background and Motivation

**O\*NET** (the Occupational Information Network) is the U.S. government's primary database of occupational characteristics. For hundreds of occupations, O\*NET records detailed task statements collected through surveys of incumbent workers and rates each task on three scales: how important it is, what fraction of workers perform it, and how frequently it is performed.

Scientific research is largely absent from O\*NET at useful resolution. O\*NET has entries for broad categories like "Biological Scientists" or "Economists," but not for the granular topics — Gene Editing, Monetary Policy, Quantum Computing — where work actually differs. SciNET fills this gap by applying the O\*NET methodology at the level of OpenAlex research topics.

The primary outputs are:

- **~100,000+ task statements** organized across ~4,500 topics, ~250 subfields, and 26 fields
- **Augmentation scores** (0–100%): estimated time savings from generative AI assistance
- **Automation tiers** (T0–T4): classification of AI automation exposure
- **Skill requirements** on 35 O\*NET-standard skill dimensions

---

## 2. Taxonomy: The OpenAlex Hierarchy

### 2.1 Source: OpenAlex topics

The taxonomy follows [OpenAlex](https://openalex.org/), a free and open catalog of scholarly publications. OpenAlex classifies scholarly works into a four-level hierarchy:

| Level | Count | Example |
|-------|-------|---------|
| Domain | 5 | Physical Sciences |
| Field | 26 | Physics and Astronomy |
| Subfield | ~250 | Condensed Matter Physics |
| Topic | ~4,500 | Superconductivity and Magnetic Properties |

Each OpenAlex topic is accompanied by a short summary, a set of keywords, and (where available) a link to the corresponding Wikipedia article. These are included in [`data/openalex_topics.csv`](data/openalex_topics.csv) and serve as context in the task-generation prompts.

### 2.2 Display field mapping

OpenAlex's 26 fields do not always match natural research communities. For example, OpenAlex groups Economics, Sociology, and Psychology together as "Social Sciences." SciNET remaps these to approximately 30 **display fields** that more closely track disciplinary boundaries.

The mapping uses a two-pass approach:

1. **Rule-based assignment.** Most subfields can be deterministically mapped (e.g., "Cardiology" → Medicine). Subfields that do not map unambiguously are flagged.
2. **LLM-based classification.** For ambiguous cases, a language model classifies the topic into one of the 30 display fields given the topic's name, keywords, and summary. Batches of up to 15 topics are processed per API call; outputs take the form `A:11, B:24, ...` for efficiency.

The 30 display fields include, for example: Agricultural Sciences, Anthropology, Arts, Biology, Biomedical Sciences, Business & Management, Chemistry, Computer Science, Economics, Education, Engineering, Environmental Science, Geography, History, Law, Mathematics, Medicine & Clinical Sciences, Neuroscience, Philosophy, Physics & Astronomy, Political Science, Psychology, and Sociology.

Similarly, topics are assigned to **display subfields** within their display field via a second round of batched LLM classification.

---

## 3. O\*NET-Style Task Statements

### 3.1 Task statement structure

All tasks follow the O\*NET canonical structure:

```
[Action Verb] + [Object] + [Modifiers] + [Purpose]
```

**Writing rules:**

- Begin with a present-tense action verb (e.g., *Analyze*, *Design*, *Develop*, *Estimate*, *Collect*)
- Include the object being acted on
- Add optional modifiers specifying how or under what conditions
- End with an optional purpose introduced by "to …"
- One core action per statement; avoid chained steps
- Approximately 8–18 words
- Plain language; avoid jargon unless necessary for precision
- Parallel structure across statements; mutual exclusivity encouraged

**Reference examples from O\*NET:**

> "Analyze data from research conducted to detect and measure physical phenomena."

> "Plan, design, or conduct surveys using questionnaires, focus groups, or interviews."

> "Compile, analyze, and report data to explain economic phenomena and forecast trends."

### 3.2 Scope heuristics

Tasks are written at the level of a *research team*, not a single individual, using the collaborative voice. Statements describe what a typical researcher in the field *does*, not what they might occasionally do. See [Section 4.3](#43-coverage-thresholds) for the quantitative coverage thresholds enforced at each level.

---

## 4. Task Hierarchy and Generation

SciNET uses a **top-down hierarchical generation** approach: tasks at each level are generated in the context of all tasks already defined at parent levels, ensuring that child-level tasks are genuine refinements (not repetitions) of their parents.

### 4.1 Level structure

| Level | Scope | Source | Coverage threshold |
|-------|-------|--------|--------------------|
| L1 — Universal | All researchers | Manually curated | — |
| L2 — Domain | e.g., Life Sciences | Manually curated | — |
| L3 — Subfield | e.g., Economics | LLM-generated | ≥ 70% of subfield researchers |
| L4 — Topic | e.g., Labor Market and Education | LLM-generated | ≥ 80% of topic researchers |

The data files in this repository (`generated_tasks.csv`, `task_augmentation.csv`, `task_automation.csv`) were produced by a **three-level variant** of this pipeline (field → subfield → topic) described in [Section 4.4](#44-three-level-pipeline-released-data). The four-level architecture is described here first because it provides the clearest conceptual picture.

### 4.2 Manually curated levels (L1 and L2)

**L1 — Universal tasks (25 tasks)**

These tasks apply to virtually all researchers regardless of field and serve as the shared backbone of the SciNET hierarchy. They are organized into seven categories:

| Category | Tasks (count) | Examples |
|----------|---------------|---------|
| Ideation & Hypothesis Generation | 5 | "Identify gaps in existing literature to formulate novel research questions." |
| Data Gathering | 4 | "Design data collection protocols and instruments to ensure validity and reproducibility." |
| Data Analysis | 4 | "Apply statistical methods to test hypotheses and estimate effect sizes." |
| Writing & Communication | 4 | "Draft manuscripts describing research questions, methods, results, and interpretations." |
| Peer Review & Service | 2 | "Evaluate manuscripts submitted to journals for scientific rigor and contribution." |
| Mentorship & Teaching | 3 | "Supervise graduate students and postdoctoral researchers on research projects." |
| Administration & Collaboration | 3 | "Manage research budgets, personnel, and project timelines." |

**L2 — Domain tasks (11–12 tasks per domain)**

L2 tasks are domain-specific refinements of L1 tasks. Each L2 task carries an explicit `l1_task_id` link to the L1 task it refines. Four research domains are covered:

| Domain | Tasks (count) | Example |
|--------|---------------|---------|
| Social Sciences | 12 | "Design surveys or questionnaires to measure attitudes, behaviors, or experiences." |
| Life Sciences | 12 | "Follow biosafety protocols when handling biological materials." |
| Physical Sciences | 12 | "Quantify measurement uncertainty and propagate errors through calculations." |
| Health Sciences | 11 | "Ensure compliance with patient privacy regulations (e.g., HIPAA)." |

The L2 tasks capture practices that are characteristic of an entire research domain but would not apply across all domains — for example, IRB approval workflows in the Social Sciences and Health Sciences, or instrument calibration procedures in the Physical Sciences.

### 4.3 LLM-generated levels (L3 and L4)

L3 and L4 tasks are generated by a language model given:

1. The full list of parent tasks (L2 for generating L3; L3 for generating L4), each labelled with its parent-level ID
2. The names of topics that fall within the target subfield or topic (as contextual grounding)
3. A detailed prompt specifying writing style, scope, and coverage requirements

**L3 subfield prompt (excerpt):**

> You are generating task statements for researchers in {subfield\_name} (a subfield of {domain\_name}).
>
> INPUT: L2 DOMAIN TASKS ({domain\_name})
> These are the domain-level tasks. Your job is to generate subfield-specific refinements of these.
>
> OBJECTIVE: Generate subfield-specific refinements of the L2 tasks above. Each L3 task you generate should:
> - Refine ONE specific L2 task (specify which L2 task number it refines)
> - Be specific to {subfield\_name} (would NOT apply to other subfields)
> - Be common enough that **70%+ of {subfield\_name} researchers** do it regularly

**L4 topic prompt (excerpt):**

> OBJECTIVE: Generate topic-specific refinements of the L3 tasks above. Each L4 task you generate should:
> - Refine ONE specific L3 task (specify which L3 task number it refines)
> - Be specific to {topic\_name} (would NOT apply to other topics in {subfield\_name})
> - Be common enough that **80%+ of {topic\_name} researchers** do it regularly

Each generated task includes an explicit `l2_task_id` (for L3) or `l3_task_id` (for L4), enabling full parent-chain tracing from any L4 task up to the relevant L1 universal task.

### 4.4 Coverage thresholds

The coverage thresholds (70% at L3, 80% at L4) serve a dual purpose. They push the model toward tasks that represent common, substantial research activities — analogous to O\*NET's concept of "relevance" — and they push against overly specific tasks (e.g., a particular niche dataset or one-off technique) that would inflate the task count without adding representational value. The tighter threshold at L4 reflects that topic-level tasks should be highly characteristic of the specific research area.

### 4.5 Three-level pipeline (released data)

The CSV files in this repository were produced by a simplified **three-level pipeline** (field → subfield → topic) in which all three levels are LLM-generated:

- **Field level** (10–30 tasks): tasks common to all researchers across the field; subject to a "50%+ of researchers" heuristic; must not be subfield-specific
- **Subfield level** (10–30 tasks): tasks *additional* to field-level tasks that are distinctive of the subfield; prompt explicitly passes the field tasks and instructs the model not to paraphrase them
- **Topic level** (10–30 tasks): tasks *additional* to both field- and subfield-level tasks that are distinctive of the specific topic; prompt passes both parent levels

The key design principle — that each child level generates *new* tasks rather than repeating or rephrasing parent tasks — is preserved. The `level` column in `generated_tasks.csv` records which level each task was generated at.

**Execution:** Subfield tasks are generated in parallel using a thread pool. Topic tasks are generated via the [Anthropic Batch API](https://docs.anthropic.com/en/docs/build-with-claude/message-batches), which processes hundreds of topics concurrently.

### 4.6 Deduplication and quality control

- **Prompt-level:** The model is instructed to ensure mutual exclusivity across tasks and to avoid vague catch-all statements ("analyze data," "collect data"). Parent tasks are provided in the prompt explicitly so the model can avoid paraphrasing them.
- **Code-level:** After parsing model responses, a normalization function deduplicates tasks by exact string match after whitespace normalization.
- **Error handling:** If a model response cannot be parsed as valid JSON, a regex fallback extracts the task list from code blocks or raw text. Unparseable responses are logged as errors without discarding the run. All generation is checkpointed so interrupted runs can resume.

---

## 5. Task Rating and Filtering

To determine which tasks are "core" to a research area (performed by most researchers) versus "supplemental" (performed by a minority), SciNET replicates O\*NET's worker survey methodology using language models as simulated respondents.

### 5.1 O\*NET survey scales

O\*NET collects three ratings for each task from incumbent workers:

| Scale | Abbreviation | Range | Question |
|-------|-------------|-------|---------|
| Importance | IM | 1–5 | "How important is this task to your job?" |
| Relevance (% workers) | RT | 0–100% | "What percentage of workers in this occupation perform this task?" |
| Frequency | FT | 1–7 | "How often is this task performed?" (1=yearly or less, 7=hourly or more) |

### 5.2 SciNET adaptation

SciNET replicates the O\*NET survey by prompting a language model to play the role of a researcher with 10+ years of experience in the target occupation and to rate all tasks for that occupation simultaneously. The batched design — rating all tasks in a single API call — provides consistency within a rating session and is approximately 6× more efficient than rating tasks individually.

The prompt includes calibrated distribution guidance to prevent scale compression, for example:

> "PERCENT OF WORKERS (RT): … CRITICAL: 100 should be your most common answer — use it for ~30% of tasks. Expected distribution: ~30% = 100, ~55% = 90–99, ~15% = below 90."

### 5.3 Core vs. Supplemental classification

| Category | Criteria |
|----------|---------|
| **Core** | RT ≥ 50% AND IM ≥ 3.0 ("Important") |
| **Supplemental** | Does not meet both Core thresholds |

The RT threshold of 50% is set below O\*NET's conventional 67% to account for a systematic downward bias in LLM relevance estimates (see [Section 7.1](#71-onet-calibration)). The IM threshold of 3.0 matches O\*NET practice. Frequency (FT) is recorded but not used for filtering.

---

## 6. AI Exposure Scoring

Each task in `generated_tasks.csv` is independently scored on two AI exposure dimensions.

### 6.1 Augmentation score (0–100%)

The augmentation score estimates the share of time a researcher can save on a task by using generative AI as an assistant — that is, with a human still in the loop directing the work.

**Prompt approach:** The model receives a description of the field and the task statement and is asked:

> "Estimate the percentage of time that the researcher can save by using the described Generative AI to assist with the task."

The model is instructed to return a single number between 0 and 100. No explanatory text is requested, which reduces verbosity and eases parsing.

**Scale interpretation:** A score of 35 means the model estimates that 35% of the time typically spent on this task could be saved with AI assistance. A score of 0 means no time savings; 100 means the task could be completed in near-zero time.

This measure is adapted from the augmentation framework developed in Althoff & Reichardt (2025).

### 6.2 Automation tier (T0–T4)

The automation tier classifies whether, and to what degree, generative AI could perform the *entire* task autonomously — without ongoing human direction. The rubric follows Eloundou et al. (2023) extended to the scientific domain:

| Tier | Definition |
|------|-----------|
| **T0** | No automation exposure. GenAI cannot perform any aspect of the task in any meaningful manner (e.g., physical laboratory manipulations). |
| **T1** | Low exposure. GenAI can perform 0–50% of task components at high quality. |
| **T2** | Moderate exposure. GenAI can perform 50–90% of task components at high quality. |
| **T3** | High exposure. GenAI can perform 90–100% of components, but human oversight is required before the output is used. |
| **T4** | Full exposure. GenAI can complete the task with high quality; no oversight is normally needed. |

**Prompt approach:** The model first checks whether the task meets the T0 criterion (physical/non-digital actions that GenAI cannot assist with at all). If not, it classifies among T1–T4. Six worked annotation examples spanning different fields and tiers are included in the prompt to anchor the rubric. The model provides both the tier label and a written rationale; both are included in `task_automation.csv`.

### 6.3 Skill requirements (1–7)

For each task, a language model rates the required level on each of 35 O\*NET standard skills (e.g., Reading Comprehension, Critical Thinking, Programming, Science). Skill anchors at levels 2, 4, and 6 are drawn directly from O\*NET documentation to ensure scale alignment. Each (task, skill) pair is rated independently; the model returns a single integer on the 1–7 scale.

---

## 7. Validation

### 7.1 O\*NET calibration

To assess how well LLM task ratings match human incumbent survey responses, we conducted a calibration exercise against O\*NET ground truth.

**Sample construction:**

1. All occupations in the O\*NET Task Ratings database with keywords indicating scientific research (e.g., "scientist," "researcher," "biologist," "economist") were selected — yielding 40 scientific occupations.
2. Each O\*NET task for these occupations was classified by a language model on a 1–5 researcher-relevance scale. Tasks scoring ≥ 4 were retained, yielding 425 researcher-relevant tasks with known O\*NET IM, RT, and FT ground truth.
3. The SciNET batched rating prompt was applied to the same tasks and occupations.

**Results (Claude Opus 4.5, n = 425 tasks, 40 occupations):**

| Scale | Pearson r | 95% CI | LLM mean | O\*NET mean | Bias |
|-------|-----------|--------|----------|-------------|------|
| Importance (IM) | 0.60 | [0.535, 0.657] | 3.68 | 3.83 | −0.15 |
| % Workers (RT) | 0.63 | [0.566, 0.682] | 80.0 | 86.0 | −5.93 |
| Frequency (FT) | 0.76 | [0.719, 0.799] | 3.23 | 3.29 | −0.06 |

The correlations are modest-to-strong, with the weakest performance on Importance and the strongest on Frequency. The small downward bias on % Workers (−5.9 percentage points) motivated the use of a 50% rather than 67% RT threshold for Core task classification. The prompt calibration includes distribution guidance (e.g., expected fractions of tasks at each RT level) derived from this exercise.

### 7.2 Protocols.io step coverage

Protocols.io is a platform where researchers publish detailed laboratory and research protocols, including step-by-step procedure lists. These protocols provide a ground-truth record of what researchers actually do in practice — independent of any LLM. We use protocol steps to evaluate whether SciNET's task database covers real-world research activities.

**Data collection:**

A corpus of approximately 20,600 protocols was assembled from three sources:
- Public protocols available via the protocols.io search API
- Unlisted protocols with DOIs indexed in OpenAlex
- Additional protocols identified through CrossRef under the protocols.io DOI prefix (10.17504)

For each protocol, procedure steps, title, abstract, authors, and metadata were collected. Protocols were linked to OpenAlex publications where DOIs overlapped, enabling topic-level assignment.

**Assignment pipeline:**

Each protocol is routed to the SciNET topic it best represents through a four-phase LLM-assisted pipeline:

1. **Field validation (Phase 1.5).** A language model checks whether the OpenAlex-assigned field is correct given the protocol title, abstract, and first three steps. If not, it suggests the correct field.
2. **Subfield validation (Phase 2).** The same approach validates subfield assignment within the confirmed field.
3. **Topic assignment (Phase 3).** The model selects the best-matching SciNET topic from a list of candidates within the subfield, and provides a confidence score from 1–5. Only protocols with confidence ≥ 4 are used in downstream analysis.
4. **Step coverage (Phase 4).** For each procedure step, the model determines whether it is covered by any existing SciNET task at the field, subfield, or topic level. Steps are classified as: *placeholder* (instructions to follow a prior protocol, excluded from coverage calculations), *prep* (routine preparatory actions such as centrifugation or sample labeling), or *substantive* (steps that correspond to meaningful research tasks). Coverage is measured as the fraction of non-placeholder steps matched to a SciNET task.

**Results:** With correct field routing, LLM-assessed step coverage exceeds 95% for most protocols, indicating that SciNET's task database captures the vast majority of substantive research activities described in real protocols. Field misclassification — a common source of OpenAlex metadata error, affecting roughly 70% of protocols in pilot validation — is the primary driver of apparent coverage gaps.

**Missing task augmentation:**

Uncovered steps are not discarded. Instead, they are grouped by (field, subfield, topic), and a language model proposes new O\*NET-style task statements to cover them. Proposed tasks are then deduplicated against existing SciNET tasks using sequence similarity matching (threshold: 90% character overlap) before any additions are made.

### 7.3 Bio-protocol scraping

A second external validation source is [Bio-Protocol](https://bio-protocol.org/), a peer-reviewed journal that publishes detailed experimental protocols primarily in the life sciences. A corpus of approximately 85,000 protocols was scraped (with a 3-second crawl delay per robots.txt). Each protocol includes title, abstract, procedure steps with durations, materials list, and author affiliations. This corpus provides complementary coverage in domains — particularly molecular biology — that are well-represented in Bio-Protocol but less so in protocols.io.

---

## 8. Models and Infrastructure

| Component | Model | Notes |
|-----------|-------|-------|
| Task generation (3-level) | Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) | Field, subfield, and topic tasks |
| Task generation (4-level) | Claude Opus 4.5 (`claude-opus-4-5-20251101`) | L3/L4 tasks; higher model for quality |
| Augmentation scoring | Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) | Single-number output; high throughput |
| Automation scoring | Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) | T0–T4 classification with rationale |
| Skill requirements | Claude Haiku 4.5 (`claude-haiku-4-5-20251001`) | 35 skills × ~100k tasks |
| O\*NET calibration | Claude Opus 4.5 (`claude-opus-4-5-20251101`) | Gold-standard comparison |
| Protocols.io validation | Claude Sonnet 4.5 (`claude-sonnet-4-5-20250929`) | Multi-phase routing and coverage |
| Field/subfield classification | Claude Sonnet 4.5 (`claude-sonnet-4-20250514`) | Taxonomy mapping |

All models are accessed via the Anthropic API. Topic-level task generation and AI exposure scoring use the [Anthropic Batch API](https://docs.anthropic.com/en/docs/build-with-claude/message-batches), which provides a 50% cost reduction and higher throughput. Prompt caching (ephemeral) is used for system prompts and shared context blocks. All long-running pipeline steps checkpoint results incrementally so that interrupted runs can resume without reprocessing completed items.

---

## 9. Limitations

**LLM as simulated respondent.** The coverage thresholds (70%, 80%) and the Core/Supplemental classification rely on LLM judgments, not surveys of actual researchers. While correlations with O\*NET human surveys are meaningful (r = 0.60–0.76), the LLM is not a perfect proxy for incumbent workers. The calibration exercise used scientific occupations from O\*NET, but these are broader than SciNET's specific topics.

**Coverage threshold reliability.** The RT scale exhibits the largest calibration gap (r = 0.63, bias −5.9 pp). The 50% Core threshold was chosen to approximately match O\*NET's effective pass rate, but this adjustment is approximate. Tasks near the threshold boundary should be interpreted with caution.

**English-language bias.** Task statements are generated in English using English-language topic labels and keywords. Research practices may differ across linguistic or cultural contexts not well-represented in either O\*NET or the underlying LLMs' training data.

**OpenAlex taxonomy drift.** OpenAlex periodically revises its topic labels and assignments. The `old_topic_label` and `new_topic_label` columns in `openalex_topics.csv` reflect a specific label revision; downstream uses should verify topic IDs rather than relying solely on label strings.

**Protocol coverage bias.** The protocols.io and Bio-Protocol validation corpora skew toward experimental life sciences and biomedicine. Coverage validation for computational, social science, and humanities research topics is more limited.

---

## References

- Althoff, L., & Reichardt, C. (2025). *Generative AI and Labor Market Impacts.*
- Arts, S., Cassiman, B., & Gomez, J. C. (2025). *Beyond Citations: Measuring Novel Scientific Ideas.*
- Eloundou, T., Manning, S., Mishkin, P., & Rock, D. (2023). GPTs are GPTs: An Early Look at the Labor Market Impact Potential of Large Language Models. *Science*, 384(6702), 1306–1312.
- Liang, W., et al. (2024). Mapping the Increasing Use of LLMs in Scientific Papers. *arXiv:2404.01268.*
- Peterson, N. G., Mumford, M. D., Borman, W. C., Jeanneret, P. R., & Fleishman, E. A. (2001). Understanding Work Using the Occupational Information Network (O\*NET). *Personnel Psychology*, 54(2), 451–492.
- Waltman, L., & van Eck, N. J. (2012). A new methodology for constructing a publication-output indicator. *Journal of the American Society for Information Science and Technology*, 63(12), 2378–2392.
