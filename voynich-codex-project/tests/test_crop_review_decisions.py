from pathlib import Path
from tempfile import TemporaryDirectory

from scripts.review_crop_decisions import (
    build_decision_rows,
    decision_for_crop,
    region_label,
    svg_status,
)


def test_region_label_formats_manifest_coordinates():
    row = {"crop_x": "31", "crop_y": "158", "crop_width": "768", "crop_height": "913"}

    assert region_label(row) == "x=31 y=158 w=768 h=913"


def test_svg_status_reports_existing_valid_svg():
    with TemporaryDirectory() as tmp:
        svg = Path(tmp) / "crop.svg"
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>', encoding="utf-8")

        assert svg_status(svg) == "svg_ok"


def test_decision_for_rough_crop_keeps_not_isolated():
    row = {
        "crop_id": "R7-001",
        "crop_scope": "rough_region_only",
        "isolation_status": "needs_exact_glyph_isolation",
        "missing_group_tokens": "dol",
    }

    decision = decision_for_crop(row, "svg_ok")

    assert decision["review_decision"] == "keep_not_isolated"
    assert decision["coordinate_decision"] == "no_glyph_coordinates"
    assert decision["missing_token_status"] == "missing_tokens_remain"
    assert "rough_region_only" in decision["decision_reason"]


def test_build_decision_rows_preserves_crop_identity():
    with TemporaryDirectory() as tmp:
        svg = Path(tmp) / "R7-001_R6-001_f67r1.svg"
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg"></svg>', encoding="utf-8")
        rows = [
            {
                "crop_id": "R7-001",
                "source_review_id": "R6-001",
                "folio": "f67r1",
                "locus": "f67r1.6,+Cc",
                "group_tokens": "dal dar dol",
                "missing_group_tokens": "dol",
                "isolation_status": "needs_exact_glyph_isolation",
                "crop_scope": "rough_region_only",
                "crop_x": "31",
                "crop_y": "158",
                "crop_width": "768",
                "crop_height": "913",
                "crop_svg": str(svg),
            }
        ]

        decisions = build_decision_rows(rows)

    assert decisions[0]["decision_id"] == "R8-001"
    assert decisions[0]["crop_id"] == "R7-001"
    assert decisions[0]["source_review_id"] == "R6-001"
    assert decisions[0]["review_region"] == "x=31 y=158 w=768 h=913"
    assert decisions[0]["svg_status"] == "svg_ok"
