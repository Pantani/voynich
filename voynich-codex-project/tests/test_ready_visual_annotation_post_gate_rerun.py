from scripts.plan_ready_visual_annotation_post_gate_rerun import (
    build_post_gate_rows,
    post_gate_status,
    summarize_post_gate_rows,
)


def gate_row(route34_id="R34-001", gate="blocked_pending_manual_annotation"):
    return {
        "route34_id": route34_id,
        "route32_id": route34_id.replace("R34", "R32"),
        "route33_id": route34_id.replace("R34", "R33"),
        "route31_id": route34_id.replace("R34", "R31"),
        "route28_id": "R28-001",
        "folio": "f99v",
        "priority_level": "P0",
        "locus_kind": "P",
        "gate_status": gate,
        "next_action": "fill_r32_entry_sheet_using_html_then_rerun_r33_r31",
        "semantic_guardrail": "manual_visual_gate_not_evidence",
    }


def test_post_gate_status_blocks_when_manual_gate_is_pending():
    assert post_gate_status("blocked_pending_manual_annotation") == (
        "blocked_by_manual_gate",
        "skip_r33_r31_rerun_until_manual_entries",
        "fill_r32_entry_sheet_using_html_then_rerun_r34",
    )


def test_post_gate_status_marks_ready_rows_for_controlled_rerun():
    assert post_gate_status("ready_to_rerun_r33_r31") == (
        "ready_for_controlled_rerun",
        "rerun_r33_then_r31_for_explicit_entries",
        "run_r33_apply_entries_then_r31_validation",
    )


def test_build_post_gate_rows_preserves_traceability_and_guardrail():
    rows = build_post_gate_rows([gate_row()])

    assert rows[0]["route35_id"] == "R35-001"
    assert rows[0]["route34_id"] == "R34-001"
    assert rows[0]["route32_id"] == "R32-001"
    assert rows[0]["r35_status"] == "blocked_by_manual_gate"
    assert rows[0]["rerun_action"] == "skip_r33_r31_rerun_until_manual_entries"
    assert rows[0]["next_action"] == "fill_r32_entry_sheet_using_html_then_rerun_r34"
    assert rows[0]["semantic_guardrail"] == "post_gate_rerun_not_visual_evidence"


def test_build_post_gate_rows_handles_ready_and_invalid_gate_rows():
    rows = build_post_gate_rows(
        [
            gate_row("R34-001", gate="ready_to_rerun_r33_r31"),
            gate_row("R34-002", gate="blocked_invalid_manual_annotation"),
        ]
    )

    assert rows[0]["r35_status"] == "ready_for_controlled_rerun"
    assert rows[0]["rerun_action"] == "rerun_r33_then_r31_for_explicit_entries"
    assert rows[1]["r35_status"] == "blocked_by_gate_issue"
    assert rows[1]["rerun_action"] == "skip_r33_r31_rerun_until_gate_clean"


def test_summarize_post_gate_rows_counts_status_action_and_priority():
    rows = build_post_gate_rows(
        [
            gate_row("R34-001", gate="blocked_pending_manual_annotation"),
            gate_row("R34-002", gate="ready_to_rerun_r33_r31"),
        ]
    )

    summary = summarize_post_gate_rows(rows)

    assert summary["r35_status"]["blocked_by_manual_gate"] == 1
    assert summary["r35_status"]["ready_for_controlled_rerun"] == 1
    assert summary["rerun_action"]["skip_r33_r31_rerun_until_manual_entries"] == 1
    assert summary["priority_level"]["P0"] == 2
