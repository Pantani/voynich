from scripts.prepare_exact_form_visual_gap_queue import (
    build_gap_queue_rows,
    expand_manifest_folios,
    image_manifest_index,
    markdown_cell,
    priority_level,
    summarize_gap_queue_rows,
)


def test_expand_manifest_folios_handles_grouped_commons_rows():
    assert expand_manifest_folios("f67r1_r2") == {"f67r1", "f67r2"}
    assert expand_manifest_folios("f68r1_r2_r3") == {"f68r1", "f68r2", "f68r3"}
    assert expand_manifest_folios("f88v_f89r1_r2") == {"f88v", "f89r1", "f89r2"}
    assert expand_manifest_folios("f99v") == {"f99v"}


def test_image_manifest_index_maps_expanded_folios_to_manifest_rows():
    manifest = [
        {
            "folio": "f68r1_r2_r3",
            "image_url": "https://example.test/f68.jpg",
            "commons_page": "https://commons.test/f68",
        }
    ]

    index = image_manifest_index(manifest)

    assert index["f68r3"]["manifest_folio"] == "f68r1_r2_r3"
    assert index["f68r3"]["image_url"] == "https://example.test/f68.jpg"


def test_priority_level_prefers_available_images_and_larger_gaps():
    assert priority_level(8, "manifest_available") == "P0"
    assert priority_level(3, "manifest_available") == "P1"
    assert priority_level(12, "not_in_manifest") == "P1"
    assert priority_level(1, "manifest_available") == "P2"
    assert priority_level(1, "not_in_manifest") == "P3"


def test_build_gap_queue_rows_groups_unannotated_exact_forms_by_folio_and_locus_kind():
    exact_rows = [
        {
            "route26_id": "R26-0001",
            "folio": "f68r3",
            "locus": "f68r3.1,@Cc",
            "locus_kind": "C",
            "token": "otar",
            "prefix": "ot",
            "suffix": "ar",
            "line_position": "middle",
            "section_note": "cosmo",
            "visual_match_status": "no_visual_annotation",
        },
        {
            "route26_id": "R26-0002",
            "folio": "f68r3",
            "locus": "f68r3.2,@Cc",
            "locus_kind": "C",
            "token": "okal",
            "prefix": "ok",
            "suffix": "al",
            "line_position": "start",
            "section_note": "cosmo",
            "visual_match_status": "no_visual_annotation",
        },
        {
            "route26_id": "R26-0003",
            "folio": "f68r3",
            "locus": "f68r3.3,@Cc",
            "locus_kind": "C",
            "token": "otol",
            "prefix": "ot",
            "suffix": "ol",
            "line_position": "end",
            "section_note": "cosmo",
            "visual_match_status": "matched_visual_annotation",
        },
    ]
    manifest = [
        {
            "folio": "f68r1_r2_r3",
            "image_url": "https://example.test/f68.jpg",
            "commons_page": "https://commons.test/f68",
        }
    ]

    rows = build_gap_queue_rows(exact_rows, manifest)

    assert len(rows) == 1
    assert rows[0]["route27_id"] == "R27-001"
    assert rows[0]["folio"] == "f68r3"
    assert rows[0]["locus_kind"] == "C"
    assert rows[0]["gap_rows"] == "2"
    assert rows[0]["unique_loci"] == "2"
    assert rows[0]["token_counts"] == "okal=1|otar=1"
    assert rows[0]["image_source_status"] == "manifest_available"
    assert rows[0]["image_manifest_folio"] == "f68r1_r2_r3"
    assert rows[0]["semantic_guardrail"] == "visual_gap_priority_not_evidence"


def test_build_gap_queue_rows_sorts_by_priority_then_gap_size():
    exact_rows = [
        {
            "route26_id": "R26-0001",
            "folio": "f1r",
            "locus": "f1r.1,@P0",
            "locus_kind": "P",
            "token": "otar",
            "prefix": "ot",
            "suffix": "ar",
            "line_position": "middle",
            "visual_match_status": "no_visual_annotation",
        },
        {
            "route26_id": "R26-0002",
            "folio": "f70v2",
            "locus": "f70v2.1,@Cc",
            "locus_kind": "C",
            "token": "okal",
            "prefix": "ok",
            "suffix": "al",
            "line_position": "middle",
            "visual_match_status": "no_visual_annotation",
        },
        {
            "route26_id": "R26-0003",
            "folio": "f70v2",
            "locus": "f70v2.2,@Cc",
            "locus_kind": "C",
            "token": "okar",
            "prefix": "ok",
            "suffix": "ar",
            "line_position": "middle",
            "visual_match_status": "no_visual_annotation",
        },
    ]
    manifest = [{"folio": "f70v2", "image_url": "https://example.test/f70.jpg", "commons_page": ""}]

    rows = build_gap_queue_rows(exact_rows, manifest)

    assert rows[0]["folio"] == "f70v2"
    assert rows[0]["priority_level"] == "P1"
    assert rows[1]["folio"] == "f1r"


def test_summarize_gap_queue_rows_counts_priority_image_status_and_locus_kind():
    rows = [
        {
            "priority_level": "P0",
            "image_source_status": "manifest_available",
            "locus_kind": "C",
            "folio": "f68r3",
        },
        {
            "priority_level": "P1",
            "image_source_status": "not_in_manifest",
            "locus_kind": "P",
            "folio": "f113v",
        },
    ]

    summary = summarize_gap_queue_rows(rows)

    assert summary["priority_level"]["P0"] == 1
    assert summary["image_source_status"]["not_in_manifest"] == 1
    assert summary["locus_kind"]["P"] == 1
    assert summary["folio"]["f68r3"] == 1


def test_markdown_cell_preserves_pipe_separated_counters_inside_one_cell():
    assert markdown_cell("okal=1|otar=1") == "okal=1<br>otar=1"
