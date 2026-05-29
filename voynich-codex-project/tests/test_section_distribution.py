"""Tests for analyze_section_distribution.py (Rota 44)."""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from scripts.analyze_section_distribution import (
    GUARDRAIL,
    build_tables,
    cramer_v,
    detect_currier,
    detect_section_type,
)


def make_rows(specs: list[tuple[str, str, str, str, str]]) -> list[dict[str, str]]:
    """(token, folio, section_note, locus_kind, prefix/suffix inferred)"""
    rows = []
    for token, folio, section_note, locus_kind, _ in specs:
        prefix = token[:2] if len(token) >= 4 else ""
        suffix = token[2:] if len(token) >= 4 else ""
        rows.append({
            "token": token,
            "folio": folio,
            "section_note": section_note,
            "locus_kind": locus_kind,
            "prefix": prefix,
            "suffix": suffix,
        })
    return rows


def test_detect_currier_a():
    assert detect_currier("Currier's language A, hand 1") == "A"
    assert detect_currier("Currier's language A, hand 2") == "A"


def test_detect_currier_b():
    assert detect_currier("Currier's language B, hand 3") == "B"


def test_detect_currier_unknown():
    assert detect_currier("Light star, 7 points, tail") == "unknown"
    assert detect_currier("") == "unknown"


def test_detect_section_type_astronomical():
    assert detect_section_type("Light star, 7 points, tail", "f68r") == "astronomical"
    assert detect_section_type("Light star, dotted, 7 points", "f70r") == "astronomical"


def test_detect_section_type_balneological():
    assert detect_section_type("2 lakes and 14 nymphs", "f78r") == "balneological"


def test_detect_section_type_pharmaceutical():
    assert detect_section_type("B@R p88 pharmaceutical recipe", "f88r") == "pharmaceutical"


def test_detect_section_type_herbal_by_folio():
    assert detect_section_type("Currier's language A, hand 1", "f10r") == "herbal"


def test_build_tables_currier_suffix_separation():
    rows = make_rows([
        ("okar", "f68r", "Currier's language B, hand 3", "P", ""),  # B, suffix=ar
        ("okar", "f68r", "Currier's language B, hand 3", "P", ""),
        ("okol", "f10r", "Currier's language A, hand 1", "P", ""),  # A, suffix=ol
        ("okol", "f10r", "Currier's language A, hand 1", "P", ""),
        ("okol", "f10r", "Currier's language A, hand 1", "P", ""),
    ])
    tables = build_tables(rows)
    cs = tables["currier_suffix"]
    assert cs["B"].get("ar", 0) == 2
    assert cs["A"].get("ol", 0) == 3
    # Operator split should be identical (all ok-)
    cp = tables["currier_prefix"]
    assert cp["B"].get("ok", 0) == 2
    assert cp["A"].get("ok", 0) == 3


def test_build_tables_section_form():
    rows = make_rows([
        ("okar", "f68r", "Light star, 7 points, tail", "C", ""),
        ("otar", "f68r", "Light star, dotted, 7 points, tail", "C", ""),
        ("okal", "f84r", "2 lakes and 14 nymphs", "P", ""),
    ])
    tables = build_tables(rows)
    sf = tables["section_form"]
    assert sf["astronomical"].get("okar", 0) >= 1
    assert sf["astronomical"].get("otar", 0) >= 1
    assert sf["balneological"].get("okal", 0) == 1


def test_cramer_v_two_category_separation():
    # Perfect separation: A always -ol, B always -ar → V = 1.0
    table = {"A": {"ol": 10}, "B": {"ar": 10}}
    v = cramer_v(table)
    assert v == pytest.approx(1.0, abs=0.01)


def test_cramer_v_uniform_distribution():
    # Uniform: equal -ar/-ol in both → V ≈ 0
    table = {"A": {"ar": 5, "ol": 5}, "B": {"ar": 5, "ol": 5}}
    v = cramer_v(table)
    assert v == pytest.approx(0.0, abs=0.01)


def test_cramer_v_operator_vs_suffix_asymmetry():
    # Replicate Rota 44 finding: suffix V >> prefix V
    suffix_table = {
        "A": {"ol": 20, "or": 8, "al": 4, "ar": 1},
        "B": {"ar": 27, "al": 20, "ol": 10, "or": 7},
    }
    prefix_table = {
        "A": {"ok": 17, "ot": 16},
        "B": {"ok": 32, "ot": 32},
    }
    v_suf = cramer_v(suffix_table)
    v_pref = cramer_v(prefix_table)
    assert v_suf > v_pref * 5, f"Expected V(suffix) >> V(prefix), got {v_suf:.3f} vs {v_pref:.3f}"


def test_guardrail_constant():
    assert "decipherment" in GUARDRAIL
    assert "not" in GUARDRAIL


def test_real_data_currier_suffix_beats_prefix():
    data_dir = Path(__file__).resolve().parents[1] / "data" / "derived"
    exact_csv = data_dir / "exact_form_context_table_zl3b.csv"
    if not exact_csv.exists():
        pytest.skip("exact_form_context_table_zl3b.csv not found")
    rows = list(csv.DictReader(exact_csv.open(encoding="utf-8")))
    tables = build_tables(rows)
    v_suf = cramer_v(tables["currier_suffix"])
    v_pref = cramer_v(tables["currier_prefix"])
    assert v_suf > v_pref * 5, (
        f"Expected Currier×suffix V >> Currier×prefix V, got {v_suf:.4f} vs {v_pref:.4f}"
    )


def test_real_data_section_form_has_signal():
    data_dir = Path(__file__).resolve().parents[1] / "data" / "derived"
    exact_csv = data_dir / "exact_form_context_table_zl3b.csv"
    if not exact_csv.exists():
        pytest.skip("exact_form_context_table_zl3b.csv not found")
    rows = list(csv.DictReader(exact_csv.open(encoding="utf-8")))
    tables = build_tables(rows)
    v_sf = cramer_v(tables["section_form"])
    assert v_sf > 0.05, f"Expected section×form V > 0.05, got {v_sf:.4f}"
