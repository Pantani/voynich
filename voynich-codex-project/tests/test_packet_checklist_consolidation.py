from scripts.consolidate_packet_item_checklist import (
    build_consolidated_rows,
    coordinate_status,
    final_outcome,
    normalize_flag,
    summarize_rows,
)


def test_normalize_flag_preserves_blank_and_allowed_values():
    assert normalize_flag("") == "blank"
    assert normalize_flag("yes") == "yes"
    assert normalize_flag("no") == "no"
    assert normalize_flag("uncertain") == "uncertain"
    assert normalize_flag("maybe") == "invalid"


def test_coordinate_status_requires_new_crop_flag_for_coordinates():
    blank = {
        "manual_new_crop_needed": "",
        "manual_new_crop_x": "",
        "manual_new_crop_y": "",
        "manual_new_crop_width": "",
        "manual_new_crop_height": "",
    }
    complete = {
        "manual_new_crop_needed": "yes",
        "manual_new_crop_x": "10",
        "manual_new_crop_y": "20",
        "manual_new_crop_width": "30",
        "manual_new_crop_height": "40",
    }
    missing_flag = {
        "manual_new_crop_needed": "",
        "manual_new_crop_x": "10",
        "manual_new_crop_y": "20",
        "manual_new_crop_width": "30",
        "manual_new_crop_height": "40",
    }

    assert coordinate_status(blank) == "no_new_crop_coordinates"
    assert coordinate_status(complete) == "new_crop_coordinates_complete"
    assert coordinate_status(missing_flag) == "coordinates_without_new_crop_flag"


def test_blank_checklist_row_stays_pending_without_evidence():
    row = {
        "manual_token_seen": "",
        "manual_new_crop_needed": "",
        "manual_image_insufficient": "",
        "manual_new_crop_x": "",
        "manual_new_crop_y": "",
        "manual_new_crop_width": "",
        "manual_new_crop_height": "",
    }

    outcome = final_outcome(row)

    assert outcome["consolidation_outcome"] == "pending_visual_check"
    assert outcome["visual_evidence_status"] == "no_new_visual_evidence"
    assert outcome["axis_test_eligibility"] == "not_eligible"


def test_seen_token_with_complete_new_crop_becomes_review_evidence():
    row = {
        "manual_token_seen": "yes",
        "manual_new_crop_needed": "yes",
        "manual_image_insufficient": "no",
        "manual_new_crop_x": "10",
        "manual_new_crop_y": "20",
        "manual_new_crop_width": "30",
        "manual_new_crop_height": "40",
    }

    outcome = final_outcome(row)

    assert outcome["consolidation_outcome"] == "token_seen_new_crop_ready"
    assert outcome["visual_evidence_status"] == "new_crop_candidate"
    assert outcome["axis_test_eligibility"] == "eligible_after_crop_generation"


def test_build_consolidated_rows_preserves_checklist_traceability():
    rows = [
        {
            "checklist_id": "R13-001",
            "packet_id": "R12-001",
            "route11_id": "R11-002",
            "manual_review_id": "R9-001",
            "crop_id": "R7-009",
            "target_type": "missing_group_tokens",
            "manual_token_seen": "",
            "manual_new_crop_needed": "",
            "manual_image_insufficient": "",
        }
    ]

    consolidated = build_consolidated_rows(rows)

    assert consolidated[0]["route14_id"] == "R14-001"
    assert consolidated[0]["checklist_id"] == "R13-001"
    assert consolidated[0]["packet_id"] == "R12-001"
    assert consolidated[0]["consolidation_outcome"] == "pending_visual_check"


def test_summarize_rows_counts_outcomes_and_targets():
    rows = [
        {
            "consolidation_outcome": "pending_visual_check",
            "visual_evidence_status": "no_new_visual_evidence",
            "axis_test_eligibility": "not_eligible",
            "coordinate_status": "no_new_crop_coordinates",
            "target_type": "missing_group_tokens",
            "packet_id": "R12-001",
        },
        {
            "consolidation_outcome": "token_seen_new_crop_ready",
            "visual_evidence_status": "new_crop_candidate",
            "axis_test_eligibility": "eligible_after_crop_generation",
            "coordinate_status": "new_crop_coordinates_complete",
            "target_type": "matched_group_tokens",
            "packet_id": "R12-001",
        },
    ]

    summary = summarize_rows(rows)

    assert summary["consolidation_outcome"]["pending_visual_check"] == 1
    assert summary["visual_evidence_status"]["new_crop_candidate"] == 1
    assert summary["packet_id"]["R12-001"] == 2
