#!/usr/bin/env python3
"""Export data/questions.json to an Anki-importable TSV file.

Output: anki_export.tsv at the repo root.

Format:
    #separator:tab
    #html:true
    #columns:Front<TAB>Back<TAB>Tags

Each row:
    Front  = question text + A/B/C/D options (HTML, <br> for line breaks,
             <img> for question/option images)
    Back   = "Answer: X" (bold) + explanation
    Tags   = topic::<topic> subtopic::<subtopic> source::<source>
             (spaces in names replaced with underscores; Anki uses
             space-separated tags with '::' for hierarchy)

Images: paths like "data/images/foo.png" are emitted as <img src="foo.png">.
To render them in Anki, copy data/images/* into your
~/Library/Application Support/Anki2/<profile>/collection.media/ folder.
"""

import html
import json
import re
from pathlib import Path

QUESTIONS_PATH = Path("data/questions.json")
OUTPUT_PATH = Path("anki_export.tsv")


def image_filename(path: str) -> str:
    """data/images/foo.png -> foo.png"""
    return path.rsplit("/", 1)[-1]


def to_html(text: str) -> str:
    """Escape, then convert newlines to <br>. Tabs to spaces (TSV-safe)."""
    escaped = html.escape(text).replace("\t", "    ")
    return escaped.replace("\n", "<br>")


def build_front(q: dict) -> str:
    parts: list[str] = []

    for img_path in q.get("images", []):
        parts.append(f'<img src="{image_filename(img_path)}">')

    parts.append(to_html(q["question"]))
    parts.append("")  # blank line before options

    option_images = q.get("option_images", {}) or {}
    for letter in sorted(q["options"].keys()):
        opt_text = q["options"][letter]
        line = f"<b>{letter}.</b> {to_html(opt_text)}" if opt_text else f"<b>{letter}.</b>"
        if letter in option_images:
            line += f' <img src="{image_filename(option_images[letter])}">'
        parts.append(line)

    return "<br>".join(parts)


def build_back(q: dict) -> str:
    correct = q.get("correct_answer", "?")
    explanation = to_html(q.get("explanation", ""))
    return f"<b>Answer: {correct}</b><br><br>{explanation}"


def tag_value(s: str) -> str:
    """Anki tags can't contain spaces — convert to underscores; strip punctuation
    that would confuse the tag parser."""
    s = re.sub(r"[^\w]+", "_", s)
    return s.strip("_") or "unknown"


def build_tags(q: dict) -> str:
    parts = []
    if q.get("topic"):
        parts.append(f"topic::{tag_value(q['topic'])}")
    if q.get("subtopic"):
        parts.append(f"subtopic::{tag_value(q['subtopic'])}")
    if q.get("source"):
        parts.append(f"source::{tag_value(q['source'])}")
    return " ".join(parts)


def main() -> int:
    questions = json.loads(QUESTIONS_PATH.read_text())

    lines = [
        "#separator:tab",
        "#html:true",
        "#notetype:Basic",
        "#deck:Databricks Learner",
        "#columns:Front\tBack\tTags",
        "#tags column:3",
    ]

    image_count = 0
    for q in questions:
        if q.get("images") or q.get("option_images"):
            image_count += 1
        front = build_front(q)
        back = build_back(q)
        tags = build_tags(q)
        lines.append(f"{front}\t{back}\t{tags}")

    OUTPUT_PATH.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Wrote {len(questions)} cards to {OUTPUT_PATH}")
    print(f"  Cards with images: {image_count}")
    print(f"  Copy data/images/* into Anki's collection.media to render images.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
