# Databricks Learner — Project Context for Claude

Streamlit app for **Databricks Certified Data Engineer Associate** (exam version effective 2026-05-04). Questions are stored in `data/questions.json`. UI is in German; questions are in English (matching the real exam).

## Adding questions — recommended flow

When the user asks for new questions ("add 5 questions on X", "more questions about Y"):

1. **Write the batch as a JSON file** at the repo root or a path the user specifies. Each entry must conform to the schema below.
2. **Run the importer**:
   ```bash
   python3 import_batch.py path/to/batch.json
   ```
   The importer validates against `TOPICS` and the schema, then calls `add_questions_bulk` (which assigns `id` + `created_at` and appends to `data/questions.json`).
3. **Delete the batch file** after a successful import unless the user wants to keep it for git history.

Do **not** hand-edit `data/questions.json` directly, and do not write a new Python script per batch. `add_more_questions.py` exists as a fallback only — prefer JSON + `import_batch.py`.

## Question schema

```json
{
  "topic": "<exact key from TOPICS>",
  "subtopic": "<exact subtopic from TOPICS[topic]>",
  "question": "Scenario-based prompt in English.",
  "options": {"A": "…", "B": "…", "C": "…", "D": "…"},
  "correct_answer": "A|B|C|D",
  "explanation": "Why the correct answer is right AND why each distractor is wrong.",
  "objective": "<optional; defaults to subtopic>",
  "source": "<optional; defaults to 'ai'>"
}
```

`id` and `created_at` are added by the importer — do not include them in batches.

## TOPICS taxonomy

Source of truth: `utils/questions.py` (`TOPICS` dict). Topic and subtopic strings in batches must match exactly.

- **Databricks Intelligence Platform** — Core components and architecture · Delta Lake · Unity Catalog · Compute services
- **Data Ingestion and Loading** — Batch, streaming, incremental loading · COPY INTO command · Auto Loader · Lakeflow Connect · JDBC/ODBC ingestion · Ingestion method selection · Semi-structured data
- **Data Transformation and Modeling** — Data cleaning with PySpark/SQL · DataFrame joins · Column and row manipulation · Deduplication and aggregation · Spark tuning parameters · Gold layer objects · Data quality checks
- **Working with Lakeflow Jobs** — Control flows · Task configuration and dependencies · Job schedules and trigger types · Time-based vs data-driven triggers
- **Implementing CI/CD** — Databricks Repos and Git integration · Automation Bundle (DABs) · Databricks CLI
- **Troubleshooting, Monitoring, and Optimization** — Job performance monitoring · Lakeflow Jobs UI · Spark UI bottlenecks · Liquid Clustering and predictive optimization · Cluster startup failures
- **Governance and Security** — Managed vs external tables · Access controls (GRANT, REVOKE, DENY) · Column-level masking and row-level security · ABAC policies

## Style guide (mirror of `pages/3_KI_Generator.py` SYSTEM_PROMPT)

- Exactly 4 options (A, B, C, D), one correct.
- All distractors must be plausible — no obvious throwaways.
- Prefer practical scenarios over pure recall.
- Explanation must justify the right answer **and** refute each wrong one.
- Questions in English (exam language), even though UI is German.

## Key files

- `data/questions.json` — question bank (appended via `add_questions_bulk`).
- `utils/questions.py` — `TOPICS`, CRUD helpers.
- `pages/3_KI_Generator.py` — in-app Claude generator + the canonical `SYSTEM_PROMPT`.
- `import_batch.py` — JSON batch importer with validation. **Use this.**
- `add_more_questions.py` — legacy hand-written-in-Python helper. Keep as fallback only.
- `import_questions.py` — one-time importer for `old_questions.md` community exports.
