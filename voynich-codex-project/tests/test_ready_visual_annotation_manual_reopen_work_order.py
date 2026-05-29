from scripts.prepare_ready_visual_annotation_manual_reopen_work_order import (
    build_reopen_work_order_rows,
    summarize_reopen_work_order_rows,
    work_order_status,
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
        "manual_annotation_status": status,
        "manual_visual_notes": notes,
        "allowed_manual_annotation_status": "annotated/not_visible/uncertain",
    }


def protocol_row(route32_id="R32-001", status="awaiting_human_visual_entry"):
    return {
        "route36_id": route32_id.replace("R32", "R36"),
        "route35_id": route32_id.replace("R32", "R35"),
        "route34_id": route32_id.replace("R32", "R34"),
        "route32_id": route32_id,
        "manual_fill_status": status,
        "blocking_reason": "manual_entry_required",
    }


def chain_row(route32_id="R32-001", status="blocked_no_human_entries"):
    return {
        "route37_id": route32_id.replace("R32", "R37"),
        "route36_id": route32_id.replace("R32", "R36"),
        "route32_id": route32_id,
        "r37_status": status,
        "chain_action": "skip_r34_r35_r33_r31_until_manual_fill",
    }


def test_work_order_status_blocks_blank_manual_entries():
    assert work_order_status("", "", "awaiting_human_visual_entry", "blocked_no_human_entries") == (
        "manual_fill_required",
        "do_not_reopen_chain_until_r32_filled",
        "fill_manual_annotation_status_and_notes_in_r32",
    )


def test_work_order_status_marks_ready_entries_for_chain_reopen():
    assert work_order_status(
        "annotated",
        "visible beside label",
        "human_entry_present_ready_for_gate_rerun",
        "ready_for_revalidation_chain",
    ) == (
        "ready_to_reopen_revalidation_chain",
        "reopen_chain_after_r36_r37_refresh",
        "rerun_r36_r37_r34_r35_r33_r31",
    )


def test_work_order_status_blocks_invalid_protocol_or_chain_status():
    assert work_order_status("annotated", "visible", "invalid_manual_entry_needs_correction", "blocked_invalid_manual_entries") == (
        "blocked_by_invalid_manual_entry",
        "do_not_reopen_chain_until_r32_corrected",
        "fix_r32_entry_then_rerun_r36",
    )


def test_build_reopen_work_order_rows_preserves_blank_fields_and_traceability():
    rows = build_reopen_work_order_rows(
        [entry_row()],
        [protocol_row()],
        [chain_row()],
        "docs/rota_32.html",
    )

    assert rows[0]["route38_id"] == "R38-001"
    assert rows[0]["route37_id"] == "R37-001"
    assert rows[0]["route36_id"] == "R36-001"
    assert rows[0]["route32_id"] == "R32-001"
    assert rows[0]["manual_annotation_status"] == ""
    assert rows[0]["manual_visual_notes"] == ""
    assert rows[0]["fields_to_fill"] == "manual_annotation_status manual_visual_notes"
    assert rows[0]["work_order_status"] == "manual_fill_required"
    assert rows[0]["chain_reopen_action"] == "do_not_reopen_chain_until_r32_filled"
    assert rows[0]["html_reference"] == "docs/rota_32.html"
    assert rows[0]["semantic_guardrail"] == "manual_reopen_work_order_not_visual_evidence"


def test_build_reopen_work_order_rows_marks_ready_entries_without_changing_values():
    rows = build_reopen_work_order_rows(
        [entry_row(status="uncertain", notes="visible but ambiguous")],
        [protocol_row(status="human_entry_present_ready_for_gate_rerun")],
        [chain_row(status="ready_for_revalidation_chain")],
        "docs/rota_32.html",
    )

    assert rows[0]["manual_annotation_status"] == "uncertain"
    assert rows[0]["manual_visual_notes"] == "visible but ambiguous"
    assert rows[0]["work_order_status"] == "ready_to_reopen_revalidation_chain"
    assert rows[0]["next_action"] == "rerun_r36_r37_r34_r35_r33_r31"


def test_summarize_reopen_work_order_rows_counts_status_and_priority():
    rows = build_reopen_work_order_rows(
        [
            entry_row("R32-001"),
            entry_row("R32-002", status="not_visible", notes="not visible in source"),
        ],
        [protocol_row("R32-001"), protocol_row("R32-002", status="human_entry_present_ready_for_gate_rerun")],
        [chain_row("R32-001"), chain_row("R32-002", status="ready_for_revalidation_chain")],
        "docs/rota_32.html",
    )

    summary = summarize_reopen_work_order_rows(rows)

    assert summary["work_order_status"]["manual_fill_required"] == 1
    assert summary["work_order_status"]["ready_to_reopen_revalidation_chain"] == 1
    assert summary["priority_level"]["P0"] == 2
