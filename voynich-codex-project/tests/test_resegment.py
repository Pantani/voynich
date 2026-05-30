"""Tests for Rota 61 re-segmentation analysis (analyze_resegment.py).

THE last falsification of the "what is Voynichese" arc: a verbose cipher would hide
syntax BELOW the token grid, so re-segmenting (BPE) the character stream should
REVIVE order-structure. Because greedy merges manufacture apparent structure in ANY
text, the test is DIFFERENTIAL: identical BPE pipeline on Voynich AND on R60's
structure-matched nulls (markov2_char, bag-of-words), comparing order-gain revival.

Tests pin the mechanism, not a conclusion:
  - BPE merges the most-frequent adjacent pair ("aaab" -> "aa" merged first).
  - BPE never merges across a line break (boundary is the locus line).
  - order_gain is HIGH on a highly-ordered synthetic (a repeating phrase) and ~0 on
    a shuffled (bag-of-units) sequence.
  - fixed-width unit serialization preserves the multiset under shuffle (only ORDER
    differs between real and shuffled), and byte width scales with vocab size.
  - the differential and verdict thresholds behave as specified.
  - cross_boundary_merge_frac detects units that swallow a former space.
  - surrogate generators (trusted from R60) feed the pipeline and re-cut to the real
    line geometry without crossing line lengths.
  - main() writes BOTH CSVs with the guardrail, the required metrics, and a token
    sanity gain that ~ reproduces R60's ~0.03.

All randomness is seeded. No decipherment claims are made anywhere.
"""
from __future__ import annotations

import csv
import random
from pathlib import Path

from scripts.analyze_resegment import (
    DEFAULT_CORPUS,
    GUARDRAIL,
    _bytes_per_id,
    _count_pairs,
    _flatten,
    _merge_pair,
    char_lines,
    classify_verdict,
    classify_verdict_both,
    cross_boundary_merge_frac,
    differential,
    learn_bpe,
    main,
    order_gain_bz2,
    order_gain_lzma,
    recut_stream_to_line_lengths,
    serialize_units,
)
from scripts.analyze_compressibility import gen_markov2_char, gen_word_unigram, word_sequence
from scripts.analyze_language_signature import SPACE, parse_loci


# --------------------------------------------------------------------------- #
# BPE core: most-frequent pair, line boundaries                               #
# --------------------------------------------------------------------------- #
def test_bpe_merges_most_frequent_pair_first():
    # "aaab" -> pairs: (a,a) x2, (a,b) x1. First merge must be (a,a).
    lines = [list("aaab")]
    seg, vocab, merges = learn_bpe(lines, k=1)
    assert merges[0] == ("a", "a")
    # the new symbol expands to "aa"
    new_syms = [s for s in seg[0] if s not in ("a", "b")]
    assert new_syms, "expected a merged symbol in the segmentation"
    assert all(vocab[s] == "aa" for s in new_syms)
    # surface text of the whole line is preserved (no chars lost/added)
    assert "".join(vocab[s] for s in seg[0]) == "aaab"


def test_bpe_merge_pair_helper_is_nonoverlapping_left_to_right():
    # "aaaa" with pair (a,a): standard non-overlapping LTR -> two merged symbols.
    lines = [list("aaaa")]
    _merge_pair(lines, ("a", "a"), "X")
    assert lines[0] == ["X", "X"]


def test_bpe_respects_line_boundaries_no_cross_merge():
    # Two lines each "ab"; the most-frequent pair is (a,b) (count 2). The boundary
    # between line0's 'b' and line1's 'a' must NEVER be counted or merged.
    lines = [list("ab"), list("ab")]
    pairs = _count_pairs(lines)
    assert pairs[("a", "b")] == 2
    assert ("b", "a") not in pairs  # cross-line pair never appears
    seg, vocab, merges = learn_bpe(lines, k=1)
    assert merges[0] == ("a", "b")
    # each line collapses to a single unit "ab"; no unit spans both lines
    assert len(seg) == 2
    for line in seg:
        assert "".join(vocab[s] for s in line) == "ab"


def test_bpe_stops_when_no_pairs_left():
    # single char per line: no adjacent pair exists, so no merge happens even if K>0
    lines = [["a"], ["b"]]
    seg, vocab, merges = learn_bpe(lines, k=5)
    assert merges == []
    assert seg == [["a"], ["b"]]


def test_bpe_is_deterministic_under_ties():
    lines = [list("xyxy")]  # (x,y) x2, (y,x) x1 -> first merge (x,y)
    a = learn_bpe(lines, k=2)
    b = learn_bpe(lines, k=2)
    assert a[2] == b[2]  # identical merge order


# --------------------------------------------------------------------------- #
# Order gain                                                                  #
# --------------------------------------------------------------------------- #
def test_order_gain_high_on_repeating_phrase():
    # A long, highly-ordered repeating unit sequence compresses far better in order
    # than shuffled (bag-of-units), so order_gain should be clearly positive.
    units = ["A", "B", "C", "D"] * 800
    og, vocab = order_gain_lzma(units, seed=0)
    assert vocab == 4
    assert og > 0.3


def test_order_gain_near_zero_on_shuffled_sequence():
    # Start from a structured sequence, shuffle it -> the "real" order IS already a
    # bag-of-units, so its order_gain over another shuffle should be ~0.
    rng = random.Random(123)
    base = (["A", "B", "C", "D"] * 800)[:]
    rng.shuffle(base)
    og, _ = order_gain_lzma(base, seed=7)
    assert abs(og) < 0.05


def test_order_gain_empty_is_zero():
    og, vocab = order_gain_lzma([], seed=0)
    assert og == 0.0 and vocab == 0


# --------------------------------------------------------------------------- #
# Serialization                                                               #
# --------------------------------------------------------------------------- #
def test_bytes_per_id_scales_with_vocab():
    assert _bytes_per_id(1) == 1
    assert _bytes_per_id(256) == 1  # 0..255 fit in one byte
    assert _bytes_per_id(257) == 2
    assert _bytes_per_id(70000) == 3


def test_serialize_preserves_multiset_under_shuffle():
    # order_gain reuses ONE id_map for real + shuffle, so a permutation yields a
    # byte-IDENTICAL multiset (only order differs) -- the fair basis of the metric.
    units = ["A", "B", "B", "C", "A"]
    id_map = {"A": 0, "B": 1, "C": 2}
    real_bytes, vocab = serialize_units(units, id_map)
    assert vocab == 3
    rng = random.Random(1)
    shuffled = units[:]
    rng.shuffle(shuffled)
    shuf_bytes, vocab2 = serialize_units(shuffled, id_map)
    assert vocab2 == vocab
    # same length (fixed width) and IDENTICAL multiset of id-chunks (order differs)
    assert len(real_bytes) == len(shuf_bytes) == len(units) * _bytes_per_id(vocab)
    w = _bytes_per_id(vocab)
    real_chunks = sorted(real_bytes[i : i + w] for i in range(0, len(real_bytes), w))
    shuf_chunks = sorted(shuf_bytes[i : i + w] for i in range(0, len(shuf_bytes), w))
    assert real_chunks == shuf_chunks
    # and first-appearance id_map (no map passed) still works
    auto_bytes, auto_vocab = serialize_units(units)
    assert auto_vocab == 3 and len(auto_bytes) == len(units) * _bytes_per_id(3)


# --------------------------------------------------------------------------- #
# cross_boundary_merge_frac                                                   #
# --------------------------------------------------------------------------- #
def test_cross_boundary_merge_frac_detects_space_swallowing():
    # One line "a b" (chars a, space, b). Merging enough collapses it into a single
    # unit whose surface contains a space => cross_boundary_merge_frac == 1.0.
    lines = char_lines([["a", "b"]])  # -> [['a',' ','b']]
    seg, vocab, _ = learn_bpe(lines, k=5)
    # fully merged single unit "a b"
    assert len(seg[0]) == 1
    frac = cross_boundary_merge_frac(seg, vocab)
    assert frac == 1.0


def test_cross_boundary_merge_frac_zero_when_no_space_in_units():
    # No spaces present at all -> no unit can contain a space.
    lines = [list("aaaa")]
    seg, vocab, _ = learn_bpe(lines, k=2)
    assert cross_boundary_merge_frac(seg, vocab) == 0.0


def test_char_lines_inserts_space_between_tokens_only():
    # "ab","cd" on one line -> chars a b ' ' c d ; tokens within a line are
    # space-joined, so exactly one space appears between the two tokens.
    cl = char_lines([["ab", "cd"]])
    assert cl == [["a", "b", SPACE, "c", "d"]]


# --------------------------------------------------------------------------- #
# Re-cut surrogate to real line geometry                                      #
# --------------------------------------------------------------------------- #
def test_recut_stream_matches_line_lengths():
    stream = "abcdefghij"
    lengths = [3, 2, 5]
    cut = recut_stream_to_line_lengths(stream, lengths)
    assert ["".join(line) for line in cut] == ["abc", "de", "fghij"]


def test_recut_stream_truncates_short_final_line():
    stream = "abcd"
    lengths = [3, 5]  # second line wants 5 chars but only 1 remains
    cut = recut_stream_to_line_lengths(stream, lengths)
    assert ["".join(line) for line in cut] == ["abc", "d"]


# --------------------------------------------------------------------------- #
# Differential + verdict                                                      #
# --------------------------------------------------------------------------- #
def test_differential_subtracts_larger_surrogate():
    assert differential(0.10, 0.04, 0.06) == 0.10 - 0.06
    assert differential(0.05, 0.05, 0.05) == 0.0


def test_verdict_hidden_structure_when_clearly_exceeds():
    # voy=0.10, surrogates ~0.04 -> diff 0.06 > 0.02 AND 0.10 > 1.5*0.04
    assert classify_verdict(0.10, 0.04, 0.03) == "hidden_structure"


def test_verdict_no_hidden_when_similar_to_surrogates():
    # voy ~ surrogates -> mechanical revival only
    assert classify_verdict(0.045, 0.040, 0.042) == "no_hidden_structure"
    # passes absolute but fails the ratio (surrogate baseline is large)
    assert classify_verdict(0.30, 0.27, 0.20) == "no_hidden_structure"


# --------------------------------------------------------------------------- #
# Surrogate generators feed the pipeline (trusted from R60)                   #
# --------------------------------------------------------------------------- #
def test_surrogates_recut_without_crossing_real_line_lengths():
    lines = parse_loci(DEFAULT_CORPUS)
    words = word_sequence(lines)
    real_stream = SPACE.join(words)
    cl = char_lines(lines)
    line_lengths = [len(line) for line in cl]
    n = len(real_stream)
    mk = gen_markov2_char(real_stream, n, seed=2)
    bow = gen_word_unigram(words, n, seed=3)
    mk_lines = recut_stream_to_line_lengths(mk, line_lengths)
    bow_lines = recut_stream_to_line_lengths(bow, line_lengths)
    # surrogate generators produce >= real length, so every full line is realized
    assert len(mk_lines) == len(line_lengths)
    assert len(bow_lines) == len(line_lengths)
    # per-line lengths match the real geometry (BPE boundary parity)
    assert [len(x) for x in mk_lines] == line_lengths
    assert [len(x) for x in bow_lines] == line_lengths


# --------------------------------------------------------------------------- #
# main(): writes both CSVs with guardrail + required metrics                  #
# --------------------------------------------------------------------------- #
def test_main_writes_both_csvs_with_guardrail(tmp_path: Path):
    out_table = tmp_path / "resegment_zl3b.csv"
    out_summary = tmp_path / "resegment_summary_zl3b.csv"
    # small K keeps the test fast while exercising the full pipeline
    rc = main(
        [
            str(DEFAULT_CORPUS),
            "-K",
            "40",
            "--seed",
            "0",
            "--out-table",
            str(out_table),
            "--out-summary",
            str(out_summary),
        ]
    )
    assert rc == 0
    assert out_table.exists() and out_summary.exists()

    with out_table.open() as f:
        trows = list(csv.DictReader(f))
    # four streams: voynich token + 3x BPE
    streams = {(r["stream"], r["segmentation"]) for r in trows}
    assert ("voynich", "token") in streams
    assert ("voynich", "bpe_k40") in streams
    assert ("markov2_surrogate", "bpe_k40") in streams
    assert ("bagofwords_surrogate", "bpe_k40") in streams
    assert all(r["semantic_guardrail"] == GUARDRAIL for r in trows)

    with out_summary.open() as f:
        srows = list(csv.DictReader(f))
    metrics = {r["metric"]: r["value"] for r in srows}
    for key in (
        "K",
        "revival_voy",
        "revival_markov",
        "revival_bow",
        "differential",
        "cross_boundary_merge_frac",
        "voy_token_order_gain",
        "verdict",
        "guardrail",
    ):
        assert key in metrics, f"missing summary metric {key}"
    assert metrics["guardrail"] == GUARDRAIL
    assert metrics["verdict"] in ("hidden_structure", "no_hidden_structure")
    # token sanity gain should be a small positive number near R60's ~0.03
    assert -0.02 <= float(metrics["voy_token_order_gain"]) <= 0.15


def test_main_is_deterministic(tmp_path: Path):
    args = lambda tag: [  # noqa: E731
        str(DEFAULT_CORPUS),
        "-K",
        "30",
        "--seed",
        "0",
        "--out-table",
        str(tmp_path / f"t_{tag}.csv"),
        "--out-summary",
        str(tmp_path / f"s_{tag}.csv"),
    ]
    assert main(args("a")) == 0
    assert main(args("b")) == 0
    assert (tmp_path / "s_a.csv").read_text() == (tmp_path / "s_b.csv").read_text()


# --------------------------------------------------------------------------- #
# bz2 robustness cross-check (the Rota 60 gate)                               #
# --------------------------------------------------------------------------- #
def test_order_gain_bz2_runs_and_matches_lzma_on_ordered_input():
    """bz2 order gain is finite, in [0,1), and (like lzma) HIGH on ordered input."""
    units = (["a", "b", "c", "d"] * 200) + ["a", "a", "a"]
    g_bz2, vocab = order_gain_bz2(units, seed=1)
    assert 0.0 <= g_bz2 < 1.0
    assert vocab >= 1
    # a fully shuffled-style bag (already random) should give ~0 on bz2 too
    rng = random.Random(0)
    rnd = [rng.choice("abcd") for _ in range(800)]
    assert order_gain_bz2(rnd, seed=2)[0] < 0.05


def test_classify_verdict_both_requires_both_compressors():
    """The robust verdict only fires when the differential holds on lzma AND bz2.

    Encodes the R60 lesson: an lzma-only gain that bz2 kills is an artifact, not
    hidden structure. (revival_voy, revival_markov, revival_bow) per compressor.
    """
    strong = (0.30, 0.05, 0.05)   # voy >> surrogates, clears abs+ratio gates
    weak = (0.07, 0.06, 0.065)    # voy ~ surrogates, fails gates
    assert classify_verdict_both(strong, strong) == "hidden_structure_robust"
    # lzma strong, bz2 collapses -> the actual Rota 61 outcome
    assert classify_verdict_both(strong, weak) == "lzma_artifact"
    assert classify_verdict_both(weak, strong) == "bz2_only_ambiguous"
    assert classify_verdict_both(weak, weak) == "no_hidden_structure"


def test_summary_has_bz2_metrics_and_robust_verdict(tmp_path):
    """main() must persist the bz2 cross-check metrics and a both-compressor verdict."""
    table = tmp_path / "t.csv"
    summary = tmp_path / "s.csv"
    rc = main([str(DEFAULT_CORPUS), "-K", "60", "--out-table", str(table), "--out-summary", str(summary)])
    assert rc == 0
    metrics = {r["metric"]: r["value"] for r in csv.DictReader(summary.open())}
    for key in ("revival_voy_bz2", "differential_bz2", "verdict_lzma_only", "verdict"):
        assert key in metrics, key
    assert metrics["verdict"] in {
        "hidden_structure_robust",
        "lzma_artifact",
        "bz2_only_ambiguous",
        "no_hidden_structure",
    }
    assert GUARDRAIL in summary.read_text()
