"""Functions for loading Voynich corpus data."""
from __future__ import annotations
import csv
from pathlib import Path
from typing import Iterator

from .types import Token, Locus, MatrixCandidate

# Default paths relative to project root
_ROOT = Path(__file__).resolve().parents[2]
_BORDER_MATRIX_CSV = _ROOT / "data" / "derived" / "border_matrix_context_zl3b.csv"
_EXACT_FORMS_CSV = _ROOT / "data" / "derived" / "exact_form_context_table_zl3b.csv"
_ZL3B_TXT = _ROOT / "data" / "raw" / "ZL3b-n.txt"


def read_border_matrix(path: Path | None = None) -> list[dict[str, str]]:
    """Load the border matrix context CSV as a list of dicts.

    Returns the full corpus (41,005 tokens, 5,385 loci) with columns:
    folio, locus, locus_kind, prefix, suffix, line_position, token, etc.
    """
    p = path or _BORDER_MATRIX_CSV
    with p.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_exact_forms(path: Path | None = None) -> list[dict[str, str]]:
    """Load the exact form context table (786 rows, 8 ok/ot forms).

    Columns include visual annotation fields (visual_zone, ring, sector, etc.)
    in addition to the base corpus fields.
    """
    p = path or _EXACT_FORMS_CSV
    with p.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def read_zl3b_raw(path: Path | None = None) -> Iterator[str]:
    """Iterate over raw lines of the ZL3b-n.txt IVTFF transcription."""
    p = path or _ZL3B_TXT
    with p.open(encoding="utf-8") as f:
        yield from f


def iter_tokens(rows: list[dict[str, str]]) -> Iterator[Token]:
    """Convert border_matrix rows to Token objects."""
    for r in rows:
        try:
            idx = int(r.get("token_index", "0") or 0)
            count = int(r.get("line_token_count", "0") or 0)
        except ValueError:
            idx, count = 0, 0
        yield Token(
            token=r.get("token", ""),
            folio=r.get("folio", ""),
            locus=r.get("locus", ""),
            locus_kind=r.get("locus_kind", ""),
            line_position=r.get("line_position", ""),
            token_index=idx,
            line_token_count=count,
            prefix=r.get("prefix", ""),
            suffix=r.get("suffix", ""),
            previous_token=r.get("previous_token", ""),
            next_token=r.get("next_token", ""),
        )


def iter_matrix_candidates(rows: list[dict[str, str]]) -> Iterator[MatrixCandidate]:
    """Convert exact_form rows to MatrixCandidate objects."""
    for r in rows:
        yield MatrixCandidate(
            token=r.get("token", ""),
            folio=r.get("folio", ""),
            locus=r.get("locus", ""),
            locus_kind=r.get("locus_kind", ""),
            prefix=r.get("prefix", ""),
            suffix=r.get("suffix", ""),
            line_position=r.get("line_position", ""),
            visual_zone=r.get("visual_zone", ""),
            visual_notes=r.get("visual_notes", ""),
            annotation_confidence=r.get("annotation_confidence", ""),
        )
