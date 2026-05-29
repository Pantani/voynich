"""Tests for Rota 53 nucleus ch/sh analysis (scripts/analyze_nucleus.py)."""
from __future__ import annotations

import collections
from pathlib import Path

from scripts.analyze_nucleus import (
    GUARDRAIL,
    build,
    classify_section,
    clean_token,
    cramer_v,
    main,
    nucleus,
    parse_corpus,
    permutation_p,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"


def test_nucleus_classifies_ch_xor_sh():
    assert nucleus("shol") == "sh"
    assert nucleus("chol") == "ch"
    assert nucleus("chtaiin") == "ch"
    # both present -> excluded; neither present -> excluded
    assert nucleus("shchy") is None
    assert nucleus("daiin") is None
    # benched gallows carry no 'ch' substring and are excluded
    assert nucleus("cthy") is None
    assert nucleus("cphol") is None


def test_clean_token_resolves_alternates_and_strips_markup():
    assert clean_token("[cth:oto]res") == "cthres"
    assert clean_token("ok[a:o]in") == "okain"
    assert clean_token("sholdy<!@254;>") == "sholdy"
    assert clean_token("{c'y}") == ""  # {..} transcriber comments stripped whole
    assert clean_token("123") == ""


def test_classify_section_ranges():
    assert classify_section("f1r") == "herbal"
    assert classify_section("f66v") == "herbal"
    assert classify_section("f70r") == "astronomical"
    assert classify_section("f75r") == "balneological"
    assert classify_section("f99v") == "pharmaceutical"
    assert classify_section("f103r") == "recipes"


def test_cramer_v_extremes():
    # perfect association -> V == 1
    perfect = {"x": collections.Counter({"ch": 50}), "y": collections.Counter({"sh": 50})}
    v, n = cramer_v(perfect)
    assert n == 100
    assert v > 0.99
    # independence -> V ~ 0
    indep = {
        "x": collections.Counter({"ch": 50, "sh": 50}),
        "y": collections.Counter({"ch": 50, "sh": 50}),
    }
    v2, _ = cramer_v(indep)
    assert v2 < 1e-9


def test_permutation_p_detects_real_and_null_association():
    # strong association -> small p
    strong = [("x", "ch")] * 40 + [("y", "sh")] * 40
    v, _ = cramer_v({"x": collections.Counter({"ch": 40}), "y": collections.Counter({"sh": 40})})
    assert permutation_p(strong, v, n_perm=200, seed=1) < 0.05
    # no association -> large p
    null = [("x", "ch"), ("x", "sh"), ("y", "ch"), ("y", "sh")] * 20
    v0, _ = cramer_v(
        {"x": collections.Counter({"ch": 20, "sh": 20}), "y": collections.Counter({"ch": 20, "sh": 20})}
    )
    assert permutation_p(null, v0, n_perm=200, seed=1) > 0.2


def test_parse_corpus_reads_currier_and_tokens():
    folio_currier, tokens = parse_corpus(CORPUS)
    # known: f1r is Currier A per its $L=A header
    assert folio_currier.get("f1r") == "A"
    assert set(folio_currier.values()) <= {"A", "B", "?"}
    assert len(tokens) > 30000  # full corpus is ~41k tokens
    # tokens are (folio, clean_token) with bare-letter tokens
    assert all(t.islower() and t.isalpha() for _, t in tokens[:200])


def test_section_beats_currier_and_survives_control():
    """Integration: the Rota 52/53 finding holds on the real corpus."""
    folio_currier, tokens = parse_corpus(CORPUS)
    b = build(folio_currier, tokens)
    v_section, _ = cramer_v(b["section"])
    v_currier, _ = cramer_v(b["currier"])
    v_within_b, _ = cramer_v(b["within_B"])
    assert v_section > v_currier  # content beats scribe
    assert v_within_b > 0.10  # survives the Currier-B control


def test_main_writes_outputs(tmp_path):
    ctx = tmp_path / "ctx.csv"
    sec = tmp_path / "sec.csv"
    summ = tmp_path / "summary.csv"
    md = tmp_path / "rota53.md"
    rc = main(
        [
            str(CORPUS),
            "--n-perm",
            "30",
            "--out-context",
            str(ctx),
            "--out-section",
            str(sec),
            "--out-summary",
            str(summ),
            "--md",
            str(md),
        ]
    )
    assert rc == 0
    for p in (ctx, sec, summ, md):
        assert p.exists() and p.stat().st_size > 0
    assert GUARDRAIL in summ.read_text(encoding="utf-8")
    assert GUARDRAIL in md.read_text(encoding="utf-8")
