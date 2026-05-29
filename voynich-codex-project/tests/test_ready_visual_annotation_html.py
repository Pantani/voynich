from scripts.prepare_ready_visual_annotation_html import (
    build_ready_html_rows,
    render_html_card,
    render_markdown_section,
    summarize_ready_html_rows,
)


def package_row(route28_id, package_status, folio="f99v", priority_level="P1", locus_kind="P"):
    return {
        "route28_id": route28_id,
        "route27_id": route28_id.replace("R28", "R27"),
        "folio": folio,
        "locus_kind": locus_kind,
        "priority_level": priority_level,
        "gap_rows": "8",
        "unique_loci": "5",
        "token_counts": "okal=3|otar=2",
        "top_loci": f"{folio}.1,+P0|{folio}.2,+P0",
        "section_notes": "paragraph labels",
        "image_url": f"https://example.test/{folio}.jpg",
        "commons_page": f"https://commons.test/{folio}",
        "package_status": package_status,
        "manual_annotation_status": "",
        "manual_source_image_url": "",
        "manual_visual_notes": "",
    }


def validation_row(route28_id, status="pending_blank_manual_annotation"):
    return {
        "route31_id": route28_id.replace("R28", "R31"),
        "route28_id": route28_id,
        "manual_validation_status": status,
    }


def test_build_ready_html_rows_filters_pending_ready_items_only():
    rows = build_ready_html_rows(
        [
            package_row("R28-001", "ready_for_manual_visual_annotation", folio="f99v", priority_level="P0"),
            package_row("R28-002", "blocked_pending_source_image", folio="f113v"),
            package_row("R28-003", "ready_for_manual_visual_annotation", folio="f84r"),
        ],
        [
            validation_row("R28-001"),
            validation_row("R28-003", status="valid_manual_annotation"),
        ],
    )

    assert len(rows) == 1
    assert rows[0]["route32_id"] == "R32-001"
    assert rows[0]["route31_id"] == "R31-001"
    assert rows[0]["route28_id"] == "R28-001"
    assert rows[0]["folio"] == "f99v"
    assert rows[0]["html_card_status"] == "ready_for_focused_manual_visual_annotation"


def test_build_ready_html_rows_preserves_traceability_allowed_values_and_blank_fields():
    rows = build_ready_html_rows(
        [package_row("R28-001", "ready_for_manual_visual_annotation")],
        [validation_row("R28-001")],
    )

    assert rows[0]["allowed_manual_annotation_status"] == "annotated/not_visible/uncertain"
    assert rows[0]["fields_to_fill"] == "manual_annotation_status manual_visual_notes"
    assert rows[0]["manual_annotation_status"] == ""
    assert rows[0]["manual_visual_notes"] == ""
    assert rows[0]["output_rule"] == "copy_completed_fields_back_to_route28_package_then_rerun_route31"
    assert rows[0]["semantic_guardrail"] == "focused_visual_annotation_html_not_evidence"


def test_summarize_ready_html_rows_counts_status_priority_and_locus():
    rows = build_ready_html_rows(
        [
            package_row("R28-001", "ready_for_manual_visual_annotation", priority_level="P0", locus_kind="P"),
            package_row("R28-002", "ready_for_manual_visual_annotation", folio="f99r", locus_kind="L"),
        ],
        [validation_row("R28-001"), validation_row("R28-002")],
    )

    summary = summarize_ready_html_rows(rows)

    assert summary["html_card_status"]["ready_for_focused_manual_visual_annotation"] == 2
    assert summary["priority_level"]["P0"] == 1
    assert summary["priority_level"]["P1"] == 1
    assert summary["locus_kind"]["L"] == 1
    assert summary["folio"]["f99r"] == 1


def test_render_html_card_includes_manifest_image_allowed_statuses_and_guardrail():
    row = build_ready_html_rows(
        [package_row("R28-001", "ready_for_manual_visual_annotation", folio="f99v")],
        [validation_row("R28-001")],
    )[0]

    html = render_html_card(row)

    assert '<img src="https://example.test/f99v.jpg"' in html
    assert "annotated/not_visible/uncertain" in html
    assert "manual_annotation_status" in html
    assert "manual_visual_notes" in html
    assert "focused_visual_annotation_html_not_evidence" in html


def test_render_markdown_section_includes_output_rule_and_guardrail():
    row = build_ready_html_rows(
        [package_row("R28-001", "ready_for_manual_visual_annotation")],
        [validation_row("R28-001")],
    )[0]

    text = render_markdown_section(row)

    assert "R32-001" in text
    assert "copy_completed_fields_back_to_route28_package_then_rerun_route31" in text
    assert "focused_visual_annotation_html_not_evidence" in text
