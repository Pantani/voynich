from scripts.prepare_ready_visual_annotation_manual_fill_protocol import (
    build_manual_fill_rows,
    manual_fill_status,
    summarize_manual_fill_rows,
)


def entry_row(route32_id="R32-001", status="", notes=""):
    return {
        "route32_id": route32_id,
        "route31_id": route32_id.replace("R32", "R31"),
        "route28_id": "R28-001",
        "folio": "f99v",
        "priority_level": "P0",
        "locus_kind": "P",
        "manual_annotation_status": status,
        "manual_visual_notes": notes,
        "allowed_manual_annotation_status": "annotated/not_visible/uncertain",
    }


def post_gate_row(route32_id="R32-001", r35_status="blocked_by_manual_gate"):
    return {
        "route35_id": route32_id.replace("R32", "R35"),
        "route34_id": route32_id.replace("R32", "R34"),
        "route32_id": route32_id,
        "route28_id": "R28-001",
        "r35_status": r35_status,
        "rerun_action": "skip_r33_r31_rerun_until_manual_entries",
        "next_action": "fill_r32_entry_sheet_using_html_then_rerun_r34",
    }


def test_manual_fill_status_waits_for_blank_human_entry():
    assert manual_fill_status("", "") == (
        "awaiting_human_visual_entry",
        "manual_entry_required",
        "open_r32_html_fill_status_and_notes_then_rerun_r34",
    )


def test_manual_fill_status_accepts_allowed_status_with_notes():
    assert manual_fill_status("uncertain", "visible but ambiguous") == (
        "human_entry_present_ready_for_gate_rerun",
        "manual_entry_present",
        "rerun_r34_then_r35",
    )


def test_manual_fill_status_rejects_invalid_or_incomplete_values():
    assert manual_fill_status("maybe", "bad") == (
        "invalid_manual_entry_needs_correction",
        "manual_annotation_status_not_allowed",
        "fix_r32_status_and_notes_then_rerun_r34",
    )
    assert manual_fill_status("annotated", "") == (
        "invalid_manual_entry_needs_correction",
        "manual_visual_notes_required",
        "fix_r32_status_and_notes_then_rerun_r34",
    )


def test_build_manual_fill_rows_preserves_blank_fields_and_traceability():
    rows = build_manual_fill_rows([entry_row()], [post_gate_row()], "docs/rota_32.html")

    assert rows[0]["route36_id"] == "R36-001"
    assert rows[0]["route35_id"] == "R35-001"
    assert rows[0]["route32_id"] == "R32-001"
    assert rows[0]["manual_annotation_status"] == ""
    assert rows[0]["manual_visual_notes"] == ""
    assert rows[0]["manual_fill_status"] == "awaiting_human_visual_entry"
    assert rows[0]["html_reference"] == "docs/rota_32.html"
    assert rows[0]["semantic_guardrail"] == "manual_fill_protocol_not_visual_evidence"


def test_build_manual_fill_rows_marks_ready_entries_without_changing_values():
    rows = build_manual_fill_rows(
        [entry_row(status="not_visible", notes="target group not visible in source image")],
        [post_gate_row()],
        "docs/rota_32.html",
    )

    assert rows[0]["manual_annotation_status"] == "not_visible"
    assert rows[0]["manual_fill_status"] == "human_entry_present_ready_for_gate_rerun"
    assert rows[0]["next_action"] == "rerun_r34_then_r35"


def test_summarize_manual_fill_rows_counts_status_and_priority():
    rows = build_manual_fill_rows(
        [
            entry_row(route32_id="R32-001"),
            entry_row(route32_id="R32-002", status="annotated", notes="visible near label"),
        ],
        [post_gate_row("R32-001"), post_gate_row("R32-002")],
        "docs/rota_32.html",
    )

    summary = summarize_manual_fill_rows(rows)

    assert summary["manual_fill_status"]["awaiting_human_visual_entry"] == 1
    assert summary["manual_fill_status"]["human_entry_present_ready_for_gate_rerun"] == 1
    assert summary["priority_level"]["P0"] == 2
