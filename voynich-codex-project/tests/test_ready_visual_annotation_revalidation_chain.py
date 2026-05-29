from scripts.plan_ready_visual_annotation_revalidation_chain import (
    build_revalidation_chain_rows,
    chain_status,
    summarize_revalidation_chain_rows,
)


def protocol_row(route36_id="R36-001", fill_status="awaiting_human_visual_entry"):
    return {
        "route36_id": route36_id,
        "route35_id": route36_id.replace("R36", "R35"),
        "route34_id": route36_id.replace("R36", "R34"),
        "route32_id": route36_id.replace("R36", "R32"),
        "route31_id": route36_id.replace("R36", "R31"),
        "route28_id": "R28-001",
        "folio": "f99v",
        "priority_level": "P0",
        "locus_kind": "P",
        "manual_fill_status": fill_status,
        "blocking_reason": "manual_entry_required",
        "next_action": "open_r32_html_fill_status_and_notes_then_rerun_r34",
        "semantic_guardrail": "manual_fill_protocol_not_visual_evidence",
    }


def test_chain_status_blocks_when_protocol_awaits_human_entry():
    assert chain_status("awaiting_human_visual_entry") == (
        "blocked_no_human_entries",
        "skip_r34_r35_r33_r31_until_manual_fill",
        "fill_r32_entry_sheet_then_rerun_r36",
    )


def test_chain_status_allows_ready_manual_entries_only():
    assert chain_status("human_entry_present_ready_for_gate_rerun") == (
        "ready_for_revalidation_chain",
        "run_r34_r35_r33_r31_in_order",
        "rerun_chain_and_review_r31_valid_annotations",
    )


def test_chain_status_blocks_invalid_protocol_entries():
    assert chain_status("invalid_manual_entry_needs_correction") == (
        "blocked_invalid_manual_entries",
        "skip_r34_r35_r33_r31_until_protocol_clean",
        "fix_r32_entries_then_rerun_r36",
    )


def test_build_revalidation_chain_rows_preserves_traceability_and_order():
    rows = build_revalidation_chain_rows([protocol_row()])

    assert rows[0]["route37_id"] == "R37-001"
    assert rows[0]["route36_id"] == "R36-001"
    assert rows[0]["route32_id"] == "R32-001"
    assert rows[0]["chain_order"] == "R34>R35>R33>R31"
    assert rows[0]["r37_status"] == "blocked_no_human_entries"
    assert rows[0]["chain_action"] == "skip_r34_r35_r33_r31_until_manual_fill"
    assert rows[0]["next_action"] == "fill_r32_entry_sheet_then_rerun_r36"
    assert rows[0]["semantic_guardrail"] == "revalidation_chain_not_visual_evidence"


def test_build_revalidation_chain_rows_marks_ready_and_invalid_protocol_rows():
    rows = build_revalidation_chain_rows(
        [
            protocol_row("R36-001", "human_entry_present_ready_for_gate_rerun"),
            protocol_row("R36-002", "invalid_manual_entry_needs_correction"),
        ]
    )

    assert rows[0]["r37_status"] == "ready_for_revalidation_chain"
    assert rows[0]["chain_action"] == "run_r34_r35_r33_r31_in_order"
    assert rows[1]["r37_status"] == "blocked_invalid_manual_entries"
    assert rows[1]["chain_action"] == "skip_r34_r35_r33_r31_until_protocol_clean"


def test_summarize_revalidation_chain_rows_counts_status_action_and_priority():
    rows = build_revalidation_chain_rows(
        [
            protocol_row("R36-001", "awaiting_human_visual_entry"),
            protocol_row("R36-002", "human_entry_present_ready_for_gate_rerun"),
        ]
    )

    summary = summarize_revalidation_chain_rows(rows)

    assert summary["r37_status"]["blocked_no_human_entries"] == 1
    assert summary["r37_status"]["ready_for_revalidation_chain"] == 1
    assert summary["chain_action"]["skip_r34_r35_r33_r31_until_manual_fill"] == 1
    assert summary["priority_level"]["P0"] == 2
