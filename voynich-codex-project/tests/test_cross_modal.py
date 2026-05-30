"""Tests for analyze_cross_modal.py (Rota 63 — frente visual cross-modal)."""
from __future__ import annotations

import collections
import csv
import random
from pathlib import Path

import pytest

from scripts.analyze_cross_modal import (
    GUARDRAIL,
    GUARDRAIL_COMBINED,
    GUARDRAIL_REFINED,
    COARSE_MAP,
    COARSE_MAP_COMBINED,
    COARSE_MAP_REFINED,
    COMBINED_INPUTS,
    NYMPH_FOLIOS,
    NYMPH_FOLIOS_REFINED,
    PHARMA_FOLIOS_COMBINED,
    PHARMA_FOLIOS_REFINED,
    REFINED_INPUT,
    R64_SUMMARY_INPUT,
    clean_token,
    coarse_class,
    coarse_class_combined,
    coarse_class_refined,
    cramer_v,
    first_glyph,
    prefix4,
    gallows_present,
    gallows_class,
    length_bucket,
    nucleus,
    vowel_present,
    build_elements,
    load_combined,
    load_refined,
    permutation_pvalues,
    pharma_vessel_vs_organ,
    pharma_object_type_test,
    nymph_consistency,
    nymph_profile_divergence,
    decide_verdict,
    decide_verdict_combined,
    read_r64_summary,
    run_combined,
    run_refined,
    _global_shuffle,
    _within_folio_shuffle,
    _r64_per_feature_p_within,
    main,
)


# --------------------------------------------------------------------------
# cramer_v on a known table
# --------------------------------------------------------------------------
def test_cramer_v_perfect_separation():
    table = {"A": collections.Counter({"x": 10}), "B": collections.Counter({"y": 10})}
    v, n = cramer_v(table)
    assert n == 20
    assert v == pytest.approx(1.0, abs=0.01)


def test_cramer_v_uniform_is_zero():
    table = {"A": collections.Counter({"x": 5, "y": 5}),
             "B": collections.Counter({"x": 5, "y": 5})}
    v, n = cramer_v(table)
    assert v == pytest.approx(0.0, abs=0.01)
    assert n == 20


def test_cramer_v_small_n_returns_zero():
    table = {"A": collections.Counter({"x": 1}), "B": collections.Counter({"y": 1})}
    v, n = cramer_v(table)
    assert v == 0.0
    assert n == 2


# --------------------------------------------------------------------------
# coarse mapping correctness
# --------------------------------------------------------------------------
def test_coarse_mapping_correct():
    assert coarse_class("leaf") == "organ"
    assert coarse_class("root") == "organ"
    assert coarse_class("stem") == "organ"
    assert coarse_class("flower") == "organ"
    assert coarse_class("spray") == "organ"
    assert coarse_class("whole_plant") == "whole_plant"
    assert coarse_class("container") == "vessel"
    assert coarse_class("star") == "sky"
    assert coarse_class("figure_roundel") == "sky"


def test_coarse_mapping_unknown_and_case():
    assert coarse_class("dragon") == "other"
    assert coarse_class("CONTAINER") == "vessel"  # case-insensitive
    assert coarse_class("") == "other"


def test_coarse_map_covers_all_object_types_in_data():
    # Every object_type present in the input CSV must map to a real coarse class.
    csv_path = Path(__file__).resolve().parents[1] / "data" / "derived" / "rota63_cross_modal_labels_zl3b.csv"
    if not csv_path.exists():
        pytest.skip("rota63_cross_modal_labels_zl3b.csv not found")
    types = {r["object_type"].strip().lower() for r in csv.DictReader(csv_path.open(encoding="utf-8"))}
    for t in types:
        assert t in COARSE_MAP, f"object_type {t!r} not in COARSE_MAP"


# --------------------------------------------------------------------------
# token cleaning + feature extraction on sample tokens
# --------------------------------------------------------------------------
def test_clean_token_strips_locus_dots_and_case():
    assert clean_token("okar.y") == "okary"
    assert clean_token("otar.arody") == "otararody"
    assert clean_token("OkAl") == "okal"
    assert clean_token("ok-al_2") == "okal"
    assert clean_token("") == ""


def test_prefix4_buckets():
    assert prefix4("qotoear") == "qo"
    assert prefix4("okary") == "ok"
    assert prefix4("otoldy") == "ot"
    assert prefix4("ykeodar") == "yk"
    assert prefix4("ytodal") == "yt"
    assert prefix4("oparal") == "o-other"   # starts o but not ok/ot/qo
    assert prefix4("salo") == "other"
    assert prefix4("") == "other"


def test_first_glyph():
    assert first_glyph("okary") == "o"
    assert first_glyph("salo") == "s"
    assert first_glyph("") == "none"


def test_gallows_present_and_class():
    assert gallows_present("okary") == "yes"        # k
    assert gallows_present("otoldy") == "yes"        # t
    assert gallows_present("salo") == "no"
    assert gallows_present("oran") == "no"
    # gallows_class = first gallows encountered
    assert gallows_class("okary") == "k"
    assert gallows_class("otoldy") == "t"
    assert gallows_class("cpheor") == "p"
    assert gallows_class("salo") == "none"


def test_length_bucket():
    assert length_bucket("oky") == "short"        # 3
    assert length_bucket("okal") == "short"       # 4
    assert length_bucket("oparal") == "mid"       # 6
    assert length_bucket("okaramy") == "long"     # 7
    assert length_bucket("daramdal") == "long"    # 8


def test_nucleus_chsh():
    assert nucleus("cheocthy") == "ch"      # leading 'ch'
    assert nucleus("otorchy") == "ch"       # 'ch' mid-token
    assert nucleus("ockhosam") == "none"    # 'c'+'k', no 'ch' digraph
    assert nucleus("skeeal") == "none"      # 's'+'k', no 'sh' digraph
    assert nucleus("okal") == "none"


def test_nucleus_sh_explicit():
    assert nucleus("shol") == "sh"
    assert nucleus("ashom") == "sh"


def test_vowel_present():
    assert vowel_present("okal") == "yes"
    assert vowel_present("krk") == "no"
    assert vowel_present("") == "no"


# --------------------------------------------------------------------------
# build_elements
# --------------------------------------------------------------------------
def _row(folio, otype, tok, conf="high"):
    return {
        "folio": folio,
        "object_type": otype,
        "label_token": tok,
        "annotation_confidence": conf,
        "semantic_guardrail": GUARDRAIL,
    }


def test_build_elements_maps_and_extracts():
    rows = [_row("f99r", "container", "okaradag"), _row("f99r", "root", "okar.y", "medium")]
    els = build_elements(rows)
    assert len(els) == 2
    assert els[0]["coarse"] == "vessel"
    assert els[0]["prefix4"] == "ok"
    assert els[1]["coarse"] == "organ"
    assert els[1]["token"] == "okary"      # dot stripped
    assert els[1]["confidence"] == "medium"


def test_build_elements_skips_empty_token():
    rows = [_row("f99r", "container", ""), _row("f99r", "root", "okar")]
    els = build_elements(rows)
    assert len(els) == 1


# --------------------------------------------------------------------------
# within-folio shuffle preserves per-folio class counts (differs from global)
# --------------------------------------------------------------------------
def test_within_folio_shuffle_preserves_per_folio_counts():
    folios = ["fA", "fA", "fA", "fB", "fB"]
    classes = ["organ", "organ", "vessel", "sky", "sky"]
    rng = random.Random(1)
    out = _within_folio_shuffle(classes, folios, rng)
    # per-folio multiset of classes is preserved exactly
    def per_folio(vals):
        d = collections.defaultdict(collections.Counter)
        for f, c in zip(folios, vals):
            d[f][c] += 1
        return {k: dict(v) for k, v in d.items()}
    assert per_folio(out) == per_folio(classes)


def test_within_folio_differs_from_global_shuffle():
    # Construct a case where global shuffle CAN move classes across folios but
    # within-folio cannot. fA is all-organ, fB is all-vessel: within-folio shuffle
    # is a no-op (each folio uniform), but global shuffle will (with high prob)
    # mix classes across folios. So the per-folio counts differ between them.
    folios = ["fA"] * 5 + ["fB"] * 5
    classes = ["organ"] * 5 + ["vessel"] * 5

    def per_folio(vals):
        d = collections.defaultdict(collections.Counter)
        for f, c in zip(folios, vals):
            d[f][c] += 1
        return {k: dict(v) for k, v in d.items()}

    rng_w = random.Random(7)
    within = _within_folio_shuffle(classes, folios, rng_w)
    assert per_folio(within) == per_folio(classes)  # uniform folios: unchanged

    # at least one global shuffle (over several seeds) mixes the folios
    mixed = False
    for s in range(20):
        g = _global_shuffle(classes, random.Random(s))
        if per_folio(g) != per_folio(classes):
            mixed = True
            break
    assert mixed, "global shuffle should be able to move classes across folios"


# --------------------------------------------------------------------------
# synthetic: a feature perfectly predicts class WITHIN folio -> low p_within_folio
# --------------------------------------------------------------------------
def test_synthetic_feature_predicts_class_within_folio_low_p():
    # Two folios; within EACH folio, prefix perfectly separates vessel vs organ.
    # vessels carry 'ok' prefix, organs carry 's' (other). This must NOT be
    # explainable by folio alone -> p_within_folio should be small.
    rows = []
    for fo in ("fA", "fB"):
        for i in range(4):
            rows.append(_row(fo, "container", "okal"))    # vessel, prefix ok
            rows.append(_row(fo, "root", "salos"))        # organ, prefix other
    els = build_elements(rows)
    v, p_g, p_w, n = permutation_pvalues(els, "prefix4", n_perm=500, seed=1)
    assert n == 16
    assert v == pytest.approx(1.0, abs=0.01)
    assert p_w < 0.05, f"within-folio p should be small, got {p_w}"
    assert p_g < 0.05


def test_synthetic_folio_confound_dies_under_within_folio():
    # Pure folio confound: each folio is HOMOGENEOUS in class AND in feature.
    # fA = all vessels with 'ok'; fB = all organs with 's'. Global shuffle sees a
    # strong V (feature predicts class), but within-folio shuffle is a no-op so
    # the observed V is never exceeded -> p_within_folio ~ 1.0 (max). This is the
    # spurious global signal the within-folio control is designed to kill.
    rows = []
    for i in range(6):
        rows.append(_row("fA", "container", "okal"))
        rows.append(_row("fB", "root", "salos"))
    els = build_elements(rows)
    v, p_g, p_w, n = permutation_pvalues(els, "prefix4", n_perm=500, seed=2)
    assert v == pytest.approx(1.0, abs=0.01)   # strong global association
    assert p_g < 0.05                          # global thinks it's real
    assert p_w > 0.5                           # within-folio control kills it


# --------------------------------------------------------------------------
# pharma vessel vs organ subset
# --------------------------------------------------------------------------
def test_pharma_vessel_vs_organ_subset_selection():
    rows = [
        _row("f99r", "container", "okaradag"),   # pharma vessel -> in
        _row("f99r", "root", "okary"),           # pharma organ  -> in
        _row("f99v", "container", "okaramy"),    # pharma vessel -> in
        _row("f67r2", "star", "qotoear"),        # astro sky     -> out (not pharma)
        _row("f99r", "whole_plant", "aora"),     # pharma whole_plant -> out (not vessel/organ)
    ]
    els = build_elements(rows)
    res = pharma_vessel_vs_organ(els, n_perm=200, seed=3)
    assert res["n"] == 3
    assert res["n_vessel"] == 2
    assert res["n_organ"] == 1


# --------------------------------------------------------------------------
# verdict logic
# --------------------------------------------------------------------------
def test_decide_verdict_correspondence_requires_both_subsets():
    all_rows = [
        {"feature": "prefix4", "p_within_folio": 0.01},
        {"feature": "nucleus", "p_within_folio": 0.30},
    ]
    nonunc_rows = [
        {"feature": "prefix4", "p_within_folio": 0.02},   # survives in non-uncertain too
        {"feature": "nucleus", "p_within_folio": 0.40},
    ]
    verdict, best, p = decide_verdict(all_rows, nonunc_rows)
    assert verdict == "cross_modal_correspondence"
    assert best == "prefix4"
    assert p == 0.01


def test_decide_verdict_pilot_when_nonuncertain_fails():
    all_rows = [{"feature": "prefix4", "p_within_folio": 0.01}]
    nonunc_rows = [{"feature": "prefix4", "p_within_folio": 0.20}]  # fails on subset
    verdict, best, p = decide_verdict(all_rows, nonunc_rows)
    assert verdict == "decoupled_pilot"


def test_decide_verdict_pilot_when_global_only():
    # signal only global (p_within_folio never < 0.05) -> pilot
    all_rows = [{"feature": "prefix4", "p_within_folio": 0.50}]
    nonunc_rows = [{"feature": "prefix4", "p_within_folio": 0.60}]
    verdict, _best, _p = decide_verdict(all_rows, nonunc_rows)
    assert verdict == "decoupled_pilot"


# --------------------------------------------------------------------------
# guardrail
# --------------------------------------------------------------------------
def test_guardrail_contains_not_decipherment():
    assert "not" in GUARDRAIL
    assert "decipherment" in GUARDRAIL


# --------------------------------------------------------------------------
# main writes both CSVs (small n_perm for speed)
# --------------------------------------------------------------------------
def test_main_writes_both_csvs(tmp_path):
    src = Path(__file__).resolve().parents[1] / "data" / "derived" / "rota63_cross_modal_labels_zl3b.csv"
    if not src.exists():
        pytest.skip("rota63_cross_modal_labels_zl3b.csv not found")
    out_test = tmp_path / "cross_modal_test.csv"
    out_sum = tmp_path / "cross_modal_summary.csv"
    rc = main([
        str(src),
        "--out-test", str(out_test),
        "--out-summary", str(out_sum),
        "--n-perm", "200",
        "--seed", "63",
    ])
    assert rc == 0
    assert out_test.exists() and out_sum.exists()

    test_rows = list(csv.DictReader(out_test.open(encoding="utf-8")))
    # 7 features x 2 subsets = 14 rows
    assert len(test_rows) == 14
    subsets = {r["subset"] for r in test_rows}
    assert subsets == {"all", "non_uncertain"}
    for r in test_rows:
        assert r["semantic_guardrail"] == GUARDRAIL
        assert 0.0 <= float(r["p_within_folio"]) <= 1.0
        assert 0.0 <= float(r["p_global"]) <= 1.0

    sum_rows = {r["metric"]: r["value"] for r in csv.DictReader(out_sum.open(encoding="utf-8"))}
    for key in (
        "n_total", "n_non_uncertain", "best_feature", "best_p_within_folio",
        "pharma_vessel_vs_organ_V", "pharma_vessel_vs_organ_p_within_folio",
        "verdict", "semantic_guardrail",
    ):
        assert key in sum_rows, f"missing summary metric {key}"
    assert sum_rows["verdict"] in ("cross_modal_correspondence", "decoupled_pilot")
    assert sum_rows["semantic_guardrail"] == GUARDRAIL


def test_main_deterministic(tmp_path):
    src = Path(__file__).resolve().parents[1] / "data" / "derived" / "rota63_cross_modal_labels_zl3b.csv"
    if not src.exists():
        pytest.skip("rota63_cross_modal_labels_zl3b.csv not found")

    def run(d):
        ot = d / "t.csv"
        os = d / "s.csv"
        main([str(src), "--out-test", str(ot), "--out-summary", str(os),
              "--n-perm", "300", "--seed", "63"])
        return ot.read_text(encoding="utf-8"), os.read_text(encoding="utf-8")

    a_test, a_sum = run(tmp_path / "a")
    b_test, b_sum = run(tmp_path / "b")
    assert a_test == b_test  # same seed -> identical permutation p-values
    assert a_sum == b_sum


# ==========================================================================
# Rota 64 — MODO COMBINADO (amplia o piloto R63 p/ n=171, 12 fólios)
# ==========================================================================
def _combined_exists():
    return all(Path(p).exists() for p in COMBINED_INPUTS)


def test_combined_guardrail_is_rota64():
    assert GUARDRAIL_COMBINED == "rota64_cross_modal_not_decipherment"
    assert "not" in GUARDRAIL_COMBINED and "decipherment" in GUARDRAIL_COMBINED


# -- (1) concat loader gives 171 rows --
def test_load_combined_gives_171_rows():
    if not _combined_exists():
        pytest.skip("combined annotation CSVs not found")
    rows = load_combined()
    assert len(rows) == 171
    # both source guardrails present (proves concat of the two files)
    guards = {r["semantic_guardrail"] for r in rows}
    assert "rota63_cross_modal_not_decipherment" in guards
    assert "rota64_cross_modal_not_decipherment" in guards


def test_load_combined_12_folios_and_nymph_in_two_folios():
    if not _combined_exists():
        pytest.skip("combined annotation CSVs not found")
    rows = load_combined()
    folios = {r["folio"].strip() for r in rows}
    assert len(folios) == 12
    nymph_folios = {r["folio"].strip() for r in rows if r["object_type"].strip().lower() == "nymph"}
    assert nymph_folios == set(NYMPH_FOLIOS)  # nymphs only in the 2 zodiac folios


# -- (2) coarse mapping incl figure class --
def test_coarse_combined_includes_figure_class():
    assert coarse_class_combined("nymph") == "figure"
    assert coarse_class_combined("figure_roundel") == "figure"
    assert coarse_class_combined("star") == "sky"
    assert coarse_class_combined("ring_segment") == "sky"
    assert coarse_class_combined("container") == "vessel"
    assert coarse_class_combined("root") == "organ"
    assert coarse_class_combined("whole_plant") == "whole_plant"
    assert coarse_class_combined("CONTAINER") == "vessel"  # case-insensitive
    assert coarse_class_combined("other") == "other"       # unmapped -> other
    assert coarse_class_combined("") == "other"


def test_coarse_map_combined_covers_all_object_types_except_other():
    if not _combined_exists():
        pytest.skip("combined annotation CSVs not found")
    rows = load_combined()
    types = {r["object_type"].strip().lower() for r in rows}
    # every type maps to a real coarse class except the explicit 'other' bucket
    for t in types:
        coarse = coarse_class_combined(t)
        if t == "other":
            assert coarse == "other"
        else:
            assert t in COARSE_MAP_COMBINED, f"object_type {t!r} not in COARSE_MAP_COMBINED"
            assert coarse in ("organ", "whole_plant", "vessel", "figure", "sky")


def test_build_elements_combined_coarse_counts():
    if not _combined_exists():
        pytest.skip("combined annotation CSVs not found")
    rows = load_combined()
    els = build_elements(rows, coarse_fn=coarse_class_combined)
    assert len(els) == 171
    counts = collections.Counter(e["coarse"] for e in els)
    # figure is now LARGE (44 nymph + 4 figure_roundel = 48)
    assert counts["figure"] == 48
    assert counts["vessel"] == 15
    assert counts["organ"] == 81
    assert counts["whole_plant"] == 17
    assert counts["sky"] == 9
    assert counts["other"] == 1


# -- (3) within-folio shuffle preserves per-folio class counts (combined data) --
def test_within_folio_shuffle_preserves_counts_on_combined():
    if not _combined_exists():
        pytest.skip("combined annotation CSVs not found")
    rows = load_combined()
    els = build_elements(rows, coarse_fn=coarse_class_combined)
    folios = [e["folio"] for e in els]
    classes = [e["coarse"] for e in els]
    rng = random.Random(64)
    out = _within_folio_shuffle(classes, folios, rng)

    def per_folio(vals):
        d = collections.defaultdict(collections.Counter)
        for f, c in zip(folios, vals):
            d[f][c] += 1
        return {k: dict(v) for k, v in d.items()}

    assert per_folio(out) == per_folio(classes)  # exact per-folio class multiset


# -- (4) nymph-consistency function on synthetic cases --
def _nymph_row(folio, tok, conf="medium"):
    return {
        "folio": folio,
        "object_type": "nymph",
        "label_token": tok,
        "annotation_confidence": conf,
        "semantic_guardrail": GUARDRAIL_COMBINED,
    }


def test_nymph_consistency_consistent_synthetic():
    # Nymphs structured (all 'ot...' prefix vs non-nymph 'sal') AND the two folios
    # share the SAME label profile -> low cross-folio divergence -> 'consistent'.
    rows = []
    for fo in ("f71r", "f73r"):
        for i in range(8):
            rows.append(_nymph_row(fo, "otoldar"))   # identical profile both folios
    # non-nymph contrast so is_nymph structures a feature
    for i in range(8):
        rows.append({"folio": "f88v", "object_type": "root", "label_token": "salos",
                     "annotation_confidence": "medium", "semantic_guardrail": GUARDRAIL_COMBINED})
    els = build_elements(rows, coarse_fn=coarse_class_combined)
    res = nymph_consistency(els, ("f71r", "f73r"), n_perm=400, seed=64)
    assert res["n_nymph"] == 16
    assert res["n_folios"] == 2
    assert res["struct_p"] < 0.05            # nymphs structurally distinct
    assert res["p_divergent"] >= 0.05        # profiles NOT more divergent than chance
    assert res["result"] == "consistent"


def test_nymph_consistency_folio_local_synthetic():
    # Nymphs structured, but each folio uses a DISJOINT vocabulary:
    # f71r = 'ot...'/t-gallows, f73r = 'ok...'/k-gallows. Profiles diverge far more
    # than a folio-label shuffle -> 'folio_local' (NOT a consistent object-name).
    rows = []
    for i in range(10):
        rows.append(_nymph_row("f71r", "otoltar"))   # ot / t-gallows / long
    for i in range(10):
        rows.append(_nymph_row("f73r", "okeesy"))     # ok / k-gallows
    for i in range(10):
        rows.append({"folio": "f88v", "object_type": "root", "label_token": "salos",
                     "annotation_confidence": "medium", "semantic_guardrail": GUARDRAIL_COMBINED})
    els = build_elements(rows, coarse_fn=coarse_class_combined)
    res = nymph_consistency(els, ("f71r", "f73r"), n_perm=400, seed=64)
    assert res["n_nymph"] == 20
    assert res["struct_p"] < 0.05            # still structured
    assert res["p_divergent"] < 0.05         # significantly MORE divergent than chance
    assert res["result"] == "folio_local"


def test_nymph_consistency_insufficient_folios():
    rows = [_nymph_row("f71r", "otoldar") for _ in range(6)]
    els = build_elements(rows, coarse_fn=coarse_class_combined)
    res = nymph_consistency(els, ("f71r", "f73r"), n_perm=100, seed=64)
    assert res["n_folios"] == 1
    assert res["result"] == "insufficient_folios"


def test_nymph_profile_divergence_identical_is_zero():
    rows = [_nymph_row("f71r", "otoldar"), _nymph_row("f73r", "otoldar")]
    els = build_elements(rows, coarse_fn=coarse_class_combined)
    nym = [e for e in els if e["object_type"] == "nymph"]
    div, per_feat = nymph_profile_divergence(nym, "f71r", "f73r")
    assert div == pytest.approx(0.0, abs=1e-9)   # identical tokens -> identical profiles
    assert len(per_feat) == 7


# -- pharma object-type test (parameterized folio set) --
def test_pharma_object_type_test_uses_param_folios():
    rows = [
        _row("f88r", "container", "otorchety"),   # combined-pharma vessel -> in
        _row("f88r", "root", "osal", "medium"),   # combined-pharma organ  -> in
        _row("f89v1", "container", "okoraldy"),   # combined-pharma vessel -> in
        _row("f99r", "container", "okaradag"),    # combined-pharma vessel -> in
        _row("f99r", "root", "okary", "medium"),  # combined-pharma organ  -> in
        _row("f71r", "nymph", "otaly", "medium"), # NOT pharma -> out
        _row("f88r", "whole_plant", "otoram"),    # not vessel/organ -> out
    ]
    els = build_elements(rows, coarse_fn=coarse_class_combined)
    res = pharma_object_type_test(els, PHARMA_FOLIOS_COMBINED, n_perm=200, seed=64)
    assert res["n"] == 5
    assert res["n_vessel"] == 3
    assert res["n_organ"] == 2
    assert res["best_feature"] in (
        "first_glyph", "prefix4", "gallows_present", "gallows_class",
        "length_bucket", "nucleus", "vowel_present",
    )


# -- combined verdict logic --
def test_decide_verdict_combined_nymph_signal_triggers():
    # No headline signal, but nymph profiles consistent+structured -> correspondence.
    all_rows = [{"feature": "prefix4", "p_within_folio": 0.50}]
    nonunc_rows = [{"feature": "prefix4", "p_within_folio": 0.60}]
    nymph = {"result": "consistent"}
    verdict, _b, _p = decide_verdict_combined(all_rows, nonunc_rows, nymph)
    assert verdict == "cross_modal_correspondence"


def test_decide_verdict_combined_headline_triggers():
    all_rows = [{"feature": "length_bucket", "p_within_folio": 0.01}]
    nonunc_rows = [{"feature": "length_bucket", "p_within_folio": 0.02}]
    nymph = {"result": "folio_local"}
    verdict, best, p = decide_verdict_combined(all_rows, nonunc_rows, nymph)
    assert verdict == "cross_modal_correspondence"
    assert best == "length_bucket"
    assert p == 0.01


def test_decide_verdict_combined_decoupled_when_neither():
    # headline fails the both-subsets rule AND nymph is folio_local -> decoupled.
    all_rows = [{"feature": "gallows_present", "p_within_folio": 0.0536}]
    nonunc_rows = [{"feature": "gallows_present", "p_within_folio": 0.25}]
    nymph = {"result": "folio_local"}
    verdict, _b, _p = decide_verdict_combined(all_rows, nonunc_rows, nymph)
    assert verdict == "decoupled"


# -- (5) main combined-mode writes both CSVs --
def test_main_combined_writes_both_csvs(tmp_path):
    if not _combined_exists():
        pytest.skip("combined annotation CSVs not found")
    out_test = tmp_path / "ctest.csv"
    out_sum = tmp_path / "csum.csv"
    rc = main([
        "--combined",
        "--out-test-combined", str(out_test),
        "--out-summary-combined", str(out_sum),
        "--n-perm", "300",
        "--seed", "64",
    ])
    assert rc == 0
    assert out_test.exists() and out_sum.exists()

    test_rows = list(csv.DictReader(out_test.open(encoding="utf-8")))
    assert len(test_rows) == 14  # 7 features x 2 subsets
    subsets = {r["subset"] for r in test_rows}
    assert subsets == {"all", "non_uncertain"}
    for r in test_rows:
        assert r["semantic_guardrail"] == GUARDRAIL_COMBINED
        assert 0.0 <= float(r["p_within_folio"]) <= 1.0
        assert 0.0 <= float(r["p_global"]) <= 1.0
    # all-rows feature tests must be over the full n=171
    all_n = {int(r["n"]) for r in test_rows if r["subset"] == "all"}
    assert all_n == {171}

    sum_rows = {r["metric"]: r["value"] for r in csv.DictReader(out_sum.open(encoding="utf-8"))}
    for key in (
        "n_total", "n_non_uncertain", "n_folios", "best_feature", "best_p_within_folio",
        "pharma_test_result", "nymph_consistency_result", "verdict", "semantic_guardrail",
    ):
        assert key in sum_rows, f"missing summary metric {key}"
    assert sum_rows["n_total"] == "171"
    assert sum_rows["n_folios"] == "12"
    assert sum_rows["verdict"] in ("cross_modal_correspondence", "decoupled")
    assert sum_rows["pharma_test_result"] in ("object_type_signal", "no_object_type_signal")
    assert sum_rows["nymph_consistency_result"] in (
        "consistent", "folio_local", "unstructured", "insufficient_folios",
    )
    assert sum_rows["semantic_guardrail"] == GUARDRAIL_COMBINED


def test_run_combined_returns_171_and_verdict(tmp_path):
    if not _combined_exists():
        pytest.skip("combined annotation CSVs not found")
    res = run_combined(
        str(tmp_path / "t.csv"), str(tmp_path / "s.csv"), n_perm=300, seed=64
    )
    assert res["n_total"] == 171
    assert res["n_folios"] == 12
    assert res["verdict"] in ("cross_modal_correspondence", "decoupled")
    assert res["pharma"]["n_vessel"] == 15
    assert res["nymph"]["n_nymph"] == 44


def test_main_combined_deterministic(tmp_path):
    if not _combined_exists():
        pytest.skip("combined annotation CSVs not found")

    def run(d):
        ot = d / "t.csv"
        os = d / "s.csv"
        main(["--combined", "--out-test-combined", str(ot),
              "--out-summary-combined", str(os), "--n-perm", "300", "--seed", "64"])
        return ot.read_text(encoding="utf-8"), os.read_text(encoding="utf-8")

    a_test, a_sum = run(tmp_path / "a")
    b_test, b_sum = run(tmp_path / "b")
    assert a_test == b_test
    assert a_sum == b_sum


# ==========================================================================
# Rota 65 Leg B (Round 2) — MODO REFINADO
# Re-roda o teste cross-modal-controlado-por-fólio sobre a anotação refinada do
# visual-annotator (rota65b_cross_modal_refined_zl3b.csv). Mesmo conjunto de 171
# linhas que R63+R64 mas com confidence refinada (n_non_uncertain de 70 -> 108)
# e uma coluna extra `refinement_note` documentando cada promoção.
# ==========================================================================
def _refined_exists():
    return Path(REFINED_INPUT).exists()


def test_refined_guardrail_is_rota65b():
    assert GUARDRAIL_REFINED == "rota65b_cross_modal_refined_not_decipherment"
    assert "rota65b" in GUARDRAIL_REFINED
    assert "refined" in GUARDRAIL_REFINED
    assert "not" in GUARDRAIL_REFINED and "decipherment" in GUARDRAIL_REFINED


def test_refined_constants_match_combined():
    # MODO REFINADO usa os MESMOS conjuntos de fólios e o MESMO mapa coarse do
    # R64 (a anotação só mudou confidence; composição folio×object_type idêntica).
    assert PHARMA_FOLIOS_REFINED == PHARMA_FOLIOS_COMBINED
    assert NYMPH_FOLIOS_REFINED == NYMPH_FOLIOS
    assert COARSE_MAP_REFINED == COARSE_MAP_COMBINED


def test_load_refined_gives_171_rows_with_refinement_note():
    # (1) loader devolve as 171 linhas refinadas; (2) coluna nova refinement_note
    # presente em todas as linhas (mesmo que vazia); (3) guardrail refinado fixado.
    if not _refined_exists():
        pytest.skip("refined CSV not found")
    rows = load_refined()
    assert len(rows) == 171
    headers = list(rows[0].keys())
    assert "refinement_note" in headers, "refined CSV must carry refinement_note column"
    # guardrail por-linha do refinement
    guards = {r["semantic_guardrail"] for r in rows}
    assert GUARDRAIL_REFINED in guards


def test_refined_non_uncertain_count_is_108():
    # Promoções do refinement: 38 uncertain->medium, 15 medium->high, 0
    # uncertain->high (anotador deliberadamente honesto). n_non_uncertain
    # cresce de 70 (R64) para 108 (R65b).
    if not _refined_exists():
        pytest.skip("refined CSV not found")
    rows = load_refined()
    non_unc = [r for r in rows if r["annotation_confidence"].strip().lower() != "uncertain"]
    assert len(non_unc) == 108
    conf = collections.Counter(r["annotation_confidence"].strip().lower() for r in rows)
    assert conf["uncertain"] == 63
    assert conf["medium"] == 82
    assert conf["high"] == 26


def test_refined_same_composition_as_r64():
    # Refinement só mexeu em CONFIDENCE; folios e object_types idênticos a R63+R64.
    if not _refined_exists() or not all(Path(p).exists() for p in COMBINED_INPUTS):
        pytest.skip("refined or combined CSVs not found")
    refined_rows = load_refined()
    combined_rows = load_combined()
    assert len(refined_rows) == len(combined_rows) == 171
    assert (
        collections.Counter(r["object_type"].strip().lower() for r in refined_rows)
        == collections.Counter(r["object_type"].strip().lower() for r in combined_rows)
    )
    assert (
        {r["folio"].strip() for r in refined_rows}
        == {r["folio"].strip() for r in combined_rows}
    )


def test_coarse_class_refined_same_as_combined():
    # alias semântico: refinement reusa o mapa combinado do R64.
    for t in ("leaf", "root", "container", "nymph", "figure_roundel", "star", "whole_plant"):
        assert coarse_class_refined(t) == coarse_class_combined(t)
    assert coarse_class_refined("other") == "other"
    assert coarse_class_refined("") == "other"


def test_build_elements_refined_matches_combined_coarse_counts():
    # Sem mudar object_type/folio, build_elements (coarse_fn=refined) deve
    # produzir os MESMOS multisets de coarse que o R64.
    if not _refined_exists():
        pytest.skip("refined CSV not found")
    els = build_elements(load_refined(), coarse_fn=coarse_class_refined)
    assert len(els) == 171
    counts = collections.Counter(e["coarse"] for e in els)
    assert counts["figure"] == 48
    assert counts["vessel"] == 15
    assert counts["organ"] == 81
    assert counts["whole_plant"] == 17
    assert counts["sky"] == 9
    assert counts["other"] == 1


def test_read_r64_summary_returns_dict():
    # Lê o summary canônico do R64 e expõe métricas-chave para o delta vs refinement.
    if not Path(R64_SUMMARY_INPUT).exists():
        pytest.skip("R64 summary CSV not found")
    s = read_r64_summary()
    assert "best_feature" in s
    assert "best_p_within_folio" in s
    assert "pharma_test_p_within_folio" in s
    assert "nymph_p_divergent" in s


def test_read_r64_summary_missing_file_returns_empty(tmp_path):
    # Robustez: arquivo ausente -> dict vazio (testes/synth não devem quebrar).
    out = read_r64_summary(tmp_path / "no_such.csv")
    assert out == {}


def test_r64_per_feature_p_within_missing_file_returns_empty(tmp_path):
    assert _r64_per_feature_p_within(tmp_path / "no.csv") == {}


def test_main_refined_writes_both_csvs_with_guardrail(tmp_path):
    # E2E: main(['--refined', ...]) escreve ambos CSVs com o guardrail R65b e o
    # schema pedido (feature, subset, n, V, p_global, p_within_folio,
    # R64_p_within_folio, delta, guardrail) no test; summary com chaves do
    # coordenador. Seed fixa, n_perm baixo (rapidez).
    if not _refined_exists():
        pytest.skip("refined CSV not found")
    out_test = tmp_path / "rtest.csv"
    out_sum = tmp_path / "rsum.csv"
    rc = main([
        "--refined",
        "--out-test-refined", str(out_test),
        "--out-summary-refined", str(out_sum),
        "--n-perm", "300",
        "--seed", "65",
    ])
    assert rc == 0
    assert out_test.exists() and out_sum.exists()

    test_rows = list(csv.DictReader(out_test.open(encoding="utf-8")))
    assert len(test_rows) == 14  # 7 features x 2 subsets
    # schema EXATO do test CSV (inclui R64_p_within_folio + delta).
    for col in ("feature", "subset", "n", "cramer_v", "p_global",
                "p_within_folio", "R64_p_within_folio", "delta",
                "semantic_guardrail"):
        assert col in test_rows[0], f"missing column {col} in test CSV"
    subsets = {r["subset"] for r in test_rows}
    assert subsets == {"all", "non_uncertain"}
    for r in test_rows:
        assert r["semantic_guardrail"] == GUARDRAIL_REFINED
        assert 0.0 <= float(r["p_within_folio"]) <= 1.0
        assert 0.0 <= float(r["p_global"]) <= 1.0
    # all-rows feature tests rodam sobre n=171; non_uncertain sobre n=108.
    n_by_subset = {r["subset"]: int(r["n"]) for r in test_rows}
    assert n_by_subset["all"] == 171
    assert n_by_subset["non_uncertain"] == 108

    sum_rows = {r["metric"]: r["value"]
                for r in csv.DictReader(out_sum.open(encoding="utf-8"))}
    for key in (
        "n_total", "n_non_uncertain", "n_uncertain", "pct_uncertain",
        "best_feature", "best_p_within_folio_allrows",
        "best_p_within_folio_nonunc", "R64_best_p_within_folio",
        "pharma_p_within_folio", "R64_pharma_p_within_folio",
        "nymph_divergence_p", "R64_nymph_divergence_p",
        "verdict", "semantic_guardrail",
    ):
        assert key in sum_rows, f"missing summary metric {key}"
    assert sum_rows["n_total"] == "171"
    assert sum_rows["n_non_uncertain"] == "108"
    assert sum_rows["n_uncertain"] == "63"
    assert sum_rows["semantic_guardrail"] == GUARDRAIL_REFINED
    assert sum_rows["verdict"] in (
        "signal_emerged", "nymph_local_hardens", "decoupled_refined",
    )


def test_run_refined_returns_n_and_verdict(tmp_path):
    # Idem mas pela API direta de run_refined (chamado tb pelo coordenador).
    if not _refined_exists():
        pytest.skip("refined CSV not found")
    res = run_refined(
        str(tmp_path / "t.csv"),
        str(tmp_path / "s.csv"),
        n_perm=300,
        seed=65,
    )
    assert res["n_total"] == 171
    assert res["n_non_uncertain"] == 108
    assert res["n_uncertain"] == 63
    assert res["n_folios"] == 12
    assert res["verdict"] in (
        "signal_emerged", "nymph_local_hardens", "decoupled_refined",
    )
    assert res["pharma"]["n_vessel"] == 15
    assert res["nymph"]["n_nymph"] == 44


def test_main_refined_deterministic(tmp_path):
    # Mesma seed -> mesmos arquivos byte-a-byte (RNG seedado em tudo).
    if not _refined_exists():
        pytest.skip("refined CSV not found")

    def run(d):
        d.mkdir(parents=True, exist_ok=True)
        ot = d / "t.csv"
        os = d / "s.csv"
        main([
            "--refined",
            "--out-test-refined", str(ot),
            "--out-summary-refined", str(os),
            "--n-perm", "300",
            "--seed", "65",
        ])
        return ot.read_text(encoding="utf-8"), os.read_text(encoding="utf-8")

    a_test, a_sum = run(tmp_path / "a")
    b_test, b_sum = run(tmp_path / "b")
    assert a_test == b_test
    assert a_sum == b_sum


def test_refined_does_not_modify_annotation_csvs():
    # GUARDRAIL OPERACIONAL: o pipeline NUNCA pode reescrever a anotação refinada.
    # Roda run_refined (com out paths em tmp) e verifica que o conteúdo bruto da
    # anotação NÃO mudou.
    if not _refined_exists():
        pytest.skip("refined CSV not found")
    src = Path(REFINED_INPUT)
    before = src.read_bytes()
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        run_refined(
            str(Path(td) / "t.csv"),
            str(Path(td) / "s.csv"),
            n_perm=200,
            seed=65,
        )
    after = src.read_bytes()
    assert before == after
