#!/usr/bin/env python3
"""Hand-campaign token signature: do paleographic HANDS carry a token-structural
norm BEYOND what Currier (language A/B) and section already explain?

EXTERNAL FRONT, leg B (the textual counterpart of "writing campaigns"). R68
characterised the OBJECT's production (hands/quires/Currier blocks) and found it
strongly BLOCKED (p=0.001), with V(hand x Currier)=0.98, 5 hands, interleaved
production. That tells us the codex was made deliberately; it does NOT tell us
whether each scribal HAND has its own *token* fingerprint, or whether "hand" is
simply the SAME partition as Currier wearing a different label.

FALSIFIABLE QUESTION:
  Do the writing "campaigns" (paleographic HANDS, $H) have a distinct STRUCTURAL
  token signature ABOVE AND BEYOND what Currier (A/B) already explains?
    - survives -> production in campaigns / scribes with distinct habits
      (consistent with team production; firms "serious artefact"; moves NO meaning).
    - collinear -> "hand" and "language" are the SAME partition relabelled
      (V(hand x Currier)=0.98 already hints at this); no new layer.

HAND ATTRIBUTION SOURCE -- REUSED EXACTLY FROM R68 (analyze_codicology):
  the IVTFF per-folio header tag `$H` (integer 1-5). We import
  parse_folio_metadata / hand_label / currier_label / section_label / cramer_v
  from scripts.analyze_codicology so the folio->hand map is byte-for-byte R68.
  Tokenisation reuses the analyze_nucleus mechanism: split a locus line on
  `[.\s]+`, then clean each raw token to bare EVA letters.

SIGNATURES MEASURED PER HAND (token-level):
  * h2  -- char conditional entropy H(c_i | c_{i-1}) with word boundaries,
           Miller-Madow bias-corrected; the per-group BIAS FLOOR is reported.
  * repeat_rate -- fraction of adjacent identical tokens (the daiin-daiin tic).
  * prefix mix  -- fraction of tokens starting qo- / ok- / ot- / yk- / yt-.
  * a/o-bit     -- among tokens with an {ar,al,or,ol} nucleus, fraction o-type.
  * token length-- mean char length.

THE DECISIVE CONTROL (the whole point):
  Build a hand x prefix-bucket contingency table and take Cramer's V. Then ask
  whether that hand structure SURVIVES (a) WITHIN a fixed Currier value and
  (b) WITHIN a fixed section. Significance is judged against a FOLIO-BLOCK
  permutation null (shuffle the per-folio hand labels among folios -- keeping each
  folio's tokens together -- and recompute V), restricted to the stratum's folios
  for the within-Currier / within-section tests. The null's mean V is the BIAS
  FLOOR for V under finite samples.

COLLINEARITY (to avoid a false positive): folio-level V(hand x Currier),
V(hand x section), V(Currier x section) -- if hand is near-perfectly collinear
with Currier, any "hand effect" is just Currier, and within a single Currier value
there are too few hands to show residual structure.

VERDICT (pure function of measured booleans):
  hand_campaign_signature_beyond_currier -- the hand x prefix V survives a
    within-Currier folio-block null in at least one testable stratum (>=2 hands).
  hand_collinear_with_currier -- V(hand x Currier) is near-perfect AND no
    within-Currier stratum shows residual hand structure beyond its null.
  hand_signature_unconfirmed -- otherwise.

This is evidence about PRODUCTION habits, never about meaning. CAVEAT in every
output: distinct scribal token habits are consistent with BOTH a meaningful text
AND a content-free generator -- they do NOT decide that question. Guardrail in
every CSV: rota72_hand_campaign_not_decipherment.
"""
from __future__ import annotations

import argparse
import collections
import csv
import math
import random
import re
from pathlib import Path

# --- REUSE R68's hand-attribution source exactly (the $H tag) + Cramer's V ----
from scripts.analyze_codicology import (  # noqa: E402
    build_folio_rows,
    cramer_v,
    currier_label,
    folio_sort_key,
    hand_label,
    parse_folio_metadata,
    section_label,
)

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota72_hand_campaign_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"

# Locus line: <fNNr.LOC,...> <TAB> transcription  (header lines have no '.').
_LOC = re.compile(r"^<(f[0-9]+[rv]\d?)\.\d+[^>]*>\s*(.*)$")

PREFIXES = ("qo", "ok", "ot", "yk", "yt")
PREFIX_BUCKETS = (*PREFIXES, "other")
LEN_BINS = ("1-2", "3-4", "5-6", "7+")

N_PERM = 1000
PERM_SEED = 72720
MIN_STRATUM_TOKENS = 200  # a within-Currier/section stratum is testable above this
COLLINEAR_THRESHOLD = 0.85  # V(hand x Currier) at/above this == "near-perfect"


# --------------------------------------------------------------------------- #
# Tokenisation (reuses the analyze_nucleus mechanism)                          #
# --------------------------------------------------------------------------- #
def clean_token(raw: str) -> str:
    """Normalise one raw IVTFF token to bare EVA letters.

    Resolves [a:b] alternate readings to the first option, strips inline comments
    {..}, markup <..>, locus weirdness @NNN;, then drops any non a-z character.
    Identical in spirit to analyze_nucleus.clean_token so token counts match the
    rest of the project.
    """
    raw = re.sub(r"\[([^:\]]*):[^\]]*\]", r"\1", raw)  # [cth:oto] -> cth
    raw = re.sub(r"\{[^}]*\}", "", raw)
    raw = re.sub(r"<[^>]*>", "", raw)
    raw = re.sub(r"@\d+;?", "", raw)
    return re.sub(r"[^a-z]", "", raw.lower())


def parse_folio_tokens(path: Path) -> dict[str, list[str]]:
    """Return {folio -> [clean_token, ...]} preserving in-line token order.

    Only locus lines contribute tokens; header lines carry the metadata parsed
    separately by parse_folio_metadata (the R68 hand source).
    """
    by_folio: dict[str, list[str]] = collections.defaultdict(list)
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        m = _LOC.match(raw_line)
        if not m:
            continue
        folio, text = m.group(1), m.group(2)
        for raw in re.split(r"[.\s]+", text):
            tok = clean_token(raw)
            if tok:
                by_folio[folio].append(tok)
    return dict(by_folio)


# --------------------------------------------------------------------------- #
# Per-token classifiers                                                        #
# --------------------------------------------------------------------------- #
def prefix_bucket(token: str) -> str:
    """The qo-/ok-/ot-/yk-/yt- prefix bucket of a token, else 'other'."""
    for p in PREFIXES:
        if token.startswith(p):
            return p
    return "other"


def length_bin(token: str) -> str:
    """Coarse character-length bin for a token."""
    n = len(token)
    if n <= 2:
        return "1-2"
    if n <= 4:
        return "3-4"
    if n <= 6:
        return "5-6"
    return "7+"


def ao_nucleus_count(token: str) -> tuple[int, int]:
    """Count (a, o) occurrences in the matrix nucleus slot {ar,al,or,ol}.

    Returns (n_a, n_o): how many times an 'a' resp. 'o' immediately precedes an
    r/l in the token. This is the project's a/o matrix axis, applied uniformly.
    """
    n_a = n_o = 0
    for i in range(len(token) - 1):
        if token[i + 1] in "rl":
            if token[i] == "a":
                n_a += 1
            elif token[i] == "o":
                n_o += 1
    return n_a, n_o


# --------------------------------------------------------------------------- #
# Entropy with Miller-Madow bias correction                                    #
# --------------------------------------------------------------------------- #
def _entropy_mm(counts: "collections.Counter") -> tuple[float, float, int, int]:
    """Plugin and Miller-Madow entropy (bits) of a count distribution.

    Returns (h_plugin, h_mm, support_K, N). MM adds (K-1)/(2N) where K is the
    number of observed outcomes with positive count -- the standard small-sample
    correction.
    """
    n = sum(counts.values())
    if n == 0:
        return 0.0, 0.0, 0, 0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / n
            h -= p * math.log2(p)
    k = sum(1 for c in counts.values() if c > 0)
    h_mm = h + (k - 1) / (2 * n)
    return h, h_mm, k, n


def char_h2(tokens: list[str]) -> tuple[float, float, float]:
    """Conditional char entropy H(c_i | c_{i-1}) over the token stream.

    Tokens are joined by a boundary symbol ' ' so word edges are modelled. Both
    plugin and Miller-Madow estimates are returned, plus the BIAS FLOOR
    (h_plugin - h_mm of the conditional, i.e. the MM correction magnitude), so the
    floor of the estimator is explicit. Conditional entropy is computed as
    H(X,Y) - H(X), each MM-corrected.
    """
    if not tokens:
        return 0.0, 0.0, 0.0
    seq = " ".join(tokens)
    joint: "collections.Counter[tuple[str, str]]" = collections.Counter()
    marg: "collections.Counter[str]" = collections.Counter()
    prev = " "
    for ch in seq + " ":
        joint[(prev, ch)] += 1
        marg[prev] += 1
        prev = ch
    _, hxy_mm, _, _ = _entropy_mm(joint)
    hxy_plug, _, _, _ = _entropy_mm(joint)
    _, hx_mm, _, _ = _entropy_mm(marg)
    hx_plug, _, _, _ = _entropy_mm(marg)
    h2_mm = hxy_mm - hx_mm
    h2_plug = hxy_plug - hx_plug
    bias_floor = h2_plug - h2_mm  # MM correction magnitude for the conditional
    return h2_plug, h2_mm, bias_floor


def repeat_rate(tokens: list[str]) -> float:
    """Fraction of adjacent token pairs that are identical."""
    if len(tokens) < 2:
        return 0.0
    same = sum(1 for a, b in zip(tokens, tokens[1:]) if a == b)
    return same / (len(tokens) - 1)


# --------------------------------------------------------------------------- #
# Group signature                                                             #
# --------------------------------------------------------------------------- #
def group_signature(tokens: list[str]) -> dict[str, float]:
    """All scalar signature metrics for one bag of tokens."""
    n = len(tokens)
    h2_plug, h2_mm, floor = char_h2(tokens)
    pref = collections.Counter(prefix_bucket(t) for t in tokens)
    na = no = 0
    for t in tokens:
        a, o = ao_nucleus_count(t)
        na += a
        no += o
    sig: dict[str, float] = {
        "n_tokens": float(n),
        "h2_plugin": h2_plug,
        "h2_mm": h2_mm,
        "bias_floor": floor,
        "repeat_rate": repeat_rate(tokens),
        "ao_o_frac": (no / (na + no)) if (na + no) else 0.0,
        "n_ao_tokens": float(na + no),
        "mean_len": (sum(len(t) for t in tokens) / n) if n else 0.0,
    }
    for p in PREFIX_BUCKETS:
        sig[f"frac_{p}"] = (pref.get(p, 0) / n) if n else 0.0
    return sig


# --------------------------------------------------------------------------- #
# Contingency V over a token-classifier, with a folio-block permutation null   #
# --------------------------------------------------------------------------- #
def _table_from_assignment(
    folio_hand: dict[str, str],
    folio_tokens: dict[str, list[str]],
    folios: list[str],
    classify,
) -> dict[str, "collections.Counter[str]"]:
    """hand -> Counter(bucket) built by attributing each folio's tokens to its
    (possibly permuted) hand label."""
    tab: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for f in folios:
        h = folio_hand[f]
        for t in folio_tokens.get(f, ()):
            tab[h][classify(t)] += 1
    return {k: v for k, v in tab.items()}


def folio_block_v(
    folio_hand: dict[str, str],
    folio_tokens: dict[str, list[str]],
    folios: list[str],
    classify,
    n_perm: int,
    seed: int,
) -> tuple[float, float, float, int]:
    """Observed Cramer's V(hand x classifier) and its folio-block permutation null.

    The null SHUFFLES the per-folio hand labels among the given folios (each
    folio's whole token bag travels with the shuffled label), recomputing V each
    time. This respects the folio block structure (within-folio autocorrelation)
    and asks only whether the hand->token-shape link is real beyond folio
    clustering. Returns (v_obs, v_null_mean, p, n_hands) where p = (#null >= obs +
    1)/(n_perm + 1) and v_null_mean is the finite-sample BIAS FLOOR of V.
    """
    hands_present = {folio_hand[f] for f in folios}
    obs_tab = _table_from_assignment(folio_hand, folio_tokens, folios, classify)
    v_obs, _ = cramer_v(obs_tab)
    if len(hands_present) < 2 or len(folios) < 2:
        return v_obs, v_obs, 1.0, len(hands_present)
    labels = [folio_hand[f] for f in folios]
    rng = random.Random(seed)
    ge = 1
    total = v_obs
    for _ in range(n_perm):
        rng.shuffle(labels)
        perm_hand = {f: labels[i] for i, f in enumerate(folios)}
        tab = _table_from_assignment(perm_hand, folio_tokens, folios, classify)
        v, _ = cramer_v(tab)
        total += v
        if v >= v_obs:
            ge += 1
    p = ge / (n_perm + 1)
    v_null_mean = total / (n_perm + 1)
    return v_obs, v_null_mean, p, len(hands_present)


# --------------------------------------------------------------------------- #
# Verdict (pure function of measured booleans)                                 #
# --------------------------------------------------------------------------- #
def classify_verdict(
    double_tested: bool, double_survives: bool, v_hand_currier: float
) -> str:
    """Pure-function verdict from the DOUBLE-control booleans.

    The decisive control fixes BOTH Currier AND section (a Currier x section cell
    with >=2 hands and enough tokens) and asks whether hand x prefix V still beats
    the folio-block null. This rejects the failure mode where within-Currier hand
    structure is merely carrying SECTION (within Currier A, hand is perfectly
    collinear with section).

    hand_campaign_signature_beyond_currier requires that at least one Currier x
    section cell was TESTABLE (double_tested) AND its hand effect survived its
    folio-block null (double_survives). If hand is near-perfectly collinear with
    Currier and nothing survives the double control, the verdict is
    hand_collinear_with_currier; anything else is unconfirmed.
    """
    if double_tested and double_survives:
        return "hand_campaign_signature_beyond_currier"
    if v_hand_currier >= COLLINEAR_THRESHOLD and not double_survives:
        return "hand_collinear_with_currier"
    return "hand_signature_unconfirmed"


# --------------------------------------------------------------------------- #
# Campaign-boundary contrast (interleaved production seams, R68)               #
# --------------------------------------------------------------------------- #
def _prefix_dist(tokens: list[str]) -> dict[str, float]:
    n = len(tokens)
    c = collections.Counter(prefix_bucket(t) for t in tokens)
    return {b: (c.get(b, 0) / n if n else 0.0) for b in PREFIX_BUCKETS}


def _tv_distance(d1: dict[str, float], d2: dict[str, float]) -> float:
    """Total-variation distance between two prefix distributions."""
    return 0.5 * sum(abs(d1[b] - d2[b]) for b in PREFIX_BUCKETS)


def campaign_boundary_contrast(
    folio_rows: list[dict[str, str]], folio_tokens: dict[str, list[str]]
) -> dict[str, float]:
    """Does the prefix signature jump at hand-change seams within a quire?

    Walk the canonically-ordered folios. A "campaign seam" is an adjacent pair in
    the SAME quire whose hand differs (interleaved production, per R68). Compare
    the mean TV distance of the prefix distribution across campaign seams vs across
    same-hand adjacent pairs (a within-hand baseline). Returns counts and the two
    mean distances; if the seam mean exceeds the baseline the signature does shift
    at the campaign boundary.
    """
    seam_d: list[float] = []
    base_d: list[float] = []
    n_seams = 0
    for prev, cur in zip(folio_rows, folio_rows[1:]):
        pq, cq = prev.get("quire", "?"), cur.get("quire", "?")
        ph, ch = prev["hand"], cur["hand"]
        if ph == "unknown" or ch == "unknown":
            continue
        tp = folio_tokens.get(prev["folio"], [])
        tc = folio_tokens.get(cur["folio"], [])
        if not tp or not tc:
            continue
        d = _tv_distance(_prefix_dist(tp), _prefix_dist(tc))
        same_quire = pq == cq and pq != "?" and cq != "?"
        if ph != ch and same_quire:
            seam_d.append(d)
            n_seams += 1
        elif ph == ch:
            base_d.append(d)
    return {
        "n_campaign_seams": float(n_seams),
        "n_same_hand_pairs": float(len(base_d)),
        "mean_tv_at_seam": (sum(seam_d) / len(seam_d)) if seam_d else 0.0,
        "mean_tv_same_hand": (sum(base_d) / len(base_d)) if base_d else 0.0,
    }


# --------------------------------------------------------------------------- #
# IO                                                                           #
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
    p.add_argument("--n-perm", type=int, default=N_PERM)
    p.add_argument("--seed", type=int, default=PERM_SEED)
    d = ROOT / "data" / "derived"
    p.add_argument("--out-metrics", default=str(d / "hand_campaign_metrics_zl3b.csv"))
    p.add_argument("--out-summary", default=str(d / "hand_campaign_summary_zl3b.csv"))
    return p.parse_args(argv)


# --------------------------------------------------------------------------- #
# Main                                                                         #
# --------------------------------------------------------------------------- #
def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    corpus = Path(args.corpus)

    meta = parse_folio_metadata(corpus)
    folio_rows = build_folio_rows(meta)  # canonical order, R68 labels
    folio_tokens = parse_folio_tokens(corpus)

    # folio -> labels (R68 source)
    folio_hand = {r["folio"]: r["hand"] for r in folio_rows}
    folio_currier = {r["folio"]: r["currier"] for r in folio_rows}
    folio_section = {r["folio"]: r["section"] for r in folio_rows}

    # folios that actually carry tokens AND a known hand
    folios_hand = [
        f for f in folio_hand if folio_hand[f] != "unknown" and folio_tokens.get(f)
    ]

    # -- collinearity (folio-level, anchors R68's V(hand x Currier)=0.98) --
    def folio_v(a: str, b: str) -> float:
        tab: dict[str, collections.Counter] = collections.defaultdict(
            collections.Counter
        )
        for r in folio_rows:
            av, bv = r[a], r[b]
            if av == "unknown" or bv == "unknown":
                continue
            tab[av][bv] += 1
        v, _ = cramer_v({k: v for k, v in tab.items()})
        return v

    v_hand_currier = folio_v("hand", "currier")
    v_hand_section = folio_v("hand", "section")
    v_currier_section = folio_v("currier", "section")

    # -- headline token signature: hand x prefix, with folio-block null --
    v_pref_all, v_pref_all_null, p_pref_all, n_hands_all = folio_block_v(
        folio_hand, folio_tokens, folios_hand, prefix_bucket, args.n_perm, args.seed
    )
    # secondary token signatures (length, a/o) overall
    v_len_all, v_len_null, p_len_all, _ = folio_block_v(
        folio_hand, folio_tokens, folios_hand, length_bin, args.n_perm, args.seed + 7
    )
    v_ao_all, v_ao_null, p_ao_all, _ = folio_block_v(
        folio_hand,
        folio_tokens,
        folios_hand,
        lambda t: "o" if ao_nucleus_count(t)[1] > ao_nucleus_count(t)[0] else "a",
        args.n_perm,
        args.seed + 13,
    )

    # -- within-Currier control (the decisive test) --
    within_currier: list[dict] = []
    within_tested = False
    within_survives = False
    for c in ("A", "B"):
        fs = [f for f in folios_hand if folio_currier[f] == c]
        n_tok = sum(len(folio_tokens[f]) for f in fs)
        hands_here = sorted({folio_hand[f] for f in fs})
        testable = len(hands_here) >= 2 and n_tok >= MIN_STRATUM_TOKENS
        if len(hands_here) >= 2:
            v, vnull, p, nh = folio_block_v(
                folio_hand, folio_tokens, fs, prefix_bucket, args.n_perm,
                args.seed + 100 + ord(c),
            )
        else:
            v = vnull = 0.0
            p = 1.0
            nh = len(hands_here)
        survives = testable and p < 0.05 and v > vnull
        if testable:
            within_tested = True
        if survives:
            within_survives = True
        within_currier.append(
            {
                "stratum": f"currier={c}",
                "n_folios": len(fs),
                "n_tokens": n_tok,
                "n_hands": nh,
                "hands": "|".join(hands_here),
                "v_hand_prefix": round(v, 4),
                "v_null_mean": round(vnull, 4),
                "p_vs_null": round(p, 6),
                "testable": testable,
                "survives": survives,
            }
        )

    # -- within-section control (secondary) --
    within_section: list[dict] = []
    sections = sorted({folio_section[f] for f in folios_hand if folio_section[f] != "unknown"})
    section_survives = False
    section_tested = False
    for s in sections:
        fs = [f for f in folios_hand if folio_section[f] == s]
        n_tok = sum(len(folio_tokens[f]) for f in fs)
        hands_here = sorted({folio_hand[f] for f in fs})
        testable = len(hands_here) >= 2 and n_tok >= MIN_STRATUM_TOKENS
        if len(hands_here) >= 2:
            v, vnull, p, nh = folio_block_v(
                folio_hand, folio_tokens, fs, prefix_bucket, args.n_perm,
                args.seed + 200 + abs(hash(s)) % 997,
            )
        else:
            v = vnull = 0.0
            p = 1.0
            nh = len(hands_here)
        survives = testable and p < 0.05 and v > vnull
        if testable:
            section_tested = True
        if survives:
            section_survives = True
        within_section.append(
            {
                "stratum": f"section={s}",
                "n_folios": len(fs),
                "n_tokens": n_tok,
                "n_hands": nh,
                "hands": "|".join(hands_here),
                "v_hand_prefix": round(v, 4),
                "v_null_mean": round(vnull, 4),
                "p_vs_null": round(p, 6),
                "testable": testable,
                "survives": survives,
            }
        )

    # -- DECISIVE double control: within (Currier x section) cells --
    # Fix BOTH Currier and section; a cell with >=2 hands and enough tokens isolates
    # the hand effect from section AND from Currier. This is the verdict driver.
    within_cell: list[dict] = []
    cells: dict[tuple[str, str], list[str]] = collections.defaultdict(list)
    for f in folios_hand:
        cells[(folio_currier[f], folio_section[f])].append(f)
    double_tested = False
    double_survives = False
    for (c, s), fs in sorted(cells.items()):
        if c == "unknown" or s == "unknown":
            continue
        n_tok = sum(len(folio_tokens[f]) for f in fs)
        hands_here = sorted({folio_hand[f] for f in fs})
        testable = len(hands_here) >= 2 and n_tok >= MIN_STRATUM_TOKENS
        if len(hands_here) >= 2:
            v, vnull, p, nh = folio_block_v(
                folio_hand, folio_tokens, fs, prefix_bucket, args.n_perm,
                args.seed + 300 + abs(hash((c, s))) % 997,
            )
        else:
            v = vnull = 0.0
            p = 1.0
            nh = len(hands_here)
        survives = testable and p < 0.05 and v > vnull
        if testable:
            double_tested = True
        if survives:
            double_survives = True
        within_cell.append(
            {
                "stratum": f"currier={c},section={s}",
                "n_folios": len(fs),
                "n_tokens": n_tok,
                "n_hands": nh,
                "hands": "|".join(hands_here),
                "v_hand_prefix": round(v, 4),
                "v_null_mean": round(vnull, 4),
                "p_vs_null": round(p, 6),
                "testable": testable,
                "survives": survives,
            }
        )

    # -- campaign-boundary contrast --
    boundary = campaign_boundary_contrast(folio_rows, folio_tokens)

    # -- verdict (driven by the DOUBLE control: hand beyond Currier AND section) --
    verdict = classify_verdict(double_tested, double_survives, v_hand_currier)

    # -- per-hand metric table (overall + per-Currier strata) --
    metric_rows: list[dict] = []
    metric_fields = [
        "stratum", "hand", "n_tokens", "h2_plugin", "h2_mm", "bias_floor",
        "repeat_rate", "ao_o_frac", "n_ao_tokens", "mean_len",
        *[f"frac_{p}" for p in PREFIX_BUCKETS], "semantic_guardrail",
    ]

    def emit_group(stratum: str, hand: str, tokens: list[str]) -> None:
        sig = group_signature(tokens)
        row = {"stratum": stratum, "hand": hand}
        for k, v in sig.items():
            row[k] = round(v, 6) if isinstance(v, float) else v
        row["semantic_guardrail"] = GUARDRAIL
        metric_rows.append(row)

    hands_sorted = sorted({folio_hand[f] for f in folios_hand})
    for h in hands_sorted:
        toks: list[str] = []
        for f in folios_hand:
            if folio_hand[f] == h:
                toks += folio_tokens[f]
        emit_group("all", h, toks)
    for c in ("A", "B"):
        for h in hands_sorted:
            toks = []
            for f in folios_hand:
                if folio_currier[f] == c and folio_hand[f] == h:
                    toks += folio_tokens[f]
            if toks:
                emit_group(f"currier={c}", h, toks)
    write_csv(Path(args.out_metrics), metric_rows, metric_fields)

    # -- summary table --
    caveat = (
        "measures scribal PRODUCTION habits per hand (the $H tag from R68); says "
        "NOTHING about meaning. Distinct hand habits are consistent with BOTH a "
        "meaningful text AND a content-free generator."
    )
    n_tokens_total = sum(len(v) for v in folio_tokens.values())
    summary_rows = [
        {"metric": "n_folios_with_hand_and_text", "value": str(len(folios_hand))},
        {"metric": "n_tokens_total", "value": str(n_tokens_total)},
        {"metric": "n_hands", "value": str(len(hands_sorted))},
        {"metric": "hands", "value": "|".join(hands_sorted)},
        # collinearity (folio-level)
        {"metric": "V_hand_currier_folio", "value": str(round(v_hand_currier, 4))},
        {"metric": "V_hand_section_folio", "value": str(round(v_hand_section, 4))},
        {"metric": "V_currier_section_folio", "value": str(round(v_currier_section, 4))},
        # headline token signature, overall, vs folio-block null
        {"metric": "V_hand_prefix_all", "value": str(round(v_pref_all, 4))},
        {"metric": "V_hand_prefix_all_null", "value": str(round(v_pref_all_null, 4))},
        {"metric": "V_hand_prefix_all_p", "value": str(round(p_pref_all, 6))},
        {"metric": "V_hand_length_all", "value": str(round(v_len_all, 4))},
        {"metric": "V_hand_length_all_null", "value": str(round(v_len_null, 4))},
        {"metric": "V_hand_length_all_p", "value": str(round(p_len_all, 6))},
        {"metric": "V_hand_ao_all", "value": str(round(v_ao_all, 4))},
        {"metric": "V_hand_ao_all_null", "value": str(round(v_ao_null, 4))},
        {"metric": "V_hand_ao_all_p", "value": str(round(p_ao_all, 6))},
        # decisive controls
        {"metric": "within_currier_tested", "value": str(within_tested)},
        {"metric": "within_currier_survives", "value": str(within_survives)},
        {"metric": "within_section_tested", "value": str(section_tested)},
        {"metric": "within_section_survives", "value": str(section_survives)},
        # DECISIVE double control (within Currier x section)
        {"metric": "within_currier_section_tested", "value": str(double_tested)},
        {"metric": "within_currier_section_survives", "value": str(double_survives)},
        # campaign boundary
        {"metric": "n_campaign_seams", "value": str(int(boundary["n_campaign_seams"]))},
        {"metric": "mean_tv_at_seam", "value": str(round(boundary["mean_tv_at_seam"], 4))},
        {"metric": "mean_tv_same_hand", "value": str(round(boundary["mean_tv_same_hand"], 4))},
        # verdict
        {"metric": "verdict", "value": verdict},
        {"metric": "caveat", "value": caveat},
        {"metric": "guardrail", "value": GUARDRAIL},
    ]
    # append per-stratum control rows for auditability
    for r in within_currier + within_section + within_cell:
        summary_rows.append(
            {
                "metric": f"control[{r['stratum']}]",
                "value": (
                    f"hands={r['hands']} n_tokens={r['n_tokens']} "
                    f"V={r['v_hand_prefix']} null={r['v_null_mean']} "
                    f"p={r['p_vs_null']} testable={r['testable']} "
                    f"survives={r['survives']}"
                ),
            }
        )
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    # -- console report (mechanical) --
    print(f"n_folios_with_hand_and_text={len(folios_hand)} n_tokens={n_tokens_total} "
          f"n_hands={len(hands_sorted)} hands={hands_sorted}")
    print("[collinearity, folio-level]")
    print(f"  V(hand x Currier)={v_hand_currier:.4f}  "
          f"V(hand x section)={v_hand_section:.4f}  "
          f"V(Currier x section)={v_currier_section:.4f}")
    print("[headline token signature -- hand x prefix, folio-block null]")
    print(f"  V_obs={v_pref_all:.4f}  null_mean(bias_floor)={v_pref_all_null:.4f}  "
          f"p={p_pref_all:.6f}  n_hands={n_hands_all}")
    print(f"  length: V={v_len_all:.4f} null={v_len_null:.4f} p={p_len_all:.6f}")
    print(f"  a/o:    V={v_ao_all:.4f} null={v_ao_null:.4f} p={p_ao_all:.6f}")
    print("[within-Currier control (decisive)]")
    for r in within_currier:
        print(f"  {r['stratum']}: hands={r['hands']} n_tok={r['n_tokens']} "
              f"V={r['v_hand_prefix']} null={r['v_null_mean']} p={r['p_vs_null']} "
              f"testable={r['testable']} survives={r['survives']}")
    print("[within-section control]")
    for r in within_section:
        print(f"  {r['stratum']}: hands={r['hands']} n_tok={r['n_tokens']} "
              f"V={r['v_hand_prefix']} null={r['v_null_mean']} p={r['p_vs_null']} "
              f"testable={r['testable']} survives={r['survives']}")
    print("[DECISIVE double control -- within (Currier x section) cells]")
    for r in within_cell:
        if r["n_hands"] >= 2:
            print(f"  {r['stratum']}: hands={r['hands']} n_tok={r['n_tokens']} "
                  f"V={r['v_hand_prefix']} null={r['v_null_mean']} p={r['p_vs_null']} "
                  f"testable={r['testable']} survives={r['survives']}")
    print(f"  -> double_tested={double_tested} double_survives={double_survives}")
    print("[campaign-boundary contrast (interleaved seams within a quire)]")
    print(f"  n_seams={int(boundary['n_campaign_seams'])} "
          f"mean_TV_at_seam={boundary['mean_tv_at_seam']:.4f} "
          f"mean_TV_same_hand={boundary['mean_tv_same_hand']:.4f}")
    print(f"VERDICT={verdict}")
    print(f"caveat: {caveat}")
    print(f"metrics_csv={args.out_metrics}")
    print(f"summary_csv={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
