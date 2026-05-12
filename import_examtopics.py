#!/usr/bin/env python3
"""
Parses pages saved from examtopics.com and imports questions into data/questions.json.

Accepts two file formats in `examtopics_html/`:
  - .webarchive (Safari) — preferred: contains HTML + auth-fetched images as
    subresources, so question/option images can be extracted.
  - .html (plain "save as") — works, but image-containing questions are skipped
    because examtopics' image CDN returns 403 to anonymous requests.

If both .webarchive and .html exist for the same stem (e.g. page_5.*), the
.webarchive version is preferred.

Usage:
    python3 import_examtopics.py [<dir>] [--dry-run] [--inspect]

Defaults to examtopics_html/ in the repo root. Images are written to data/images/.

Behavior:
- Uses examtopics' stated "Correct Answer". Multi-answer letters (e.g. "BA")
  are sorted alphabetically ("AB"); the quiz UI uses checkboxes when len > 1.
- Skips question only if HTML is plain (.html) AND the question has images.
- Replaces existing duplicate questions EXCEPT when the existing source is
  `community_old_exam` (those are protected).
"""

import argparse
import json
import plistlib
import re
import sys
import uuid
from datetime import date
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("ERROR: beautifulsoup4 not installed. Run: pip install beautifulsoup4")
    sys.exit(1)

from import_questions import map_topic
from utils.questions import load_questions, save_questions

IMAGES_DIR = Path("data/images")

QUESTION_CARD_SELECTORS = [
    "div.exam-question-card",
    "div.question-body",
    '[class*="question-card"]',
]
QUESTION_TEXT_SELECTORS = [
    "p.card-text",
    ".question-body",
    ".card-text",
    '[class*="question-text"]',
]
OPTIONS_CONTAINER_SELECTORS = [
    ".question-choices-container",
    ".choices-list",
    "ul.choices",
]
CORRECT_ANSWER_SELECTORS = [
    ".correct-answer-box .correct-answer",
    ".correct-answer",
    ".question-answer .correct-answer",
]


def first_match(card, selectors: list[str]):
    for sel in selectors:
        el = card.select_one(sel)
        if el:
            return el
    return None


def normalize_question(text: str) -> str:
    """For dedup: lowercase, collapse whitespace, strip punctuation, first 200 chars."""
    t = text.lower()
    t = re.sub(r"\s+", " ", t)
    t = re.sub(r"[^\w\s]", "", t)
    return t.strip()[:200]


def load_html_and_images(path: Path) -> tuple[str, dict[str, bytes]]:
    """Return (html, {filename: bytes}). For .html, images dict is empty."""
    if path.suffix == ".webarchive":
        with open(path, "rb") as f:
            data = plistlib.load(f)
        html = data["WebMainResource"]["WebResourceData"].decode("utf-8")
        images: dict[str, bytes] = {}
        for sub in data.get("WebSubresources", []):
            url = sub.get("WebResourceURL", "")
            mime = sub.get("WebResourceMIMEType", "")
            if "img.examtopics.com" in url and mime.startswith("image/"):
                name = url.rsplit("/", 1)[-1]
                images[name] = sub["WebResourceData"]
        return html, images
    return path.read_text(encoding="utf-8"), {}


def collect_files(html_dir: Path) -> list[Path]:
    """Pick one file per stem, preferring .webarchive over .html."""
    by_stem: dict[str, Path] = {}
    for f in sorted(html_dir.iterdir()):
        if f.suffix not in (".html", ".webarchive"):
            continue
        if f.stem not in by_stem or f.suffix == ".webarchive":
            by_stem[f.stem] = f
    return [by_stem[s] for s in sorted(by_stem)]


def save_images(images: dict[str, bytes]) -> int:
    """Write images to data/images/ (idempotent — skips existing files)."""
    if not images:
        return 0
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    written = 0
    for name, data in images.items():
        target = IMAGES_DIR / name
        if not target.exists():
            target.write_bytes(data)
            written += 1
    return written


def extract_question_cards(soup):
    for sel in QUESTION_CARD_SELECTORS:
        cards = soup.select(sel)
        if cards:
            return cards
    return []


def extract_question_text(card) -> str | None:
    el = first_match(card, QUESTION_TEXT_SELECTORS)
    if not el:
        return None
    return el.get_text(separator="\n").strip() or None


def extract_question_images(card, images_available: set[str]) -> list[str]:
    """Images in the question body, NOT inside the options container."""
    body = card.select_one(".question-body") or card
    options_container = first_match(body, OPTIONS_CONTAINER_SELECTORS)
    option_imgs = set()
    if options_container:
        option_imgs = {id(i) for i in options_container.find_all("img")}
    paths: list[str] = []
    for img in body.find_all("img"):
        if id(img) in option_imgs:
            continue
        src = img.get("src", "")
        if "img.examtopics.com" not in src:
            continue
        name = src.rsplit("/", 1)[-1]
        if name in images_available:
            paths.append(str(IMAGES_DIR / name))
    return paths


def extract_options(card, images_available: set[str]) -> tuple[dict[str, str], dict[str, str]] | None:
    """Returns (options, option_images) or None."""
    container = first_match(card, OPTIONS_CONTAINER_SELECTORS)
    if not container:
        return None
    options: dict[str, str] = {}
    option_images: dict[str, str] = {}
    for li in container.select("li"):
        text = li.get_text(separator=" ").strip()
        m = re.match(r"^([A-E])[\.\):]\s*(.*)", text, re.DOTALL)
        if not m:
            continue
        key = m.group(1)
        val = re.sub(r"\s+", " ", m.group(2)).strip()
        options[key] = val
        img = li.find("img")
        if img:
            src = img.get("src", "")
            name = src.rsplit("/", 1)[-1]
            if "img.examtopics.com" in src and name in images_available:
                option_images[key] = str(IMAGES_DIR / name)
    if len(options) < 4:
        return None
    # Option must have either text or an image
    for key, val in options.items():
        if not val and key not in option_images:
            return None
    return options, option_images


def extract_correct_answer(card) -> str | None:
    el = first_match(card, CORRECT_ANSWER_SELECTORS)
    if not el:
        return None
    m = re.search(r"([A-E]+)", el.get_text())
    if not m:
        return None
    return "".join(sorted(set(m.group(1))))


def inspect_first_card(soup, images: dict[str, bytes]) -> None:
    cards = extract_question_cards(soup)
    print(f"Found {len(cards)} question cards. Images available: {len(images)}")
    if not cards:
        print("\nTop-level divs (first 20):")
        for div in soup.select("div[class]")[:20]:
            print(f"  div class={div.get('class')}")
        return
    first = cards[0]
    print(f"\nFirst card classes: {first.get('class')}")
    print("Extraction attempts:")
    qt = extract_question_text(first)
    print(f"  question: {qt[:100] + '…' if qt else 'NONE'}")
    avail = set(images.keys())
    print(f"  question images: {extract_question_images(first, avail)}")
    print(f"  options: {extract_options(first, avail)}")
    print(f"  correct answer: {extract_correct_answer(first)}")


def parse_file(path: Path) -> tuple[list[dict], dict[str, int], int]:
    html, images = load_html_and_images(path)
    images_written = save_images(images)
    avail = set(images.keys())
    soup = BeautifulSoup(html, "html.parser")
    cards = extract_question_cards(soup)
    results: list[dict] = []
    skipped = {"no_question": 0, "no_options": 0, "no_answer": 0, "image_missing": 0}

    for card in cards:
        question = extract_question_text(card)
        if not question:
            skipped["no_question"] += 1
            continue
        opt_result = extract_options(card, avail)
        if not opt_result:
            skipped["no_options"] += 1
            continue
        options, option_images = opt_result
        # If the card references CDN images but we don't have them (plain .html
        # without auth), skip — the quiz UI would render broken paths.
        body = card.select_one(".question-body") or card
        cdn_imgs = [i for i in body.find_all("img") if "img.examtopics.com" in i.get("src", "")]
        if cdn_imgs and not avail:
            skipped["image_missing"] += 1
            continue
        question_images = extract_question_images(card, avail)
        stated = extract_correct_answer(card)
        if not stated:
            skipped["no_answer"] += 1
            continue
        topic, subtopic = map_topic(question)
        q = {
            "topic": topic,
            "subtopic": subtopic,
            "objective": subtopic,
            "question": question,
            "options": options,
            "correct_answer": stated,
            "explanation": f"Stated answer from examtopics: {stated}.",
            "source": "examtopics",
        }
        if question_images:
            q["images"] = question_images
        if option_images:
            q["option_images"] = option_images
        results.append(q)

    return results, skipped, images_written


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("html_dir", nargs="?", default="examtopics_html")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--inspect", action="store_true")
    args = parser.parse_args()

    html_dir = Path(args.html_dir)
    if not html_dir.exists():
        print(f"ERROR: directory not found: {html_dir}")
        return 1

    files = collect_files(html_dir)
    if not files:
        print(f"ERROR: no .html or .webarchive files in {html_dir}")
        return 1

    if args.inspect:
        html, images = load_html_and_images(files[0])
        print(f"Inspecting {files[0].name}\n")
        inspect_first_card(BeautifulSoup(html, "html.parser"), images)
        return 0

    print(f"Parsing {len(files)} file(s) from {html_dir}…\n")
    all_new: list[dict] = []
    total_skipped = {"no_question": 0, "no_options": 0, "no_answer": 0, "image_missing": 0}
    total_imgs_written = 0
    for f in files:
        parsed, skipped, imgs_written = parse_file(f)
        total_imgs_written += imgs_written
        img_note = f" [+{imgs_written} new imgs]" if imgs_written else ""
        print(f"  {f.name}: {len(parsed)} parsed, skipped {sum(skipped.values())} ({skipped}){img_note}")
        all_new.extend(parsed)
        for k, v in skipped.items():
            total_skipped[k] += v

    print(f"\nTotal parsed: {len(all_new)} | skipped: {sum(total_skipped.values())} {total_skipped} | new images: {total_imgs_written}")
    if not all_new:
        print("Nothing to import.")
        return 1

    existing = load_questions()
    existing_by_norm = {normalize_question(q["question"]): i for i, q in enumerate(existing)}
    multi_count = sum(1 for q in all_new if len(q["correct_answer"]) > 1)
    img_count = sum(1 for q in all_new if q.get("images") or q.get("option_images"))
    print(f"  of which multi-answer: {multi_count}, with images: {img_count}")

    replaced = added = protected = 0
    for new_q in all_new:
        new_q["id"] = str(uuid.uuid4())
        new_q["created_at"] = str(date.today())
        norm = normalize_question(new_q["question"])
        if norm in existing_by_norm:
            idx = existing_by_norm[norm]
            if existing[idx].get("source") == "community_old_exam":
                protected += 1
                continue
            existing[idx] = new_q
            replaced += 1
        else:
            existing.append(new_q)
            existing_by_norm[norm] = len(existing) - 1
            added += 1

    print(f"\nResult: {added} added, {replaced} replaced, {protected} protected (community_old_exam). Bank size: {len(existing)}")

    if args.dry_run:
        print("(dry-run — no changes written to questions.json)")
        return 0

    save_questions(existing)
    print(f"Wrote {len(existing)} questions to data/questions.json")
    return 0


if __name__ == "__main__":
    sys.exit(main())
