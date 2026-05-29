"""Tests for Rota 57 word grounding (scripts/analyze_word_grounding.py).

Settles whether the Rota-56 section-diagnostic words are REFERENTIAL (name
depicted objects -> label-bound + folio-concentrated) or PROSE-REGISTER (spread
across many folios' running text, low label_frac).

Covers: SYNTHETIC known-answer cases — a fabricated "label-bound, single-folio"
word (label_frac=1, low folio entropy, name-like) and a "spread paragraph" word
(low label_frac, high folio entropy); folio_entropy_norm correctness; label_frac /
para_frac correctness; the diagnostic-set selection (top-N by lift_S per section);
the permutation comparison of the mean difference; the verdict logic; and the real
corpus integration with both CSVs + guardrail and the ~37671 token sanity check.
"""
from __future__ import annotations

import collections
import csv
import math
from pathlib import Path

from scripts.analyze_word_grounding import (
    GUARDRAIL,
    build,
    decide_verdict,
    diagnostic_set,
    entropy,
    main,
    perm_test_mean_diff,
    top_lift_by_section,
    word_grounding_metrics,
)
from scripts.analyze_nucleus_context import parse_corpus_with_kind

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"


# --------------------------------------------------------------------------
# Entropy correctness
# --------------------------------------------------------------------------
def test_entropy_known_values():
    assert abs(entropy([1, 1, 1, 1]) - 2.0) < 1e-9  # uniform over 4 -> 2 bits
    assert entropy([10]) == 0.0  # degenerate -> 0
    assert entropy([]) == 0.0  # empty -> 0
    assert abs(entropy([5, 5]) - 1.0) < 1e-9  # fair coin -> 1 bit


# --------------------------------------------------------------------------
# SYNTHETIC known-answer: a label-bound single-folio NAME vs a spread PROSE word
# --------------------------------------------------------------------------
def test_synthetic_label_bound_single_folio_word_is_name_like():
    # 'objname' occurs 25x, ALL on one folio, ALL in label loci -> referential
    # signature: label_frac=1, folio_entropy_norm=0 (single folio), top_share=1.
    records = [("f80r", "L", "objname")] * 25
    m = word_grounding_metrics(records, min_freq=20)["objname"]
    assert m["label_frac"] == 1.0
    assert m["para_frac"] == 0.0
    assert m["folio_entropy_norm"] == 0.0  # one folio -> fully concentrated
    assert m["top_folio_share"] == 1.0
    assert m["n_folios"] == 1


def test_synthetic_spread_paragraph_word_is_prose_like():
    # 'prosey' occurs 5x on each of 8 folios, ALL in paragraph loci -> prose
    # signature: label_frac=0, folio_entropy_norm=1 (evenly spread), low top_share.
    records = []
    for i in range(8):
        records += [(f"f{10 + i}r", "P", "prosey")] * 5
    m = word_grounding_metrics(records, min_freq=20)["prosey"]
    assert m["label_frac"] == 0.0
    assert m["para_frac"] == 1.0
    assert abs(m["folio_entropy_norm"] - 1.0) < 1e-9  # 8 folios, even -> norm 1
    assert abs(m["top_folio_share"] - (5 / 40)) < 1e-9  # 0.125
    assert m["n_folios"] == 8


# --------------------------------------------------------------------------
# folio_entropy_norm correctness on a known skewed distribution
# --------------------------------------------------------------------------
def test_folio_entropy_norm_normalization():
    # 'w' appears on 2 folios: 30x and 10x => H = -(.75log2.75 + .25log2.25),
    # normalized by log2(2)=1, so folio_entropy_norm == that H exactly.
    records = [("fa", "P", "w")] * 30 + [("fb", "P", "w")] * 10
    m = word_grounding_metrics(records, min_freq=20)["w"]
    expected_h = -(0.75 * math.log2(0.75) + 0.25 * math.log2(0.25))
    assert abs(m["folio_entropy_norm"] - expected_h) < 1e-9
    assert abs(m["top_folio_share"] - 0.75) < 1e-9
    # min_freq gate: a freq-19 word is dropped
    recs2 = [("fa", "P", "w")] * 19
    assert "w" not in word_grounding_metrics(recs2, min_freq=20)


# --------------------------------------------------------------------------
# label_frac / para_frac correctness with mixed kinds
# --------------------------------------------------------------------------
def test_label_and_para_frac_with_mixed_kinds():
    # 12 label + 6 paragraph + 2 circular = 20 occurrences across folios.
    records = (
        [("fa", "L", "mix")] * 12
        + [("fb", "P", "mix")] * 6
        + [("fc", "C", "mix")] * 2
    )
    m = word_grounding_metrics(records, min_freq=20)["mix"]
    assert abs(m["label_frac"] - 12 / 20) < 1e-9
    assert abs(m["para_frac"] - 6 / 20) < 1e-9
    # label_frac + para_frac need not sum to 1 (circular/other excluded)
    assert m["label_frac"] + m["para_frac"] < 1.0


# --------------------------------------------------------------------------
# Diagnostic-set selection: top-N by lift_S per section, pooled
# --------------------------------------------------------------------------
def test_top_lift_by_section_matches_definition():
    # 100 tokens, 50 herbal / 50 recipes. 'wa' freq 40: 30 herbal, 10 recipes
    # => P(herbal|wa)=.75 / P(herbal)=.5 => lift_herbal=1.5.
    pairs = (
        [("wa", "herbal")] * 30
        + [("wa", "recipes")] * 10
        + [("filler", "herbal")] * 20
        + [("filler", "recipes")] * 40
    )
    tops = top_lift_by_section(pairs, ["herbal"], min_freq=20, top_n=5)
    assert ("wa", 40, 1.5) in tops["herbal"]


def test_diagnostic_set_picks_top_per_section_and_pools():
    # Two clean sections; per-section the most section-skewed freq>=20 words win.
    pairs = (
        [("h_word", "herbal")] * 40           # pure herbal -> top herbal
        + [("r_word", "recipes")] * 40        # pure recipes -> top recipes
        + [("flat", "herbal")] * 25 + [("flat", "recipes")] * 25  # flat, not diag
    )
    diag, word_sec = diagnostic_set(pairs, ["herbal", "recipes"], min_freq=20, top_n=1)
    assert diag == {"h_word", "r_word"}  # top-1 of each section, pooled
    assert word_sec["h_word"] == "herbal" and word_sec["r_word"] == "recipes"
    assert "flat" not in diag  # the section-flat word is NOT diagnostic


# --------------------------------------------------------------------------
# Permutation comparison of the mean difference
# --------------------------------------------------------------------------
def test_perm_test_mean_diff_detects_real_separation():
    # Cleanly separated groups -> large observed diff, small permutation p.
    group_a = [1.0] * 30  # e.g. label-bound diagnostic words
    group_b = [0.0] * 30  # prose baseline words
    diff, mean_a, p = perm_test_mean_diff(group_a, group_b, n_perm=500, seed=1)
    assert abs(diff - 1.0) < 1e-9
    assert abs(mean_a - 1.0) < 1e-9
    assert p < 0.01


def test_perm_test_mean_diff_no_separation_is_nonsignificant():
    # Identical distributions -> diff ~ 0, p large (not significant).
    group_a = [0.3, 0.5, 0.7] * 10
    group_b = [0.3, 0.5, 0.7] * 10
    diff, _mean_a, p = perm_test_mean_diff(group_a, group_b, n_perm=500, seed=2)
    assert abs(diff) < 1e-9
    assert p > 0.2
    # empty group -> NaN p (defensive)
    _d, _m, pnan = perm_test_mean_diff([], [1.0, 2.0], n_perm=100, seed=0)
    assert math.isnan(pnan)


# --------------------------------------------------------------------------
# Verdict logic — the three encoded outcomes
# --------------------------------------------------------------------------
def test_decide_verdict_referential():
    # diag label_frac >> corpus baseline (0.40 vs 0.05 = 8x), folio-concentrated
    # (lower entropy, higher top_share), many label-dominant (10/15).
    v = decide_verdict(
        corpus_label_frac=0.05,
        diag_label_frac=0.40,
        base_label_frac=0.05,
        diag_folio_entropy=0.40,
        base_folio_entropy=0.80,
        diag_top_share=0.60,
        base_top_share=0.30,
        n_diag_label_dominant=10,
        n_diag=15,
        n_diag_folio_concentrated=9,
    )
    assert v == "referential"


def test_decide_verdict_prose_register():
    # diag label_frac ~ corpus baseline (not inflated, mostly paragraph), highly
    # spread (entropy ~ baseline and >= 0.75), zero label-dominant / concentrated.
    v = decide_verdict(
        corpus_label_frac=0.05,
        diag_label_frac=0.05,
        base_label_frac=0.05,
        diag_folio_entropy=0.95,
        base_folio_entropy=0.96,
        diag_top_share=0.12,
        base_top_share=0.09,
        n_diag_label_dominant=0,
        n_diag=15,
        n_diag_folio_concentrated=0,
    )
    assert v == "prose_register"


def test_decide_verdict_prose_register_holds_when_top_share_slightly_above_baseline():
    # REGRESSION for the real-corpus case: diagnostics have a marginally HIGHER
    # top_folio_share than the all-other-words baseline (0.122 vs 0.086) yet both
    # are far below the 0.5 concentration line and entropy is ~1 -> still prose,
    # NOT mixed. A tiny top_share gap must not flip the verdict.
    v = decide_verdict(
        corpus_label_frac=0.0273,
        diag_label_frac=0.0264,
        base_label_frac=0.0146,
        diag_folio_entropy=0.9562,
        base_folio_entropy=0.9622,
        diag_top_share=0.1222,
        base_top_share=0.0860,
        n_diag_label_dominant=0,
        n_diag=75,
        n_diag_folio_concentrated=0,
    )
    assert v == "prose_register"


def test_decide_verdict_mixed():
    # Elevated label_frac (inflated above corpus baseline) but spread across folios
    # and few label-dominant -> neither clean referential nor clean prose -> mixed.
    v = decide_verdict(
        corpus_label_frac=0.05,
        diag_label_frac=0.12,
        base_label_frac=0.05,
        diag_folio_entropy=0.85,
        base_folio_entropy=0.80,
        diag_top_share=0.25,
        base_top_share=0.30,
        n_diag_label_dominant=1,
        n_diag=15,
        n_diag_folio_concentrated=0,
    )
    assert v == "mixed"


# --------------------------------------------------------------------------
# build() integration on a controlled mini-corpus
# --------------------------------------------------------------------------
def test_build_separates_diagnostic_from_baseline():
    # herbal folios carry 'hword' (paragraph), recipes folios carry 'rword'
    # (paragraph), plus a section-flat 'flat' everywhere -> diag = {hword, rword}.
    records = []
    for i in range(3):  # herbal folios f1..f3 (classify_section: 1..66 -> herbal)
        records += [(f"f{i + 1}r", "P", "hword")] * 30
        records += [(f"f{i + 1}r", "P", "flat")] * 20
    for i in range(3):  # recipes folios f103..f105 (103..116 -> recipes)
        records += [(f"f{103 + i}r", "P", "rword")] * 30
        records += [(f"f{103 + i}r", "P", "flat")] * 20
    b = build(records, min_freq=20, top_n=1)
    assert "hword" in b["diag_words"] and "rword" in b["diag_words"]
    assert "flat" not in b["diag_words"]
    # corpus_label_frac is 0 here (no label loci) and token coverage counts all
    assert b["corpus_label_frac"] == 0.0
    assert b["token_coverage"] == len(records)
    # every diag row carries the guardrail and an is_diagnostic flag
    assert all(r["semantic_guardrail"] == GUARDRAIL for r in b["diag_rows"])
    assert {r["is_diagnostic"] for r in b["diag_rows"]} <= {0, 1}


# --------------------------------------------------------------------------
# Real corpus sanity: token coverage matches Rota 56 (~37671)
# --------------------------------------------------------------------------
def test_real_corpus_token_coverage_matches_rota56():
    records = parse_corpus_with_kind(CORPUS)
    b = build(records, min_freq=20, top_n=15)
    # section-known token coverage must equal the Rota 56 figure
    assert b["token_coverage"] == 37671
    # diagnostic set is non-empty and a strict subset of all freq>=20 types
    assert b["diag_words"]
    all_types = {r["word"] for r in b["diag_rows"]}
    assert b["diag_words"] < all_types
    # the diagnostic pool is at most 5 sections * 15 = 75 words
    assert len(b["diag_words"]) <= 75


# --------------------------------------------------------------------------
# main writes both CSVs with the guardrail and the required summary metrics
# --------------------------------------------------------------------------
def test_main_writes_both_csvs_with_guardrail(tmp_path):
    grounding = tmp_path / "grounding.csv"
    summ = tmp_path / "summary.csv"
    rc = main(
        [
            str(CORPUS),
            "--n-perm",
            "200",
            "--out-grounding",
            str(grounding),
            "--out-summary",
            str(summ),
        ]
    )
    assert rc == 0
    for p in (grounding, summ):
        assert p.exists() and p.stat().st_size > 0
        assert GUARDRAIL in p.read_text(encoding="utf-8")
    # grounding CSV has exactly the required columns
    grows = list(csv.DictReader(grounding.open(encoding="utf-8")))
    assert grows
    assert set(grows[0].keys()) == {
        "word",
        "section",
        "is_diagnostic",
        "freq",
        "label_frac",
        "para_frac",
        "folio_entropy_norm",
        "top_folio_share",
        "semantic_guardrail",
    }
    # summary has all the required metrics
    rows = list(csv.DictReader(summ.open(encoding="utf-8")))
    metrics = {r["metric"]: r["value"] for r in rows}
    for required in (
        "corpus_label_frac",
        "diag_mean_label_frac",
        "base_mean_label_frac",
        "diag_mean_folio_entropy",
        "base_mean_folio_entropy",
        "diag_mean_top_folio_share",
        "base_mean_top_folio_share",
        "n_diag_label_dominant",
        "n_diag_folio_concentrated",
        "perm_p_label_frac_diff",
        "verdict",
        "guardrail",
    ):
        assert required in metrics
    assert metrics["guardrail"] == GUARDRAIL
    assert metrics["verdict"] in {"referential", "prose_register", "mixed"}
    # there is at least one diagnostic and one baseline word
    flags = [int(r["is_diagnostic"]) for r in grows]
    assert sum(flags) >= 1 and (len(flags) - sum(flags)) >= 1
