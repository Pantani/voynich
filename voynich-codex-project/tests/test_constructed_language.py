"""Tests for assess_constructed_language.py (Rota 70).

A SYNTHESIS/POSITIONING route: it scores the constructed-language ("lingua ignota")
hypothesis against the closed ledger (R43-R69) and derives a verdict that is a PURE
FUNCTION of the scorecard tallies. No new corpus statistic is computed. Every
assertion checks the synthesis logic and the golden rule -- never meaning.
"""
from __future__ import annotations

import csv
from pathlib import Path

from scripts.assess_constructed_language import (
    CRITERIA,
    DEFAULT_CODICOLOGY,
    GUARDRAIL,
    apply_anchor,
    classify_verdict,
    load_codicology_anchor,
    main,
    parse_args,
    tally,
)


# --------------------------------------------------------------------------- #
# Scorecard integrity                                                          #
# --------------------------------------------------------------------------- #
def test_every_criterion_has_valid_effects():
    valid = {"supports", "weakens", "neutral"}
    assert len(CRITERIA) >= 8
    for c in CRITERIA:
        assert c["broad"] in valid
        assert c["hildegard"] in valid
        assert isinstance(c["caps"], bool)
        # each criterion cites a source route and a finding
        assert c["source"] and c["finding"]


def test_criterion_ids_unique():
    ids = [c["id"] for c in CRITERIA]
    assert len(ids) == len(set(ids))


def test_exactly_one_criterion_caps_confirmation():
    # the R62/R67 content-free generator is the single confirmability-capping fact
    capping = [c for c in CRITERIA if c["caps"]]
    assert len(capping) == 1
    assert capping[0]["id"] == "contentfree_generator_reproduces_signatures"


# --------------------------------------------------------------------------- #
# Tallies match the documented closed state                                    #
# --------------------------------------------------------------------------- #
def test_tally_sums_to_n_criteria():
    for key in ("broad", "hildegard"):
        t = tally(CRITERIA, key)
        assert sum(t.values()) == len(CRITERIA)


def test_broad_family_is_not_refuted():
    # H_broad (a constructed SYSTEM) has no weakening criterion -> family stays alive
    t = tally(CRITERIA, "broad")
    assert t["weakens"] == 0
    assert t["supports"] >= 1


def test_hildegard_model_is_weakened():
    # the specific glossed-noun model is outweighed by weakening evidence
    t = tally(CRITERIA, "hildegard")
    assert t["weakens"] > t["supports"]


# --------------------------------------------------------------------------- #
# Verdict is a pure function of its booleans (all branches reachable)          #
# --------------------------------------------------------------------------- #
def test_classify_verdict_all_branches():
    assert classify_verdict(False, True, False) == "constructed_family_refuted"
    assert classify_verdict(False, False, True) == "constructed_family_refuted"
    assert (
        classify_verdict(True, True, True) == "constructed_confirmable_by_statistics"
    )
    assert (
        classify_verdict(True, True, False)
        == "constructed_family_alive_hildegard_excluded_frozen"
    )
    assert (
        classify_verdict(True, False, False)
        == "constructed_family_alive_hildegard_open_frozen"
    )


def test_actual_state_verdict():
    # the closed-state booleans must yield the documented verdict
    t_broad = tally(CRITERIA, "broad")
    t_hild = tally(CRITERIA, "hildegard")
    family_alive = t_broad["weakens"] == 0
    hildegard_weakened = t_hild["weakens"] > t_hild["supports"]
    confirmable = not any(c["caps"] for c in CRITERIA)
    assert classify_verdict(family_alive, hildegard_weakened, confirmable) == (
        "constructed_family_alive_hildegard_excluded_frozen"
    )


# --------------------------------------------------------------------------- #
# Codicology anchor is optional and, when present, real                        #
# --------------------------------------------------------------------------- #
def test_anchor_absent_file_returns_empty(tmp_path):
    assert load_codicology_anchor(tmp_path / "nope.csv") == {}


def test_anchor_present_matches_real_codicology_summary():
    # the R68 summary exists in the repo; the anchor should read its verdict live
    if not Path(DEFAULT_CODICOLOGY).exists():
        return  # graceful: route still runs without the anchor
    anchor = load_codicology_anchor(Path(DEFAULT_CODICOLOGY))
    assert "verdict" in anchor
    # apply_anchor rewrites the production criterion's finding from live values
    crit = [dict(c) for c in CRITERIA]
    apply_anchor(crit, anchor)
    prod = next(c for c in crit if c["id"] == "serious_deliberate_production")
    assert anchor["verdict"] in prod["finding"]


# --------------------------------------------------------------------------- #
# main() writes both CSVs + the doc, all carrying the guardrail                #
# --------------------------------------------------------------------------- #
def test_main_writes_outputs_with_guardrail(tmp_path):
    out_score = tmp_path / "score.csv"
    out_summary = tmp_path / "summary.csv"
    md = tmp_path / "doc.md"
    rc = main(
        [
            str(DEFAULT_CODICOLOGY),
            "--out-scorecard",
            str(out_score),
            "--out-summary",
            str(out_summary),
            "--md",
            str(md),
        ]
    )
    assert rc == 0
    assert md.exists() and md.read_text(encoding="utf-8").strip()

    score = list(csv.DictReader(out_score.open(encoding="utf-8")))
    assert len(score) == len(CRITERIA)
    assert all(r["semantic_guardrail"] == GUARDRAIL for r in score)
    assert all(
        r["effect_on_broad"] in ("supports", "weakens", "neutral") for r in score
    )

    vals = {
        r["metric"]: r["value"]
        for r in csv.DictReader(out_summary.open(encoding="utf-8"))
    }
    assert vals["guardrail"] == GUARDRAIL
    assert vals["route_type"] == "synthesis_positioning_not_new_measurement"
    assert vals["verdict"] == "constructed_family_alive_hildegard_excluded_frozen"
    assert vals["family_alive"] == "True"
    assert vals["hildegard_weakened"] == "True"
    assert vals["confirmable_by_corpus_statistics"] == "False"


def test_summary_verdict_consistent_with_its_booleans(tmp_path):
    out_summary = tmp_path / "summary.csv"
    main(
        [
            str(DEFAULT_CODICOLOGY),
            "--out-scorecard",
            str(tmp_path / "s.csv"),
            "--out-summary",
            str(out_summary),
            "--md",
            str(tmp_path / "d.md"),
        ]
    )
    vals = {
        r["metric"]: r["value"]
        for r in csv.DictReader(out_summary.open(encoding="utf-8"))
    }
    family = vals["family_alive"] == "True"
    hild = vals["hildegard_weakened"] == "True"
    conf = vals["confirmable_by_corpus_statistics"] == "True"
    assert vals["verdict"] == classify_verdict(family, hild, conf)
    # tallies in the summary must add up to the number of criteria
    assert (
        int(vals["broad_supports"])
        + int(vals["broad_weakens"])
        + int(vals["broad_neutral"])
        == int(vals["n_criteria"])
    )


def test_parse_args_defaults_point_into_derived():
    args = parse_args([])
    assert args.out_scorecard.endswith("constructed_language_scorecard_zl3b.csv")
    assert args.out_summary.endswith("constructed_language_summary_zl3b.csv")
    assert args.md.endswith("rota_71_lingua_construida.md")


# --------------------------------------------------------------------------- #
# Golden rule: the summary makes no meaning claim                              #
# --------------------------------------------------------------------------- #
def test_golden_rule_no_meaning_words(tmp_path):
    out_summary = tmp_path / "summary.csv"
    main(
        [
            str(DEFAULT_CODICOLOGY),
            "--out-scorecard",
            str(tmp_path / "s.csv"),
            "--out-summary",
            str(out_summary),
            "--md",
            str(tmp_path / "d.md"),
        ]
    )
    banned = (" means ", "translates to", "meaning of", "stands for")
    text = out_summary.read_text(encoding="utf-8").lower()
    for b in banned:
        assert b not in text
    # guardrail negation present (not an affirmative decipherment claim)
    assert "not_decipherment" in text
    assert GUARDRAIL in text
    # the route explicitly disclaims new measurement and meaning
    assert "synthesis_positioning_not_new_measurement" in text
    assert "assigns no meaning to any token" in text
