from scripts.verify_ready_visual_annotation_manual_gate import (
    build_manual_gate_rows,
    gate_status,
    summarize_manual_gate_rows,
)


def entry_row(route32_id="R32-001", status="", notes=""):
    return {
        "route32_id": route32_id,
        "route31_id": route32_id.replace("R32", "R31"),
        "route28_id": "R28-001",
        "folio": "f99v",
        "priority_level": "P0",
        "manual_annotation_status": status,
        "manual_visual_notes": notes,
        "allowed_manual_annotation_status": "annotated/not_visible/uncertain",
    }


def application_log(route32_id="R32-001", apply_status="skipped_blank_manual_annotation"):
    return {
        "route33_id": route32_id.replace("R32", "R33"),
        "route32_id": route32_id,
        "route28_id": "R28-001",
        "apply_status": apply_status,
        "package_action": "no_package_change",
    }


def test_gate_status_keeps_blank_manual_annotation_blocked_not_invalid():
    assert gate_status("", "", "present", "skipped_blank_manual_annotation") == (
        "blocked_pending_manual_annotation",
        "fill_r32_entry_sheet_using_html_then_rerun_r33_r31",
    )


def test_build_manual_gate_rows_checks_html_card_and_application_log():
    rows = build_manual_gate_rows(
        [entry_row()],
        [application_log()],
        "R32-001 R28-001 f99v annotated/not_visible/uncertain focused_visual_annotation_html_not_evidence",
    )

    assert rows[0]["route34_id"] == "R34-001"
    assert rows[0]["route32_id"] == "R32-001"
    assert rows[0]["html_card_check"] == "present"
    assert rows[0]["manual_entry_status"] == "pending_blank_manual_annotation"
    assert rows[0]["r33_apply_status"] == "skipped_blank_manual_annotation"
    assert rows[0]["gate_status"] == "blocked_pending_manual_annotation"
    assert rows[0]["next_action"] == "fill_r32_entry_sheet_using_html_then_rerun_r33_r31"
    assert rows[0]["semantic_guardrail"] == "manual_visual_gate_not_evidence"


def test_build_manual_gate_rows_marks_valid_manual_entry_ready_for_rerun():
    rows = build_manual_gate_rows(
        [entry_row(status="annotated", notes="visible near target token group")],
        [application_log()],
        "R32-001 R28-001 f99v annotated/not_visible/uncertain focused_visual_annotation_html_not_evidence",
    )

    assert rows[0]["manual_entry_status"] == "manual_annotation_filled"
    assert rows[0]["manual_notes_status"] == "notes_present"
    assert rows[0]["gate_status"] == "ready_to_rerun_r33_r31"
    assert rows[0]["next_action"] == "rerun_r33_then_r31_validation"


def test_build_manual_gate_rows_marks_invalid_or_missing_html_blocked():
    rows = build_manual_gate_rows(
        [
            entry_row(route32_id="R32-001", status="maybe", notes="bad value"),
            entry_row(route32_id="R32-002", status="uncertain", notes="visible but ambiguous"),
        ],
        [application_log("R32-001"), application_log("R32-002")],
        "R32-001 R28-001 f99v annotated/not_visible/uncertain focused_visual_annotation_html_not_evidence",
    )

    assert rows[0]["manual_entry_status"] == "invalid_manual_annotation_entry"
    assert rows[0]["gate_status"] == "blocked_invalid_manual_annotation"
    assert rows[1]["html_card_check"] == "missing"
    assert rows[1]["gate_status"] == "blocked_missing_html_card"


def test_summarize_manual_gate_rows_counts_gate_status_and_priority():
    rows = build_manual_gate_rows(
        [
            entry_row(route32_id="R32-001", status="", notes=""),
            entry_row(route32_id="R32-002", status="annotated", notes="visible"),
        ],
        [application_log("R32-001"), application_log("R32-002")],
        "R32-001 R32-002 R28-001 f99v annotated/not_visible/uncertain focused_visual_annotation_html_not_evidence",
    )

    summary = summarize_manual_gate_rows(rows)

    assert summary["gate_status"]["blocked_pending_manual_annotation"] == 1
    assert summary["gate_status"]["ready_to_rerun_r33_r31"] == 1
    assert summary["priority_level"]["P0"] == 2
