from scripts.consolidate_manual_svg_review import (
    build_consolidated_rows,
    coordinate_status,
    final_outcome,
    summarize_rows,
)


def test_coordinate_status_requires_complete_positive_numbers():
    complete = {
        "manual_tighter_x": "12",
        "manual_tighter_y": "34",
        "manual_tighter_width": "56",
        "manual_tighter_height": "78",
    }
    incomplete = {
        "manual_tighter_x": "12",
        "manual_tighter_y": "",
        "manual_tighter_width": "56",
        "manual_tighter_height": "78",
    }
    invalid = {
        "manual_tighter_x": "12",
        "manual_tighter_y": "34",
        "manual_tighter_width": "0",
        "manual_tighter_height": "78",
    }

    assert coordinate_status(complete) == "manual_coordinates_complete"
    assert coordinate_status(incomplete) == "incomplete_manual_coordinates"
    assert coordinate_status(invalid) == "invalid_manual_coordinates"


def test_pending_manual_review_is_not_glyph_confirmation():
    row = {
        "manual_final_status": "pending_manual_review",
        "manual_tighter_x": "",
        "manual_tighter_y": "",
        "manual_tighter_width": "",
        "manual_tighter_height": "",
    }

    outcome = final_outcome(row)

    assert outcome["consolidation_outcome"] == "pending_manual_review"
    assert outcome["coordinate_status"] == "no_manual_coordinates"
    assert outcome["evidence_status"] == "no_glyph_confirmation"
    assert outcome["axis_test_eligibility"] == "not_eligible"


def test_confirmed_region_requires_complete_coordinates():
    row = {
        "manual_final_status": "confirmed_tighter_region",
        "manual_tighter_x": "10",
        "manual_tighter_y": "20",
        "manual_tighter_width": "30",
        "manual_tighter_height": "40",
    }

    outcome = final_outcome(row)

    assert outcome["consolidation_outcome"] == "confirmed_tighter_region"
    assert outcome["coordinate_status"] == "manual_coordinates_complete"
    assert outcome["evidence_status"] == "tighter_region_confirmed"
    assert outcome["axis_test_eligibility"] == "eligible_after_manual_review"


def test_build_consolidated_rows_preserves_manual_identity():
    rows = [
        {
            "manual_review_id": "R9-001",
            "decision_id": "R8-009",
            "crop_id": "R7-009",
            "source_review_id": "R6-009",
            "folio": "f67r1",
            "locus": "f67r1.5,@Cc",
            "prefix_family": "ot",
            "group_tokens": "otardar otor",
            "manual_final_status": "pending_manual_review",
            "manual_tighter_x": "",
            "manual_tighter_y": "",
            "manual_tighter_width": "",
            "manual_tighter_height": "",
        }
    ]

    consolidated = build_consolidated_rows(rows)

    assert consolidated[0]["route10_id"] == "R10-001"
    assert consolidated[0]["manual_review_id"] == "R9-001"
    assert consolidated[0]["crop_id"] == "R7-009"
    assert consolidated[0]["consolidation_outcome"] == "pending_manual_review"


def test_summarize_rows_counts_pending_and_eligible_rows():
    rows = [
        {
            "consolidation_outcome": "pending_manual_review",
            "coordinate_status": "no_manual_coordinates",
            "evidence_status": "no_glyph_confirmation",
            "axis_test_eligibility": "not_eligible",
        },
        {
            "consolidation_outcome": "confirmed_tighter_region",
            "coordinate_status": "manual_coordinates_complete",
            "evidence_status": "tighter_region_confirmed",
            "axis_test_eligibility": "eligible_after_manual_review",
        },
    ]

    summary = summarize_rows(rows)

    assert summary["consolidation_outcome"]["pending_manual_review"] == 1
    assert summary["consolidation_outcome"]["confirmed_tighter_region"] == 1
    assert summary["axis_test_eligibility"]["eligible_after_manual_review"] == 1
