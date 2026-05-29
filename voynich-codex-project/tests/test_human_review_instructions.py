from scripts.prepare_human_review_instructions import (
    build_instruction_items,
    build_instruction_packets,
    fields_to_fill,
    instruction_mode,
    render_packet_section,
    summarize_instructions,
)


def test_instruction_mode_follows_packet_goal():
    assert instruction_mode({"packet_goal": "review_source_image_first"}) == "open_source_image_before_svg"
    assert instruction_mode({"packet_goal": "search_tokens_then_redraw_crop"}) == "search_tokens_then_redraw_crop"
    assert instruction_mode({"packet_goal": "tighten_current_svg_regions"}) == "tighten_current_svg_regions"


def test_fields_to_fill_lists_manual_checklist_columns():
    fields = fields_to_fill()

    assert "manual_token_seen" in fields
    assert "manual_new_crop_needed" in fields
    assert "manual_image_insufficient" in fields
    assert "manual_notes" in fields


def test_build_instruction_packets_merges_packet_counts_with_checklist_items():
    packets = [
        {
            "packet_id": "R12-001",
            "folio": "f67r1",
            "source_image": "images/raw/commons_f67r1_r2.jpg",
            "item_count": "2",
            "missing_token_count": "1",
            "packet_goal": "review_source_image_first",
        }
    ]
    checklist = [
        {
            "checklist_id": "R13-001",
            "packet_id": "R12-001",
            "review_target": "otardar",
            "target_type": "missing_group_tokens",
            "crop_svg": "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
            "priority_bucket": "P0_operator_missing_tokens",
        },
        {
            "checklist_id": "R13-002",
            "packet_id": "R12-001",
            "review_target": "ar ol",
            "target_type": "matched_group_tokens",
            "crop_svg": "images/derived/review_crops/R7-002_R6-002_f67r1.svg",
            "priority_bucket": "P3_tighten_existing_region",
        },
    ]

    output = build_instruction_packets(packets, checklist)

    assert output[0]["instruction_id"] == "R15-001"
    assert output[0]["packet_id"] == "R12-001"
    assert output[0]["checklist_ids"] == "R13-001 R13-002"
    assert output[0]["instruction_mode"] == "open_source_image_before_svg"
    assert output[0]["semantic_guardrail"] == "human_instruction_not_visual_evidence"


def test_build_instruction_items_preserves_item_traceability():
    checklist = [
        {
            "checklist_id": "R13-001",
            "packet_id": "R12-001",
            "route11_id": "R11-002",
            "manual_review_id": "R9-001",
            "crop_id": "R7-009",
            "folio": "f67r1",
            "locus": "f67r1.5,@Cc",
            "source_image": "images/raw/commons_f67r1_r2.jpg",
            "crop_svg": "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
            "review_target": "otardar",
            "target_type": "missing_group_tokens",
            "priority_bucket": "P0_operator_missing_tokens",
        }
    ]

    items = build_instruction_items(checklist)

    assert items[0]["instruction_item_id"] == "R15I-001"
    assert items[0]["checklist_id"] == "R13-001"
    assert items[0]["manual_review_id"] == "R9-001"
    assert items[0]["fields_to_fill"] == fields_to_fill()


def test_render_packet_section_includes_image_targets_and_guardrail():
    packet = {
        "instruction_id": "R15-001",
        "packet_id": "R12-001",
        "folio": "f67r1",
        "source_image": "images/raw/commons_f67r1_r2.jpg",
        "instruction_mode": "open_source_image_before_svg",
        "fields_to_fill": fields_to_fill(),
        "semantic_guardrail": "human_instruction_not_visual_evidence",
    }
    items = [
        {
            "packet_id": "R12-001",
            "checklist_id": "R13-001",
            "review_target": "otardar",
            "target_type": "missing_group_tokens",
            "crop_svg": "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
            "priority_bucket": "P0_operator_missing_tokens",
        }
    ]

    text = render_packet_section(packet, items)

    assert "images/raw/commons_f67r1_r2.jpg" in text
    assert "otardar" in text
    assert "manual_token_seen" in text
    assert "human_instruction_not_visual_evidence" in text


def test_summarize_instructions_counts_packet_modes():
    rows = [
        {"instruction_mode": "open_source_image_before_svg", "folio": "f67r1"},
        {"instruction_mode": "search_tokens_then_redraw_crop", "folio": "f84r"},
    ]

    summary = summarize_instructions(rows)

    assert summary["instruction_mode"]["open_source_image_before_svg"] == 1
    assert summary["folio"]["f84r"] == 1
