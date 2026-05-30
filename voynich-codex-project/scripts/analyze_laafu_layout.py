#!/usr/bin/env python3
"""Rota 67: is the corpus's `laafu_I` residual a SPARSE content-free LAYOUT rule,
or does it carry topic-conditioned CONTENT?

CONTEXT. R62 (the content-free generator capstone) reproduced 13/14 measured
signatures of Voynichese with a simple LOCAL contentless process. The ONLY
signature its `line_edge_bias` mechanism could not reach was LAAFU:
`laafu_I = mutual_information(laafu_pairs(lines))` (I(word ; position-bucket),
buckets {first, medial, last}). The real value is **0.471 bits**; the R62
generator reached only **0.303** (the baseline this route compares against; the
gap is 0.168 bits). The cryptanalyst pre-registered this residual as
DEGENERATE-LIKELY (≈82% layout): the excess is probably carried by the
manuscript's CALLIGRAPHIC HEAD habits (line-initial gallows littera notabilior,
line-final justification glyphs) rather than by topic-conditioned syntax.

This route decides between two readings with four pre-registered analyses plus a
debiased estimator, and emits a verdict that is a PURE FUNCTION of the measured
booleans.

THE FOUR DECISIVE ANALYSES (cryptanalyst pre-registration)
  1. Paleographic-head subtraction (THE decisive control). HEAD tokens = first
     glyph ∈ {p,t} (line-initial gallows littera notabilior) OR last glyph ∈
     {m,g} OR endswith "dy" (line-final justification habit). Recompute laafu_I
     with HEAD token IDENTITIES collapsed to a single placeholder (position
     preserved) → `laafu_I_headless`. If headless ≈ 0.303 (the R62 baseline) the
     0.168 excess was the calligraphic head → LAYOUT. Reports `head_gap_explained
     _frac = (0.471 - headless)/(0.471 - 0.303)`.
  2. Sparse-closure curve. Per-token MI contribution
     c(t) = Σ_bucket P(t,bucket)·log2(P(bucket|t)/P(bucket)); rank desc; cumulative
     fraction of total laafu_I vs k. Reports k50/k70/k90. Small k (k70 ≤ ~40) =
     SPARSE = layout.
  3. Section-invariance of edge tokens. For line-FIRST and line-LAST tokens, per
     content section, take top-k by positional lift; cross-section Jaccard
     overlap of those sets, AND Jensen–Shannon divergence of the line-final token
     distribution across sections vs a within-folio line-position permutation null
     (≥500 perms). High overlap (≥0.6) + JS within the null band (p>0.05) =
     universal habit = LAYOUT; section-specific edge tokens beyond the null
     (p<0.01) = CONTENT.
  4. Within-Currier (mandatory; never pool). laafu_I within Currier A lines and
     within Currier B lines SEPARATELY. Pooling A/B manufactures token↔position MI
     from their vocabulary shift (a confounder). Reports `laafu_I_A`, `laafu_I_B`.
  Plus a Miller–Madow-corrected laafu_I (each entropy H corrected by
  +(K_obs-1)/(2N·ln2) bits) alongside the plug-in value, to confirm 0.471 is not
  pure finite-sample inflation and the gap vs 0.303 survives.

VERDICT (pure function of the measured booleans)
  `laafu_is_layout`  iff head-subtraction residual ≈ 0.303 (head explains ≥~70% of
     the gap) AND sparse closure (k70 ≤ ~40) AND section-invariance (overlap ≥0.6,
     JS p>0.05). Degenerate → the R62 generator becomes effectively SUFFICIENT
     14/14, strengthening "meaning is not necessary".
  `laafu_carries_content` iff the residual-above-head is section-specific beyond
     the null (overlap < 0.6 AND JS p < 0.01) — an ACTIONABLE genuine crack.
  `laafu_mixed` otherwise (the evidence splits).

GOLDEN RULE. Even `laafu_carries_content` means "the position binding is
topic-conditioned", NEVER a translation. `laafu_is_layout` means the residual is a
RICHER CONTENT-FREE LAYOUT rule (not syntax), NOT a decipherment. Guardrail in
every output row.
"""
from __future__ import annotations

import argparse
import collections
import csv
import math
import random
import re
from pathlib import Path

from scripts.analyze_generator import parse_loci_with_section
from scripts.analyze_language_signature import (
    _position_bucket,
    laafu_pairs,
    mutual_information,
    shannon_entropy,
)
from scripts.analyze_nucleus import classify_section, clean_token

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota67_laafu_layout_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"

# The R62 line_edge_bias generator's best laafu_I (the baseline; see analyze_generator
# ablation "full" row). The 0.471-vs-0.303 gap of 0.168 bits is what this route
# attributes to either the calligraphic HEAD (layout) or to topic (content).
R62_BASELINE = 0.303
LAAFU_REAL_REF = 0.471

# Paleographic HEAD habits (R66/cryptanalyst pre-registration):
#   - line-initial gallows littera notabilior: first glyph p or t
#   - line-final justification glyphs: last glyph m or g
#   - line-final "-dy" justification habit: token endswith "dy"
HEAD_FIRST_GLYPHS = ("p", "t")
HEAD_LAST_GLYPHS = ("m", "g")
HEAD_SUFFIX = "dy"
HEAD_PLACEHOLDER = "\x00HEAD"  # collapsed identity for every HEAD token

# Verdict thresholds (cryptanalyst pre-registration).
HEAD_GAP_LAYOUT_THRESH = 0.70  # head explains >=70% of the 0.168 gap -> layout
CLOSURE_K70_LAYOUT_THRESH = 40  # k70 <= 40 reaching 70% of laafu_I -> sparse/layout
SECTION_OVERLAP_LAYOUT_THRESH = 0.60  # cross-section Jaccard >= 0.6 -> universal
SECTION_JS_P_LAYOUT_THRESH = 0.05  # JS within null band (p>0.05) -> universal
SECTION_JS_P_CONTENT_THRESH = 0.01  # JS beyond null (p<0.01) -> section-specific

# Sections kept for the section-invariance analysis (content sections; "other"
# and sparse sections are dropped so the overlap is between real content topics).
SECTION_EDGE_TOPK = 15
SECTION_MIN_LINES = 30
N_SECTION_PERMS = 500

# The IVTFF folio header carries the Currier language tag $L=A/B (see
# analyze_nucleus.parse_corpus / analyze_section_scribe). Reuse that mechanism.
_HDR = re.compile(r"^<(f[0-9]+[rv]\d?)>")
_LOC = re.compile(r"^<(f[0-9]+[rv]\d?)\.\d+[^>]*>\s*(.*)$")
_LANG = re.compile(r"\$L=([A-Z?])")


# --------------------------------------------------------------------------- #
# Corpus parse with per-line section + Currier + folio                        #
# --------------------------------------------------------------------------- #
def parse_loci_with_section_currier(
    path: Path,
) -> tuple[list[list[str]], list[str], list[str], list[str]]:
    """Return (lines, sections, curriers, folios), all index-aligned.

    `lines` and `sections` reproduce analyze_generator.parse_loci_with_section
    EXACTLY (same tokenization, same line set, so laafu_I matches R62). In
    addition each line gets its Currier language (read from the folio's `$L=`
    header tag, the same mechanism as analyze_nucleus.parse_corpus) and its raw
    folio id (for the within-folio permutation null in analysis 3).
    """
    folio_currier: dict[str, str] = {}
    lines: list[list[str]] = []
    sections: list[str] = []
    curriers: list[str] = []
    folios: list[str] = []
    cur_folio = "?"
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        mh = _HDR.match(raw_line)
        if mh:
            cur_folio = mh.group(1)
            ml = _LANG.search(raw_line)
            folio_currier[cur_folio] = ml.group(1) if ml else "?"
            continue
        m = _LOC.match(raw_line)
        if not m:
            continue
        folio = m.group(1)
        body = m.group(2).replace(",", ".")
        toks = [t for t in (clean_token(r) for r in body.split(".")) if t]
        if toks:
            lines.append(toks)
            sections.append(classify_section(folio))
            curriers.append(folio_currier.get(folio, "?"))
            folios.append(folio)
    return lines, sections, curriers, folios


# --------------------------------------------------------------------------- #
# Analysis 1: paleographic-head subtraction                                   #
# --------------------------------------------------------------------------- #
def is_head_token(token: str) -> bool:
    """True if a token is a calligraphic HEAD per the pre-registered definition.

    HEAD = first glyph in {p,t} (line-initial gallows littera notabilior) OR last
    glyph in {m,g} OR endswith "dy" (line-final justification habit). These are
    surface calligraphic habits, not lexical content; collapsing their IDENTITY
    (analysis 1) removes the head's contribution to laafu_I while keeping its
    position.
    """
    if not token:
        return False
    if token[0] in HEAD_FIRST_GLYPHS:
        return True
    if token[-1] in HEAD_LAST_GLYPHS:
        return True
    if token.endswith(HEAD_SUFFIX):
        return True
    return False


def collapse_head_identities(lines: list[list[str]]) -> list[list[str]]:
    """Map every HEAD token to a single placeholder symbol, keeping its position.

    Non-HEAD tokens are untouched. This is the headless corpus on which
    `laafu_I_headless` is measured: if the 0.168 excess over the R62 baseline was
    carried by head IDENTITY, collapsing all heads to one symbol drops laafu_I to
    ~the baseline (the head no longer distinguishes positions by word identity).
    """
    return [
        [HEAD_PLACEHOLDER if is_head_token(t) else t for t in line] for line in lines
    ]


def laafu_I_of(lines: list[list[str]]) -> float:
    """laafu_I = mutual_information(laafu_pairs(lines)) — the R62 estimator verbatim."""
    return mutual_information(laafu_pairs(lines))


# --------------------------------------------------------------------------- #
# Debiased estimator: Miller–Madow                                            #
# --------------------------------------------------------------------------- #
def _miller_madow_entropy(counter: collections.Counter) -> float:
    """Miller–Madow bias-corrected Shannon entropy in bits.

    H_MM = H_plugin + (K_obs - 1) / (2 N ln 2), where K_obs is the number of
    observed outcomes and N the sample size. The correction RAISES each entropy by
    a small finite-sample term; applied to H(X)+H(Y)-H(X,Y) the joint correction
    (largest support) dominates, so the corrected MI is BELOW the plug-in MI.
    """
    n = sum(counter.values())
    if n == 0:
        return 0.0
    h = shannon_entropy(counter)
    k = sum(1 for c in counter.values() if c > 0)
    return h + (k - 1) / (2.0 * n * math.log(2.0))


def laafu_I_miller_madow(pairs: list[tuple[str, str]]) -> float:
    """Miller–Madow-corrected I(word;position) in bits.

    I_MM = H_MM(X) + H_MM(Y) - H_MM(X,Y). The joint table has the largest support
    (K_obs), so its +correction is the biggest term and I_MM <= I_plugin: it
    confirms 0.471 is not pure finite-sample inflation if the corrected value
    still clears the R62 baseline.
    """
    if not pairs:
        return 0.0
    xs = collections.Counter(x for x, _ in pairs)
    ys = collections.Counter(y for _, y in pairs)
    joint = collections.Counter(pairs)
    return (
        _miller_madow_entropy(xs)
        + _miller_madow_entropy(ys)
        - _miller_madow_entropy(joint)
    )


# --------------------------------------------------------------------------- #
# Analysis 2: sparse-closure curve                                            #
# --------------------------------------------------------------------------- #
def token_mi_contributions(pairs: list[tuple[str, str]]) -> list[tuple[str, float]]:
    """Per-token MI contribution to laafu_I, sorted by contribution descending.

    c(t) = Σ_bucket P(t, bucket) · log2( P(bucket|t) / P(bucket) ). Summed over all
    tokens this equals laafu_I exactly (the standard token-wise decomposition of
    mutual information). A few high-c tokens accounting for most of laafu_I means
    the binding is SPARSE (a handful of edge habits), the layout signature.
    """
    if not pairs:
        return []
    n = len(pairs)
    joint = collections.Counter(pairs)
    xs = collections.Counter(x for x, _ in pairs)
    ys = collections.Counter(y for _, y in pairs)
    contrib: dict[str, float] = collections.defaultdict(float)
    for (tok, bucket), c in joint.items():
        p_tb = c / n
        p_t = xs[tok] / n
        p_b = ys[bucket] / n
        if p_tb > 0 and p_t > 0 and p_b > 0:
            contrib[tok] += p_tb * math.log2(p_tb / (p_t * p_b))
    # rank by contribution desc; tie-break by token for determinism
    return sorted(contrib.items(), key=lambda kv: (-kv[1], kv[0]))


def closure_curve(
    contributions: list[tuple[str, float]],
) -> tuple[list[tuple[int, float, float]], float]:
    """Cumulative closure curve and the (clamped) total laafu_I.

    Returns ([(k, cumulative_contrib, cumulative_fraction), ...], total). The total
    is Σ c(t) = laafu_I. The cumulative fraction is monotone non-decreasing in k.
    NOTE: individual c(t) can be negative (a token that anti-aligns with a
    position), so cumulative_contrib (and hence the fraction) is monotone ONLY
    because the list is sorted descending — it is guaranteed non-decreasing here.
    """
    total = sum(c for _, c in contributions)
    rows: list[tuple[int, float, float]] = []
    run = 0.0
    for k, (_tok, c) in enumerate(contributions, start=1):
        run += c
        frac = (run / total) if total != 0 else 0.0
        rows.append((k, run, frac))
    return rows, total


def closure_k_at(rows: list[tuple[int, float, float]], target_frac: float) -> int:
    """Smallest k whose cumulative fraction first reaches target_frac.

    Because the curve is built from a descending sort it is monotone
    non-decreasing, so the first crossing is well-defined; if it never reaches the
    target (degenerate), returns the full length.
    """
    for k, _run, frac in rows:
        if frac >= target_frac:
            return k
    return rows[-1][0] if rows else 0


# --------------------------------------------------------------------------- #
# Analysis 3: section-invariance of edge tokens                               #
# --------------------------------------------------------------------------- #
def edge_tokens_by_section(
    lines: list[list[str]], sections: list[str], position: str
) -> dict[str, collections.Counter]:
    """Counter of line-edge tokens per section for position in {"first","last"}.

    Only lines with >=3 tokens contribute an edge token (the edge is then
    unambiguous, matching the laafu_pairs framing). Returns {section -> Counter of
    edge token -> count}.
    """
    by_sec: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for line, sec in zip(lines, sections):
        if len(line) < 3:
            continue
        tok = line[0] if position == "first" else line[-1]
        by_sec[sec][tok] += 1
    return by_sec


def top_lift_tokens(
    section_counts: collections.Counter,
    global_counts: collections.Counter,
    top_k: int,
    min_count: int = 3,
) -> set[str]:
    """Top-k tokens by positional LIFT (section edge-frac / global edge-frac).

    Lift > 1 means a token is over-represented at this edge in this section vs the
    whole corpus. A frequency FLOOR (min_count occurrences in the section) is
    essential: without it the ranking is swamped by hapaxes — a token seen ONCE in
    one section has infinite lift but carries no layout signal — which would force
    cross-section overlap to a spurious 0. With the floor the set is the section's
    genuinely RECURRENT over-represented edge tokens; high cross-section overlap of
    those is the universal-habit (layout) signature, low overlap is section-
    specific (content). Ranking by lift (not raw count) so a token common
    everywhere does not crowd out section-specific ones.
    """
    n_sec = sum(section_counts.values())
    n_glob = sum(global_counts.values())
    if n_sec == 0 or n_glob == 0:
        return set()
    lifts: list[tuple[str, float, int]] = []
    for tok, c in section_counts.items():
        if c < min_count:
            continue
        sec_frac = c / n_sec
        glob_frac = global_counts.get(tok, 0) / n_glob
        lift = sec_frac / glob_frac if glob_frac > 0 else float("inf")
        lifts.append((tok, lift, c))
    # rank by lift desc; tie-break by raw count desc then token for determinism
    lifts.sort(
        key=lambda kv: (
            kv[1] if math.isfinite(kv[1]) else 1e18,
            kv[2],
            kv[0],
        ),
        reverse=True,
    )
    return {tok for tok, _lift, _c in lifts[:top_k]}


def jaccard(a: set[str], b: set[str]) -> float:
    """Jaccard overlap |A∩B| / |A∪B|; empty∪empty -> 0.0."""
    if not a and not b:
        return 0.0
    return len(a & b) / len(a | b)


def _js_divergence(p: dict[str, float], q: dict[str, float]) -> float:
    """Jensen–Shannon divergence (bits) between two discrete distributions."""
    keys = set(p) | set(q)
    m = {k: 0.5 * (p.get(k, 0.0) + q.get(k, 0.0)) for k in keys}

    def _kl(a: dict[str, float]) -> float:
        s = 0.0
        for k in keys:
            ak = a.get(k, 0.0)
            mk = m.get(k, 0.0)
            if ak > 0 and mk > 0:
                s += ak * math.log2(ak / mk)
        return s

    return 0.5 * _kl(p) + 0.5 * _kl(q)


def _normalize(counter: collections.Counter) -> dict[str, float]:
    n = sum(counter.values())
    return {k: c / n for k, c in counter.items()} if n else {}


def mean_pairwise_js(
    section_finals: dict[str, collections.Counter],
) -> float:
    """Mean pairwise JS divergence of the line-final token distribution across sections."""
    secs = sorted(section_finals)
    dists = {s: _normalize(section_finals[s]) for s in secs}
    vals: list[float] = []
    for i in range(len(secs)):
        for j in range(i + 1, len(secs)):
            vals.append(_js_divergence(dists[secs[i]], dists[secs[j]]))
    return sum(vals) / len(vals) if vals else 0.0


def section_invariance(
    lines: list[list[str]],
    sections: list[str],
    folios: list[str],
    *,
    top_k: int,
    min_lines: int,
    n_perm: int,
    seed: int,
) -> dict:
    """Cross-section Jaccard overlap + JS-divergence-vs-null for line-edge tokens.

    Kept sections are content sections with >= min_lines (>=3-token) lines.
    OVERLAP: mean pairwise Jaccard of the top-k line-FIRST sets and of the top-k
    line-LAST sets (by positional lift), averaged. High overlap = the same edge
    tokens recur across topics = a universal LAYOUT habit.
    JS NULL: the observed mean pairwise JS of the line-final distribution across
    sections, compared to a within-FOLIO line-position permutation null. The null
    shuffles the position-bucket labels among each folio's tokens, so which token
    lands in "last" position is randomized within the folio while the folio's (and
    hence the section's) vocabulary is exactly preserved. p = fraction of perms
    whose mean JS >= observed (add-one smoothed). JS within the null band (p>0.05)
    = the final-position token bag is no more topic-separated than the section word
    bag already implies = universal/LAYOUT; JS beyond the null (p<0.01) = the
    final-position habit is section-specific beyond vocabulary = CONTENT.
    """
    # which sections qualify (enough >=3-token lines)
    line_counts: collections.Counter = collections.Counter()
    for line, sec in zip(lines, sections):
        if len(line) >= 3:
            line_counts[sec] += 1
    kept = {s for s, c in line_counts.items() if c >= min_lines and s != "other"}

    # restrict everything to kept sections
    k_lines, k_secs, k_folios = [], [], []
    for line, sec, fol in zip(lines, sections, folios):
        if sec in kept and len(line) >= 3:
            k_lines.append(line)
            k_secs.append(sec)
            k_folios.append(fol)

    first_by_sec = edge_tokens_by_section(k_lines, k_secs, "first")
    last_by_sec = edge_tokens_by_section(k_lines, k_secs, "last")
    global_first: collections.Counter = collections.Counter()
    global_last: collections.Counter = collections.Counter()
    for c in first_by_sec.values():
        global_first.update(c)
    for c in last_by_sec.values():
        global_last.update(c)

    secs = sorted(kept)

    def _mean_overlap(by_sec, glob):
        sets = {s: top_lift_tokens(by_sec.get(s, collections.Counter()), glob, top_k) for s in secs}
        vals = []
        for i in range(len(secs)):
            for j in range(i + 1, len(secs)):
                vals.append(jaccard(sets[secs[i]], sets[secs[j]]))
        return (sum(vals) / len(vals) if vals else 0.0), sets

    first_overlap, first_sets = _mean_overlap(first_by_sec, global_first)
    last_overlap, last_sets = _mean_overlap(last_by_sec, global_last)
    mean_overlap = (first_overlap + last_overlap) / 2.0

    # observed JS of the line-final distribution across sections
    js_obs = mean_pairwise_js(last_by_sec)

    # within-folio line-position permutation null. For each folio, gather all
    # (token, position-bucket) slots from its >=3-token lines; the null permutes
    # the BUCKET labels among that folio's slots, so which token sits at "last"
    # is randomized WITHIN the folio. Folio->section is fixed, so each section's
    # vocabulary is exactly preserved; only the position binding is destroyed. We
    # then recompute the line-final (bucket=="last") distribution per section and
    # its mean pairwise JS. If line-final tokens are section-specific BEYOND folio
    # vocabulary, js_obs exceeds the null band (small p). Folio->section map is
    # 1:1 here (folios are single-section), so this is the decisive test of whether
    # the final-position habit, not just the section's word bag, differs by topic.
    folio_section: dict[str, str] = {}
    folio_slots: dict[str, list[tuple[str, str]]] = collections.defaultdict(list)
    for line, sec, fol in zip(k_lines, k_secs, k_folios):
        folio_section[fol] = sec
        n = len(line)
        for i, tok in enumerate(line):
            folio_slots[fol].append((tok, _position_bucket(i, n)))

    rng = random.Random(seed)
    hits = 0
    js_null_total = 0.0
    n_eff = max(1, n_perm)
    folio_items = list(folio_slots.items())
    for _ in range(n_eff):
        perm_by_sec: dict[str, collections.Counter] = collections.defaultdict(
            collections.Counter
        )
        for fol, slots in folio_items:
            sec = folio_section[fol]
            buckets = [b for _t, b in slots]
            rng.shuffle(buckets)
            for (tok, _orig), b in zip(slots, buckets):
                if b == "last":
                    perm_by_sec[sec][tok] += 1
        js_perm = mean_pairwise_js(perm_by_sec)
        js_null_total += js_perm
        if js_perm >= js_obs:
            hits += 1
    js_p = (hits + 1) / (n_eff + 1)
    js_null_mean = js_null_total / n_eff

    return {
        "kept_sections": secs,
        "first_overlap": first_overlap,
        "last_overlap": last_overlap,
        "mean_overlap": mean_overlap,
        "js_obs": js_obs,
        "js_null_mean": js_null_mean,
        "js_p": js_p,
        "first_sets": first_sets,
        "last_sets": last_sets,
        "first_by_sec": first_by_sec,
        "last_by_sec": last_by_sec,
    }


# --------------------------------------------------------------------------- #
# Analysis 4: within-Currier laafu_I (never pool)                             #
# --------------------------------------------------------------------------- #
def laafu_I_within_currier(
    lines: list[list[str]], curriers: list[str], target: str
) -> tuple[float, int]:
    """laafu_I computed on ONLY the lines of one Currier language.

    Pooling A/B inflates I(word;position) via their vocabulary shift (a confounder
    independent of any genuine line-position binding), so each mode is measured in
    isolation. Returns (laafu_I, n_lines_used).
    """
    sub = [line for line, cur in zip(lines, curriers) if cur == target]
    return laafu_I_of(sub), len(sub)


# --------------------------------------------------------------------------- #
# Verdict (pure function of the measured booleans)                            #
# --------------------------------------------------------------------------- #
def classify_verdict(
    *,
    head_gap_explained_frac: float,
    closure_k70: int,
    section_overlap: float,
    section_js_p: float,
) -> tuple[str, dict]:
    """Verdict as a PURE FUNCTION of the four measured booleans (mirrored in tests).

    layout_head   = head explains >= 70% of the 0.168 gap
    layout_sparse = k70 <= 40 (a handful of tokens carry 70% of laafu_I)
    layout_invar  = cross-section overlap >= 0.6 AND JS within the null (p>0.05)
    content_section = section-specific edges: overlap < 0.6 AND JS beyond null (p<0.01)

      laafu_is_layout       iff layout_head AND layout_sparse AND layout_invar
      laafu_carries_content iff content_section (and NOT the full layout verdict)
      laafu_mixed           otherwise
    """
    layout_head = head_gap_explained_frac >= HEAD_GAP_LAYOUT_THRESH
    layout_sparse = closure_k70 <= CLOSURE_K70_LAYOUT_THRESH
    layout_invar = (
        section_overlap >= SECTION_OVERLAP_LAYOUT_THRESH
        and section_js_p > SECTION_JS_P_LAYOUT_THRESH
    )
    content_section = (
        section_overlap < SECTION_OVERLAP_LAYOUT_THRESH
        and section_js_p < SECTION_JS_P_CONTENT_THRESH
    )
    is_layout = layout_head and layout_sparse and layout_invar
    if is_layout:
        verdict = "laafu_is_layout"
    elif content_section:
        verdict = "laafu_carries_content"
    else:
        verdict = "laafu_mixed"
    flags = {
        "layout_head": layout_head,
        "layout_sparse": layout_sparse,
        "layout_invar": layout_invar,
        "content_section": content_section,
    }
    return verdict, flags


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
    p.add_argument("--top-k", type=int, default=SECTION_EDGE_TOPK)
    p.add_argument("--min-lines", type=int, default=SECTION_MIN_LINES)
    p.add_argument("--n-perm", type=int, default=N_SECTION_PERMS)
    d = ROOT / "data" / "derived"
    p.add_argument("--out-closure", default=str(d / "laafu_layout_closure_zl3b.csv"))
    p.add_argument("--out-section", default=str(d / "laafu_layout_section_zl3b.csv"))
    p.add_argument("--out-summary", default=str(d / "laafu_layout_summary_zl3b.csv"))
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    lines, sections, curriers, folios = parse_loci_with_section_currier(
        Path(args.corpus)
    )

    # --- real laafu_I (R62 estimator verbatim) ---
    pairs = laafu_pairs(lines)
    laafu_real = mutual_information(pairs)

    # debiased (Miller–Madow)
    laafu_mm = laafu_I_miller_madow(pairs)

    # --- Analysis 1: paleographic-head subtraction ---
    headless_lines = collapse_head_identities(lines)
    laafu_headless = laafu_I_of(headless_lines)
    gap = LAAFU_REAL_REF - R62_BASELINE  # 0.168 reference gap
    head_gap_explained_frac = (
        (LAAFU_REAL_REF - laafu_headless) / gap if gap != 0 else float("nan")
    )

    # --- Analysis 2: sparse-closure curve ---
    contributions = token_mi_contributions(pairs)
    closure_rows_raw, closure_total = closure_curve(contributions)
    k50 = closure_k_at(closure_rows_raw, 0.50)
    k70 = closure_k_at(closure_rows_raw, 0.70)
    k90 = closure_k_at(closure_rows_raw, 0.90)

    # --- Analysis 3: section-invariance of edge tokens ---
    sec = section_invariance(
        lines,
        sections,
        folios,
        top_k=args.top_k,
        min_lines=args.min_lines,
        n_perm=args.n_perm,
        seed=args.seed,
    )

    # --- Analysis 4: within-Currier laafu_I (never pool) ---
    laafu_A, n_A = laafu_I_within_currier(lines, curriers, "A")
    laafu_B, n_B = laafu_I_within_currier(lines, curriers, "B")

    # --- VERDICT (pure function of the booleans) ---
    verdict, flags = classify_verdict(
        head_gap_explained_frac=head_gap_explained_frac,
        closure_k70=k70,
        section_overlap=sec["mean_overlap"],
        section_js_p=sec["js_p"],
    )

    # ------------------------------------------------------------------ #
    # closure CSV                                                        #
    # ------------------------------------------------------------------ #
    closure_rows = [
        {
            "k": k,
            "token": contributions[k - 1][0]
            if contributions[k - 1][0] != HEAD_PLACEHOLDER
            else "<HEAD>",
            "token_contrib_bits": _r(contributions[k - 1][1], 8),
            "cumulative_bits": _r(run, 8),
            "cumulative_frac": _r(frac, 6),
            "semantic_guardrail": GUARDRAIL,
        }
        for (k, run, frac) in closure_rows_raw
    ]
    write_csv(
        Path(args.out_closure),
        closure_rows,
        [
            "k",
            "token",
            "token_contrib_bits",
            "cumulative_bits",
            "cumulative_frac",
            "semantic_guardrail",
        ],
    )

    # ------------------------------------------------------------------ #
    # section CSV: per-section edge summary + per-pair Jaccard rows       #
    # ------------------------------------------------------------------ #
    section_rows: list[dict] = []
    for s in sec["kept_sections"]:
        n_first = sum(sec["first_by_sec"].get(s, collections.Counter()).values())
        n_last = sum(sec["last_by_sec"].get(s, collections.Counter()).values())
        section_rows.append(
            {
                "row_type": "section",
                "section_a": s,
                "section_b": "",
                "n_first_lines": n_first,
                "n_last_lines": n_last,
                "top_first": "|".join(sorted(sec["first_sets"].get(s, set()))),
                "top_last": "|".join(sorted(sec["last_sets"].get(s, set()))),
                "jaccard_first": "",
                "jaccard_last": "",
                "semantic_guardrail": GUARDRAIL,
            }
        )
    secs = sec["kept_sections"]
    for i in range(len(secs)):
        for j in range(i + 1, len(secs)):
            a, b = secs[i], secs[j]
            section_rows.append(
                {
                    "row_type": "pair",
                    "section_a": a,
                    "section_b": b,
                    "n_first_lines": "",
                    "n_last_lines": "",
                    "top_first": "",
                    "top_last": "",
                    "jaccard_first": _r(
                        jaccard(sec["first_sets"][a], sec["first_sets"][b]), 4
                    ),
                    "jaccard_last": _r(
                        jaccard(sec["last_sets"][a], sec["last_sets"][b]), 4
                    ),
                    "semantic_guardrail": GUARDRAIL,
                }
            )
    write_csv(
        Path(args.out_section),
        section_rows,
        [
            "row_type",
            "section_a",
            "section_b",
            "n_first_lines",
            "n_last_lines",
            "top_first",
            "top_last",
            "jaccard_first",
            "jaccard_last",
            "semantic_guardrail",
        ],
    )

    # ------------------------------------------------------------------ #
    # summary CSV                                                        #
    # ------------------------------------------------------------------ #
    caveat = (
        "'laafu_is_layout' means the residual is a richer CONTENT-FREE layout "
        "rule, not syntax; NOT a decipherment"
    )
    summary_rows = [
        {"metric": "laafu_real", "value": _r(laafu_real, 6)},
        {"metric": "laafu_r62_baseline", "value": _r(R62_BASELINE, 6)},
        {"metric": "laafu_miller_madow", "value": _r(laafu_mm, 6)},
        {"metric": "laafu_headless", "value": _r(laafu_headless, 6)},
        {"metric": "head_gap_explained_frac", "value": _r(head_gap_explained_frac, 6)},
        {"metric": "closure_k50", "value": str(k50)},
        {"metric": "closure_k70", "value": str(k70)},
        {"metric": "closure_k90", "value": str(k90)},
        {"metric": "section_top_overlap", "value": _r(sec["mean_overlap"], 6)},
        {"metric": "section_js_p_vs_null", "value": _r(sec["js_p"], 6)},
        {"metric": "laafu_I_currierA", "value": _r(laafu_A, 6)},
        {"metric": "laafu_I_currierB", "value": _r(laafu_B, 6)},
        {"metric": "verdict", "value": verdict},
        {"metric": "caveat", "value": caveat},
        {"metric": "guardrail", "value": GUARDRAIL},
    ]
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    # ------------------------------------------------------------------ #
    # console report                                                     #
    # ------------------------------------------------------------------ #
    print(
        f"n_lines={len(lines)} laafu_real={laafu_real:.4f} "
        f"laafu_miller_madow={laafu_mm:.4f} r62_baseline={R62_BASELINE:.3f}"
    )
    print("ANALYSIS 1 — paleographic-head subtraction (THE decisive control):")
    print(
        f"  laafu_headless={laafu_headless:.4f}  "
        f"head_gap_explained_frac={head_gap_explained_frac:.4f}  "
        f"(>= {HEAD_GAP_LAYOUT_THRESH:.2f} => layout) -> layout_head={flags['layout_head']}"
    )
    print("ANALYSIS 2 — sparse-closure curve:")
    print(
        f"  total_laafu(curve)={closure_total:.4f}  k50={k50} k70={k70} k90={k90}  "
        f"(k70 <= {CLOSURE_K70_LAYOUT_THRESH} => sparse) -> layout_sparse={flags['layout_sparse']}"
    )
    print("ANALYSIS 3 — section-invariance of edge tokens:")
    print(
        f"  kept_sections={sec['kept_sections']}\n"
        f"  first_overlap={sec['first_overlap']:.4f} last_overlap={sec['last_overlap']:.4f} "
        f"mean_overlap={sec['mean_overlap']:.4f}  "
        f"JS_obs={sec['js_obs']:.4f} JS_null_mean={sec['js_null_mean']:.4f} "
        f"JS_p={sec['js_p']:.4f} (n_perm={args.n_perm})"
    )
    print(
        f"  (overlap>={SECTION_OVERLAP_LAYOUT_THRESH:.2f} & p>{SECTION_JS_P_LAYOUT_THRESH:.2f} "
        f"=> universal) -> layout_invar={flags['layout_invar']}  "
        f"content_section={flags['content_section']}"
    )
    print("ANALYSIS 4 — within-Currier laafu_I (never pool):")
    print(
        f"  laafu_I_A={laafu_A:.4f} (n_lines={n_A})  "
        f"laafu_I_B={laafu_B:.4f} (n_lines={n_B})"
    )
    print(f"VERDICT={verdict}  flags={flags}")
    print(
        "caveat: 'laafu_is_layout' means the residual is a richer CONTENT-FREE "
        "layout rule, not syntax; NOT a decipherment. Even 'laafu_carries_content' "
        "means position binding is topic-conditioned, never a translation."
    )
    print(f"closure_csv={args.out_closure}")
    print(f"section_csv={args.out_section}")
    print(f"summary_csv={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
