#!/usr/bin/env python3
"""Basic token frequency analysis for EVA-like text files."""
from __future__ import annotations
import sys
from collections import Counter
from pathlib import Path

import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

# Allow running as a script from project root or scripts dir
sys.path.insert(0, str(Path(__file__).resolve().parent))
from parse_eva_text import tokens_from_files


def main(argv: list[str]) -> int:
    if not argv:
        print("Usage: python scripts/analyze_tokens.py data/transcriptions/*.eva")
        return 2
    toks = tokens_from_files(argv)
    c = Counter(toks)
    print(f"tokens: {len(toks)}")
    print(f"types:  {len(c)}")
    print("\nTop tokens:")
    for tok, n in c.most_common(50):
        print(f"{tok}\t{n}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
