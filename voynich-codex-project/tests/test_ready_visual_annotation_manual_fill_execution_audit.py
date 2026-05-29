from scripts.audit_ready_visual_annotation_manual_fill_execution import (
    build_execution_audit_rows,
    execution_status,
    summarize_execution_audit_rows,
)


def entry_row(route32_id="R32-001", status="", notes=""):
    return {
        "route32_id": route32_id,
        "route31_id": route32_id.replace("R32", "R31"),
        "route28_id": "R28-001",
        "folio": "f99v",
        "priority_level": "P0",
        "locus_kind": "P",
        "image_url": "https://example.test/f99v.jpg",
        "commons_page": "https://commons.test/f99v",
        "allowed_manual_annotation_status": "annotated/not_visible/uncertain",
        "manual_annotation_status": status,
        "manual_visual_notes": notes,
    }


def work_order_row(route32_id="R32-001", status="manual_fill_required"):
    return {
        "route38_id": route32_id.replace("R32", "R38"),
        "route37_id": route32_id.replace("R32", "R37"),
        "route36_id": route32_id.replace("R32", "R36"),
        "route32_id": route32_id,
        "html_reference": "docs/rota_32.html",
        "work_order_status": status,
    }


def protocol_row(route32_id="R32-001", status="awaiting_human_visual_entry"):
    return {
        "route36_id": route32_id.replace("R32", "R36"),
        "route32_id": route32_id,
        "manual_fill_status": status,
    }


def chain_row(route32_id="R32-001", status="blocked_no_human_entries"):
    return {
        "route37_id": route32_id.replace("R32", "R37"),
        "route32_id": route32_id,
        "r37_status": status,
    }


def test_execution_status_blocks_blank_manual_fields():
    assert execution_status("", "", "awaiting_human_visual_entry", "blocked_no_human_entries") == (
        "manual_fill_not_executed",
        "blocked_no_manual_entry",
        "human_fill_r32_fields_from_r38_order",
    )


def test_execution_status_rejects_partial_manual_fields():
    assert execution_status("annotated", "", "awaiting_human_visual_entry", "blocked_no_human_entries") == (
        "invalid_partial_manual_entry",
        "blocked_invalid_manual_entry",
        "complete_or_clear_r32_manual_fields_then_rerun_r36",
    )


def test_execution_status_requires_protocol_refresh_after_valid_entry():
    assert execution_status("uncertain", "visible but ambiguous", "awaiting_human_visual_entry", "blocked_no_human_entries") == (
        "manual_entry_present_protocol_refresh_required",
        "blocked_until_r36_r37_refresh",
        "rerun_r36_r37_then_recompute_r39",
    )


def test_execution_status_releases_only_after_protocol_and_chain_ready():
    assert execution_status(
        "not_visible",
        "source image checked; form not visible",
        "human_entry_present_ready_for_gate_rerun",
        "ready_for_revalidation_chain",
    ) == (
        "ready_for_revalidation_chain_reopen",
        "ready_to_reopen_chain",
        "rerun_r34_r35_r33_r31",
    )


def test_build_execution_audit_rows_preserves_blank_fields_and_traceability():
    rows = build_execution_audit_rows(
        [entry_row()],
        [work_order_row()],
        [protocol_row()],
        [chain_row()],
    )

    assert rows[0]["route39_id"] == "R39-001"
    assert rows[0]["route38_id"] == "R38-001"
    assert rows[0]["route32_id"] == "R32-001"
    assert rows[0]["manual_annotation_status"] == ""
    assert rows[0]["manual_visual_notes"] == ""
    assert rows[0]["fill_execution_status"] == "manual_fill_not_executed"
    assert rows[0]["chain_release_status"] == "blocked_no_manual_entry"
    assert rows[0]["next_action"] == "human_fill_r32_fields_from_r38_order"
    assert rows[0]["html_reference"] == "docs/rota_32.html"
    assert rows[0]["semantic_guardrail"] == "manual_fill_execution_audit_not_visual_evidence"


def test_build_execution_audit_rows_marks_ready_entries_without_changing_values():
    rows = build_execution_audit_rows(
        [entry_row(status="not_visible", notes="checked source image; form not visible")],
        [work_order_row(status="ready_to_reopen_revalidation_chain")],
        [protocol_row(status="human_entry_present_ready_for_gate_rerun")],
        [chain_row(status="ready_for_revalidation_chain")],
    )

    assert rows[0]["manual_annotation_status"] == "not_visible"
    assert rows[0]["manual_visual_notes"] == "checked source image; form not visible"
    assert rows[0]["fill_execution_status"] == "ready_for_revalidation_chain_reopen"
    assert rows[0]["chain_release_status"] == "ready_to_reopen_chain"


def test_summarize_execution_audit_rows_counts_statuses():
    rows = build_execution_audit_rows(
        [
            entry_row("R32-001"),
            entry_row("R32-002", status="uncertain", notes="ambiguous source image"),
        ],
        [work_order_row("R32-001"), work_order_row("R32-002")],
        [protocol_row("R32-001"), protocol_row("R32-002")],
        [chain_row("R32-001"), chain_row("R32-002")],
    )

    summary = summarize_execution_audit_rows(rows)

    assert summary["fill_execution_status"]["manual_fill_not_executed"] == 1
    assert summary["fill_execution_status"]["manual_entry_present_protocol_refresh_required"] == 1
    assert summary["chain_release_status"]["blocked_no_manual_entry"] == 1
    assert summary["chain_release_status"]["blocked_until_r36_r37_refresh"] == 1
