"""Tests for analyze_form_collocations.py (Rota 43)."""
from __future__ import annotations

import csv
import io
from pathlib import Path

import pytest

from scripts.analyze_form_collocations import (
    GUARDRAIL,
    build_locus_index,
    chi2_standalone_asymmetry,
    collocation_analysis,
    standalone_after,
    trigrams_and_bigrams,
)

FORMS = ["okal", "okar", "okol", "okor", "otal", "otar", "otol", "otor"]
BORDER = {"ar", "al", "or", "ol"}


def make_exact_rows(tokens_with_prev_next: list[tuple[str, str, str]]) -> list[dict[str, str]]:
    return [
        {
            "token": tok,
            "previous_token": prev,
            "next_token": nxt,
            "line_position": "middle",
            "locus_kind": "P",
            "prefix": tok[:2],
            "suffix": tok[2:],
        }
        for tok, prev, nxt in tokens_with_prev_next
    ]


def make_corpus_rows(locus_sequences: list[list[str]]) -> list[dict[str, str]]:
    rows = []
    for l_idx, seq in enumerate(locus_sequences):
        for t_idx, tok in enumerate(seq):
            rows.append({
                "folio": "f01r",
                "locus": f"L{l_idx:03d}",
                "token": tok,
                "token_index": str(t_idx),
            })
    return rows


def test_standalone_after_counts_border_tokens():
    exact = make_exact_rows([
        ("okar", "_", "ar"),
        ("okar", "_", "al"),
        ("okar", "_", "chedy"),
        ("okal", "_", "ar"),
        ("okal", "_", "daiin"),
    ])
    result = standalone_after(exact)
    assert result["okar"]["ar"] == 1
    assert result["okar"]["al"] == 1
    assert "chedy" not in result["okar"]
    assert result["okal"]["ar"] == 1
    assert sum(result["okal"].values()) == 1


def test_collocation_analysis_counts_neighbors():
    exact = make_exact_rows([
        ("okar", "daiin", "ar"),
        ("okar", "_", "ar"),
        ("okal", "aiin", "_"),
    ])
    prev, nxt, pos, locus, ps = collocation_analysis(exact)
    assert prev["okar"]["daiin"] == 1
    assert nxt["okar"]["ar"] == 2
    assert prev["okal"]["aiin"] == 1
    assert ps[("ok", "ar")] == 2
    assert ps[("ok", "al")] == 1


def test_build_locus_index_sorts_by_token_index():
    corpus = make_corpus_rows([["okar", "ar", "chedy"], ["okal", "daiin"]])
    idx = build_locus_index(corpus)
    for key, toks in idx.items():
        indices = [t[0] for t in toks]
        assert indices == sorted(indices)


def test_trigrams_finds_form_border_pattern():
    corpus = make_corpus_rows([
        ["okar", "ar", "_END_placeholder"],
        ["otar", "ar", "al"],
    ])
    idx = build_locus_index(corpus)
    trigrams, bigrams_ff, compounds = trigrams_and_bigrams(idx)
    assert trigrams[("okar", "ar", "_END_placeholder")] == 1
    assert trigrams[("otar", "ar", "al")] == 1


def test_trigrams_finds_bigram_form_form():
    corpus = make_corpus_rows([["okar", "otar", "daiin"]])
    idx = build_locus_index(corpus)
    _, bigrams_ff, _ = trigrams_and_bigrams(idx)
    assert bigrams_ff[("okar", "otar")] == 1


def test_trigrams_finds_compound_form_border_form():
    corpus = make_corpus_rows([["okar", "ar", "otol"]])
    idx = build_locus_index(corpus)
    _, _, compounds = trigrams_and_bigrams(idx)
    assert compounds[("okar", "ar", "otol")] == 1


def test_chi2_asymmetry_detects_difference():
    # ar-group: 30 hits out of 200 total (15%)
    # al-group: 14 hits out of 200 total (7%)
    import collections
    standalone = {
        "okar": collections.Counter({"ar": 20, "ol": 10}),
        "otar": collections.Counter({"ar": 8, "al": 5, "ol": 3}),
        "okal": collections.Counter({"or": 4, "ol": 3, "ar": 2, "al": 1}),
        "otal": collections.Counter({"ol": 4, "al": 2, "or": 2, "ar": 1}),
    }
    exact_rows = (
        make_exact_rows([("okar", "_", "ar")] * 100 + [("otar", "_", "ar")] * 100)
        + make_exact_rows([("okal", "_", "daiin")] * 100 + [("otal", "_", "daiin")] * 100)
    )
    result = chi2_standalone_asymmetry(standalone, exact_rows)
    assert result["ar_group_rate"] > result["al_group_rate"]
    assert result["chi2"] > 0


def test_chi2_returns_zero_for_equal_rates():
    import collections
    standalone = {
        "okar": collections.Counter({"ar": 10}),
        "otar": collections.Counter({"ar": 10}),
        "okal": collections.Counter({"ar": 10}),
        "otal": collections.Counter({"ar": 10}),
    }
    exact_rows = (
        make_exact_rows([("okar", "_", "ar")] * 100 + [("otar", "_", "ar")] * 100)
        + make_exact_rows([("okal", "_", "ar")] * 100 + [("otal", "_", "ar")] * 100)
    )
    result = chi2_standalone_asymmetry(standalone, exact_rows)
    assert result["chi2"] == pytest.approx(0.0, abs=0.01)


def test_guardrail_constant():
    assert "decipherment" in GUARDRAIL


def test_real_data_chi2_is_significant():
    data_dir = Path(__file__).resolve().parents[1] / "data" / "derived"
    exact_csv = data_dir / "exact_form_context_table_zl3b.csv"
    if not exact_csv.exists():
        pytest.skip("exact_form_context_table_zl3b.csv not found")
    exact_rows = list(csv.DictReader(exact_csv.open(encoding="utf-8")))
    standalone = standalone_after(exact_rows)
    result = chi2_standalone_asymmetry(standalone, exact_rows)
    assert result["chi2"] > 7.88, f"Expected chi2 > 7.88 (p<0.005), got {result['chi2']:.2f}"
    assert result["ar_group_rate"] > result["al_group_rate"]
