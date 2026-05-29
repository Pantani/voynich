from scripts.prepare_visual_decision_entry_sheet import (
    FIELDNAMES,
    allowed_values,
    build_entry_rows,
    render_entry_section,
    summarize_entry_rows,
)


def test_allowed_values_are_explicit_for_manual_decision_fields():
    assert allowed_values("manual_token_seen") == "yes/no/uncertain"
    assert allowed_values("manual_new_crop_needed") == "yes/no"
    assert allowed_values("manual_image_insufficient") == "yes/no"
    assert allowed_values("manual_notes") == ""


def test_fieldnames_keep_allowed_values_next_to_blank_manual_fields():
    assert "allowed_manual_token_seen" in FIELDNAMES
    assert "manual_token_seen" in FIELDNAMES
    assert FIELDNAMES.index("allowed_manual_token_seen") < FIELDNAMES.index("manual_token_seen")
    assert "semantic_guardrail" in FIELDNAMES


def test_build_entry_rows_filters_blank_application_log_and_joins_package_fields():
    application_log = [
        {
            "route20_id": "R20-001",
            "route19_id": "R19-001",
            "route18_id": "R18-001",
            "checklist_id": "R13-001",
            "manual_review_id": "R9-001",
            "crop_id": "R7-009",
            "folio": "f67r1",
            "priority_level": "P0",
            "target_type": "missing_group_tokens",
            "review_target": "otardar",
            "application_status": "skipped_blank_manual_decision",
        },
        {
            "route20_id": "R20-002",
            "route19_id": "R19-002",
            "route18_id": "R18-002",
            "checklist_id": "R13-002",
            "application_status": "applied_manual_values",
        },
    ]
    package_rows = [
        {
            "route19_id": "R19-001",
            "route18_id": "R18-001",
            "checklist_id": "R13-001",
            "source_image": "images/raw/commons_f67r1_r2.jpg",
            "crop_svg": "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
            "review_region": "x=31 y=158 w=768 h=913",
            "priority_bucket": "P0_operator_missing_tokens",
            "locus": "f67r1.5,@Cc",
        }
    ]

    rows = build_entry_rows(application_log, package_rows)

    assert len(rows) == 1
    assert rows[0]["route21_id"] == "R21-001"
    assert rows[0]["route20_id"] == "R20-001"
    assert rows[0]["route19_id"] == "R19-001"
    assert rows[0]["source_image"] == "images/raw/commons_f67r1_r2.jpg"
    assert rows[0]["crop_svg"] == "images/derived/review_crops/R7-009_R6-009_f67r1.svg"
    assert rows[0]["entry_status"] == "awaiting_manual_entry"


def test_build_entry_rows_keeps_manual_fields_blank_and_guarded():
    application_log = [
        {
            "route20_id": "R20-001",
            "route19_id": "R19-001",
            "checklist_id": "R13-001",
            "application_status": "skipped_blank_manual_decision",
        }
    ]
    package_rows = [{"route19_id": "R19-001", "checklist_id": "R13-001"}]

    rows = build_entry_rows(application_log, package_rows)

    assert rows[0]["allowed_manual_token_seen"] == "yes/no/uncertain"
    assert rows[0]["allowed_manual_new_crop_needed"] == "yes/no"
    assert rows[0]["allowed_manual_image_insufficient"] == "yes/no"
    assert rows[0]["manual_token_seen"] == ""
    assert rows[0]["manual_new_crop_needed"] == ""
    assert rows[0]["manual_image_insufficient"] == ""
    assert rows[0]["output_rule"] == "copy_completed_entry_values_to_direct_visual_package"
    assert rows[0]["semantic_guardrail"] == "entry_sheet_not_visual_evidence"


def test_summarize_entry_rows_counts_status_priority_folio_and_target_type():
    rows = [
        {
            "entry_status": "awaiting_manual_entry",
            "priority_level": "P0",
            "folio": "f67r1",
            "target_type": "missing_group_tokens",
        },
        {
            "entry_status": "awaiting_manual_entry",
            "priority_level": "P1",
            "folio": "f70v2",
            "target_type": "missing_group_tokens",
        },
    ]

    summary = summarize_entry_rows(rows)

    assert summary["entry_status"]["awaiting_manual_entry"] == 2
    assert summary["priority_level"]["P0"] == 1
    assert summary["folio"]["f70v2"] == 1
    assert summary["target_type"]["missing_group_tokens"] == 2


def test_render_entry_section_includes_allowed_values_and_guardrail():
    row = {
        "route21_id": "R21-001",
        "route20_id": "R20-001",
        "route19_id": "R19-001",
        "checklist_id": "R13-001",
        "folio": "f67r1",
        "review_target": "otardar",
        "source_image": "images/raw/commons_f67r1_r2.jpg",
        "crop_svg": "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
        "allowed_manual_token_seen": "yes/no/uncertain",
        "allowed_manual_new_crop_needed": "yes/no",
        "allowed_manual_image_insufficient": "yes/no",
        "output_rule": "copy_completed_entry_values_to_direct_visual_package",
        "semantic_guardrail": "entry_sheet_not_visual_evidence",
    }

    text = render_entry_section(row)

    assert "R21-001" in text
    assert "yes/no/uncertain" in text
    assert "copy_completed_entry_values_to_direct_visual_package" in text
    assert "entry_sheet_not_visual_evidence" in text
