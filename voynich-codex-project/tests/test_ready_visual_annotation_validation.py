from scripts.validate_ready_visual_annotations import (
    build_manual_annotation_rows,
    build_valid_manual_annotations,
    summarize_manual_annotation_rows,
)


def package_row(route28_id="R28-001", package_status="ready_for_manual_visual_annotation", manual_status="", notes=""):
    return {
        "route28_id": route28_id,
        "route27_id": route28_id.replace("R28", "R27"),
        "folio": "f99v",
        "locus_kind": "P",
        "priority_level": "P1",
        "gap_rows": "2",
        "unique_loci": "2",
        "token_counts": "okal=1|otar=1",
        "top_loci": "f99v.1,+P0|f99v.2,+P0",
        "section_notes": "label row",
        "image_source_status": "manifest_available",
        "image_manifest_folio": "f99v",
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/69/Voynich_Manuscript_%28176%29.jpg",
        "commons_page": "https://commons.wikimedia.org/wiki/File:Voynich_Manuscript_(176).jpg",
        "workstream": "annotate_from_manifest_image",
        "package_status": package_status,
        "manual_annotation_status": manual_status,
        "manual_source_image_url": "",
        "manual_visual_notes": notes,
        "semantic_guardrail": "visual_annotation_package_not_evidence",
    }


def test_build_manual_annotation_rows_filters_ready_items_and_keeps_blank_pending():
    rows = build_manual_annotation_rows(
        [
            package_row("R28-001", "ready_for_manual_visual_annotation"),
            package_row("R28-002", "blocked_pending_source_image"),
        ]
    )

    assert len(rows) == 1
    assert rows[0]["route31_id"] == "R31-001"
    assert rows[0]["route28_id"] == "R28-001"
    assert rows[0]["manual_validation_status"] == "pending_blank_manual_annotation"
    assert rows[0]["apply_status"] == "skipped_blank_manual_annotation"
    assert rows[0]["manual_annotation_valid"] == "no"
    assert rows[0]["semantic_guardrail"] == "manual_visual_annotation_not_axis_meaning"


def test_build_manual_annotation_rows_accepts_allowed_status_with_notes():
    rows = build_manual_annotation_rows(
        [package_row(manual_status="annotated", notes="manual note: exact forms visible near labels")]
    )

    assert rows[0]["manual_validation_status"] == "valid_manual_annotation"
    assert rows[0]["apply_status"] == "manual_annotation_recorded"
    assert rows[0]["manual_annotation_valid"] == "yes"


def test_build_manual_annotation_rows_rejects_invalid_or_incomplete_values():
    invalid = build_manual_annotation_rows([package_row(manual_status="seen", notes="bad status")])[0]
    incomplete = build_manual_annotation_rows([package_row(manual_status="annotated", notes="")])[0]

    assert invalid["manual_validation_status"] == "invalid_manual_annotation"
    assert invalid["validation_reason"] == "manual_annotation_status_not_allowed"
    assert incomplete["manual_validation_status"] == "invalid_manual_annotation"
    assert incomplete["validation_reason"] == "manual_visual_notes_required_for_filled_status"


def test_build_valid_manual_annotations_keeps_only_valid_records():
    validation_rows = build_manual_annotation_rows(
        [
            package_row("R28-001"),
            package_row("R28-002", manual_status="uncertain", notes="manual note: unclear glyph shape"),
        ]
    )

    valid = build_valid_manual_annotations(validation_rows)

    assert len(valid) == 1
    assert valid[0]["route31_id"] == "R31-002"
    assert valid[0]["manual_annotation_status"] == "uncertain"
    assert valid[0]["semantic_guardrail"] == "manual_visual_annotation_not_axis_meaning"


def test_summarize_manual_annotation_rows_counts_validation_and_apply_statuses():
    rows = build_manual_annotation_rows(
        [
            package_row("R28-001"),
            package_row("R28-002", manual_status="not_visible", notes="manual note: not visible enough"),
        ]
    )

    summary = summarize_manual_annotation_rows(rows)

    assert summary["manual_validation_status"]["pending_blank_manual_annotation"] == 1
    assert summary["manual_validation_status"]["valid_manual_annotation"] == 1
    assert summary["apply_status"]["manual_annotation_recorded"] == 1
    assert summary["manual_annotation_valid"]["yes"] == 1
