#!/usr/bin/env python3
"""Rota 60: compression ladder — does word ORDER carry information, or texture?

THE decisive final test of the "what is Voynichese" arc. Rotas 43-59 settled:
the token is 100% functional; word-level content is weak & prose-register;
text<->image are decoupled; it is NOT natural-language prose; and (R59) it is
*morphologically rich but syntactically thin* — character mutual information
I(d) collapses to the noise floor by d~=15 (= the token scale), with NO
mid-range (d~=20-100) dependency that natural-language prose carries; the only
long-range tail is a weak cross-line topic clustering.

R59 left ONE question open: is the structure that exists INFORMATION or just
TEXTURE? Concretely — does the ORDER of words carry compressible information
(= syntax -> encoded language) or not (= bag-of-words -> texture -> generator)?

METHOD — a COMPRESSION LADDER. A general-purpose compressor (lzma / bz2)
captures redundancy at all scales; comparing the real corpus to a sequence of
null models that preserve progressively MORE structure localizes WHERE the
corpus's compressibility (its information) actually lives.

We build the real space-joined CHARACTER stream (identical to Rota 58/59,
len 228177) and the ordered WORD sequence, then synthesize four control streams,
each of the SAME character length as the real stream (seeded for reproducibility):

  1. order0          — i.i.d. resample of characters from the real char-unigram
                       distribution. Destroys everything but char frequency.
                       Expected to compress near h1 ~= 3.87 bits/char.
  2. markov2_char    — sample P(c_i | c_{i-2}, c_{i-1}) estimated from the real
                       stream (restart from a random real trigram-context on a
                       dead end). Same char-trigram statistics, NO higher
                       structure. Expected ~ h2 ~= 2.15 bits/char.
  3. word_unigram    — THE KEY NULL (bag-of-words). Draw whole REAL words i.i.d.
                       from the real word-frequency distribution and join with
                       spaces until the char-length matches the real stream, then
                       truncate. Preserves word identities + word frequencies +
                       word-internal structure; DESTROYS word ORDER.
  4. word_bigram     — generate the word SEQUENCE from a word-bigram model, then
                       join with spaces. Captures only adjacent word-order.

Each stream is compressed with BOTH lzma and bz2. We report the compressed size
in bits and in bits/char = compressed_bytes*8 / stream_len. Because every stream
has the SAME length, bits/char is a fair, size-independent comparison.

KEY COMPARISONS (on lzma; bz2 reported as a robustness check):
  gain_over_markov2      = (bpc_markov2 - bpc_real) / bpc_markov2
      -> total structure beyond char-trigrams (word identity + order + repetition)
  gain_over_wordunigram  = (bpc_wordunigram - bpc_real) / bpc_wordunigram
      -> THE DECISIVE NUMBER: word-ORDER information specifically (real vs its
         own bag-of-words twin).
  The markov2 -> wordunigram gap is the word-IDENTITY contribution.

VERDICT (encode):
  gain_over_wordunigram < 0.03  -> "texture_bag_of_words": word ORDER carries
      little/no compressible information; confirms syntactically-thin (R59);
      consistent with a constructed/generator system, NOT sentence-level language.
  gain_over_wordunigram >= 0.03 -> "word_order_informative": there IS exploitable
      word-order / syntactic redundancy; encoded-real-language stays alive.

CAVEAT (reported in the output): compressed bits/char is an UPPER bound on the
true entropy rate (a real compressor is not optimal), but a same-length,
same-compressor comparison between the real stream and a null is FAIR — the
non-optimality applies equally to both. This is NOT a decipherment: it measures
compressibility, not meaning. Guardrail in every output CSV.
"""
from __future__ import annotations

import argparse
import bz2
import collections
import csv
import lzma
import math
import random
from pathlib import Path

from scripts.analyze_language_signature import SPACE, _char_stream, parse_loci

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota60_compressibility_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"

# Decision threshold on gain_over_wordunigram (word-order information share).
ORDER_INFO_THRESHOLD = 0.03


# --------------------------------------------------------------------------- #
# Stream construction                                                         #
# --------------------------------------------------------------------------- #
def word_sequence(lines: list[list[str]]) -> list[str]:
    """Ordered list of clean tokens in reading order (lines concatenated).

    This is the exact word sequence whose space-join is the real character
    stream (`_char_stream`), so `len(SPACE.join(word_sequence(lines)))` equals
    the real `stream_len`. Word order is preserved; this sequence is the object
    whose ORDER the bag-of-words null destroys.
    """
    return [t for line in lines for t in line]


def stream_from_words(words: list[str]) -> str:
    """Space-join a word sequence into the character stream (str form)."""
    return SPACE.join(words)


# --------------------------------------------------------------------------- #
# Null-model generators (all seeded for reproducibility)                      #
# --------------------------------------------------------------------------- #
def gen_order0(real_stream: str, target_len: int, seed: int) -> str:
    """i.i.d. characters resampled from the real char-unigram distribution.

    Destroys all structure above single-character frequency. Generated to exactly
    `target_len` characters. Expected to compress near h1 (the unigram entropy).
    """
    rng = random.Random(seed)
    uni = collections.Counter(real_stream)
    chars = list(uni.keys())
    weights = list(uni.values())
    # random.choices is i.i.d. weighted sampling with replacement
    return "".join(rng.choices(chars, weights=weights, k=target_len))


def _build_trigram_model(
    stream: str,
) -> tuple[dict[tuple[str, str], tuple[list[str], list[int]]], list[tuple[str, str]]]:
    """P(c | c_{-2}, c_{-1}) as a context -> (symbols, weights) table.

    Also returns the list of all observed (c_{-2}, c_{-1}) contexts (with
    multiplicity) so a generator can restart from a real context on a dead end
    (every context here has >=1 continuation, but a freshly-picked context is
    used to reseed after we deliberately reset).
    """
    model: dict[tuple[str, str], collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    contexts: list[tuple[str, str]] = []
    for a, b, c in zip(stream, stream[1:], stream[2:]):
        model[(a, b)][c] += 1
        contexts.append((a, b))
    compiled: dict[tuple[str, str], tuple[list[str], list[int]]] = {}
    for ctx, counter in model.items():
        syms = list(counter.keys())
        wts = list(counter.values())
        compiled[ctx] = (syms, wts)
    return compiled, contexts


def gen_markov2_char(real_stream: str, target_len: int, seed: int) -> str:
    """Generate from the order-2 (trigram) character model of the real stream.

    Samples c_i ~ P(c_i | c_{i-2}, c_{i-1}). On a context with no continuation
    (a dead end — possible only at the true final bigram), restart from a random
    real trigram context. Preserves the exact char-trigram statistics and NO
    higher structure. Expected to compress near h2 (the conditional entropy).
    """
    rng = random.Random(seed)
    model, contexts = _build_trigram_model(real_stream)
    if target_len <= 0 or not contexts:
        return real_stream[:target_len]

    # Seed the first two characters from a randomly chosen real context.
    a, b = rng.choice(contexts)
    out: list[str] = [a, b]
    while len(out) < target_len:
        ctx = (out[-2], out[-1])
        entry = model.get(ctx)
        if entry is None:
            # dead end: restart from a random real context (rare; keeps stats)
            a, b = rng.choice(contexts)
            out.append(a)
            if len(out) < target_len:
                out.append(b)
            continue
        syms, wts = entry
        nxt = rng.choices(syms, weights=wts, k=1)[0]
        out.append(nxt)
    return "".join(out[:target_len])


def gen_word_unigram(words: list[str], target_len: int, seed: int) -> str:
    """BAG-OF-WORDS null: i.i.d. whole REAL words from the word-freq distribution.

    Draws whole tokens (with replacement) from the real word-frequency
    distribution, joins them with single spaces until the joined length reaches
    `target_len`, then truncates to exactly `target_len`. Preserves word
    identities, word frequencies, and word-internal structure; DESTROYS word
    ORDER. This is the decisive null: real vs its own bag-of-words twin.
    """
    rng = random.Random(seed)
    uni = collections.Counter(words)
    vocab = list(uni.keys())
    weights = list(uni.values())
    parts: list[str] = []
    length = 0
    # +1 per join accounts for the separating space (no leading space).
    while length < target_len:
        w = rng.choices(vocab, weights=weights, k=1)[0]
        add = len(w) + (1 if parts else 0)
        parts.append(w)
        length += add
    return SPACE.join(parts)[:target_len]


def gen_word_bigram(words: list[str], target_len: int, seed: int) -> str:
    """Generate a word SEQUENCE from a word-bigram model, then space-join.

    Samples w_i ~ P(w_i | w_{i-1}) estimated from the real ordered word sequence
    (restart from a random real word on a dead end), joins with single spaces
    until the joined length reaches `target_len`, then truncates. Captures only
    ADJACENT word-order redundancy (the weakest order signal).
    """
    rng = random.Random(seed)
    if not words:
        return ""
    model: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for a, b in zip(words, words[1:]):
        model[a][b] += 1
    compiled: dict[str, tuple[list[str], list[int]]] = {
        w: (list(c.keys()), list(c.values())) for w, c in model.items()
    }
    vocab = list(collections.Counter(words).keys())

    cur = rng.choice(words)
    parts: list[str] = [cur]
    length = len(cur)
    while length < target_len:
        entry = compiled.get(cur)
        if entry is None:
            cur = rng.choice(vocab)
        else:
            syms, wts = entry
            cur = rng.choices(syms, weights=wts, k=1)[0]
        parts.append(cur)
        length += len(cur) + 1  # +1 for the separating space
    return SPACE.join(parts)[:target_len]


# --------------------------------------------------------------------------- #
# Compression                                                                 #
# --------------------------------------------------------------------------- #
def compress_size_bits(text: str, compressor: str) -> int:
    """Compressed size in BITS of `text` under `compressor` ('lzma' or 'bz2').

    Encodes the stream as UTF-8 (the EVA alphabet + space is pure ASCII, so this
    is one byte per char) and compresses at maximum preset. Returns the byte
    length times 8.
    """
    data = text.encode("utf-8")
    if compressor == "lzma":
        comp = lzma.compress(data, preset=9 | lzma.PRESET_EXTREME)
    elif compressor == "bz2":
        comp = bz2.compress(data, compresslevel=9)
    else:  # pragma: no cover - guarded by caller
        raise ValueError(f"unknown compressor: {compressor!r}")
    return len(comp) * 8


def bits_per_char(compressed_bits: int, stream_len: int) -> float:
    """compressed bits divided by stream length (size-independent rate)."""
    return compressed_bits / stream_len if stream_len > 0 else 0.0


def gain(bpc_null: float, bpc_real: float) -> float:
    """Relative compressibility gain of real over a null: (null - real)/null.

    Positive when the real stream compresses to FEWER bits/char than the null
    (i.e. it carries redundancy the null lacks). 0 when they tie; can be slightly
    negative if the null compresses better (real has no extra exploitable order).
    """
    if bpc_null <= 0:
        return 0.0
    return (bpc_null - bpc_real) / bpc_null


# --------------------------------------------------------------------------- #
# Verdict                                                                     #
# --------------------------------------------------------------------------- #
def classify_verdict(gain_over_wordunigram: float) -> str:
    """Decisive verdict from the word-order information share (lzma).

    gain_over_wordunigram < 0.03 -> 'texture_bag_of_words' (word order carries
    little/no compressible information; syntactically thin; generator-consistent).
    Otherwise -> 'word_order_informative' (exploitable word-order redundancy;
    encoded-real-language stays alive).
    """
    if gain_over_wordunigram < ORDER_INFO_THRESHOLD:
        return "texture_bag_of_words"
    return "word_order_informative"


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
    p.add_argument("--seed", type=int, default=0)
    p.add_argument(
        "--no-word-bigram",
        action="store_true",
        help="skip the optional word_bigram model",
    )
    d = ROOT / "data" / "derived"
    p.add_argument("--out-table", default=str(d / "compressibility_zl3b.csv"))
    p.add_argument("--out-summary", default=str(d / "compressibility_summary_zl3b.csv"))
    return p.parse_args(argv)


def build_streams(
    lines: list[list[str]], seed: int, with_word_bigram: bool
) -> tuple[dict[str, str], int]:
    """Build the real stream and all (seeded) synthetic streams, each == real len.

    Returns (model_name -> stream, stream_len). Distinct seed offsets per model
    keep the generators independent yet reproducible.
    """
    words = word_sequence(lines)
    real = stream_from_words(words)
    n = len(real)
    streams: dict[str, str] = {
        "real": real,
        "order0": gen_order0(real, n, seed + 1),
        "markov2_char": gen_markov2_char(real, n, seed + 2),
        "word_unigram": gen_word_unigram(words, n, seed + 3),
    }
    if with_word_bigram:
        streams["word_bigram"] = gen_word_bigram(words, n, seed + 4)
    return streams, n


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    lines = parse_loci(Path(args.corpus))
    with_word_bigram = not args.no_word_bigram
    streams, stream_len = build_streams(lines, args.seed, with_word_bigram)

    compressors = ("lzma", "bz2")
    # model order is fixed so the table is stable/readable
    model_order = ["real", "order0", "markov2_char", "word_unigram"]
    if with_word_bigram:
        model_order.append("word_bigram")

    # bpc[model][compressor] = bits/char
    bits: dict[str, dict[str, int]] = collections.defaultdict(dict)
    bpc: dict[str, dict[str, float]] = collections.defaultdict(dict)
    table_rows: list[dict] = []
    for model in model_order:
        text = streams[model]
        for comp in compressors:
            cb = compress_size_bits(text, comp)
            rate = bits_per_char(cb, stream_len)
            bits[model][comp] = cb
            bpc[model][comp] = rate
            table_rows.append(
                {
                    "model": model,
                    "compressor": comp,
                    "compressed_bits": cb,
                    "bits_per_char": round(rate, 6),
                    "semantic_guardrail": GUARDRAIL,
                }
            )

    # --- key comparisons (lzma is the headline; bz2 for robustness) ---
    gain_markov2_lzma = gain(bpc["markov2_char"]["lzma"], bpc["real"]["lzma"])
    gain_worduni_lzma = gain(bpc["word_unigram"]["lzma"], bpc["real"]["lzma"])
    gain_worduni_bz2 = gain(bpc["word_unigram"]["bz2"], bpc["real"]["bz2"])

    verdict = classify_verdict(gain_worduni_lzma)

    # --- table CSV ---
    write_csv(
        Path(args.out_table),
        table_rows,
        ["model", "compressor", "compressed_bits", "bits_per_char", "semantic_guardrail"],
    )

    # --- summary CSV ---
    def _r(x: float, nd: int = 6) -> str:
        return str(round(x, nd))

    summary_rows = [
        {"metric": "stream_len", "value": str(stream_len)},
        {"metric": "bpc_real_lzma", "value": _r(bpc["real"]["lzma"])},
        {"metric": "bpc_order0_lzma", "value": _r(bpc["order0"]["lzma"])},
        {"metric": "bpc_markov2_lzma", "value": _r(bpc["markov2_char"]["lzma"])},
        {"metric": "bpc_wordunigram_lzma", "value": _r(bpc["word_unigram"]["lzma"])},
        {"metric": "gain_over_markov2", "value": _r(gain_markov2_lzma)},
        {"metric": "gain_over_wordunigram", "value": _r(gain_worduni_lzma)},
        {"metric": "bpc_real_bz2", "value": _r(bpc["real"]["bz2"])},
        {"metric": "bpc_order0_bz2", "value": _r(bpc["order0"]["bz2"])},
        {"metric": "bpc_markov2_bz2", "value": _r(bpc["markov2_char"]["bz2"])},
        {"metric": "bpc_wordunigram_bz2", "value": _r(bpc["word_unigram"]["bz2"])},
        {"metric": "gain_over_wordunigram_bz2", "value": _r(gain_worduni_bz2)},
    ]
    if with_word_bigram:
        gain_wordbi_lzma = gain(bpc["word_bigram"]["lzma"], bpc["real"]["lzma"])
        summary_rows.append(
            {"metric": "bpc_wordbigram_lzma", "value": _r(bpc["word_bigram"]["lzma"])}
        )
        summary_rows.append(
            {"metric": "gain_over_wordbigram", "value": _r(gain_wordbi_lzma)}
        )
    summary_rows.append({"metric": "verdict", "value": verdict})
    summary_rows.append({"metric": "guardrail", "value": GUARDRAIL})
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    # --- console report ---
    print(f"stream_len={stream_len}")
    for model in model_order:
        print(
            f"{model:14s} lzma_bpc={bpc[model]['lzma']:.4f} "
            f"bz2_bpc={bpc[model]['bz2']:.4f}"
        )
    print(f"gain_over_markov2(lzma)={gain_markov2_lzma:.4f}")
    print(
        f"gain_over_wordunigram(lzma)={gain_worduni_lzma:.4f} "
        f"(bz2={gain_worduni_bz2:.4f})  <-- DECISIVE"
    )
    print(f"VERDICT={verdict}")
    print(
        "caveat: bits/char is an UPPER bound on entropy rate; same-length "
        "same-compressor comparison is fair."
    )
    print(f"table_csv={args.out_table}")
    print(f"summary_csv={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
