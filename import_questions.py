#!/usr/bin/env python3
"""
Parses old_questions.md and imports questions into data/questions.json.

Rules:
- Community vote wins over stated answer
- Skip if options are code/image only (## A. pattern)
- Skip if top community vote < 70% (ambiguous)
- Maps old topics to new exam topic structure
"""

import re
import json
import uuid
from datetime import date
from pathlib import Path

BASE_DIR = Path(__file__).parent
MD_FILE = BASE_DIR / "old_questions.md"
DATA_FILE = BASE_DIR / "data" / "questions.json"

COMMUNITY_THRESHOLD = 70


def _match(text: str, *keywords: str) -> bool:
    """True if any keyword matches as a whole word (case-insensitive)."""
    return any(re.search(r'\b' + re.escape(k) + r'\b', text) for k in keywords)


def map_topic(question_text: str) -> tuple[str, str]:
    t = question_text.lower()

    # --- Governance (most specific first) ---
    if _match(t, "grant", "revoke", "privilege", "ownership"):
        return "Governance and Security", "Access controls (GRANT, REVOKE, DENY)"
    if _match(t, "managed table", "external table"):
        return "Governance and Security", "Managed vs external tables"
    if _match(t, "unity catalog", "data explorer", "metastore"):
        return "Governance and Security", "Managed vs external tables"
    if _match(t, "owner of", "transfer ownership", "data explorer"):
        return "Governance and Security", "Managed vs external tables"

    # --- CI/CD (before generic "job"/"task" to avoid false matches) ---
    if _match(t, "databricks repos", "git repository", "git operation", "cloned from",
               "central git", "pull request", "sync.*repo"):
        return "Implementing CI/CD", "Databricks Repos and Git integration"

    # --- Ingestion ---
    if _match(t, "auto loader", "cloudfiles", "cloud files"):
        return "Data Ingestion and Loading", "Auto Loader"
    if _match(t, "copy into"):
        return "Data Ingestion and Loading", "COPY INTO command"
    if _match(t, "jdbc", "sqlite", "org.apache.spark.sql"):
        return "Data Ingestion and Loading", "JDBC/ODBC ingestion"

    # --- Streaming / DLT ---
    if _match(t, "structured streaming", "readstream", "writestream", "checkpoint"):
        return "Data Transformation and Modeling", "Gold layer objects"
    if _match(t, "delta live table", "live table", "streaming live", "constraint", "expect"):
        return "Data Transformation and Modeling", "Gold layer objects"

    # --- Medallion / Gold layer ---
    if _match(t, "bronze", "silver", "medallion", "multi-hop"):
        return "Data Transformation and Modeling", "Gold layer objects"
    if re.search(r'\bgold table', t) or _match(t, "hop from"):
        return "Data Transformation and Modeling", "Gold layer objects"

    # --- Joins ---
    if _match(t, "union", "intersect"):
        return "Data Transformation and Modeling", "DataFrame joins"
    if re.search(r'\bjoin\b', t):
        return "Data Transformation and Modeling", "DataFrame joins"

    # --- Aggregations ---
    if _match(t, "pivot", "aggregate", "count_if", "count_null", "null value", "approx_count"):
        return "Data Transformation and Modeling", "Deduplication and aggregation"

    # --- Column / UDF ---
    if _match(t, "udf", "user-defined", "higher-order", "array functions", "array function"):
        return "Data Transformation and Modeling", "Column and row manipulation"

    # --- DDL / DML / SQL transforms ---
    if _match(t, "merge into", "insert into", "delete from", "create table", "drop table"):
        return "Data Transformation and Modeling", "Data cleaning with PySpark/SQL"
    if _match(t, "spark.sql", "spark.table", "spark.read", "pyspark"):
        return "Data Transformation and Modeling", "Data cleaning with PySpark/SQL"
    if _match(t, "temporary view", "relational object"):
        return "Data Transformation and Modeling", "Gold layer objects"
    if _match(t, "tblproperties", "dbproperties", "describe database", "describe location"):
        return "Data Transformation and Modeling", "Data cleaning with PySpark/SQL"

    # --- Lakeflow Jobs / Orchestration ---
    if _match(t, "cron", "programmatically"):
        return "Working with Lakeflow Jobs", "Job schedules and trigger types"
    if _match(t, "sql endpoint", "sql warehouse", "dashboard", "alert", "webhook"):
        return "Troubleshooting, Monitoring, and Optimization", "Job performance monitoring"
    if _match(t, "cluster pool", "single-node", "startup time", "start up time"):
        return "Databricks Intelligence Platform", "Compute services"
    if _match(t, "job", "tasks", "schedule", "workflow", "dependency", "depends on", "runs tab"):
        return "Working with Lakeflow Jobs", "Task configuration and dependencies"

    # --- Platform / Delta Lake ---
    if _match(t, "optimize", "vacuum", "time travel", "z-order", "liquid cluster"):
        return "Databricks Intelligence Platform", "Delta Lake"
    if _match(t, "delta table", "parquet", "file format"):
        return "Databricks Intelligence Platform", "Delta Lake"
    if _match(t, "lakehouse", "data lake", "data warehouse", "siloed", "acid"):
        return "Databricks Intelligence Platform", "Core components and architecture"
    if _match(t, "control plane", "data plane", "web application"):
        return "Databricks Intelligence Platform", "Core components and architecture"
    if _match(t, "open source", "vendor lock", "open format"):
        return "Databricks Intelligence Platform", "Core components and architecture"
    if _match(t, "autoscale", "cluster size", "cluster type"):
        return "Databricks Intelligence Platform", "Compute services"

    return "Databricks Intelligence Platform", "Core components and architecture"


def parse_options(options_text: str) -> dict[str, str] | None:
    """Parse A. B. C. D. E. options from a code block. Returns None if can't parse."""
    lines = options_text.strip().splitlines()
    options: dict[str, str] = {}
    current_key = None

    for line in lines:
        m = re.match(r'^([A-E])\.\s*(.*)', line.strip())
        if m:
            current_key = m.group(1)
            options[current_key] = m.group(2).strip()
        elif current_key and line.strip():
            # Continuation line
            options[current_key] = options[current_key] + " " + line.strip()

    return options if len(options) >= 4 else None


def parse_community(community_text: str) -> tuple[str, int] | None:
    """Return (best_answer, pct) or None if can't parse."""
    votes = re.findall(r'([A-E])\s*\((\d+)%\)', community_text)
    if not votes:
        return None
    best = max(votes, key=lambda x: int(x[1]))
    return best[0], int(best[1])


def parse_questions(md_text: str) -> list[dict]:
    question_re = re.compile(r'Question #(\d+) Topic 1\s*\n', re.MULTILINE)
    matches = list(question_re.finditer(md_text))

    results = []
    skipped_code = 0
    skipped_ambiguous = 0
    skipped_parse = 0

    for i, m in enumerate(matches):
        num = m.group(1)
        content_start = m.end()
        content_end = matches[i + 1].start() if i + 1 < len(matches) else len(md_text)
        block = md_text[content_start:content_end]

        # Skip questions where options are code/image placeholders
        if re.search(r'^## [A-E]\.', block, re.MULTILINE):
            print(f"  Q{num}: SKIP — code-only options")
            skipped_code += 1
            continue

        # Extract all backtick code blocks
        code_blocks = re.findall(r'```\n(.*?)\n```', block, re.DOTALL)
        if len(code_blocks) < 2:
            print(f"  Q{num}: SKIP — missing code blocks ({len(code_blocks)} found)")
            skipped_parse += 1
            continue

        options_block = code_blocks[0]
        answer_block = code_blocks[-1]

        options = parse_options(options_block)
        if not options:
            print(f"  Q{num}: SKIP — couldn't parse options")
            skipped_parse += 1
            continue

        result = parse_community(answer_block)
        if not result:
            print(f"  Q{num}: SKIP — couldn't parse community vote")
            skipped_parse += 1
            continue

        community_answer, community_pct = result

        if community_pct < COMMUNITY_THRESHOLD:
            print(f"  Q{num}: SKIP — ambiguous ({community_pct}% agreement)")
            skipped_ambiguous += 1
            continue

        # Get question text (before first code block)
        first_tick = block.find("```")
        question_text = block[:first_tick].strip()
        question_text = re.sub(r'\n{3,}', '\n\n', question_text).strip()

        topic, subtopic = map_topic(question_text)

        stated_match = re.search(r'Correct Answer:\s*([A-E])', answer_block)
        stated = stated_match.group(1) if stated_match else "?"
        marker = " (overridden)" if stated != community_answer else ""
        print(f"  Q{num}: OK — answer={community_answer}{marker}, {community_pct}%, topic={topic[:30]}")

        results.append({
            "id": str(uuid.uuid4()),
            "topic": topic,
            "subtopic": subtopic,
            "objective": "",
            "question": question_text,
            "options": options,
            "correct_answer": community_answer,
            "explanation": f"Community consensus: {community_answer} ({community_pct}%). "
                           + (f"Note: stated answer was {stated}." if stated != community_answer else ""),
            "created_at": str(date.today()),
            "source": "community_old_exam",
        })

    print(f"\nSummary: {len(results)} imported, "
          f"{skipped_code} skipped (code-only), "
          f"{skipped_ambiguous} skipped (ambiguous), "
          f"{skipped_parse} skipped (parse error)")
    return results


def load_existing() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save(questions: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)


def main() -> None:
    if not MD_FILE.exists():
        print(f"ERROR: {MD_FILE} not found")
        return

    print(f"Parsing {MD_FILE}...\n")
    md_text = MD_FILE.read_text(encoding="utf-8")
    new_questions = parse_questions(md_text)

    if not new_questions:
        print("No questions parsed — nothing saved.")
        return

    existing = load_existing()
    # Remove any previously imported community questions so re-runs are idempotent
    existing = [q for q in existing if q.get("source") != "community_old_exam"]
    combined = existing + new_questions

    save(combined)
    print(f"\nSaved {len(new_questions)} new questions. Total in bank: {len(combined)}.")
    print(f"\nDu kannst jetzt '{MD_FILE.name}' löschen.")


if __name__ == "__main__":
    main()
