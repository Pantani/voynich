from scripts.apply_ready_visual_annotation_entries import (
    apply_ready_entry_rows,
    summarize_application_log_rows,
    validate_entry_fields,
)


def package_row(route28_id="R28-001", package_status="ready_for_manual_visual_annotation"):
    return {
        "route28_id": route28_id,
        "route27_id": route28_id.replace("R28", "R27"),
        "folio": "f99v",
        "locus_kind": "P",
        "priority_level": "P0",
        "package_status": package_status,
        "manual_annotation_status": "",
        "manual_source_image_url": "",
        "manual_visual_notes": "",
        "semantic_guardrail": "visual_annotation_package_not_evidence",
    }


def entry_row(route32_id="R32-001", route28_id="R28-001", status="", notes=""):
    return {
        "route32_id": route32_id,
        "route31_id": route32_id.replace("R32", "R31"),
        "route28_id": route28_id,
        "manual_annotation_status": status,
        "manual_visual_notes": notes,
        "semantic_guardrail": "focused_visual_annotation_html_not_evidence",
    }


def test_validate_entry_fields_keeps_blank_pending_not_invalid():
    assert validate_entry_fields("", "") == (
        "no",
        "pending_blank_manual_annotation",
        "manual_fields_blank",
        "skipped_blank_manual_annotation",
        "no_package_change",
    )


def test_apply_ready_entry_rows_skips_blank_entries_and_preserves_package():
    updated, log = apply_ready_entry_rows([entry_row()], [package_row()])

    assert updated[0]["manual_annotation_status"] == ""
    assert updated[0]["manual_visual_notes"] == ""
    assert log[0]["route33_id"] == "R33-001"
    assert log[0]["manual_entry_valid"] == "no"
    assert log[0]["apply_status"] == "skipped_blank_manual_annotation"
    assert log[0]["package_action"] == "no_package_change"
    assert log[0]["semantic_guardrail"] == "ready_visual_entry_application_not_visual_evidence"


def test_apply_ready_entry_rows_applies_valid_entries_to_derived_package_only():
    updated, log = apply_ready_entry_rows(
        [entry_row(status="annotated", notes="visible near label ring")],
        [package_row()],
    )

    assert updated[0]["manual_annotation_status"] == "annotated"
    assert updated[0]["manual_visual_notes"] == "visible near label ring"
    assert log[0]["manual_entry_valid"] == "yes"
    assert log[0]["apply_status"] == "applied_manual_annotation_to_derived_package"
    assert log[0]["package_action"] == "updated_derived_package_row"


def test_apply_ready_entry_rows_rejects_invalid_or_not_ready_entries():
    updated, log = apply_ready_entry_rows(
        [
            entry_row(route32_id="R32-001", route28_id="R28-001", status="maybe", notes="bad"),
            entry_row(route32_id="R32-002", route28_id="R28-002", status="annotated", notes="filled"),
        ],
        [
            package_row("R28-001"),
            package_row("R28-002", package_status="blocked_pending_source_image"),
        ],
    )

    assert updated[0]["manual_annotation_status"] == ""
    assert updated[1]["manual_annotation_status"] == ""
    assert log[0]["validation_reason"] == "manual_annotation_status_not_allowed"
    assert log[0]["apply_status"] == "skipped_invalid_manual_annotation"
    assert log[1]["validation_reason"] == "package_item_not_ready_for_manual_visual_annotation"
    assert log[1]["apply_status"] == "skipped_not_ready_package_item"


def test_summarize_application_log_rows_counts_apply_status_and_actions():
    _, log = apply_ready_entry_rows(
        [
            entry_row(route32_id="R32-001", status="", notes=""),
            entry_row(route32_id="R32-002", status="uncertain", notes="visible but ambiguous"),
        ],
        [package_row("R28-001"), package_row("R28-002")],
    )

    summary = summarize_application_log_rows(log)

    assert summary["apply_status"]["skipped_blank_manual_annotation"] == 1
    assert summary["apply_status"]["applied_manual_annotation_to_derived_package"] == 1
    assert summary["package_action"]["no_package_change"] == 1
    assert summary["package_action"]["updated_derived_package_row"] == 1
