# Time use

[`data/task_hours_per_year.csv`](data/task_hours_per_year.csv) gives, for every task in every subfield where it is
performed, the hours a year a researcher spends on it: 25,271 rows, one per task and subfield. The slides
[`slides/time_use.pdf`](slides/time_use.pdf) walk through the measure with an example from Labor Economics.

## The measure

Tasks are of two types. **Paper tasks** are done to produce particular papers, such as collecting a dataset, running
the estimation or drafting the manuscript. **General tasks** are ongoing and not tied to particular papers, such as
teaching a course, supervising students or reviewing for journals.

```
paper tasks     hours per year = hours per instance x instances per paper x papers per year
general tasks   hours per year = hours per instance x instances per year
```

An instance is one unit of the task's work, such as one round of revisions or one student supervised for a year.

| Component | Formula | Source |
|---|---|---|
| hours per instance (paper tasks) | team hours one instance takes x share not counted under another task | team hours: [`task_time.csv`](data/task_time.csv), estimated by Claude Opus 4.8 from each task's substeps and validated against laboratory protocols from protocols.io (see [METHODOLOGY.md](METHODOLOGY.md)); share: Claude Opus 5.5 |
| instances per paper | share of papers that involve the task x instances per paper that involves it / papers per instance | share: [`task_prevalence.csv`](data/task_prevalence.csv), about 100 sampled papers per subfield judged by Claude Sonnet 5 (Sonnet 5.5 and Opus 5.5 for field, domain and universal tasks); the two counts: Claude Opus 5.5 |
| papers per year | papers a researcher publishes per year / authors per paper | OpenAlex journal articles published 2015–2019 in the subfield: the median number of papers per author-year and the mean number of authors per paper |
| hours per instance (general tasks) | hours the researcher spends per instance x share not counted under another task | hours: Claude Sonnet 5.5; share: Claude Opus 5.5 |
| instances per year | share of researchers who do the task x instances per year for each of them | share: [`task_ratings.csv`](data/task_ratings.csv) (Claude Opus 5); instances: Claude Sonnet 5.5 |

Claude Opus 5.5 assigns each task its type, reading the task with its steps and the other tasks of its subfield. Six
ongoing universal tasks (brainstorming, coordinating with collaborators, learning methods, managing budgets, observing
phenomena, presenting findings) are general in every field.

**Shared work.** Claude Opus 5.5 compares the tasks of each field and of each subfield and flags pairs whose steps
contain the same work. The shared work is counted once, under one task of the pair: that task keeps all its hours, and
the other loses the share of its hours that is the shared work. 41% of paper tasks lose some work this way; the median
one keeps 60% of its hours.

**Universal tasks** are answered once per field and apply in every subfield of the field. Their general numbers are
asked several times and the median answer is kept, with the unit stated for the nine that have one (one student
supervised for a year, one course, one manuscript reviewed).

**Caps.** A universal general task's hours per researcher who does it are capped at 2.5 times its median across
fields, and any other general task at 189 hours a year, the 99th percentile of those tasks. About 90 rows are capped
and flagged.

## Example: Labor Economics

*Respond to peer reviewer comments and revise manuscripts* (paper task): one round takes the team 121 hours, none of it
counted under another task; 72% of papers go through revision, with two rounds each; a labor economist publishes 2.0
papers a year with 2.04 authors per paper.

```
hours per instance  = 121 x 100%       = 121
instances per paper = 72% x 2 / 1      = 1.44
papers per year     = 2.0 / 2.04       = 0.98
hours per year      = 121 x 1.44 x 0.98 = 171
```

*Supervise graduate students and postdoctoral researchers* (general task): one student-year takes 60 hours; 89% of
labor economists supervise, three students each.

```
hours per instance = 60 x 100% = 60
instances per year = 89% x 3   = 2.7
hours per year     = 60 x 2.7  = 160
```

Summed over its tasks, Labor Economics comes to 2,121 hours a year. Across all subfields the median is 1,977 hours.

## Columns

| Column | Description |
|---|---|
| `domain`, `field`, `subfield`, `level`, `task` | The task and the subfield it is performed in (`level`: `subfield`, `field`, `domain` or `universal`) |
| `task_type` | `paper` or `general` |
| `hours_per_year` | Hours a year a researcher spends on the task |
| `hours_per_instance` | Component, both types |
| `instances_per_paper`, `papers_per_year` | Components, paper tasks |
| `instances_per_year` | Component, general tasks |
| `team_hours_per_instance` | Part of hours per instance, paper tasks |
| `own_hours_per_instance` | Part of hours per instance, general tasks |
| `share_not_counted_elsewhere` | Part of hours per instance, both types |
| `share_of_papers_involving_task`, `instances_per_involving_paper`, `papers_per_instance` | Parts of instances per paper |
| `papers_per_author_year`, `authors_per_paper` | Parts of papers per year |
| `share_of_researchers_doing_task`, `instances_per_year_each` | Parts of instances per year |
| `retimed` | The task's time in this subfield was estimated with an explicit definition of one instance |
| `capped` | Hours capped as described above |

Columns that do not apply to a row's type are empty. On every row, `hours_per_year` is the product of its components,
and a subfield's hours a year are the sum of its rows.

## Notes

- Apart from papers per author-year and authors per paper, every piece is a language model's judgment; the share of
  papers involving a task is judged on real papers, the rest on the task's description and steps.
- Papers per year describes the average publishing author, students included, while the general tasks describe
  researchers who also teach and supervise.
- Differences between fields partly reflect how the models answer for each field.
