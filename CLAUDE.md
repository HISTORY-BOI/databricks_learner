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
- `import_batch.py` — JSON batch importer with validation. **Use this for AI-generated questions.**
- `import_examtopics.py` — parses pages saved from a logged-in examtopics session in `examtopics_html/`. Accepts `.webarchive` (Safari, preferred — includes auth-fetched images as subresources) and `.html` (plain — image-containing questions skipped). Uses examtopics' stated "Correct Answer" (community vote distribution is JS-rendered and absent from saved DOM). Multi-answer letters are sorted alphabetically (`"BA"` → `"AB"`). Question/option images are extracted to `data/images/` and referenced by relative path. Duplicates: replaces existing entries unless their source is `community_old_exam` (those are protected). Use `--inspect` to debug selectors if parsing yields 0.
- `add_more_questions.py` — legacy hand-written-in-Python helper. Keep as fallback only.
- `import_questions.py` — one-time importer for `old_questions.md` community exports; `map_topic` is reused by `import_examtopics.py`.

## examtopics import workflow

1. Log in at examtopics.com, open each "view" page. The stated "Correct Answer" is always in the saved DOM; the community vote bars are NOT (JS-rendered) and would not be captured even with full scrolling.
2. Save each page into `examtopics_html/` (gitignored). **Verify file size > 0.** Two formats supported:
   - **`.webarchive` (Safari, preferred)**: `File → Save As… → Format: Web Archive`. Bundles HTML + all auth-fetched images into one file. Enables full import including image-based questions.
   - **`.html`**: `File → Save As… → Format: Page Source`. Smaller but image-based questions are skipped (CDN auth-gated).
3. `python3 import_examtopics.py --inspect` to verify the parser sees question cards. If 0 found, adjust the `*_SELECTORS` lists at the top of the script.
4. `python3 import_examtopics.py --dry-run` to preview counts.
5. `python3 import_examtopics.py` to write. Images land in `data/images/` (gitignored).

Skip categories reported per file: `no_question`, `no_options`, `no_answer`, `image_missing` (plain-HTML save of a question whose images we can't fetch).

## Question schema additions

Optional fields populated by the examtopics importer when images are available:
- `images`: list of relative paths (e.g. `["data/images/image106.png"]`) — rendered above the question text.
- `option_images`: dict like `{"A": "data/images/image106.png", ...}` — rendered next to / under each option.
- `correct_answer`: for multi-answer questions, a sorted concatenation of letters (e.g. `"AB"`). The quiz UI switches to checkboxes when `len(correct_answer) > 1`.
