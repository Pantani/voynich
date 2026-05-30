"""Tests for Rota 71 Hebrew alphagram + abjad attack (analyze_hebrew_alphagram.py).

The decisive structural claim of Kondrak & Hauer (2018) is that every Voynich word
is an ALPHAGRAM (its letters re-sorted into one fixed alphabetic order). That is a
TOTAL-ORDER claim, so it is checked three independent ways:
  - alphagram_fraction (tokens non-decreasing under a best order),
  - pair_decidedness (every glyph pair strictly ordered),  ORDER-FREE
  - majority_cycles (a total order is acyclic -> 0).        ORDER-FREE, an
    impossibility proof when > 0.
The order-free measures are pinned on hand-built corpora with known answers; the
real-corpus assertions confirm the refutation (far from the alphagram ceiling, lift
reproduced by the generator) without asserting any decipherment.
"""
from __future__ import annotations

import collections
import csv
import random
from pathlib import Path

from scripts.analyze_hebrew_alphagram import (
    ALPHAGRAM_PASS,
    GUARDRAIL,
    MIN_PAIR,
    STRICT_MAJORITY,
    alphagram_battery,
    alphagram_fraction,
    char_units,
    classify_verdict,
    glyph_units,
    infer_order,
    main,
    majority_cycles,
    pair_decidedness,
    pair_order_counts,
    run,
    sort_words,
    spearman,
    strip_vowels,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"


# --------------------------------------------------------------------------- #
# Tokenisation                                                                #
# --------------------------------------------------------------------------- #
def test_char_units_is_one_char_per_unit():
    assert char_units("qokeey") == list("qokeey")
    assert char_units("") == []


def test_glyph_units_merges_eva_digraphs():
    # ch, sh and benched gallows are single glyphs; everything else is one char
    assert glyph_units("chol") == ["ch", "o", "l"]
    assert glyph_units("shey") == ["sh", "e", "y"]
    assert glyph_units("qokeey") == ["q", "o", "k", "e", "e", "y"]
    assert glyph_units("cthy") == ["cth", "y"]  # longest-match: cth before ch
    assert glyph_units("ckhdy") == ["ckh", "d", "y"]


# --------------------------------------------------------------------------- #
# Order inference                                                             #
# --------------------------------------------------------------------------- #
def test_infer_order_recovers_a_clean_total_order():
    # every word is a prefix of "abcd" -> mean positions strictly increasing
    toks = ["ab", "abc", "abcd", "bcd", "cd"] * 4
    order = infer_order(toks, char_units)
    assert order == ["a", "b", "c", "d"]


def test_alphagram_fraction_one_on_sorted_zero_on_reversed():
    order = ["a", "b", "c", "d"]
    assert alphagram_fraction(["abc", "abd", "acd"], order, char_units) == 1.0
    # strictly decreasing words are never non-decreasing
    assert alphagram_fraction(["ba", "dc", "cb"], order, char_units) == 0.0


def test_sort_words_hits_the_ceiling():
    order = ["a", "b", "c", "d"]
    toks = ["dca", "bda", "cab"]
    srt = sort_words(toks, order, char_units)
    assert srt == ["acd", "abd", "abc"]
    assert alphagram_fraction(srt, order, char_units) == 1.0


# --------------------------------------------------------------------------- #
# Pairwise order / decidedness / cycles (order-free, the robust discriminators)
# --------------------------------------------------------------------------- #
def test_pair_order_counts_on_known_word():
    pc = pair_order_counts(["abc"], char_units)
    assert pc[("a", "b")] == 1 and pc[("a", "c")] == 1 and pc[("b", "c")] == 1
    assert pc[("b", "a")] == 0


def test_pair_decidedness_one_for_total_order_zero_for_ambiguous():
    pc = pair_order_counts(["abc"] * MIN_PAIR, char_units)
    d = pair_decidedness(pc, MIN_PAIR, STRICT_MAJORITY)
    assert d["decided_frac"] == 1.0 and d["weighted_majority"] == 1.0
    # equal both-direction evidence -> nothing decided
    pc2 = pair_order_counts(["ab"] * MIN_PAIR + ["ba"] * MIN_PAIR, char_units)
    d2 = pair_decidedness(pc2, MIN_PAIR, STRICT_MAJORITY)
    assert d2["decided_frac"] == 0.0
    assert abs(d2["weighted_majority"] - 0.5) < 1e-9


def test_majority_cycles_zero_for_dag_positive_for_cycle():
    # consistent order a<b<c -> acyclic
    dag = pair_order_counts(["abc"] * MIN_PAIR, char_units)
    assert majority_cycles(dag, MIN_PAIR) == 0
    # a<b, b<c, c<a -> one 3-cycle (no total order can exist)
    cyc = pair_order_counts(["ab"] * MIN_PAIR + ["bc"] * MIN_PAIR + ["ca"] * MIN_PAIR,
                            char_units)
    assert majority_cycles(cyc, MIN_PAIR) == 1


def test_strip_vowels_removes_candidate_vowels():
    # ABJAD_VOWELS = a,o,e,y
    assert strip_vowels(["qokeedy"], frozenset("aoey"), char_units) == ["qkd"]
    assert strip_vowels(["aoey"], frozenset("aoey"), char_units) == []  # all-vowel dropped


def test_spearman_monotonic_and_reversed():
    assert abs(spearman([1, 2, 3, 4], [10, 20, 30, 40]) - 1.0) < 1e-9
    assert abs(spearman([1, 2, 3, 4], [40, 30, 20, 10]) + 1.0) < 1e-9


# --------------------------------------------------------------------------- #
# Verdict logic                                                               #
# --------------------------------------------------------------------------- #
def _battery(af, dec, cyc):
    return {"alphagram_fraction": af, "decided_frac": dec, "weighted_majority": 0.8,
            "majority_cycles": cyc, "n_pairs": 100, "mean_units": 5.0}


def test_classify_refutes_when_far_from_ceiling():
    real = _battery(0.27, 0.35, 15)
    floor = _battery(0.06, 0.00, 191)
    ceil = _battery(1.0, 1.0, 0)
    gen = _battery(0.28, 0.39, 12)          # generator reproduces the lift
    abjad = _battery(0.47, 0.42, 3)
    verdict, reasons = classify_verdict(real, floor, ceil, gen, abjad, freq_tie=True)
    assert verdict == "hebrew_alphagram_refuted"
    assert any("no_total_order_exists" in r for r in reasons)
    assert any("reproduced_by_generator" in r for r in reasons)


def test_classify_would_accept_a_true_alphagram():
    # a corpus that really is an alphagram AND not reproduced by the generator
    real = _battery(0.98, 0.99, 0)
    floor = _battery(0.05, 0.00, 150)
    ceil = _battery(1.0, 1.0, 0)
    gen = _battery(0.30, 0.40, 10)          # generator does NOT reach it
    abjad = _battery(0.98, 0.99, 0)
    verdict, _ = classify_verdict(real, floor, ceil, gen, abjad, freq_tie=False)
    assert verdict == "alphagram_compatible"


# --------------------------------------------------------------------------- #
# Real corpus: the refutation holds                                           #
# --------------------------------------------------------------------------- #
def test_real_corpus_refutes_alphagram():
    res = run(CORPUS, seed=70)
    assert res["n_tokens"] == 37671  # reproduces Rota 53/57/58 token universe
    real, floor, ceil = res["real"], res["floor"], res["ceiling"]
    # ceiling is a true alphagram by construction
    assert abs(ceil["alphagram_fraction"] - 1.0) < 1e-9
    assert ceil["majority_cycles"] == 0
    # real sits well below the ceiling and above the shuffle floor
    assert floor["alphagram_fraction"] < real["alphagram_fraction"] < 0.5
    assert real["decided_frac"] < ALPHAGRAM_PASS
    # the impossibility proof: at least one majority cycle -> no total order
    assert real["majority_cycles"] > 0
    assert res["verdict"] == "hebrew_alphagram_refuted"


def test_generator_reproduces_the_order_lift():
    res = run(CORPUS, seed=70)
    # the modest order-consistency lift is within-word morphology the content-free
    # generator reproduces -> not evidence of an alphabetic re-sorting
    assert abs(res["real"]["alphagram_fraction"]
               - res["generator_base"]["alphagram_fraction"]) < 0.05


def test_glyph_unit_pass_also_refutes():
    res = run(CORPUS, seed=70)
    assert res["glyph_real"]["decided_frac"] < ALPHAGRAM_PASS
    assert res["glyph_real"]["majority_cycles"] > 0


def test_frequency_match_is_non_discriminating():
    res = run(CORPUS, seed=70)
    # Hebrew vs English sorted-profile correlations are both high and ~tie
    assert res["freq_tie"] is True
    assert res["freq_spearman_hebrew"] > 0.9
    assert abs(res["freq_spearman_hebrew"] - res["freq_spearman_english"]) < 0.05


# --------------------------------------------------------------------------- #
# main() writes the three CSVs with the guardrail                             #
# --------------------------------------------------------------------------- #
def test_main_writes_csvs_with_guardrail(tmp_path):
    out_s = tmp_path / "summary.csv"
    out_c = tmp_path / "corpora.csv"
    out_p = tmp_path / "pairs.csv"
    rc = main(["--corpus", str(CORPUS), "--seed", "70",
               "--out-summary", str(out_s), "--out-corpora", str(out_c),
               "--out-pairs", str(out_p)])
    assert rc == 0
    summary = {r["metric"]: r["value"] for r in csv.DictReader(out_s.open(encoding="utf-8"))}
    assert summary["verdict"] == "hebrew_alphagram_refuted"
    assert summary["guardrail"] == GUARDRAIL
    assert int(summary["majority_cycles_real"]) > 0

    corpora = list(csv.DictReader(out_c.open(encoding="utf-8")))
    names = {r["corpus"] for r in corpora}
    assert {"real", "floor_shuffle", "ceiling_sorted", "generator_base"} <= names
    assert all(r["guardrail"] == GUARDRAIL for r in corpora)
    ceiling = next(r for r in corpora if r["corpus"] == "ceiling_sorted")
    assert abs(float(ceiling["alphagram_fraction"]) - 1.0) < 1e-9

    pairs = list(csv.DictReader(out_p.open(encoding="utf-8")))
    assert pairs and all(r["guardrail"] == GUARDRAIL for r in pairs)
    # there is at least one ambiguous (undecided) glyph pair -> not a total order
    assert any(r["decided"] == "no" for r in pairs)
