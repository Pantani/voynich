from collections import Counter

from scripts.analyze_matrix_controls import (
    chi_square_independence,
    contingency,
    exact_family_counts,
    expected_suffix_by_locus_given_prefix,
)


def test_chi_square_independence_detects_balanced_table():
    table = {
        "P": Counter({"ar": 5, "ol": 5}),
        "C": Counter({"ar": 5, "ol": 5}),
    }

    result = chi_square_independence(table)

    assert result.statistic == 0
    assert result.degrees_of_freedom == 1
    assert result.cramers_v == 0


def test_contingency_and_exact_family_counts():
    rows = [
        {"locus_kind": "P", "suffix": "ar", "token": "okar", "target_status": "exact"},
        {"locus_kind": "P", "suffix": "al", "token": "okal", "target_status": "exact"},
        {"locus_kind": "C", "suffix": "ol", "token": "qokol", "target_status": "exact"},
        {"locus_kind": "C", "suffix": "ol", "token": "cheol", "target_status": "broad"},
    ]

    table = contingency(rows, "locus_kind")
    families = {row["family"]: row for row in exact_family_counts(rows)}

    assert table["P"]["ar"] == 1
    assert table["C"]["ol"] == 2
    assert families["ok"]["total"] == "2"
    assert families["qok"]["qokol"] == "1"


def test_prefix_controlled_expected_counts_preserve_totals():
    rows = [
        {"prefix": "ok", "locus_kind": "P", "suffix": "ar"},
        {"prefix": "ok", "locus_kind": "P", "suffix": "ol"},
        {"prefix": "ok", "locus_kind": "C", "suffix": "ar"},
        {"prefix": "ok", "locus_kind": "C", "suffix": "ol"},
        {"prefix": "qok", "locus_kind": "P", "suffix": "al"},
        {"prefix": "qok", "locus_kind": "C", "suffix": "al"},
    ]

    expected = expected_suffix_by_locus_given_prefix(rows)

    assert sum(expected["P"].values()) == 3
    assert sum(expected["C"].values()) == 3
    assert expected["P"]["ar"] == 1
    assert expected["P"]["ol"] == 1
    assert expected["P"]["al"] == 1
