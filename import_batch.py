#!/usr/bin/env python3
"""
Imports a JSON batch of questions into data/questions.json after validating each entry
against the TOPICS taxonomy and the required schema.

Usage:
    python3 import_batch.py path/to/batch.json

Batch file is a JSON array of objects with at minimum:
    topic, subtopic, question, options {A, B, C, D}, correct_answer, explanation
Optional: objective (defaults to subtopic), source (defaults to "ai").
"""

import json
import sys
from pathlib import Path

from utils.questions import TOPICS, add_questions_bulk

REQUIRED_FIELDS = ("topic", "subtopic", "question", "options", "correct_answer", "explanation")
REQUIRED_OPTION_KEYS = {"A", "B", "C", "D"}


def validate(q: dict, idx: int) -> list[str]:
    errors = []

    for field in REQUIRED_FIELDS:
        if field not in q or q[field] in (None, "", {}):
            errors.append(f"missing required field '{field}'")

    if errors:
        return errors  # bail early; downstream checks would just NPE

    if q["topic"] not in TOPICS:
        errors.append(f"unknown topic '{q['topic']}' (must be one of: {list(TOPICS.keys())})")
        return errors

    if q["subtopic"] not in TOPICS[q["topic"]]:
        errors.append(
            f"unknown subtopic '{q['subtopic']}' for topic '{q['topic']}' "
            f"(must be one of: {TOPICS[q['topic']]})"
        )

    if not isinstance(q["options"], dict) or set(q["options"].keys()) != REQUIRED_OPTION_KEYS:
        errors.append(f"options must be a dict with exactly keys A, B, C, D — got {list(q['options'].keys()) if isinstance(q['options'], dict) else type(q['options']).__name__}")
    else:
        for key, val in q["options"].items():
            if not isinstance(val, str) or not val.strip():
                errors.append(f"option {key} is empty or not a string")

    if q["correct_answer"] not in REQUIRED_OPTION_KEYS:
        errors.append(f"correct_answer must be one of A, B, C, D — got '{q['correct_answer']}'")

    return errors


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"ERROR: file not found: {path}")
        return 1

    with open(path, encoding="utf-8") as f:
        batch = json.load(f)

    if not isinstance(batch, list):
        print("ERROR: top-level JSON must be an array of question objects")
        return 1

    all_errors: list[str] = []
    for i, q in enumerate(batch):
        errors = validate(q, i)
        for e in errors:
            all_errors.append(f"  [{i}] {e}")

    if all_errors:
        print(f"Validation failed for {path}:")
        print("\n".join(all_errors))
        return 1

    for q in batch:
        q.setdefault("objective", q["subtopic"])
        q.setdefault("source", "ai")

    count = add_questions_bulk(batch)
    print(f"Imported {count} questions from {path.name}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
