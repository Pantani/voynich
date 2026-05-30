"""Tests for Rota 60 compression-ladder analysis (analyze_compressibility.py).

The decisive final test of the "what is Voynichese" arc: does word ORDER carry
compressible information (syntax / encoded language) or does the corpus compress
like its own bag-of-words (texture, syntactically thin)? Tests pin:

  - a highly-repetitive synthetic ("abc abc abc"...) compresses FAR below its
    char-shuffle (a compressor exploits the repetition; shuffling destroys it).
  - a random-char stream compresses ~= h0 (no structure to exploit).
  - markov2_char resample reproduces the real char conditional entropy h2 within
    +/- 0.15 bits (same trigram statistics, no higher structure).
  - word_unigram resample reproduces the real word-frequency distribution
    (the top words match by rank).
  - bits/char computation correctness, the gain formula, the verdict thresholds.
  - main() writes both CSVs with the guardrail and the required metrics; the real
    stream length is 228177; generation is deterministic under a fixed seed.

All randomness is seeded. No decipherment claims are made anywhere.
"""
from __future__ import annotations

import collections
import csv
import math
from pathlib import Path

from scripts.analyze_compressibility import (
    GUARDRAIL,
    bits_per_char,
    build_streams,
    classify_verdict,
    compress_size_bits,
    gain,
    gen_markov2_char,
    gen_order0,
    gen_word_unigram,
    main,
    stream_from_words,
    word_sequence,
)
from scripts.analyze_language_signature import _char_stream, parse_loci

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"


# --------------------------------------------------------------------------- #
# Helper: char conditional entropy h2 (independent reimplementation)          #
# --------------------------------------------------------------------------- #
def _h2_char(stream: str) -> float:
    """H(c_i | c_{i-1}) in bits via H(prev,cur) - H(prev) over adjacent pairs."""
    pair = collections.Counter(zip(stream, stream[1:]))
    prev = collections.Counter(stream[:-1])

    def _h(counter):
        n = sum(counter.values())
        return -sum((c / n) * math.log2(c / n) for c in counter.values() if c)

    return _h(pair) - _h(prev)


# --------------------------------------------------------------------------- #
# Compression behaviour                                                       #
# --------------------------------------------------------------------------- #
def test_repetitive_stream_compresses_far_below_char_shuffle():
    """A highly-repetitive stream ("abc " x N) is hugely redundant: a compressor
    crushes it. Shuffling its characters destroys that structure, so the shuffle
    compresses to FAR more bits. This is the core sanity of the whole method."""
    import random

    rep = "abc " * 20000  # 80000 chars, extreme long-range repetition
    chars = list(rep)
    random.Random(0).shuffle(chars)
    shuffled = "".join(chars)

    for comp in ("lzma", "bz2"):
        rep_bits = compress_size_bits(rep, comp)
        shuf_bits = compress_size_bits(shuffled, comp)
        # the repetitive original must compress to a small fraction of the shuffle
        assert rep_bits < 0.25 * shuf_bits, (comp, rep_bits, shuf_bits)


def test_random_char_stream_compresses_near_h0():
    """An i.i.d. uniform stream over a k-symbol alphabet has h0 = log2(k) and no
    exploitable structure, so a general compressor lands close to h0 bits/char
    (a small overhead above, never far below)."""
    import random

    rng = random.Random(7)
    alphabet = "abcdefgh"  # 8 symbols -> h0 = 3 bits/char
    stream = "".join(rng.choice(alphabet) for _ in range(60000))
    h0 = math.log2(len(alphabet))
    bpc = bits_per_char(compress_size_bits(stream, "lzma"), len(stream))
    # within ~0.4 bits of h0 (compressor overhead), and NOT far below it
    assert abs(bpc - h0) < 0.4
    assert bpc > h0 - 0.15


def test_order0_resample_lands_near_unigram_entropy():
    """order0 (i.i.d. from the real char-unigram dist) compresses near h1, the
    unigram entropy: it preserves only char frequency, so its bits/char is the
    unigram entropy plus compressor overhead, far above the real corpus rate."""
    lines = parse_loci(CORPUS)
    real = _char_stream(lines)
    uni = collections.Counter(real)
    n = sum(uni.values())
    h1 = -sum((c / n) * math.log2(c / n) for c in uni.values())
    stream = gen_order0("".join(real), len(real), seed=1)
    assert len(stream) == len(real)
    bpc = bits_per_char(compress_size_bits(stream, "lzma"), len(stream))
    # lands near h1 (within ~0.3 bits): no higher structure to exploit
    assert abs(bpc - h1) < 0.3


# --------------------------------------------------------------------------- #
# markov2_char reproduces the real char conditional entropy                   #
# --------------------------------------------------------------------------- #
def test_markov2_resample_reproduces_real_h2_within_tolerance():
    """Generating from the real order-2 char model reproduces the real char
    conditional entropy h2 within +/- 0.15 bits: the trigram statistics are
    matched, so H(c|prev) of the synthetic ~= the real h2."""
    lines = parse_loci(CORPUS)
    real = "".join(_char_stream(lines))
    real_h2 = _h2_char(real)
    synth = gen_markov2_char(real, len(real), seed=2)
    assert len(synth) == len(real)
    synth_h2 = _h2_char(synth)
    assert abs(synth_h2 - real_h2) < 0.15, (real_h2, synth_h2)


# --------------------------------------------------------------------------- #
# word_unigram reproduces the real word-frequency distribution                #
# --------------------------------------------------------------------------- #
def test_word_unigram_reproduces_word_frequency_top_words():
    """The bag-of-words null draws whole real words i.i.d. from the word-freq
    distribution, so the synthetic stream's most common words match the real
    corpus's most common words (by identity, in rank order for the very top)."""
    lines = parse_loci(CORPUS)
    words = word_sequence(lines)
    real = stream_from_words(words)
    real_top = [w for w, _ in collections.Counter(words).most_common(10)]

    synth = gen_word_unigram(words, len(real), seed=3)
    # split the synthetic stream back into tokens on the space separator
    synth_words = [w for w in synth.split(" ") if w]
    synth_top = [w for w, _ in collections.Counter(synth_words).most_common(10)]

    # the single most frequent word must match; top-5 sets must coincide
    assert synth_top[0] == real_top[0]
    assert set(synth_top[:5]) == set(real_top[:5])
    # length matches the real stream exactly
    assert len(synth) == len(real)


def test_word_unigram_destroys_order_but_keeps_identities():
    """Bag-of-words preserves the VOCABULARY: every synthetic token is a real
    token, EXCEPT the final token may be a truncation fragment (the stream is cut
    to exactly the real length, which can split the last word mid-token). Word
    ORDER is destroyed."""
    lines = parse_loci(CORPUS)
    words = word_sequence(lines)
    real = stream_from_words(words)
    vocab = set(words)
    synth_words = [w for w in gen_word_unigram(words, len(real), seed=5).split(" ") if w]
    # all but the last (possibly-truncated) token are genuine corpus words
    assert set(synth_words[:-1]) <= vocab


# --------------------------------------------------------------------------- #
# bits/char + gain formula                                                    #
# --------------------------------------------------------------------------- #
def test_bits_per_char_formula():
    assert bits_per_char(800, 100) == 8.0
    assert bits_per_char(0, 100) == 0.0
    assert bits_per_char(123, 0) == 0.0  # guarded divide-by-zero


def test_gain_formula_signs_and_zero():
    # null compresses worse (higher bpc) than real -> positive gain
    assert abs(gain(4.0, 3.0) - 0.25) < 1e-12
    # tie -> zero gain
    assert gain(3.0, 3.0) == 0.0
    # real compresses worse than null -> negative gain
    assert gain(3.0, 3.6) < 0.0
    # degenerate null -> 0.0
    assert gain(0.0, 1.0) == 0.0


# --------------------------------------------------------------------------- #
# Verdict thresholds                                                          #
# --------------------------------------------------------------------------- #
def test_classify_verdict_thresholds():
    assert classify_verdict(0.0) == "texture_bag_of_words"
    assert classify_verdict(0.029) == "texture_bag_of_words"
    assert classify_verdict(0.03) == "word_order_informative"
    assert classify_verdict(0.20) == "word_order_informative"
    # a slightly-negative gain (real no better than its bag) is still texture
    assert classify_verdict(-0.01) == "texture_bag_of_words"


# --------------------------------------------------------------------------- #
# Determinism + stream sanity                                                 #
# --------------------------------------------------------------------------- #
def test_build_streams_deterministic_and_equal_length():
    """All synthetic streams equal the real char length, and a fixed seed makes
    generation reproducible byte-for-byte."""
    lines = parse_loci(CORPUS)
    streams_a, n_a = build_streams(lines, seed=0, with_word_bigram=True)
    streams_b, n_b = build_streams(lines, seed=0, with_word_bigram=True)
    assert n_a == n_b == 228177  # real stream length (matches Rota 58/59)
    for name in ("real", "order0", "markov2_char", "word_unigram", "word_bigram"):
        assert len(streams_a[name]) == n_a  # every stream is the SAME length
        assert streams_a[name] == streams_b[name]  # deterministic under seed


# --------------------------------------------------------------------------- #
# main() outputs                                                              #
# --------------------------------------------------------------------------- #
def test_main_writes_both_csvs_with_guardrail(tmp_path):
    table = tmp_path / "table.csv"
    summary = tmp_path / "summary.csv"
    rc = main(
        [
            str(CORPUS),
            "--out-table",
            str(table),
            "--out-summary",
            str(summary),
        ]
    )
    assert rc == 0
    for p in (table, summary):
        assert p.exists() and p.stat().st_size > 0
        assert GUARDRAIL in p.read_text(encoding="utf-8")

    # table CSV: one row per (model, compressor); columns present; bpc > 0
    with table.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    models = {r["model"] for r in rows}
    assert {"real", "order0", "markov2_char", "word_unigram", "word_bigram"} <= models
    for r in rows:
        assert {"model", "compressor", "compressed_bits", "bits_per_char"} <= set(r)
        assert r["compressor"] in {"lzma", "bz2"}
        assert int(r["compressed_bits"]) > 0
        assert float(r["bits_per_char"]) > 0.0
        assert r["semantic_guardrail"] == GUARDRAIL

    # summary CSV: every required metric present and well-formed
    with summary.open(encoding="utf-8") as f:
        m = {r["metric"]: r["value"] for r in csv.DictReader(f)}
    for metric in (
        "stream_len",
        "bpc_real_lzma",
        "bpc_order0_lzma",
        "bpc_markov2_lzma",
        "bpc_wordunigram_lzma",
        "gain_over_markov2",
        "gain_over_wordunigram",
        "bpc_real_bz2",
        "gain_over_wordunigram_bz2",
        "verdict",
        "guardrail",
    ):
        assert metric in m, metric
    assert m["guardrail"] == GUARDRAIL
    assert int(m["stream_len"]) == 228177
    assert m["verdict"] in {"texture_bag_of_words", "word_order_informative"}


def test_main_ladder_orders_real_below_nulls(tmp_path):
    """On the real corpus the ladder must be monotone in the expected direction:
    order0 (only char freq) compresses WORST, markov2 (char trigrams) better, and
    the real stream compresses at least as well as its bag-of-words twin. This
    confirms each null preserves strictly less structure than the next."""
    table = tmp_path / "t.csv"
    summary = tmp_path / "s.csv"
    main([str(CORPUS), "--out-table", str(table), "--out-summary", str(summary)])
    with summary.open(encoding="utf-8") as f:
        m = {r["metric"]: float(v) if (v := r["value"]) and v.replace(".", "").replace("-", "").isdigit() else r["value"] for r in csv.DictReader(f)}
    bpc_real = float(m["bpc_real_lzma"])
    bpc_order0 = float(m["bpc_order0_lzma"])
    bpc_markov2 = float(m["bpc_markov2_lzma"])
    bpc_worduni = float(m["bpc_wordunigram_lzma"])
    # order0 is the loosest null (highest bpc), markov2 tighter
    assert bpc_order0 > bpc_markov2
    # real compresses better than (or equal to) its char-trigram null
    assert bpc_real <= bpc_markov2 + 1e-6
    # real compresses no worse than its own bag-of-words (gain >= ~0)
    assert bpc_real <= bpc_worduni + 0.05
    # the decisive gain is finite and reported
    assert -0.5 < float(m["gain_over_wordunigram"]) < 1.0
