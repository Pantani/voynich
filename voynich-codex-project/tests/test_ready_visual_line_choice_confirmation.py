from scripts.prepare_ready_visual_line_choice_confirmation import (
    GUARDRAIL,
    build_confirmation_rows,
    candidate_options,
    render_html,
)


def queue_row(**overrides):
    row = {
        "route42k_id": "R42K-001",
        "route42f_id": "R42F-001",
        "route42b_id": "R42B-001",
        "route32_id": "R32-001",
        "folio": "f67r2",
        "target_locus": "f67r2.35,@Pb",
        "transcription_text": "chol.okol",
        "review_bucket": "revisar_primeiro",
        "review_priority_score": "71",
        "best_visual_line_number": "2",
        "best_line_zone_box_pct": "67.90,9.71,83.97,14.33",
        "candidate_visual_lines": "1|2|3",
        "top_fragment_crop_boxes": "77.34,8.46,82.60,14.98|71.97,8.46,76.48,14.82",
        "local_image_path": "images/raw/yale_iiif_r32/f67r2_1006194.jpg",
    }
    row.update(overrides)
    return row


def zone_row(**overrides):
    row = {
        "route42f_id": "R42F-001",
        "candidate_visual_line_zones": (
            "1=18.90,1.02,51.43,4.48|"
            "2=67.90,9.71,83.97,14.33|"
            "3=59.63,73.87,86.90,77.77"
        ),
    }
    row.update(overrides)
    return row


def test_candidate_options_marks_suggested_line_and_keeps_alternatives():
    options = candidate_options(queue_row(), zone_row())

    assert [option["line_number"] for option in options] == ["1", "2", "3"]
    assert options[1]["is_suggested"] is True
    assert options[1]["box_pct"] == "67.90,9.71,83.97,14.33"

    confirmation_style_options = candidate_options(
        {"candidate_visual_lines": "1|2|3", "suggested_visual_line_number": "2"},
        zone_row(),
    )
    assert confirmation_style_options[1]["is_suggested"] is True


def test_build_confirmation_rows_preserves_suggestion_without_selecting_it():
    rows = build_confirmation_rows([queue_row()], [zone_row()])

    assert rows[0]["route42l_id"] == "R42L-001"
    assert rows[0]["route42k_id"] == "R42K-001"
    assert rows[0]["suggested_visual_line_number"] == "2"
    assert rows[0]["suggested_zone_box_pct"] == "67.90,9.71,83.97,14.33"
    assert rows[0]["selected_visual_line_number"] == ""
    assert rows[0]["selected_zone_box_pct"] == ""
    assert rows[0]["confirmation_status"] == "pending_human_confirmation"
    assert rows[0]["semantic_guardrail"] == GUARDRAIL


def test_render_html_is_a_confirmation_tool_not_auto_apply():
    rows = build_confirmation_rows([queue_row()], [zone_row()])
    html = render_html(rows, "data/annotations/ready_visual_line_choice_confirmation_zl3b.csv")

    assert "Rota 42L" in html
    assert "Confirmar linha sugerida" in html
    assert "Usar linha sugerida" in html
    assert "Nao aplicar automaticamente" in html
    assert "data-crop-preview" in html
    assert "Baixar CSV" in html
    assert "Abrir R42M" in html
    assert "Abrir R42F" in html
    assert "R42F-001" in html
    assert GUARDRAIL in html
