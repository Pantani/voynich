from scripts.prepare_priority_human_review import (
    build_priority_review_rows,
    priority_level,
    render_review_section,
    review_focus,
    summarize_priority_review,
)


def test_priority_level_reads_prefix_before_underscore():
    assert priority_level({"priority_bucket": "P0_operator_missing_tokens"}) == "P0"
    assert priority_level({"priority_bucket": "P1_core_missing_tokens"}) == "P1"
    assert priority_level({"priority_bucket": ""}) == "unranked"


def test_review_focus_maps_priority_buckets_to_operational_focus():
    assert review_focus({"priority_bucket": "P0_operator_missing_tokens"}) == "operator_missing_tokens_first"
    assert review_focus({"priority_bucket": "P1_core_missing_tokens"}) == "core_missing_tokens_second"
    assert review_focus({"priority_bucket": "P3_tighten_existing_region"}) == "defer_to_later_batch"


def test_build_priority_review_rows_filters_pending_p0_p1_only():
    evidence_rows = [
        {
            "route16_id": "R16-001",
            "instruction_item_id": "R15I-001",
            "checklist_id": "R13-001",
            "packet_id": "R12-001",
            "priority_bucket": "P0_operator_missing_tokens",
            "human_review_state": "pending_human_review",
        },
        {
            "route16_id": "R16-002",
            "instruction_item_id": "R15I-002",
            "checklist_id": "R13-002",
            "packet_id": "R12-001",
            "priority_bucket": "P1_core_missing_tokens",
            "human_review_state": "pending_human_review",
        },
        {
            "route16_id": "R16-003",
            "instruction_item_id": "R15I-003",
            "checklist_id": "R13-003",
            "packet_id": "R12-001",
            "priority_bucket": "P2_other_missing_tokens",
            "human_review_state": "pending_human_review",
        },
        {
            "route16_id": "R16-004",
            "instruction_item_id": "R15I-004",
            "checklist_id": "R13-004",
            "packet_id": "R12-001",
            "priority_bucket": "P0_operator_missing_tokens",
            "human_review_state": "human_confirmed_new_crop_candidate",
        },
    ]

    rows = build_priority_review_rows(evidence_rows)

    assert [row["route17_id"] for row in rows] == ["R17-001", "R17-002"]
    assert [row["checklist_id"] for row in rows] == ["R13-001", "R13-002"]
    assert all(row["review_batch"] == "P0_P1_pending_human_review" for row in rows)


def test_build_priority_review_rows_preserves_traceability_and_manual_fields():
    evidence_rows = [
        {
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
            "target_type": "missing_group_tokens",
            "review_target": "otardar",
            "human_review_state": "pending_human_review",
        }
    ]

    rows = build_priority_review_rows(evidence_rows)

    assert rows[0]["route17_id"] == "R17-001"
    assert rows[0]["route16_id"] == "R16-001"
    assert rows[0]["manual_review_id"] == "R9-001"
    assert rows[0]["crop_id"] == "R7-009"
    assert "manual_token_seen" in rows[0]["fields_to_fill"]
    assert rows[0]["semantic_guardrail"] == "priority_review_not_visual_evidence"


def test_summarize_priority_review_counts_batch_dimensions():
    rows = [
        {
            "priority_level": "P0",
            "packet_id": "R12-001",
            "folio": "f67r1",
            "target_type": "missing_group_tokens",
            "review_focus": "operator_missing_tokens_first",
        },
        {
            "priority_level": "P1",
            "packet_id": "R12-001",
            "folio": "f67r1",
            "target_type": "missing_group_tokens",
            "review_focus": "core_missing_tokens_second",
        },
    ]

    summary = summarize_priority_review(rows)

    assert summary["priority_level"]["P0"] == 1
    assert summary["packet_id"]["R12-001"] == 2
    assert summary["target_type"]["missing_group_tokens"] == 2


def test_render_review_section_includes_image_svg_fields_and_guardrail():
    row = {
        "route17_id": "R17-001",
        "checklist_id": "R13-001",
        "folio": "f67r1",
        "source_image": "images/raw/commons_f67r1_r2.jpg",
        "crop_svg": "images/derived/review_crops/R7-009_R6-009_f67r1.svg",
        "review_target": "otardar",
        "fields_to_fill": "manual_token_seen manual_new_crop_needed manual_image_insufficient manual_notes",
        "semantic_guardrail": "priority_review_not_visual_evidence",
    }

    text = render_review_section(row)

    assert "images/raw/commons_f67r1_r2.jpg" in text
    assert "R7-009_R6-009_f67r1.svg" in text
    assert "manual_token_seen" in text
    assert "priority_review_not_visual_evidence" in text
