#!/usr/bin/env python3
"""Rota 62: is a SIMPLE LOCAL CONTENTLESS GENERATOR sufficient to reproduce ALL
of Voynich's measured statistics simultaneously?

THE capstone of the CLOSED "what is Voynichese" arc (R43-R61). Established: the
token system is morphologically RICH but syntactically THIN; it is NOT natural
prose (char h2=2.15 << natural); character mutual information collapses to the
noise floor by d~=15 (the token scale) with no mid-range prose dependency; it
compresses ~ like its own bag-of-words (word order carries ~1-3% extra, vs
12-25% in natural language); and re-segmentation (BPE) does NOT revive hidden
syntax (R61). Every surviving local statistic is reproducible "by all surviving
hypotheses" -- but no one had checked whether ONE simple local process can match
the WHOLE battery AT ONCE.

This route builds that process and tests it head-to-head against the real corpus.

THE GENERATOR -- a parametric LOCAL process with four interpretable, TOGGLEABLE
mechanisms (each ablatable). It is contentless: it never assigns meaning, it only
re-uses the corpus's own token inventory and surface habits.

  1. base (bag-of-real-words). Sample whole REAL tokens i.i.d. from the token-
     unigram frequency distribution; impose the real per-line token-count
     distribution (each synthetic line draws its length from the real line-length
     distribution). This alone reproduces Zipf / Heaps / within-token char stats
     (h2) almost by construction -- that is EXPECTED and fine (the token inventory
     IS the corpus's morphology; we are testing whether anything ABOVE the bag is
     needed).
  2. section_cond. Make the token-unigram distribution SECTION-CONDITIONED (a per-
     section word-frequency table). Each synthetic line inherits the section of
     the real line at the same index, so the section *sequence* is the real one.
     Needed to reproduce the weak cross-line topical tail (R56/R59): it is a
     topic-vocabulary TABLE, not syntax.
  3. self_citation. With probability p_rep, instead of drawing fresh, REPEAT a
     token copied from the last W tokens (default W=1 -> the immediately previous
     token). Tuned so the synthetic adjacent-repeat rate ~= the real 0.875%.
  4. line_edge_bias. Bias line-INITIAL tokens toward those whose FIRST glyph is a
     gallows (p/t) and line-FINAL tokens toward the real line-final token
     distribution, to reproduce LAAFU (line-as-a-functional-unit). Tuned to match
     the real line-initial gallows fraction (~0.185 vs corpus ~0.041).

The synthetic corpus has the SAME size (~37.7k tokens, 5216 lines, same line
geometry) and is fully seeded / reproducible.

MEASURE THE FULL BATTERY on BOTH real and synthetic (reusing the R58/R59/R60
functions): char h2; adjacent-repeat rate; LAAFU I(word;position) + line-initial
gallows fraction; char MI I(d) at d=1,2,5,10,50,100 + correlation length; Zipf
slope; Heaps beta; gain_over_wordunigram (lzma). A MATCH TABLE reports
metric | real | generator | |delta| | tolerance | within_tol.

ABLATION reports which mechanisms are NECESSARY by measuring the battery for
base only; base+section_cond; base+section_cond+self_citation; full.

VERDICT:
  - full generator matches ALL key metrics within tolerance -> "generator_sufficient":
    a simple local contentless process reproduces Voynich's entire statistical
    profile; nothing in the statistics REQUIRES meaning -> strongly upweights
    generator/constructed.
  - generator FAILS >=1 key metric despite the mechanisms -> "generator_insufficient":
    name the resisting signature; Voynich has structure a simple local generator
    cannot capture.

CAVEAT (in the output): "generator_sufficient" shows meaning is NOT REQUIRED to
explain the statistics -- it does NOT prove the text is meaningless. A meaningful
text could still carry these same stats. This is NOT a decipherment. Guardrail in
every output CSV.
"""
from __future__ import annotations

import argparse
import collections
import csv
import math
import random
import re
from pathlib import Path

from scripts.analyze_compressibility import (
    bits_per_char,
    compress_size_bits,
    gain,
    stream_from_words,
)
from scripts.analyze_compressibility import gen_word_unigram
from scripts.analyze_language_signature import (
    SPACE,
    _char_stream,
    adjacent_repeats,
    char_entropies,
    laafu_pairs,
    mutual_information,
    parse_loci,
)
from scripts.analyze_long_range import (
    correlation_length,
    excess_curve,
    heaps_beta,
    mi_at_distance,
    mi_curve,
    null_mi_curve,
    token_stream,
    zipf_slope,
)
from scripts.analyze_nucleus import classify_section, clean_token

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota62_generator_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"

# Gallows glyphs that open a token in the LAAFU line-initial bias. EVA p/t are
# the two ordinary gallows; the real line-initial first-glyph distribution is
# dominated by them, so they are the target of the edge bias.
GALLOWS = ("p", "t")

# Distance checkpoints for the char-MI battery (matches R59 framing).
MI_CHECKPOINTS = (1, 2, 5, 10, 50, 100)
MAX_D = 150
N_NULL_SHUFFLES = 5
ZIPF_RANK_LO = 10
ZIPF_RANK_HI = 1000

# The four mechanisms, in cumulative ablation order.
MECHANISMS = ("base", "section_cond", "self_citation", "line_edge_bias")

# Per-mechanism toggles for the cumulative ablation ladder.
ABLATION_LADDER = [
    ("base", {"section_cond": False, "self_citation": False, "line_edge_bias": False}),
    ("base+section_cond", {"section_cond": True, "self_citation": False, "line_edge_bias": False}),
    (
        "base+section_cond+self_citation",
        {"section_cond": True, "self_citation": True, "line_edge_bias": False},
    ),
    (
        "full",
        {"section_cond": True, "self_citation": True, "line_edge_bias": True},
    ),
]


# --------------------------------------------------------------------------- #
# Corpus parse with per-line section labels                                   #
# --------------------------------------------------------------------------- #
_LOC = re.compile(r"^<(f[0-9]+[rv]\d?)\.\d+[^>]*>\s*(.*)$")


def parse_loci_with_section(path: Path) -> tuple[list[list[str]], list[str]]:
    """Return (lines, sections) where lines mirror analyze_language_signature.

    `lines` is exactly `parse_loci(path)` (same tokenization, same line set), and
    `sections[i]` is the content section of `lines[i]` derived from its folio via
    analyze_nucleus.classify_section. Keeping the two lists index-aligned lets the
    generator inherit the REAL per-line section sequence (so section_cond does not
    need to model section dynamics -- it reuses the corpus's own section order).
    """
    lines: list[list[str]] = []
    sections: list[str] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        m = _LOC.match(raw_line)
        if not m:
            continue
        folio = m.group(1)
        body = m.group(2).replace(",", ".")
        toks = [t for t in (clean_token(r) for r in body.split(".")) if t]
        if toks:
            lines.append(toks)
            sections.append(classify_section(folio))
    return lines, sections


# --------------------------------------------------------------------------- #
# Real-corpus profiles the generator samples from                             #
# --------------------------------------------------------------------------- #
def line_length_distribution(lines: list[list[str]]) -> tuple[list[int], list[int]]:
    """(lengths, weights): the empirical distribution of tokens-per-line.

    The generator draws each synthetic line's length from this distribution, so
    the synthetic line geometry matches the real one in expectation (and the
    total token count matches closely; the generator also pins the exact line
    COUNT by producing one synthetic line per real line, see `generate`).
    """
    c = collections.Counter(len(line) for line in lines)
    return list(c.keys()), list(c.values())


def token_unigram(lines: list[list[str]]) -> tuple[list[str], list[int]]:
    """Global token-frequency table (vocab, weights) over all tokens."""
    c = collections.Counter(t for line in lines for t in line)
    return list(c.keys()), list(c.values())


def section_unigrams(
    lines: list[list[str]], sections: list[str]
) -> dict[str, tuple[list[str], list[int]]]:
    """Per-section token-frequency tables {section -> (vocab, weights)}.

    This is the topic-vocabulary TABLE of mechanism 2: it carries the corpus's
    weak cross-line topicality as a static per-section word distribution, with NO
    syntax and NO cross-token dependency.
    """
    by_sec: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for line, sec in zip(lines, sections):
        for t in line:
            by_sec[sec][t] += 1
    return {sec: (list(c.keys()), list(c.values())) for sec, c in by_sec.items()}


def line_final_distribution(lines: list[list[str]]) -> tuple[list[str], list[int]]:
    """(vocab, weights) of the REAL line-final tokens (last token of each line).

    Mechanism 4 draws the synthetic line-final token from this distribution to
    reproduce the line-final habit half of LAAFU.
    """
    c = collections.Counter(line[-1] for line in lines if line)
    return list(c.keys()), list(c.values())


def gallows_initial_pool(
    vocab: list[str], weights: list[int]
) -> tuple[list[str], list[int]]:
    """Sub-distribution of tokens whose FIRST glyph is a gallows (p/t).

    Restricting the line-initial draw to this pool (with the same relative
    frequencies) is how mechanism 4 lifts the line-initial gallows fraction from
    the corpus baseline (~0.04) toward the real line-initial value (~0.185). If
    `p_initial_gallows` < 1 the draw mixes this pool with the full vocabulary.
    """
    g_v: list[str] = []
    g_w: list[int] = []
    for v, w in zip(vocab, weights):
        if v and v[0] in GALLOWS:
            g_v.append(v)
            g_w.append(w)
    return g_v, g_w


def real_line_initial_gallows_fraction(lines: list[list[str]]) -> float:
    """Fraction of lines (>=1 token) whose first token starts with a gallows.

    This is the LAAFU target the line_edge_bias mechanism is tuned to match.
    """
    n = 0
    hits = 0
    for line in lines:
        if line:
            n += 1
            if line[0][0] in GALLOWS:
                hits += 1
    return hits / n if n else 0.0


# --------------------------------------------------------------------------- #
# The generator                                                               #
# --------------------------------------------------------------------------- #
class GeneratorProfile:
    """Pre-computed sampling tables extracted once from the real corpus.

    Holds the line-length distribution, the global and per-section token-unigram
    tables, the line-final distribution, and the gallows-initial pools (global +
    per-section). All synthetic draws come from these; nothing in here encodes
    meaning -- they are surface-frequency tables only.
    """

    def __init__(self, lines: list[list[str]], sections: list[str]):
        self.lengths, self.length_w = line_length_distribution(lines)
        self.global_vocab, self.global_w = token_unigram(lines)
        self.section_tables = section_unigrams(lines, sections)
        self.final_vocab, self.final_w = line_final_distribution(lines)
        self.global_gallows = gallows_initial_pool(self.global_vocab, self.global_w)
        self.section_gallows = {
            sec: gallows_initial_pool(v, w)
            for sec, (v, w) in self.section_tables.items()
        }
        self.real_lengths = [len(line) for line in lines]
        self.real_sections = sections


def _draw(rng: random.Random, vocab: list[str], weights: list[int]) -> str:
    """One weighted i.i.d. draw; empty pool -> empty string (caller guards)."""
    if not vocab:
        return ""
    return rng.choices(vocab, weights=weights, k=1)[0]


def generate(
    profile: GeneratorProfile,
    *,
    section_cond: bool,
    self_citation: bool,
    line_edge_bias: bool,
    p_rep: float,
    rep_window: int,
    p_initial_gallows: float,
    seed: int,
) -> list[list[str]]:
    """Generate a synthetic corpus (list of token-lines) from the profile.

    Geometry: one synthetic line per real line, each synthetic line's length
    drawn from the real line-length distribution (so line COUNT is pinned and
    line LENGTH matches in distribution). Each synthetic line inherits the real
    line's section (used only when section_cond is on).

    Per token, in reading order within a line:
      * line_edge_bias on: position 0 draws from the gallows-initial pool with
        prob p_initial_gallows else from the body pool; the LAST position draws
        from the real line-final distribution.
      * self_citation on: at an interior/uncopyable position, with prob p_rep,
        copy a token uniformly from the last `rep_window` emitted tokens (>=1
        available) instead of drawing fresh -> lifts adjacent repetition.
      * otherwise: a fresh i.i.d. draw from the (section or global) token-unigram.

    The mechanisms compose; with all three booleans False this is pure
    bag-of-real-words (base).
    """
    rng = random.Random(seed)
    out: list[list[str]] = []
    for li in range(len(profile.real_lengths)):
        n = rng.choices(profile.lengths, weights=profile.length_w, k=1)[0]
        sec = profile.real_sections[li] if section_cond else None
        if sec is not None and sec in profile.section_tables:
            body_vocab, body_w = profile.section_tables[sec]
            g_vocab, g_w = profile.section_gallows.get(sec, profile.global_gallows)
        else:
            body_vocab, body_w = profile.global_vocab, profile.global_w
            g_vocab, g_w = profile.global_gallows
        # fall back to global pool if a section gallows pool is empty
        if not g_vocab:
            g_vocab, g_w = profile.global_gallows

        line: list[str] = []
        for pos in range(n):
            is_first = pos == 0
            is_last = pos == n - 1

            if line_edge_bias and is_last and not is_first:
                tok = _draw(rng, profile.final_vocab, profile.final_w)
            elif line_edge_bias and is_first:
                if g_vocab and rng.random() < p_initial_gallows:
                    tok = _draw(rng, g_vocab, g_w)
                else:
                    tok = _draw(rng, body_vocab, body_w)
            elif (
                self_citation
                and line
                and rng.random() < p_rep
            ):
                # copy from the last rep_window emitted tokens (>=1 available)
                w = min(rep_window, len(line))
                tok = line[rng.randint(len(line) - w, len(line) - 1)]
            else:
                tok = _draw(rng, body_vocab, body_w)

            if not tok:  # degenerate empty pool -> skip (keeps stream valid)
                tok = _draw(rng, profile.global_vocab, profile.global_w)
            line.append(tok)
        out.append(line)
    return out


# --------------------------------------------------------------------------- #
# p_rep calibration                                                           #
# --------------------------------------------------------------------------- #
def calibrate_p_rep(
    profile: GeneratorProfile,
    target_repeat: float,
    *,
    section_cond: bool,
    line_edge_bias: bool,
    rep_window: int,
    p_initial_gallows: float,
    seed: int,
    n_iter: int = 18,
) -> float:
    """Bisection search for p_rep so the synthetic adjacent-repeat ~= target.

    The adjacent-repeat rate is monotone increasing in p_rep (more copying ->
    more adjacent matches), so a bisection on [0,1] converges. Each evaluation
    builds a full synthetic corpus at a fixed seed (so the search is
    deterministic) and measures its adjacent-repeat rate. Returns the midpoint of
    the final bracket.
    """
    lo, hi = 0.0, 1.0

    def repeat_at(p: float) -> float:
        synth = generate(
            profile,
            section_cond=section_cond,
            self_citation=True,
            line_edge_bias=line_edge_bias,
            p_rep=p,
            rep_window=rep_window,
            p_initial_gallows=p_initial_gallows,
            seed=seed,
        )
        return adjacent_repeats(synth)["observed"]

    for _ in range(n_iter):
        mid = (lo + hi) / 2.0
        if repeat_at(mid) < target_repeat:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


# --------------------------------------------------------------------------- #
# Battery: measure every metric on a list of token-lines                      #
# --------------------------------------------------------------------------- #
def measure_battery(
    lines: list[list[str]], *, seed: int, max_d: int, n_null: int
) -> dict[str, float]:
    """Compute the full statistical battery on one corpus (real or synthetic).

    Reuses the exact R58/R59/R60 estimators so real and synthetic are measured by
    identical code. Returns a flat metric->value dict:
      h2, adjacent_repeat, laafu_I, line_initial_gallows,
      mi_d1/2/5/10/50/100, corr_length, zipf_slope, heaps_beta,
      gain_over_wordunigram (lzma), plus n_lines / n_tokens / stream_len.
    """
    stream = _char_stream(lines)
    ce = char_entropies(lines)
    rep = adjacent_repeats(lines)
    laafu_I = mutual_information(laafu_pairs(lines))
    li_gallows = real_line_initial_gallows_fraction(lines)

    mi = mi_curve(stream, max_d)
    null = null_mi_curve(stream, max_d, n_null, seed)
    excess = excess_curve(mi, null)
    null_floor = sum(null) / len(null) if null else 0.0
    corr_len = correlation_length(excess, null_floor)

    toks = token_stream(lines)
    z_slope, _z_r2, _z_n = zipf_slope(toks, ZIPF_RANK_LO, ZIPF_RANK_HI)
    h_beta, _h_r2, _h_n = heaps_beta(toks)

    # gain_over_wordunigram (lzma): real stream vs its own bag-of-words twin
    real_stream = stream_from_words(toks)
    n = len(real_stream)
    bag = gen_word_unigram(toks, n, seed + 3)
    bpc_real = bits_per_char(compress_size_bits(real_stream, "lzma"), n)
    bpc_bag = bits_per_char(compress_size_bits(bag, "lzma"), n)
    g_worduni = gain(bpc_bag, bpc_real)

    out = {
        "h2": ce["h2"],
        "adjacent_repeat": rep["observed"],
        "laafu_I": laafu_I,
        "line_initial_gallows": li_gallows,
        "corr_length": float(corr_len),
        "zipf_slope": z_slope,
        "heaps_beta": h_beta,
        "gain_over_wordunigram": g_worduni,
        "n_lines": float(len(lines)),
        "n_tokens": float(len(toks)),
        "stream_len": float(len(stream)),
    }
    for d in MI_CHECKPOINTS:
        out[f"mi_d{d}"] = mi[d - 1] if d - 1 < len(mi) else float("nan")
    return out


# Per-metric tolerances for the match table. Absolute |real-gen| deltas.
# Rationale: entropy/MI metrics in bits get small absolute tolerances; rates and
# fractions get tolerances comparable to their sampling noise at ~37k tokens;
# corr_length (an integer d) gets +/-5; the compressibility gain (a small ratio
# near 0) gets 0.03 (the R60 decision scale).
TOLERANCES: dict[str, float] = {
    "h2": 0.10,
    "adjacent_repeat": 0.0030,
    "laafu_I": 0.08,
    "line_initial_gallows": 0.05,
    "mi_d1": 0.15,
    "mi_d2": 0.12,
    "mi_d5": 0.05,
    "mi_d10": 0.02,
    "mi_d50": 0.005,
    "mi_d100": 0.005,
    "corr_length": 5.0,
    "zipf_slope": 0.15,
    "heaps_beta": 0.08,
    "gain_over_wordunigram": 0.03,
}

# The KEY metrics that decide the verdict (the headline statistical signatures).
KEY_METRICS = (
    "h2",
    "adjacent_repeat",
    "laafu_I",
    "corr_length",
    "zipf_slope",
    "heaps_beta",
    "gain_over_wordunigram",
)


def build_match_rows(
    real: dict[str, float], gen: dict[str, float]
) -> list[dict]:
    """One match-table row per tolerance-tracked metric (stable order)."""
    rows = []
    order = [
        "h2",
        "adjacent_repeat",
        "laafu_I",
        "line_initial_gallows",
        "mi_d1",
        "mi_d2",
        "mi_d5",
        "mi_d10",
        "mi_d50",
        "mi_d100",
        "corr_length",
        "zipf_slope",
        "heaps_beta",
        "gain_over_wordunigram",
    ]
    for metric in order:
        r = real[metric]
        g = gen[metric]
        tol = TOLERANCES[metric]
        delta = abs(r - g)
        rows.append(
            {
                "metric": metric,
                "real": round(r, 6),
                "generator": round(g, 6),
                "abs_delta": round(delta, 6),
                "tolerance": tol,
                "within_tol": delta <= tol,
                "key_metric": metric in KEY_METRICS,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def classify_verdict(match_rows: list[dict]) -> tuple[str, int, int, list[str]]:
    """Verdict from the KEY-metric match results.

    Counts how many KEY metrics fall within tolerance. All key metrics matched
    -> "generator_sufficient"; otherwise "generator_insufficient" and the names
    of the resisting key metrics are returned.
    """
    key_rows = [r for r in match_rows if r["key_metric"]]
    matched = [r for r in key_rows if r["within_tol"]]
    resisting = [r["metric"] for r in key_rows if not r["within_tol"]]
    verdict = (
        "generator_sufficient" if len(resisting) == 0 else "generator_insufficient"
    )
    return verdict, len(matched), len(key_rows), resisting


# --------------------------------------------------------------------------- #
# IO                                                                          #
# --------------------------------------------------------------------------- #
def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _r(x: float, nd: int = 6) -> str:
    if isinstance(x, float) and (math.isnan(x) or math.isinf(x)):
        return "nan" if math.isnan(x) else ("inf" if x > 0 else "-inf")
    return str(round(x, nd))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("corpus", nargs="?", default=str(DEFAULT_CORPUS))
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--max-d", type=int, default=MAX_D)
    p.add_argument("--n-null", type=int, default=N_NULL_SHUFFLES)
    p.add_argument("--rep-window", type=int, default=1)
    p.add_argument(
        "--p-initial-gallows",
        type=float,
        default=-1.0,
        help="line-initial gallows-draw probability; <0 auto-tunes to the real fraction",
    )
    p.add_argument(
        "--p-rep",
        type=float,
        default=-1.0,
        help="self-citation probability; <0 auto-calibrates to the real repeat rate",
    )
    d = ROOT / "data" / "derived"
    p.add_argument("--out-match", default=str(d / "generator_match_zl3b.csv"))
    p.add_argument("--out-ablation", default=str(d / "generator_ablation_zl3b.csv"))
    p.add_argument("--out-summary", default=str(d / "generator_summary_zl3b.csv"))
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    lines, sections = parse_loci_with_section(Path(args.corpus))
    profile = GeneratorProfile(lines, sections)

    # --- real battery ---
    real = measure_battery(lines, seed=args.seed, max_d=args.max_d, n_null=args.n_null)
    real_repeat = real["adjacent_repeat"]
    real_li_gallows = real["line_initial_gallows"]

    # --- tune line_edge_bias: the line-initial gallows draw probability is the
    #     real line-initial gallows FRACTION directly (each line-initial token is
    #     drawn from the gallows pool with that probability, reproducing it). ---
    if args.p_initial_gallows < 0:
        p_initial_gallows = real_li_gallows
    else:
        p_initial_gallows = args.p_initial_gallows

    # --- calibrate self_citation p_rep to the real adjacent-repeat rate, in the
    #     FULL configuration (section_cond + line_edge_bias on) so the tuned value
    #     is the one the headline generator uses. ---
    if args.p_rep < 0:
        p_rep = calibrate_p_rep(
            profile,
            real_repeat,
            section_cond=True,
            line_edge_bias=True,
            rep_window=args.rep_window,
            p_initial_gallows=p_initial_gallows,
            seed=args.seed + 100,
        )
    else:
        p_rep = args.p_rep

    # --- ABLATION ladder: measure the battery for each cumulative mechanism set ---
    ablation_rows: list[dict] = []
    full_gen_battery: dict[str, float] | None = None
    for label, toggles in ABLATION_LADDER:
        synth = generate(
            profile,
            section_cond=toggles["section_cond"],
            self_citation=toggles["self_citation"],
            line_edge_bias=toggles["line_edge_bias"],
            p_rep=p_rep,
            rep_window=args.rep_window,
            p_initial_gallows=p_initial_gallows,
            seed=args.seed + 100,
        )
        bat = measure_battery(
            synth, seed=args.seed, max_d=args.max_d, n_null=args.n_null
        )
        if label == "full":
            full_gen_battery = bat
        ablation_rows.append(
            {
                "mechanism_set": label,
                "h2": _r(bat["h2"], 4),
                "adjacent_repeat": _r(bat["adjacent_repeat"], 6),
                "laafu_I": _r(bat["laafu_I"], 6),
                "line_initial_gallows": _r(bat["line_initial_gallows"], 4),
                "corr_length": str(int(bat["corr_length"])),
                "zipf_slope": _r(bat["zipf_slope"], 4),
                "heaps_beta": _r(bat["heaps_beta"], 4),
                "gain_over_wordunigram": _r(bat["gain_over_wordunigram"], 6),
                "semantic_guardrail": GUARDRAIL,
            }
        )

    assert full_gen_battery is not None

    # --- MATCH TABLE: real vs full generator ---
    match_rows = build_match_rows(real, full_gen_battery)
    verdict, n_matched, n_key, resisting = classify_verdict(match_rows)

    write_csv(
        Path(args.out_match),
        match_rows,
        [
            "metric",
            "real",
            "generator",
            "abs_delta",
            "tolerance",
            "within_tol",
            "key_metric",
            "semantic_guardrail",
        ],
    )
    write_csv(
        Path(args.out_ablation),
        ablation_rows,
        [
            "mechanism_set",
            "h2",
            "adjacent_repeat",
            "laafu_I",
            "line_initial_gallows",
            "corr_length",
            "zipf_slope",
            "heaps_beta",
            "gain_over_wordunigram",
            "semantic_guardrail",
        ],
    )

    n_metrics_total = len(match_rows)
    n_metrics_within = sum(1 for r in match_rows if r["within_tol"])
    summary_rows = [
        {"metric": "mechanisms_in_full", "value": "+".join(MECHANISMS)},
        {"metric": "n_metrics", "value": str(n_metrics_total)},
        {"metric": "n_matched", "value": str(n_metrics_within)},
        {"metric": "n_key_metrics", "value": str(n_key)},
        {"metric": "n_key_matched", "value": str(n_matched)},
        {"metric": "key_metrics_resisting", "value": ",".join(resisting) if resisting else "none"},
        {"metric": "p_rep_used", "value": _r(p_rep, 6)},
        {"metric": "p_initial_gallows_used", "value": _r(p_initial_gallows, 6)},
        {"metric": "rep_window", "value": str(args.rep_window)},
        {"metric": "real_adjacent_repeat", "value": _r(real_repeat, 6)},
        {"metric": "gen_adjacent_repeat", "value": _r(full_gen_battery["adjacent_repeat"], 6)},
        {"metric": "verdict", "value": verdict},
        {
            "metric": "caveat",
            "value": (
                "generator_sufficient shows meaning is NOT REQUIRED to explain the "
                "statistics; it does NOT prove the text is meaningless (a meaningful "
                "text could carry the same stats)."
            ),
        },
        {"metric": "guardrail", "value": GUARDRAIL},
    ]
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    # --- console report ---
    print(
        f"n_lines real={int(real['n_lines'])} gen={int(full_gen_battery['n_lines'])} | "
        f"n_tokens real={int(real['n_tokens'])} gen={int(full_gen_battery['n_tokens'])}"
    )
    print(f"p_rep_used={p_rep:.6f} p_initial_gallows_used={p_initial_gallows:.6f}")
    print("MATCH TABLE (metric | real | generator | |d| | tol | within):")
    for r in match_rows:
        star = "*" if r["key_metric"] else " "
        print(
            f"  {star}{r['metric']:22s} real={r['real']:<12} gen={r['generator']:<12} "
            f"|d|={r['abs_delta']:<10} tol={r['tolerance']:<8} within={r['within_tol']}"
        )
    print("ABLATION (mechanism_set | h2 | adj_rep | laafu_I | corr_len | zipf | heaps | gain):")
    for r in ablation_rows:
        print(
            f"  {r['mechanism_set']:32s} h2={r['h2']} adj={r['adjacent_repeat']} "
            f"laafu={r['laafu_I']} cl={r['corr_length']} zipf={r['zipf_slope']} "
            f"heaps={r['heaps_beta']} gain={r['gain_over_wordunigram']}"
        )
    print(
        f"n_key_matched={n_matched}/{n_key}  n_metrics_matched={n_metrics_within}/{n_metrics_total}  "
        f"resisting={resisting if resisting else 'none'}"
    )
    print(f"VERDICT={verdict}")
    print(
        "caveat: 'generator_sufficient' shows meaning is NOT REQUIRED to explain "
        "the stats; it does NOT prove the text is meaningless."
    )
    print(f"match_csv={args.out_match}")
    print(f"ablation_csv={args.out_ablation}")
    print(f"summary_csv={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
