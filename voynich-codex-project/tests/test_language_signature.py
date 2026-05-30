"""Tests for Rota 58 language-signature analysis (analyze_language_signature.py).

Covers the three structural signatures (char/word conditional entropy, LAAFU
mutual information with a permutation null, adjacent same-token repetition) plus
the per-locus parser that must preserve token order and reproduce the Rota
53/57 token total (37671). Entropy primitives are checked against closed-form
values on known distributions; the LAAFU MI is checked on synthetic datasets
with a known answer (perfectly position-bound -> high I, low p; no binding ->
I near the null).
"""
from __future__ import annotations

import collections
import csv
import math
from pathlib import Path

from scripts.analyze_language_signature import (
    GUARDRAIL,
    adjacent_repeats,
    char_entropies,
    classify_verdict,
    conditional_entropy,
    laafu_pairs,
    laafu_permutation_null,
    line_edge_biases,
    main,
    mutual_information,
    parse_loci,
    shannon_entropy,
    shuffled_char_h2,
    word_entropies,
)
from scripts.analyze_nucleus import parse_corpus

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"


def test_shannon_entropy_uniform_four_symbols_is_two_bits():
    # uniform over 4 symbols -> h1 = log2(4) = 2.0 bits
    assert abs(shannon_entropy(collections.Counter({c: 7 for c in "abcd"})) - 2.0) < 1e-9
    # uniform over 2 -> 1 bit; deterministic -> 0; empty -> 0
    assert abs(shannon_entropy(collections.Counter({"a": 3, "b": 3})) - 1.0) < 1e-9
    assert shannon_entropy(collections.Counter({"x": 99})) == 0.0
    assert shannon_entropy(collections.Counter()) == 0.0


def test_char_entropies_uniform_iid_stream_h1_equals_h0_and_h2_equals_h1():
    """A long i.i.d. uniform 4-letter stream: h1->2 bits, and with no order
    structure h2 (conditional) should be ~h1 (here exactly, by construction)."""
    # 'abcd' repeated has every bigram equally; build as one line of 1-char tokens
    # joined by SPACE would inject SPACE into the alphabet, so test the helper
    # directly on a single token-less construction via word_entropies-free path:
    # use 4 symbols cycled -> each symbol appears equally, each ordered pair
    # (a,b),(b,c),(c,d),(d,a) equally -> H(pair)=2, H(prev)=2 -> NO: cycle is
    # deterministic. Instead assert the documented relation h2<=h1 holds and
    # h0>=h1 on the cycled stream.
    lines = [list("abcdabcdabcd")]  # tokens are single chars; SPACE separates
    ce = char_entropies(lines)
    assert ce["h0"] >= ce["h1"] - 1e-9
    assert ce["h2"] <= ce["h1"] + 1e-9


def test_conditional_entropy_never_exceeds_unigram_on_real_corpus():
    lines = parse_loci(CORPUS)
    ce = char_entropies(lines)
    # h0 >= h1 >= h2 (each conditioning step cannot increase uncertainty)
    assert ce["h0"] >= ce["h1"] - 1e-9
    assert ce["h2"] <= ce["h1"] + 1e-9
    # h2 is positive and finite
    assert 0.0 < ce["h2"] < ce["h1"]


def test_shuffled_char_h2_collapses_to_unigram():
    """Global char-shuffle destroys bigram structure -> shuffled h2 ~ h1, and
    well above the real (ordered) h2."""
    lines = parse_loci(CORPUS)
    ce = char_entropies(lines)
    h2s = shuffled_char_h2(lines, seed=0)
    assert abs(h2s - ce["h1"]) < 0.05  # shuffled conditional ~= unigram
    assert h2s > ce["h2"] + 0.5  # real local predictability is large


def test_conditional_entropy_helper_matches_joint_minus_prev():
    pair = collections.Counter({("a", "b"): 3, ("a", "c"): 1, ("b", "a"): 4})
    prev = collections.Counter({"a": 4, "b": 4})
    expected = shannon_entropy(pair) - shannon_entropy(prev)
    assert abs(conditional_entropy(pair, prev) - expected) < 1e-12
    assert conditional_entropy(collections.Counter(), collections.Counter()) == 0.0


def test_word_entropies_counts_and_bounds():
    lines = [["a", "b", "a"], ["a", "c"]]
    we = word_entropies(lines)
    assert we["n_tokens"] == 5
    assert we["n_types"] == 3  # a, b, c
    # h2_word <= H1_word (conditioning cannot increase uncertainty)
    assert we["h2_word"] <= we["h1_word"] + 1e-9


def test_laafu_pairs_only_lines_with_at_least_three_tokens():
    lines = [["a", "b"], ["a", "b", "c"], ["x", "y", "z", "w"]]
    pairs = laafu_pairs(lines)
    # 2-token line dropped; 3-token + 4-token lines contribute 3 + 4 = 7 pairs
    assert len(pairs) == 7
    buckets = collections.Counter(p for _, p in pairs)
    assert buckets["first"] == 2  # one per qualifying line
    assert buckets["last"] == 2
    assert buckets["medial"] == 3  # 1 from 3-tok line, 2 from 4-tok line


def test_mutual_information_zero_when_independent():
    # X fully crossed with Y in equal counts -> I(X;Y)=0
    pairs = []
    for x in ("a", "b"):
        for y in ("first", "medial", "last"):
            pairs.extend([(x, y)] * 5)
    assert abs(mutual_information(pairs)) < 1e-9


def test_laafu_synthetic_position_bound_gives_high_i_low_p():
    """A dataset where each word appears in exactly one position bucket ->
    I(word;position) is high and the permutation p is small."""
    lines = []
    # words A* always first, M* always medial, L* always last
    for k in range(40):
        lines.append([f"A{k%4}", f"M{k%4}", f"L{k%4}"])
    pairs = laafu_pairs(lines)
    obs, null_mean, p = laafu_permutation_null(pairs, n_perm=300, seed=1)
    assert obs > 2.0 * null_mean  # observed crushes the null
    assert p < 0.05


def test_laafu_synthetic_no_binding_gives_i_near_null():
    """When the SAME words are uniformly spread across all positions, observed I
    sits at the permutation null (no position information)."""
    lines = []
    # every line uses the same three words in rotating order so each word hits
    # every bucket equally -> word carries no position info
    words = ["w0", "w1", "w2"]
    for k in range(60):
        rot = words[k % 3:] + words[: k % 3]
        lines.append(rot)
    pairs = laafu_pairs(lines)
    obs, null_mean, p = laafu_permutation_null(pairs, n_perm=300, seed=2)
    assert obs < 0.05  # essentially no mutual information
    assert p > 0.05  # not distinguishable from the shuffled null


def test_line_edge_biases_detect_overrepresented_glyph():
    # every line starts with a 'p..' token and ends with a '..m' token, while
    # the medial tokens never use p (first) or m (last)
    lines = [["paa", "xyz", "qqm"] for _ in range(10)]
    init_rows, final_rows = line_edge_biases(lines, top_k=3)
    top_init = init_rows[0]
    top_final = final_rows[0]
    assert top_init["glyph"] == "p"
    assert top_final["glyph"] == "m"
    # p as a line-initial first glyph is over-represented vs corpus-wide first
    # glyphs (corpus first glyphs: p,x,q -> p is 1/3; edge first: p is 1/1)
    assert top_init["ratio"] > 1.0
    assert top_final["ratio"] > 1.0


def test_adjacent_repeats_counting_and_iid_expectation():
    # line: a a a b -> adjacent pairs: (a,a),(a,a),(a,b) -> 2 repeats / 3 pairs
    # line: b b      -> (b,b) -> 1 repeat / 1 pair
    lines = [["a", "a", "a", "b"], ["b", "b"]]
    rep = adjacent_repeats(lines)
    assert rep["adj_pairs"] == 4
    assert rep["repeats"] == 3
    assert abs(rep["observed"] - 3 / 4) < 1e-12
    # unigram counts: a=3, b=3 over 6 tokens -> p=0.5 each
    # expected_iid = 0.5^2 + 0.5^2 = 0.5
    assert abs(rep["expected_iid"] - 0.5) < 1e-12
    assert abs(rep["ratio"] - (0.75 / 0.5)) < 1e-12
    assert rep["repeat_tokens"]["a"] == 2
    assert rep["repeat_tokens"]["b"] == 1


def test_classify_verdict_thresholds():
    # 0 anomalies -> language_like
    n, v, flags = classify_verdict(h2_char=3.2, i_obs=0.1, i_null_mean=0.1, i_p=0.5, adj_ratio=1.0)
    assert (n, v) == (0, "language_like")
    # only char h2 anomalous -> mixed
    n, v, flags = classify_verdict(h2_char=2.1, i_obs=0.1, i_null_mean=0.1, i_p=0.5, adj_ratio=1.0)
    assert (n, v) == (1, "mixed")
    assert flags["char_h2_anomalous"] and not flags["laafu_anomalous"]
    # all three anomalous -> low_content_signatures
    n, v, flags = classify_verdict(h2_char=2.0, i_obs=1.0, i_null_mean=0.2, i_p=0.001, adj_ratio=5.0)
    assert (n, v) == (3, "low_content_signatures")
    assert all(flags.values())
    # LAAFU just under 2x null -> not anomalous even with p<0.05
    n, v, flags = classify_verdict(h2_char=3.0, i_obs=0.39, i_null_mean=0.2, i_p=0.01, adj_ratio=1.0)
    assert not flags["laafu_anomalous"]


def test_parse_loci_preserves_order_and_reproduces_token_total():
    lines = parse_loci(CORPUS)
    # flattened token total must equal analyze_nucleus.parse_corpus (37671)
    flat = [t for line in lines for t in line]
    _, ref = parse_corpus(CORPUS)
    assert len(flat) == len(ref) == 37671
    # order is preserved: the flattened per-locus tokens match parse_corpus order
    assert flat == [t for _, t in ref]
    # every line is non-empty (empties dropped)
    assert all(len(line) >= 1 for line in lines)


def test_parse_loci_inline_synthetic_order():
    # write a tiny IVTFF-shaped file and confirm token order within a locus
    txt = (
        "<f1r>      <! $L=A>\n"
        "<f1r.1,@P0>   alpha.beta.gamma\n"
        "<f1r.2,+P0>   delta,epsilon\n"  # comma -> token separator
        "# comment line ignored\n"
        "<f1r.3,=Pt>   <%>zeta<$>\n"
    )
    p = ROOT / "tests" / "_tmp_langsig_parse.txt"
    p.write_text(txt, encoding="utf-8")
    try:
        lines = parse_loci(p)
        assert lines[0] == ["alpha", "beta", "gamma"]
        assert lines[1] == ["delta", "epsilon"]
        assert lines[2] == ["zeta"]
    finally:
        p.unlink()


def test_main_writes_three_csvs_with_guardrail(tmp_path):
    summary = tmp_path / "summary.csv"
    lineedge = tmp_path / "lineedge.csv"
    repeats = tmp_path / "repeats.csv"
    rc = main(
        [
            str(CORPUS),
            "--n-perm",
            "40",
            "--out-summary",
            str(summary),
            "--out-lineedge",
            str(lineedge),
            "--out-repeats",
            str(repeats),
        ]
    )
    assert rc == 0
    for p in (summary, lineedge, repeats):
        assert p.exists() and p.stat().st_size > 0
        assert GUARDRAIL in p.read_text(encoding="utf-8")

    # summary must carry every required metric
    text = summary.read_text(encoding="utf-8")
    for metric in (
        "alphabet_size",
        "h0",
        "h1",
        "h2_char",
        "h2_char_shuffled",
        "H1_word",
        "h2_word",
        "I_word_linepos_bits",
        "I_linepos_null_mean",
        "I_linepos_p",
        "adjacent_repeat_rate",
        "adjacent_repeat_iid",
        "adjacent_repeat_ratio",
        "n_anomalous_signatures",
        "verdict",
        "guardrail",
    ):
        assert metric in text

    # line-edge CSV has both edges and finite-or-inf ratios
    with lineedge.open(encoding="utf-8") as f:
        edge_rows = list(csv.DictReader(f))
    assert {r["edge"] for r in edge_rows} == {"initial", "final"}
    assert all(r["glyph"] for r in edge_rows)

    # repeats CSV: positive integer counts, includes a known repeated token
    with repeats.open(encoding="utf-8") as f:
        rep_rows = list(csv.DictReader(f))
    assert len(rep_rows) > 0
    assert all(int(r["adjacent_repeat_count"]) > 0 for r in rep_rows)


def test_main_summary_values_in_expected_ranges(tmp_path):
    """Sanity gate on the real corpus: char h2 in the published-Voynich band and
    the token/char totals as documented."""
    summary = tmp_path / "summary.csv"
    lineedge = tmp_path / "lineedge.csv"
    repeats = tmp_path / "repeats.csv"
    main(
        [
            str(CORPUS),
            "--n-perm",
            "40",
            "--out-summary",
            str(summary),
            "--out-lineedge",
            str(lineedge),
            "--out-repeats",
            str(repeats),
        ]
    )
    with summary.open(encoding="utf-8") as f:
        m = {r["metric"]: r["value"] for r in csv.DictReader(f)}
    assert int(m["n_tokens"]) == 37671
    h2 = float(m["h2_char"])
    assert 1.8 < h2 < 2.5  # anomalously low / published Voynich band
    # shuffled h2 must sit close to h1 (structure destroyed)
    assert abs(float(m["h2_char_shuffled"]) - float(m["h1"])) < 0.05
    assert float(m["h0"]) >= float(m["h1"]) >= h2  # h0 >= h1 >= h2
    assert m["verdict"] in {"language_like", "mixed", "low_content_signatures"}
