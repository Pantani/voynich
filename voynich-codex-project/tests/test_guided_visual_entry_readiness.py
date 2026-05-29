from scripts.verify_guided_visual_entry_readiness import (
    build_readiness_rows,
    has_manual_values,
    readiness_status,
    render_readiness_section,
    summarize_readiness_rows,
)


MANUAL_FIELDS = {
    "manual_token_seen": "",
    "manual_new_crop_needed": "",
    "manual_image_insufficient": "",
    "manual_new_crop_x": "",
    "manual_new_crop_y": "",
    "manual_new_crop_width": "",
    "manual_new_crop_height": "",
    "manual_notes": "",
}


def manifest_row(**overrides):
    row = {
        "route23_id": "R23-001",
        "route22_id": "R22-001",
        "route21_id": "R21-001",
        "route19_id": "R19-001",
        "checklist_id": "R13-001",
        "manual_review_id": "R9-001",
        "crop_id": "R7-009",
        "folio": "f67r1",
        "source_image": "images/raw/commons_f67r1_r2.jpg",
        "crop_svg": "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
        "priority_level": "P0",
        "target_type": "missing_group_tokens",
        "review_target": "otardar",
        "allowed_manual_token_seen": "yes/no/uncertain",
        "allowed_manual_new_crop_needed": "yes/no",
        "allowed_manual_image_insufficient": "yes/no",
        "html_card_status": "ready_for_guided_manual_entry",
    }
    row.update(overrides)
    return row


def entry_row(**overrides):
    row = {
        "route21_id": "R21-001",
        **MANUAL_FIELDS,
    }
    row.update(overrides)
    return row


def test_has_manual_values_detects_blank_and_filled_entry_rows():
    assert has_manual_values(entry_row()) is False
    assert has_manual_values(entry_row(manual_token_seen="yes")) is True
    assert has_manual_values(entry_row(manual_notes="ambiguous")) is True


def test_readiness_status_requires_assets_html_and_blank_manual_entry():
    ready = {
        "source_image_status": "present",
        "crop_svg_status": "present",
        "html_card_check": "present",
        "allowed_values_check": "present",
        "manual_entry_status": "blank_manual_entry",
    }

    assert readiness_status(ready) == "ready_for_manual_fill"
    assert readiness_status({**ready, "source_image_status": "missing"}) == "blocked_missing_asset"
    assert readiness_status({**ready, "html_card_check": "missing"}) == "blocked_missing_html_card"
    assert readiness_status({**ready, "manual_entry_status": "has_manual_entry"}) == "manual_entry_already_present"


def test_build_readiness_rows_checks_assets_html_and_traceability():
    html_text = "R23-001 R21-001 R19-001 yes/no/uncertain guided_html_not_visual_evidence"
    existing_paths = {
        "images/raw/commons_f67r1_r2.jpg",
        "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
    }

    rows = build_readiness_rows([manifest_row()], [entry_row()], html_text, existing_paths=existing_paths)

    assert rows[0]["route24_id"] == "R24-001"
    assert rows[0]["route23_id"] == "R23-001"
    assert rows[0]["source_image_status"] == "present"
    assert rows[0]["crop_svg_status"] == "present"
    assert rows[0]["html_card_check"] == "present"
    assert rows[0]["allowed_values_check"] == "present"
    assert rows[0]["manual_entry_status"] == "blank_manual_entry"
    assert rows[0]["readiness_status"] == "ready_for_manual_fill"


def test_build_readiness_rows_marks_manual_entries_without_overwriting():
    html_text = "R23-001 R21-001 R19-001 yes/no/uncertain guided_html_not_visual_evidence"
    existing_paths = {
        "images/raw/commons_f67r1_r2.jpg",
        "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
    }

    rows = build_readiness_rows(
        [manifest_row()],
        [entry_row(manual_token_seen="uncertain")],
        html_text,
        existing_paths=existing_paths,
    )

    assert rows[0]["manual_entry_status"] == "has_manual_entry"
    assert rows[0]["readiness_status"] == "manual_entry_already_present"
    assert rows[0]["next_action"] == "rerun_route_22_to_validate_manual_entries"


def test_summarize_readiness_rows_counts_readiness_assets_priority_and_folio():
    rows = [
        {
            "readiness_status": "ready_for_manual_fill",
            "source_image_status": "present",
            "crop_svg_status": "present",
            "html_card_check": "present",
            "manual_entry_status": "blank_manual_entry",
            "priority_level": "P0",
            "folio": "f67r1",
            "target_type": "missing_group_tokens",
        },
        {
            "readiness_status": "blocked_missing_asset",
            "source_image_status": "missing",
            "crop_svg_status": "present",
            "html_card_check": "present",
            "manual_entry_status": "blank_manual_entry",
            "priority_level": "P1",
            "folio": "f70v2",
            "target_type": "missing_group_tokens",
        },
    ]

    summary = summarize_readiness_rows(rows)

    assert summary["readiness_status"]["ready_for_manual_fill"] == 1
    assert summary["source_image_status"]["missing"] == 1
    assert summary["manual_entry_status"]["blank_manual_entry"] == 2
    assert summary["priority_level"]["P0"] == 1
    assert summary["folio"]["f70v2"] == 1


def test_render_readiness_section_includes_next_action_and_guardrail():
    row = {
        "route24_id": "R24-001",
        "route23_id": "R23-001",
        "route21_id": "R21-001",
        "readiness_status": "ready_for_manual_fill",
        "next_action": "fill_r21_csv_manually_using_guided_html_then_rerun_route_22",
        "semantic_guardrail": "readiness_check_not_visual_evidence",
    }

    text = render_readiness_section(row)

    assert "R24-001" in text
    assert "ready_for_manual_fill" in text
    assert "fill_r21_csv_manually_using_guided_html_then_rerun_route_22" in text
    assert "readiness_check_not_visual_evidence" in text
