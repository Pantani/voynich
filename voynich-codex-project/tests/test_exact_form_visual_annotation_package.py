from scripts.prepare_exact_form_visual_annotation_package import (
    build_annotation_package_rows,
    markdown_cell,
    render_html_card,
    summarize_annotation_package_rows,
)


def queue_row(route27_id, priority_level, image_source_status, gap_rows="2"):
    return {
        "route27_id": route27_id,
        "folio": "f99v" if image_source_status == "manifest_available" else "f113v",
        "locus_kind": "P",
        "gap_rows": gap_rows,
        "unique_loci": "2",
        "token_counts": "okal=1|otar=1",
        "prefix_counts": "ok=1|ot=1",
        "suffix_counts": "al=1|ar=1",
        "line_position_counts": "middle=2",
        "top_loci": "f99v.1,+P0|f99v.2,+P0",
        "section_notes": "label row",
        "image_source_status": image_source_status,
        "image_manifest_folio": "f99v" if image_source_status == "manifest_available" else "",
        "image_url": "https://example.test/f99v.jpg" if image_source_status == "manifest_available" else "",
        "commons_page": "https://commons.test/f99v" if image_source_status == "manifest_available" else "",
        "priority_level": priority_level,
        "priority_reason": "some_reason",
        "review_action": "source_action",
        "semantic_guardrail": "visual_gap_priority_not_evidence",
    }


def test_build_annotation_package_rows_filters_p0_p1_and_splits_workstreams():
    rows = build_annotation_package_rows(
        [
            queue_row("R27-001", "P0", "manifest_available", gap_rows="8"),
            queue_row("R27-002", "P1", "not_in_manifest", gap_rows="12"),
            queue_row("R27-003", "P2", "manifest_available", gap_rows="1"),
        ]
    )

    assert [row["route28_id"] for row in rows] == ["R28-001", "R28-002"]
    assert rows[0]["route27_id"] == "R27-001"
    assert rows[0]["workstream"] == "annotate_from_manifest_image"
    assert rows[0]["package_status"] == "ready_for_manual_visual_annotation"
    assert rows[0]["manual_annotation_status"] == ""
    assert rows[0]["manual_visual_notes"] == ""
    assert rows[0]["semantic_guardrail"] == "visual_annotation_package_not_evidence"
    assert rows[1]["workstream"] == "source_image_required"
    assert rows[1]["package_status"] == "blocked_pending_source_image"


def test_summarize_annotation_package_rows_counts_workstream_and_priority():
    rows = build_annotation_package_rows(
        [
            queue_row("R27-001", "P0", "manifest_available"),
            queue_row("R27-002", "P1", "not_in_manifest"),
        ]
    )

    summary = summarize_annotation_package_rows(rows)

    assert summary["priority_level"]["P0"] == 1
    assert summary["workstream"]["annotate_from_manifest_image"] == 1
    assert summary["package_status"]["blocked_pending_source_image"] == 1
    assert summary["image_source_status"]["not_in_manifest"] == 1


def test_markdown_cell_keeps_pipe_separated_counts_inside_one_cell():
    assert markdown_cell("okal=1|otar=1") == "okal=1<br>otar=1"


def test_render_html_card_uses_image_when_ready_and_does_not_infer_missing_source():
    ready = build_annotation_package_rows([queue_row("R27-001", "P0", "manifest_available")])[0]
    blocked = build_annotation_package_rows([queue_row("R27-002", "P1", "not_in_manifest")])[0]

    ready_html = render_html_card(ready)
    blocked_html = render_html_card(blocked)

    assert '<img src="https://example.test/f99v.jpg"' in ready_html
    assert "Imagem ainda nao esta no manifesto" in blocked_html
    assert "visual_annotation_package_not_evidence" in blocked_html
