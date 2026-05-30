#!/usr/bin/env python3
"""Rota 61: re-segmentation — is there HIDDEN order-structure below the token grid?

THE last decisive falsification of the "what is Voynichese" arc. Rotas 43-60
settled: the token is 100% functional; word-content is weak prose-register; it is
NOT natural-language prose; it is morphologically RICH but syntactically THIN; and
(R60) it compresses ~ like its own bag-of-words (word ORDER carries only ~1-3% of
the compressibility, vs 12-25% in natural prose) -> NO sentence-level syntax AT
THE TOKEN SCALE.

The ONE surviving "meaningful" hypothesis is a VERBOSE CIPHER: 1 plaintext word ->
MANY Voynich tokens, so the true linguistic units are NOT the space-delimited
tokens and the syntax is hidden BELOW / ACROSS the token grid. If so, RE-SEGMENTING
the character stream into better units should REVIVE the order-structure that the
token grid hid.

THE TRAP: a greedy merge re-segmentation (BPE) mechanically manufactures recurring
units and apparent structure in ANY text, so an absolute "revival" is meaningless.
The test must be DIFFERENTIAL: apply the IDENTICAL BPE pipeline to Voynich AND to
structure-matched NULLS (R60's markov2_char and bag-of-words surrogates), and ask
whether Voynich's order-structure revives MORE than the nulls'.

PIPELINE
  1. Per-line token/char data (reuse R60 parse_loci). Space-joined char stream and
     ordered word sequence. The line (locus) is the BPE boundary unit: no merge may
     span a line break (it would invent cross-line bigrams that never co-occur).
  2. BPE on the CHARACTER stream: start with single chars as symbols; K times, find
     the most frequent adjacent symbol-pair NOT crossing a line boundary and merge
     it into one new symbol everywhere. Result = a re-segmented UNIT sequence. The
     space between tokens is itself a stream symbol, so a merge MAY swallow a former
     space; we report cross_boundary_merge_frac = fraction of final units whose
     surface text contains a space (descriptive: high => the token grid's spaces are
     NOT the natural unit boundaries).
  3. Two equal-(line-)length SURROGATES (seeded), reusing R60 generators:
     markov2_char and word_unigram (bag-of-words). Each surrogate is re-cut into the
     SAME per-line char lengths as the real stream (identical BPE boundary geometry),
     then BPE is RE-LEARNED on it independently -> its own unit sequence.
  4. DECISIVE METRIC -- order gain AFTER re-segmentation. Serialize a unit sequence's
     unit-IDs to fixed-width bytes; compress (lzma) the REAL unit order vs a SHUFFLED
     unit order (= bag-of-units: preserves unit frequency, destroys order).
         order_gain = (C_shuffled - C_real) / C_shuffled
     Computed for: Voynich @ token segmentation (sanity: must ~ reproduce R60's
     gain_over_wordunigram ~0.03); Voynich @ BPE-K units; markov2 @ BPE-K units;
     bag-of-words @ BPE-K units.
  5. DIFFERENTIAL: revival_voy = order_gain(Voynich BPE);
     revival_markov / revival_bow likewise; signal = revival_voy - max(surrogates).

VERDICT (encode):
  - revival_voy clearly EXCEEDS both surrogates (differential > ~0.02 absolute AND
    revival_voy > ~1.5x the larger surrogate) -> "hidden_structure": re-segmentation
    recovers order-structure the token grid hid -> verbose-cipher / re-segmentable
    meaning stays ALIVE.
  - otherwise -> "no_hidden_structure": BPE revival is purely mechanical; no order
    structure beyond the rigid morphology -> the token grid IS the natural unit;
    syntactic thinness is fundamental -> generator / constructed.

CAVEAT (reported): BPE is a heuristic and K-dependent; an absolute revival number is
not portable. The DIFFERENTIAL (real minus structure-matched null) is K-robust to
first order because all streams pass through the SAME pipeline. This is NOT a
decipherment: it measures order-compressibility of re-segmented units, not meaning.
Guardrail in every output CSV.
"""
from __future__ import annotations

import argparse
import bz2
import collections
import csv
import lzma
import random
from pathlib import Path

from scripts.analyze_compressibility import (
    gen_markov2_char,
    gen_word_unigram,
    word_sequence,
)
from scripts.analyze_language_signature import SPACE, parse_loci

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota61_resegment_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"

DEFAULT_K = 300
# Verdict thresholds on the differential (revival_voy - max surrogate).
DIFFERENTIAL_ABS = 0.02
DIFFERENTIAL_RATIO = 1.5


# --------------------------------------------------------------------------- #
# Line construction (the BPE boundary unit)                                   #
# --------------------------------------------------------------------------- #
def char_lines(lines: list[list[str]]) -> list[list[str]]:
    """Per-locus list of single-character symbols (tokens space-joined WITHIN a line).

    The flattened concatenation `SPACE.join(SPACE.join(line) for line in ...)` is the
    real character stream (== R60's `_char_stream` up to the line-vs-global join,
    which is identical since both insert one SPACE between every adjacent token).
    Here we keep the line grouping so BPE never merges across a line break. Each
    inner element is a length-1 string (the initial BPE symbol = one character).
    """
    return [list(SPACE.join(toks)) for toks in lines if toks]


def recut_stream_to_line_lengths(stream: str, line_lengths: list[int]) -> list[list[str]]:
    """Slice a flat char string into lines of the given per-line lengths.

    Used to give a surrogate the SAME line geometry (count + per-line char lengths)
    as the real corpus, so its BPE has identical boundary constraints. Any leftover
    characters (from rounding in generation) are dropped; a short final line is
    truncated to what is available.
    """
    out: list[list[str]] = []
    pos = 0
    n = len(stream)
    for length in line_lengths:
        if pos >= n:
            break
        chunk = stream[pos : pos + length]
        if chunk:
            out.append(list(chunk))
        pos += length
    return out


# --------------------------------------------------------------------------- #
# BPE (byte-pair encoding) on the character stream                            #
# --------------------------------------------------------------------------- #
def _count_pairs(lines: list[list[str]]) -> collections.Counter:
    """Count adjacent symbol-pairs WITHIN each line (never across a line break)."""
    pairs: collections.Counter = collections.Counter()
    for line in lines:
        for a, b in zip(line, line[1:]):
            pairs[(a, b)] += 1
    return pairs


def _merge_pair(lines: list[list[str]], pair: tuple[str, str], new_sym: str) -> None:
    """Replace every adjacent occurrence of `pair` with `new_sym`, in place per line.

    Left-to-right, non-overlapping (after a merge we advance past the new symbol),
    which is the standard BPE merge semantics.
    """
    a, b = pair
    for li, line in enumerate(lines):
        merged: list[str] = []
        i = 0
        L = len(line)
        while i < L:
            if i < L - 1 and line[i] == a and line[i + 1] == b:
                merged.append(new_sym)
                i += 2
            else:
                merged.append(line[i])
                i += 1
        lines[li] = merged


def learn_bpe(
    char_lines_in: list[list[str]], k: int
) -> tuple[list[list[str]], dict[str, str], list[tuple[str, str]]]:
    """Run K BPE merges on per-line char symbols.

    Returns (segmented_lines, vocab, merges) where:
      * segmented_lines  -- lines of UNIT symbols after K merges (deterministic);
      * vocab            -- unit-symbol -> its surface text (concatenated chars),
                            for EVERY symbol present after merging (incl. unmerged
                            single chars);
      * merges           -- the ordered list of merged (left, right) symbol pairs.

    The most-frequent pair is chosen each round; ties are broken deterministically
    by the pair key (so the run is fully reproducible). New symbols are named with a
    private-use prefix that cannot collide with EVA characters or the space.
    """
    # deep copy so the caller's input is untouched
    lines = [line[:] for line in char_lines_in]
    # surface[sym] = the literal text the symbol expands to
    surface: dict[str, str] = {}
    for line in lines:
        for s in line:
            surface.setdefault(s, s)
    merges: list[tuple[str, str]] = []
    for step in range(k):
        pairs = _count_pairs(lines)
        if not pairs:
            break
        best_count = max(pairs.values())
        # deterministic tie-break: smallest pair key among the maxima
        best_pair = min(p for p, c in pairs.items() if c == best_count)
        if best_count < 1:
            break
        new_sym = f"{step}"  # private-use prefix -> no collision with EVA
        surface[new_sym] = surface[best_pair[0]] + surface[best_pair[1]]
        _merge_pair(lines, best_pair, new_sym)
        merges.append(best_pair)
    # vocab = surface of every symbol that survives in the segmented lines
    present: set[str] = {s for line in lines for s in line}
    vocab = {s: surface[s] for s in present}
    return lines, vocab, merges


def cross_boundary_merge_frac(segmented_lines: list[list[str]], vocab: dict[str, str]) -> float:
    """Fraction of UNIT TOKENS in the stream whose surface text contains a space.

    A unit spans a former word boundary iff its expanded surface contains the SPACE
    symbol. We weight by occurrence (every emitted unit counts), so this is the
    share of the re-segmented stream that ignores the token grid's spaces. High =>
    the spaces are not the natural unit boundaries.
    """
    total = 0
    crossing = 0
    for line in segmented_lines:
        for s in line:
            total += 1
            if SPACE in vocab.get(s, s):
                crossing += 1
    return crossing / total if total else 0.0


# --------------------------------------------------------------------------- #
# Order gain via compression of serialized unit-IDs                           #
# --------------------------------------------------------------------------- #
def _flatten(lines: list[list[str]]) -> list[str]:
    """Flatten per-line unit symbols into one unit sequence (reading order)."""
    return [s for line in lines for s in line]


def _bytes_per_id(vocab_size: int) -> int:
    """Minimum whole bytes needed to index `vocab_size` distinct unit IDs (>=1)."""
    n = max(1, vocab_size)
    width = 1
    while (1 << (8 * width)) < n:
        width += 1
    return width


def serialize_units(
    units: list[str], id_map: dict[str, int] | None = None
) -> tuple[bytes, int]:
    """Map units to dense integer IDs and pack big-endian into fixed-width bytes.

    Fixed width (same for every unit) so the byte length is exactly
    len(units) * bytes_per_id; the compressor then sees pure ORDER information.

    If `id_map` is given it is REUSED (unit -> id), so serializing a permutation of
    the same units yields a byte-IDENTICAL multiset (only order differs) -- the fair
    basis for the order_gain comparison. If omitted, IDs are assigned in
    first-appearance order. Returns (packed_bytes, vocab_size).
    """
    if id_map is None:
        id_map = {}
        for u in units:
            if u not in id_map:
                id_map[u] = len(id_map)
    width = _bytes_per_id(len(id_map))
    buf = bytearray()
    for u in units:
        buf += id_map[u].to_bytes(width, "big")
    return bytes(buf), len(id_map)


def _lzma_size(data: bytes) -> int:
    """Compressed size in BYTES under lzma at maximum preset (reuses R60's choice)."""
    return len(lzma.compress(data, preset=9 | lzma.PRESET_EXTREME))


def _bz2_size(data: bytes) -> int:
    """Compressed size in BYTES under bz2 (BWT-based, level 9) — robustness twin."""
    return len(bz2.compress(data, 9))


def _order_gain(units: list[str], seed: int, sizer) -> tuple[float, int]:
    """Order-information gain of a unit sequence vs its own bag-of-units.

    Serializes the REAL unit order and a SHUFFLED copy (same multiset of unit IDs,
    so identical 0th-order content; only ORDER differs), compresses both with the
    given `sizer` (a bytes->compressed-size fn), and returns
    ((C_shuffled - C_real) / C_shuffled, vocab_size). Positive => the real order
    carries exploitable redundancy beyond unit frequency.
    """
    if not units:
        return 0.0, 0
    # Build the id_map ONCE and reuse it for the shuffle so the two serializations
    # share a byte-identical multiset; only the ORDER differs.
    id_map: dict[str, int] = {}
    for u in units:
        if u not in id_map:
            id_map[u] = len(id_map)
    real_bytes, vocab_size = serialize_units(units, id_map)
    rng = random.Random(seed)
    shuffled = units[:]
    rng.shuffle(shuffled)
    shuf_bytes, _ = serialize_units(shuffled, id_map)
    c_real = sizer(real_bytes)
    c_shuf = sizer(shuf_bytes)
    if c_shuf <= 0:
        return 0.0, vocab_size
    return (c_shuf - c_real) / c_shuf, vocab_size


def order_gain_lzma(units: list[str], seed: int) -> tuple[float, int]:
    """Order gain under lzma (LZ77+range). See _order_gain."""
    return _order_gain(units, seed, _lzma_size)


def order_gain_bz2(units: list[str], seed: int) -> tuple[float, int]:
    """Order gain under bz2 (BWT). The R60 LESSON: an lzma-only word-order gain near
    threshold can be a compressor artifact that bz2 does NOT confirm — so the
    `hidden_structure` claim must survive on BOTH compressors. See _order_gain."""
    return _order_gain(units, seed, _bz2_size)


# --------------------------------------------------------------------------- #
# Differential + verdict                                                       #
# --------------------------------------------------------------------------- #
def differential(revival_voy: float, revival_markov: float, revival_bow: float) -> float:
    """revival_voy minus the larger of the two surrogate revivals."""
    return revival_voy - max(revival_markov, revival_bow)


def classify_verdict(
    revival_voy: float, revival_markov: float, revival_bow: float
) -> str:
    """Differential verdict (K-robust to first order).

    'hidden_structure' iff the differential exceeds DIFFERENTIAL_ABS in absolute
    terms AND revival_voy exceeds DIFFERENTIAL_RATIO x the larger surrogate (so a
    tiny surrogate baseline cannot trip the ratio alone). Otherwise
    'no_hidden_structure'.
    """
    larger = max(revival_markov, revival_bow)
    diff = revival_voy - larger
    ratio_ok = revival_voy > DIFFERENTIAL_RATIO * larger if larger > 0 else revival_voy > 0
    if diff > DIFFERENTIAL_ABS and ratio_ok:
        return "hidden_structure"
    return "no_hidden_structure"


def _diff_ok(revival_voy: float, revival_markov: float, revival_bow: float) -> bool:
    """True iff the differential clears BOTH the absolute and ratio gates."""
    larger = max(revival_markov, revival_bow)
    diff = revival_voy - larger
    ratio_ok = revival_voy > DIFFERENTIAL_RATIO * larger if larger > 0 else revival_voy > 0
    return diff > DIFFERENTIAL_ABS and ratio_ok


def classify_verdict_both(
    lz: tuple[float, float, float], bz: tuple[float, float, float]
) -> str:
    """Robust verdict requiring the differential to hold on BOTH compressors.

    Each arg is (revival_voy, revival_markov, revival_bow) for one compressor.
    - 'hidden_structure_robust': gates pass on lzma AND bz2.
    - 'lzma_artifact': passes on lzma but COLLAPSES on bz2 (the Rota 60 pattern —
      an lzma-only gain that bz2 does not confirm is a compressor artifact, NOT
      hidden structure). This is the honest 'no hidden structure' outcome.
    - 'bz2_only_ambiguous': passes on bz2 only (rare; flag for inspection).
    - 'no_hidden_structure': fails on both.
    """
    lz_ok = _diff_ok(*lz)
    bz_ok = _diff_ok(*bz)
    if lz_ok and bz_ok:
        return "hidden_structure_robust"
    if lz_ok and not bz_ok:
        return "lzma_artifact"
    if bz_ok and not lz_ok:
        return "bz2_only_ambiguous"
    return "no_hidden_structure"


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
    return str(round(x, nd))


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("corpus", nargs="?", default=str(DEFAULT_CORPUS))
    p.add_argument("-K", "--merges", type=int, default=DEFAULT_K, help="number of BPE merges")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument(
        "--extra-k",
        default="",
        help="comma-separated extra K values for differential-stability check "
        "(e.g. '150,500'); reported to console + summary only",
    )
    d = ROOT / "data" / "derived"
    p.add_argument("--out-table", default=str(d / "resegment_zl3b.csv"))
    p.add_argument("--out-summary", default=str(d / "resegment_summary_zl3b.csv"))
    return p.parse_args(argv)


def _build_surrogate_lines(
    real_stream: str, words: list[str], line_lengths: list[int], seed: int
) -> tuple[list[list[str]], list[list[str]]]:
    """Generate markov2 + bag-of-words surrogates and re-cut to the real line geometry.

    Each surrogate is generated to the real stream length (R60 generators), then
    sliced into the same per-line char lengths so BPE sees identical line boundaries.
    Distinct seed offsets keep the two surrogates independent yet reproducible.
    """
    n = len(real_stream)
    markov = gen_markov2_char(real_stream, n, seed + 2)
    bow = gen_word_unigram(words, n, seed + 3)
    markov_lines = recut_stream_to_line_lengths(markov, line_lengths)
    bow_lines = recut_stream_to_line_lengths(bow, line_lengths)
    return markov_lines, bow_lines


def _differential_at_k(
    voy_char_lines: list[list[str]],
    markov_char_lines: list[list[str]],
    bow_char_lines: list[list[str]],
    k: int,
    seed: int,
) -> dict[str, float]:
    """Run BPE@k on all three streams and return their revivals + differential."""
    voy_seg, voy_vocab, _ = learn_bpe(voy_char_lines, k)
    mk_seg, _, _ = learn_bpe(markov_char_lines, k)
    bw_seg, _, _ = learn_bpe(bow_char_lines, k)
    rv_voy, voy_units_vocab = order_gain_lzma(_flatten(voy_seg), seed + 10)
    rv_mk, _ = order_gain_lzma(_flatten(mk_seg), seed + 11)
    rv_bw, _ = order_gain_lzma(_flatten(bw_seg), seed + 12)
    return {
        "revival_voy": rv_voy,
        "revival_markov": rv_mk,
        "revival_bow": rv_bw,
        "differential": differential(rv_voy, rv_mk, rv_bw),
        "cross_boundary_merge_frac": cross_boundary_merge_frac(voy_seg, voy_vocab),
        "voy_units_vocab": float(voy_units_vocab),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    lines = parse_loci(Path(args.corpus))
    words = word_sequence(lines)
    real_stream = SPACE.join(words)
    k = args.merges
    seed = args.seed

    # Per-line char symbols (BPE boundary unit) + their lengths.
    voy_char_lines = char_lines(lines)
    line_lengths = [len(line) for line in voy_char_lines]

    # --- SANITY: order gain at the TOKEN segmentation (units = whole tokens) ---
    # The token sequence is exactly `words`; its order_gain must ~ reproduce R60's
    # gain_over_wordunigram (~0.03). This validates the whole serialize+compress path.
    voy_token_order_gain, token_vocab = order_gain_lzma(words, seed + 1)

    # --- Surrogates, re-cut to the real line geometry ---
    markov_char_lines, bow_char_lines = _build_surrogate_lines(
        real_stream, words, line_lengths, seed
    )

    # --- BPE @ K on all three streams + revivals ---
    voy_seg, voy_vocab, voy_merges = learn_bpe(voy_char_lines, k)
    markov_seg, markov_vocab, _ = learn_bpe(markov_char_lines, k)
    bow_seg, bow_vocab, _ = learn_bpe(bow_char_lines, k)

    voy_units = _flatten(voy_seg)
    markov_units = _flatten(markov_seg)
    bow_units = _flatten(bow_seg)

    revival_voy, voy_unit_vocab = order_gain_lzma(voy_units, seed + 10)
    revival_markov, markov_unit_vocab = order_gain_lzma(markov_units, seed + 11)
    revival_bow, bow_unit_vocab = order_gain_lzma(bow_units, seed + 12)

    diff = differential(revival_voy, revival_markov, revival_bow)
    cbmf = cross_boundary_merge_frac(voy_seg, voy_vocab)
    verdict = classify_verdict(revival_voy, revival_markov, revival_bow)

    # --- bz2 ROBUSTNESS CROSS-CHECK (the R60 gate) ---
    # Recompute the SAME unit sequences' order gain under bz2. The lzma-only
    # differential is near-threshold; R60 showed such gains can be lzma artifacts
    # that bz2 kills. The robust verdict requires BOTH compressors.
    revival_voy_bz2, _ = order_gain_bz2(voy_units, seed + 10)
    revival_markov_bz2, _ = order_gain_bz2(markov_units, seed + 11)
    revival_bow_bz2, _ = order_gain_bz2(bow_units, seed + 12)
    diff_bz2 = differential(revival_voy_bz2, revival_markov_bz2, revival_bow_bz2)
    verdict_both = classify_verdict_both(
        (revival_voy, revival_markov, revival_bow),
        (revival_voy_bz2, revival_markov_bz2, revival_bow_bz2),
    )

    # --- optional K-stability sweep (extra-k) ---
    extra_results: dict[int, dict[str, float]] = {}
    extra_ks = [int(x) for x in args.extra_k.split(",") if x.strip()]
    for ek in extra_ks:
        extra_results[ek] = _differential_at_k(
            voy_char_lines, markov_char_lines, bow_char_lines, ek, seed
        )

    # --- per-stream table CSV ---
    def _row(stream_name: str, seg_label: str, units: list[str], n_vocab: int, og: float) -> dict:
        return {
            "stream": stream_name,
            "segmentation": seg_label,
            "n_units": len(units),
            "vocab_size": n_vocab,
            "order_gain_lzma": _r(og),
            "semantic_guardrail": GUARDRAIL,
        }

    table_rows = [
        _row("voynich", "token", words, token_vocab, voy_token_order_gain),
        _row("voynich", f"bpe_k{k}", voy_units, voy_unit_vocab, revival_voy),
        _row("markov2_surrogate", f"bpe_k{k}", markov_units, markov_unit_vocab, revival_markov),
        _row("bagofwords_surrogate", f"bpe_k{k}", bow_units, bow_unit_vocab, revival_bow),
    ]
    write_csv(
        Path(args.out_table),
        table_rows,
        ["stream", "segmentation", "n_units", "vocab_size", "order_gain_lzma", "semantic_guardrail"],
    )

    # --- summary CSV ---
    summary_rows = [
        {"metric": "K", "value": str(k)},
        {"metric": "stream_len", "value": str(len(real_stream))},
        {"metric": "n_lines", "value": str(len(voy_char_lines))},
        {"metric": "voy_token_order_gain", "value": _r(voy_token_order_gain)},
        {
            "metric": "voy_token_order_gain_note",
            "value": (
                "same-sign small-positive analog of R60 gain_over_wordunigram"
                "(0.034); ID-serialization+exact-permutation null isolates pure "
                "token-order, so it runs a few pts higher; both << natural 0.12-0.25"
            ),
        },
        {"metric": "revival_voy", "value": _r(revival_voy)},
        {"metric": "revival_markov", "value": _r(revival_markov)},
        {"metric": "revival_bow", "value": _r(revival_bow)},
        {"metric": "differential", "value": _r(diff)},
        {"metric": "cross_boundary_merge_frac", "value": _r(cbmf)},
        {"metric": "voy_bpe_vocab_size", "value": str(voy_unit_vocab)},
        {"metric": "n_merges_applied", "value": str(len(voy_merges))},
        {"metric": "verdict_lzma_only", "value": verdict},
        {"metric": "revival_voy_bz2", "value": _r(revival_voy_bz2)},
        {"metric": "revival_markov_bz2", "value": _r(revival_markov_bz2)},
        {"metric": "revival_bow_bz2", "value": _r(revival_bow_bz2)},
        {"metric": "differential_bz2", "value": _r(diff_bz2)},
        {"metric": "verdict", "value": verdict_both},
    ]
    for ek in extra_ks:
        r = extra_results[ek]
        summary_rows.append({"metric": f"differential_k{ek}", "value": _r(r["differential"])})
        summary_rows.append({"metric": f"revival_voy_k{ek}", "value": _r(r["revival_voy"])})
    summary_rows.append({"metric": "guardrail", "value": GUARDRAIL})
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    # --- console report ---
    print(f"K={k} stream_len={len(real_stream)} n_lines={len(voy_char_lines)}")
    print(f"voy_token_order_gain={voy_token_order_gain:.4f} (sanity vs R60 ~0.03)")
    print(
        f"revival_voy(BPE)={revival_voy:.4f}  "
        f"revival_markov={revival_markov:.4f}  revival_bow={revival_bow:.4f}"
    )
    print(
        f"DIFFERENTIAL lzma (voy - max surrogate)={diff:.4f}  "
        f"cross_boundary_merge_frac={cbmf:.4f}"
    )
    print(
        f"bz2 cross-check: revival_voy={revival_voy_bz2:.4f} "
        f"markov={revival_markov_bz2:.4f} bow={revival_bow_bz2:.4f} "
        f"DIFFERENTIAL bz2={diff_bz2:.4f}"
    )
    for ek in extra_ks:
        r = extra_results[ek]
        print(
            f"  [K={ek}] revival_voy={r['revival_voy']:.4f} "
            f"differential={r['differential']:.4f}"
        )
    print(f"VERDICT(lzma-only)={verdict}  VERDICT(both-compressors)={verdict_both}")
    print(
        "caveat: BPE is heuristic & K-dependent; the DIFFERENTIAL (real - "
        "structure-matched null) is K-robust to first order. NOT a decipherment."
    )
    print(f"table_csv={args.out_table}")
    print(f"summary_csv={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
