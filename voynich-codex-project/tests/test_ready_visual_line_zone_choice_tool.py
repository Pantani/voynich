from scripts.prepare_ready_visual_line_zone_choice_tool import (
    GUARDRAIL,
    build_zone_choice_rows,
    render_html,
    selected_zone_from_line_map,
)


def calibration_row(target_locus="f99v.12,+P0", route42c_id="R42C-005"):
    return {
        "route42c_id": route42c_id,
        "route42b_id": "R42B-003",
        "route32_id": "R32-001",
        "folio": "f99v",
        "target_locus": target_locus,
        "line_number": target_locus.split(".", 1)[1].split(",", 1)[0],
        "transcription_text": "qokeo.qokeol.chockhy.otol.daiin",
        "local_image_path": "images/raw/yale_iiif_r32/f99v_1006247.jpg",
        "calibration_status": "pending_calibration",
        "baseline_points": "",
    }


def suggestion_row(target_locus="f99v.12,+P0"):
    return {
        "route42c_id": "R42C-005",
        "route42b_id": "R42B-003",
        "route32_id": "R32-001",
        "folio": "f99v",
        "target_locus": target_locus,
        "line_number": target_locus.split(".", 1)[1].split(",", 1)[0],
        "local_image_path": "images/raw/yale_iiif_r32/f99v_1006247.jpg",
        "suggestion_status": "opencv_candidates_detected_needs_manual_zone",
        "candidate_count": "2",
        "opencv_auto_action": "needs_manual_zone",
    }


def line_map_row(number="5", band_box_pct="12.00,30.00,76.00,31.40"):
    return {
        "local_image_path": "images/raw/yale_iiif_r32/f99v_1006247.jpg",
        "visual_line_number": number,
        "band_box_pct": band_box_pct,
        "baseline_points": "12.00,31.40 76.00,31.40",
        "confidence": "0.72",
    }


def test_selected_zone_from_line_map_expands_visual_line_box_safely():
    zone = selected_zone_from_line_map(line_map_row())

    assert zone == "10.50,28.80,77.50,32.60"


def test_build_zone_choice_rows_lists_only_targets_that_need_manual_zone_and_preserves_selection():
    rows = build_zone_choice_rows(
        [calibration_row(), calibration_row("f99v.21,@P0", "R42C-007")],
        [suggestion_row(), {**suggestion_row("f99v.21,@P0"), "opencv_auto_action": "prefill_pending_baseline"}],
        [line_map_row("5"), line_map_row("6", "12.00,33.00,76.00,34.40")],
        [
            {
                "route32_id": "R32-001",
                "target_locus": "f99v.12,+P0",
                "zone_status": "zone_selected_pending_opencv",
                "selected_visual_line_number": "5",
                "manual_zone_notes": "parece a linha correta",
            }
        ],
    )

    assert len(rows) == 1
    assert rows[0]["target_locus"] == "f99v.12,+P0"
    assert rows[0]["candidate_visual_lines"] == "5|6"
    assert rows[0]["candidate_visual_line_zones"] == (
        "5=10.50,28.80,77.50,32.60|6=10.50,31.80,77.50,35.60"
    )
    assert rows[0]["selected_visual_line_number"] == "5"
    assert rows[0]["selected_zone_box_pct"] == "10.50,28.80,77.50,32.60"
    assert rows[0]["zone_status"] == "zone_selected_pending_opencv"
    assert rows[0]["semantic_guardrail"] == GUARDRAIL


def test_render_html_is_child_simple_and_does_not_claim_evidence():
    rows = build_zone_choice_rows(
        [calibration_row()],
        [suggestion_row()],
        [line_map_row("5")],
        [],
    )

    html = render_html(rows, "data/annotations/ready_visual_line_zone_choice_zl3b.csv")

    assert "Rota 42F" in html
    assert "Escolha a linha que combina" in html
    assert "Essa e a linha" in html
    assert "selected_visual_line_number" in html
    assert "candidate_visual_line_zones" in html
    assert "transcription_visual_html" in html
    assert "eva-visual-line" in html
    assert "line-crop-card" in html
    assert "data-crop-preview" in html
    assert "paintCropPreviews" in html
    assert "Clique no recorte que bate" in html
    assert "lineZoneMap" in html
    assert "line-zone-choice" in html
    assert "Abrir R42C" in html
    assert "Abrir R42D" in html
    assert "Abrir R42E" in html
    assert "nao preenche a R32" in html
    assert GUARDRAIL in html
