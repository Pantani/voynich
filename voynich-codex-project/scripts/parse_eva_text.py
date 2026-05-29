#!/usr/bin/env python3
"""Utility functions for rough EVA token cleanup."""
from __future__ import annotations
import re
from pathlib import Path
from typing import Iterable

COMMENT_RE = re.compile(r"#.*$")
LOCUS_RE = re.compile(r"<[^>]+>")
CLEAN_RE = re.compile(r"[^a-zA-Z0-9.\s-]")


def clean_line(line: str) -> str:
    line = COMMENT_RE.sub("", line)
    line = LOCUS_RE.sub("", line)
    line = line.replace("-", " ").replace("=", " ")
    line = CLEAN_RE.sub(" ", line)
    return line.lower()


def tokens_from_text(text: str) -> list[str]:
    toks: list[str] = []
    for line in text.splitlines():
        line = clean_line(line)
        for part in re.split(r"[\s.]+", line):
            part = part.strip()
            if part:
                toks.append(part)
    return toks


def tokens_from_files(paths: Iterable[str | Path]) -> list[str]:
    toks: list[str] = []
    for path in paths:
        p = Path(path)
        toks.extend(tokens_from_text(p.read_text(encoding="utf-8")))
    return toks
