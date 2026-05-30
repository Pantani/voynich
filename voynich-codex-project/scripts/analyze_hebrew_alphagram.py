#!/usr/bin/env python3
"""Rota 71: the Hebrew hypothesis (Kondrak & Hauer 2018) -- alphagram + abjad attack.

The "Voynich is Hebrew" claim has two very different forms and the repo has only
attacked one of them so far:

  * POINT DECIPHERMENTS (Cheshire/Bax/Gibbs-style sentence translations) are
    R66 thesis #13, already REFUTED by char_h2=2.15 and the absence of a
    corpus-wide reproducing grammar. They cherry-pick a handful of tokens.

  * The ALGORITHMIC version -- Kondrak & Hauer (2018, "Decoding Anagrammed Texts
    ...", TACL) -- is different and was NEVER isolated here. They ran written
    language identification over ~380 languages; Hebrew scored first; and they
    proposed a SPECIFIC generative model for the cipher:
        each Voynich word = a Hebrew word that was
          (a) ABJAD-stripped of its vowels, and
          (b) had its remaining letters RE-SORTED into alphabetical order
              (an "alphagram" / alphabetic anagram).
    Their decode of the first line ("she made recommendations to the priest...")
    rests on UN-alphagramming + supplying vowels + Google-translate.

This route isolates and attacks the FALSIFIABLE pillar of the algorithmic claim:
the ALPHAGRAM hypothesis. If every word is an alphabetic anagram, then there
exists ONE total order of the glyphs under which (almost) EVERY token is a
non-decreasing sequence -- equivalently, the majority pairwise glyph order is a
strict TOTAL order (transitive, acyclic) and almost every token obeys it.

Decisive confound (the R62 lens, reused): the Voynich already has rigid templatic
morphology (qo-/ok-/ot- onsets, -dy/-y/-aiin codas; the Stolfi word grammar).
That positional rigidity ALONE pushes order-consistency well above chance WITHOUT
any Hebrew alphagram. So every directional/order signal is arbitrated against the
content-free R62 generator, which redraws WHOLE real words in i.i.d. order: its
WITHIN-WORD morphology is identical to the corpus. Therefore any within-word
order signal the generator reproduces is MORPHOLOGY (templatic form), not evidence
of an alphabetic re-sorting of an underlying language -> degenerate, not Hebrew.

Measures:
  A. ALPHAGRAM / total-order test (the pillar).
     - alphagram_fraction: share of tokens (len>=2) that are non-decreasing under
       the inferred best total order, on REAL vs floor (within-word shuffle) vs
       ceiling (the same tokens actually sorted == a true alphagram) vs the R62
       generator. A true alphabetic text sits at the ceiling (~1.0).
     - pair_decidedness: share of co-occurring glyph pairs whose order is STRICT
       (one direction >= 95%). A total order needs ~all pairs decided; natural
       text and templatic morphology leave many pairs ambiguous. ORDER-FREE
       (independent of which total order we pick) -> the robust discriminator.
     - majority_cycles: 3-cycles (a<b<c<a) in the majority-order tournament. A
       total order is acyclic -> 0 cycles. Any cycle PROVES no alphagram order
       exists (a hard impossibility result, not a threshold).
  B. GLYPH-UNIT robustness. EVA writes some single glyphs as digraphs (ch, sh,
     cth, ckh, cph, cfh). The whole test is repeated treating those as single
     units, so the verdict cannot be an artifact of ASCII character splitting.
  C. ABJAD test. K-H also require vowel suppression. Candidate EVA "vowels"
     (a, o, e, y) are stripped and the alphagram/decidedness recomputed: does
     removing vowels rescue a total order? (Pre-registered: it should not.)
     Also mean word length vs the abjad anchor (Hebrew consonant skeletons ~3-4).
  D. LETTER-FREQUENCY (weak, non-discriminating by design). Rank-frequency profile
     of Voynich glyphs vs Hebrew AND English anchors (literature, NEVER recomputed).
     Zipf makes any two languages' sorted profiles correlate ~1.0, so a Hebrew
     match is non-informative; we report both correlations to show they tie.

Right-to-left reading (Hebrew is R->L) is the scope of Rota 69 (directionality /
mirror), kept separate; this route is the alphagram + abjad pillar.

NOT a decipherment. Guardrail in every output CSV.
"""
from __future__ import annotations

import argparse
import collections
import csv
import itertools
import random
from pathlib import Path

from scripts.analyze_generator import (
    GeneratorProfile,
    generate,
    parse_loci_with_section,
)

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota71_hebrew_alphagram_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"

# --- thresholds (pre-registered) ------------------------------------------- #
# To be "alphagram-compatible" a corpus must look like a TRUE alphagram: nearly
# every token ordered AND nearly every glyph pair strictly ordered.
ALPHAGRAM_PASS = 0.90       # alphagram_fraction AND pair_decidedness must exceed this
GEN_DELTA_TOL = 0.03        # |real - generator| below this -> reproduced (morphology)
MIN_PAIR = 5                # ignore glyph pairs seen fewer than this many times
STRICT_MAJORITY = 0.95      # a pair is "decided" if one direction >= this share
N_SHUFFLE = 5               # within-word shuffle repeats for the floor
SEED = 70

# EVA multi-character glyphs treated as single units in the glyph-unit pass.
# (ch/sh plus the four benched gallows; longest-match first.)
EVA_GLYPHS = ("cth", "ckh", "cph", "cfh", "ch", "sh")

# Candidate EVA vowels for the abjad pass (a/o are the matrix axis; e/y frequent).
ABJAD_VOWELS = frozenset("aoey")

# Literature anchors: sorted (descending) relative letter frequencies, % -- NOT
# recomputed here. Hebrew letters (no niqqud); English letters. Used only to show
# that a sorted-profile match is non-discriminating (both tie via Zipf).
HEBREW_FREQ_DESC = [10.8, 10.6, 8.4, 7.3, 6.4, 6.0, 5.9, 5.5, 5.0, 4.9,
                    4.4, 4.0, 3.6, 3.3, 3.1, 2.9, 2.5, 2.2, 1.9, 1.6, 1.2, 0.9]
ENGLISH_FREQ_DESC = [12.7, 9.1, 8.2, 7.5, 7.0, 6.7, 6.3, 6.1, 6.0, 4.3,
                     4.0, 2.8, 2.8, 2.4, 2.4, 2.0, 1.9, 1.5, 1.0, 0.8, 0.8, 0.2]


# --------------------------------------------------------------------------- #
# Tokenisation into units                                                     #
# --------------------------------------------------------------------------- #
def char_units(token: str) -> list[str]:
    """One ASCII character per unit (the K-H working representation)."""
    return list(token)


def glyph_units(token: str) -> list[str]:
    """Greedy longest-match split treating EVA digraphs as single glyphs."""
    out: list[str] = []
    i = 0
    n = len(token)
    while i < n:
        for g in EVA_GLYPHS:
            if token.startswith(g, i):
                out.append(g)
                i += len(g)
                break
        else:
            out.append(token[i])
            i += 1
    return out


# --------------------------------------------------------------------------- #
# Order inference and the alphagram / total-order measures                    #
# --------------------------------------------------------------------------- #
def infer_order(tokens: list[str], unit_fn) -> list[str]:
    """Infer a best total glyph order by mean relative position within words.

    This is the order most charitable to the alphagram claim (it maximises
    forward agreement); the decidedness/cycle tests below are order-FREE and do
    not depend on it.
    """
    pos_sum: collections.Counter = collections.Counter()
    pos_n: collections.Counter = collections.Counter()
    for t in tokens:
        u = unit_fn(t)
        if len(u) < 2:
            continue
        last = len(u) - 1
        for i, c in enumerate(u):
            pos_sum[c] += i / last
            pos_n[c] += 1
    score = {c: pos_sum[c] / pos_n[c] for c in pos_n}
    return sorted(score, key=lambda c: (score[c], c))


def alphagram_fraction(tokens: list[str], order: list[str], unit_fn) -> float:
    """Share of multi-unit tokens that are non-decreasing under `order`."""
    rank = {c: i for i, c in enumerate(order)}
    ok = tot = 0
    for t in tokens:
        u = unit_fn(t)
        if len(u) < 2:
            continue
        tot += 1
        rs = [rank.get(c, -1) for c in u]
        if all(rs[i] <= rs[i + 1] for i in range(len(rs) - 1)):
            ok += 1
    return ok / tot if tot else 0.0


def pair_order_counts(tokens: list[str], unit_fn) -> collections.Counter:
    """Counter[(a, b)] = times glyph a appears before glyph b within a word."""
    cnt: collections.Counter = collections.Counter()
    for t in tokens:
        u = unit_fn(t)
        for i, a in enumerate(u):
            for b in u[i + 1:]:
                if a != b:
                    cnt[(a, b)] += 1
    return cnt


def _unordered_pairs(pc: collections.Counter) -> dict:
    """Collapse directed counts into {frozenset-key: (fwd, rev)} on a fixed order."""
    pairs: dict = {}
    for (a, b), n in pc.items():
        key = (a, b) if a < b else (b, a)
        slot = pairs.setdefault(key, [0, 0])
        slot[0 if (a, b) == key else 1] += n
    return pairs


def pair_decidedness(pc: collections.Counter, min_pair: int, strict: float) -> dict:
    """Fraction of co-occurring glyph pairs with a strict-majority order.

    A true alphagram is a total order -> every pair is decided (== 1.0).
    Returns decided_frac, weighted_majority (mean majority share weighted by
    pair frequency), and n_pairs (pairs with >= min_pair observations).
    """
    pairs = _unordered_pairs(pc)
    decided = total = 0
    wmaj = 0.0
    wtot = 0
    for f, r in pairs.values():
        s = f + r
        if s < min_pair:
            continue
        total += 1
        maj = max(f, r) / s
        if maj >= strict:
            decided += 1
        wmaj += maj * s
        wtot += s
    return {
        "decided_frac": decided / total if total else 0.0,
        "weighted_majority": wmaj / wtot if wtot else 0.0,
        "n_pairs": total,
    }


def majority_cycles(pc: collections.Counter, min_pair: int) -> int:
    """Count 3-cycles (a>b, b>c, c>a) in the majority-order tournament.

    A total order (alphagram) is acyclic -> 0. Any cycle proves NO single glyph
    order can sort every word, i.e. the text cannot be an alphabetic anagram.
    """
    pairs = _unordered_pairs(pc)
    # winner[x][y] = True if x tends to precede y by majority (decided pairs only)
    nodes = set()
    succ: dict = collections.defaultdict(set)
    for (a, b), (f, r) in pairs.items():
        if f + r < min_pair or f == r:
            continue
        nodes.update((a, b))
        if f > r:
            succ[a].add(b)
        else:
            succ[b].add(a)
    cycles = 0
    for x, y, z in itertools.combinations(sorted(nodes), 3):
        # count any directed 3-cycle among the triangle's three edges
        edges = succ
        if (y in edges[x] and z in edges[y] and x in edges[z]) or \
           (z in edges[x] and y in edges[z] and x in edges[y]):
            cycles += 1
    return cycles


# --------------------------------------------------------------------------- #
# Corpus transforms                                                           #
# --------------------------------------------------------------------------- #
def within_word_shuffle(tokens: list[str], rng: random.Random, unit_fn) -> list[str]:
    """Shuffle units inside each word (destroys order -> alphagram floor)."""
    out = []
    for t in tokens:
        u = unit_fn(t)
        rng.shuffle(u)
        out.append("".join(u))
    return out


def sort_words(tokens: list[str], order: list[str], unit_fn) -> list[str]:
    """Sort each word's units under `order` (== a true alphagram -> ceiling)."""
    rank = {c: i for i, c in enumerate(order)}
    return ["".join(sorted(unit_fn(t), key=lambda c: rank.get(c, -1))) for t in tokens]


def strip_vowels(tokens: list[str], vowels: frozenset, unit_fn) -> list[str]:
    """Drop candidate vowels (abjad), keeping only consonant skeletons."""
    out = []
    for t in tokens:
        cons = [c for c in unit_fn(t) if c not in vowels]
        if cons:
            out.append("".join(cons))
    return out


def mean_units(tokens: list[str], unit_fn) -> float:
    lens = [len(unit_fn(t)) for t in tokens]
    return sum(lens) / len(lens) if lens else 0.0


# --------------------------------------------------------------------------- #
# Letter-frequency profile (weak / non-discriminating)                        #
# --------------------------------------------------------------------------- #
def freq_profile_desc(tokens: list[str], unit_fn, k: int) -> list[float]:
    c: collections.Counter = collections.Counter()
    for t in tokens:
        c.update(unit_fn(t))
    tot = sum(c.values()) or 1
    vals = sorted((v / tot * 100 for v in c.values()), reverse=True)
    return vals[:k]


def spearman(a: list[float], b: list[float]) -> float:
    """Spearman rank correlation of two equal-length sequences (plug-in)."""
    n = min(len(a), len(b))
    if n < 2:
        return float("nan")
    a, b = a[:n], b[:n]

    def ranks(xs):
        order = sorted(range(len(xs)), key=lambda i: xs[i])
        rk = [0.0] * len(xs)
        for pos, i in enumerate(order):
            rk[i] = pos
        return rk

    ra, rb = ranks(a), ranks(b)
    ma, mb = sum(ra) / n, sum(rb) / n
    num = sum((ra[i] - ma) * (rb[i] - mb) for i in range(n))
    da = sum((ra[i] - ma) ** 2 for i in range(n)) ** 0.5
    db = sum((rb[i] - mb) ** 2 for i in range(n)) ** 0.5
    return num / (da * db) if da and db else float("nan")


# --------------------------------------------------------------------------- #
# Per-corpus alphagram battery                                                #
# --------------------------------------------------------------------------- #
def alphagram_battery(tokens: list[str], order: list[str], unit_fn) -> dict:
    pc = pair_order_counts(tokens, unit_fn)
    dec = pair_decidedness(pc, MIN_PAIR, STRICT_MAJORITY)
    return {
        "alphagram_fraction": alphagram_fraction(tokens, order, unit_fn),
        "decided_frac": dec["decided_frac"],
        "weighted_majority": dec["weighted_majority"],
        "n_pairs": dec["n_pairs"],
        "majority_cycles": majority_cycles(pc, MIN_PAIR),
        "mean_units": mean_units(tokens, unit_fn),
    }


# --------------------------------------------------------------------------- #
# Generator corpora (the arbiter)                                             #
# --------------------------------------------------------------------------- #
def generator_tokens(lines, sections, seed: int) -> dict[str, list[str]]:
    """Flat token lists from the content-free R62 generator (base + full)."""
    profile = GeneratorProfile(lines, sections)
    base = generate(profile, section_cond=False, self_citation=False,
                    line_edge_bias=False, p_rep=0.0, rep_window=1,
                    p_initial_gallows=0.0, seed=seed)
    full = generate(profile, section_cond=True, self_citation=True,
                    line_edge_bias=True, p_rep=0.0046, rep_window=1,
                    p_initial_gallows=0.185, seed=seed)
    flat = lambda L: [t for ln in L for t in ln if t]
    return {"generator_base": flat(base), "generator_full": flat(full)}


# --------------------------------------------------------------------------- #
# Verdict                                                                      #
# --------------------------------------------------------------------------- #
def classify_verdict(real: dict, floor: dict, ceiling: dict, gen: dict,
                     abjad: dict, freq_tie: bool) -> tuple[str, list[str]]:
    """Adjudicate the alphagram hypothesis. Returns (verdict, reasons)."""
    reasons: list[str] = []
    af, dec, cyc = real["alphagram_fraction"], real["decided_frac"], real["majority_cycles"]

    alphagram_compatible = af >= ALPHAGRAM_PASS and dec >= ALPHAGRAM_PASS and cyc == 0
    if cyc > 0:
        reasons.append(f"no_total_order_exists: {cyc} majority 3-cycles (alphagram needs 0)")
    if dec < ALPHAGRAM_PASS:
        reasons.append(f"pairs_not_strictly_ordered: decided={dec:.3f} << {ALPHAGRAM_PASS}")
    if af < ALPHAGRAM_PASS:
        reasons.append(f"tokens_not_sorted: alphagram_fraction={af:.3f} << ceiling {ceiling['alphagram_fraction']:.2f}")

    # position of REAL between shuffle-floor and true-alphagram-ceiling
    lo, hi = floor["alphagram_fraction"], ceiling["alphagram_fraction"]
    frac_to_ceiling = (af - lo) / (hi - lo) if hi > lo else float("nan")

    # is the (modest) order lift just morphology the generator reproduces?
    gdelta = abs(af - gen["alphagram_fraction"])
    reproduced = gdelta <= GEN_DELTA_TOL
    if reproduced:
        reasons.append(
            f"order_lift_reproduced_by_generator: real={af:.3f} ~ gen={gen['alphagram_fraction']:.3f} "
            f"(delta={gdelta:.3f} <= {GEN_DELTA_TOL}) -> templatic morphology, not alphabetic")

    # did stripping vowels rescue a total order?
    if abjad["decided_frac"] < ALPHAGRAM_PASS:
        reasons.append(
            f"abjad_does_not_rescue: vowel-stripped decided={abjad['decided_frac']:.3f}, "
            f"cycles={abjad['majority_cycles']}")
    if freq_tie:
        reasons.append("letter_frequency_non_discriminating: Hebrew ties English (Zipf)")

    if alphagram_compatible and not reproduced:
        verdict = "alphagram_compatible"  # would support K-H
    else:
        verdict = "hebrew_alphagram_refuted"
    return verdict, reasons + [f"frac_to_ceiling={frac_to_ceiling:.3f}"]


# --------------------------------------------------------------------------- #
# IO helpers                                                                   #
# --------------------------------------------------------------------------- #
def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _r(x: float, nd: int = 6) -> str:
    return f"{x:.{nd}f}" if isinstance(x, float) else str(x)


# --------------------------------------------------------------------------- #
# Main                                                                         #
# --------------------------------------------------------------------------- #
def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Rota 70: Hebrew alphagram + abjad attack")
    p.add_argument("--corpus", type=Path, default=DEFAULT_CORPUS)
    p.add_argument("--seed", type=int, default=SEED)
    p.add_argument("--out-summary", type=Path,
                   default=ROOT / "data" / "derived" / "hebrew_alphagram_summary_zl3b.csv")
    p.add_argument("--out-corpora", type=Path,
                   default=ROOT / "data" / "derived" / "hebrew_alphagram_corpora_zl3b.csv")
    p.add_argument("--out-pairs", type=Path,
                   default=ROOT / "data" / "derived" / "hebrew_alphagram_pairs_zl3b.csv")
    return p.parse_args(argv)


def run(corpus: Path, seed: int) -> dict:
    """Full analysis; returns everything needed for CSVs and tests (no IO)."""
    lines, sections = parse_loci_with_section(corpus)
    tokens = [t for ln in lines for t in ln if t]
    rng = random.Random(seed)

    order = infer_order(tokens, char_units)
    real = alphagram_battery(tokens, order, char_units)

    # floor: average over N within-word shuffles
    floors = [alphagram_battery(within_word_shuffle(tokens, rng, char_units), order, char_units)
              for _ in range(N_SHUFFLE)]
    floor = {k: (sum(f[k] for f in floors) / len(floors) if isinstance(floors[0][k], float)
                 else floors[0][k]) for k in floors[0]}

    # ceiling: the same tokens actually sorted == a true alphagram
    ceiling = alphagram_battery(sort_words(tokens, order, char_units), order, char_units)

    # generator arbiter
    gens = generator_tokens(lines, sections, seed)
    gen_order = infer_order(gens["generator_base"], char_units)
    gen_base = alphagram_battery(gens["generator_base"], gen_order, char_units)
    gen_full = alphagram_battery(gens["generator_full"], gen_order, char_units)

    # glyph-unit robustness pass
    g_order = infer_order(tokens, glyph_units)
    glyph_real = alphagram_battery(tokens, g_order, glyph_units)

    # abjad pass (strip candidate vowels, char units)
    abjad_tokens = strip_vowels(tokens, ABJAD_VOWELS, char_units)
    abjad_order = infer_order(abjad_tokens, char_units)
    abjad = alphagram_battery(abjad_tokens, abjad_order, char_units)

    # letter-frequency tie test (non-discriminating by design)
    k = min(len(HEBREW_FREQ_DESC), len(ENGLISH_FREQ_DESC))
    prof = freq_profile_desc(tokens, char_units, k)
    sp_he = spearman(prof, HEBREW_FREQ_DESC)
    sp_en = spearman(prof, ENGLISH_FREQ_DESC)
    freq_tie = abs(sp_he - sp_en) < 0.05  # Hebrew not distinguishable from English

    verdict, reasons = classify_verdict(real, floor, ceiling, gen_base, abjad, freq_tie)

    return {
        "n_tokens": len(tokens), "n_lines": len(lines),
        "order": "".join(order), "gen_order": "".join(gen_order),
        "real": real, "floor": floor, "ceiling": ceiling,
        "generator_base": gen_base, "generator_full": gen_full,
        "glyph_real": glyph_real, "abjad": abjad,
        "freq_spearman_hebrew": sp_he, "freq_spearman_english": sp_en,
        "freq_tie": freq_tie,
        "verdict": verdict, "reasons": reasons,
        "pairs": _unordered_pairs(pair_order_counts(tokens, char_units)),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    res = run(args.corpus, args.seed)

    # --- corpora CSV (per-corpus battery) ---
    corpora_rows = []
    label_map = [
        ("real", res["real"]), ("floor_shuffle", res["floor"]),
        ("ceiling_sorted", res["ceiling"]), ("generator_base", res["generator_base"]),
        ("generator_full", res["generator_full"]), ("glyph_unit_real", res["glyph_real"]),
        ("abjad_vowel_stripped", res["abjad"]),
    ]
    for name, b in label_map:
        corpora_rows.append({
            "corpus": name,
            "alphagram_fraction": _r(b["alphagram_fraction"]),
            "pair_decided_frac": _r(b["decided_frac"]),
            "weighted_majority": _r(b["weighted_majority"]),
            "majority_cycles": b["majority_cycles"],
            "n_pairs": b["n_pairs"],
            "mean_units": _r(b["mean_units"], 4),
            "guardrail": GUARDRAIL,
        })
    write_csv(args.out_corpora, corpora_rows,
              ["corpus", "alphagram_fraction", "pair_decided_frac", "weighted_majority",
               "majority_cycles", "n_pairs", "mean_units", "guardrail"])

    # --- pairs CSV (evidence of non-total-order: ambiguous pairs) ---
    pair_rows = []
    for (a, b), (f, r) in sorted(res["pairs"].items(), key=lambda kv: -(kv[1][0] + kv[1][1])):
        s = f + r
        if s < MIN_PAIR:
            continue
        maj = max(f, r) / s
        pair_rows.append({
            "glyph_a": a, "glyph_b": b, "a_before_b": f, "b_before_a": r,
            "total": s, "majority": _r(maj, 4),
            "decided": "yes" if maj >= STRICT_MAJORITY else "no",
            "guardrail": GUARDRAIL,
        })
    write_csv(args.out_pairs, pair_rows,
              ["glyph_a", "glyph_b", "a_before_b", "b_before_a", "total",
               "majority", "decided", "guardrail"])

    # --- summary CSV ---
    real, floor, ceil = res["real"], res["floor"], res["ceiling"]
    gen = res["generator_base"]
    lo, hi = floor["alphagram_fraction"], ceil["alphagram_fraction"]
    frac_to_ceiling = (real["alphagram_fraction"] - lo) / (hi - lo) if hi > lo else float("nan")
    summary_rows = [
        {"metric": "n_tokens", "value": str(res["n_tokens"])},
        {"metric": "n_lines", "value": str(res["n_lines"])},
        {"metric": "inferred_order", "value": res["order"]},
        {"metric": "alphagram_fraction_real", "value": _r(real["alphagram_fraction"])},
        {"metric": "alphagram_fraction_floor", "value": _r(floor["alphagram_fraction"])},
        {"metric": "alphagram_fraction_ceiling", "value": _r(ceil["alphagram_fraction"])},
        {"metric": "alphagram_fraction_generator", "value": _r(gen["alphagram_fraction"])},
        {"metric": "frac_to_ceiling", "value": _r(frac_to_ceiling)},
        {"metric": "pair_decided_frac_real", "value": _r(real["decided_frac"])},
        {"metric": "pair_decided_frac_generator", "value": _r(gen["decided_frac"])},
        {"metric": "weighted_majority_real", "value": _r(real["weighted_majority"])},
        {"metric": "majority_cycles_real", "value": str(real["majority_cycles"])},
        {"metric": "n_pairs_real", "value": str(real["n_pairs"])},
        {"metric": "alphagram_fraction_glyph_unit", "value": _r(res["glyph_real"]["alphagram_fraction"])},
        {"metric": "pair_decided_frac_glyph_unit", "value": _r(res["glyph_real"]["decided_frac"])},
        {"metric": "majority_cycles_glyph_unit", "value": str(res["glyph_real"]["majority_cycles"])},
        {"metric": "abjad_decided_frac", "value": _r(res["abjad"]["decided_frac"])},
        {"metric": "abjad_majority_cycles", "value": str(res["abjad"]["majority_cycles"])},
        {"metric": "abjad_mean_units", "value": _r(res["abjad"]["mean_units"], 4)},
        {"metric": "real_mean_units", "value": _r(real["mean_units"], 4)},
        {"metric": "freq_spearman_hebrew", "value": _r(res["freq_spearman_hebrew"], 4)},
        {"metric": "freq_spearman_english", "value": _r(res["freq_spearman_english"], 4)},
        {"metric": "freq_non_discriminating", "value": str(res["freq_tie"])},
        {"metric": "alphagram_pass_threshold", "value": str(ALPHAGRAM_PASS)},
        {"metric": "verdict", "value": res["verdict"]},
        {"metric": "reasons", "value": " | ".join(res["reasons"])},
        {"metric": "guardrail", "value": GUARDRAIL},
    ]
    write_csv(args.out_summary, summary_rows, ["metric", "value"])

    # --- console ---
    print(f"corpus={args.corpus.name}  n_tokens={res['n_tokens']}")
    print(f"inferred order (mean-position): {res['order']}")
    print("  corpus                alphagram_frac  pair_decided  wt_maj   cycles  mean_units")
    for name, b in label_map:
        print(f"  {name:<20} {b['alphagram_fraction']:>10.4f}   {b['decided_frac']:>10.4f}  "
              f"{b['weighted_majority']:>6.3f}  {b['majority_cycles']:>5d}  {b['mean_units']:>8.3f}")
    print(f"REAL sits {frac_to_ceiling:.1%} of the way from shuffle-floor to alphagram-ceiling")
    print(f"abjad (vowels stripped): decided={res['abjad']['decided_frac']:.4f} "
          f"cycles={res['abjad']['majority_cycles']}")
    print(f"freq spearman: hebrew={res['freq_spearman_hebrew']:.4f} "
          f"english={res['freq_spearman_english']:.4f} tie={res['freq_tie']}")
    print(f"VERDICT={res['verdict']}")
    for r in res["reasons"]:
        print(f"  - {r}")
    print(f"summary_csv={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
