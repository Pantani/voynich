#!/usr/bin/env python3
"""Rota 58: real language (heavily encoded) vs low-content system?

THE decisive route. Rotas 43-57 established that the Voynich token is 100%
functional/lexical, word-level topicality is WEAK and prose-register (not
object-naming), and text and image are decoupled. The remaining question is
structural, not lexical: does Voynichese carry the statistical signatures of a
*real natural language that has been heavily encoded*, or of a *low-content
system* (generative / glossolalia-like with topical drift)?

This route measures the three classic structural signatures on the ZL3b corpus
and weighs them against natural-language baselines drawn from the literature
(labelled as anchors; NEVER recomputed here):

  1. CHARACTER CONDITIONAL ENTROPY -- the famous one.
     h0 = log2(alphabet), h1 = unigram char entropy, h2 = H(c_i | c_{i-1}).
     Also word-level H1_word and h2_word = H(w_i | w_{i-1}).
     Internal null: char-shuffle -> h2 collapses toward h1 (no 2nd-order
     structure), measuring how much local predictability really exists.
     Anchors: NL char h2 ~ 3.1-3.6 bits (English), Latin ~ 2.5-3.0; published
     Voynich h2 ~ 2.0-2.3 (Bennett/Stolfi). h2 < 2.5 -> "anomalously low/rigid".

  2. LAAFU (Line As A Functional Unit).
     Lines with >=3 tokens; bucket each token's position first/medial/last.
     I(word ; position_bucket) in bits with a permutation null (shuffle the
     position labels, ~300 perms) -> observed, null_mean, empirical p. Also the
     strongest line-edge glyph biases (line-initial FIRST glyph, line-final LAST
     glyph) vs the corpus first/last-glyph distribution. NL anchor: word identity
     is nearly invariant to line position (text wraps arbitrarily); strong
     I(word;position) beyond null is anomalous.

  3. ADJACENT SAME-TOKEN REPETITION.
     Within each line, positions where token[i]==token[i-1]. Observed rate vs the
     i.i.d. unigram expectation sum_w p(w)^2. NL anchor: adjacent same-word
     repetition in prose is < ~0.25%.

VERDICT: count the signatures in the low-content/anomalous range
  - char h2 < 2.5 bits
  - I(word;linepos) >> null (p<0.05 AND observed > ~2x null_mean)
  - adjacent_repeat ratio (observed/iid) > 3
  verdict = "low_content_signatures" if >=2/3 anomalous, "mixed" if 1,
  "language_like" if 0. Interpretation stays nuanced: anomalies may indicate
  low-content OR heavy encoding -- the coordinator + cryptanalyst weigh that.

NOT decifration: this is a language signature, not a decipherment. Guardrail in
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

from scripts.analyze_nucleus import clean_token

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota58_language_signature_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"

# A locus line carries tokens: <folio.unit[,marker]> body. Folio header lines
# (<f...> with no .unit) carry no tokens. This is the exact spec regex and
# mirrors scripts.analyze_nucleus so the token universe reproduces Rota 53/57.
_LOC = re.compile(r"^<f\d+[rv]\d?\.\d+[^>]*>\s*(.*)$")

SPACE = " "  # word-boundary symbol in the character stream


def parse_loci(path: Path) -> list[list[str]]:
    """Yield, per locus line, the ordered list of clean tokens (empties dropped).

    Each locus line is treated as one "line" with its token order preserved.
    Folio header lines carry no tokens and are skipped. Tokenization mirrors
    analyze_nucleus.parse_corpus (clean_token, split on '.', commas first mapped
    to '.'), so the flattened token total matches Rota 53/57 (37671 tokens).
    """
    lines: list[list[str]] = []
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        m = _LOC.match(raw_line)
        if not m:
            continue
        body = m.group(1).replace(",", ".")
        toks = [t for t in (clean_token(r) for r in body.split(".")) if t]
        if toks:
            lines.append(toks)
    return lines


# --------------------------------------------------------------------------- #
# Entropy primitives                                                          #
# --------------------------------------------------------------------------- #
def shannon_entropy(counter: collections.Counter) -> float:
    """Shannon entropy in bits of a Counter of outcome frequencies."""
    n = sum(counter.values())
    if n == 0:
        return 0.0
    h = 0.0
    for c in counter.values():
        if c:
            p = c / n
            h -= p * math.log2(p)
    return h


def conditional_entropy(
    pair_counts: collections.Counter, prev_counts: collections.Counter
) -> float:
    """H(X_i | X_{i-1}) in bits from joint (prev,cur) and marginal prev counts.

    H(cur|prev) = H(prev,cur) - H(prev), computed over the SAME population of
    adjacent pairs (prev_counts is the marginal of the first element of every
    counted pair, so both entropies share the denominator N_pairs).
    """
    n = sum(pair_counts.values())
    if n == 0:
        return 0.0
    h_joint = shannon_entropy(pair_counts)
    h_prev = shannon_entropy(prev_counts)
    return h_joint - h_prev


def char_entropies(lines: list[list[str]]) -> dict:
    """Character-level h0/h1/h2 over the space-joined stream.

    The stream is the tokens of each line joined by a single SPACE symbol, with
    lines concatenated (also separated by SPACE, so a line boundary is just
    another word boundary -- there is no special end-of-line symbol). The
    alphabet is every distinct symbol present (EVA letters + SPACE).
    """
    stream = _char_stream(lines)
    uni = collections.Counter(stream)
    alphabet_size = len(uni)
    h0 = math.log2(alphabet_size) if alphabet_size > 0 else 0.0
    h1 = shannon_entropy(uni)

    pair_counts: collections.Counter = collections.Counter()
    prev_counts: collections.Counter = collections.Counter()
    for a, b in zip(stream, stream[1:]):
        pair_counts[(a, b)] += 1
        prev_counts[a] += 1
    h2 = conditional_entropy(pair_counts, prev_counts)

    return {
        "stream_len": len(stream),
        "alphabet_size": alphabet_size,
        "alphabet": "".join(sorted(uni)),
        "h0": h0,
        "h1": h1,
        "h2": h2,
    }


def _char_stream(lines: list[list[str]]) -> list[str]:
    """Flatten lines into one character list, tokens separated by SPACE."""
    words = [t for line in lines for t in line]
    text = SPACE.join(words)
    return list(text)


def shuffled_char_h2(lines: list[list[str]], seed: int) -> float:
    """h2 of the character stream after a full shuffle (destroys order).

    Under a global character shuffle the bigram structure is gone, so
    H(c_i|c_{i-1}) collapses to ~h1; the gap (real h2 below this) is the local
    predictability that genuine adjacency contributes.
    """
    stream = _char_stream(lines)
    rng = random.Random(seed)
    shuffled = stream[:]
    rng.shuffle(shuffled)
    pair_counts: collections.Counter = collections.Counter()
    prev_counts: collections.Counter = collections.Counter()
    for a, b in zip(shuffled, shuffled[1:]):
        pair_counts[(a, b)] += 1
        prev_counts[a] += 1
    return conditional_entropy(pair_counts, prev_counts)


def word_entropies(lines: list[list[str]]) -> dict:
    """Word-level H1_word and h2_word = H(w_i | w_{i-1}).

    Adjacent word pairs are taken WITHIN each line only (no pair spans a line
    boundary), matching the line-as-unit framing; the unigram marginal H1_word
    is over all tokens.
    """
    uni: collections.Counter = collections.Counter()
    pair_counts: collections.Counter = collections.Counter()
    prev_counts: collections.Counter = collections.Counter()
    for line in lines:
        for t in line:
            uni[t] += 1
        for a, b in zip(line, line[1:]):
            pair_counts[(a, b)] += 1
            prev_counts[a] += 1
    return {
        "n_tokens": sum(uni.values()),
        "n_types": len(uni),
        "h1_word": shannon_entropy(uni),
        "h2_word": conditional_entropy(pair_counts, prev_counts),
    }


# --------------------------------------------------------------------------- #
# Measure 2: LAAFU -- line-as-a-functional-unit                               #
# --------------------------------------------------------------------------- #
def _position_bucket(idx: int, length: int) -> str:
    if idx == 0:
        return "first"
    if idx == length - 1:
        return "last"
    return "medial"


def laafu_pairs(lines: list[list[str]]) -> list[tuple[str, str]]:
    """[(word, position_bucket), ...] over lines with >=3 tokens.

    Restricting to >=3 keeps all three buckets (first/medial/last) populated and
    well-defined for every counted line.
    """
    pairs: list[tuple[str, str]] = []
    for line in lines:
        n = len(line)
        if n < 3:
            continue
        for i, tok in enumerate(line):
            pairs.append((tok, _position_bucket(i, n)))
    return pairs


def mutual_information(pairs: list[tuple[str, str]]) -> float:
    """I(X;Y) in bits from a list of (X,Y) observations.

    I = H(X) + H(Y) - H(X,Y), all plug-in (MLE) Shannon entropies in bits.
    """
    if not pairs:
        return 0.0
    xs = collections.Counter(x for x, _ in pairs)
    ys = collections.Counter(y for _, y in pairs)
    joint = collections.Counter(pairs)
    return shannon_entropy(xs) + shannon_entropy(ys) - shannon_entropy(joint)


def laafu_permutation_null(
    pairs: list[tuple[str, str]], n_perm: int, seed: int
) -> tuple[float, float, float]:
    """Permutation null for I(word;position): observed, null_mean, empirical p.

    The position labels are shuffled across all tokens, breaking any
    word<->position dependence while preserving both marginals. p = fraction of
    permutations whose I >= observed (add-one smoothed).
    """
    observed = mutual_information(pairs)
    if n_perm <= 0 or not pairs:
        return observed, float("nan"), float("nan")
    rng = random.Random(seed)
    words = [w for w, _ in pairs]
    positions = [p for _, p in pairs]
    total = 0.0
    hits = 0
    for _ in range(n_perm):
        rng.shuffle(positions)
        mi = mutual_information(list(zip(words, positions)))
        total += mi
        if mi >= observed:
            hits += 1
    null_mean = total / n_perm
    p = (hits + 1) / (n_perm + 1)
    return observed, null_mean, p


def line_edge_biases(
    lines: list[list[str]], top_k: int = 3
) -> tuple[list[dict], list[dict]]:
    """Top over-represented line-initial first-glyphs and line-final last-glyphs.

    For line-INITIAL tokens we compare the distribution of their FIRST glyph to
    the corpus-wide first-glyph distribution (every token's first glyph). For
    line-FINAL tokens we compare their LAST glyph to the corpus-wide last-glyph
    distribution. Only lines with >=3 tokens contribute an edge token (so the
    edge is unambiguous); the corpus baseline uses all tokens. ratio =
    edge_frac / corpus_frac (over-representation factor).
    """
    corpus_first: collections.Counter = collections.Counter()
    corpus_last: collections.Counter = collections.Counter()
    edge_first: collections.Counter = collections.Counter()
    edge_last: collections.Counter = collections.Counter()
    for line in lines:
        for t in line:
            corpus_first[t[0]] += 1
            corpus_last[t[-1]] += 1
        if len(line) >= 3:
            edge_first[line[0][0]] += 1
            edge_last[line[-1][-1]] += 1

    def _rows(edge: collections.Counter, corpus: collections.Counter, label: str):
        n_edge = sum(edge.values())
        n_corpus = sum(corpus.values())
        out = []
        for glyph, cnt in edge.items():
            ef = cnt / n_edge if n_edge else 0.0
            cf = corpus.get(glyph, 0) / n_corpus if n_corpus else 0.0
            ratio = ef / cf if cf > 0 else float("inf")
            out.append(
                {
                    "edge": label,
                    "glyph": glyph,
                    "edge_frac": round(ef, 6),
                    "corpus_frac": round(cf, 6),
                    "ratio": round(ratio, 4) if math.isfinite(ratio) else ratio,
                }
            )
        # most over-represented first; finite ratios rank by value
        out.sort(key=lambda r: (r["ratio"] if math.isfinite(r["ratio"]) else 1e9), reverse=True)
        return out[:top_k]

    return _rows(edge_first, corpus_first, "initial"), _rows(edge_last, corpus_last, "final")


# --------------------------------------------------------------------------- #
# Measure 3: adjacent same-token repetition                                   #
# --------------------------------------------------------------------------- #
def adjacent_repeats(lines: list[list[str]]) -> dict:
    """Adjacent same-token repetition rate vs the i.i.d. unigram expectation.

    Within each line, count adjacent pairs and how many are token[i]==token[i-1].
    expected_iid = sum_w p(w)^2 is the probability two independent unigram draws
    match (the collision probability). ratio = observed / expected_iid. Also the
    top adjacent-repeated tokens with their counts.
    """
    uni: collections.Counter = collections.Counter()
    adj_pairs = 0
    repeats = 0
    repeat_tokens: collections.Counter = collections.Counter()
    for line in lines:
        for t in line:
            uni[t] += 1
        for a, b in zip(line, line[1:]):
            adj_pairs += 1
            if a == b:
                repeats += 1
                repeat_tokens[a] += 1
    n_tokens = sum(uni.values())
    expected_iid = (
        sum((c / n_tokens) ** 2 for c in uni.values()) if n_tokens else 0.0
    )
    observed = repeats / adj_pairs if adj_pairs else 0.0
    ratio = observed / expected_iid if expected_iid > 0 else float("inf")
    return {
        "adj_pairs": adj_pairs,
        "repeats": repeats,
        "observed": observed,
        "expected_iid": expected_iid,
        "ratio": ratio,
        "repeat_tokens": repeat_tokens,
    }


# --------------------------------------------------------------------------- #
# Verdict                                                                     #
# --------------------------------------------------------------------------- #
def classify_verdict(
    h2_char: float,
    i_obs: float,
    i_null_mean: float,
    i_p: float,
    adj_ratio: float,
) -> tuple[int, str, dict]:
    """Count anomalous signatures and assign the verdict label."""
    anom_h2 = h2_char < 2.5
    anom_laafu = (
        not math.isnan(i_p)
        and i_p < 0.05
        and not math.isnan(i_null_mean)
        and i_obs > 2.0 * i_null_mean
    )
    anom_repeat = math.isfinite(adj_ratio) and adj_ratio > 3.0
    n = int(anom_h2) + int(anom_laafu) + int(anom_repeat)
    if n >= 2:
        verdict = "low_content_signatures"
    elif n == 1:
        verdict = "mixed"
    else:
        verdict = "language_like"
    flags = {
        "char_h2_anomalous": anom_h2,
        "laafu_anomalous": anom_laafu,
        "adjacent_repeat_anomalous": anom_repeat,
    }
    return n, verdict, flags


# --------------------------------------------------------------------------- #
# IO                                                                          #
# --------------------------------------------------------------------------- #
def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("corpus", nargs="?", default=str(DEFAULT_CORPUS))
    p.add_argument("--n-perm", type=int, default=300)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--top-k", type=int, default=3)
    p.add_argument("--top-repeats", type=int, default=20)
    d = ROOT / "data" / "derived"
    p.add_argument("--out-summary", default=str(d / "language_signature_summary_zl3b.csv"))
    p.add_argument("--out-lineedge", default=str(d / "language_signature_lineedge_zl3b.csv"))
    p.add_argument("--out-repeats", default=str(d / "language_signature_repeats_zl3b.csv"))
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    lines = parse_loci(Path(args.corpus))

    # 1) character + word entropies
    ce = char_entropies(lines)
    h2_shuffled = shuffled_char_h2(lines, args.seed)
    we = word_entropies(lines)

    # 2) LAAFU
    pairs = laafu_pairs(lines)
    i_obs, i_null_mean, i_p = laafu_permutation_null(pairs, args.n_perm, args.seed)
    init_rows, final_rows = line_edge_biases(lines, args.top_k)

    # 3) adjacent repeats
    rep = adjacent_repeats(lines)

    n_anom, verdict, flags = classify_verdict(
        ce["h2"], i_obs, i_null_mean, i_p, rep["ratio"]
    )

    # --- summary CSV ---
    summary_rows = [
        {"metric": "alphabet_size", "value": str(ce["alphabet_size"])},
        {"metric": "h0", "value": str(round(ce["h0"], 4))},
        {"metric": "h1", "value": str(round(ce["h1"], 4))},
        {"metric": "h2_char", "value": str(round(ce["h2"], 4))},
        {"metric": "h2_char_shuffled", "value": str(round(h2_shuffled, 4))},
        {"metric": "H1_word", "value": str(round(we["h1_word"], 4))},
        {"metric": "h2_word", "value": str(round(we["h2_word"], 4))},
        {"metric": "I_word_linepos_bits", "value": str(round(i_obs, 6))},
        {
            "metric": "I_linepos_null_mean",
            "value": str(round(i_null_mean, 6)) if not math.isnan(i_null_mean) else "nan",
        },
        {
            "metric": "I_linepos_p",
            "value": str(round(i_p, 6)) if not math.isnan(i_p) else "nan",
        },
        {"metric": "adjacent_repeat_rate", "value": str(round(rep["observed"], 8))},
        {"metric": "adjacent_repeat_iid", "value": str(round(rep["expected_iid"], 8))},
        {
            "metric": "adjacent_repeat_ratio",
            "value": str(round(rep["ratio"], 4)) if math.isfinite(rep["ratio"]) else "inf",
        },
        {"metric": "n_anomalous_signatures", "value": str(n_anom)},
        {"metric": "char_h2_anomalous", "value": str(flags["char_h2_anomalous"])},
        {"metric": "laafu_anomalous", "value": str(flags["laafu_anomalous"])},
        {"metric": "adjacent_repeat_anomalous", "value": str(flags["adjacent_repeat_anomalous"])},
        {"metric": "n_lines", "value": str(len(lines))},
        {"metric": "n_tokens", "value": str(we["n_tokens"])},
        {"metric": "n_chars_stream", "value": str(ce["stream_len"])},
        {"metric": "verdict", "value": verdict},
        {"metric": "guardrail", "value": GUARDRAIL},
    ]
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    # --- line-edge CSV ---
    edge_rows: list[dict] = []
    for r in init_rows + final_rows:
        rr = dict(r)
        rr["semantic_guardrail"] = GUARDRAIL
        # render inf ratio as string for CSV stability
        if not math.isfinite(rr["ratio"]):
            rr["ratio"] = "inf"
        edge_rows.append(rr)
    write_csv(
        Path(args.out_lineedge),
        edge_rows,
        ["edge", "glyph", "edge_frac", "corpus_frac", "ratio", "semantic_guardrail"],
    )

    # --- repeats CSV ---
    repeat_rows = [
        {
            "token": tok,
            "adjacent_repeat_count": cnt,
            "semantic_guardrail": GUARDRAIL,
        }
        for tok, cnt in rep["repeat_tokens"].most_common(args.top_repeats)
    ]
    write_csv(
        Path(args.out_repeats),
        repeat_rows,
        ["token", "adjacent_repeat_count", "semantic_guardrail"],
    )

    # --- console report ---
    print(
        f"alphabet_size={ce['alphabet_size']} h0={ce['h0']:.4f} h1={ce['h1']:.4f} "
        f"h2_char={ce['h2']:.4f} h2_char_shuffled={h2_shuffled:.4f}"
    )
    print(f"H1_word={we['h1_word']:.4f} h2_word={we['h2_word']:.4f}")
    print(
        f"I(word;linepos)={i_obs:.6f} null_mean={i_null_mean:.6f} p={i_p:.4g} "
        f"(n_perm={args.n_perm})"
    )
    print(f"line-initial first-glyph biases (top {args.top_k}): "
          f"{[(r['glyph'], r['ratio']) for r in init_rows]}")
    print(f"line-final last-glyph biases (top {args.top_k}): "
          f"{[(r['glyph'], r['ratio']) for r in final_rows]}")
    print(
        f"adjacent_repeat_rate={rep['observed']:.6f} iid={rep['expected_iid']:.6f} "
        f"ratio={rep['ratio']:.4f} top={rep['repeat_tokens'].most_common(3)}"
    )
    print(f"n_anomalous_signatures={n_anom} flags={flags} VERDICT={verdict}")
    print(f"n_lines={len(lines)} n_tokens={we['n_tokens']} n_chars={ce['stream_len']}")
    print(f"summary_csv={args.out_summary}")
    print(f"lineedge_csv={args.out_lineedge}")
    print(f"repeats_csv={args.out_repeats}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
