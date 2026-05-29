from scripts.consolidate_human_review_evidence import (
    build_evidence_rows,
    classify_human_evidence,
    summarize_evidence_rows,
)


def test_blank_human_review_fields_stay_pending_without_evidence():
    row = {
        "manual_token_seen": "",
        "manual_new_crop_needed": "",
        "manual_image_insufficient": "",
        "manual_new_crop_x": "",
        "manual_new_crop_y": "",
        "manual_new_crop_width": "",
        "manual_new_crop_height": "",
    }

    outcome = classify_human_evidence(row)

    assert outcome["human_review_state"] == "pending_human_review"
    assert outcome["evidence_category"] == "no_human_visual_evidence"
    assert outcome["crop_generation_action"] == "no_crop_generation"
    assert outcome["axis_test_readiness"] == "not_ready"


def test_seen_token_with_complete_new_crop_coordinates_becomes_crop_candidate():
    row = {
        "manual_token_seen": "yes",
        "manual_new_crop_needed": "yes",
        "manual_image_insufficient": "no",
        "manual_new_crop_x": "10",
        "manual_new_crop_y": "20",
        "manual_new_crop_width": "30",
        "manual_new_crop_height": "40",
    }

    outcome = classify_human_evidence(row)

    assert outcome["human_review_state"] == "human_confirmed_new_crop_candidate"
    assert outcome["evidence_category"] == "human_seen_with_new_crop_coordinates"
    assert outcome["crop_generation_action"] == "generate_new_crop_candidate"
    assert outcome["axis_test_readiness"] == "ready_after_new_crop_review"


def test_image_insufficient_suspends_item_without_rejecting_token():
    row = {
        "manual_token_seen": "uncertain",
        "manual_new_crop_needed": "no",
        "manual_image_insufficient": "yes",
        "manual_new_crop_x": "",
        "manual_new_crop_y": "",
        "manual_new_crop_width": "",
        "manual_new_crop_height": "",
    }

    outcome = classify_human_evidence(row)

    assert outcome["human_review_state"] == "image_insufficient"
    assert outcome["evidence_category"] == "no_human_visual_evidence"
    assert outcome["crop_generation_action"] == "seek_alternate_image"
    assert outcome["axis_test_readiness"] == "not_ready"


def test_build_evidence_rows_preserves_instruction_and_checklist_traceability():
    instruction_items = [
        {
            "instruction_item_id": "R15I-001",
            "checklist_id": "R13-001",
            "packet_id": "R12-001",
            "manual_review_id": "R9-001",
            "crop_id": "R7-009",
            "source_review_id": "R6-009",
            "folio": "f67r1",
            "locus": "f67r1.5,@Cc",
            "source_image": "images/raw/commons_f67r1_r2.jpg",
            "crop_svg": "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
            "target_type": "missing_group_tokens",
            "review_target": "otardar",
        }
    ]
    checklist_rows = [
        {
            "checklist_id": "R13-001",
            "priority_bucket": "P0_operator_missing_tokens",
            "manual_token_seen": "",
            "manual_new_crop_needed": "",
            "manual_image_insufficient": "",
            "manual_new_crop_x": "",
            "manual_new_crop_y": "",
            "manual_new_crop_width": "",
            "manual_new_crop_height": "",
            "manual_notes": "",
        }
    ]

    rows = build_evidence_rows(instruction_items, checklist_rows)

    assert rows[0]["route16_id"] == "R16-001"
    assert rows[0]["instruction_item_id"] == "R15I-001"
    assert rows[0]["checklist_id"] == "R13-001"
    assert rows[0]["manual_review_id"] == "R9-001"
    assert rows[0]["crop_id"] == "R7-009"
    assert rows[0]["human_review_state"] == "pending_human_review"
    assert rows[0]["semantic_guardrail"] == "human_review_evidence_not_axis_meaning"


def test_build_evidence_rows_marks_missing_checklist_rows():
    instruction_items = [
        {
            "instruction_item_id": "R15I-001",
            "checklist_id": "R13-999",
            "packet_id": "R12-001",
            "manual_review_id": "R9-999",
            "crop_id": "R7-999",
            "source_review_id": "R6-999",
            "folio": "f67r1",
            "locus": "f67r1.5,@Cc",
            "source_image": "images/raw/commons_f67r1_r2.jpg",
            "crop_svg": "images/derived/review_crops/missing.svg",
            "target_type": "missing_group_tokens",
            "review_target": "missing",
        }
    ]

    rows = build_evidence_rows(instruction_items, [])

    assert rows[0]["human_review_state"] == "missing_checklist_row"
    assert rows[0]["next_action"] == "restore checklist row before consolidation"


def test_summarize_evidence_rows_counts_review_state_and_packets():
    rows = [
        {
            "human_review_state": "pending_human_review",
            "evidence_category": "no_human_visual_evidence",
            "crop_generation_action": "no_crop_generation",
            "axis_test_readiness": "not_ready",
            "packet_id": "R12-001",
            "target_type": "missing_group_tokens",
        },
        {
            "human_review_state": "human_confirmed_new_crop_candidate",
            "evidence_category": "human_seen_with_new_crop_coordinates",
            "crop_generation_action": "generate_new_crop_candidate",
            "axis_test_readiness": "ready_after_new_crop_review",
            "packet_id": "R12-001",
            "target_type": "matched_group_tokens",
        },
    ]

    summary = summarize_evidence_rows(rows)

    assert summary["human_review_state"]["pending_human_review"] == 1
    assert summary["evidence_category"]["human_seen_with_new_crop_coordinates"] == 1
    assert summary["crop_generation_action"]["generate_new_crop_candidate"] == 1
    assert summary["packet_id"]["R12-001"] == 2
