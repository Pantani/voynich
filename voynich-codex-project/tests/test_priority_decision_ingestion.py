from scripts.ingest_priority_human_decisions import (
    build_priority_decision_rows,
    decision_bucket,
    missing_checklist_decision,
    render_decision_section,
    summarize_priority_decisions,
)


def test_decision_bucket_maps_pending_and_ready_states():
    assert decision_bucket({"human_review_state": "pending_human_review"}) == "pending_manual_decision"
    assert decision_bucket({"human_review_state": "human_confirmed_new_crop_candidate"}) == "new_crop_candidate"
    assert decision_bucket({"human_review_state": "human_token_not_seen"}) == "token_not_seen"
    assert decision_bucket({"human_review_state": "image_insufficient"}) == "image_insufficient"


def test_missing_checklist_decision_requires_restoring_source_row():
    decision = missing_checklist_decision()

    assert decision["human_review_state"] == "missing_checklist_row"
    assert decision["decision_bucket"] == "missing_source_data"
    assert decision["next_action"] == "restore checklist row before ingesting priority decision"


def test_build_priority_decision_rows_preserves_route17_and_manual_traceability():
    priority_rows = [
        {
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
        }
    ]
    checklist_rows = [
        {
            "checklist_id": "R13-001",
            "manual_token_seen": "",
            "manual_new_crop_needed": "",
            "manual_image_insufficient": "",
            "manual_new_crop_x": "",
            "manual_new_crop_y": "",
            "manual_new_crop_width": "",
            "manual_new_crop_height": "",
            "manual_notes": "",
        }
    ]

    rows = build_priority_decision_rows(priority_rows, checklist_rows)

    assert rows[0]["route18_id"] == "R18-001"
    assert rows[0]["route17_id"] == "R17-001"
    assert rows[0]["checklist_id"] == "R13-001"
    assert rows[0]["manual_review_id"] == "R9-001"
    assert rows[0]["human_review_state"] == "pending_human_review"
    assert rows[0]["decision_bucket"] == "pending_manual_decision"
    assert rows[0]["semantic_guardrail"] == "priority_decision_not_axis_meaning"


def test_seen_token_with_complete_crop_is_ready_for_candidate_crop_generation():
    priority_rows = [
        {
            "route17_id": "R17-001",
            "checklist_id": "R13-001",
            "packet_id": "R12-001",
            "priority_level": "P0",
            "target_type": "missing_group_tokens",
            "review_target": "otardar",
        }
    ]
    checklist_rows = [
        {
            "checklist_id": "R13-001",
            "manual_token_seen": "yes",
            "manual_new_crop_needed": "yes",
            "manual_image_insufficient": "no",
            "manual_new_crop_x": "10",
            "manual_new_crop_y": "20",
            "manual_new_crop_width": "30",
            "manual_new_crop_height": "40",
            "manual_notes": "visible after zoom",
        }
    ]

    rows = build_priority_decision_rows(priority_rows, checklist_rows)

    assert rows[0]["human_review_state"] == "human_confirmed_new_crop_candidate"
    assert rows[0]["decision_bucket"] == "new_crop_candidate"
    assert rows[0]["crop_generation_action"] == "generate_new_crop_candidate"
    assert rows[0]["axis_test_readiness"] == "ready_after_new_crop_review"


def test_missing_checklist_row_is_kept_out_of_evidence():
    priority_rows = [
        {
            "route17_id": "R17-001",
            "checklist_id": "R13-999",
            "packet_id": "R12-001",
            "priority_level": "P0",
            "target_type": "missing_group_tokens",
            "review_target": "missing",
        }
    ]

    rows = build_priority_decision_rows(priority_rows, [])

    assert rows[0]["human_review_state"] == "missing_checklist_row"
    assert rows[0]["decision_bucket"] == "missing_source_data"
    assert rows[0]["axis_test_readiness"] == "not_ready"


def test_summarize_priority_decisions_counts_decision_buckets():
    rows = [
        {
            "decision_bucket": "pending_manual_decision",
            "human_review_state": "pending_human_review",
            "priority_level": "P0",
            "packet_id": "R12-001",
            "folio": "f67r1",
            "crop_generation_action": "no_crop_generation",
            "axis_test_readiness": "not_ready",
        },
        {
            "decision_bucket": "new_crop_candidate",
            "human_review_state": "human_confirmed_new_crop_candidate",
            "priority_level": "P1",
            "packet_id": "R12-002",
            "folio": "f70v2",
            "crop_generation_action": "generate_new_crop_candidate",
            "axis_test_readiness": "ready_after_new_crop_review",
        },
    ]

    summary = summarize_priority_decisions(rows)

    assert summary["decision_bucket"]["pending_manual_decision"] == 1
    assert summary["decision_bucket"]["new_crop_candidate"] == 1
    assert summary["priority_level"]["P0"] == 1


def test_render_decision_section_includes_manual_values_and_guardrail():
    row = {
        "route18_id": "R18-001",
        "route17_id": "R17-001",
        "checklist_id": "R13-001",
        "folio": "f67r1",
        "review_target": "otardar",
        "manual_token_seen": "",
        "manual_new_crop_needed": "",
        "manual_image_insufficient": "",
        "decision_bucket": "pending_manual_decision",
        "next_action": "fill checklist manual fields from visual review",
        "semantic_guardrail": "priority_decision_not_axis_meaning",
    }

    text = render_decision_section(row)

    assert "R18-001" in text
    assert "manual_token_seen" in text
    assert "pending_manual_decision" in text
    assert "priority_decision_not_axis_meaning" in text
