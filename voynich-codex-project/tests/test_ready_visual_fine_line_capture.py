from scripts.prepare_ready_visual_fine_line_capture import (
    GUARDRAIL,
    build_fine_capture_rows,
    compute_refined_capture,
    render_html,
)


def confirmation_row(**overrides):
    row = {
        "route42l_id": "R42L-001",
        "route42k_id": "R42K-001",
        "route42f_id": "R42F-008",
        "route42b_id": "R42B-004",
        "route32_id": "R32-003",
        "folio": "f67r2",
        "target_locus": "f67r2.35,@Pb",
        "transcription_text": "chol.[g:d]iin.okol",
        "review_bucket": "revisar_primeiro",
        "review_priority_score": "71",
        "suggested_visual_line_number": "2",
        "suggested_zone_box_pct": "67.90,9.71,83.97,14.33",
        "candidate_visual_lines": "1|2|3",
        "top_fragment_crop_boxes": "77.34,8.46,82.60,14.98|71.97,8.46,76.48,14.82|69.96,8.46,72.82,14.15",
        "local_image_path": "images/raw/yale_iiif_r32/f67r2_1006194.jpg",
    }
    row.update(overrides)
    return row


def test_compute_refined_capture_uses_fragment_union_inside_suggested_zone():
    refined = compute_refined_capture(confirmation_row())

    assert refined["refined_capture_box_pct"] == "69.56,9.71,83.00,14.33"
    assert refined["refined_baseline_points"] == "69.56,13.31 83.00,13.31"
    assert refined["fragment_count"] == "3"
    assert refined["area_reduction_pct"] == "16.37"
    assert refined["fine_capture_status"] == "fine_capture_ready_needs_human_confirmation"
    assert refined["confidence_band"] == "media"
    assert refined["semantic_guardrail"] == GUARDRAIL


def test_build_fine_capture_rows_preserves_route_links_and_never_selects_line():
    rows = build_fine_capture_rows([confirmation_row()])

    assert rows[0]["route42m_id"] == "R42M-001"
    assert rows[0]["route42l_id"] == "R42L-001"
    assert rows[0]["route42f_id"] == "R42F-008"
    assert rows[0]["suggested_visual_line_number"] == "2"
    assert rows[0]["selected_visual_line_number"] == ""
    assert rows[0]["selected_zone_box_pct"] == ""
    assert rows[0]["human_next_step"] == "confirmar visualmente na R42L antes de aplicar na R42F"


def test_compute_refined_capture_falls_back_when_fragments_are_missing():
    refined = compute_refined_capture(confirmation_row(top_fragment_crop_boxes=""))

    assert refined["refined_capture_box_pct"] == "67.90,9.71,83.97,14.33"
    assert refined["fragment_count"] == "0"
    assert refined["area_reduction_pct"] == "0.00"
    assert refined["fine_capture_status"] == "needs_manual_capture_review"
    assert refined["confidence_band"] == "baixa"


def test_render_html_shows_fine_capture_as_visual_aid_not_evidence():
    rows = build_fine_capture_rows([confirmation_row()])
    html = render_html(rows, "data/derived/ready_visual_fine_line_capture_zl3b.csv")

    assert "Rota 42M" in html
    assert "Captura fina" in html
    assert "nao e OCR" in html
    assert "data-crop-preview" in html
    assert "Abrir R42L" in html
    assert "Abrir R42C" in html
    assert "R42M-001" in html
    assert GUARDRAIL in html
