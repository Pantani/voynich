from scripts.prepare_packet_item_checklist import (
    build_checklist_rows,
    checklist_template,
    review_target,
    review_target_type,
    summarize_checklist,
)


def test_review_target_uses_missing_tokens_when_focus_is_missing():
    row = {
        "second_pass_focus": "locate_missing_group_tokens",
        "missing_group_tokens": "oteedar oteeeor",
        "group_tokens": "otar oteedar oteeeor",
    }

    assert review_target(row) == "oteedar oteeeor"
    assert review_target_type(row) == "missing_group_tokens"


def test_review_target_uses_group_tokens_when_tightening_existing_region():
    row = {
        "second_pass_focus": "tighten_existing_matched_tokens",
        "missing_group_tokens": "",
        "group_tokens": "ar ol",
    }

    assert review_target(row) == "ar ol"
    assert review_target_type(row) == "matched_group_tokens"


def test_checklist_template_leaves_manual_fields_blank():
    row = {
        "packet_id": "R12-001",
        "route11_id": "R11-002",
        "route10_id": "R10-001",
        "manual_review_id": "R9-001",
        "crop_id": "R7-009",
        "source_review_id": "R6-009",
        "folio": "f67r1",
        "locus": "f67r1.5,@Cc",
        "source_image": "images/raw/commons_f67r1_r2.jpg",
        "crop_svg": "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
        "review_region": "x=31 y=158 w=768 h=913",
        "prefix_family": "ot",
        "axis_coverage": "ao",
        "group_tokens": "otardar otor",
        "missing_group_tokens": "otardar",
        "priority_bucket": "P0_operator_missing_tokens",
        "second_pass_focus": "locate_missing_group_tokens",
        "crop_strategy": "search_single_missing_token_then_redraw_crop",
    }

    output = checklist_template(row, 1)

    assert output["checklist_id"] == "R13-001"
    assert output["packet_id"] == "R12-001"
    assert output["initial_check_status"] == "pending_visual_check"
    assert output["manual_token_seen"] == ""
    assert output["manual_new_crop_needed"] == ""
    assert output["manual_image_insufficient"] == ""
    assert output["manual_notes"] == ""
    assert output["semantic_guardrail"] == "checklist_item_not_axis_evidence"


def test_build_checklist_rows_preserves_packet_order_and_traceability():
    rows = [
        {
            "packet_id": "R12-002",
            "route11_id": "R11-001",
            "route10_id": "R10-002",
            "manual_review_id": "R9-002",
            "crop_id": "R7-010",
            "folio": "f70v2",
            "locus": "f70v2.21,@Cc",
            "group_tokens": "otar oteedar oteeeor",
            "missing_group_tokens": "oteedar oteeeor",
            "second_pass_focus": "locate_missing_group_tokens",
            "priority_bucket": "P0_operator_missing_tokens",
        },
        {
            "packet_id": "R12-001",
            "route11_id": "R11-002",
            "route10_id": "R10-001",
            "manual_review_id": "R9-001",
            "crop_id": "R7-009",
            "folio": "f67r1",
            "locus": "f67r1.5,@Cc",
            "group_tokens": "otardar otor",
            "missing_group_tokens": "otardar",
            "second_pass_focus": "locate_missing_group_tokens",
            "priority_bucket": "P0_operator_missing_tokens",
        },
    ]

    output = build_checklist_rows(rows)

    assert [row["packet_id"] for row in output] == ["R12-001", "R12-002"]
    assert [row["checklist_id"] for row in output] == ["R13-001", "R13-002"]
    assert output[0]["route11_id"] == "R11-002"
    assert output[0]["manual_review_id"] == "R9-001"


def test_summarize_checklist_counts_packets_and_targets():
    rows = [
        {
            "packet_id": "R12-001",
            "target_type": "missing_group_tokens",
            "initial_check_status": "pending_visual_check",
            "priority_bucket": "P0_operator_missing_tokens",
        },
        {
            "packet_id": "R12-001",
            "target_type": "matched_group_tokens",
            "initial_check_status": "pending_visual_check",
            "priority_bucket": "P3_tighten_existing_region",
        },
    ]

    summary = summarize_checklist(rows)

    assert summary["packet_id"]["R12-001"] == 2
    assert summary["target_type"]["missing_group_tokens"] == 1
    assert summary["initial_check_status"]["pending_visual_check"] == 2
