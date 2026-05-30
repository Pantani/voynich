"""Tests for analyze_codicology.py (Rota 68).

Object-level production analysis from IVTFF per-folio metadata: folio ordering,
Currier-block contiguity + permutation null, section/hand x Currier alignment,
quire mapping, and a verdict that is a PURE FUNCTION of measured booleans. Every
assertion is about how the codex was MADE -- never about meaning (golden rule).
"""
from __future__ import annotations

import csv
from pathlib import Path

import pytest

from scripts.analyze_codicology import (
    DEFAULT_CORPUS,
    GUARDRAIL,
    classify_verdict,
    count_runs,
    cramer_v,
    cross_tab,
    currier_label,
    folio_sort_key,
    main,
    mean_run_length,
    parse_args,
    parse_folio_metadata,
    permutation_p_fewer_runs,
    section_label,
)
from scripts import analyze_nucleus


# --------------------------------------------------------------------------- #
# Canonical folio sort                                                         #
# --------------------------------------------------------------------------- #
def test_folio_sort_f2r_before_f10r_before_f10v():
    folios = ["f10v", "f10r", "f2r", "f1v", "f1r"]
    ordered = sorted(folios, key=folio_sort_key)
    assert ordered == ["f1r", "f1v", "f2r", "f10r", "f10v"]


def test_folio_sort_recto_before_verso_and_foldout_subleaf():
    # r before v within a folio; foldout sub-leaf orders after lower/absent digit
    folios = ["f67v1", "f67r2", "f67r1", "f68r1"]
    ordered = sorted(folios, key=folio_sort_key)
    assert ordered == ["f67r1", "f67r2", "f67v1", "f68r1"]
    # numeric, not lexical: f10 after f9
    assert folio_sort_key("f9r") < folio_sort_key("f10r")


# --------------------------------------------------------------------------- #
# IVTFF Currier parse matches the reused mechanism                             #
# --------------------------------------------------------------------------- #
def test_currier_parse_matches_analyze_nucleus_on_sample():
    meta = parse_folio_metadata(DEFAULT_CORPUS)
    folio_currier, _ = analyze_nucleus.parse_corpus(DEFAULT_CORPUS)
    # folios that DO carry $L in the header
    sample = ["f1r", "f1v", "f9r", "f75r", "f103r"]
    for f in sample:
        # both derive Currier from the same $L= header tag
        assert currier_label(meta[f]) in ("A", "B")
        # analyze_nucleus stores the raw $L char; ours normalises A/B vs unknown
        assert meta[f]["L"] == folio_currier[f]


def test_missing_currier_degrades_gracefully():
    # f67r1 genuinely has NO $L tag in ZL3b -> reported as 'unknown', not crash.
    meta = parse_folio_metadata(DEFAULT_CORPUS)
    assert "L" not in meta["f67r1"]
    assert currier_label(meta["f67r1"]) == "unknown"


def test_metadata_parse_extracts_expected_tags():
    meta = parse_folio_metadata(DEFAULT_CORPUS)
    # f1r header: $Q=A $P=A $F=a $B=1 $I=T $L=A $H=1 $C=1 $X=V
    assert meta["f1r"]["Q"] == "A"
    assert meta["f1r"]["L"] == "A"
    assert meta["f1r"]["H"] == "1"
    assert meta["f1r"]["I"] == "T"
    assert section_label(meta["f1r"]) == "text_only"
    assert section_label(meta["f1v"]) == "herbal"  # $I=H


# --------------------------------------------------------------------------- #
# Run counting on tiny synthetic sequences                                     #
# --------------------------------------------------------------------------- #
def test_count_runs_tiny_synthetic():
    assert count_runs([]) == 0
    assert count_runs(["A"]) == 1
    assert count_runs(["A", "A", "A"]) == 1
    assert count_runs(["A", "A", "B", "A"]) == 3
    assert count_runs(["A", "B", "A", "B"]) == 4


def test_mean_run_length():
    assert mean_run_length(["A", "A", "B", "A"]) == pytest.approx(4 / 3)
    assert mean_run_length(["A", "A", "A", "A"]) == 4.0
    assert mean_run_length([]) == 0.0


# --------------------------------------------------------------------------- #
# Permutation null: determinism, range, and blocked < random                  #
# --------------------------------------------------------------------------- #
def test_permutation_null_deterministic_and_in_range():
    labels = ["A"] * 10 + ["B"] * 10
    p1, mean1, obs1 = permutation_p_fewer_runs(labels, n_perm=500, seed=7)
    p2, mean2, obs2 = permutation_p_fewer_runs(labels, n_perm=500, seed=7)
    assert (p1, mean1, obs1) == (p2, mean2, obs2)  # deterministic under seed
    assert 0.0 <= p1 <= 1.0
    # different seed may differ but still a valid probability
    p3, _, _ = permutation_p_fewer_runs(labels, n_perm=500, seed=8)
    assert 0.0 <= p3 <= 1.0


def test_blocked_sequence_has_fewer_runs_than_random():
    # perfectly blocked: 2 runs, far below the null mean -> small p
    blocked = ["A"] * 50 + ["B"] * 50
    p_blocked, mean_null, obs = permutation_p_fewer_runs(blocked, n_perm=1000, seed=1)
    assert obs == 2
    assert obs < mean_null
    assert p_blocked < 0.05
    # an already-random/alternating sequence is NOT significantly blocked
    alternating = ["A", "B"] * 50
    p_alt, _, obs_alt = permutation_p_fewer_runs(alternating, n_perm=1000, seed=1)
    assert obs_alt == 100
    assert p_alt > 0.05


def test_permutation_p_degenerate_single_label():
    # one distinct label -> no meaningful shuffle; p defined as 1.0
    p, mean_null, obs = permutation_p_fewer_runs(["A"] * 8, n_perm=100, seed=3)
    assert p == 1.0
    assert obs == 1


# --------------------------------------------------------------------------- #
# Cramer's V range + real cross-tab                                            #
# --------------------------------------------------------------------------- #
def test_cramer_v_in_unit_interval_on_real_crosstab():
    meta = parse_folio_metadata(DEFAULT_CORPUS)
    rows = [
        {
            "section": section_label(t),
            "currier": currier_label(t),
            "hand": t.get("H", "unknown"),
        }
        for t in meta.values()
    ]
    tab = cross_tab(rows, "section", "currier", exclude={"unknown"})
    v, n = cramer_v(tab)
    assert 0.0 <= v <= 1.0
    assert n > 0


def test_cramer_v_perfect_association_is_one():
    # section deterministically predicts currier -> V == 1
    table = {
        "herbal": __import__("collections").Counter({"A": 10}),
        "balneo": __import__("collections").Counter({"B": 10}),
    }
    v, n = cramer_v(table)
    assert v == pytest.approx(1.0)
    assert n == 20


# --------------------------------------------------------------------------- #
# Coverage counts are bounded by n_folios                                      #
# --------------------------------------------------------------------------- #
def test_coverage_counts_le_n_folios(tmp_path):
    args = parse_args(
        [
            str(DEFAULT_CORPUS),
            "--n-perm",
            "50",
            "--out-summary",
            str(tmp_path / "s.csv"),
            "--out-runs",
            str(tmp_path / "r.csv"),
            "--out-alignment",
            str(tmp_path / "a.csv"),
            "--md",
            str(tmp_path / "d.md"),
        ]
    )
    rc = main(
        [
            str(DEFAULT_CORPUS),
            "--n-perm",
            "50",
            "--out-summary",
            str(args.out_summary),
            "--out-runs",
            str(args.out_runs),
            "--out-alignment",
            str(args.out_alignment),
            "--md",
            str(args.md),
        ]
    )
    assert rc == 0
    summary = {
        r["metric"]: r["value"]
        for r in csv.DictReader(Path(args.out_summary).open(encoding="utf-8"))
    }
    n = int(summary["n_folios"])
    for k in ("coverage_L", "coverage_Q", "coverage_H", "coverage_I"):
        assert 0 <= int(summary[k]) <= n
    # A + B counts cannot exceed Currier coverage
    assert int(summary["n_currier_A"]) + int(summary["n_currier_B"]) == int(
        summary["coverage_L"]
    )


# --------------------------------------------------------------------------- #
# Verdict is deterministic from booleans (both branches)                       #
# --------------------------------------------------------------------------- #
def test_verdict_planned_blocked_requires_both_booleans():
    assert classify_verdict(True, True) == "planned_blocked_codex"


def test_verdict_interleaved_when_either_boolean_false():
    assert classify_verdict(True, False) == "interleaved_production"
    assert classify_verdict(False, True) == "interleaved_production"
    assert classify_verdict(False, False) == "interleaved_production"


# --------------------------------------------------------------------------- #
# main() writes all 3 CSVs, each carrying the guardrail                        #
# --------------------------------------------------------------------------- #
def test_main_writes_three_csvs_with_guardrail(tmp_path):
    out_runs = tmp_path / "runs.csv"
    out_align = tmp_path / "align.csv"
    out_summary = tmp_path / "summary.csv"
    md = tmp_path / "doc.md"
    rc = main(
        [
            str(DEFAULT_CORPUS),
            "--n-perm",
            "50",
            "--out-runs",
            str(out_runs),
            "--out-alignment",
            str(out_align),
            "--out-summary",
            str(out_summary),
            "--md",
            str(md),
        ]
    )
    assert rc == 0
    for path in (out_runs, out_align, out_summary):
        assert path.exists()
        rows = list(csv.DictReader(path.open(encoding="utf-8")))
        assert rows, f"{path} is empty"
        # every row carries the guardrail (summary carries it as a metric row)
        if "semantic_guardrail" in rows[0]:
            assert all(r["semantic_guardrail"] == GUARDRAIL for r in rows)
        else:
            vals = {r["metric"]: r["value"] for r in rows}
            assert vals["guardrail"] == GUARDRAIL


def test_summary_verdict_consistent_with_its_booleans(tmp_path):
    out_summary = tmp_path / "summary.csv"
    rc = main(
        [
            str(DEFAULT_CORPUS),
            "--n-perm",
            "200",
            "--out-runs",
            str(tmp_path / "r.csv"),
            "--out-alignment",
            str(tmp_path / "a.csv"),
            "--out-summary",
            str(out_summary),
            "--md",
            str(tmp_path / "d.md"),
        ]
    )
    assert rc == 0
    vals = {
        r["metric"]: r["value"]
        for r in csv.DictReader(out_summary.open(encoding="utf-8"))
    }
    blocked = vals["currier_blocked"] == "True"
    aligns = vals["changes_align_quires"] == "True"
    assert vals["verdict"] == classify_verdict(blocked, aligns)
    # p in [0,1]; coverage_L well populated (the documented minimum)
    p = float(vals["currier_runs_p_vs_null"])
    assert 0.0 <= p <= 1.0
    assert int(vals["coverage_L"]) >= 100


# --------------------------------------------------------------------------- #
# Golden rule: no meaning words in the verdict/summary text                    #
# --------------------------------------------------------------------------- #
def test_golden_rule_no_meaning_words(tmp_path):
    out_summary = tmp_path / "summary.csv"
    md = tmp_path / "doc.md"
    main(
        [
            str(DEFAULT_CORPUS),
            "--n-perm",
            "50",
            "--out-runs",
            str(tmp_path / "r.csv"),
            "--out-alignment",
            str(tmp_path / "a.csv"),
            "--out-summary",
            str(out_summary),
            "--md",
            str(md),
        ]
    )
    # Affirmative meaning-claim phrases that must never appear. (The literal
    # "decipher" is intentionally NOT banned: it occurs only inside the guardrail
    # negation "not_decipherment"; we assert that negation is intact below.)
    banned = (" means ", "translates to", "meaning of", "stands for")
    text = out_summary.read_text(encoding="utf-8").lower()
    for b in banned:
        assert b not in text
    assert "not_decipherment" in text  # guardrail negation present, not a claim
    # verdict values themselves are production-only labels
    assert any(
        v in text
        for v in ("planned_blocked_codex", "interleaved_production")
    )
    # the caveat explicitly disclaims meaning
    assert "says nothing about meaning" in text
    # guardrail present
    assert GUARDRAIL in text
