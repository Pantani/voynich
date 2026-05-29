from scripts.plan_ready_visual_annotation_conditional_chain_reopen import (
    build_conditional_reopen_rows,
    chain_reopen_plan_status,
    summarize_conditional_reopen_rows,
)


def audit_row(
    route32_id="R32-001",
    fill_status="manual_fill_not_executed",
    release_status="blocked_no_manual_entry",
    next_action="human_fill_r32_fields_from_r38_order",
):
    return {
        "route39_id": route32_id.replace("R32", "R39"),
        "route38_id": route32_id.replace("R32", "R38"),
        "route37_id": route32_id.replace("R32", "R37"),
        "route36_id": route32_id.replace("R32", "R36"),
        "route32_id": route32_id,
        "route31_id": route32_id.replace("R32", "R31"),
        "route28_id": "R28-001",
        "folio": "f99v",
        "priority_level": "P0",
        "locus_kind": "P",
        "fill_execution_status": fill_status,
        "chain_release_status": release_status,
        "next_action": next_action,
    }


def test_chain_reopen_plan_status_blocks_when_manual_fill_not_executed():
    assert chain_reopen_plan_status("manual_fill_not_executed", "blocked_no_manual_entry", "human_fill_r32_fields_from_r38_order") == (
        "blocked_waiting_human_entry",
        "do_not_run_revalidation_chain",
        "fill_r32_manual_fields_then_rerun_r36_r37_r39",
    )


def test_chain_reopen_plan_status_blocks_until_protocol_refresh():
    assert chain_reopen_plan_status(
        "manual_entry_present_protocol_refresh_required",
        "blocked_until_r36_r37_refresh",
        "rerun_r36_r37_then_recompute_r39",
    ) == (
        "blocked_pending_protocol_refresh",
        "do_not_run_revalidation_chain",
        "rerun_r36_r37_r39_before_chain",
    )


def test_chain_reopen_plan_status_blocks_invalid_manual_entry():
    assert chain_reopen_plan_status(
        "invalid_partial_manual_entry",
        "blocked_invalid_manual_entry",
        "complete_or_clear_r32_manual_fields_then_rerun_r36",
    ) == (
        "blocked_invalid_manual_entry",
        "do_not_run_revalidation_chain",
        "complete_or_clear_r32_manual_fields_then_rerun_r36",
    )


def test_chain_reopen_plan_status_releases_only_when_r39_is_ready():
    assert chain_reopen_plan_status(
        "ready_for_revalidation_chain_reopen",
        "ready_to_reopen_chain",
        "rerun_r34_r35_r33_r31",
    ) == (
        "ready_to_run_revalidation_chain",
        "run_R34_R35_R33_R31",
        "execute_chain_and_validate_outputs",
    )


def test_build_conditional_reopen_rows_preserves_traceability_and_blocks_blank_audit():
    rows = build_conditional_reopen_rows([audit_row()])

    assert rows[0]["route40_id"] == "R40-001"
    assert rows[0]["route39_id"] == "R39-001"
    assert rows[0]["route32_id"] == "R32-001"
    assert rows[0]["chain_order"] == "R34>R35>R33>R31"
    assert rows[0]["reopen_plan_status"] == "blocked_waiting_human_entry"
    assert rows[0]["planned_chain_action"] == "do_not_run_revalidation_chain"
    assert rows[0]["next_action"] == "fill_r32_manual_fields_then_rerun_r36_r37_r39"
    assert rows[0]["semantic_guardrail"] == "conditional_chain_reopen_plan_not_visual_evidence"


def test_build_conditional_reopen_rows_marks_ready_audit_for_chain_run():
    rows = build_conditional_reopen_rows(
        [
            audit_row(
                fill_status="ready_for_revalidation_chain_reopen",
                release_status="ready_to_reopen_chain",
                next_action="rerun_r34_r35_r33_r31",
            )
        ]
    )

    assert rows[0]["reopen_plan_status"] == "ready_to_run_revalidation_chain"
    assert rows[0]["planned_chain_action"] == "run_R34_R35_R33_R31"
    assert rows[0]["next_action"] == "execute_chain_and_validate_outputs"


def test_summarize_conditional_reopen_rows_counts_statuses():
    rows = build_conditional_reopen_rows(
        [
            audit_row("R32-001"),
            audit_row(
                "R32-002",
                fill_status="manual_entry_present_protocol_refresh_required",
                release_status="blocked_until_r36_r37_refresh",
                next_action="rerun_r36_r37_then_recompute_r39",
            ),
        ]
    )

    summary = summarize_conditional_reopen_rows(rows)

    assert summary["reopen_plan_status"]["blocked_waiting_human_entry"] == 1
    assert summary["reopen_plan_status"]["blocked_pending_protocol_refresh"] == 1
    assert summary["planned_chain_action"]["do_not_run_revalidation_chain"] == 2
