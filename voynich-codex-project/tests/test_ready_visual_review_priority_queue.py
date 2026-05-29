from scripts.prepare_ready_visual_review_priority_queue import (
    GUARDRAIL,
    build_priority_rows,
    parse_candidate_zones,
    render_html,
    score_zone_choice,
)


def zone_row(**overrides):
    row = {
        "route42f_id": "R42F-001",
        "route42b_id": "R42B-010",
        "route32_id": "R32-001",
        "folio": "f99v",
        "target_locus": "f99v.12,+P0",
        "transcription_text": "okal.okor",
        "local_image_path": "images/raw/yale_iiif_r32/f99v_1006247.jpg",
        "candidate_count": "2",
        "candidate_visual_lines": "3|4",
        "candidate_visual_line_zones": "3=10.00,20.00,30.00,21.00|4=10.00,24.00,34.00,25.00",
        "zone_status": "pending_zone_choice",
    }
    row.update(overrides)
    return row


def fragment_row(line_number="3", confidence="0.80", route42j_id="R42J-001"):
    return {
        "route42j_id": route42j_id,
        "folio_labels": "f99v",
        "local_image_path": "images/raw/yale_iiif_r32/f99v_1006247.jpg",
        "visual_line_number": line_number,
        "visual_word_number": "1",
        "crop_box_pct": "9.00,19.00,31.00,22.00",
        "confidence": confidence,
    }


def context_row(**overrides):
    row = {
        "route42b_id": "R42B-010",
        "priority_level": "P0",
        "image_quality_assist": "high",
        "target_region_locatable_assist": "partial",
        "visual_context_assist": "paragraph_text_visible",
    }
    row.update(overrides)
    return row


def test_parse_candidate_zones_keeps_line_to_box_mapping():
    assert parse_candidate_zones("3=10.00,20.00,30.00,21.00|4=1,2,3,4") == {
        "3": "10.00,20.00,30.00,21.00",
        "4": "1,2,3,4",
    }


def test_score_zone_choice_prioritizes_fewer_candidates_and_real_fragments():
    score, bucket = score_zone_choice(
        candidate_count=2,
        fragment_candidate_count=3,
        best_line_avg_confidence=0.82,
        priority_level="P0",
        image_quality_assist="high",
    )

    assert score >= 80
    assert bucket == "revisar_primeiro"


def test_build_priority_rows_ranks_pending_zone_choices_by_review_value():
    rows = build_priority_rows(
        zone_rows=[
            zone_row(route42f_id="R42F-hard", candidate_count="15", candidate_visual_lines="1|2|3"),
            zone_row(route42f_id="R42F-easy", candidate_count="2", candidate_visual_lines="3|4"),
        ],
        fragment_rows=[
            fragment_row(line_number="3", confidence="0.80", route42j_id="R42J-001"),
            fragment_row(line_number="3", confidence="0.90", route42j_id="R42J-002"),
            fragment_row(line_number="4", confidence="0.60", route42j_id="R42J-003"),
        ],
        context_rows=[context_row()],
    )

    assert [row["route42k_id"] for row in rows] == ["R42K-001", "R42K-002"]
    assert rows[0]["route42f_id"] == "R42F-easy"
    assert rows[0]["review_bucket"] == "revisar_primeiro"
    assert rows[0]["best_visual_line_number"] == "3"
    assert rows[0]["fragment_candidate_count"] == "3"
    assert rows[0]["top_fragment_ids"] == "R42J-002|R42J-001"
    assert rows[0]["semantic_guardrail"] == GUARDRAIL


def test_render_html_exposes_priority_queue_as_visual_review_not_evidence():
    rows = build_priority_rows(
        zone_rows=[zone_row()],
        fragment_rows=[fragment_row()],
        context_rows=[context_row()],
    )

    html = render_html(rows, "data/derived/ready_visual_review_priority_queue_zl3b.csv")

    assert "Rota 42K" in html
    assert "Fila priorizada" in html
    assert "Nao e OCR" in html
    assert "data-crop-preview" in html
    assert "R42F-001" in html
    assert "Abrir R42F" in html
    assert "Abrir R42J" in html
    assert GUARDRAIL in html
