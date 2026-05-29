from scripts.prepare_guided_visual_entry_html import (
    build_guided_rows,
    html_image_path,
    render_html_card,
    render_markdown_section,
    summarize_guided_rows,
)


def base_entry(**overrides):
    row = {
        "route21_id": "R21-001",
        "route20_id": "R20-001",
        "route19_id": "R19-001",
        "route18_id": "R18-001",
        "route17_id": "R17-001",
        "checklist_id": "R13-001",
        "manual_review_id": "R9-001",
        "crop_id": "R7-009",
        "folio": "f67r1",
        "source_image": "images/raw/commons_f67r1_r2.jpg",
        "crop_svg": "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
        "review_region": "x=31 y=158 w=768 h=913",
        "priority_level": "P0",
        "target_type": "missing_group_tokens",
        "review_target": "otardar",
        "allowed_manual_token_seen": "yes/no/uncertain",
        "allowed_manual_new_crop_needed": "yes/no",
        "allowed_manual_image_insufficient": "yes/no",
    }
    row.update(overrides)
    return row


def base_log(**overrides):
    row = {
        "route22_id": "R22-001",
        "route21_id": "R21-001",
        "route19_id": "R19-001",
        "validation_status": "pending_blank_manual_entry",
        "apply_status": "skipped_blank_manual_entry",
    }
    row.update(overrides)
    return row


def test_html_image_path_is_relative_from_docs_directory():
    assert html_image_path("images/raw/commons_f67r1_r2.jpg") == "../images/raw/commons_f67r1_r2.jpg"
    assert html_image_path("") == ""


def test_build_guided_rows_filters_pending_blank_entries_only():
    entries = [
        base_entry(route21_id="R21-001", route19_id="R19-001"),
        base_entry(route21_id="R21-002", route19_id="R19-002"),
    ]
    validation_log = [
        base_log(route22_id="R22-001", route21_id="R21-001", route19_id="R19-001"),
        base_log(
            route22_id="R22-002",
            route21_id="R21-002",
            route19_id="R19-002",
            validation_status="valid_manual_entry",
        ),
    ]

    rows = build_guided_rows(entries, validation_log)

    assert len(rows) == 1
    assert rows[0]["route23_id"] == "R23-001"
    assert rows[0]["route22_id"] == "R22-001"
    assert rows[0]["route21_id"] == "R21-001"
    assert rows[0]["html_card_status"] == "ready_for_guided_manual_entry"


def test_build_guided_rows_preserves_traceability_allowed_values_and_guardrail():
    rows = build_guided_rows([base_entry()], [base_log()])

    assert rows[0]["manual_review_id"] == "R9-001"
    assert rows[0]["crop_id"] == "R7-009"
    assert rows[0]["allowed_manual_token_seen"] == "yes/no/uncertain"
    assert rows[0]["allowed_manual_new_crop_needed"] == "yes/no"
    assert rows[0]["csv_target_field_list"] == "manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes"
    assert rows[0]["output_rule"] == "fill_r21_csv_manually_then_rerun_route_22"
    assert rows[0]["semantic_guardrail"] == "guided_html_not_visual_evidence"


def test_summarize_guided_rows_counts_status_priority_folio_and_target_type():
    rows = [
        {
            "html_card_status": "ready_for_guided_manual_entry",
            "validation_status": "pending_blank_manual_entry",
            "priority_level": "P0",
            "folio": "f67r1",
            "target_type": "missing_group_tokens",
        },
        {
            "html_card_status": "ready_for_guided_manual_entry",
            "validation_status": "pending_blank_manual_entry",
            "priority_level": "P1",
            "folio": "f70v2",
            "target_type": "missing_group_tokens",
        },
    ]

    summary = summarize_guided_rows(rows)

    assert summary["html_card_status"]["ready_for_guided_manual_entry"] == 2
    assert summary["validation_status"]["pending_blank_manual_entry"] == 2
    assert summary["priority_level"]["P0"] == 1
    assert summary["folio"]["f70v2"] == 1
    assert summary["target_type"]["missing_group_tokens"] == 2


def test_render_html_card_includes_images_allowed_values_and_csv_target():
    row = build_guided_rows([base_entry()], [base_log()])[0]

    html = render_html_card(row)

    assert "../images/raw/commons_f67r1_r2.jpg" in html
    assert "../images/derived/review_crops/R7-009_R6-009_f67r1.svg" in html
    assert "yes/no/uncertain" in html
    assert "manual_token_seen" in html
    assert "R21-001" in html
    assert "guided_html_not_visual_evidence" in html


def test_render_markdown_section_includes_output_rule_and_guardrail():
    row = build_guided_rows([base_entry()], [base_log()])[0]

    text = render_markdown_section(row)

    assert "R23-001" in text
    assert "fill_r21_csv_manually_then_rerun_route_22" in text
    assert "guided_html_not_visual_evidence" in text
