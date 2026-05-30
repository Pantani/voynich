#!/usr/bin/env python3
"""Rota 65 Leg A — RADIAL/CIRCULAR vs PARAGRAPH: does ring text behave
statistically differently from running prose, or is the apparent difference
a section-vocabulary artifact of the cosmological/astro folios?

CONTEXT
  The cosmological folios (f67-70 star/zodiac wheels, f85v-86r rosettes) carry
  text in RING / RADIAL / CIRCULAR layouts rather than paragraphs. The IVTFF
  transcription tags each locus with a single-letter KIND: P (paragraph),
  L (label), C (circular), R (radial / ring-line). The tag lives just past the
  comma in ``<f85v.10,@C>``-style locus headers; analyze_nucleus_context.py
  already exposes ``parse_corpus_with_kind`` which extracts (folio, kind, token)
  records, so we REUSE it.

QUESTION (falsifiable)
  Does the radial/circular class differ from paragraph in token-level features
  (vocabulary, prefix mix, nucleus mix, length, character h2), and does that
  difference SURVIVE controlling for the folio it lives on? Folio control is
  decisive: radial loci concentrate in a handful of cosmological folios, so a
  GLOBAL contrast mostly re-measures section vocabulary (the same confounder
  pattern R63/R64 fought). The WITHIN-FOLIO contrast — restricted to folios
  that carry BOTH a paragraph AND a radial/circular block — is the real test.

DESIGN
  1. Coarse class per token (commitado ANTES de testar):
        paragraph = {P}
        radial    = {C, R}     # ring / radial / circular
        label     = {L}
        other     = anything else
  2. Per class compute:
       - top-10 token unigrams
       - prefix distribution (qo-/ok-/ot-/yk-/yt-/none)
       - nucleus distribution (ch / sh / none)
       - mean token length + bucketed distribution
       - conditional character h2 within the class
  3. Contrast RADIAL vs PARAGRAPH (headline). For each feature compute
     V(class x feature) and a permutation p (>= 2000 shuffles, seeded).
  4. CONTROL — within-folio version: V(class x feature) restricted to folios
     that have BOTH paragraph AND radial/circular loci (the cosmological
     folios themselves carry both). Shuffle class only WITHIN folio.
  5. SPECIFIC FOLIO CASE — f67r2 already showed (Rota 50) that ot- prefers
     label loci on the moon labels. On this folio, run the radial-vs-paragraph
     prefix contrast directly and check whether the R50 pattern holds.

VERDICT
  - "radial_paragraph_differ" iff at least one feature has p_within_folio<0.05
    on >=2 folios that carry both classes.
  - "no_difference" otherwise.

NOT a translation. Guardrail in every output CSV.
"""
from __future__ import annotations

import argparse
import collections
import csv
import math
import random
import re
from pathlib import Path

from scripts.analyze_nucleus_context import parse_corpus_with_kind

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota65a_radial_paragraph_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"
N_PERM_DEFAULT = 2000
SEED_DEFAULT = 65

# --- coarse class commit (BEFORE testing, no df inflation) -----------------
KIND_TO_CLASS: dict[str, str] = {
    "P": "paragraph",
    "C": "radial",  # circular
    "R": "radial",  # radial / ring-line
    "L": "label",
}
CLASSES = ("paragraph", "radial", "label", "other")
HEADLINE_CLASSES = ("paragraph", "radial")

# --- token feature extractors (mirror cross-modal vocabulary) --------------
PREFIXES = ("qo", "ok", "ot", "yk", "yt")
NUCLEI = ("ch", "sh")


def coarse_class(kind: str) -> str:
    """Map a single-letter locus KIND to its coarse class."""
    return KIND_TO_CLASS.get(kind, "other")


def prefix_of(tok: str) -> str:
    """Bucket the operator prefix carried by the token (qo/ok/ot/yk/yt/none)."""
    if not tok:
        return "none"
    p2 = tok[:2]
    if p2 in PREFIXES:
        return p2
    return "none"


def nucleus_of(tok: str) -> str:
    """ch / sh / none — first bench substring seen (tokens are short)."""
    has_ch = "ch" in tok
    has_sh = "sh" in tok
    if has_ch and not has_sh:
        return "ch"
    if has_sh and not has_ch:
        return "sh"
    if has_ch and has_sh:
        # both present: report the first occurrence (deterministic, rare)
        return "ch" if tok.find("ch") < tok.find("sh") else "sh"
    return "none"


def length_bucket(tok: str) -> str:
    """short<=4 / mid 5-6 / long>=7 — same buckets as R63/R64."""
    n = len(tok)
    if n <= 4:
        return "short"
    if n <= 6:
        return "mid"
    return "long"


FEATURES: dict[str, "callable"] = {
    "prefix": prefix_of,
    "nucleus": nucleus_of,
    "length_bucket": length_bucket,
}


# --- statistics helpers ---------------------------------------------------
def cramer_v(table: dict[str, collections.Counter]) -> tuple[float, int]:
    """Cramer's V of {row_key: Counter(col_key->n)}. Returns (V, N). N<4 -> 0."""
    rk = list(table.keys())
    ck = sorted({c for cnt in table.values() for c in cnt})
    t = [[table[r].get(c, 0) for c in ck] for r in rk]
    N = sum(sum(row) for row in t)
    if N < 4:
        return 0.0, N
    rs = [sum(row) for row in t]
    cs = [sum(t[i][j] for i in range(len(rk))) for j in range(len(ck))]
    chi2 = sum(
        (t[i][j] - rs[i] * cs[j] / N) ** 2 / (rs[i] * cs[j] / N)
        for i in range(len(rk))
        for j in range(len(ck))
        if rs[i] * cs[j] / N > 0
    )
    k = min(len(rk), len(ck))
    return (math.sqrt(chi2 / (N * (k - 1))) if N * (k - 1) > 0 else 0.0), N


def char_h2(tokens: list[str]) -> float:
    """Conditional character entropy h2 = H(next | prev) in bits over a class.

    Tokens are concatenated with a single space sentinel so a token boundary
    does not bleed digrams across tokens. Same definition as R58.
    """
    s = " ".join(tokens)
    if len(s) < 3:
        return 0.0
    bg: collections.Counter = collections.Counter()
    ug: collections.Counter = collections.Counter()
    for i in range(len(s) - 1):
        a, b = s[i], s[i + 1]
        bg[(a, b)] += 1
        ug[a] += 1
    h = 0.0
    n = sum(bg.values())
    if n == 0:
        return 0.0
    for (a, b), c in bg.items():
        p_ab = c / n
        p_b_given_a = c / ug[a]
        h -= p_ab * math.log2(p_b_given_a) if p_b_given_a > 0 else 0
    return h


def _global_shuffle(class_vals: list[str], rng: random.Random) -> list[str]:
    out = class_vals[:]
    rng.shuffle(out)
    return out


def _within_folio_shuffle(
    class_vals: list[str], folios: list[str], rng: random.Random
) -> list[str]:
    """Shuffle classes ONLY within each folio.

    Preserves the per-folio multiset of classes (so the per-folio class counts
    are identical to the observed); only the assignment of class to token
    within a folio is randomized. This is the decisive control against the
    section-vocabulary artifact.
    """
    idx_by_folio: dict[str, list[int]] = collections.defaultdict(list)
    for i, fo in enumerate(folios):
        idx_by_folio[fo].append(i)
    out = class_vals[:]
    for idxs in idx_by_folio.values():
        vals = [class_vals[i] for i in idxs]
        rng.shuffle(vals)
        for i, v in zip(idxs, vals):
            out[i] = v
    return out


def feature_table(
    elements: list[tuple[str, str, str]], feature: str
) -> dict[str, collections.Counter]:
    """elements = [(folio, coarse_class, token), ...] -> table feat_val x class."""
    fn = FEATURES[feature]
    table: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for _f, cls, tok in elements:
        table[fn(tok)][cls] += 1
    return table


def permutation_pvalues(
    elements: list[tuple[str, str, str]],
    feature: str,
    n_perm: int,
    seed: int,
) -> tuple[float, float, float, int]:
    """Return (V_obs, p_global, p_within_folio, N) for a feature.

    p uses the +1 convention so neither p_value can be 0. p_global shuffles
    classes across ALL elements; p_within_folio shuffles classes only inside
    each folio (controls for section vocabulary).
    """
    fn = FEATURES[feature]
    feat_vals = [fn(t) for _f, _c, t in elements]
    class_vals = [c for _f, c, _t in elements]
    folios = [f for f, _c, _t in elements]
    v_obs, n = cramer_v(_pair_table(feat_vals, class_vals))

    rng_g = random.Random(seed)
    ge_global = 0
    for _ in range(n_perm):
        perm = _global_shuffle(class_vals, rng_g)
        v, _ = cramer_v(_pair_table(feat_vals, perm))
        if v >= v_obs - 1e-12:
            ge_global += 1

    rng_w = random.Random(seed + 1)
    ge_within = 0
    for _ in range(n_perm):
        perm = _within_folio_shuffle(class_vals, folios, rng_w)
        v, _ = cramer_v(_pair_table(feat_vals, perm))
        if v >= v_obs - 1e-12:
            ge_within += 1

    p_global = (ge_global + 1) / (n_perm + 1)
    p_within = (ge_within + 1) / (n_perm + 1)
    return v_obs, p_global, p_within, n


def _pair_table(
    feat_vals: list[str], class_vals: list[str]
) -> dict[str, collections.Counter]:
    table: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for fv, cv in zip(feat_vals, class_vals):
        table[fv][cv] += 1
    return table


# --- distribution / summary --------------------------------------------------
def per_class_distribution(
    records: list[tuple[str, str, str]],
) -> dict[str, dict[str, object]]:
    """For each coarse class, return summary stats used by the distribution CSV.

    Keys per class:
      n               -- n tokens
      top10           -- list of (tok, n) top-10 unigrams
      top_token       -- first item of top10 or ("", 0)
      prefix_counts   -- Counter of prefix buckets
      top_prefix      -- prefix with the largest count
      nucleus_counts  -- Counter of ch/sh/none
      length_counts   -- Counter of short/mid/long buckets
      mean_length     -- float
      h2              -- conditional char entropy in bits over the class
    """
    by_class: dict[str, list[str]] = {c: [] for c in CLASSES}
    by_class_folios: dict[str, list[str]] = {c: [] for c in CLASSES}
    for folio, kind, tok in records:
        cls = coarse_class(kind)
        by_class[cls].append(tok)
        by_class_folios[cls].append(folio)

    out: dict[str, dict[str, object]] = {}
    for cls in CLASSES:
        toks = by_class[cls]
        n = len(toks)
        if n == 0:
            out[cls] = {
                "n": 0,
                "top10": [],
                "top_token": ("", 0),
                "prefix_counts": collections.Counter(),
                "top_prefix": "none",
                "nucleus_counts": collections.Counter(),
                "length_counts": collections.Counter(),
                "mean_length": 0.0,
                "h2": 0.0,
            }
            continue
        unigrams = collections.Counter(toks)
        top10 = unigrams.most_common(10)
        pcounts = collections.Counter(prefix_of(t) for t in toks)
        ncounts = collections.Counter(nucleus_of(t) for t in toks)
        lcounts = collections.Counter(length_bucket(t) for t in toks)
        mean_len = sum(len(t) for t in toks) / n
        h2 = char_h2(toks)
        out[cls] = {
            "n": n,
            "top10": top10,
            "top_token": top10[0],
            "prefix_counts": pcounts,
            "top_prefix": max(pcounts.items(), key=lambda x: x[1])[0],
            "nucleus_counts": ncounts,
            "length_counts": lcounts,
            "mean_length": mean_len,
            "h2": h2,
        }
    return out


def folios_with_both(
    records: list[tuple[str, str, str]],
    a: str = "paragraph",
    b: str = "radial",
) -> list[str]:
    """Folios that carry at least one token of class ``a`` AND at least one of ``b``."""
    by_folio: dict[str, set[str]] = collections.defaultdict(set)
    for folio, kind, _tok in records:
        by_folio[folio].add(coarse_class(kind))
    return sorted(f for f, cls in by_folio.items() if a in cls and b in cls)


def restrict_to_radial_paragraph(
    records: list[tuple[str, str, str]],
    folios: list[str] | None = None,
) -> list[tuple[str, str, str]]:
    """Keep only tokens whose coarse class is paragraph or radial.

    If ``folios`` is given, additionally restrict to that folio set (the
    within-folio universe).
    """
    fol = set(folios) if folios is not None else None
    out: list[tuple[str, str, str]] = []
    for folio, kind, tok in records:
        cls = coarse_class(kind)
        if cls not in HEADLINE_CLASSES:
            continue
        if fol is not None and folio not in fol:
            continue
        out.append((folio, cls, tok))
    return out


# --- per-folio test (R50 confirmation on f67r2) ------------------------------
def per_folio_radial_paragraph_test(
    records: list[tuple[str, str, str]],
    folio: str,
    feature: str,
    n_perm: int,
    seed: int,
) -> dict[str, object]:
    """Run V(feature x class) + permutation p on tokens of ONE folio.

    Restricts to coarse class in {paragraph, radial}. The permutation here
    is a single-folio shuffle of class labels (Fisher-style). Returns dict
    with n, n_paragraph, n_radial, V, p per class.
    """
    sub = [
        (f, coarse_class(k), t)
        for f, k, t in records
        if f == folio and coarse_class(k) in HEADLINE_CLASSES
    ]
    n = len(sub)
    n_par = sum(1 for _f, c, _t in sub if c == "paragraph")
    n_rad = sum(1 for _f, c, _t in sub if c == "radial")
    result: dict[str, object] = {
        "folio": folio,
        "feature": feature,
        "n": n,
        "n_paragraph": n_par,
        "n_radial": n_rad,
        "cramer_v": 0.0,
        "p_within_folio": 1.0,
    }
    if n < 4 or n_par == 0 or n_rad == 0:
        return result
    fn = FEATURES[feature]
    feat_vals = [fn(t) for _f, _c, t in sub]
    class_vals = [c for _f, c, _t in sub]
    v_obs, _ = cramer_v(_pair_table(feat_vals, class_vals))
    rng = random.Random(seed)
    ge = 0
    for _ in range(n_perm):
        perm = class_vals[:]
        rng.shuffle(perm)
        v, _ = cramer_v(_pair_table(feat_vals, perm))
        if v >= v_obs - 1e-12:
            ge += 1
    result["cramer_v"] = round(v_obs, 4)
    result["p_within_folio"] = round((ge + 1) / (n_perm + 1), 4)
    return result


def per_folio_label_paragraph_test(
    records: list[tuple[str, str, str]],
    folio: str,
    feature: str,
    n_perm: int,
    seed: int,
) -> dict[str, object]:
    """R50-style contrast: LABEL (L) vs PARAGRAPH (P) on a single folio.

    f67r2 carries the moon labels Rota 50 already tagged as ot-prefixed.
    R50 framing is label-vs-text, not radial-vs-text (this folio has no
    radial loci). Returns the same dict shape as the radial-vs-paragraph
    function, with n_label in place of n_radial.
    """
    sub = [
        (f, coarse_class(k), t)
        for f, k, t in records
        if f == folio and coarse_class(k) in ("paragraph", "label")
    ]
    n = len(sub)
    n_par = sum(1 for _f, c, _t in sub if c == "paragraph")
    n_lab = sum(1 for _f, c, _t in sub if c == "label")
    result: dict[str, object] = {
        "folio": folio,
        "feature": feature,
        "scope": "focus_label_vs_paragraph",
        "n": n,
        "n_paragraph": n_par,
        "n_label": n_lab,
        "cramer_v": 0.0,
        "p_within_folio": 1.0,
    }
    if n < 4 or n_par == 0 or n_lab == 0:
        return result
    fn = FEATURES[feature]
    feat_vals = [fn(t) for _f, _c, t in sub]
    class_vals = [c for _f, c, _t in sub]
    v_obs, _ = cramer_v(_pair_table(feat_vals, class_vals))
    rng = random.Random(seed)
    ge = 0
    for _ in range(n_perm):
        perm = class_vals[:]
        rng.shuffle(perm)
        v, _ = cramer_v(_pair_table(feat_vals, perm))
        if v >= v_obs - 1e-12:
            ge += 1
    result["cramer_v"] = round(v_obs, 4)
    result["p_within_folio"] = round((ge + 1) / (n_perm + 1), 4)
    return result


# --- CSV writers -------------------------------------------------------------
def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def _distribution_rows(dist: dict[str, dict[str, object]]) -> list[dict]:
    rows = []
    for cls in CLASSES:
        d = dist[cls]
        top_tok = d["top_token"]  # type: ignore[index]
        top_tok_str = f"{top_tok[0]}={top_tok[1]}" if d["n"] else ""
        prefix_summary = ";".join(
            f"{p}={d['prefix_counts'].get(p, 0)}"  # type: ignore[union-attr]
            for p in (*PREFIXES, "none")
        )
        nucleus_summary = ";".join(
            f"{n}={d['nucleus_counts'].get(n, 0)}"  # type: ignore[union-attr]
            for n in (*NUCLEI, "none")
        )
        length_summary = ";".join(
            f"{lb}={d['length_counts'].get(lb, 0)}"  # type: ignore[union-attr]
            for lb in ("short", "mid", "long")
        )
        rows.append(
            {
                "class": cls,
                "n": d["n"],
                "top_token": top_tok_str,
                "top_prefix": d["top_prefix"],
                "prefix_distribution": prefix_summary,
                "nucleus_distribution": nucleus_summary,
                "length_distribution": length_summary,
                "mean_length": round(float(d["mean_length"]), 3),
                "h2_within_class": round(float(d["h2"]), 4),
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("corpus", nargs="?", default=str(DEFAULT_CORPUS))
    p.add_argument("--n-perm", type=int, default=N_PERM_DEFAULT)
    p.add_argument("--seed", type=int, default=SEED_DEFAULT)
    d = ROOT / "data" / "derived"
    p.add_argument(
        "--out-distribution",
        default=str(d / "radial_paragraph_distribution_zl3b.csv"),
    )
    p.add_argument(
        "--out-test", default=str(d / "radial_paragraph_test_zl3b.csv")
    )
    p.add_argument(
        "--out-summary", default=str(d / "radial_paragraph_summary_zl3b.csv")
    )
    p.add_argument(
        "--focus-folio",
        default="f67r2",
        help="Folio on which to confirm the R50 label-prefix pattern.",
    )
    return p.parse_args(argv)


# --- main --------------------------------------------------------------------
def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    records = parse_corpus_with_kind(Path(args.corpus))

    # 1) Per-class distribution (all classes, corpus-wide).
    dist = per_class_distribution(records)

    # 2) Headline contrast: radial vs paragraph, GLOBAL + WITHIN-FOLIO universe.
    # Global universe = every paragraph/radial token in the corpus.
    headline_global = restrict_to_radial_paragraph(records)
    # Within-folio universe = folios with BOTH paragraph and radial loci.
    both_folios = folios_with_both(records, "paragraph", "radial")
    headline_within = restrict_to_radial_paragraph(records, both_folios)

    # 3) Per-feature: V_global, p_global, V_within_folio, p_within_folio.
    test_rows: list[dict] = []
    feature_results: dict[str, dict[str, float]] = {}
    for fi, feature in enumerate(FEATURES):
        v_g, p_g, _p_w_global_ignored, n_g = permutation_pvalues(
            headline_global, feature, args.n_perm, args.seed + 7 * fi
        )
        # within-folio universe only: p_within_folio = shuffle CLASSES inside
        # each folio (decisive control). p_global on this sub-universe is the
        # same information as V_within_folio's null, so we keep only the two
        # reported numbers (V_within, p_within).
        v_w, _p_g_within_universe, p_w, n_w = permutation_pvalues(
            headline_within, feature, args.n_perm, args.seed + 7 * fi + 3
        )
        test_rows.append(
            {
                "feature": feature,
                "n_global": n_g,
                "V_global": round(v_g, 4),
                "p_global": round(p_g, 4),
                "n_within_folio": n_w,
                "V_within_folio": round(v_w, 4),
                "p_within_folio": round(p_w, 4),
                "semantic_guardrail": GUARDRAIL,
            }
        )
        feature_results[feature] = {
            "V_global": v_g,
            "p_global": p_g,
            "V_within_folio": v_w,
            "p_within_folio": p_w,
        }

    # 4) Per-folio (each folio that carries both classes) -- decisive for verdict.
    per_folio_rows: list[dict] = []
    folio_feature_hit: dict[str, set[str]] = collections.defaultdict(set)
    for folio in both_folios:
        for fi, feature in enumerate(FEATURES):
            r = per_folio_radial_paragraph_test(
                records,
                folio,
                feature,
                args.n_perm,
                args.seed + 1000 + 11 * fi,
            )
            r["semantic_guardrail"] = GUARDRAIL
            per_folio_rows.append(r)
            if float(r["p_within_folio"]) < 0.05:
                folio_feature_hit[feature].add(folio)

    # Verdict: at least one feature with p_within_folio<0.05 on >=2 folios that
    # carry both classes.
    differing_feature = None
    differing_folios: list[str] = []
    for feature, fols in folio_feature_hit.items():
        if len(fols) >= 2:
            differing_feature = feature
            differing_folios = sorted(fols)
            break
    verdict = "radial_paragraph_differ" if differing_feature else "no_difference"

    # 5) Specific case: f67r2 (R50 framing). f67r2 carries P + L loci on its
    #    moon labels but no radial — so the R50 confirmation must be a
    #    LABEL-vs-PARAGRAPH contrast (R50's original framing). We ALSO emit
    #    the radial-vs-paragraph row for the same folio for completeness; it
    #    will be a no-op (n_radial=0) on folios like f67r2.
    focus = args.focus_folio
    focus_radial = per_folio_radial_paragraph_test(
        records, focus, "prefix", args.n_perm, args.seed + 99999
    )
    focus_radial["semantic_guardrail"] = GUARDRAIL
    focus_label = per_folio_label_paragraph_test(
        records, focus, "prefix", args.n_perm, args.seed + 99998
    )
    focus_label["semantic_guardrail"] = GUARDRAIL
    # R50 confirms iff label-vs-paragraph on the focus folio is significant
    # under the prefix feature (R50 found ot- on labels there).
    focus_confirms = (
        float(focus_label["p_within_folio"]) < 0.05
        and int(focus_label.get("n_label", 0)) > 0
        and int(focus_label.get("n_paragraph", 0)) > 0
    )

    # --- write CSVs ---
    write_csv(
        Path(args.out_distribution),
        _distribution_rows(dist),
        [
            "class",
            "n",
            "top_token",
            "top_prefix",
            "prefix_distribution",
            "nucleus_distribution",
            "length_distribution",
            "mean_length",
            "h2_within_class",
            "semantic_guardrail",
        ],
    )
    # ``test`` CSV: aggregate (headline rows) + per-folio rows so the within-
    # folio breakdown lives next to the global numbers.
    test_fieldnames = [
        "feature",
        "scope",
        "folio",
        "n",
        "n_paragraph",
        "n_radial",
        "V",
        "p_within_folio",
        "V_global",
        "p_global",
        "semantic_guardrail",
    ]
    aggregate_rows = []
    for row in test_rows:
        aggregate_rows.append(
            {
                "feature": row["feature"],
                "scope": "global",
                "folio": "",
                "n": row["n_global"],
                "n_paragraph": "",
                "n_radial": "",
                "V": row["V_global"],
                "p_within_folio": "",
                "V_global": row["V_global"],
                "p_global": row["p_global"],
                "semantic_guardrail": GUARDRAIL,
            }
        )
        aggregate_rows.append(
            {
                "feature": row["feature"],
                "scope": "within_folio_universe",
                "folio": "",
                "n": row["n_within_folio"],
                "n_paragraph": "",
                "n_radial": "",
                "V": row["V_within_folio"],
                "p_within_folio": row["p_within_folio"],
                "V_global": "",
                "p_global": "",
                "semantic_guardrail": GUARDRAIL,
            }
        )
    for r in per_folio_rows:
        aggregate_rows.append(
            {
                "feature": r["feature"],
                "scope": "per_folio",
                "folio": r["folio"],
                "n": r["n"],
                "n_paragraph": r["n_paragraph"],
                "n_radial": r["n_radial"],
                "V": r["cramer_v"],
                "p_within_folio": r["p_within_folio"],
                "V_global": "",
                "p_global": "",
                "semantic_guardrail": GUARDRAIL,
            }
        )
    # focus row: radial-vs-paragraph on the focus folio (may be n=0 if no
    # radial loci on that folio, as is the case on f67r2).
    aggregate_rows.append(
        {
            "feature": focus_radial["feature"],
            "scope": "focus_folio",
            "folio": focus_radial["folio"],
            "n": focus_radial["n"],
            "n_paragraph": focus_radial["n_paragraph"],
            "n_radial": focus_radial["n_radial"],
            "V": focus_radial["cramer_v"],
            "p_within_folio": focus_radial["p_within_folio"],
            "V_global": "",
            "p_global": "",
            "semantic_guardrail": GUARDRAIL,
        }
    )
    # focus row: label-vs-paragraph on the focus folio (R50's framing on
    # f67r2's moon labels). n_radial column is reused to carry n_label so
    # the CSV schema stays stable.
    aggregate_rows.append(
        {
            "feature": focus_label["feature"],
            "scope": "focus_folio_label",
            "folio": focus_label["folio"],
            "n": focus_label["n"],
            "n_paragraph": focus_label["n_paragraph"],
            "n_radial": focus_label["n_label"],
            "V": focus_label["cramer_v"],
            "p_within_folio": focus_label["p_within_folio"],
            "V_global": "",
            "p_global": "",
            "semantic_guardrail": GUARDRAIL,
        }
    )
    write_csv(Path(args.out_test), aggregate_rows, test_fieldnames)

    # --- summary ---
    n_par = dist["paragraph"]["n"]
    n_rad = dist["radial"]["n"]
    n_lab = dist["label"]["n"]
    n_oth = dist["other"]["n"]
    # best-feature pick by V_within_folio (decisive against the section
    # confounder); break ties by V_global.
    best_feature = max(
        feature_results.items(),
        key=lambda kv: (kv[1]["V_within_folio"], kv[1]["V_global"]),
    )
    best_name = best_feature[0]
    best_metrics = best_feature[1]

    summary_rows = [
        {"metric": "n_paragraph", "value": str(n_par)},
        {"metric": "n_radial", "value": str(n_rad)},
        {"metric": "n_label", "value": str(n_lab)},
        {"metric": "n_other", "value": str(n_oth)},
        {"metric": "n_folios_with_both", "value": str(len(both_folios))},
        {"metric": "folios_with_both", "value": ";".join(both_folios)},
        {"metric": "best_feature_within_folio", "value": best_name},
        {
            "metric": "best_feature_V_global",
            "value": str(round(best_metrics["V_global"], 4)),
        },
        {
            "metric": "best_feature_p_global",
            "value": str(round(best_metrics["p_global"], 4)),
        },
        {
            "metric": "best_feature_V_within_folio",
            "value": str(round(best_metrics["V_within_folio"], 4)),
        },
        {
            "metric": "best_feature_p_within_folio",
            "value": str(round(best_metrics["p_within_folio"], 4)),
        },
        {"metric": "verdict_feature", "value": differing_feature or ""},
        {
            "metric": "verdict_folios",
            "value": ";".join(differing_folios),
        },
        {"metric": "verdict", "value": verdict},
        {"metric": "focus_folio", "value": focus},
        # focus_radial = radial-vs-paragraph on the focus folio (n=0 means
        # the folio has no radial loci, e.g. f67r2).
        {
            "metric": "focus_radial_n_paragraph",
            "value": str(focus_radial["n_paragraph"]),
        },
        {
            "metric": "focus_radial_n_radial",
            "value": str(focus_radial["n_radial"]),
        },
        {
            "metric": "focus_radial_cramer_v",
            "value": str(focus_radial["cramer_v"]),
        },
        {
            "metric": "focus_radial_p_within_folio",
            "value": str(focus_radial["p_within_folio"]),
        },
        # focus_label = label-vs-paragraph (R50 framing) on the focus folio.
        # The R50 confirmation gate keys off these numbers.
        {
            "metric": "focus_label_n_paragraph",
            "value": str(focus_label["n_paragraph"]),
        },
        {
            "metric": "focus_label_n_label",
            "value": str(focus_label["n_label"]),
        },
        {
            "metric": "focus_label_cramer_v",
            "value": str(focus_label["cramer_v"]),
        },
        {
            "metric": "focus_label_p_within_folio",
            "value": str(focus_label["p_within_folio"]),
        },
        {"metric": "focus_confirms_R50", "value": str(focus_confirms)},
        {"metric": "n_perm", "value": str(args.n_perm)},
        {"metric": "seed", "value": str(args.seed)},
        {"metric": "semantic_guardrail", "value": GUARDRAIL},
    ]
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    print(
        f"n_par={n_par} n_rad={n_rad} n_lab={n_lab} both_folios={len(both_folios)}"
    )
    for row in test_rows:
        print(
            f"feature={row['feature']:>14s} V_global={row['V_global']:.4f}"
            f" p_global={row['p_global']:.4f} V_within={row['V_within_folio']:.4f}"
            f" p_within={row['p_within_folio']:.4f}"
        )
    print(
        f"best_feature_within={best_name} "
        f"V_within={best_metrics['V_within_folio']:.4f}"
        f" p_within={best_metrics['p_within_folio']:.4f}"
    )
    print(
        f"focus={focus} radial: n_par={focus_radial['n_paragraph']} "
        f"n_rad={focus_radial['n_radial']} V={focus_radial['cramer_v']} "
        f"p={focus_radial['p_within_folio']}"
    )
    print(
        f"focus={focus} label : n_par={focus_label['n_paragraph']} "
        f"n_lab={focus_label['n_label']} V={focus_label['cramer_v']} "
        f"p={focus_label['p_within_folio']} confirms_R50={focus_confirms}"
    )
    print(f"verdict={verdict} ({differing_feature or 'no-feature'},"
          f" folios={','.join(differing_folios) or '-'})")
    print(f"distribution_csv={args.out_distribution}")
    print(f"test_csv={args.out_test}")
    print(f"summary_csv={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
