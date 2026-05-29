#!/usr/bin/env python3
"""Analyze candidate Voynich border/prefix patterns.

This is deliberately simple. It gives quick counts for the hypotheses:
- operators: ok-, ot-, qo-, yk-, yt-
- borders: -dy, -y, -aiin, -iin, -ar, -al, -or, -ol, -dar, -dal
"""
from __future__ import annotations
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_eva_text import tokens_from_files

PREFIXES = ["qok", "qo", "ok", "ot", "yk", "yt", "o", "y"]
SUFFIXES = ["daiin", "aiin", "iin", "dar", "dal", "dy", "ar", "al", "or", "ol", "y"]
MATRIX_SUFFIXES = ["ar", "al", "or", "ol"]
MATRIX_PREFIXES = ["ok", "ot", "qo", "qok", "yk", "yt", "o", "y", "ch", "sh", "d"]


def count_prefixes(tokens: list[str]) -> Counter[str]:
    out = Counter()
    for tok in tokens:
        for pref in PREFIXES:
            if tok.startswith(pref):
                out[pref] += 1
    return out


def count_suffixes(tokens: list[str]) -> Counter[str]:
    out = Counter()
    for tok in tokens:
        for suff in SUFFIXES:
            if tok.endswith(suff):
                out[suff] += 1
    return out


def matrix(tokens: list[str]) -> dict[str, Counter[str]]:
    out: dict[str, Counter[str]] = defaultdict(Counter)
    for tok in tokens:
        for pref in MATRIX_PREFIXES:
            if tok.startswith(pref):
                for suff in MATRIX_SUFFIXES:
                    if tok.endswith(suff):
                        out[pref][suff] += 1
    return out


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: python scripts/analyze_border_matrix.py data/transcriptions/*.eva")
        return 2
    toks = tokens_from_files(argv)
    print(f"tokens={len(toks)} types={len(set(toks))}")

    print("\nPrefix counts")
    for k, v in count_prefixes(toks).most_common():
        print(f"{k}\t{v}")

    print("\nSuffix counts")
    for k, v in count_suffixes(toks).most_common():
        print(f"{k}\t{v}")

    print("\nMatrix prefix × suffix")
    mat = matrix(toks)
    header = ["prefix"] + MATRIX_SUFFIXES
    print("\t".join(header))
    for pref in sorted(mat):
        print("\t".join([pref] + [str(mat[pref][s]) for s in MATRIX_SUFFIXES]))

    print("\nCandidate matrix tokens")
    for tok in sorted(set(toks)):
        if any(tok.startswith(p) for p in MATRIX_PREFIXES) and any(tok.endswith(s) for s in MATRIX_SUFFIXES):
            print(tok)
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
