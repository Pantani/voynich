from pathlib import Path

from scripts.prepare_review_crops import (
    build_crop_manifest,
    clamp_box,
    crop_file_name,
    rough_crop_box,
    svg_for_crop,
)


def test_clamp_box_keeps_crop_inside_image():
    assert clamp_box((-5, 10, 120, 250), 100, 200) == (0, 10, 100, 190)


def test_rough_crop_box_uses_folio_specific_region():
    f67 = {
        "folio": "f67r1",
        "image_files": "images/raw/commons_f67r1_r2.jpg",
        "ring": "outer/annular text around left-page diagram",
    }
    f68 = {
        "folio": "f68r3",
        "image_files": "images/raw/commons_f68r1_r2_r3.jpg",
        "ring": "annular/circular text",
    }

    f67_box = rough_crop_box(f67, 1000, 800)
    f68_box = rough_crop_box(f68, 1000, 800)

    assert f67_box[0] < 150
    assert f67_box[2] < 600
    assert f68_box[0] > 550
    assert f68_box[2] < 450


def test_build_crop_manifest_preserves_not_isolated_status():
    rows = [
        {
            "review_id": "R6-001",
            "folio": "f67r1",
            "locus": "f67r1.6,+Cc",
            "prefix_family": "d",
            "group_tokens": "dal dar dol",
            "matched_annotation_tokens": "dal dar",
            "missing_group_tokens": "dol",
            "exact_glyph_status": "needs_exact_glyph_isolation",
            "image_files": "images/raw/commons_f67r1_r2.jpg",
            "ring": "outer/annular text around left-page diagram",
            "visual_zones": "circular text",
        }
    ]

    manifest = build_crop_manifest(rows, {"images/raw/commons_f67r1_r2.jpg": (1000, 800)})

    assert manifest[0]["crop_id"] == "R7-001"
    assert manifest[0]["source_review_id"] == "R6-001"
    assert manifest[0]["isolation_status"] == "needs_exact_glyph_isolation"
    assert manifest[0]["crop_scope"] == "rough_region_only"
    assert manifest[0]["crop_svg"].endswith("R7-001_R6-001_f67r1.svg")


def test_svg_for_crop_uses_viewbox_and_relative_image_href():
    row = {
        "crop_id": "R7-001",
        "source_review_id": "R6-001",
        "folio": "f67r1",
        "locus": "f67r1.6,+Cc",
        "group_tokens": "dal dar dol",
        "crop_x": "10",
        "crop_y": "20",
        "crop_width": "300",
        "crop_height": "200",
        "image_width": "1000",
        "image_height": "800",
        "source_image": "images/raw/commons_f67r1_r2.jpg",
        "isolation_status": "needs_exact_glyph_isolation",
    }

    svg = svg_for_crop(row, Path("images/derived/review_crops"))

    assert 'viewBox="10 20 300 200"' in svg
    assert 'href="../../raw/commons_f67r1_r2.jpg"' in svg
    assert "needs_exact_glyph_isolation" in svg


def test_crop_file_name_is_stable_and_safe():
    assert crop_file_name("R7-001", "R6-001", "f67r1") == "R7-001_R6-001_f67r1.svg"
