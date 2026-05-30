"""Tests for Rota 69 directionality / reversal / mirror-page analysis.

Covers the load-bearing claims: (1) single-step conditional entropy is reversal-
invariant on the real corpus (h2_fwd == h2_bwd to within sampling), so reading
direction is invisible at the sequence level; (2) the only bigram-directional
content is the word-edge asymmetry dir_edge = H(first) - H(last), which is
reproduced by the content-free generator and FLIPS SIGN under per-token reversal
(pure morphology); (3) reversal moves nothing into the natural-language h2 band;
(4) facing pages are not mirrors once the same-section confound is removed.
Primitives are checked against closed-form values; the integration test asserts
the verdict is `leonardo_operations_degenerate`.
"""
from __future__ import annotations

import csv
import math
from pathlib import Path

from scripts.analyze_directionality_mirror import (
    GUARDRAIL,
    block_cond_entropy,
    classify_verdict,
    cond_entropy_pairs,
    directional_entropies,
    facing_mirror_test,
    global_word_shuffle,
    main,
    mirror_match_fraction,
    palindrome_fraction,
    parse_folio_sequences,
    reverse_each_token,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"


# --------------------------------------------------------------------------- #
# Entropy primitives                                                          #
# --------------------------------------------------------------------------- #
def test_block_cond_entropy_deterministic_sequence_is_zero():
    # "abababab": next char fully determined by previous -> H(c|prev)=0.
    assert block_cond_entropy(list("abababab"), 1) == 0.0


def test_block_cond_entropy_cyclic_is_zero():
    # "abcdabcd...": order-1 context fully determines the next char -> H(c|prev)=0.
    assert block_cond_entropy(list("abcd" * 250), 1) == 0.0


def test_cond_entropy_pairs_known_value():
    # X->Y: a->{x,y} 50/50, b->z always. H(Y|X)=P(a)*1 + P(b)*0.
    pairs = [("a", "x"), ("a", "y"), ("b", "z"), ("b", "z")]
    # P(a)=0.5 -> contributes 0.5*1bit; P(b)=0.5 -> 0. Total 0.5.
    assert abs(cond_entropy_pairs(pairs) - 0.5) < 1e-9


# --------------------------------------------------------------------------- #
# Corpus transforms                                                           #
# --------------------------------------------------------------------------- #
def test_reverse_each_token_mirrors_chars_keeps_order():
    lines = [["abc", "de"], ["xyz"]]
    assert reverse_each_token(lines) == [["cba", "ed"], ["zyx"]]


def test_global_word_shuffle_preserves_multiset_and_line_lengths():
    lines = [["a", "b", "c"], ["d", "e"]]
    out = global_word_shuffle(lines, seed=1)
    assert [len(line) for line in out] == [3, 2]
    assert sorted(t for line in out for t in line) == ["a", "b", "c", "d", "e"]


def test_token_reversal_flips_dir_edge_sign():
    # dir_edge = H(first) - H(last); mirroring every token swaps first<->last glyph
    # distributions, so dir_edge must flip sign with the same magnitude.
    lines = [["okal", "otar", "chol", "qokeedy"], ["daiin", "shol", "okaiin"]]
    d = directional_entropies(lines)
    r = directional_entropies(reverse_each_token(lines))
    assert abs(d["dir_edge"] + r["dir_edge"]) < 1e-9
    assert d["dir_edge"] != 0.0


# --------------------------------------------------------------------------- #
# Mirror-page primitives                                                      #
# --------------------------------------------------------------------------- #
def test_palindrome_fraction_full_and_none():
    assert palindrome_fraction(["a", "b", "a"]) == 1.0  # middle ignored, ends match
    assert palindrome_fraction(["a", "b", "c", "d"]) == 0.0


def test_mirror_match_fraction_alignment():
    assert mirror_match_fraction(["a", "b", "c"], ["a", "x", "c"]) == 2 / 3
    assert mirror_match_fraction([], ["a"]) == 0.0


def test_facing_mirror_returns_effect_keys():
    folios = parse_folio_sequences(CORPUS)
    res = facing_mirror_test(folios, n_perm=50, seed=0)
    for k in ("obs_reverse", "obs_forward", "mirror_effect", "null_effect_mean", "p"):
        assert k in res


# --------------------------------------------------------------------------- #
# Real-corpus scientific properties                                           #
# --------------------------------------------------------------------------- #
def test_reversal_invariance_on_real_corpus():
    """h2 (and h3) are direction-invariant on the real corpus: the theorem holds."""
    from scripts.analyze_generator import parse_loci_with_section

    lines, _ = parse_loci_with_section(CORPUS)
    d = directional_entropies(lines)
    assert abs(d["h2_fwd"] - d["h2_bwd"]) < 0.01
    assert abs(d["h3_fwd"] - d["h3_bwd"]) < 0.01
    # endings more constrained than beginnings (right-anchored morphology)
    assert d["dir_edge"] > 0.3


def test_classify_verdict_degenerate_when_no_signal():
    real = {"h2_fwd": 2.15, "h2_bwd": 2.15, "dir_edge": 0.68}
    rev = {"h2_fwd": 2.15, "h2_bwd": 2.15, "dir_edge": -0.68}
    gen = {"h2_fwd": 2.15, "h2_bwd": 2.15, "dir_edge": 0.69}
    de = {"real": real, "real_reversed_tokens": rev, "generator_base": gen}
    facing = {"obs_reverse": 0.004, "obs_forward": 0.006, "mirror_effect": -0.002,
              "null_effect_mean": -0.004, "p": 0.4}
    palin = {"observed": 0.006, "null_mean": 0.007, "p": 0.9}
    verdict, flags = classify_verdict(de, facing, palin)
    assert verdict == "leonardo_operations_degenerate"
    assert flags["bulk_reversal_symmetric"] is True
    assert flags["morphology_artifact_confirmed"] is True


def test_main_writes_outputs_and_degenerate_verdict(tmp_path):
    out_sum = tmp_path / "summary.csv"
    out_cor = tmp_path / "corpora.csv"
    rc = main([
        str(CORPUS), "--n-perm", "60", "--seed", "0",
        "--out-summary", str(out_sum), "--out-corpora", str(out_cor),
    ])
    assert rc == 0
    rows = {r["metric"]: r["value"] for r in csv.DictReader(out_sum.open())}
    assert rows["guardrail"] == GUARDRAIL
    assert rows["verdict"] == "leonardo_operations_degenerate"
    assert rows["bulk_reversal_symmetric"] == "True"
    assert rows["morphology_artifact_confirmed"] == "True"
    assert rows["directional_beyond_morphology"] == "False"
    # reverse overlap must NOT exceed forward overlap (no real mirroring)
    assert float(rows["facing_mirror_effect"]) <= 0.0 or float(rows["facing_mirror_p"]) >= 0.01
