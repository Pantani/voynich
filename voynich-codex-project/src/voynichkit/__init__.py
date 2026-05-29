"""voynichkit — Python package for Voynich corpus analysis.

Provides a clean programmatic API over the ZL3b EVA corpus and derived datasets.
The scripts in scripts/ remain the canonical CLI entry points; this package
exposes their core logic for interactive use and future notebooks.
"""
from .constants import FORMS, BORDER, OPERATORS, CLOSURES
from .types import Token, Locus, MatrixCandidate
from .corpus import read_border_matrix, read_exact_forms, read_zl3b_raw

__all__ = [
    "FORMS",
    "BORDER",
    "OPERATORS",
    "CLOSURES",
    "Token",
    "Locus",
    "MatrixCandidate",
    "read_border_matrix",
    "read_exact_forms",
    "read_zl3b_raw",
]
