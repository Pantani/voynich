from scripts.prepare_direct_visual_decision_package import (
    build_direct_visual_rows,
    html_image_path,
    render_html_card,
    render_markdown_section,
    summarize_direct_visual_rows,
)


def test_html_image_path_is_relative_from_docs_directory():
    assert html_image_path("images/raw/commons_f67r1_r2.jpg") == "../images/raw/commons_f67r1_r2.jpg"
    assert html_image_path("") == ""


def test_build_direct_visual_rows_filters_pending_decisions_only():
    decisions = [
        {
            "route18_id": "R18-001",
            "route17_id": "R17-001",
            "checklist_id": "R13-001",
            "decision_bucket": "pending_manual_decision",
            "priority_level": "P0",
        },
        {
            "route18_id": "R18-002",
            "route17_id": "R17-002",
            "checklist_id": "R13-002",
            "decision_bucket": "new_crop_candidate",
            "priority_level": "P1",
        },
    ]

    rows = build_direct_visual_rows(decisions)

    assert len(rows) == 1
    assert rows[0]["route19_id"] == "R19-001"
    assert rows[0]["checklist_id"] == "R13-001"
    assert rows[0]["decision_package_status"] == "ready_for_manual_visual_decision"


def test_build_direct_visual_rows_preserves_traceability_and_blank_manual_fields():
    decisions = [
        {
            "route18_id": "R18-001",
            "route17_id": "R17-001",
            "route16_id": "R16-001",
            "instruction_item_id": "R15I-001",
            "checklist_id": "R13-001",
            "packet_id": "R12-001",
            "manual_review_id": "R9-001",
            "crop_id": "R7-009",
            "source_review_id": "R6-009",
            "folio": "f67r1",
            "locus": "f67r1.5,@Cc",
            "source_image": "images/raw/commons_f67r1_r2.jpg",
            "crop_svg": "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
            "review_region": "x=31 y=158 w=768 h=913",
            "priority_bucket": "P0_operator_missing_tokens",
            "priority_level": "P0",
            "target_type": "missing_group_tokens",
            "review_target": "otardar",
            "decision_bucket": "pending_manual_decision",
        }
    ]

    rows = build_direct_visual_rows(decisions)

    assert rows[0]["route18_id"] == "R18-001"
    assert rows[0]["manual_review_id"] == "R9-001"
    assert rows[0]["manual_token_seen"] == ""
    assert rows[0]["manual_new_crop_needed"] == ""
    assert rows[0]["manual_image_insufficient"] == ""
    assert rows[0]["semantic_guardrail"] == "direct_visual_package_not_evidence"


def test_summarize_direct_visual_rows_counts_priority_and_folios():
    rows = [
        {
            "priority_level": "P0",
            "folio": "f67r1",
            "decision_package_status": "ready_for_manual_visual_decision",
            "target_type": "missing_group_tokens",
        },
        {
            "priority_level": "P1",
            "folio": "f70v2",
            "decision_package_status": "ready_for_manual_visual_decision",
            "target_type": "missing_group_tokens",
        },
    ]

    summary = summarize_direct_visual_rows(rows)

    assert summary["priority_level"]["P0"] == 1
    assert summary["folio"]["f70v2"] == 1
    assert summary["decision_package_status"]["ready_for_manual_visual_decision"] == 2


def test_render_html_card_includes_source_image_svg_fields_and_guardrail():
    row = {
        "route19_id": "R19-001",
        "checklist_id": "R13-001",
        "folio": "f67r1",
        "review_target": "otardar",
        "source_image": "images/raw/commons_f67r1_r2.jpg",
        "crop_svg": "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
        "fields_to_fill": "manual_token_seen manual_new_crop_needed manual_image_insufficient manual_notes",
        "semantic_guardrail": "direct_visual_package_not_evidence",
    }

    html = render_html_card(row)

    assert "../images/raw/commons_f67r1_r2.jpg" in html
    assert "../images/derived/review_crops/R7-009_R6-009_f67r1.svg" in html
    assert "manual_token_seen" in html
    assert "direct_visual_package_not_evidence" in html


def test_render_markdown_section_includes_output_rule():
    row = {
        "route19_id": "R19-001",
        "checklist_id": "R13-001",
        "folio": "f67r1",
        "review_target": "otardar",
        "source_image": "images/raw/commons_f67r1_r2.jpg",
        "crop_svg": "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
        "output_rule": "copy_manual_values_back_to_packet_item_checklist",
        "semantic_guardrail": "direct_visual_package_not_evidence",
    }

    text = render_markdown_section(row)

    assert "R19-001" in text
    assert "copy_manual_values_back_to_packet_item_checklist" in text
    assert "direct_visual_package_not_evidence" in text
