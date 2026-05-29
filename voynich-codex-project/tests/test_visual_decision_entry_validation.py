from scripts.validate_visual_decision_entry_sheet import (
    apply_valid_entries_to_package,
    build_validation_log,
    has_manual_values,
    render_log_section,
    summarize_validation_log,
    validate_entry_row,
)


def base_entry(**overrides):
    row = {
        "route21_id": "R21-001",
        "route20_id": "R20-001",
        "route19_id": "R19-001",
        "checklist_id": "R13-001",
        "folio": "f67r1",
        "priority_level": "P0",
        "target_type": "missing_group_tokens",
        "review_target": "otardar",
        "manual_token_seen": "",
        "manual_new_crop_needed": "",
        "manual_image_insufficient": "",
        "manual_new_crop_x": "",
        "manual_new_crop_y": "",
        "manual_new_crop_width": "",
        "manual_new_crop_height": "",
        "manual_notes": "",
    }
    row.update(overrides)
    return row


def test_validate_entry_row_accepts_allowed_values_and_complete_new_crop():
    row = base_entry(
        manual_token_seen="yes",
        manual_new_crop_needed="yes",
        manual_image_insufficient="no",
        manual_new_crop_x="10",
        manual_new_crop_y="20",
        manual_new_crop_width="30",
        manual_new_crop_height="40",
    )

    assert validate_entry_row(row) == []


def test_validate_entry_row_rejects_invalid_values_and_incomplete_rectangles():
    row = base_entry(
        manual_token_seen="maybe",
        manual_new_crop_needed="yes",
        manual_image_insufficient="unknown",
        manual_new_crop_x="10",
        manual_new_crop_y="",
        manual_new_crop_width="-4",
        manual_new_crop_height="abc",
    )

    errors = validate_entry_row(row)

    assert "manual_token_seen_invalid" in errors
    assert "manual_image_insufficient_invalid" in errors
    assert "new_crop_rect_incomplete" in errors
    assert "manual_new_crop_width_must_be_positive_integer" in errors
    assert "manual_new_crop_height_must_be_positive_integer" in errors


def test_has_manual_values_distinguishes_blank_from_explicit_entry():
    assert has_manual_values(base_entry()) is False
    assert has_manual_values(base_entry(manual_token_seen="uncertain")) is True
    assert has_manual_values(base_entry(manual_notes="visible but ambiguous")) is True


def test_build_validation_log_classifies_pending_valid_and_invalid_entries():
    rows = [
        base_entry(route21_id="R21-001", route19_id="R19-001"),
        base_entry(route21_id="R21-002", route19_id="R19-002", manual_token_seen="no"),
        base_entry(route21_id="R21-003", route19_id="R19-003", manual_token_seen="maybe"),
    ]

    log = build_validation_log(rows)

    assert log[0]["route22_id"] == "R22-001"
    assert log[0]["validation_status"] == "pending_blank_manual_entry"
    assert log[0]["apply_status"] == "skipped_blank_manual_entry"
    assert log[1]["validation_status"] == "valid_manual_entry"
    assert log[1]["apply_status"] == "ready_to_apply_manual_values"
    assert log[2]["validation_status"] == "invalid_manual_entry"
    assert log[2]["apply_status"] == "blocked_invalid_manual_entry"
    assert log[2]["semantic_guardrail"] == "validated_values_are_manual_not_axis_meaning"


def test_apply_valid_entries_to_package_copies_only_valid_nonblank_values():
    package_rows = [
        {
            "route19_id": "R19-001",
            "checklist_id": "R13-001",
            "manual_token_seen": "",
            "manual_new_crop_needed": "",
            "manual_notes": "keep existing",
        },
        {
            "route19_id": "R19-002",
            "checklist_id": "R13-002",
            "manual_token_seen": "",
            "manual_new_crop_needed": "",
            "manual_notes": "",
        },
    ]
    entry_rows = [
        base_entry(route19_id="R19-001", checklist_id="R13-001", manual_token_seen="yes"),
        base_entry(route19_id="R19-002", checklist_id="R13-002", manual_token_seen="maybe", manual_notes="do not copy"),
    ]

    updated = apply_valid_entries_to_package(package_rows, entry_rows)

    assert updated[0]["manual_token_seen"] == "yes"
    assert updated[0]["manual_notes"] == "keep existing"
    assert updated[1]["manual_token_seen"] == ""
    assert updated[1]["manual_notes"] == ""


def test_summarize_validation_log_counts_validation_apply_priority_and_folio():
    log = [
        {
            "validation_status": "pending_blank_manual_entry",
            "apply_status": "skipped_blank_manual_entry",
            "priority_level": "P0",
            "folio": "f67r1",
            "target_type": "missing_group_tokens",
        },
        {
            "validation_status": "valid_manual_entry",
            "apply_status": "ready_to_apply_manual_values",
            "priority_level": "P1",
            "folio": "f70v2",
            "target_type": "missing_group_tokens",
        },
    ]

    summary = summarize_validation_log(log)

    assert summary["validation_status"]["pending_blank_manual_entry"] == 1
    assert summary["apply_status"]["ready_to_apply_manual_values"] == 1
    assert summary["priority_level"]["P0"] == 1
    assert summary["folio"]["f70v2"] == 1
    assert summary["target_type"]["missing_group_tokens"] == 2


def test_render_log_section_includes_status_errors_and_guardrail():
    row = {
        "route22_id": "R22-001",
        "route21_id": "R21-001",
        "route19_id": "R19-001",
        "checklist_id": "R13-001",
        "validation_status": "invalid_manual_entry",
        "validation_errors": "manual_token_seen_invalid",
        "apply_status": "blocked_invalid_manual_entry",
        "next_action": "fix invalid manual fields before applying",
        "semantic_guardrail": "validated_values_are_manual_not_axis_meaning",
    }

    text = render_log_section(row)

    assert "R22-001" in text
    assert "manual_token_seen_invalid" in text
    assert "blocked_invalid_manual_entry" in text
    assert "validated_values_are_manual_not_axis_meaning" in text
