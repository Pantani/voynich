#!/usr/bin/env python3
"""Rota 69: Leonardo-style directionality, reversal & mirror-page attack.

The user asked to test hypotheses popular on the internet that frame the Voynich
as a Leonardo-da-Vinci-style production: mirror writing, reversed words ("palavras
de tras pra frente"), right-to-left reading, and mirrored facing pages. The
authorship claim itself is refuted by materiality (the vellum is C14-dated
1404-1438; Leonardo was born 1452), but the TECHNIQUES are testable regardless of
who held the pen. A 2025 arXiv paper ("Directionality of the Voynich Script",
2509.10573) makes the quantitative version of the claim: that conditional-entropy
and word-boundary signatures favour RIGHT-TO-LEFT reading.

A LOAD-BEARING THEOREM (flagged blind by the cryptanalyst, then confirmed here):
for any STATIONARY token process, single-step conditional entropy is REVERSAL-
INVARIANT --
    H(c_i | c_{i-1}) - H(c_{i-1} | c_i) = H(c_i) - H(c_{i-1}) -> 0,
because the joint bigram entropy is symmetric under swapping the pair and the two
marginals differ only by the stream's first/last character. The same holds at
every order. CONSEQUENCE: the famous h2 (and h3, ...) CANNOT distinguish L->R from
R->L reading -- reading direction is statistically invisible at the bulk sequence
level. We DEMONSTRATE this empirically (h2_fwd ~= h2_bwd) rather than asserting it.

So where can a real directional signal live? Only in things that BREAK stationarity:
  (a) WORD-INTERNAL morphology asymmetry: which side carries the rigid, low-entropy
      closing morphemes. This collapses to ONE number -- H(first glyph) vs
      H(last glyph). In Voynich, endings (-y, -aiin, -dy) are far more constrained
      than beginnings, so H(last) < H(first). This is pure templated morphology and
      is reproduced EXACTLY by the content-free R62 generator (it reuses whole real
      words), and it simply FLIPS SIGN when every token is reversed. => artifact.
  (b) NON-STATIONARY LAYOUT (line position / LAAFU): the one residual the generator
      did not fully reproduce -- but R66/R67 already showed that residual is LAYOUT,
      not content. Reversal/mirror operations do not touch it.

This route therefore tests every Leonardo operation and arbitrates it against the
content-free generator (which draws WHOLE real words in i.i.d. order: identical
within-word morphology, destroyed word order). A signal counts as NEW only if it
beats the generator -- the same bar the LAAFU residual once met.

Measures:
  A. BULK directional entropy (demonstration): h2_fwd, h2_bwd, h3_fwd, h3_bwd on
     real / generator / word-shuffle / token-reversed corpora. Expectation: fwd ~=
     bwd everywhere (reversal-invariance).
  B. WORD-EDGE morphology (the only real bigram-directional content): H(first glyph),
     H(last glyph), dir = H_first - H_last; plus H(2nd|1st) at word start vs
     H(2nd-last|last) at word end. Compared real vs generator vs token-reversed.
  C. REVERSAL lift: does any reversal move bulk h2 into the natural-language band
     [2.5, 3.6]? (anchors from literature, never recomputed).
  D. MIRROR-PAGE test: facing-folio token sequence vs the REVERSE of its neighbour,
     and per-page palindrome score, each against a permutation null.

NL anchors (literature, NOT recomputed): English char h2 ~ 3.1-3.6 and is nearly
direction-symmetric; published Voynich h2 ~ 2.0-2.3.

NOT a decipherment. Guardrail in every output CSV.
"""
from __future__ import annotations

import argparse
import collections
import csv
import math
import random
import re
from pathlib import Path

from scripts.analyze_language_signature import SPACE, shannon_entropy
from scripts.analyze_generator import (
    GeneratorProfile,
    generate,
    parse_loci_with_section,
)
from scripts.analyze_nucleus import clean_token

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota69_directionality_mirror_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"

# Natural-language anchors from the literature (NEVER recomputed here).
NL_H2_LOW, NL_H2_HIGH = 2.5, 3.6  # English/Latin character h2 band
# A directional signal counts as "beyond morphology" only if the real WORD-EDGE
# asymmetry differs from the content-free generator's by more than this (bits).
DIR_DELTA_THRESHOLD = 0.05
BULK_SYMMETRY_TOL = 0.02  # |h2_fwd - h2_bwd| below this confirms reversal-invariance

# Folio + locus line: capture the folio id and the token body.
_FOLIO_LOC = re.compile(r"^<(f\d+[rv]\d?)\.\d+[^>]*>\s*(.*)$")


# --------------------------------------------------------------------------- #
# Character streams and block conditional entropy                             #
# --------------------------------------------------------------------------- #
def char_stream(lines: list[list[str]]) -> list[str]:
    """Flatten lines into one character list, tokens separated by SPACE."""
    return list(SPACE.join(t for line in lines for t in line))


def block_cond_entropy(stream: list[str], order: int) -> float:
    """H(c_i | the `order` preceding chars), in bits, plug-in estimate.

    order=1 -> h2 = H(c_i|c_{i-1}); order=2 -> h3 = H(c_i|c_{i-2},c_{i-1}).
    Computed as H(context, next) - H(context) over the shared population.
    """
    if len(stream) <= order:
        return 0.0
    ctx: collections.Counter = collections.Counter()
    ctx_next: collections.Counter = collections.Counter()
    for i in range(order, len(stream)):
        c = tuple(stream[i - order : i])
        ctx[c] += 1
        ctx_next[(c, stream[i])] += 1
    return shannon_entropy(ctx_next) - shannon_entropy(ctx)


def cond_entropy_pairs(pairs: list[tuple[str, str]]) -> float:
    """H(Y | X) in bits from a list of (X, Y) observations (plug-in)."""
    if not pairs:
        return 0.0
    joint = collections.Counter(pairs)
    xs = collections.Counter(x for x, _ in pairs)
    return shannon_entropy(joint) - shannon_entropy(xs)


def directional_entropies(lines: list[list[str]]) -> dict:
    """Bulk fwd/bwd h2 & h3 plus word-edge morphology for one corpus.

    Bulk fwd/bwd are expected ~equal (stationary reversal-invariance). The real
    directional content is the WORD-EDGE block: dir = H(first glyph) - H(last
    glyph) (>0 means endings more constrained than beginnings, i.e. right-anchored),
    and the start/end inward conditional entropies.
    """
    stream = char_stream(lines)
    rev = stream[::-1]
    toks = [t for line in lines for t in line if t]
    first = collections.Counter(t[0] for t in toks)
    last = collections.Counter(t[-1] for t in toks)
    start_pairs = [(t[0], t[1]) for t in toks if len(t) >= 2]  # predict 2nd from 1st
    end_pairs = [(t[-1], t[-2]) for t in toks if len(t) >= 2]  # predict 2nd-last from last
    h_first = shannon_entropy(first)
    h_last = shannon_entropy(last)
    return {
        "n_chars": len(stream),
        "n_tokens": len(toks),
        "h1": shannon_entropy(collections.Counter(stream)),
        "h2_fwd": block_cond_entropy(stream, 1),
        "h2_bwd": block_cond_entropy(rev, 1),
        "h3_fwd": block_cond_entropy(stream, 2),
        "h3_bwd": block_cond_entropy(rev, 2),
        "h_first": h_first,
        "h_last": h_last,
        "dir_edge": h_first - h_last,  # >0: right-anchored (endings more predictable)
        "h_start_inward": cond_entropy_pairs(start_pairs),
        "h_end_inward": cond_entropy_pairs(end_pairs),
    }


# --------------------------------------------------------------------------- #
# Corpus transforms (the Leonardo operations + controls)                      #
# --------------------------------------------------------------------------- #
def reverse_each_token(lines: list[list[str]]) -> list[list[str]]:
    """Mirror every token's characters in place ('palavras de tras pra frente')."""
    return [[t[::-1] for t in line] for line in lines]


def global_word_shuffle(lines: list[list[str]], seed: int) -> list[list[str]]:
    """Keep every whole word intact, destroy word ORDER, rebuild same line lengths.

    A transparent morphology-only control: any asymmetry that survives here lives
    INSIDE the word, not in syntax. (Agrees with the generator base.)
    """
    rng = random.Random(seed)
    words = [t for line in lines for t in line]
    rng.shuffle(words)
    out: list[list[str]] = []
    idx = 0
    for line in lines:
        out.append(words[idx : idx + len(line)])
        idx += len(line)
    return out


def build_generator_corpora(
    lines: list[list[str]], sections: list[str], seed: int
) -> dict[str, list[list[str]]]:
    """Synthetic corpora from the content-free R62 generator (the arbiter).

    base: pure bag-of-real-words in random order (every mechanism off).
    full: the R62 model (section vocab + self-citation + line-edge bias).
    Both reuse WHOLE real words, so within-word morphology is identical to real.
    """
    profile = GeneratorProfile(lines, sections)
    base = generate(
        profile, section_cond=False, self_citation=False, line_edge_bias=False,
        p_rep=0.0, rep_window=1, p_initial_gallows=0.0, seed=seed,
    )
    full = generate(
        profile, section_cond=True, self_citation=True, line_edge_bias=True,
        p_rep=0.0046, rep_window=1, p_initial_gallows=0.185, seed=seed,
    )
    return {"generator_base": base, "generator_full": full}


# --------------------------------------------------------------------------- #
# Mirror-page test                                                            #
# --------------------------------------------------------------------------- #
def parse_folio_sequences(path: Path) -> "collections.OrderedDict[str, list[str]]":
    """folio id -> ordered list of clean tokens (all its loci concatenated)."""
    folios: "collections.OrderedDict[str, list[str]]" = collections.OrderedDict()
    for raw in path.read_text(encoding="utf-8").splitlines():
        m = _FOLIO_LOC.match(raw)
        if not m:
            continue
        folio, body = m.group(1), m.group(2).replace(",", ".")
        toks = [t for t in (clean_token(r) for r in body.split(".")) if t]
        if toks:
            folios.setdefault(folio, []).extend(toks)
    return folios


def _mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def mirror_match_fraction(a: list[str], b: list[str]) -> float:
    """Fraction of aligned positions (from the start, over min length) where a==b."""
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    return sum(1 for i in range(n) if a[i] == b[i]) / n


def palindrome_fraction(seq: list[str]) -> float:
    """Fraction of mirror positions i where seq[i] == seq[L-1-i] (page self-mirror)."""
    L = len(seq)
    if L < 2:
        return 0.0
    half = L // 2
    return sum(1 for i in range(half) if seq[i] == seq[L - 1 - i]) / half


def facing_mirror_test(
    folios: "collections.OrderedDict[str, list[str]]", n_perm: int, seed: int
) -> dict:
    """Are facing folios MIRRORS of each other (not merely same-section neighbours)?

    The naive test "facing-page reverse-overlap > random-pair overlap" is CONFOUNDED:
    adjacent folios share section, scribe and vocabulary, so they overlap more than
    distant pages in EITHER alignment. The mirror-SPECIFIC statistic isolates the
    confound: mirror_effect = reverse_overlap - forward_overlap over the SAME pairs.
    Genuine mirroring makes reverse beat forward; shared vocabulary affects both
    equally so the difference is ~0. The null permutes which folio is each one's
    partner and recomputes the same difference. (Pre-registered adjudication.)
    """
    seqs = list(folios.values())
    n = len(seqs)
    if n < 3:
        return {"obs_reverse": 0.0, "obs_forward": 0.0, "mirror_effect": 0.0,
                "null_effect_mean": 0.0, "p": float("nan"), "n_pairs": 0}

    def scores(partner_pairs: list[tuple[int, int]]) -> tuple[float, float]:
        rev = _mean([mirror_match_fraction(seqs[a], seqs[b][::-1]) for a, b in partner_pairs])
        fwd = _mean([mirror_match_fraction(seqs[a], seqs[b]) for a, b in partner_pairs])
        return rev, fwd

    consecutive = [(i, i + 1) for i in range(n - 1)]
    obs_rev, obs_fwd = scores(consecutive)
    obs_effect = obs_rev - obs_fwd
    rng = random.Random(seed)
    null_effects: list[float] = []
    partners = list(range(n))
    for _ in range(n_perm):
        rng.shuffle(partners)
        rp = [(i, partners[i]) for i in range(n - 1)]
        r, f = scores(rp)
        null_effects.append(r - f)
    null_mean = _mean(null_effects)
    p = (sum(1 for x in null_effects if x >= obs_effect) + 1) / (n_perm + 1)
    return {"obs_reverse": obs_rev, "obs_forward": obs_fwd, "mirror_effect": obs_effect,
            "null_effect_mean": null_mean, "p": p, "n_pairs": n - 1}


def palindrome_page_test(
    folios: "collections.OrderedDict[str, list[str]]", n_perm: int, seed: int
) -> dict:
    """Are pages internally palindromic vs a within-page token-shuffle null?"""
    seqs = [s for s in folios.values() if len(s) >= 4]
    if not seqs:
        return {"observed": 0.0, "null_mean": 0.0, "p": float("nan"), "n_pages": 0}
    obs = _mean([palindrome_fraction(s) for s in seqs])
    rng = random.Random(seed)
    null_means: list[float] = []
    for _ in range(n_perm):
        scores = []
        for s in seqs:
            ss = s[:]
            rng.shuffle(ss)
            scores.append(palindrome_fraction(ss))
        null_means.append(_mean(scores))
    null_mean = _mean(null_means)
    p = (sum(1 for x in null_means if x >= obs) + 1) / (n_perm + 1)
    return {"observed": obs, "null_mean": null_mean, "p": p, "n_pages": len(seqs)}


# --------------------------------------------------------------------------- #
# Verdict                                                                      #
# --------------------------------------------------------------------------- #
def classify_verdict(de: dict[str, dict], facing: dict, palin: dict) -> tuple[str, dict]:
    """Decide whether any Leonardo operation beats the content-free baseline.

    de maps corpus-name -> directional_entropies dict. Decision channels:
      * directional_beyond_morphology: real word-edge asymmetry (dir_edge) differs
        from the generator's by > DIR_DELTA_THRESHOLD => word-ORDER carries a
        directional bigram signal the bag-of-words lacks (actionable).
      * morphology_artifact_confirmed: token reversal flips dir_edge sign and keeps
        magnitude (the gap is purely "which side the suffix is on").
      * reversal_lift: a reversal moves bulk h2 into [2.5, 3.6] (actionable).
      * mirror_signal: facing-page or palindrome test beats its null at p<0.05.
      * bulk_reversal_symmetric: |h2_fwd - h2_bwd| < tol on real (the theorem holds).
    """
    real, gen = de["real"], de["generator_base"]
    rev = de["real_reversed_tokens"]
    dir_delta = abs(real["dir_edge"] - gen["dir_edge"])
    directional_beyond_morphology = dir_delta > DIR_DELTA_THRESHOLD
    # token reversal should flip dir_edge sign with preserved magnitude => artifact
    flip_ok = (
        real["dir_edge"] * rev["dir_edge"] < 0
        and abs(abs(rev["dir_edge"]) - abs(real["dir_edge"])) < 0.30 * abs(real["dir_edge"])
        if abs(real["dir_edge"]) > 1e-9
        else False
    )
    reversal_lift = any(
        NL_H2_LOW <= de[c]["h2_fwd"] <= NL_H2_HIGH
        for c in ("real_reversed_tokens",)
    ) or (NL_H2_LOW <= real["h2_bwd"] <= NL_H2_HIGH)
    # mirror-SPECIFIC: reverse must beat forward (not just beat distant pages), p<0.01
    facing_sig = (
        not math.isnan(facing["p"]) and facing["p"] < 0.01
        and facing["mirror_effect"] > facing["null_effect_mean"]
        and facing["obs_reverse"] > facing["obs_forward"]
    )
    palin_sig = (
        not math.isnan(palin["p"]) and palin["p"] < 0.05
        and palin["observed"] > palin["null_mean"]
    )
    mirror_signal = facing_sig or palin_sig
    bulk_sym = abs(real["h2_fwd"] - real["h2_bwd"]) < BULK_SYMMETRY_TOL

    flags = {
        "bulk_reversal_symmetric": bulk_sym,
        "real_dir_edge": round(real["dir_edge"], 4),
        "generator_dir_edge": round(gen["dir_edge"], 4),
        "dir_edge_delta_vs_generator": round(dir_delta, 6),
        "morphology_artifact_confirmed": flip_ok,
        "directional_beyond_morphology": directional_beyond_morphology,
        "reversal_lift": reversal_lift,
        "facing_mirror_signal": facing_sig,
        "palindrome_signal": palin_sig,
    }
    if directional_beyond_morphology:
        verdict = "directional_word_order_signal"
    elif mirror_signal:
        verdict = "mirror_page_signal"
    elif reversal_lift:
        verdict = "reversal_lift"
    else:
        verdict = "leonardo_operations_degenerate"
    return verdict, flags


# --------------------------------------------------------------------------- #
# IO                                                                           #
# --------------------------------------------------------------------------- #
def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _r(x, nd: int = 4) -> str:
    return str(round(x, nd)) if isinstance(x, float) and math.isfinite(x) else str(x)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("corpus", nargs="?", default=str(DEFAULT_CORPUS))
    p.add_argument("--n-perm", type=int, default=300)
    p.add_argument("--seed", type=int, default=0)
    d = ROOT / "data" / "derived"
    p.add_argument("--out-summary", default=str(d / "directionality_summary_zl3b.csv"))
    p.add_argument("--out-corpora", default=str(d / "directionality_corpora_zl3b.csv"))
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    corpus = Path(args.corpus)
    lines, sections = parse_loci_with_section(corpus)

    variants: dict[str, list[list[str]]] = {
        "real": lines,
        "real_reversed_tokens": reverse_each_token(lines),
        "word_shuffle": global_word_shuffle(lines, args.seed),
    }
    variants.update(build_generator_corpora(lines, sections, args.seed))
    de = {name: directional_entropies(v) for name, v in variants.items()}

    folios = parse_folio_sequences(corpus)
    facing = facing_mirror_test(folios, args.n_perm, args.seed)
    palin = palindrome_page_test(folios, args.n_perm, args.seed)

    verdict, flags = classify_verdict(de, facing, palin)

    # --- per-corpus directional CSV ---
    corpora_rows = [
        {
            "corpus": name, "n_chars": d["n_chars"], "n_tokens": d["n_tokens"],
            "h1": _r(d["h1"]), "h2_fwd": _r(d["h2_fwd"]), "h2_bwd": _r(d["h2_bwd"]),
            "h3_fwd": _r(d["h3_fwd"]), "h3_bwd": _r(d["h3_bwd"]),
            "h_first": _r(d["h_first"]), "h_last": _r(d["h_last"]),
            "dir_edge": _r(d["dir_edge"]),
            "h_start_inward": _r(d["h_start_inward"]),
            "h_end_inward": _r(d["h_end_inward"]),
            "semantic_guardrail": GUARDRAIL,
        }
        for name, d in de.items()
    ]
    write_csv(
        Path(args.out_corpora), corpora_rows,
        ["corpus", "n_chars", "n_tokens", "h1", "h2_fwd", "h2_bwd", "h3_fwd",
         "h3_bwd", "h_first", "h_last", "dir_edge", "h_start_inward",
         "h_end_inward", "semantic_guardrail"],
    )

    # --- summary CSV ---
    real = de["real"]
    summary_rows = [
        {"metric": "real_h2_fwd", "value": _r(real["h2_fwd"])},
        {"metric": "real_h2_bwd", "value": _r(real["h2_bwd"])},
        {"metric": "real_h2_fwd_minus_bwd", "value": _r(real["h2_fwd"] - real["h2_bwd"], 6)},
        {"metric": "real_h3_fwd", "value": _r(real["h3_fwd"])},
        {"metric": "real_h3_bwd", "value": _r(real["h3_bwd"])},
        {"metric": "bulk_reversal_symmetric", "value": str(flags["bulk_reversal_symmetric"])},
        {"metric": "real_h_first_glyph", "value": _r(real["h_first"])},
        {"metric": "real_h_last_glyph", "value": _r(real["h_last"])},
        {"metric": "real_dir_edge", "value": _r(flags["real_dir_edge"])},
        {"metric": "generator_dir_edge", "value": _r(flags["generator_dir_edge"])},
        {"metric": "dir_edge_delta_vs_generator", "value": _r(flags["dir_edge_delta_vs_generator"], 6)},
        {"metric": "reversed_tokens_dir_edge", "value": _r(de["real_reversed_tokens"]["dir_edge"])},
        {"metric": "reversed_tokens_h2_fwd", "value": _r(de["real_reversed_tokens"]["h2_fwd"])},
        {"metric": "morphology_artifact_confirmed", "value": str(flags["morphology_artifact_confirmed"])},
        {"metric": "nl_h2_band", "value": f"[{NL_H2_LOW},{NL_H2_HIGH}]"},
        {"metric": "facing_reverse_overlap", "value": _r(facing["obs_reverse"], 6)},
        {"metric": "facing_forward_overlap", "value": _r(facing["obs_forward"], 6)},
        {"metric": "facing_mirror_effect", "value": _r(facing["mirror_effect"], 6)},
        {"metric": "facing_mirror_null_effect", "value": _r(facing["null_effect_mean"], 6)},
        {"metric": "facing_mirror_p", "value": _r(facing["p"], 6)},
        {"metric": "facing_mirror_n_pairs", "value": str(facing["n_pairs"])},
        {"metric": "palindrome_observed", "value": _r(palin["observed"], 6)},
        {"metric": "palindrome_null_mean", "value": _r(palin["null_mean"], 6)},
        {"metric": "palindrome_p", "value": _r(palin["p"], 6)},
        {"metric": "palindrome_n_pages", "value": str(palin["n_pages"])},
        {"metric": "directional_beyond_morphology", "value": str(flags["directional_beyond_morphology"])},
        {"metric": "reversal_lift", "value": str(flags["reversal_lift"])},
        {"metric": "facing_mirror_signal", "value": str(flags["facing_mirror_signal"])},
        {"metric": "palindrome_signal", "value": str(flags["palindrome_signal"])},
        {"metric": "n_folios", "value": str(len(folios))},
        {"metric": "verdict", "value": verdict},
        {"metric": "guardrail", "value": GUARDRAIL},
    ]
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    # --- console report ---
    print(f"corpus={corpus.name}  n_folios={len(folios)}")
    print("  corpus               h1    h2_fwd h2_bwd h3_fwd h3_bwd  Hfirst Hlast dir_edge")
    for name, d in de.items():
        print(
            f"  {name:<20} {d['h1']:.3f} {d['h2_fwd']:.3f}  {d['h2_bwd']:.3f}  "
            f"{d['h3_fwd']:.3f}  {d['h3_bwd']:.3f}   {d['h_first']:.3f} {d['h_last']:.3f} {d['dir_edge']:+.4f}"
        )
    print(
        f"REVERSAL-INVARIANCE: real h2_fwd-h2_bwd={real['h2_fwd']-real['h2_bwd']:+.5f} "
        f"(<{BULK_SYMMETRY_TOL}? {flags['bulk_reversal_symmetric']}) -> direction invisible at sequence level"
    )
    print(
        f"WORD-EDGE: real dir_edge={flags['real_dir_edge']:+.4f}  gen dir_edge={flags['generator_dir_edge']:+.4f}  "
        f"delta={flags['dir_edge_delta_vs_generator']:.4f} (<{DIR_DELTA_THRESHOLD}? morphology)  "
        f"token-reverse flips? {flags['morphology_artifact_confirmed']}"
    )
    print(
        f"facing-mirror: reverse={facing['obs_reverse']:.5f} forward={facing['obs_forward']:.5f} "
        f"effect={facing['mirror_effect']:+.5f} null={facing['null_effect_mean']:+.5f} p={facing['p']:.4g}"
    )
    print(
        f"palindrome: obs={palin['observed']:.5f} null={palin['null_mean']:.5f} p={palin['p']:.4g}"
    )
    print(f"VERDICT={verdict}")
    print(f"summary_csv={args.out_summary}")
    print(f"corpora_csv={args.out_corpora}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
