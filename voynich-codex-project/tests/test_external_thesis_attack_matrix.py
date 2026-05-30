"""Tests for Rota 66 external-thesis attack matrix (analyze_external_thesis_attack_matrix.py).

R62 proved the token-scale battery is degenerate: a content-free local generator
reproduces 13/14 of Voynich's signatures, so corpus statistics cannot separate
"designed-with-meaning" from "generator" -- EXCEPT on the one signature the
generator under-shoots (laafu_I, real 0.471 vs gen 0.303). This route formalizes
the team's pre-registered decision rule over every external thesis and VALIDATES
it against the generator's OWN output (non-circular). The tests pin:

  - the matrix is the 13-row table with unique ids 1..13 and only-valid verdicts;
  - load_generator_baseline reads the REAL generator CSVs -> RESISTING_SET={laafu_I},
    n_metrics=14, n_matched=13, laafu_real>laafu_gen, gap~0.168;
  - the consistency invariants hold for ALL rows, including the NON-CIRCULAR check
    (resists_generator => discriminating_signal in RESISTING_SET read from the CSV);
  - exactly one thesis (9, on laafu_I) beats the generator;
  - exactly 6 theses are refuted_by_instrument, and they are {1,2,3,5,10,13};
  - the verdict tally equals the expected counts;
  - main() writes BOTH CSVs with guardrail + required columns;
  - the GOLDEN RULE: no output cell asserts a translation / meaning.

Generation is deterministic (no Date/random). The generator-baseline test reuses
the real CSVs at data/derived/.
"""
from __future__ import annotations

import csv
from pathlib import Path

from scripts.analyze_external_thesis_attack_matrix import (
    GENERATOR_REPRODUCED,
    GUARDRAIL,
    MATRIX_FIELDS,
    NO_TRANSLATION_CLAIM,
    SIGNAL_CLASSES,
    THESES,
    VERDICTS,
    beats_generator,
    build_matrix_rows,
    build_summary_rows,
    load_generator_baseline,
    main,
    refuted_by_instrument,
)

ROOT = Path(__file__).resolve().parents[1]
GEN_SUMMARY = ROOT / "data" / "derived" / "generator_summary_zl3b.csv"
GEN_MATCH = ROOT / "data" / "derived" / "generator_match_zl3b.csv"

# The non-circular resisting set, loaded once from the real generator output.
_BASELINE = load_generator_baseline(GEN_SUMMARY, GEN_MATCH)
_RESISTING = _BASELINE["resisting_set"]


def _rows():
    return build_matrix_rows(_RESISTING)


# --------------------------------------------------------------------------- #
# (a) the matrix has 13 rows, unique ids 1..13, all-valid verdicts             #
# --------------------------------------------------------------------------- #
def test_matrix_has_13_rows_unique_ids_valid_verdicts():
    rows = _rows()
    assert len(rows) == 13
    ids = [r["thesis_id"] for r in rows]
    assert ids == list(range(1, 14))  # exactly 1..13, in order, no dupes
    assert len(set(ids)) == 13
    for r in rows:
        assert r["verdict"] in VERDICTS
        assert r["signal_class"] in SIGNAL_CLASSES
        assert r["semantic_guardrail"] == GUARDRAIL
    # the raw data table agrees on count/ids before any computation
    assert [t["thesis_id"] for t in THESES] == list(range(1, 14))
    # the 13 reproduced signatures are exactly the documented panel
    assert len(GENERATOR_REPRODUCED) == 13
    assert "laafu_I" not in GENERATOR_REPRODUCED  # the one the generator FAILS


# --------------------------------------------------------------------------- #
# (b) load_generator_baseline reads the REAL generator CSVs                     #
# --------------------------------------------------------------------------- #
def test_load_generator_baseline_reads_real_csvs():
    b = load_generator_baseline(GEN_SUMMARY, GEN_MATCH)
    assert b["resisting_set"] == {"laafu_I"}
    assert b["n_metrics"] == 14
    assert b["n_matched"] == 13
    # the laafu anchor: real over-shoots the content-free generator by ~0.168
    assert b["laafu_real"] > b["laafu_gen"]
    assert abs(b["laafu_real"] - 0.471) < 0.01
    assert abs(b["laafu_gen"] - 0.303) < 0.01
    assert abs(b["laafu_gap"] - 0.168) < 0.01
    # gap is consistent with real-gen
    assert abs(b["laafu_gap"] - (b["laafu_real"] - b["laafu_gen"])) < 1e-6
    assert b["gen_verdict"] == "generator_insufficient"


def test_load_generator_baseline_handles_none(tmp_path):
    """key_metrics_resisting == 'none' must parse to an EMPTY resisting set (so a
    fully-sufficient generator would leave no signature for any thesis to resist)."""
    s = tmp_path / "summary.csv"
    m = tmp_path / "match.csv"
    with s.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "value"])
        w.writerow(["n_metrics", "14"])
        w.writerow(["n_matched", "14"])
        w.writerow(["key_metrics_resisting", "none"])
        w.writerow(["verdict", "generator_sufficient"])
    with m.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["metric", "real", "generator", "abs_delta"])
        w.writerow(["laafu_I", "0.47", "0.47", "0.0"])
    b = load_generator_baseline(s, m)
    assert b["resisting_set"] == set()


# --------------------------------------------------------------------------- #
# (c) consistency invariants hold for ALL rows (incl. the non-circular check)   #
# --------------------------------------------------------------------------- #
def test_consistency_invariants_hold_for_all_rows():
    rows = _rows()
    for r in rows:
        sclass = r["signal_class"]
        # the two booleans are the COMPUTED functions of the class
        assert r["beats_generator"] == beats_generator(sclass)
        assert r["refuted_by_instrument"] == refuted_by_instrument(sclass)
        # refuted_by_instrument <=> verdict == refuted
        assert r["refuted_by_instrument"] == (r["verdict"] == "refuted")
        # beats_generator <=> verdict == actionable
        assert r["beats_generator"] == (r["verdict"] == "actionable")
        # NON-CIRCULAR: resists_generator => discriminator in the generator's resisting set
        if sclass == "resists_generator":
            assert r["discriminating_signal"] in _RESISTING


def test_non_circular_check_rejects_unearned_discriminator():
    """If the generator's resisting set did NOT include laafu_I, thesis 9's
    resists_generator claim would be UNEARNED and build_matrix_rows must refuse it.
    This proves the check is grounded in the loaded set, not self-certified."""
    import pytest

    with pytest.raises(AssertionError):
        build_matrix_rows(set())  # empty: laafu_I not earned -> thesis 9 fails


# --------------------------------------------------------------------------- #
# (d) exactly one thesis beats the generator, and it is thesis 9 / laafu_I      #
# --------------------------------------------------------------------------- #
def test_exactly_one_thesis_beats_generator_and_it_is_9():
    rows = _rows()
    beaters = [r for r in rows if r["beats_generator"]]
    assert len(beaters) == 1
    only = beaters[0]
    assert only["thesis_id"] == 9
    assert only["discriminating_signal"] == "laafu_I"
    assert only["signal_class"] == "resists_generator"
    assert only["verdict"] == "actionable"
    # and laafu_I is exactly the generator's documented resisting signature
    assert only["discriminating_signal"] in _RESISTING


# --------------------------------------------------------------------------- #
# (e) exactly 6 refuted_by_instrument, and they are {1,2,3,5,10,13}             #
# --------------------------------------------------------------------------- #
def test_exactly_six_refuted_by_instrument_correct_ids():
    rows = _rows()
    refuted_ids = {r["thesis_id"] for r in rows if r["refuted_by_instrument"]}
    assert refuted_ids == {1, 2, 3, 5, 10, 13}
    assert len(refuted_ids) == 6
    # refuted_by_instrument is exactly the contradicted_by_corpus class
    for r in rows:
        assert r["refuted_by_instrument"] == (r["signal_class"] == "contradicted_by_corpus")


# --------------------------------------------------------------------------- #
# (f) the verdict tally equals the expected counts                             #
# --------------------------------------------------------------------------- #
def test_verdict_tally_matches_expected():
    rows = _rows()
    tally = {v: 0 for v in VERDICTS}
    for r in rows:
        tally[r["verdict"]] += 1
    assert tally == {
        "refuted": 6,
        "unsupported": 2,
        "survives_weakly": 3,
        "actionable": 1,
        "external_only": 1,
    }
    # and the explicit id partitions
    by_v = {v: sorted(r["thesis_id"] for r in rows if r["verdict"] == v) for v in VERDICTS}
    assert by_v["refuted"] == [1, 2, 3, 5, 10, 13]
    assert by_v["unsupported"] == [4, 6]
    assert by_v["survives_weakly"] == [7, 8, 12]
    assert by_v["actionable"] == [9]
    assert by_v["external_only"] == [11]


# --------------------------------------------------------------------------- #
# (g) main() writes BOTH CSVs with guardrail + required columns                 #
# --------------------------------------------------------------------------- #
def test_main_writes_both_csvs_with_guardrail(tmp_path):
    matrix = tmp_path / "matrix.csv"
    summary = tmp_path / "summary.csv"
    rc = main(
        [
            "--gen-summary", str(GEN_SUMMARY),
            "--gen-match", str(GEN_MATCH),
            "--out-matrix", str(matrix),
            "--out-summary", str(summary),
        ]
    )
    assert rc == 0
    for p in (matrix, summary):
        assert p.exists() and p.stat().st_size > 0
        assert GUARDRAIL in p.read_text(encoding="utf-8")

    # matrix CSV: 13 rows, required columns, guardrail on every row
    with matrix.open(encoding="utf-8") as f:
        mrows = list(csv.DictReader(f))
    assert len(mrows) == 13
    for r in mrows:
        assert set(MATRIX_FIELDS) <= set(r)
        assert r["semantic_guardrail"] == GUARDRAIL
        assert r["verdict"] in VERDICTS
        assert r["beats_generator"] in {"True", "False"}
        assert r["refuted_by_instrument"] in {"True", "False"}
    # exactly one beater in the written file, and it is thesis 9
    beaters = [r for r in mrows if r["beats_generator"] == "True"]
    assert len(beaters) == 1 and beaters[0]["thesis_id"] == "9"

    # summary CSV: required metrics, n_theses==13, n_beats_generator==1
    with summary.open(encoding="utf-8") as f:
        s = {r["metric"]: r["value"] for r in csv.DictReader(f)}
    assert s["guardrail"] == GUARDRAIL
    assert int(s["n_theses"]) == 13
    assert int(s["n_beats_generator"]) == 1
    assert int(s["n_refuted_by_instrument"]) == 6
    assert s["generator_resisting"] == "laafu_I"
    assert int(s["generator_n_metrics"]) == 14
    assert int(s["generator_n_matched"]) == 13
    assert s["actionable_theses"] == "9"
    assert s["dead_theses"] == "1,2,3,5,10,13"
    assert s["external_only_theses"] == "11"
    assert s["verdict"] == "1of13_beats_contentfree_generator"
    # the laafu anchor is echoed in the summary
    assert abs(float(s["laafu_real"]) - 0.471) < 0.01
    assert abs(float(s["laafu_gen"]) - 0.303) < 0.01
    assert abs(float(s["laafu_gap"]) - 0.168) < 0.01


def test_main_deterministic_same_bytes(tmp_path):
    """No Date/random anywhere: two runs produce byte-identical CSVs."""
    a1, a2 = tmp_path / "a1.csv", tmp_path / "a2.csv"
    s1, s2 = tmp_path / "s1.csv", tmp_path / "s2.csv"
    main(["--gen-summary", str(GEN_SUMMARY), "--gen-match", str(GEN_MATCH),
          "--out-matrix", str(a1), "--out-summary", str(s1)])
    main(["--gen-summary", str(GEN_SUMMARY), "--gen-match", str(GEN_MATCH),
          "--out-matrix", str(a2), "--out-summary", str(s2)])
    assert a1.read_bytes() == a2.read_bytes()
    assert s1.read_bytes() == s2.read_bytes()


# --------------------------------------------------------------------------- #
# (h) GOLDEN RULE: no output cell asserts a translation / meaning              #
# --------------------------------------------------------------------------- #
def test_golden_rule_no_translation_or_meaning_claim():
    """The script encodes verdicts about STRUCTURE, never meaning. Assert the
    banned phrases 'means' / 'translates to' never appear in any verdict or
    headline field, and that the contract constant exists and is structure-only."""
    rows = _rows()
    summary_rows = build_summary_rows(rows, _BASELINE)
    summ = {r["metric"]: r["value"] for r in summary_rows}

    banned = ("means", "translates to")
    # verdict fields (per-thesis) carry no meaning claim
    for r in rows:
        low = r["verdict"].lower()
        assert not any(b in low for b in banned), r["verdict"]
    # the headline + summary verdict carry no meaning claim
    for key in ("headline", "verdict"):
        low = summ[key].lower()
        assert not any(b in low for b in banned), (key, summ[key])

    # the contract constant exists and is itself structure-only (no meaning words)
    assert isinstance(NO_TRANSLATION_CLAIM, str) and NO_TRANSLATION_CLAIM
    low = NO_TRANSLATION_CLAIM.lower()
    assert "structure" in low
    assert "never" in low and "translation" in low
    # verdict values are the controlled vocabulary, not free-text meaning
    assert set(r["verdict"] for r in rows) <= set(VERDICTS)
