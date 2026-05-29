from scripts.prepare_ready_visual_annotation_highres_source_packet import (
    build_highres_source_rows,
    build_manifest_index,
    folio_manifest_label_candidates,
    summarize_highres_source_rows,
)


def manifest_canvas(label, image_id="1000001", width=3000, height=4000):
    return {
        "label": {"none": [label]},
        "items": [
            {
                "items": [
                    {
                        "body": {
                            "id": f"https://collections.library.yale.edu/iiif/2/{image_id}/full/full/0/default.jpg",
                            "width": width,
                            "height": height,
                        }
                    }
                ]
            }
        ],
        "rendering": [
            {
                "id": f"https://collections.library.yale.edu/download/tiff/{image_id}",
                "label": {"en": ["Full size original"]},
            }
        ],
        "metadata": [
            {"label": {"en": ["Image ID"]}, "value": {"none": [image_id]}},
            {"label": {"en": ["Image Label"]}, "value": {"none": [label]}},
            {
                "label": {"en": ["Link to this Image"]},
                "value": {"none": [f"https://collections.library.yale.edu/catalog/2002046?child_oid={image_id}"]},
            },
        ],
    }


def entry_row(route32_id="R32-001", folio="f67r2"):
    return {
        "route32_id": route32_id,
        "route28_id": "R28-001",
        "folio": folio,
        "priority_level": "P0",
        "locus_kind": "P",
        "image_url": "https://upload.wikimedia.org/current.jpg",
        "commons_page": "https://commons.wikimedia.org/wiki/current",
        "top_loci": f"{folio}.35,@Pb",
        "token_counts": "okol=2",
        "manual_annotation_status": "",
        "manual_visual_notes": "",
    }


def test_folio_manifest_label_candidates_collapses_subfolio_suffixes():
    assert folio_manifest_label_candidates("f67r2") == ["67r2", "67r"]
    assert folio_manifest_label_candidates("f67v1") == ["67v1", "67v"]
    assert folio_manifest_label_candidates("f99v") == ["99v"]


def test_build_manifest_index_preserves_image_metadata():
    index = build_manifest_index({"items": [manifest_canvas("67r", "1006194", 4972, 3738)]})

    assert index["67r"]["image_id"] == "1006194"
    assert index["67r"]["iiif_jpg_url"] == "https://collections.library.yale.edu/iiif/2/1006194/full/full/0/default.jpg"
    assert index["67r"]["width"] == "4972"
    assert index["67r"]["height"] == "3738"
    assert index["67r"]["tiff_url"] == "https://collections.library.yale.edu/download/tiff/1006194"


def test_build_highres_source_rows_uses_collapsed_manifest_label():
    rows = build_highres_source_rows(
        [entry_row()],
        build_manifest_index({"items": [manifest_canvas("67r", "1006194", 4972, 3738)]}),
        "images/raw/highres_test_missing",
    )

    assert rows[0]["route42_id"] == "R42-001"
    assert rows[0]["route32_id"] == "R32-001"
    assert rows[0]["folio"] == "f67r2"
    assert rows[0]["manifest_label"] == "67r"
    assert rows[0]["match_status"] == "matched_collapsed_folio"
    assert rows[0]["yale_image_id"] == "1006194"
    assert rows[0]["local_image_path"] == "images/raw/highres_test_missing/f67r2_1006194.jpg"
    assert rows[0]["semantic_guardrail"] == "highres_source_download_not_visual_evidence"


def test_build_highres_source_rows_matches_composite_manifest_label():
    rows = build_highres_source_rows(
        [entry_row(folio="f89r2")],
        build_manifest_index({"items": [manifest_canvas("88v and 89r", "1006233", 9078, 3777)]}),
        "images/raw/highres_test_missing",
    )

    assert rows[0]["manifest_label"] == "88v and 89r"
    assert rows[0]["match_status"] == "matched_composite_manifest_label"
    assert rows[0]["local_image_path"] == "images/raw/highres_test_missing/f89r2_1006233.jpg"


def test_build_highres_source_rows_marks_missing_manifest_label():
    rows = build_highres_source_rows(
        [entry_row(folio="f999r")],
        build_manifest_index({"items": [manifest_canvas("67r", "1006194", 4972, 3738)]}),
        "images/raw/highres_test_missing",
    )

    assert rows[0]["manifest_label"] == ""
    assert rows[0]["match_status"] == "missing_yale_manifest_match"
    assert rows[0]["yale_iiif_jpg_url"] == ""
    assert rows[0]["local_image_path"] == ""


def test_summarize_highres_source_rows_counts_matches():
    rows = build_highres_source_rows(
        [entry_row("R32-001", "f67r2"), entry_row("R32-002", "f99v")],
        build_manifest_index(
            {
                "items": [
                    manifest_canvas("67r", "1006194", 4972, 3738),
                    manifest_canvas("99v", "1006247", 2802, 3697),
                ]
            }
        ),
        "images/raw/highres_test_missing",
    )

    summary = summarize_highres_source_rows(rows)

    assert summary["match_status"]["matched_collapsed_folio"] == 1
    assert summary["match_status"]["matched_exact_manifest_label"] == 1
    assert summary["download_plan_status"]["download_pending"] == 2
