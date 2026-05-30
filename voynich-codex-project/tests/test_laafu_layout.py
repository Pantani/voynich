#!/usr/bin/env python3
"""Tests for Rota 67 (scripts/analyze_laafu_layout.py).

Covers the four decisive analyses, the debiased estimator, and the verdict logic
(a pure function of the measured booleans). All tests are deterministic: any
permutation null is seeded.
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from scripts.analyze_laafu_layout import (
    GUARDRAIL,
    R62_BASELINE,
    classify_verdict,
    closure_curve,
    collapse_head_identities,
    is_head_token,
    laafu_I_miller_madow,
    laafu_I_of,
    laafu_I_within_currier,
    main,
    parse_loci_with_section_currier,
    section_invariance,
    token_mi_contributions,
)
from scripts.analyze_language_signature import laafu_pairs, mutual_information

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"


@pytest.fixture(scope="module")
def corpus():
    lines, sections, curriers, folios = parse_loci_with_section_currier(CORPUS)
    return lines, sections, curriers, folios


# --------------------------------------------------------------------------- #
# 1. laafu_pairs / mutual_information reproduce ~0.471 on the real corpus      #
# --------------------------------------------------------------------------- #
def test_laafu_I_reproduces_real_value(corpus):
    """The R62 estimator on the parsed corpus matches the real 0.471 (tol 0.02)."""
    lines, _s, _c, _f = corpus
    laafu = mutual_information(laafu_pairs(lines))
    assert laafu == pytest.approx(0.471, abs=0.02)
    # and the convenience wrapper agrees exactly
    assert laafu_I_of(lines) == pytest.approx(laafu, abs=1e-12)


# --------------------------------------------------------------------------- #
# 2. head-subtraction lowers laafu_I and the function runs                     #
# --------------------------------------------------------------------------- #
def test_head_subtraction_lowers_laafu(corpus):
    """Collapsing HEAD token identities reduces laafu_I (headless < real)."""
    lines, _s, _c, _f = corpus
    real = laafu_I_of(lines)
    headless = laafu_I_of(collapse_head_identities(lines))
    assert headless < real
    # the headless value lands close to the R62 baseline (the head carried the gap)
    assert headless == pytest.approx(R62_BASELINE, abs=0.05)


def test_is_head_token_definition():
    """HEAD = first glyph in {p,t} OR last in {m,g} OR endswith 'dy'; else not."""
    assert is_head_token("pchedy")  # first glyph p
    assert is_head_token("tol")  # first glyph t
    assert is_head_token("cham")  # last glyph m
    assert is_head_token("otorg")  # last glyph g
    assert is_head_token("qokeedy")  # endswith dy
    assert not is_head_token("okain")  # none of the rules
    assert not is_head_token("chol")
    assert not is_head_token("")


def test_collapse_head_preserves_positions(corpus):
    """Collapsing maps HEAD tokens to a placeholder but keeps line geometry."""
    lines, _s, _c, _f = corpus
    collapsed = collapse_head_identities(lines)
    assert len(collapsed) == len(lines)
    assert all(len(a) == len(b) for a, b in zip(collapsed, lines))
    # at least one token actually got collapsed (heads exist in the corpus)
    flat_in = [t for line in lines for t in line]
    flat_out = [t for line in collapsed for t in line]
    assert sum(1 for a, b in zip(flat_in, flat_out) if a != b) > 0


# --------------------------------------------------------------------------- #
# 3. closure curve is monotone non-decreasing and k50<=k70<=k90               #
# --------------------------------------------------------------------------- #
def test_closure_curve_monotone_and_ordered(corpus):
    """Cumulative fraction is monotone non-decreasing; k50 <= k70 <= k90."""
    lines, _s, _c, _f = corpus
    pairs = laafu_pairs(lines)
    contrib = token_mi_contributions(pairs)
    rows, total = closure_curve(contrib)
    # total contribution equals laafu_I (token-wise MI decomposition)
    assert total == pytest.approx(mutual_information(pairs), abs=1e-9)
    fracs = [f for _k, _run, f in rows]
    assert all(fracs[i] <= fracs[i + 1] + 1e-12 for i in range(len(fracs) - 1))
    assert fracs[-1] == pytest.approx(1.0, abs=1e-9)

    from scripts.analyze_laafu_layout import closure_k_at

    k50 = closure_k_at(rows, 0.50)
    k70 = closure_k_at(rows, 0.70)
    k90 = closure_k_at(rows, 0.90)
    assert k50 <= k70 <= k90


# --------------------------------------------------------------------------- #
# 4. section analysis returns finite overlap in [0,1] and a p-value            #
# --------------------------------------------------------------------------- #
def test_section_invariance_returns_finite(corpus):
    """Overlap in [0,1] and a valid p-value in (0,1]; deterministic under seed."""
    lines, sections, _c, folios = corpus
    out = section_invariance(
        lines, sections, folios, top_k=15, min_lines=30, n_perm=200, seed=0
    )
    assert 0.0 <= out["mean_overlap"] <= 1.0
    assert 0.0 < out["js_p"] <= 1.0
    # seeded => reproducible
    out2 = section_invariance(
        lines, sections, folios, top_k=15, min_lines=30, n_perm=200, seed=0
    )
    assert out2["mean_overlap"] == out["mean_overlap"]
    assert out2["js_p"] == out["js_p"]


# --------------------------------------------------------------------------- #
# 5. within-Currier returns two finite values                                 #
# --------------------------------------------------------------------------- #
def test_within_currier_two_values(corpus):
    """laafu_I within A and within B are both finite and computed on real lines."""
    lines, _s, curriers, _f = corpus
    laafu_a, n_a = laafu_I_within_currier(lines, curriers, "A")
    laafu_b, n_b = laafu_I_within_currier(lines, curriers, "B")
    assert n_a > 0 and n_b > 0
    assert laafu_a == laafu_a and laafu_b == laafu_b  # not NaN
    # the binding exists within each mode (above the pooled R62 baseline)
    assert laafu_a > R62_BASELINE
    assert laafu_b > R62_BASELINE


# --------------------------------------------------------------------------- #
# 6. Miller–Madow <= plug-in (correction reduces it) and stays > baseline      #
# --------------------------------------------------------------------------- #
def test_miller_madow_below_plugin_above_baseline(corpus):
    """The debiased laafu_I is <= plug-in and still clears the R62 baseline."""
    lines, _s, _c, _f = corpus
    pairs = laafu_pairs(lines)
    plugin = mutual_information(pairs)
    mm = laafu_I_miller_madow(pairs)
    assert mm <= plugin
    assert mm > R62_BASELINE


# --------------------------------------------------------------------------- #
# 7. verdict is a deterministic function of the booleans (both branches)       #
# --------------------------------------------------------------------------- #
def test_verdict_is_layout_branch():
    """Head explains gap + sparse + invariant => laafu_is_layout."""
    verdict, flags = classify_verdict(
        head_gap_explained_frac=0.95,  # head explains 95% (>=0.70)
        closure_k70=20,  # sparse (<=40)
        section_overlap=0.75,  # high overlap (>=0.60)
        section_js_p=0.40,  # JS within null (>0.05)
    )
    assert verdict == "laafu_is_layout"
    assert flags["layout_head"] and flags["layout_sparse"] and flags["layout_invar"]


def test_verdict_carries_content_branch():
    """Section-specific edges (low overlap + JS beyond null) => laafu_carries_content."""
    verdict, flags = classify_verdict(
        head_gap_explained_frac=0.10,  # head explains little
        closure_k70=2000,  # diffuse
        section_overlap=0.05,  # low overlap (<0.60)
        section_js_p=0.001,  # JS beyond null (<0.01)
    )
    assert verdict == "laafu_carries_content"
    assert flags["content_section"]
    assert not flags["layout_head"]


def test_verdict_mixed_branch():
    """Split evidence (head-yes but not sparse/invariant, JS borderline) => mixed."""
    verdict, _flags = classify_verdict(
        head_gap_explained_frac=0.95,  # layout head
        closure_k70=2000,  # not sparse
        section_overlap=0.02,  # low overlap
        section_js_p=0.02,  # in the ambiguous band (not >0.05, not <0.01)
    )
    assert verdict == "laafu_mixed"


def test_verdict_is_deterministic():
    """Same booleans always yield the same verdict (pure function)."""
    args = dict(
        head_gap_explained_frac=0.95,
        closure_k70=20,
        section_overlap=0.75,
        section_js_p=0.40,
    )
    assert classify_verdict(**args)[0] == classify_verdict(**args)[0] == "laafu_is_layout"


# --------------------------------------------------------------------------- #
# 8. main() writes all 3 CSVs, each carrying GUARDRAIL + required columns      #
# --------------------------------------------------------------------------- #
def test_main_writes_three_csvs(tmp_path):
    """main() emits closure/section/summary CSVs with the guardrail in every row."""
    out_closure = tmp_path / "closure.csv"
    out_section = tmp_path / "section.csv"
    out_summary = tmp_path / "summary.csv"
    rc = main(
        [
            str(CORPUS),
            "--n-perm",
            "50",
            "--seed",
            "0",
            "--out-closure",
            str(out_closure),
            "--out-section",
            str(out_section),
            "--out-summary",
            str(out_summary),
        ]
    )
    assert rc == 0
    for path in (out_closure, out_section, out_summary):
        assert path.exists()

    # closure: required columns + guardrail + monotone fraction
    with out_closure.open() as f:
        crows = list(csv.DictReader(f))
    assert crows
    assert {"k", "token", "token_contrib_bits", "cumulative_bits", "cumulative_frac"} <= set(
        crows[0]
    )
    assert all(r["semantic_guardrail"] == GUARDRAIL for r in crows)
    cf = [float(r["cumulative_frac"]) for r in crows]
    assert all(cf[i] <= cf[i + 1] + 1e-9 for i in range(len(cf) - 1))

    # section: required columns + guardrail; has both row types
    with out_section.open() as f:
        srows = list(csv.DictReader(f))
    assert srows
    assert {"row_type", "section_a", "section_b", "jaccard_first", "jaccard_last"} <= set(
        srows[0]
    )
    assert all(r["semantic_guardrail"] == GUARDRAIL for r in srows)
    assert {r["row_type"] for r in srows} == {"section", "pair"}

    # summary: required metrics present + guardrail row + verdict in the allowed set
    with out_summary.open() as f:
        mrows = list(csv.DictReader(f))
    metrics = {r["metric"]: r["value"] for r in mrows}
    required = {
        "laafu_real",
        "laafu_r62_baseline",
        "laafu_miller_madow",
        "laafu_headless",
        "head_gap_explained_frac",
        "closure_k50",
        "closure_k70",
        "closure_k90",
        "section_top_overlap",
        "section_js_p_vs_null",
        "laafu_I_currierA",
        "laafu_I_currierB",
        "verdict",
        "caveat",
        "guardrail",
    }
    assert required <= set(metrics)
    assert metrics["guardrail"] == GUARDRAIL
    assert metrics["verdict"] in {
        "laafu_is_layout",
        "laafu_carries_content",
        "laafu_mixed",
    }
    assert metrics["laafu_r62_baseline"] == str(R62_BASELINE)


# --------------------------------------------------------------------------- #
# 9. golden-rule guard: no decipherment language in verdict / summary          #
# --------------------------------------------------------------------------- #
def test_golden_rule_no_decipherment_language(tmp_path):
    """Verdict + summary must not claim meaning ('means'/'translates to')."""
    out_summary = tmp_path / "summary.csv"
    main(
        [
            str(CORPUS),
            "--n-perm",
            "50",
            "--out-closure",
            str(tmp_path / "c.csv"),
            "--out-section",
            str(tmp_path / "s.csv"),
            "--out-summary",
            str(out_summary),
        ]
    )
    with out_summary.open() as f:
        mrows = list(csv.DictReader(f))
    metrics = {r["metric"]: r["value"] for r in mrows}
    # the verdict label itself never asserts meaning
    assert metrics["verdict"] in {
        "laafu_is_layout",
        "laafu_carries_content",
        "laafu_mixed",
    }
    # forbidden decipherment phrasings: a token/word being GIVEN a gloss. (The
    # mandated caveat uses "means" benignly — "'laafu_is_layout' means ..." — so
    # we ban only the token->gloss assertion patterns, not the word "means".)
    banned = ("translates to", "decoded as", "stands for", "means the word")
    blob = (metrics["verdict"] + " " + metrics["caveat"]).lower()
    for phrase in banned:
        assert phrase not in blob
    # the caveat explicitly disclaims decipherment
    assert "not a decipherment" in metrics["caveat"].lower()


def test_guardrail_value_is_pinned():
    """The guardrail constant follows the {desc}_not_decipherment convention."""
    assert GUARDRAIL == "rota67_laafu_layout_not_decipherment"
    assert GUARDRAIL.endswith("_not_decipherment")
