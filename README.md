# Databricks Learner

A Streamlit-based study app for preparing for the **Databricks Certified Data Engineer Associate** exam (version effective May 4, 2026). Practice multiple-choice questions, add your own, and generate new ones with Claude.

> The app UI is in German; this README is in English.

## Features

- **Quiz mode** — Practice questions filtered by topic, with explanations after each answer.
- **Add questions manually** — Build out your own question bank through a form.
- **AI question generator** — Use Claude to generate exam-style multiple-choice questions for any topic / subtopic in the official taxonomy.

## Exam Topics Covered

Mirrors the official exam guide (post-May 4, 2026):

- Databricks Intelligence Platform
- Data Ingestion and Loading
- Data Transformation and Modeling
- Working with Lakeflow Jobs
- Implementing CI/CD
- Troubleshooting, Monitoring, and Optimization
- Governance and Security

## Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

The AI generator page needs an Anthropic API key. Either export it before launching:

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
```

…or paste it into the input field that appears on the AI generator page.

## Run

```bash
streamlit run app.py
```

Streamlit will open the app at `http://localhost:8501`.

## Project Structure

```
.
├── app.py                       # Streamlit entry point (home page)
├── pages/
│   ├── 1_Quiz.py                # Quiz mode
│   ├── 2_Fragen_Hinzufuegen.py  # Manual question entry
│   └── 3_KI_Generator.py        # Claude-powered question generator
├── utils/
│   └── questions.py             # Question CRUD + topic taxonomy (TOPICS)
├── data/
│   └── questions.json           # Question bank (JSON file, version-controlled)
├── import_questions.py          # One-time importer for legacy community Q&A
├── add_more_questions.py        # Helper script to bulk-add hand-written questions
└── requirements.txt
```

## Adding Questions

There are three ways to grow the question bank:

1. **AI generator** — Open the *KI-Generator* page in the app, pick a topic/subtopic, review the generated questions, and save the ones you like.
2. **Manual entry** — Use the *Fragen Hinzufügen* page in the app.
3. **JSON batch import (recommended for Claude-assisted authoring)** — Write a JSON array of questions (schema below) and run:
   ```bash
   python3 import_batch.py path/to/batch.json
   ```
   The importer validates every entry against the `TOPICS` taxonomy and schema before writing, so typos in topic/subtopic names are caught up front.
4. **Bulk Python script (legacy)** — Edit `add_more_questions.py` to append a list of hand-authored question dicts, then run:
   ```bash
   python3 add_more_questions.py
   ```

All paths write to `data/questions.json` via `utils.questions.add_questions_bulk`.

## Importing Legacy Questions

If you have an `old_questions.md` file with community-voted Q&A (e.g., exported from a question dump), run:

```bash
python3 import_questions.py
```

Rules:
- Community vote overrides the stated answer.
- Questions with less than 70% community consensus are skipped.
- Questions whose options are code/image blocks are skipped.
- Re-runs are idempotent (previously imported community questions are replaced).

## Question Schema

Each entry in `data/questions.json` looks like:

```json
{
  "id": "uuid",
  "topic": "Implementing CI/CD",
  "subtopic": "Automation Bundle (DABs)",
  "objective": "Automation Bundle (DABs)",
  "question": "…",
  "options": {"A": "…", "B": "…", "C": "…", "D": "…"},
  "correct_answer": "B",
  "explanation": "…",
  "created_at": "2026-05-11",
  "source": "ai | manual | community_old_exam"
}
```
