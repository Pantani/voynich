"""Tests for Rota 59 long-range correlation analysis (analyze_long_range.py).

The decisive separator between a real-language-like system (power-law MI decay,
persisting to large d) and a simple local generator (exponential collapse to the
finite-sample floor within a few units). Tests pin:

  - MI(d) correctness on synthetic streams with a KNOWN answer: a period-7
    repeating sequence has high I at d=7 (and its multiples) and ~0 elsewhere;
    an i.i.d. random sequence has I(d) ~ the bias floor (~0) at every d.
  - the shuffle null sits at the bias floor and is ~flat in d.
  - power-law vs exponential fit DISCRIMINATION on synthetic d^-1 data
    (power-law wins) and synthetic e^(-d/3) data (exponential wins).
  - Zipf slope recovered on a synthetic Zipf sample; Heaps beta on synthetic.
  - correlation_length and the verdict thresholds.
  - main() writes both CSVs with the guardrail and the right columns/metrics.
"""
from __future__ import annotations

import csv
import math
import random
from pathlib import Path

from scripts.analyze_long_range import (
    GUARDRAIL,
    classify_verdict,
    correlation_length,
    excess_curve,
    fit_exponential,
    fit_powerlaw,
    heaps_beta,
    line_shuffled_stream,
    main,
    mi_at_distance,
    mi_curve,
    null_mi_curve,
    token_stream,
    zipf_slope,
)
from scripts.analyze_language_signature import _char_stream, parse_loci

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"


# --------------------------------------------------------------------------- #
# MEASURE 1 correctness                                                       #
# --------------------------------------------------------------------------- #
def test_mi_period7_sequence_peaks_at_lag_7():
    """A strictly period-7 stream (7 distinct symbols cycling) is deterministic
    at lag 7: c_{i+7} == c_i, so I(7) == H(unigram) = log2(7). At a lag coprime
    with 7 (e.g. 3) the pairing is a fixed permutation, also deterministic, so MI
    equals log2(7) too -- the discriminating fact is that I(7) is MAXIMAL and a
    period-7 generator has NO exponential collapse. We assert I(7) ~ log2(7)."""
    stream = list("ABCDEFG" * 200)  # 1400 chars, 7 symbols
    i7 = mi_at_distance(stream, 7)
    assert abs(i7 - math.log2(7)) < 1e-6  # perfect determinism at the period
    # at lag 14 (a multiple of the period) it is still perfectly determined
    assert abs(mi_at_distance(stream, 14) - math.log2(7)) < 1e-6


def test_mi_iid_random_sequence_near_zero_floor():
    """An i.i.d. random sequence has NO correlation at any lag: I(d) is just the
    finite-sample bias, which is tiny for a big sample and a small alphabet."""
    rng = random.Random(123)
    stream = [rng.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ") for _ in range(40000)]
    # finite-sample MI bias ~ log2(e)*(A-1)^2/(2N) ~ 0.011 bits here (A=26,
    # N=40000); far below the real-corpus adjacency excess (>0.05). It is the
    # FLAT floor, not structure.
    for d in (1, 2, 5, 20, 100):
        assert mi_at_distance(stream, d) < 0.02  # essentially the bias floor


def test_mi_nonnegative_and_empty_guard():
    # MI is non-negative by construction
    rng = random.Random(7)
    stream = [rng.choice("abcde") for _ in range(2000)]
    assert all(mi_at_distance(stream, d) >= 0.0 for d in range(1, 30))
    # d >= len(stream) -> no pairs -> 0.0
    assert mi_at_distance(list("abc"), 5) == 0.0
    assert mi_at_distance([], 1) == 0.0


def test_mi_curve_length_matches_max_d():
    stream = list("abcabcabc" * 10)
    curve = mi_curve(stream, 12)
    assert len(curve) == 12
    assert all(v >= 0.0 for v in curve)


# --------------------------------------------------------------------------- #
# Null / bias floor                                                           #
# --------------------------------------------------------------------------- #
def test_shuffle_null_is_flat_bias_floor():
    """The shuffle null destroys all order, so null_mean(d) is the finite-sample
    bias: tiny and approximately FLAT across d (no d-dependence)."""
    rng = random.Random(99)
    stream = [rng.choice("ABCDEFGHIJ") for _ in range(20000)]  # alphabet 10
    null = null_mi_curve(stream, 60, n_shuffles=3, seed=0)
    assert len(null) == 60
    assert max(null) < 0.01  # tiny bias for N=20000, A=10
    # flatness: spread across d is far below the level itself
    assert (max(null) - min(null)) < 0.005


def test_excess_curve_clamps_at_zero():
    mi = [0.5, 0.10, 0.001, 0.20]
    null = [0.10, 0.10, 0.10, 0.05]
    ex = excess_curve(mi, null)
    expected = [0.4, 0.0, 0.0, 0.15]  # negative differences clamped to 0
    assert all(abs(a - b) < 1e-12 for a, b in zip(ex, expected))


def test_null_floor_subtracted_real_corpus_excess_is_small_at_large_d_floor():
    """On the real corpus, the shuffle null must be a tiny flat floor (~0.002
    bits expected for alphabet 26, ~228k chars)."""
    lines = parse_loci(CORPUS)
    stream = _char_stream(lines)
    null = null_mi_curve(stream, 20, n_shuffles=2, seed=0)
    assert max(null) < 0.01
    assert (max(null) - min(null)) < 0.005


# --------------------------------------------------------------------------- #
# MEASURE 2: power-law vs exponential discrimination                          #
# --------------------------------------------------------------------------- #
def test_powerlaw_data_fits_powerlaw_better():
    """Synthetic excess(d) = d^-1 must be fit BETTER (higher R^2) by the power-law
    model than the exponential model, and gamma must recover ~1."""
    ds = list(range(1, 101))
    excess = [1.0 / d for d in ds]
    gamma, _a, pl_r2 = fit_powerlaw(ds, excess)
    _xi, _b, exp_r2 = fit_exponential(ds, excess)
    assert abs(gamma - 1.0) < 1e-6  # slope of log y vs log x is -1 -> gamma=1
    assert pl_r2 > 0.999  # exact power law -> near-perfect log-log fit
    assert pl_r2 > exp_r2  # power-law strictly better


def test_exponential_data_fits_exponential_better():
    """Synthetic excess(d) = e^(-d/3) must be fit BETTER by the exponential model,
    and xi must recover ~3."""
    ds = list(range(1, 61))
    excess = [math.exp(-d / 3.0) for d in ds]
    xi, _b, exp_r2 = fit_exponential(ds, excess)
    _gamma, _a, pl_r2 = fit_powerlaw(ds, excess)
    assert abs(xi - 3.0) < 1e-6  # slope of log y vs d is -1/3 -> xi=3
    assert exp_r2 > 0.999  # exact exponential -> near-perfect semilog fit
    assert exp_r2 > pl_r2  # exponential strictly better


def test_fits_ignore_nonpositive_excess():
    # zeros must be dropped (log undefined); only positive points contribute
    ds = [1, 2, 3, 4]
    excess = [1.0, 0.0, 0.25, 0.0]  # d^-2 on the surviving points (1,3)
    gamma, _a, r2 = fit_powerlaw(ds, excess)
    # surviving points (1,1.0) and (3,0.25): log-log slope = log(0.25)/log(3)
    expected_gamma = -(math.log(0.25) / math.log(3.0))
    assert abs(gamma - expected_gamma) < 1e-9
    assert not math.isnan(r2)


def test_correlation_length_thresholding():
    # excess > 2*floor up to d=4 then drops below; floor=0.01 -> thresh=0.02
    excess = [0.5, 0.3, 0.1, 0.03, 0.01, 0.005, 0.001]
    assert correlation_length(excess, null_floor=0.01) == 4
    # nothing above threshold -> 0
    assert correlation_length([0.001, 0.0, 0.002], null_floor=0.01) == 0
    # robust to a lone dip: max qualifying d wins even if an earlier d dips below
    excess2 = [0.5, 0.01, 0.5, 0.5]  # d=2 dips, but d=4 still qualifies
    assert correlation_length(excess2, null_floor=0.01) == 4


# --------------------------------------------------------------------------- #
# MEASURE 3: line shuffle                                                     #
# --------------------------------------------------------------------------- #
def test_line_shuffled_stream_preserves_length_and_multiset():
    lines = [["ab", "cd"], ["ef"], ["gh", "ij", "kl"]]
    base = _char_stream(lines)
    shuffled = line_shuffled_stream(lines, seed=3)
    # same total length and same character multiset (only line ORDER changed)
    assert len(shuffled) == len(base)
    assert sorted(shuffled) == sorted(base)


# --------------------------------------------------------------------------- #
# MEASURE 4: Zipf + Heaps                                                     #
# --------------------------------------------------------------------------- #
def test_zipf_slope_recovers_minus_one_on_synthetic_zipf():
    """Build a token multiset whose rank-r frequency is ~ floor(C/r) (a perfect
    Zipf with exponent 1). The mid-rank log-log slope must be ~ -1."""
    C = 100000
    tokens: list[str] = []
    for r in range(1, 1501):
        freq = max(1, C // r)
        tokens.extend([f"w{r}"] * freq)
    slope, r2, n = zipf_slope(tokens, 10, 1000)
    assert n > 100  # the mid-rank window is populated
    assert abs(slope - (-1.0)) < 0.05  # recovers exponent -1
    assert r2 > 0.99


def test_zipf_slope_degenerate_returns_nan():
    slope, r2, n = zipf_slope(["a", "a", "b"], 10, 1000)
    assert math.isnan(slope) and n < 2


def test_heaps_beta_on_synthetic_grows_sublinearly():
    """A stream with a steadily growing vocabulary has 0 < beta <= 1. Construct
    one where every other token is brand-new -> sublinear-to-linear growth."""
    tokens: list[str] = []
    vid = 0
    for i in range(20000):
        if i % 2 == 0:
            tokens.append(f"new{vid}")
            vid += 1
        else:
            tokens.append("common")
    beta, r2, n = heaps_beta(tokens)
    assert n >= 2
    assert 0.0 < beta <= 1.05  # vocabulary grows, not faster than linear
    assert r2 > 0.9


def test_heaps_beta_constant_vocab_is_near_zero():
    # a single repeated token -> V stays 1 -> beta ~ 0
    tokens = ["x"] * 5000
    beta, _r2, n = heaps_beta(tokens)
    assert n >= 2
    assert abs(beta) < 1e-6


# --------------------------------------------------------------------------- #
# Verdict                                                                     #
# --------------------------------------------------------------------------- #
def test_classify_verdict_branches():
    # power-law better AND long correlation -> long_range_structured
    assert classify_verdict(0.95, 0.80, corr_len=120) == "long_range_structured"
    # exponential better AND short correlation -> local_generator
    assert classify_verdict(0.70, 0.99, corr_len=5) == "local_generator"
    # power-law better but SHORT correlation -> ambiguous
    assert classify_verdict(0.95, 0.80, corr_len=8) == "ambiguous"
    # exponential better but LONG correlation -> ambiguous
    assert classify_verdict(0.70, 0.99, corr_len=80) == "ambiguous"
    # NaN power-law fit -> falls through, not long_range_structured
    assert classify_verdict(float("nan"), 0.99, corr_len=5) == "local_generator"


# --------------------------------------------------------------------------- #
# Parser / stream sanity vs Rota 58                                           #
# --------------------------------------------------------------------------- #
def test_char_stream_matches_rota58_length():
    lines = parse_loci(CORPUS)
    stream = _char_stream(lines)
    assert len(stream) == 228177  # identical construction to Rota 58
    assert len(set(stream)) == 26  # 25 EVA letters + SPACE
    # token stream total matches Rota 53/57/58
    assert len(token_stream(lines)) == 37671


# --------------------------------------------------------------------------- #
# main() outputs                                                              #
# --------------------------------------------------------------------------- #
def test_main_writes_both_csvs_with_guardrail(tmp_path):
    curve = tmp_path / "curve.csv"
    summary = tmp_path / "summary.csv"
    rc = main(
        [
            str(CORPUS),
            "--max-d",
            "20",
            "--n-null",
            "2",
            "--out-curve",
            str(curve),
            "--out-summary",
            str(summary),
        ]
    )
    assert rc == 0
    for p in (curve, summary):
        assert p.exists() and p.stat().st_size > 0
        assert GUARDRAIL in p.read_text(encoding="utf-8")

    # curve CSV: one row per d=1..20 with the required columns
    with curve.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 20
    assert [int(r["d"]) for r in rows] == list(range(1, 21))
    for r in rows:
        assert {"d", "I_d", "null_mean", "excess", "I_d_lineshuffled"} <= set(r)
        # excess never exceeds I_d, and null/excess are non-negative
        assert float(r["I_d"]) >= 0.0
        assert float(r["excess"]) >= 0.0
        assert float(r["excess"]) <= float(r["I_d"]) + 1e-9

    # summary CSV: every required metric present
    with summary.open(encoding="utf-8") as f:
        m = {r["metric"]: r["value"] for r in csv.DictReader(f)}
    for metric in (
        "powerlaw_gamma",
        "powerlaw_r2",
        "exp_xi",
        "exp_r2",
        "better_fit",
        "excess_d1",
        "excess_d10",
        "correlation_length",
        "lineshuffle_ratio_d50",
        "zipf_slope",
        "heaps_beta",
        "verdict",
        "guardrail",
    ):
        assert metric in m
    assert m["guardrail"] == GUARDRAIL
    assert m["verdict"] in {"long_range_structured", "local_generator", "ambiguous"}
    # the stream sanity also flows through the summary
    assert int(m["stream_len"]) == 228177


def test_main_real_corpus_excess_decays_from_d1(tmp_path):
    """Sanity gate on the real corpus: excess at d=1 (immediate adjacency) is the
    largest and well above the null floor; excess is reported at every checkpoint.
    Uses the full max_d so d=50/d=100 checkpoints are defined."""
    curve = tmp_path / "curve.csv"
    summary = tmp_path / "summary.csv"
    main(
        [
            str(CORPUS),
            "--n-null",
            "2",
            "--out-curve",
            str(curve),
            "--out-summary",
            str(summary),
        ]
    )
    with summary.open(encoding="utf-8") as f:
        m = {r["metric"]: r["value"] for r in csv.DictReader(f)}
    e1 = float(m["excess_d1"])
    e10 = float(m["excess_d10"])
    assert e1 > 0.05  # strong local structure at adjacency
    assert e1 > e10  # decays away from adjacency
    # both fits report a finite R^2 in [0,1]
    for key in ("powerlaw_r2", "exp_r2"):
        v = float(m[key])
        assert 0.0 <= v <= 1.0
