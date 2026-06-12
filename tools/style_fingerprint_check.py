"""Lightweight stylistic-uniformity check for the JOSS paper.

This is not an AI detector. It is a manuscript hygiene script: it counts a
small set of over-smooth academic phrases and reports sentence-length
variation so that the author can catch low-variance, slogan-like prose before
submission.
"""

from __future__ import annotations

import re
import statistics
import sys
from pathlib import Path


# These terms are diagnostic targets, not manuscript vocabulary.
FOCAL_WORDS = {
    "delve", "intricate", "meticulous", "pivotal", "realm", "navigate",
    "landscape", "tapestry", "foster", "elevate", "underscore", "showcasing",
    "compelling", "paramount", "unwavering",
}
PHRASES = [
    "it is important to note",
    "it is worth noting",
    "plays a crucial role",
    "plays a pivotal role",
    "in today's",
    "in the ever-evolving",
    "not only",
    "not just",
    "in conclusion",
    "in summary",
]


def strip_yaml_and_code(text: str) -> str:
    text = re.sub(r"^---.*?---", "", text, flags=re.DOTALL)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    return text


def sentences(text: str) -> list[str]:
    pieces = re.split(r"(?<=[.!?])\s+", text)
    return [p.strip() for p in pieces if p.strip() and len(p.strip().split()) > 2]


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    path = Path(argv[0]) if argv else Path("paper/paper.md")
    text = strip_yaml_and_code(path.read_text(encoding="utf-8"))
    lowered = text.lower()
    words = re.findall(r"[a-zA-Z]+", lowered)
    counts = {word: words.count(word) for word in sorted(FOCAL_WORDS) if words.count(word)}
    phrase_counts = {phrase: lowered.count(phrase) for phrase in PHRASES if lowered.count(phrase)}
    lengths = [len(s.split()) for s in sentences(text)]
    mean = statistics.mean(lengths) if lengths else 0.0
    stdev = statistics.pstdev(lengths) if len(lengths) > 1 else 0.0
    cv = stdev / mean if mean else 0.0
    print(f"file: {path}")
    print(f"words: {len(words)}")
    print(f"sentences: {len(lengths)}")
    print(f"mean_sentence_length: {mean:.2f}")
    print(f"sentence_length_cv: {cv:.2f}")
    print(f"focal_words: {counts if counts else '{}'}")
    print(f"phrase_counts: {phrase_counts if phrase_counts else '{}'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
