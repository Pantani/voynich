from scripts.prepare_ready_visual_annotation_external_human_entry_packet import (
    build_external_human_entry_rows,
    external_entry_status,
    summarize_external_human_entry_rows,
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
        "fields_to_fill": "manual_annotation_status manual_visual_notes",
        "manual_annotation_status": status,
        "manual_visual_notes": notes,
    }


def work_order_row(route32_id="R32-001"):
    return {
        "route38_id": route32_id.replace("R32", "R38"),
        "route32_id": route32_id,
        "html_reference": "docs/rota_32.html",
        "work_order_status": "manual_fill_required",
    }


def plan_row(route32_id="R32-001", status="blocked_waiting_human_entry"):
    return {
        "route40_id": route32_id.replace("R32", "R40"),
        "route39_id": route32_id.replace("R32", "R39"),
        "route38_id": route32_id.replace("R32", "R38"),
        "route32_id": route32_id,
        "reopen_plan_status": status,
        "planned_chain_action": "do_not_run_revalidation_chain",
        "next_action": "fill_r32_manual_fields_then_rerun_r36_r37_r39",
    }


def test_external_entry_status_requires_blank_manual_fields_to_be_filled_by_human():
    assert external_entry_status("", "", "blocked_waiting_human_entry") == (
        "external_human_entry_required",
        "fill_r32_manual_annotation_status_and_notes",
        "do_not_modify_derived_outputs",
    )


def test_external_entry_status_rejects_partial_manual_fields():
    assert external_entry_status("annotated", "", "blocked_waiting_human_entry") == (
        "invalid_partial_r32_manual_entry",
        "complete_or_clear_r32_manual_fields",
        "rerun_r36_r37_r39_r40_after_fix",
    )


def test_external_entry_status_rejects_unknown_manual_status():
    assert external_entry_status("visible", "looks visible", "blocked_waiting_human_entry") == (
        "invalid_manual_annotation_status",
        "use_allowed_status_annotated_not_visible_uncertain",
        "rerun_r36_r37_r39_r40_after_fix",
    )


def test_external_entry_status_marks_present_entry_for_refresh():
    assert external_entry_status("uncertain", "ambiguous source image", "blocked_waiting_human_entry") == (
        "external_human_entry_present",
        "rerun_r36_r37_r39_r40",
        "do_not_run_chain_until_r40_ready",
    )


def test_build_external_human_entry_rows_preserves_blank_fields_and_targets_r32():
    rows = build_external_human_entry_rows(
        [entry_row()],
        [work_order_row()],
        [plan_row()],
        "data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv",
    )

    assert rows[0]["route41_id"] == "R41-001"
    assert rows[0]["route40_id"] == "R40-001"
    assert rows[0]["route38_id"] == "R38-001"
    assert rows[0]["route32_id"] == "R32-001"
    assert rows[0]["target_csv"] == "data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv"
    assert rows[0]["target_fields"] == "manual_annotation_status manual_visual_notes"
    assert rows[0]["manual_annotation_status"] == ""
    assert rows[0]["manual_visual_notes"] == ""
    assert rows[0]["external_entry_status"] == "external_human_entry_required"
    assert rows[0]["reviewer_action"] == "fill_r32_manual_annotation_status_and_notes"
    assert rows[0]["html_reference"] == "docs/rota_32.html"
    assert rows[0]["semantic_guardrail"] == "external_human_entry_packet_not_visual_evidence"


def test_build_external_human_entry_rows_marks_present_entry_without_changing_values():
    rows = build_external_human_entry_rows(
        [entry_row(status="not_visible", notes="source checked; target form not visible")],
        [work_order_row()],
        [plan_row()],
        "data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv",
    )

    assert rows[0]["manual_annotation_status"] == "not_visible"
    assert rows[0]["manual_visual_notes"] == "source checked; target form not visible"
    assert rows[0]["external_entry_status"] == "external_human_entry_present"
    assert rows[0]["reviewer_action"] == "rerun_r36_r37_r39_r40"


def test_summarize_external_human_entry_rows_counts_statuses():
    rows = build_external_human_entry_rows(
        [
            entry_row("R32-001"),
            entry_row("R32-002", status="uncertain", notes="ambiguous source image"),
        ],
        [work_order_row("R32-001"), work_order_row("R32-002")],
        [plan_row("R32-001"), plan_row("R32-002")],
        "data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv",
    )

    summary = summarize_external_human_entry_rows(rows)

    assert summary["external_entry_status"]["external_human_entry_required"] == 1
    assert summary["external_entry_status"]["external_human_entry_present"] == 1
    assert summary["reviewer_action"]["fill_r32_manual_annotation_status_and_notes"] == 1
    assert summary["reviewer_action"]["rerun_r36_r37_r39_r40"] == 1
