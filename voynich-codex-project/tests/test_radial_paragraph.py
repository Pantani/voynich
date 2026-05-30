"""Tests for Rota 65 Leg A — radial/circular vs paragraph text contrast.

Pinned invariants of ``scripts/analyze_radial_paragraph.py``:
  * The kind-aware parser reproduces the full ZL3b token total (37671).
  * Each KIND letter maps to the committed coarse class (P->paragraph,
    C/R->radial, L->label).
  * Token features (prefix / nucleus / length_bucket) extract deterministic
    buckets — used by the headline contrast.
  * Cramer's V matches a hand-computed answer on a synthetic 2x2.
  * The within-folio shuffle preserves the per-folio class counts (so the
    within-folio null only measures token<->class assignment, not class
    abundance per folio — the decisive control against section vocabulary).
  * main() writes all three CSVs with the guardrail column populated.
"""
from __future__ import annotations

import collections
import csv
import random
from pathlib import Path

from scripts.analyze_nucleus_context import parse_corpus_with_kind
from scripts.analyze_radial_paragraph import (
    CLASSES,
    FEATURES,
    GUARDRAIL,
    KIND_TO_CLASS,
    char_h2,
    coarse_class,
    cramer_v,
    folios_with_both,
    length_bucket,
    main,
    nucleus_of,
    per_class_distribution,
    per_folio_label_paragraph_test,
    per_folio_radial_paragraph_test,
    permutation_pvalues,
    prefix_of,
    restrict_to_radial_paragraph,
    _within_folio_shuffle,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"


# ------------------------------------------------------------------
# Parsing + coarse-class invariants
# ------------------------------------------------------------------
def test_parse_corpus_reproduces_37671_and_kind_mapping_is_committed():
    records = parse_corpus_with_kind(CORPUS)
    assert len(records) == 37671  # pinned ZL3b token count

    # All KIND letters seen in ZL3b that drive the contrast are mapped exactly:
    assert coarse_class("P") == "paragraph"
    assert coarse_class("C") == "radial"
    assert coarse_class("R") == "radial"
    assert coarse_class("L") == "label"
    # anything else -> 'other' (so the verdict is not df-inflated)
    assert coarse_class("X") == "other"
    assert coarse_class("?") == "other"

    # The class universe used downstream is exactly the four committed classes:
    assert set(CLASSES) == {"paragraph", "radial", "label", "other"}
    assert set(KIND_TO_CLASS.values()) == {"paragraph", "radial", "label"}


def test_per_class_counts_match_independent_kind_partition():
    records = parse_corpus_with_kind(CORPUS)
    dist = per_class_distribution(records)
    # independent partition: count each token by its kind -> coarse class
    expected: dict[str, int] = collections.Counter()
    for _f, kind, _t in records:
        expected[coarse_class(kind)] += 1
    for cls in CLASSES:
        assert dist[cls]["n"] == expected.get(cls, 0)
    # paragraph is the dominant class in ZL3b
    assert dist["paragraph"]["n"] > dist["radial"]["n"]
    assert dist["paragraph"]["n"] > dist["label"]["n"]


# ------------------------------------------------------------------
# Feature extraction correctness
# ------------------------------------------------------------------
def test_feature_extractors_bucket_tokens_deterministically():
    # prefix: only the first 2 chars when in the committed bucket, else 'none'
    assert prefix_of("qokeey") == "qo"
    assert prefix_of("okary") == "ok"
    assert prefix_of("otedy") == "ot"
    assert prefix_of("ykchys") == "yk"
    assert prefix_of("ytchey") == "yt"
    assert prefix_of("daiin") == "none"
    assert prefix_of("") == "none"

    # nucleus: ch / sh / none, XOR by token; both present -> the earlier hit
    assert nucleus_of("chedy") == "ch"
    assert nucleus_of("shedy") == "sh"
    assert nucleus_of("okary") == "none"
    assert nucleus_of("chsh") == "ch"  # ch occurs earlier
    assert nucleus_of("shch") == "sh"

    # length_bucket: short<=4 / mid 5-6 / long>=7  (matches R63/R64)
    assert length_bucket("ar") == "short"
    assert length_bucket("daiin") == "mid"
    assert length_bucket("chedy") == "mid"
    assert length_bucket("ykeody") == "mid"
    assert length_bucket("qokeedy") == "long"

    # FEATURES dict contains exactly the three contrast features (order matters).
    assert list(FEATURES) == ["prefix", "nucleus", "length_bucket"]


# ------------------------------------------------------------------
# Stats helpers
# ------------------------------------------------------------------
def test_cramer_v_on_synthetic_2x2_matches_hand_computation():
    # Perfectly associated 2x2: V should be exactly 1.0 (chi2 = N, k-1 = 1).
    perfect: dict[str, collections.Counter] = {
        "row_A": collections.Counter({"col_X": 50, "col_Y": 0}),
        "row_B": collections.Counter({"col_X": 0, "col_Y": 50}),
    }
    v, n = cramer_v(perfect)
    assert n == 100
    assert abs(v - 1.0) < 1e-9

    # Independent 2x2 (rows = columns marginals proportional) -> V = 0.
    independent: dict[str, collections.Counter] = {
        "row_A": collections.Counter({"col_X": 25, "col_Y": 25}),
        "row_B": collections.Counter({"col_X": 25, "col_Y": 25}),
    }
    v_ind, n_ind = cramer_v(independent)
    assert n_ind == 100
    assert abs(v_ind) < 1e-9

    # Small N (<4) -> V = 0 by design (matches analyze_nucleus.cramer_v).
    tiny: dict[str, collections.Counter] = {
        "row_A": collections.Counter({"col_X": 1}),
        "row_B": collections.Counter({"col_Y": 1}),
    }
    assert cramer_v(tiny) == (0.0, 2)

    # char_h2 is deterministic and bounded; identical content -> small h2.
    h_same = char_h2(["aaaa", "aaaa"])
    h_mixed = char_h2(["chedy", "okary", "shey", "daiin", "qokeey"])
    assert 0.0 <= h_same < h_mixed


# ------------------------------------------------------------------
# Decisive control: within-folio shuffle preserves per-folio class counts
# ------------------------------------------------------------------
def test_within_folio_shuffle_preserves_per_folio_class_counts():
    # 3 folios, two classes; check shuffle preserves per-folio counts exactly.
    folios = (
        ["fA"] * 6  # 4 paragraph + 2 radial
        + ["fB"] * 4  # 1 paragraph + 3 radial
        + ["fC"] * 5  # 5 paragraph + 0 radial
    )
    classes = (
        ["paragraph"] * 4 + ["radial"] * 2
        + ["paragraph"] + ["radial"] * 3
        + ["paragraph"] * 5
    )
    pre_counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for f, c in zip(folios, classes):
        pre_counts[f][c] += 1

    for seed in (0, 1, 2, 65, 123):
        rng = random.Random(seed)
        shuffled = _within_folio_shuffle(classes, folios, rng)
        # Same length, same multiset overall
        assert len(shuffled) == len(classes)
        assert collections.Counter(shuffled) == collections.Counter(classes)
        # KEY invariant: per-folio class counts are identical to observed
        post_counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
        for f, c in zip(folios, shuffled):
            post_counts[f][c] += 1
        for fo in pre_counts:
            assert post_counts[fo] == pre_counts[fo]


def test_permutation_pvalues_returns_p_in_half_open_unit_interval_and_n_matches():
    # Tiny deterministic dataset; just check the contract of the function.
    elements = [
        ("fA", "paragraph", "qokeedy"),
        ("fA", "paragraph", "chedy"),
        ("fA", "radial", "okary"),
        ("fA", "radial", "shey"),
        ("fB", "paragraph", "daiin"),
        ("fB", "radial", "otaiin"),
        ("fB", "radial", "okol"),
        ("fB", "paragraph", "ar"),
    ]
    v, p_g, p_w, n = permutation_pvalues(elements, "prefix", 50, seed=42)
    assert n == 8
    assert 0.0 <= v <= 1.0
    # +1 convention: p in (0, 1]
    assert 0.0 < p_g <= 1.0
    assert 0.0 < p_w <= 1.0


# ------------------------------------------------------------------
# folios_with_both + per-folio test
# ------------------------------------------------------------------
def test_folios_with_both_finds_the_cosmological_set_and_drives_focus_folio():
    records = parse_corpus_with_kind(CORPUS)
    both = folios_with_both(records, "paragraph", "radial")
    # cosmological star/zodiac folios that mix prose + ring text in ZL3b
    expected = {
        "f67r1", "f67v2", "f68r1", "f68r2", "f68v2", "f68v3",
        "f69r", "f70r2", "f85r2", "f86v4",
    }
    assert set(both) == expected

    # On these folios the headline universe is non-trivial and finite
    hd_within = restrict_to_radial_paragraph(records, both)
    assert len(hd_within) > 0
    assert all(c in ("paragraph", "radial") for _f, c, _t in hd_within)
    assert all(f in expected for f, _c, _t in hd_within)


def test_per_folio_test_returns_zero_when_one_class_missing():
    # f1r is paragraph-only -> no radial -> the per-folio test must
    # return a no-op (V=0, p=1) per the falsifiable contract.
    records = parse_corpus_with_kind(CORPUS)
    r = per_folio_radial_paragraph_test(records, "f1r", "prefix", 30, seed=7)
    assert r["folio"] == "f1r"
    assert r["n_radial"] == 0
    assert r["cramer_v"] == 0.0
    assert r["p_within_folio"] == 1.0


def test_focus_label_vs_paragraph_sees_f67r2_moon_labels():
    # R50 framing: f67r2 carries paragraph (P) + label (L) moon-label loci.
    # The label-vs-paragraph focus test must see both > 0 (and the radial
    # variant must report n_radial == 0 on this folio).
    records = parse_corpus_with_kind(CORPUS)
    r_label = per_folio_label_paragraph_test(records, "f67r2", "prefix", 50, seed=99)
    assert r_label["folio"] == "f67r2"
    assert r_label["n_paragraph"] > 0
    assert r_label["n_label"] > 0
    r_radial = per_folio_radial_paragraph_test(records, "f67r2", "prefix", 50, seed=99)
    assert r_radial["n_radial"] == 0  # f67r2 has no C/R loci


def test_per_folio_test_finds_both_classes_on_cosmological_folio():
    # f67r1 carries both paragraph (P) AND radial (Ri) loci; the per-folio
    # test must SEE both classes and return non-zero counts (regression guard:
    # earlier the function was comparing the IVTFF kind letter directly to
    # the coarse class name and silently produced n=0 everywhere).
    records = parse_corpus_with_kind(CORPUS)
    r = per_folio_radial_paragraph_test(records, "f67r1", "prefix", 50, seed=11)
    assert r["folio"] == "f67r1"
    assert r["n_paragraph"] > 0
    assert r["n_radial"] > 0
    assert r["n"] == r["n_paragraph"] + r["n_radial"]
    # And the per-folio universe matches the headline restriction
    hd = restrict_to_radial_paragraph(records, ["f67r1"])
    assert len(hd) == r["n"]


# ------------------------------------------------------------------
# main() writes three CSVs with the guardrail column populated
# ------------------------------------------------------------------
def test_main_writes_three_csvs_with_guardrail_and_verdict(tmp_path):
    distribution = tmp_path / "dist.csv"
    test = tmp_path / "test.csv"
    summary = tmp_path / "summary.csv"
    rc = main(
        [
            str(CORPUS),
            "--n-perm",
            "30",
            "--out-distribution",
            str(distribution),
            "--out-test",
            str(test),
            "--out-summary",
            str(summary),
        ]
    )
    assert rc == 0
    for p in (distribution, test, summary):
        assert p.exists() and p.stat().st_size > 0
        assert GUARDRAIL in p.read_text(encoding="utf-8")

    # distribution: one row per class, with guardrail per row
    with distribution.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert {r["class"] for r in rows} == set(CLASSES)
    assert all(r["semantic_guardrail"] == GUARDRAIL for r in rows)
    par_row = next(r for r in rows if r["class"] == "paragraph")
    assert int(par_row["n"]) > 0
    assert par_row["top_token"]
    # prefix/nucleus/length distributions are populated triplets
    assert ";" in par_row["prefix_distribution"]
    assert ";" in par_row["nucleus_distribution"]
    assert ";" in par_row["length_distribution"]

    # test.csv has global, within_folio_universe, per_folio and the two
    # focus rows (radial-vs-paragraph + label-vs-paragraph) for f67r2.
    with test.open(encoding="utf-8") as f:
        test_rows = list(csv.DictReader(f))
    scopes = {r["scope"] for r in test_rows}
    assert {
        "global",
        "within_folio_universe",
        "per_folio",
        "focus_folio",
        "focus_folio_label",
    } <= scopes
    focus_rows = [r for r in test_rows if r["scope"] == "focus_folio"]
    assert focus_rows and focus_rows[0]["folio"] == "f67r2"
    label_rows = [r for r in test_rows if r["scope"] == "focus_folio_label"]
    assert label_rows and label_rows[0]["folio"] == "f67r2"

    # summary must carry the verdict, headline counts, focus result, guardrail
    text = summary.read_text(encoding="utf-8")
    for metric in (
        "n_paragraph",
        "n_radial",
        "n_label",
        "n_folios_with_both",
        "best_feature_within_folio",
        "best_feature_V_within_folio",
        "best_feature_p_within_folio",
        "verdict",
        "focus_folio",
        "focus_radial_p_within_folio",
        "focus_label_p_within_folio",
        "focus_confirms_R50",
        "n_perm",
        "seed",
        "semantic_guardrail",
    ):
        assert metric in text

    with summary.open(encoding="utf-8") as f:
        srows = {r["metric"]: r["value"] for r in csv.DictReader(f)}
    # verdict is one of the two committed strings
    assert srows["verdict"] in ("radial_paragraph_differ", "no_difference")
    # counts are coherent with the per-class distribution
    assert int(srows["n_paragraph"]) == int(par_row["n"])
