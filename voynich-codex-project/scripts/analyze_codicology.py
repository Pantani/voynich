#!/usr/bin/env python3
"""Rota 68: the OBJECT's PRODUCTION structure from IVTFF per-folio metadata.

The ONE corpus-internal contribution to the external/provenance front. R66 showed
that only provenance/material can still move the "does it mean anything?" needle;
this route characterises how the CODEX WAS MADE -- hands, quires, Currier blocks --
and asks whether that production was PLANNED/BLOCKED or INTERLEAVED. It is a
statement about the physical artefact's construction; it NEVER touches meaning.

DATA -- IVTFF per-folio header tags in data/raw/ZL3b-n.txt. Each `<f..>` line
carries a `<! ... >` comment with `$`-tags:
  $L  Currier sub-language (A/B; "?" when absent)
  $Q  quire (A-T)
  $P  page sequence within quire ; $B bifolio ; $F folio-leaf id
  $H  Currier hand (integer 1-5)
  $I  illustration type == section: H herbal, A astro, Z zodiac, B balneo,
      C cosmo, P pharma, S stars/recipes, T text-only
  $C  columns
NOT every folio carries every tag -- we parse what is present, REPORT COVERAGE
(n folios with each tag), and degrade gracefully. Currier $L + folio order are the
minimum and are well populated. The Currier parse REUSES analyze_section_scribe /
analyze_nucleus's mechanism ($L= read from the folio header).

CANONICAL FOLIO ORDER: numeric folio, then r<v, then foldout sub-leaf
(f1r < f1v < f2r < ... < f67r1 < f67r2 < ...).

THE PRODUCTION ANALYSES (object-level, falsifiable, meaning-free):

1. Currier-block contiguity. Order folios canonically; take the per-folio Currier
   ($L) label sequence; count maximal contiguous same-label RUNS and mean run
   length. Permutation null: shuffle the per-folio labels >=1000x and recompute
   n_runs. A PLANNED, blocked codex has FEWER runs / LONGER blocks than the null
   (p = fraction of shuffles with n_runs <= observed). Same for $H (hand).

2. Section <-> Currier <-> hand alignment. Cross-tabulate section ($I) x Currier
   ($L) and hand ($H) x Currier; report Cramer's V for each, and count the
   distinct (section, Currier, hand) production regimes that actually occur.
   (Context: R47 found a/o V_section=0.25 < V_Currier=0.44 -- section is confounded
   with Currier. Here we tabulate the LABELS' codicological alignment, not a/o.)

3. Regime count + quire mapping. How many distinct hands; how A/B map onto quires;
   whether quire boundaries coincide with Currier changes.

VERDICT (a pure function of measured booleans):
  planned_blocked_codex -- Currier strongly BLOCKED along folio order (runs
    significantly FEWER than the permutation null, p < 0.05) AND Currier changes
    align with quire seams (most boundaries fall at quire breaks).
  interleaved_production -- otherwise.

This is evidence about deliberate PRODUCTION (it supports "a serious constructed
artefact was made on purpose"), explicitly NOT about meaning. CAVEAT in every
output: production-seriousness is consistent with BOTH a meaningful text AND a
contentless generator -- it does NOT decide that question. Guardrail in every CSV.
"""
from __future__ import annotations

import argparse
import collections
import csv
import math
import random
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota68_codicology_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"

# Folio header line, e.g.  <f1r>      <! $Q=A $P=A $F=a $B=1 $I=T $L=A $H=1 ...>
# Reuses the analyze_nucleus mechanism: the folio id then a `<! ...>` comment.
_HDR = re.compile(r"^<(f[0-9]+[rv]\d?)>\s*<!\s*(.*?)>")
# Locus line (used only to find the dominant per-folio Currier if it ever varied).
_LOC = re.compile(r"^<(f[0-9]+[rv]\d?)\.\d+[^>]*>")
# One `$K=V` tag inside the comment (value runs up to whitespace).
_TAG = re.compile(r"\$([A-Z])=(\S+)")
# Currier $L specifically, anywhere on a line (header or, in principle, a locus).
_LANG = re.compile(r"\$L=([A-Z?])")

# Illustration-type code ($I) -> human section name (object section, not meaning).
SECTION_NAMES = {
    "H": "herbal",
    "A": "astronomical",
    "Z": "zodiac",
    "B": "balneological",
    "C": "cosmological",
    "P": "pharmaceutical",
    "S": "stars_recipes",
    "T": "text_only",
}

N_PERM = 1000
PERM_SEED = 20680


# --------------------------------------------------------------------------- #
# Canonical folio order                                                        #
# --------------------------------------------------------------------------- #
def folio_sort_key(folio: str) -> tuple[int, int, int]:
    """Canonical ordering key: (numeric folio, side r<v, foldout sub-leaf).

    f1r < f1v < f2r < ... < f10r < ... < f67r1 < f67r2 < f67v1 < ...
    'r' (recto) sorts before 'v' (verso); a trailing foldout digit (f67r2) sorts
    after the same side with a lower/absent digit (f67r1, then f67r2).
    """
    m = re.search(r"\d+", folio)
    num = int(m.group()) if m else 0
    side = 0 if "r" in folio else 1
    sub = re.search(r"[rv](\d)$", folio)
    sub_n = int(sub.group(1)) if sub else 0
    return (num, side, sub_n)


# --------------------------------------------------------------------------- #
# IVTFF metadata parse                                                         #
# --------------------------------------------------------------------------- #
def parse_folio_metadata(path: Path) -> dict[str, dict[str, str]]:
    """Parse per-folio header tags into {folio -> {tag -> value}}.

    Reads every `<f..>` header line, extracts all `$K=V` tags from its `<! ...>`
    comment, and -- to honour the "majority locus if mixed" rule for Currier --
    additionally scans locus lines for any locus-level `$L=` override, taking the
    per-folio MAJORITY Currier across loci when present. In the ZL3b corpus no
    locus carries its own $L, so this reduces to the header value; the machinery
    is kept so the rule holds if a future transliteration adds locus-level Currier.

    Only the tags that are present are recorded -- missing tags are simply absent
    from the inner dict, so coverage can be measured downstream.
    """
    meta: dict[str, dict[str, str]] = {}
    locus_currier: dict[str, collections.Counter] = collections.defaultdict(
        collections.Counter
    )
    cur_folio: str | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        mh = _HDR.match(line)
        if mh:
            cur_folio = mh.group(1)
            tags = dict(_TAG.findall(mh.group(2)))
            meta.setdefault(cur_folio, {}).update(tags)
            continue
        ml = _LOC.match(line)
        if ml:
            cur_folio = ml.group(1)
            lang = _LANG.search(line)
            if lang:
                locus_currier[cur_folio][lang.group(1)] += 1

    # Apply per-folio majority Currier from loci where it was actually present.
    for folio, counter in locus_currier.items():
        if counter:
            meta.setdefault(folio, {})["L"] = counter.most_common(1)[0][0]
    return meta


def currier_label(tags: dict[str, str]) -> str:
    """Currier label for a folio: 'A'/'B' if known, else 'unknown'."""
    v = tags.get("L", "?")
    return v if v in ("A", "B") else "unknown"


def hand_label(tags: dict[str, str]) -> str:
    """Currier hand for a folio: the integer string, else 'unknown'."""
    v = tags.get("H", "?")
    return v if v.isdigit() else "unknown"


def section_label(tags: dict[str, str]) -> str:
    """Section (illustration type $I) as a human name, else 'unknown'."""
    return SECTION_NAMES.get(tags.get("I", "?"), "unknown")


# --------------------------------------------------------------------------- #
# Run statistics + permutation null                                            #
# --------------------------------------------------------------------------- #
def count_runs(labels: list[str]) -> int:
    """Number of maximal contiguous same-label runs in a sequence.

    [] -> 0 ; [x] -> 1 ; [A,A,B,A] -> 3. Counts a new run each time the label
    changes from the previous position.
    """
    if not labels:
        return 0
    runs = 1
    for prev, cur in zip(labels, labels[1:]):
        if cur != prev:
            runs += 1
    return runs


def mean_run_length(labels: list[str]) -> float:
    """Mean length of the maximal same-label runs (len / n_runs)."""
    r = count_runs(labels)
    return len(labels) / r if r else 0.0


def runs_by_value(labels: list[str]) -> "collections.Counter[str]":
    """How many runs each distinct label contributes (for reporting)."""
    out: collections.Counter[str] = collections.Counter()
    if not labels:
        return out
    out[labels[0]] += 1
    for prev, cur in zip(labels, labels[1:]):
        if cur != prev:
            out[cur] += 1
    return out


def permutation_p_fewer_runs(
    labels: list[str], n_perm: int, seed: int
) -> tuple[float, float, int]:
    """One-sided permutation test that the sequence has FEWER runs than chance.

    Shuffles the label multiset `n_perm` times (deterministic under `seed`) and
    recomputes n_runs. Returns (p, mean_null_runs, observed_runs) where
    p = fraction of shuffles with n_runs <= observed (a small p => significantly
    BLOCKED / longer contiguous blocks than a random arrangement). The observed
    arrangement is counted in the null (the standard +1 convention) to keep
    p strictly > 0.
    """
    observed = count_runs(labels)
    if len(labels) < 2 or len(set(labels)) < 2:
        return 1.0, float(observed), observed
    rng = random.Random(seed)
    pool = list(labels)
    le = 1  # count the observed arrangement itself
    null_total = observed
    for _ in range(n_perm):
        rng.shuffle(pool)
        r = count_runs(pool)
        null_total += r
        if r <= observed:
            le += 1
    p = le / (n_perm + 1)
    mean_null = null_total / (n_perm + 1)
    return p, mean_null, observed


# --------------------------------------------------------------------------- #
# Cross-tabulation + Cramer's V                                                #
# --------------------------------------------------------------------------- #
def cross_tab(
    rows: list[dict[str, str]], row_key: str, col_key: str, exclude: set[str]
) -> dict[str, "collections.Counter[str]"]:
    """Cross-tabulate row_key x col_key over folios, skipping `exclude` values."""
    tab: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for r in rows:
        rv, cv = r[row_key], r[col_key]
        if rv in exclude or cv in exclude:
            continue
        tab[rv][cv] += 1
    return {k: v for k, v in tab.items()}


def cramer_v(table: dict[str, "collections.Counter[str]"]) -> tuple[float, int]:
    """Cramer's V for a contingency table (mirrors analyze_section_scribe)."""
    rk = list(table.keys())
    ck = list({c for cnt in table.values() for c in cnt})
    t = [[table[r].get(c, 0) for c in ck] for r in rk]
    N = sum(sum(row) for row in t)
    if N < 4 or len(rk) < 2 or len(ck) < 2:
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
    v = math.sqrt(chi2 / (N * (k - 1))) if N * (k - 1) > 0 else 0.0
    return v, N


# --------------------------------------------------------------------------- #
# Quire mapping                                                                #
# --------------------------------------------------------------------------- #
def quire_boundary_currier_changes(
    ordered: list[dict[str, str]]
) -> tuple[int, int, int]:
    """How many adjacent-folio steps are quire boundaries, and how Currier moves.

    Walking the canonically-ordered folios, a "quire boundary" is a step where the
    $Q value differs from the previous folio's. Returns
    (n_currier_change_at_boundary, n_quire_boundaries, n_currier_changes_total)
    counting only steps where BOTH folios have a known Currier (A/B). A planned,
    blocked codex changes Currier mostly AT quire seams.
    """
    n_boundaries = 0
    n_change_at_boundary = 0
    n_currier_changes = 0
    for prev, cur in zip(ordered, ordered[1:]):
        pq, cq = prev.get("quire", "?"), cur.get("quire", "?")
        is_boundary = pq != cq and pq != "?" and cq != "?"
        pc, cc = prev["currier"], cur["currier"]
        currier_known = pc != "unknown" and cc != "unknown"
        currier_changed = currier_known and pc != cc
        if currier_changed:
            n_currier_changes += 1
        if is_boundary:
            n_boundaries += 1
            if currier_changed:
                n_change_at_boundary += 1
    return n_change_at_boundary, n_boundaries, n_currier_changes


def per_quire_runs(ordered: list[dict[str, str]]) -> list[dict[str, str]]:
    """Per-quire Currier run structure for codicology_currier_runs CSV.

    For each quire (in first-appearance order along the canonical folio sequence),
    report the folio count, the Currier labels present, the number of Currier runs
    WITHIN that quire, the dominant Currier, and whether the quire is Currier-pure.
    """
    by_quire: "collections.OrderedDict[str, list[dict[str, str]]]" = (
        collections.OrderedDict()
    )
    for r in ordered:
        by_quire.setdefault(r.get("quire", "unknown"), []).append(r)
    out: list[dict[str, str]] = []
    for quire, folios in by_quire.items():
        labels = [f["currier"] for f in folios]
        known = [x for x in labels if x != "unknown"]
        present = sorted(set(known))
        dominant = (
            collections.Counter(known).most_common(1)[0][0] if known else "unknown"
        )
        out.append(
            {
                "quire": quire,
                "n_folios": str(len(folios)),
                "currier_labels": "|".join(present) if present else "unknown",
                "n_currier_runs": str(count_runs(known)),
                "dominant_currier": dominant,
                "currier_pure": str(len(present) <= 1),
                "first_folio": folios[0]["folio"],
                "last_folio": folios[-1]["folio"],
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return out


# --------------------------------------------------------------------------- #
# Verdict (pure function of measured booleans)                                 #
# --------------------------------------------------------------------------- #
def classify_verdict(
    currier_blocked: bool, changes_align_quires: bool
) -> str:
    """Pure-function verdict from the two production booleans.

    planned_blocked_codex requires BOTH that the Currier sequence is significantly
    BLOCKED versus the permutation null (currier_blocked: p < 0.05 with fewer runs)
    AND that Currier changes align with quire seams (changes_align_quires: a
    majority of the Currier transitions land on quire boundaries). Otherwise the
    production reads as interleaved.
    """
    if currier_blocked and changes_align_quires:
        return "planned_blocked_codex"
    return "interleaved_production"


# --------------------------------------------------------------------------- #
# IO                                                                           #
# --------------------------------------------------------------------------- #
def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def build_folio_rows(meta: dict[str, dict[str, str]]) -> list[dict[str, str]]:
    """One canonical-ordered record per folio with normalised label columns."""
    rows: list[dict[str, str]] = []
    for folio in sorted(meta.keys(), key=folio_sort_key):
        tags = meta[folio]
        rows.append(
            {
                "folio": folio,
                "quire": tags.get("Q", "unknown"),
                "currier": currier_label(tags),
                "hand": hand_label(tags),
                "section": section_label(tags),
            }
        )
    return rows


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("corpus", nargs="?", default=str(DEFAULT_CORPUS))
    p.add_argument("--n-perm", type=int, default=N_PERM)
    p.add_argument("--seed", type=int, default=PERM_SEED)
    d = ROOT / "data" / "derived"
    p.add_argument("--out-runs", default=str(d / "codicology_currier_runs_zl3b.csv"))
    p.add_argument("--out-alignment", default=str(d / "codicology_alignment_zl3b.csv"))
    p.add_argument("--out-summary", default=str(d / "codicology_summary_zl3b.csv"))
    p.add_argument(
        "--md", default=str(ROOT / "docs" / "research" / "rota_68_codicologia.md")
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    meta = parse_folio_metadata(Path(args.corpus))
    folios = build_folio_rows(meta)
    n_folios = len(folios)

    # --- coverage (n folios carrying each tag) ---
    cov_L = sum(1 for r in folios if r["currier"] != "unknown")
    cov_Q = sum(1 for r in folios if r["quire"] != "unknown")
    cov_H = sum(1 for r in folios if r["hand"] != "unknown")
    cov_I = sum(1 for r in folios if r["section"] != "unknown")

    n_A = sum(1 for r in folios if r["currier"] == "A")
    n_B = sum(1 for r in folios if r["currier"] == "B")
    hands = sorted({r["hand"] for r in folios if r["hand"] != "unknown"})
    quires = sorted({r["quire"] for r in folios if r["quire"] != "unknown"})

    # --- ANALYSIS 1: Currier-block contiguity + permutation null ---
    currier_seq = [r["currier"] for r in folios if r["currier"] != "unknown"]
    c_runs = count_runs(currier_seq)
    c_mean_run = mean_run_length(currier_seq)
    c_p, c_mean_null, _ = permutation_p_fewer_runs(currier_seq, args.n_perm, args.seed)

    # hand contiguity (if populated)
    hand_seq = [r["hand"] for r in folios if r["hand"] != "unknown"]
    h_runs = count_runs(hand_seq)
    h_mean_run = mean_run_length(hand_seq)
    h_p, h_mean_null, _ = permutation_p_fewer_runs(
        hand_seq, args.n_perm, args.seed + 1
    )

    # --- ANALYSIS 2: section x Currier, hand x Currier alignment ---
    sec_cur = cross_tab(folios, "section", "currier", exclude={"unknown"})
    v_sec_cur, n_sec_cur = cramer_v(sec_cur)
    hand_cur = cross_tab(folios, "hand", "currier", exclude={"unknown"})
    v_hand_cur, n_hand_cur = cramer_v(hand_cur)

    # distinct (section, Currier, hand) production regimes actually occurring
    regimes = collections.Counter(
        (r["section"], r["currier"], r["hand"])
        for r in folios
        if r["section"] != "unknown"
        and r["currier"] != "unknown"
        and r["hand"] != "unknown"
    )
    n_regimes = len(regimes)

    # --- ANALYSIS 3: quire mapping ---
    n_change_at_boundary, n_boundaries, n_currier_changes = (
        quire_boundary_currier_changes(folios)
    )
    boundary_change_frac = (
        n_change_at_boundary / n_currier_changes if n_currier_changes else 0.0
    )

    # --- verdict booleans (the verdict is a pure function of these) ---
    currier_blocked = c_p < 0.05 and c_runs < c_mean_null
    # Currier changes "align with quire seams" when a MAJORITY of the (few)
    # Currier transitions land on quire boundaries.
    changes_align_quires = boundary_change_frac > 0.5
    verdict = classify_verdict(currier_blocked, changes_align_quires)

    # --- write codicology_currier_runs_zl3b.csv (per-quire run structure) ---
    runs_rows = per_quire_runs(folios)
    write_csv(
        Path(args.out_runs),
        runs_rows,
        [
            "quire",
            "n_folios",
            "currier_labels",
            "n_currier_runs",
            "dominant_currier",
            "currier_pure",
            "first_folio",
            "last_folio",
            "semantic_guardrail",
        ],
    )

    # --- write codicology_alignment_zl3b.csv (section x Currier x hand cross-tab) ---
    align_rows: list[dict] = []
    cols = sorted({c for cnt in sec_cur.values() for c in cnt})
    for sec in sorted(sec_cur.keys()):
        row: dict[str, str] = {"axis": "section_x_currier", "row_label": sec}
        for c in ("A", "B"):
            row[f"currier_{c}"] = str(sec_cur[sec].get(c, 0))
        align_rows.append({**row, "semantic_guardrail": GUARDRAIL})
    for hd in sorted(hand_cur.keys(), key=lambda x: (len(x), x)):
        row = {"axis": "hand_x_currier", "row_label": hd}
        for c in ("A", "B"):
            row[f"currier_{c}"] = str(hand_cur[hd].get(c, 0))
        align_rows.append({**row, "semantic_guardrail": GUARDRAIL})
    write_csv(
        Path(args.out_alignment),
        align_rows,
        ["axis", "row_label", "currier_A", "currier_B", "semantic_guardrail"],
    )

    # --- write codicology_summary_zl3b.csv (metric,value) ---
    caveat = (
        "characterizes object PRODUCTION (hands/quires/blocks); says NOTHING "
        "about meaning"
    )
    summary_rows = [
        {"metric": "n_folios", "value": str(n_folios)},
        {"metric": "coverage_L", "value": str(cov_L)},
        {"metric": "coverage_Q", "value": str(cov_Q)},
        {"metric": "coverage_H", "value": str(cov_H)},
        {"metric": "coverage_I", "value": str(cov_I)},
        {"metric": "n_currier_A", "value": str(n_A)},
        {"metric": "n_currier_B", "value": str(n_B)},
        {"metric": "n_hands", "value": str(len(hands))},
        {"metric": "n_quires", "value": str(len(quires))},
        {"metric": "currier_n_runs", "value": str(c_runs)},
        {"metric": "currier_mean_run_len", "value": str(round(c_mean_run, 4))},
        {"metric": "currier_runs_p_vs_null", "value": str(round(c_p, 6))},
        {"metric": "currier_mean_null_runs", "value": str(round(c_mean_null, 4))},
        {"metric": "hand_n_runs", "value": str(h_runs) if hand_seq else "na"},
        {
            "metric": "hand_mean_run_len",
            "value": str(round(h_mean_run, 4)) if hand_seq else "na",
        },
        {
            "metric": "hand_runs_p_vs_null",
            "value": str(round(h_p, 6)) if hand_seq else "na",
        },
        {
            "metric": "V_section_currier",
            "value": str(round(v_sec_cur, 4)) if n_sec_cur else "na",
        },
        {
            "metric": "V_hand_currier",
            "value": str(round(v_hand_cur, 4)) if n_hand_cur else "na",
        },
        {"metric": "n_regimes", "value": str(n_regimes)},
        {"metric": "n_currier_changes", "value": str(n_currier_changes)},
        {"metric": "n_quire_boundaries", "value": str(n_boundaries)},
        {
            "metric": "quire_boundary_currier_change_frac",
            "value": str(round(boundary_change_frac, 4)),
        },
        {"metric": "currier_blocked", "value": str(currier_blocked)},
        {"metric": "changes_align_quires", "value": str(changes_align_quires)},
        {"metric": "verdict", "value": verdict},
        {"metric": "caveat", "value": caveat},
        {"metric": "guardrail", "value": GUARDRAIL},
    ]
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    # --- markdown report ---
    write_report(
        Path(args.md),
        folios=folios,
        n_folios=n_folios,
        coverage=(cov_L, cov_Q, cov_H, cov_I),
        currier=(n_A, n_B, c_runs, c_mean_run, c_p, c_mean_null),
        hand=(hands, h_runs, h_mean_run, h_p, h_mean_null) if hand_seq else None,
        alignment=(v_sec_cur, v_hand_cur, n_regimes),
        quire=(len(quires), n_change_at_boundary, n_boundaries, n_currier_changes,
               boundary_change_frac),
        booleans=(currier_blocked, changes_align_quires),
        verdict=verdict,
        caveat=caveat,
    )

    # --- console report ---
    print(
        f"n_folios={n_folios} coverage: L={cov_L} Q={cov_Q} H={cov_H} I={cov_I}"
    )
    print(
        f"currier: A={n_A} B={n_B} | hands={hands} | n_quires={len(quires)}"
    )
    print("[1] Currier-block contiguity:")
    print(
        f"    n_runs={c_runs} mean_run_len={c_mean_run:.3f} "
        f"null_mean_runs={c_mean_null:.2f} p_vs_null={c_p:.6f} "
        f"-> {'BLOCKED' if currier_blocked else 'not blocked'}"
    )
    if hand_seq:
        print(
            f"    hand: n_runs={h_runs} mean_run_len={h_mean_run:.3f} "
            f"null_mean_runs={h_mean_null:.2f} p_vs_null={h_p:.6f}"
        )
    print("[2] Alignment:")
    print(
        f"    V(section x Currier)={v_sec_cur:.4f}  "
        f"V(hand x Currier)={v_hand_cur:.4f}  n_regimes={n_regimes}"
    )
    print("[3] Quire mapping:")
    print(
        f"    currier_changes={n_currier_changes} at_quire_boundary="
        f"{n_change_at_boundary}/{n_boundaries} boundaries  "
        f"frac_changes_at_boundary={boundary_change_frac:.3f} "
        f"-> {'aligns' if changes_align_quires else 'does not align'}"
    )
    print(f"VERDICT={verdict}")
    print(f"caveat: {caveat}")
    print(f"runs_csv={args.out_runs}")
    print(f"alignment_csv={args.out_alignment}")
    print(f"summary_csv={args.out_summary}")
    print(f"md={args.md}")
    return 0


def write_report(
    path: Path,
    *,
    folios: list[dict[str, str]],
    n_folios: int,
    coverage: tuple[int, int, int, int],
    currier: tuple[int, int, int, float, float, float],
    hand: tuple[list[str], int, float, float, float] | None,
    alignment: tuple[float, float, int],
    quire: tuple[int, int, int, int, float],
    booleans: tuple[bool, bool],
    verdict: str,
    caveat: str,
) -> None:
    cov_L, cov_Q, cov_H, cov_I = coverage
    n_A, n_B, c_runs, c_mean_run, c_p, c_mean_null = currier
    v_sec_cur, v_hand_cur, n_regimes = alignment
    n_quires, n_change_at_boundary, n_boundaries, n_currier_changes, frac = quire
    currier_blocked, changes_align_quires = booleans
    lines = [
        "# Rota 68: codicologia do objeto — estrutura de PRODUÇÃO via metadados IVTFF",
        "",
        "Esta rota caracteriza COMO o códice foi FEITO (mãos, cadernos/quires, blocos",
        "Currier) a partir dos metadados por-fólio do IVTFF. É uma afirmação sobre o",
        "ARTEFATO físico — **nunca sobre sentido**.",
        f"Guardrail: `{GUARDRAIL}`.",
        "",
        "## Cobertura dos metadados",
        "",
        f"- n_folios = **{n_folios}**",
        f"- $L (Currier): {cov_L}/{n_folios} | $Q (quire): {cov_Q}/{n_folios} | "
        f"$H (mão): {cov_H}/{n_folios} | $I (seção): {cov_I}/{n_folios}",
        f"- Currier A = {n_A}, Currier B = {n_B}",
        "",
        "## [1] Contiguidade dos blocos Currier",
        "",
        f"Ordem canônica dos fólios; sequência de rótulos Currier ($L). "
        f"n_runs observados = **{c_runs}**, comprimento médio de bloco = "
        f"**{c_mean_run:.3f}** fólios.",
        "",
        f"Null de permutação ({N_PERM}× embaralhamentos): média de n_runs = "
        f"{c_mean_null:.2f}. p(n_runs ≤ observado) = **{c_p:.6f}**.",
        "",
        (
            f"→ Currier está **significativamente BLOCADO** (menos runs que o acaso, "
            f"p<0.05): o códice foi produzido em blocos contíguos de dialeto."
            if currier_blocked
            else "→ Currier **não** está significativamente blocado vs. o acaso."
        ),
        "",
    ]
    if hand is not None:
        hands, h_runs, h_mean_run, h_p, h_mean_null = hand
        lines += [
            "### Mãos (hand $H)",
            "",
            f"Mãos distintas: {hands}. n_runs = {h_runs}, comprimento médio = "
            f"{h_mean_run:.3f}, null mean = {h_mean_null:.2f}, p = {h_p:.6f}.",
            "",
        ]
    lines += [
        "## [2] Alinhamento seção × Currier × mão",
        "",
        f"- V(seção × Currier) = **{v_sec_cur:.4f}**",
        f"- V(mão × Currier) = **{v_hand_cur:.4f}**",
        f"- Regimes de produção (seção, Currier, mão) distintos efetivamente "
        f"ocorrendo = **{n_regimes}**",
        "",
        "## [3] Mapeamento de quires",
        "",
        f"- quires distintos = **{n_quires}**",
        f"- mudanças de Currier ao longo dos fólios = {n_currier_changes}",
        f"- fronteiras de quire = {n_boundaries}; mudanças de Currier QUE caem em "
        f"fronteira de quire = {n_change_at_boundary}",
        f"- fração de mudanças de Currier em fronteira de quire = **{frac:.3f}** → "
        f"{'alinham' if changes_align_quires else 'não alinham'} com as costuras",
        "",
        "## Veredito",
        "",
        f"**{verdict}**",
        "",
        f"(função pura dos booleanos: currier_blocked={currier_blocked}, "
        f"changes_align_quires={changes_align_quires})",
        "",
        "## Caveat (inviolável)",
        "",
        f"{caveat}. Seriedade de produção é consistente com AMBOS — um texto com "
        "sentido E um gerador sem conteúdo. Não decide a questão do sentido; não é "
        "uma decifração.",
        "",
        f"Guardrail: `{GUARDRAIL}`.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
