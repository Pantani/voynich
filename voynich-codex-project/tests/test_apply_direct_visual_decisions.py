from scripts.apply_direct_visual_decisions import (
    apply_decision_rows,
    application_status,
    build_application_log,
    has_manual_values,
    summarize_application_log,
)


def test_has_manual_values_detects_any_filled_manual_field():
    blank = {
        "manual_token_seen": "",
        "manual_new_crop_needed": "",
        "manual_image_insufficient": "",
        "manual_new_crop_x": "",
        "manual_notes": "",
    }
    filled = dict(blank)
    filled["manual_token_seen"] = "yes"

    assert has_manual_values(blank) is False
    assert has_manual_values(filled) is True


def test_application_status_skips_blank_decisions_and_applies_filled_ones():
    assert application_status({"manual_token_seen": ""}, True) == "skipped_blank_manual_decision"
    assert application_status({"manual_token_seen": "yes"}, True) == "applied_manual_values"
    assert application_status({"manual_token_seen": "yes"}, False) == "missing_checklist_row"


def test_apply_decision_rows_updates_only_matching_checklist_rows():
    checklist = [
        {
            "checklist_id": "R13-001",
            "manual_token_seen": "",
            "manual_new_crop_needed": "",
            "manual_notes": "",
        },
        {
            "checklist_id": "R13-999",
            "manual_token_seen": "",
            "manual_new_crop_needed": "",
            "manual_notes": "keep me",
        },
    ]
    package = [
        {
            "checklist_id": "R13-001",
            "manual_token_seen": "yes",
            "manual_new_crop_needed": "no",
            "manual_notes": "visible in source",
        }
    ]

    updated = apply_decision_rows(checklist, package)

    assert updated[0]["manual_token_seen"] == "yes"
    assert updated[0]["manual_new_crop_needed"] == "no"
    assert updated[0]["manual_notes"] == "visible in source"
    assert updated[1]["manual_notes"] == "keep me"


def test_apply_decision_rows_does_not_clear_existing_values_with_blank_package_fields():
    checklist = [
        {
            "checklist_id": "R13-001",
            "manual_token_seen": "uncertain",
            "manual_new_crop_needed": "no",
            "manual_notes": "existing note",
        }
    ]
    package = [
        {
            "checklist_id": "R13-001",
            "manual_token_seen": "",
            "manual_new_crop_needed": "",
            "manual_notes": "",
        }
    ]

    updated = apply_decision_rows(checklist, package)

    assert updated[0]["manual_token_seen"] == "uncertain"
    assert updated[0]["manual_new_crop_needed"] == "no"
    assert updated[0]["manual_notes"] == "existing note"


def test_build_application_log_tracks_traceability_and_status():
    checklist = [{"checklist_id": "R13-001"}]
    package = [
        {
            "route19_id": "R19-001",
            "route18_id": "R18-001",
            "checklist_id": "R13-001",
            "manual_review_id": "R9-001",
            "manual_token_seen": "",
            "manual_new_crop_needed": "",
            "manual_image_insufficient": "",
            "manual_notes": "",
        },
        {
            "route19_id": "R19-999",
            "route18_id": "R18-999",
            "checklist_id": "R13-999",
            "manual_review_id": "R9-999",
            "manual_token_seen": "yes",
            "manual_new_crop_needed": "no",
            "manual_image_insufficient": "no",
            "manual_notes": "missing row",
        },
    ]

    log = build_application_log(checklist, package)

    assert log[0]["route20_id"] == "R20-001"
    assert log[0]["application_status"] == "skipped_blank_manual_decision"
    assert log[0]["semantic_guardrail"] == "applied_values_are_manual_not_axis_meaning"
    assert log[1]["application_status"] == "missing_checklist_row"


def test_summarize_application_log_counts_statuses():
    log = [
        {"application_status": "skipped_blank_manual_decision", "priority_level": "P0", "folio": "f67r1"},
        {"application_status": "applied_manual_values", "priority_level": "P1", "folio": "f70v2"},
    ]

    summary = summarize_application_log(log)

    assert summary["application_status"]["skipped_blank_manual_decision"] == 1
    assert summary["application_status"]["applied_manual_values"] == 1
    assert summary["priority_level"]["P0"] == 1
