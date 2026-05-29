from scripts.prepare_manual_svg_review import (
    build_manual_rows,
    family_priority,
    manual_review_template,
    render_html,
)


def test_family_priority_puts_operator_families_first():
    assert family_priority("ot") < family_priority("ch")
    assert family_priority("ch") < family_priority("standalone")
    assert family_priority("d") < family_priority("standalone")


def test_manual_review_template_has_blank_coordinate_fields():
    row = {
        "decision_id": "R8-001",
        "crop_id": "R7-001",
        "source_review_id": "R6-001",
        "folio": "f67r1",
        "locus": "f67r1.6,+Cc",
        "prefix_family": "d",
        "group_tokens": "dal dar dol",
        "matched_annotation_tokens": "dal dar",
        "missing_group_tokens": "dol",
        "crop_svg": "images/derived/review_crops/R7-001_R6-001_f67r1.svg",
        "review_decision": "keep_not_isolated",
    }

    output = manual_review_template(row, 1)

    assert output["manual_review_id"] == "R9-001"
    assert output["manual_tighter_x"] == ""
    assert output["manual_tighter_y"] == ""
    assert output["manual_tighter_width"] == ""
    assert output["manual_tighter_height"] == ""
    assert output["manual_final_status"] == "pending_manual_review"


def test_build_manual_rows_sorts_by_family_then_missing_tokens():
    rows = [
        {"decision_id": "R8-002", "prefix_family": "standalone", "missing_group_tokens": "", "crop_id": "R7-002"},
        {"decision_id": "R8-010", "prefix_family": "ot", "missing_group_tokens": "oteedar", "crop_id": "R7-010"},
        {"decision_id": "R8-005", "prefix_family": "ch", "missing_group_tokens": "chedar", "crop_id": "R7-005"},
    ]

    output = build_manual_rows(rows)

    assert [row["decision_id"] for row in output] == ["R8-010", "R8-005", "R8-002"]


def test_render_html_embeds_svg_and_manual_fields():
    rows = [
        {
            "manual_review_id": "R9-001",
            "decision_id": "R8-001",
            "crop_id": "R7-001",
            "folio": "f67r1",
            "locus": "f67r1.6,+Cc",
            "prefix_family": "d",
            "group_tokens": "dal dar dol",
            "missing_group_tokens": "dol",
            "crop_svg": "images/derived/review_crops/R7-001_R6-001_f67r1.svg",
            "manual_final_status": "pending_manual_review",
        }
    ]

    html = render_html(rows)

    assert "R9-001" in html
    assert "../images/derived/review_crops/R7-001_R6-001_f67r1.svg" in html
    assert "manual_tighter_x" in html
    assert "pending_manual_review" in html
