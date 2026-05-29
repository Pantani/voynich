"""Tests for analyze_section_scribe.py (Rota 47)."""
from __future__ import annotations
import collections
import csv
from pathlib import Path
import pytest

from scripts.analyze_section_scribe import (
    GUARDRAIL,
    ao_bit,
    classify_section,
    build_tables,
    cramer_v,
)


def make_rows(specs):
    rows = []
    for token, folio, sn, cur in specs:
        rows.append({"token": token, "folio": folio, "section_note": sn,
                     "currier": cur, "prefix": token[:2], "suffix": token[2:]})
    return rows


def test_ao_bit_a_suffixes():
    assert ao_bit("al") == "a"
    assert ao_bit("ar") == "a"


def test_ao_bit_o_suffixes():
    assert ao_bit("ol") == "o"
    assert ao_bit("or") == "o"


def test_ao_bit_unknown():
    assert ao_bit("dy") is None
    assert ao_bit("") is None


def test_classify_section_astronomical_by_note():
    assert classify_section("f68r", "Light star, 7 points, tail") == "astronomical"


def test_classify_section_balneological():
    assert classify_section("f78r", "2 lakes and 14 nymphs") == "balneological"


def test_classify_section_herbal_by_range():
    assert classify_section("f10r", "") == "herbal"
    assert classify_section("f50v", "") == "herbal"


def test_classify_section_pharmaceutical():
    assert classify_section("f92r", "") == "pharmaceutical"


def test_classify_section_recipes():
    assert classify_section("f110r", "") == "recipes"


def test_build_tables_section_split():
    rows = make_rows([
        ("okal", "f10r", "", "A"),  # herbal A, suffix al → a
        ("okol", "f10r", "", "A"),  # herbal A, suffix ol → o
        ("okar", "f80r", "2 lakes and 14 nymphs", "B"),  # balneo B, ar → a
    ])
    t = build_tables(rows)
    assert t["section_ao"]["herbal"]["a"] == 1
    assert t["section_ao"]["herbal"]["o"] == 1
    assert t["section_ao"]["balneological"]["a"] == 1
    assert t["currier_ao"]["A"]["a"] == 1
    assert t["currier_ao"]["A"]["o"] == 1
    assert t["currier_ao"]["B"]["a"] == 1


def test_cramer_v_perfect_separation():
    table = {"A": collections.Counter({"o": 10}),
             "B": collections.Counter({"a": 10})}
    v, n = cramer_v(table)
    assert n == 20
    assert v == pytest.approx(1.0, abs=0.01)


def test_cramer_v_uniform():
    table = {"A": collections.Counter({"a": 5, "o": 5}),
             "B": collections.Counter({"a": 5, "o": 5})}
    v, n = cramer_v(table)
    assert v == pytest.approx(0.0, abs=0.01)


def test_cramer_v_small_n_returns_zero():
    table = {"A": collections.Counter({"a": 1}),
             "B": collections.Counter({"o": 1})}
    v, n = cramer_v(table)
    assert v == 0.0


def test_guardrail_contains_not():
    assert "not" in GUARDRAIL
    assert "decipherment" in GUARDRAIL


def test_real_data_scribe_beats_section():
    data_dir = Path(__file__).resolve().parents[1] / "data" / "derived"
    csv_path = data_dir / "exact_form_context_table_currier_zl3b.csv"
    if not csv_path.exists():
        pytest.skip("exact_form_context_table_currier_zl3b.csv not found")
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    t = build_tables(rows)
    v_sec, _ = cramer_v(t["section_ao"])
    v_cur, _ = cramer_v({k: v for k, v in t["currier_ao"].items() if k in ("A", "B")})
    assert v_cur > v_sec, f"Expected V(Currier)={v_cur:.4f} > V(section)={v_sec:.4f}"


def test_real_data_herbal_intra_section_diverges():
    data_dir = Path(__file__).resolve().parents[1] / "data" / "derived"
    csv_path = data_dir / "exact_form_context_table_currier_zl3b.csv"
    if not csv_path.exists():
        pytest.skip("exact_form_context_table_currier_zl3b.csv not found")
    rows = list(csv.DictReader(csv_path.open(encoding="utf-8")))
    herbal_ab = collections.defaultdict(collections.Counter)
    for r in rows:
        if r.get("token", "") not in ["okal","okar","okol","okor","otal","otar","otol","otor"]:
            continue
        if classify_section(r.get("folio",""), r.get("section_note","")) != "herbal":
            continue
        ao = ao_bit(r.get("suffix", ""))
        cur = r.get("currier", "")
        if ao and cur in ("A", "B"):
            herbal_ab[cur][ao] += 1
    v, n = cramer_v(herbal_ab)
    assert v > 0.40, f"Herbal intra-section V should be >0.40, got {v:.4f} (n={n})"
    assert n >= 50, f"Need n>=50 for robust test, got {n}"
