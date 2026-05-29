"""Core data types for Voynich corpus analysis."""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Token:
    """A single EVA token with its position in the locus."""
    token: str
    folio: str
    locus: str
    locus_kind: str          # P, L, C, R
    line_position: str       # start, middle, end, single
    token_index: int
    line_token_count: int
    prefix: str = ""
    suffix: str = ""
    previous_token: str = ""
    next_token: str = ""

    @property
    def is_exact_form(self) -> bool:
        from .constants import FORMS
        return self.token in FORMS

    @property
    def suffix_axis_ao(self) -> str | None:
        """Returns 'a' if suffix is al/ar, 'o' if ol/or, else None."""
        if self.suffix in ("al", "ar"):
            return "a"
        if self.suffix in ("ol", "or"):
            return "o"
        return None

    @property
    def suffix_axis_rl(self) -> str | None:
        """Returns 'r' if suffix is ar/or, 'l' if al/ol, else None."""
        if self.suffix in ("ar", "or"):
            return "r"
        if self.suffix in ("al", "ol"):
            return "l"
        return None


@dataclass(frozen=True)
class Locus:
    """A single locus (line or text unit) from the transcription."""
    folio: str
    locus_id: str            # e.g. "f67r2.35,@Pb"
    locus_kind: str          # P, L, C, R
    locus_code: str
    tokens: tuple[str, ...]  # ordered token sequence

    @property
    def token_count(self) -> int:
        return len(self.tokens)


@dataclass
class MatrixCandidate:
    """A token that is a candidate for the ar/al/or/ol matrix."""
    token: str
    folio: str
    locus: str
    locus_kind: str
    prefix: str
    suffix: str
    line_position: str
    visual_zone: str = ""
    visual_notes: str = ""
    annotation_confidence: str = ""

    @property
    def axis_ao(self) -> str:
        return "a" if self.suffix in ("al", "ar") else "o"

    @property
    def axis_rl(self) -> str:
        return "r" if self.suffix in ("ar", "or") else "l"
