#!/usr/bin/env python3
"""Rota 66: mechanize the EXTERNAL-THESIS ATTACK MATRIX and VALIDATE it against
the R62 generator's OWN output (non-circular).

This route does NOT invent a new statistical test. R62 proved the token-scale
battery is DEGENERATE: a simple local CONTENTLESS generator reproduces 13/14 of
Voynich's measured signatures, so "designed-with-meaning" and "content-free
generator" are indistinguishable by corpus statistics -- with ONE exception, the
line-as-a-functional-unit binding I(word;line-position) = laafu_I, which the real
corpus carries at 0.471 but the generator under-shoots at 0.303. That single
gap is the ONLY corpus signature that beats the content-free generator.

What this script does instead is FORMALIZE the team's pre-registered decision
rule over every external thesis that has ever been levelled at the manuscript,
and CROSS-CHECK each thesis's verdict against the generator's actual numbers so
the matrix is grounded, not asserted. It emits two CSVs (the per-thesis matrix
and a summary) and prints a console report.

THE NON-CIRCULAR LINK (the heart of this route)
-----------------------------------------------
The script READS the R62 generator's own outputs to ground the comparison; it
does NOT hardcode which signatures the generator reproduces or resists:

  * data/derived/generator_summary_zl3b.csv -> the RESISTING_SET (the key metrics
    the generator could NOT match: {laafu_I}), n_metrics (14), n_matched (13).
  * data/derived/generator_match_zl3b.csv   -> the laafu_I row's real (0.471),
    generator (0.303) and the gap (~0.168) -- the quantitative anchor.

The consistency invariant `signal_class == "resists_generator" =>
discriminating_signal in RESISTING_SET` is then checked against THAT loaded set,
so a thesis may only claim to "resist the generator" on a signature the
generator's own output confirms it failed to reproduce. That is the non-circular
check: the matrix cannot self-certify a discriminator the instrument didn't earn.

THE DECISION RULE (per thesis)
------------------------------
Each thesis is labelled with a controlled `signal_class` (what its discriminating
signal does against the corpus + generator). Two booleans are COMPUTED from that
class (never hardcoded):

  * beats_generator      = signal_class in {resists_generator, not_yet_measured}
  * refuted_by_instrument = signal_class == contradicted_by_corpus

and a `verdict` in {refuted, unsupported, survives_weakly, actionable,
external_only}. Runtime ASSERTIONS (mirrored in the tests) enforce:

  * refuted_by_instrument  <=>  verdict == refuted
  * beats_generator        <=>  verdict == actionable
  * resists_generator      =>   discriminating_signal in RESISTING_SET (the
                                non-circular check, set read from the generator CSV)
  * every verdict is one of the five allowed; every row carries the guardrail.

GOLDEN RULE
-----------
This script encodes/validates verdicts about STRUCTURE; it NEVER emits a
translation or assigns meaning to any token. The `external_residual` column names
what each thesis would still need (a key, a sibling text, provenance) -- it is the
honest statement of what corpus statistics provably cannot touch (the ~22% prior),
not a claim of meaning. The constant NO_TRANSLATION_CLAIM records this contract
and a guard checks no verdict/headline cell asserts meaning.
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota66_external_thesis_attack_not_decipherment"

DEFAULT_GEN_SUMMARY = ROOT / "data" / "derived" / "generator_summary_zl3b.csv"
DEFAULT_GEN_MATCH = ROOT / "data" / "derived" / "generator_match_zl3b.csv"

# The script makes NO translation claim. Every corpus_result / headline is about
# STRUCTURE (entropy, mutual information, line-position binding, compressibility),
# never about what a token "means" or "translates to". This constant is the
# machine-checkable contract; the test (h) asserts these banned words never appear
# in a verdict or headline field.
NO_TRANSLATION_CLAIM = "rota66 validates STRUCTURE verdicts; it never emits a translation or meaning"
_BANNED_MEANING_SUBSTRINGS = ("means", "translates to")

# --------------------------------------------------------------------------- #
# Controlled vocabulary                                                       #
# --------------------------------------------------------------------------- #
# The 13 signatures the R62 content-free generator REPRODUCES. Predicting only
# these is degenerate -- it is exactly what the generator does by construction.
GENERATOR_REPRODUCED = (
    "char_h2",
    "adjacent_repeat",
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
    "order_gain",
)

# Allowed signal classes (what a thesis's discriminating signal does).
SIGNAL_CLASSES = (
    "reproduced_by_generator",
    "resists_generator",
    "not_yet_measured",
    "contradicted_by_corpus",
    "confirmed_structure_absorbed",
    "is_the_generator",
)

# Allowed verdicts.
VERDICTS = (
    "refuted",
    "unsupported",
    "survives_weakly",
    "actionable",
    "external_only",
)


def beats_generator(signal_class: str) -> bool:
    """A thesis BEATS the content-free generator iff its discriminating signal is
    one the generator cannot reproduce (it resists it) or has simply not yet been
    measured against the generator. Both are the only ways to escape the R62
    degeneracy. COMPUTED from the class -- never hardcoded per thesis."""
    return signal_class in {"resists_generator", "not_yet_measured"}


def refuted_by_instrument(signal_class: str) -> bool:
    """A thesis is REFUTED BY THE INSTRUMENT iff the corpus itself contradicts its
    discriminating signal (the measurement points the other way). COMPUTED."""
    return signal_class == "contradicted_by_corpus"


# --------------------------------------------------------------------------- #
# The 13-thesis attack matrix (verbatim data table, id order)                 #
# --------------------------------------------------------------------------- #
# Each entry is the pre-registered team position on one external thesis. Columns:
#   thesis_id, thesis_name, proponent, predicted_signals, discriminating_signal,
#   signal_class, mapped_routes, corpus_result, controls_applied, verdict,
#   external_residual.
# beats_generator / refuted_by_instrument are COMPUTED at build time, not stored.
THESES: list[dict] = [
    {
        "thesis_id": 1,
        "thesis_name": "Direct natural language",
        "proponent": "classic",
        "predicted_signals": "char_h2~2.5-3.6;midrange_MI>0;order_gain~12-25%;adjacent_repeat<0.25%",
        "discriminating_signal": "midrange_MI",
        "signal_class": "contradicted_by_corpus",
        "mapped_routes": "R58,R59,R60,R62",
        "corpus_result": "h2=2.15 below natural; MI floor at d~15, no midrange; order_gain 1-3%",
        "controls_applied": "char_h2,line_position,second_compressor",
        "verdict": "refuted",
        "external_residual": "none",
    },
    {
        "thesis_id": 2,
        "thesis_name": "Simple substitution / lost alphabet",
        "proponent": "classic",
        "predicted_signals": "char_h2~source(2.5-3.6);midrange_MI>0;order_gain~12-25%",
        "discriminating_signal": "char_h2",
        "signal_class": "contradicted_by_corpus",
        "mapped_routes": "R58,R59,R60",
        "corpus_result": "bijection preserves source entropy; h2=2.15 below any natural source",
        "controls_applied": "char_h2,second_compressor",
        "verdict": "refuted",
        "external_residual": "none",
    },
    {
        "thesis_id": 3,
        "thesis_name": "Homophonic / verbose cipher",
        "proponent": "classic expansion",
        "predicted_signals": "char_h2 low(ok);adjacent_repeat up(ok);recoverable sub-token syntax revives on re-segmentation in BOTH compressors",
        "discriminating_signal": "bpe_resegment_gain",
        "signal_class": "contradicted_by_corpus",
        "mapped_routes": "R61,R60",
        "corpus_result": "lzma diff 0.035 collapses to bz2 0.005 = lzma_artifact; no recoverable sub-token syntax",
        "controls_applied": "second_compressor,prefix_suffix",
        "verdict": "refuted",
        "external_residual": "signature-free verbose cipher leaves no statistical trace -> external_only, no positive support",
    },
    {
        "thesis_id": 4,
        "thesis_name": "Cardan grille / Rugg / Zandbergen",
        "proponent": "Rugg 2004 (Cardano 1550s)",
        "predicted_signals": "exactly the R62 13-signature panel (mechanical table/grille output)",
        "discriminating_signal": "none",
        "signal_class": "reproduced_by_generator",
        "mapped_routes": "R62",
        "corpus_result": "reproduces 13/14 by construction; predicts no per-token laafu table",
        "controls_applied": "comparison_vs_R62",
        "verdict": "unsupported",
        "external_residual": "period-intent anachronistic (Cardano grille 1550s post-dates vellum 1404-1438); a table/grille artifact or workshop record would be external evidence",
    },
    {
        "thesis_id": 5,
        "thesis_name": "Naibbe cipher",
        "proponent": "Greshko 2024",
        "predicted_signals": "char_h2 low(ok);nulls->adjacent_repeat(ok);recoverable plaintext order once multi-glyph groups undone",
        "discriminating_signal": "bpe_resegment_gain",
        "signal_class": "contradicted_by_corpus",
        "mapped_routes": "R61,R60",
        "corpus_result": "BPE re-grouping does NOT revive order beyond structure-matched controls (bz2 collapse)",
        "controls_applied": "second_compressor",
        "verdict": "refuted",
        "external_residual": "modern reconstruction; period attestation or worked sibling text is external_only",
    },
    {
        "thesis_id": 6,
        "thesis_name": "Self-citation / Timm-Schinner",
        "proponent": "Timm & Schinner 2019",
        "predicted_signals": "adjacent_repeat~0.875%(ok);short-range MI only;floor by d~15(ok)",
        "discriminating_signal": "none",
        "signal_class": "reproduced_by_generator",
        "mapped_routes": "R62,R58",
        "corpus_result": "IS generator mechanism #3 (self_citation p_rep=0.0046); ablation reproduces 0.875%",
        "controls_applied": "comparison_vs_R62",
        "verdict": "unsupported",
        "external_residual": "none",
    },
    {
        "thesis_id": 7,
        "thesis_name": "Topic modeling",
        "proponent": "Bowern/Sterneck/Polish",
        "predicted_signals": "topical_word_MI>0(ok, I_norm=0.046);if real-language: referential coupling",
        "discriminating_signal": "topical_word_MI",
        "signal_class": "reproduced_by_generator",
        "mapped_routes": "R56,R57,R62",
        "corpus_result": "topical signal real but reproduced by generator section_cond table; R57 shows it is prose-register, NON-referential",
        "controls_applied": "folio_block,Currier,within_folio",
        "verdict": "survives_weakly",
        "external_residual": "real-language identity claim (e.g. Polish) and referential reading (R57 refutes) -> external_only",
    },
    {
        "thesis_id": 8,
        "thesis_name": "Currier A/B as scribe/dialect/mode",
        "proponent": "Currier 1976",
        "predicted_signals": "currier_ao V high~0.45(ok);a/o tracks scribe>section(ok)",
        "discriminating_signal": "currier_ao",
        "signal_class": "confirmed_structure_absorbed",
        "mapped_routes": "R45,R47",
        "corpus_result": "V(Currier x a/o)=0.45 confirmed, Currier(0.44)>section(0.25); real axis, absorbable as a generator mode/section switch",
        "controls_applied": "Currier,section",
        "verdict": "survives_weakly",
        "external_residual": "hand-vs-dialect-vs-mode NATURE resolvable only by external hand/ink paleography (ductus, ink, quire mapping)",
    },
    {
        "thesis_id": 9,
        "thesis_name": "Parisel: positional restrictions, directional layers, Currier switch",
        "proponent": "Parisel",
        "predicted_signals": "laafu_I HIGH (token<->line-position binding, real 0.471);radial_paragraph_register(ok);Currier as switch(ok)",
        "discriminating_signal": "laafu_I",
        "signal_class": "resists_generator",
        "mapped_routes": "R62,R65a,R47",
        "corpus_result": "laafu_I=0.471 real > gen 0.303 (delta~0.168) = the ONE signature beyond the content-free generator; radial!=paragraph V_within=0.217 p=0.0005",
        "controls_applied": "line_position,within_folio,Currier",
        "verdict": "actionable",
        "external_residual": "switch-NATURE external_only; per R62/R65a the residual likely reduces to a richer content-free layout rule (locus_kind = register selector)",
    },
    {
        "thesis_id": 10,
        "thesis_name": "Labels as names of drawn objects",
        "proponent": "nomenclator",
        "predicted_signals": "label_object_coupling present; same object type -> consistent label structure across folios",
        "discriminating_signal": "label_object_coupling",
        "signal_class": "contradicted_by_corpus",
        "mapped_routes": "R57,R63,R64,R65b",
        "corpus_result": "decoupled (powered n=171 + refined n=108); same nymph -> folio-local labels f71r vs f73r divergence p=0.011; only correlate = vessel-vs-organ LENGTH (structure)",
        "controls_applied": "within_folio,section,locus_type",
        "verdict": "refuted",
        "external_residual": "none",
    },
    {
        "thesis_id": 11,
        "thesis_name": "Constructed language / technical notation",
        "proponent": "philosophical-language tradition",
        "predicted_signals": "full morphologically-rich / syntactically-thin profile (templatic operators, free variation, lexically-fixed nucleus)",
        "discriminating_signal": "none",
        "signal_class": "reproduced_by_generator",
        "mapped_routes": "R49,R55,R65a,R62",
        "corpus_result": "fits the whole profile; R62: designed-system vs generator are DEGENERATE at the token scale, indistinguishable by corpus statistics",
        "controls_applied": "comparison_vs_R62",
        "verdict": "external_only",
        "external_residual": "only a key/crib, sibling text, or provenance separates designed-with-meaning from content-free; this is the ~22% prior corpus statistics provably cannot touch",
    },
    {
        "thesis_id": 12,
        "thesis_name": "Local generator without content",
        "proponent": "the R62 model",
        "predicted_signals": "R62 13-signature panel(ok); laafu_I~0.303 UNDER-shoots real 0.471",
        "discriminating_signal": "laafu_I",
        "signal_class": "is_the_generator",
        "mapped_routes": "R62",
        "corpus_result": "IS the baseline; reproduces 13/14, fails only laafu_I; proves meaning NOT NECESSARY (existence proof, not meaninglessness)",
        "controls_applied": "comparison_vs_R62",
        "verdict": "survives_weakly",
        "external_residual": "none",
    },
    {
        "thesis_id": 13,
        "thesis_name": "Point decipherments (Turkish/Hebrew/proto-Romance/Latin...)",
        "proponent": "Cheshire/Bax/Gibbs etc",
        "predicted_signals": "a SPECIFIC natural language: char_h2 natural;midrange_MI>0;order_gain~12-25%;reproducing grammar",
        "discriminating_signal": "char_h2",
        "signal_class": "contradicted_by_corpus",
        "mapped_routes": "R58,R59,R60",
        "corpus_result": "h2=2.15; no midrange MI; each 'solution' decodes a handful of cherry-picked tokens, no corpus-wide reproducing grammar",
        "controls_applied": "char_h2,second_compressor",
        "verdict": "refuted",
        "external_residual": "none",
    },
]


# --------------------------------------------------------------------------- #
# Non-circular link: load the R62 generator's own baseline                    #
# --------------------------------------------------------------------------- #
def load_generator_baseline(summary_path: Path, match_path: Path) -> dict:
    """Read the R62 generator outputs and return the grounding facts.

    From generator_summary_zl3b.csv (metric,value rows):
      * key_metrics_resisting -> RESISTING_SET (comma-split; "none" -> empty set).
        This is THE set the non-circular invariant checks discriminators against.
      * n_metrics (14), n_matched (13), verdict (generator_insufficient).
    From generator_match_zl3b.csv (per-metric rows): the laafu_I row's real,
    generator and abs_delta -- the quantitative anchor for the one signature that
    beats the content-free generator.

    Returns {resisting_set, n_metrics, n_matched, laafu_real, laafu_gen,
    laafu_gap, gen_verdict}.
    """
    summary: dict[str, str] = {}
    with summary_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            summary[row["metric"]] = row["value"]

    raw_resisting = summary.get("key_metrics_resisting", "none").strip()
    if not raw_resisting or raw_resisting.lower() == "none":
        resisting_set: set[str] = set()
    else:
        resisting_set = {s.strip() for s in raw_resisting.split(",") if s.strip()}

    n_metrics = int(summary["n_metrics"])
    n_matched = int(summary["n_matched"])
    gen_verdict = summary.get("verdict", "")

    laafu_real = laafu_gen = laafu_gap = float("nan")
    with match_path.open(encoding="utf-8") as f:
        for row in csv.DictReader(f):
            if row["metric"] == "laafu_I":
                laafu_real = float(row["real"])
                laafu_gen = float(row["generator"])
                laafu_gap = float(row["abs_delta"])
                break

    return {
        "resisting_set": resisting_set,
        "n_metrics": n_metrics,
        "n_matched": n_matched,
        "laafu_real": laafu_real,
        "laafu_gen": laafu_gen,
        "laafu_gap": laafu_gap,
        "gen_verdict": gen_verdict,
    }


# --------------------------------------------------------------------------- #
# Build + validate the matrix                                                 #
# --------------------------------------------------------------------------- #
def build_matrix_rows(resisting_set: set[str]) -> list[dict]:
    """Assemble one fully-validated matrix row per thesis, in id order.

    For each thesis the two decision booleans are COMPUTED from its signal_class,
    and the runtime consistency invariants are asserted (raising AssertionError on
    violation) -- including the non-circular check that a "resists_generator"
    thesis only discriminates on a signature in the generator's OWN resisting set.
    """
    rows: list[dict] = []
    seen_ids: set[int] = set()
    for t in THESES:
        tid = t["thesis_id"]
        assert tid not in seen_ids, f"duplicate thesis_id {tid}"
        seen_ids.add(tid)

        sclass = t["signal_class"]
        verdict = t["verdict"]
        disc = t["discriminating_signal"]
        assert sclass in SIGNAL_CLASSES, (tid, sclass)
        assert verdict in VERDICTS, (tid, verdict)

        bg = beats_generator(sclass)
        rbi = refuted_by_instrument(sclass)

        # --- consistency invariants (mirrored in the tests) ---
        assert rbi == (verdict == "refuted"), (
            f"thesis {tid}: refuted_by_instrument={rbi} but verdict={verdict}"
        )
        assert bg == (verdict == "actionable"), (
            f"thesis {tid}: beats_generator={bg} but verdict={verdict}"
        )
        # the NON-CIRCULAR check: a resists_generator claim must discriminate on a
        # signature the generator's own output failed to reproduce.
        if sclass == "resists_generator":
            assert disc in resisting_set, (
                f"thesis {tid}: claims resists_generator on '{disc}' "
                f"not in generator resisting_set {sorted(resisting_set)}"
            )
        # golden-rule guard: no meaning/translation claim in verdict or headline cells
        for field in ("verdict", "corpus_result"):
            low = t[field].lower()
            for banned in _BANNED_MEANING_SUBSTRINGS:
                assert banned not in low, (
                    f"thesis {tid}: meaning claim '{banned}' in {field}"
                )

        rows.append(
            {
                "thesis_id": tid,
                "thesis_name": t["thesis_name"],
                "proponent": t["proponent"],
                "predicted_signals": t["predicted_signals"],
                "discriminating_signal": disc,
                "signal_class": sclass,
                "beats_generator": bg,
                "refuted_by_instrument": rbi,
                "mapped_routes": t["mapped_routes"],
                "corpus_result": t["corpus_result"],
                "controls_applied": t["controls_applied"],
                "verdict": verdict,
                "external_residual": t["external_residual"],
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def _ids_with(rows: list[dict], verdict: str) -> list[int]:
    return [r["thesis_id"] for r in rows if r["verdict"] == verdict]


def build_summary_rows(rows: list[dict], baseline: dict) -> list[dict]:
    """Assemble the (metric,value) summary, including the generator anchor facts
    and the partitions of the 13 theses by verdict / by beats_generator."""
    n_refuted = sum(1 for r in rows if r["verdict"] == "refuted")
    n_unsupported = sum(1 for r in rows if r["verdict"] == "unsupported")
    n_survives = sum(1 for r in rows if r["verdict"] == "survives_weakly")
    n_actionable = sum(1 for r in rows if r["verdict"] == "actionable")
    n_external = sum(1 for r in rows if r["verdict"] == "external_only")
    n_beats = sum(1 for r in rows if r["beats_generator"])
    n_rbi = sum(1 for r in rows if r["refuted_by_instrument"])

    dead = _ids_with(rows, "refuted")
    degenerate_alive = _ids_with(rows, "unsupported") + _ids_with(rows, "survives_weakly")
    actionable_ids = _ids_with(rows, "actionable")
    external_ids = _ids_with(rows, "external_only")

    resisting = ",".join(sorted(baseline["resisting_set"])) if baseline["resisting_set"] else "none"
    headline = (
        f"{n_beats} of {len(rows)} external theses beats the R62 content-free generator "
        f"(thesis {actionable_ids[0] if actionable_ids else '-'} on laafu_I, real "
        f"{baseline['laafu_real']:.3f} > gen {baseline['laafu_gen']:.3f}); "
        f"{n_refuted} refuted by the corpus, {n_external} provably external_only structure"
    )

    def _ids(xs: list[int]) -> str:
        return ",".join(str(x) for x in sorted(xs)) if xs else "none"

    summary = [
        ("n_theses", str(len(rows))),
        ("n_refuted", str(n_refuted)),
        ("n_unsupported", str(n_unsupported)),
        ("n_survives_weakly", str(n_survives)),
        ("n_actionable", str(n_actionable)),
        ("n_external_only", str(n_external)),
        ("n_beats_generator", str(n_beats)),
        ("n_refuted_by_instrument", str(n_rbi)),
        ("generator_n_metrics", str(baseline["n_metrics"])),
        ("generator_n_matched", str(baseline["n_matched"])),
        ("generator_resisting", resisting),
        ("laafu_real", f"{baseline['laafu_real']:.6f}"),
        ("laafu_gen", f"{baseline['laafu_gen']:.6f}"),
        ("laafu_gap", f"{baseline['laafu_gap']:.6f}"),
        ("dead_theses", _ids(dead)),
        ("degenerate_alive_theses", _ids(degenerate_alive)),
        ("actionable_theses", _ids(actionable_ids)),
        ("external_only_theses", _ids(external_ids)),
        ("headline", headline),
        ("verdict", f"{n_beats}of{len(rows)}_beats_contentfree_generator"),
        ("guardrail", GUARDRAIL),
    ]
    # golden-rule guard on the headline / verdict cells
    for metric, value in summary:
        if metric in ("headline", "verdict"):
            low = value.lower()
            for banned in _BANNED_MEANING_SUBSTRINGS:
                assert banned not in low, f"meaning claim '{banned}' in summary {metric}"
    return [{"metric": m, "value": v} for m, v in summary]


# --------------------------------------------------------------------------- #
# IO                                                                          #
# --------------------------------------------------------------------------- #
def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


MATRIX_FIELDS = [
    "thesis_id",
    "thesis_name",
    "proponent",
    "predicted_signals",
    "discriminating_signal",
    "signal_class",
    "beats_generator",
    "refuted_by_instrument",
    "mapped_routes",
    "corpus_result",
    "controls_applied",
    "verdict",
    "external_residual",
    "semantic_guardrail",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--gen-summary",
        default=str(DEFAULT_GEN_SUMMARY),
        help="R62 generator_summary CSV (source of the resisting_set)",
    )
    p.add_argument(
        "--gen-match",
        default=str(DEFAULT_GEN_MATCH),
        help="R62 generator_match CSV (source of the laafu_I anchor)",
    )
    d = ROOT / "data" / "derived"
    p.add_argument("--out-matrix", default=str(d / "external_thesis_attack_matrix_zl3b.csv"))
    p.add_argument(
        "--out-summary", default=str(d / "external_thesis_attack_matrix_summary_zl3b.csv")
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    baseline = load_generator_baseline(Path(args.gen_summary), Path(args.gen_match))

    rows = build_matrix_rows(baseline["resisting_set"])
    summary_rows = build_summary_rows(rows, baseline)

    write_csv(Path(args.out_matrix), rows, MATRIX_FIELDS)
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    # --- console report ---
    print(
        f"GENERATOR BASELINE (non-circular link): n_metrics={baseline['n_metrics']} "
        f"n_matched={baseline['n_matched']} resisting={sorted(baseline['resisting_set'])} "
        f"verdict={baseline['gen_verdict']}"
    )
    print(
        f"  laafu anchor: real={baseline['laafu_real']:.3f} gen={baseline['laafu_gen']:.3f} "
        f"gap={baseline['laafu_gap']:.3f}"
    )
    print("EXTERNAL-THESIS ATTACK MATRIX (id | name | signal_class | beats | refuted_by_instr | verdict):")
    for r in rows:
        beats = "BEATS" if r["beats_generator"] else "  -  "
        rbi = "REFUTED" if r["refuted_by_instrument"] else "   -   "
        print(
            f"  {r['thesis_id']:2d} {r['thesis_name'][:46]:46s} "
            f"{r['signal_class']:26s} {beats} {rbi} -> {r['verdict']}"
        )
    summ = {r["metric"]: r["value"] for r in summary_rows}
    print(
        "TALLY: "
        f"refuted={summ['n_refuted']} unsupported={summ['n_unsupported']} "
        f"survives_weakly={summ['n_survives_weakly']} actionable={summ['n_actionable']} "
        f"external_only={summ['n_external_only']} | beats_generator={summ['n_beats_generator']} "
        f"refuted_by_instrument={summ['n_refuted_by_instrument']}"
    )
    print(f"  dead_theses={summ['dead_theses']}")
    print(f"  degenerate_alive_theses={summ['degenerate_alive_theses']}")
    print(f"  actionable_theses={summ['actionable_theses']}")
    print(f"  external_only_theses={summ['external_only_theses']}")
    print(f"HEADLINE: {summ['headline']}")
    print(f"VERDICT={summ['verdict']}")
    print(f"golden_rule: {NO_TRANSLATION_CLAIM}")
    print(f"output_csv={args.out_matrix}")
    print(f"output_csv={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
