import json
import uuid
from datetime import date
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "questions.json"

TOPICS = {
    "Databricks Intelligence Platform": [
        "Core components and architecture",
        "Delta Lake",
        "Unity Catalog",
        "Compute services",
    ],
    "Data Ingestion and Loading": [
        "Batch, streaming, incremental loading",
        "COPY INTO command",
        "Auto Loader",
        "Lakeflow Connect",
        "JDBC/ODBC ingestion",
        "Ingestion method selection",
        "Semi-structured data",
    ],
    "Data Transformation and Modeling": [
        "Data cleaning with PySpark/SQL",
        "DataFrame joins",
        "Column and row manipulation",
        "Deduplication and aggregation",
        "Spark tuning parameters",
        "Gold layer objects",
        "Data quality checks",
    ],
    "Working with Lakeflow Jobs": [
        "Control flows",
        "Task configuration and dependencies",
        "Job schedules and trigger types",
        "Time-based vs data-driven triggers",
    ],
    "Implementing CI/CD": [
        "Databricks Repos and Git integration",
        "Automation Bundle (DABs)",
        "Databricks CLI",
    ],
    "Troubleshooting, Monitoring, and Optimization": [
        "Job performance monitoring",
        "Lakeflow Jobs UI",
        "Spark UI bottlenecks",
        "Liquid Clustering and predictive optimization",
        "Cluster startup failures",
    ],
    "Governance and Security": [
        "Managed vs external tables",
        "Access controls (GRANT, REVOKE, DENY)",
        "Column-level masking and row-level security",
        "ABAC policies",
    ],
}


def load_questions() -> list[dict]:
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_questions(questions: list[dict]) -> None:
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2, ensure_ascii=False)


def add_question(q: dict) -> str:
    questions = load_questions()
    q["id"] = str(uuid.uuid4())
    q["created_at"] = str(date.today())
    questions.append(q)
    save_questions(questions)
    return q["id"]


def add_questions_bulk(new_qs: list[dict]) -> int:
    questions = load_questions()
    for q in new_qs:
        q["id"] = str(uuid.uuid4())
        q["created_at"] = str(date.today())
        questions.append(q)
    save_questions(questions)
    return len(new_qs)


def delete_question(question_id: str) -> None:
    questions = load_questions()
    save_questions([q for q in questions if q.get("id") != question_id])


def get_questions(topic: str | None = None) -> list[dict]:
    questions = load_questions()
    if topic and topic != "Alle Themen":
        return [q for q in questions if q.get("topic") == topic]
    return questions


def stats() -> dict:
    questions = load_questions()
    by_topic: dict[str, int] = {}
    for q in questions:
        t = q.get("topic", "Unbekannt")
        by_topic[t] = by_topic.get(t, 0) + 1
    return {"total": len(questions), "by_topic": by_topic}
