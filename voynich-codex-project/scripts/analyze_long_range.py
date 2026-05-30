#!/usr/bin/env python3
"""Rota 59: long-range correlation — the ONE statistic that separates a simple
LOCAL generator from any real-language-like (even heavily encoded) system.

Rota 58 settled that Voynichese is NOT natural-language prose (char h2=2.15 bits
<< natural; line-position glyph binding; elevated adjacent repetition). But every
one of those is a LOCAL statistic — reproducible by *all* surviving hypotheses:
a heavily-encoded real language, a constructed language, OR a low-content local
generator (Markov / line-template / self-citation). They do not discriminate.

The discriminating axis is LONG-RANGE correlation. A deterministic transform of
real language (cipher, abbreviation) preserves the source's long-range structure,
so mutual information between symbols a distance d apart decays as a POWER LAW
I(d) ~ d^(-gamma), persisting to large d. A simple LOCAL generator has a finite
memory: its I(d) collapses EXPONENTIALLY, I(d) ~ e^(-d/xi), to the finite-sample
noise floor within a few units. This is the classic Lin & Tegmark / Montemurro
diagnostic.

MEASURE 1 -- character-level MI decay (PRIMARY; alphabet ~26, ~228k chars, so the
  finite-sample MI bias is ~0.002 bits, statistically clean). Same space-joined
  char stream as Rota 58. For d=1..150: I(d) = sum p(a,b) log2[p(a,b)/(p(a)p(b))]
  over adjacent-at-distance-d pairs. Per-d NULL: 5 seeded full-stream shuffles ->
  null_mean(d) (the flat bias floor). excess(d) = max(0, I(d) - null_mean(d)).

MEASURE 2 -- fit power-law vs exponential to excess(d) over the range excess>0:
  power-law = OLS of log(excess) on log(d) -> slope=-gamma; exponential = OLS of
  log(excess) on d -> slope=-1/xi. Report both R^2, which fits better, excess at
  d=1/10/50/100, and correlation_length = max d with excess(d) > 2x null floor.

MEASURE 3 -- line-shuffle control. Shuffle the ORDER of locus-lines (keep each
  line's internal char sequence), rebuild the stream, recompute I(d). If real
  I(d) ~ line-shuffled at all d, the long-range signal is WITHIN-line only (local,
  line-as-unit). If real > line-shuffled beyond a line length (~50 chars), there
  is genuine CROSS-line structure (topic/narrative).

MEASURE 4 -- Zipf-Mandelbrot token rank-frequency slope over mid ranks (~10-1000;
  natural language ~ -1) and Heaps' law vocabulary growth V ~ N^beta (natural
  ~ 0.4-0.6).

VERDICT:
  - power-law fits better AND correlation_length > 50 -> "long_range_structured"
    (RULES OUT a simple local generator; consistent with encoded real language OR
    a sophisticated structured/constructed system -- NOT a clean discriminator
    between those, but it kills simple-Markov/local-template).
  - exponential fits better AND correlation_length < 10 -> "local_generator".
  - otherwise -> "ambiguous".
  Long-range MI can also arise from topic/section clustering: that is exactly what
  MEASURE 3 isolates. Interpretation stays nuanced; coordinator + cryptanalyst
  weigh it. This is NOT a decipherment. Guardrail in every output CSV.
"""
from __future__ import annotations

import argparse
import collections
import csv
import math
import random
from pathlib import Path

from scripts.analyze_language_signature import _char_stream, parse_loci

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota59_long_range_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"

MAX_D = 150
N_NULL_SHUFFLES = 5
# Zipf mid-rank window (1-indexed ranks, inclusive) and Heaps checkpoints.
ZIPF_RANK_LO = 10
ZIPF_RANK_HI = 1000


# --------------------------------------------------------------------------- #
# Measure 1: distance-d mutual information                                    #
# --------------------------------------------------------------------------- #
def mi_at_distance(stream: list[str], d: int) -> float:
    """I(c_i ; c_{i+d}) in bits, plug-in (MLE) estimator.

    Counts every (c_i, c_{i+d}) pair, forms the joint and the two marginals over
    that SAME population of pairs (so both marginals share the denominator
    N = len(stream) - d), and returns
        I = sum_{a,b} p(a,b) * log2[ p(a,b) / (p(a) p(b)) ].
    The marginals are taken from the actual left/right members of the counted
    pairs (not the global unigram), which is the unbiased plug-in form for a
    fixed lag and makes I >= 0 exactly.
    """
    n = len(stream) - d
    if n <= 0:
        return 0.0
    joint: collections.Counter = collections.Counter()
    left: collections.Counter = collections.Counter()
    right: collections.Counter = collections.Counter()
    for i in range(n):
        a = stream[i]
        b = stream[i + d]
        joint[(a, b)] += 1
        left[a] += 1
        right[b] += 1
    mi = 0.0
    for (a, b), c in joint.items():
        p_ab = c / n
        p_a = left[a] / n
        p_b = right[b] / n
        if p_ab > 0 and p_a > 0 and p_b > 0:
            mi += p_ab * math.log2(p_ab / (p_a * p_b))
    return mi


def mi_curve(stream: list[str], max_d: int) -> list[float]:
    """[I(1), I(2), ..., I(max_d)] over a character stream."""
    return [mi_at_distance(stream, d) for d in range(1, max_d + 1)]


def null_mi_curve(
    stream: list[str], max_d: int, n_shuffles: int, seed: int
) -> list[float]:
    """Per-d finite-sample bias floor: mean I(d) over n_shuffles full shuffles.

    Each shuffle destroys ALL order, so any residual I(d) is pure finite-sample
    bias (~log2(e) * (A-1)^2 / (2N) for alphabet A). Averaging several seeded
    shuffles smooths that floor; it is ~flat in d.
    """
    if n_shuffles <= 0:
        return [0.0] * max_d
    rng = random.Random(seed)
    totals = [0.0] * max_d
    work = stream[:]
    for _ in range(n_shuffles):
        rng.shuffle(work)
        curve = mi_curve(work, max_d)
        for k in range(max_d):
            totals[k] += curve[k]
    return [t / n_shuffles for t in totals]


def excess_curve(mi: list[float], null_mean: list[float]) -> list[float]:
    """excess(d) = max(0, I(d) - null_mean(d)), elementwise."""
    return [max(0.0, m - nu) for m, nu in zip(mi, null_mean)]


# --------------------------------------------------------------------------- #
# Measure 2: power-law vs exponential fits                                    #
# --------------------------------------------------------------------------- #
def _ols(xs: list[float], ys: list[float]) -> tuple[float, float, float]:
    """Ordinary least squares y = a + b x. Returns (slope b, intercept a, R^2).

    R^2 is 1 - SS_res/SS_tot; if y has zero variance R^2 is defined as 0.0 (no
    explanatory power to claim). Needs >= 2 points.
    """
    n = len(xs)
    if n < 2:
        return float("nan"), float("nan"), float("nan")
    mx = sum(xs) / n
    my = sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    sxy = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    if sxx == 0:
        return float("nan"), float("nan"), float("nan")
    b = sxy / sxx
    a = my - b * mx
    ss_tot = sum((y - my) ** 2 for y in ys)
    ss_res = sum((y - (a + b * x)) ** 2 for x, y in zip(xs, ys))
    r2 = 1.0 - ss_res / ss_tot if ss_tot > 0 else 0.0
    return b, a, r2


def fit_powerlaw(ds: list[int], excess: list[float]) -> tuple[float, float, float]:
    """OLS of log(excess) on log(d) over points with excess>0.

    Returns (gamma, intercept, R^2) where slope = -gamma (so a decaying power law
    gives gamma > 0). Uses only positive-excess points; needs >= 2 of them.
    """
    xs = [math.log(d) for d, e in zip(ds, excess) if e > 0]
    ys = [math.log(e) for e in excess if e > 0]
    b, a, r2 = _ols(xs, ys)
    gamma = -b if not math.isnan(b) else float("nan")
    return gamma, a, r2


def fit_exponential(ds: list[int], excess: list[float]) -> tuple[float, float, float]:
    """OLS of log(excess) on d over points with excess>0.

    Returns (xi, intercept, R^2) where slope = -1/xi (decaying exponential gives
    xi > 0). xi is the e-folding correlation length of the exponential model.
    """
    xs = [float(d) for d, e in zip(ds, excess) if e > 0]
    ys = [math.log(e) for e in excess if e > 0]
    b, a, r2 = _ols(xs, ys)
    xi = (-1.0 / b) if (not math.isnan(b) and b != 0) else float("nan")
    return xi, a, r2


def correlation_length(excess: list[float], null_floor: float) -> int:
    """Largest d (1-indexed) with excess(d) > 2 * null_floor; 0 if none.

    null_floor is a single representative bias level (mean of null_mean over d).
    Using the max qualifying d (not the first failure) is robust to a lone dip.
    """
    thresh = 2.0 * null_floor
    best = 0
    for i, e in enumerate(excess, start=1):
        if e > thresh:
            best = i
    return best


# --------------------------------------------------------------------------- #
# Measure 3: line-shuffle control                                             #
# --------------------------------------------------------------------------- #
def line_shuffled_stream(lines: list[list[str]], seed: int) -> list[str]:
    """Rebuild the char stream after shuffling the ORDER of locus-lines.

    Each line's internal token/char sequence is preserved; only the sequence of
    lines is permuted. This keeps every within-line correlation intact and breaks
    only cross-line (document/topic) order, so comparing I(d) real vs this isolates
    cross-line long-range structure.
    """
    rng = random.Random(seed)
    shuffled = lines[:]
    rng.shuffle(shuffled)
    return _char_stream(shuffled)


# --------------------------------------------------------------------------- #
# Measure 4: Zipf-Mandelbrot and Heaps                                        #
# --------------------------------------------------------------------------- #
def token_stream(lines: list[list[str]]) -> list[str]:
    """Flat token list in corpus order (line by line)."""
    return [t for line in lines for t in line]


def zipf_slope(tokens: list[str], rank_lo: int, rank_hi: int) -> tuple[float, float, int]:
    """Slope of log(freq) vs log(rank) over a mid-rank window.

    Ranks are 1-indexed by descending frequency (ties broken by token for a
    deterministic order). Returns (slope, R^2, n_points). Natural language ~ -1.
    """
    freqs = sorted(collections.Counter(tokens).values(), reverse=True)
    pts = [
        (r, f)
        for r, f in enumerate(freqs, start=1)
        if rank_lo <= r <= rank_hi and f > 0
    ]
    if len(pts) < 2:
        return float("nan"), float("nan"), len(pts)
    xs = [math.log(r) for r, _ in pts]
    ys = [math.log(f) for _, f in pts]
    b, _a, r2 = _ols(xs, ys)
    return b, r2, len(pts)


def heaps_beta(tokens: list[str], n_checkpoints: int = 12) -> tuple[float, float, int]:
    """Heaps' law exponent beta from V vs N at log-spaced checkpoints.

    V(N) = number of distinct types seen in the first N tokens. OLS of log(V) on
    log(N) over checkpoints -> slope = beta. Natural language ~ 0.4-0.6.
    """
    total = len(tokens)
    if total < 2:
        return float("nan"), float("nan"), 0
    seen: set[str] = set()
    # log-spaced checkpoints from a small floor up to total
    lo = max(10, total // 1000)
    checkpoints = sorted(
        {
            int(round(math.exp(t)))
            for t in _linspace(math.log(lo), math.log(total), n_checkpoints)
        }
    )
    checkpoints = [c for c in checkpoints if 1 <= c <= total]
    pts: list[tuple[int, int]] = []
    idx = 0
    next_cp = 0
    for n in range(1, total + 1):
        seen.add(tokens[n - 1])
        if next_cp < len(checkpoints) and n == checkpoints[next_cp]:
            pts.append((n, len(seen)))
            next_cp += 1
    if len(pts) < 2:
        return float("nan"), float("nan"), len(pts)
    xs = [math.log(n) for n, _ in pts]
    ys = [math.log(v) for _, v in pts]
    b, _a, r2 = _ols(xs, ys)
    return b, r2, len(pts)


def _linspace(lo: float, hi: float, n: int) -> list[float]:
    if n <= 1:
        return [hi]
    step = (hi - lo) / (n - 1)
    return [lo + step * i for i in range(n)]


# --------------------------------------------------------------------------- #
# Verdict                                                                     #
# --------------------------------------------------------------------------- #
def classify_verdict(
    powerlaw_r2: float,
    exp_r2: float,
    corr_len: int,
) -> str:
    """Long-range structure verdict from fit quality + correlation length.

    - power-law fits better (higher R^2) AND corr_len > 50 -> long_range_structured
    - exponential fits better AND corr_len < 10 -> local_generator
    - else -> ambiguous
    NaNs (degenerate fit) fall through to ambiguous.
    """
    pl = powerlaw_r2 if not math.isnan(powerlaw_r2) else -1.0
    ex = exp_r2 if not math.isnan(exp_r2) else -1.0
    if pl > ex and corr_len > 50:
        return "long_range_structured"
    if ex > pl and corr_len < 10:
        return "local_generator"
    return "ambiguous"


# --------------------------------------------------------------------------- #
# IO                                                                          #
# --------------------------------------------------------------------------- #
def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _fmt(x: float, nd: int = 6) -> str:
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return "nan" if math.isnan(x) else ("inf" if x > 0 else "-inf")
    return str(round(x, nd))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("corpus", nargs="?", default=str(DEFAULT_CORPUS))
    p.add_argument("--max-d", type=int, default=MAX_D)
    p.add_argument("--n-null", type=int, default=N_NULL_SHUFFLES)
    p.add_argument("--seed", type=int, default=0)
    d = ROOT / "data" / "derived"
    p.add_argument("--out-curve", default=str(d / "long_range_mi_zl3b.csv"))
    p.add_argument("--out-summary", default=str(d / "long_range_summary_zl3b.csv"))
    return p.parse_args(argv)


def _at(curve: list[float], d: int) -> float:
    """1-indexed lookup into a per-distance curve (NaN if out of range)."""
    return curve[d - 1] if 1 <= d <= len(curve) else float("nan")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    lines = parse_loci(Path(args.corpus))
    stream = _char_stream(lines)
    max_d = args.max_d

    # MEASURE 1: real MI curve, null floor, excess
    mi = mi_curve(stream, max_d)
    null_mean = null_mi_curve(stream, max_d, args.n_null, args.seed)
    excess = excess_curve(mi, null_mean)
    null_floor = sum(null_mean) / len(null_mean) if null_mean else 0.0

    # MEASURE 3: line-shuffle control curve
    ls_stream = line_shuffled_stream(lines, args.seed + 1)
    mi_ls = mi_curve(ls_stream, max_d)

    # MEASURE 2: fits over excess>0
    ds = list(range(1, max_d + 1))
    gamma, _pa, pl_r2 = fit_powerlaw(ds, excess)
    xi, _ea, exp_r2 = fit_exponential(ds, excess)
    corr_len = correlation_length(excess, null_floor)
    better = (
        "power_law"
        if (not math.isnan(pl_r2))
        and (math.isnan(exp_r2) or pl_r2 >= exp_r2)
        else "exponential"
    )

    # MEASURE 4: Zipf + Heaps
    toks = token_stream(lines)
    z_slope, _z_r2, _z_n = zipf_slope(toks, ZIPF_RANK_LO, ZIPF_RANK_HI)
    h_beta, _h_r2, _h_n = heaps_beta(toks)

    # line-shuffle ratios (real / line-shuffled) at key distances
    def _ratio(d: int) -> float:
        a = _at(excess, d)
        # compare on the same excess footing: subtract the same null floor from
        # the line-shuffled MI so both are above the bias floor
        b = max(0.0, _at(mi_ls, d) - null_floor)
        if b <= 0:
            return float("inf") if a > 0 else float("nan")
        return a / b

    ls_ratio_d50 = _ratio(50)
    ls_ratio_d100 = _ratio(100)

    verdict = classify_verdict(pl_r2, exp_r2, corr_len)

    # --- per-distance CSV ---
    curve_rows = [
        {
            "d": d,
            "I_d": _fmt(mi[d - 1]),
            "null_mean": _fmt(null_mean[d - 1]),
            "excess": _fmt(excess[d - 1]),
            "I_d_lineshuffled": _fmt(mi_ls[d - 1]),
            "semantic_guardrail": GUARDRAIL,
        }
        for d in ds
    ]
    write_csv(
        Path(args.out_curve),
        curve_rows,
        ["d", "I_d", "null_mean", "excess", "I_d_lineshuffled", "semantic_guardrail"],
    )

    # --- summary CSV ---
    summary_rows = [
        {"metric": "stream_len", "value": str(len(stream))},
        {"metric": "alphabet_size", "value": str(len(set(stream)))},
        {"metric": "max_d", "value": str(max_d)},
        {"metric": "null_floor", "value": _fmt(null_floor, 8)},
        {"metric": "powerlaw_gamma", "value": _fmt(gamma)},
        {"metric": "powerlaw_r2", "value": _fmt(pl_r2)},
        {"metric": "exp_xi", "value": _fmt(xi)},
        {"metric": "exp_r2", "value": _fmt(exp_r2)},
        {"metric": "better_fit", "value": better},
        {"metric": "excess_d1", "value": _fmt(_at(excess, 1))},
        {"metric": "excess_d10", "value": _fmt(_at(excess, 10))},
        {"metric": "excess_d50", "value": _fmt(_at(excess, 50))},
        {"metric": "excess_d100", "value": _fmt(_at(excess, 100))},
        {"metric": "correlation_length", "value": str(corr_len)},
        {"metric": "I_real_d50", "value": _fmt(_at(mi, 50))},
        {"metric": "I_lineshuffled_d50", "value": _fmt(_at(mi_ls, 50))},
        {"metric": "I_real_d100", "value": _fmt(_at(mi, 100))},
        {"metric": "I_lineshuffled_d100", "value": _fmt(_at(mi_ls, 100))},
        {"metric": "lineshuffle_ratio_d50", "value": _fmt(ls_ratio_d50, 4)},
        {"metric": "lineshuffle_ratio_d100", "value": _fmt(ls_ratio_d100, 4)},
        {"metric": "zipf_slope", "value": _fmt(z_slope, 4)},
        {"metric": "heaps_beta", "value": _fmt(h_beta, 4)},
        {"metric": "verdict", "value": verdict},
        {"metric": "guardrail", "value": GUARDRAIL},
    ]
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    # --- console report ---
    print(
        f"stream_len={len(stream)} alphabet={len(set(stream))} max_d={max_d} "
        f"null_floor={null_floor:.6g}"
    )
    print(
        f"excess d1={_at(excess,1):.6g} d10={_at(excess,10):.6g} "
        f"d50={_at(excess,50):.6g} d100={_at(excess,100):.6g} "
        f"correlation_length={corr_len}"
    )
    print(
        f"power_law: gamma={gamma:.4g} R2={pl_r2:.4f}  |  "
        f"exponential: xi={xi:.4g} R2={exp_r2:.4f}  -> better={better}"
    )
    print(
        f"line-shuffle: I_real(50)={_at(mi,50):.6g} I_ls(50)={_at(mi_ls,50):.6g} "
        f"ratio_d50={ls_ratio_d50:.4g} ratio_d100={ls_ratio_d100:.4g}"
    )
    print(f"zipf_slope={z_slope:.4f} heaps_beta={h_beta:.4f}")
    print(f"VERDICT={verdict}")
    print(f"curve_csv={args.out_curve}")
    print(f"summary_csv={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
