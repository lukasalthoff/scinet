# SciNet Release Data

Flat, self-contained CSV exports of the SciNet taxonomy and tasks.

## Files

| File | Description |
|------|-------------|
| `tasks.csv` | Every task in the hierarchy. Columns: `task`, `category`, `level`, `domain`, `field`, `subfield`. Level is one of "universal" (applies to all researchers), "domain" (e.g. Social Sciences), or "subfield" (e.g. Labor Economics). Higher-level columns are empty when a task belongs to a broader level. |
| `openalex_topic_subfield_mapping.csv` | Maps each OpenAlex topic to its display domain, field, and subfield. Columns: `topic_id`, `topic_name`, `domain`, `field`, `subfield`. |
