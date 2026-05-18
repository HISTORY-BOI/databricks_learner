#!/usr/bin/env python3
"""Merge a {id: explanation} JSON file into data/questions.json.

Usage:
    python3 apply_explanations.py path/to/explanations.json [--dry-run]

The input file is a flat JSON object mapping question id -> explanation string.
Only questions whose current explanation starts with "Stated answer from examtopics:"
are overwritten by default, to avoid clobbering existing manual explanations.
Pass --force to overwrite regardless.
"""

import argparse
import json
import sys
from pathlib import Path

PLACEHOLDER_PREFIX = "Stated answer from examtopics:"
QUESTIONS_PATH = Path("data/questions.json")


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("explanations_file")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--force", action="store_true",
                   help="Overwrite even non-placeholder explanations")
    args = p.parse_args()

    explanations = json.loads(Path(args.explanations_file).read_text())
    questions = json.loads(QUESTIONS_PATH.read_text())
    by_id = {q["id"]: q for q in questions}

    updated = skipped_not_placeholder = missing = 0
    for qid, new_expl in explanations.items():
        if qid not in by_id:
            missing += 1
            print(f"  MISSING id: {qid}")
            continue
        q = by_id[qid]
        current = q.get("explanation", "")
        if not args.force and not current.startswith(PLACEHOLDER_PREFIX):
            skipped_not_placeholder += 1
            continue
        q["explanation"] = new_expl
        updated += 1

    print(f"\nUpdated: {updated}  |  Skipped (already had real explanation): "
          f"{skipped_not_placeholder}  |  Missing IDs: {missing}")

    if args.dry_run:
        print("(dry-run — questions.json not written)")
        return 0
    QUESTIONS_PATH.write_text(json.dumps(questions, indent=2, ensure_ascii=False))
    print(f"Wrote {len(questions)} questions to {QUESTIONS_PATH}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
