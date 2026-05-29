from scripts.prepare_ready_visual_line_opencv_suggestions import (
    GUARDRAIL,
    build_suggestion_rows,
    choose_band_for_zone,
    merge_bands_into_visual_lines,
    render_html,
    read_csv,
    zone_choices_to_visual_zones,
    write_summary_csv,
)


def calibration_row(target_locus="f84r.24,+P0"):
    return {
        "route42c_id": "R42C-001",
        "route42b_id": "R42B-001",
        "route32_id": "R32-005",
        "folio": "f84r",
        "target_locus": target_locus,
        "line_number": "24",
        "local_image_path": "images/raw/yale_iiif_r32/f84r_1006226.jpg",
        "calibration_status": "pending_calibration",
        "baseline_points": "",
    }


def test_choose_band_for_zone_prefers_band_inside_manual_zone():
    zone = {"top": 27.0, "left": 8.0, "width": 80.0, "height": 11.0}
    bands = [
        {"x1": 5.0, "y1": 12.0, "x2": 35.0, "y2": 13.5, "confidence": 0.30},
        {"x1": 12.0, "y1": 30.0, "x2": 76.0, "y2": 31.4, "confidence": 0.72},
    ]

    chosen = choose_band_for_zone(bands, zone)

    assert chosen == bands[1]


def test_merge_bands_into_visual_lines_groups_fragments_on_the_same_text_row():
    bands = [
        {"x1": 10.0, "y1": 20.0, "x2": 25.0, "y2": 21.0, "confidence": 0.60},
        {"x1": 30.0, "y1": 20.4, "x2": 46.0, "y2": 21.4, "confidence": 0.70},
        {"x1": 12.0, "y1": 25.0, "x2": 40.0, "y2": 26.2, "confidence": 0.50},
    ]

    lines = merge_bands_into_visual_lines(bands, y_tolerance_pct=1.2)

    assert len(lines) == 2
    assert lines[0]["visual_line_number"] == "1"
    assert lines[0]["x1"] == 10.0
    assert lines[0]["x2"] == 46.0
    assert round(lines[0]["confidence"], 2) == 0.65
    assert lines[1]["visual_line_number"] == "2"


def test_merge_bands_into_visual_lines_ignores_isolated_margin_noise_on_same_row():
    bands = [
        {"x1": 12.0, "y1": 30.0, "x2": 28.0, "y2": 31.0, "confidence": 0.60},
        {"x1": 32.0, "y1": 30.2, "x2": 60.0, "y2": 31.2, "confidence": 0.70},
        {"x1": 92.0, "y1": 30.1, "x2": 99.0, "y2": 31.1, "confidence": 0.40},
    ]

    lines = merge_bands_into_visual_lines(bands, y_tolerance_pct=1.2)

    assert len(lines) == 1
    assert lines[0]["x1"] == 12.0
    assert lines[0]["x2"] == 60.0
    assert round(lines[0]["confidence"], 2) == 0.65


def test_merge_bands_into_visual_lines_rejects_full_width_page_border_noise():
    bands = [
        {"x1": 1.0, "y1": 2.0, "x2": 99.0, "y2": 3.0, "confidence": 0.80},
        {"x1": 12.0, "y1": 25.0, "x2": 70.0, "y2": 26.2, "confidence": 0.60},
    ]

    lines = merge_bands_into_visual_lines(bands, y_tolerance_pct=1.2)

    assert len(lines) == 1
    assert lines[0]["visual_line_number"] == "1"
    assert lines[0]["y1"] == 25.0


def test_build_suggestion_rows_never_marks_opencv_suggestion_as_calibrated():
    rows = build_suggestion_rows(
        [calibration_row()],
        {
            "images/raw/yale_iiif_r32/f84r_1006226.jpg": [
                {"x1": 12.0, "y1": 30.0, "x2": 76.0, "y2": 31.4, "confidence": 0.72, "visual_line_number": "6"}
            ]
        },
        {"f84r.24,+P0": {"top": 27.0, "left": 8.0, "width": 80.0, "height": 11.0}},
        cv2_available=True,
    )

    assert rows[0]["suggestion_status"] == "opencv_suggested_needs_human_confirmation"
    assert rows[0]["suggested_visual_line_number"] == "6"
    assert rows[0]["suggested_baseline_points"] == "12.00,31.40 76.00,31.40"
    assert rows[0]["calibration_status_to_apply"] == "pending_calibration"
    assert rows[0]["semantic_guardrail"] == GUARDRAIL


def test_build_suggestion_rows_labels_what_opencv_can_do_without_human_help():
    rows = build_suggestion_rows(
        [calibration_row()],
        {
            "images/raw/yale_iiif_r32/f84r_1006226.jpg": [
                {"x1": 12.0, "y1": 30.0, "x2": 76.0, "y2": 31.4, "confidence": 0.72, "visual_line_number": "6"}
            ]
        },
        {"f84r.24,+P0": {"top": 27.0, "left": 8.0, "width": 80.0, "height": 11.0}},
        cv2_available=True,
    )

    assert rows[0]["opencv_auto_action"] == "prefill_pending_baseline"
    assert rows[0]["human_next_step"] == "conferir se a linha acompanha o texto e marcar calibrada se estiver certa"
    assert rows[0]["automation_confidence_band"] == "alta"
    assert "OpenCV pode pre-preencher a baseline como rascunho" in rows[0]["algorithm_notes"]


def test_build_suggestion_rows_labels_manual_zone_when_opencv_has_lines_but_no_mapping():
    rows = build_suggestion_rows(
        [calibration_row("f1r.24,+P0")],
        {
            "images/raw/yale_iiif_r32/f84r_1006226.jpg": [
                {"x1": 12.0, "y1": 30.0, "x2": 76.0, "y2": 31.4, "confidence": 0.72}
            ]
        },
        {},
        cv2_available=True,
    )

    assert rows[0]["opencv_auto_action"] == "needs_manual_zone"
    assert rows[0]["human_next_step"] == "desenhar uma zona simples para o alvo antes de pedir baseline"
    assert rows[0]["automation_confidence_band"] == "sem_mapeamento"


def test_build_suggestion_rows_without_zone_keeps_human_mapping_required():
    rows = build_suggestion_rows(
        [calibration_row("f1r.24,+P0")],
        {
            "images/raw/yale_iiif_r32/f84r_1006226.jpg": [
                {"x1": 12.0, "y1": 30.0, "x2": 76.0, "y2": 31.4, "confidence": 0.72}
            ]
        },
        {},
        cv2_available=True,
    )

    assert rows[0]["suggestion_status"] == "opencv_candidates_detected_needs_manual_zone"
    assert rows[0]["suggested_baseline_points"] == ""
    assert rows[0]["calibration_status_to_apply"] == "pending_calibration"


def test_zone_choices_to_visual_zones_turns_selected_line_into_small_zone():
    zones = zone_choices_to_visual_zones(
        [
            {
                "target_locus": "f99v.12,+P0",
                "selected_visual_line_number": "5",
                "selected_zone_box_pct": "10.50,28.80,77.50,32.60",
                "zone_status": "zone_selected_pending_opencv",
            }
        ]
    )

    assert zones["f99v.12,+P0"] == {
        "top": 28.8,
        "left": 10.5,
        "width": 67.0,
        "height": 3.8,
        "label": "linha visual OpenCV 5 escolhida na R42F",
    }


def test_build_suggestion_rows_uses_zone_choice_to_create_pending_baseline():
    zones = zone_choices_to_visual_zones(
        [
            {
                "target_locus": "f1r.24,+P0",
                "selected_visual_line_number": "3",
                "selected_zone_box_pct": "10.50,28.80,77.50,32.60",
                "zone_status": "zone_selected_pending_opencv",
            }
        ]
    )

    rows = build_suggestion_rows(
        [calibration_row("f1r.24,+P0")],
        {
            "images/raw/yale_iiif_r32/f84r_1006226.jpg": [
                {"x1": 12.0, "y1": 30.0, "x2": 76.0, "y2": 31.4, "confidence": 0.72, "visual_line_number": "3"}
            ]
        },
        zones,
        cv2_available=True,
    )

    assert rows[0]["suggestion_status"] == "opencv_suggested_needs_human_confirmation"
    assert rows[0]["suggested_baseline_points"] == "12.00,31.40 76.00,31.40"
    assert rows[0]["opencv_auto_action"] == "prefill_pending_baseline"
    assert "zona escolhida na R42F" in rows[0]["algorithm_notes"]


def test_render_html_explains_suggestions_are_not_evidence():
    rows = build_suggestion_rows(
        [calibration_row()],
        {
            "images/raw/yale_iiif_r32/f84r_1006226.jpg": [
                {"x1": 12.0, "y1": 30.0, "x2": 76.0, "y2": 31.4, "confidence": 0.72}
            ]
        },
        {"f84r.24,+P0": {"top": 27.0, "left": 8.0, "width": 80.0, "height": 11.0}},
        cv2_available=True,
    )

    html = render_html(rows, "data/derived/ready_visual_line_opencv_suggestions_zl3b.csv")

    assert "Rota 42D" in html
    assert "OpenCV" in html
    assert "nao e palavra encontrada" in html
    assert "nao preenche a R32" in html
    assert "opencv_suggested_needs_human_confirmation" in html
    assert "Recorte real" in html
    assert "data-crop-preview" in html
    assert "paintCropPreviews" in html
    assert "O que o OpenCV resolveu sozinho" in html
    assert "prefill_pending_baseline" in html
    assert "conferir se a linha acompanha o texto" in html
    assert "Abrir R42B" in html
    assert "Abrir R42C" in html
    assert "Abrir R42E" in html
    assert GUARDRAIL in html


def test_write_summary_csv_counts_opencv_auto_actions(tmp_path):
    path = tmp_path / "summary.csv"
    write_summary_csv(
        path,
        [
            {
                "suggestion_status": "opencv_suggested_needs_human_confirmation",
                "folio": "f84r",
                "opencv_auto_action": "prefill_pending_baseline",
                "automation_confidence_band": "media",
                "semantic_guardrail": GUARDRAIL,
            },
            {
                "suggestion_status": "opencv_candidates_detected_needs_manual_zone",
                "folio": "f99v",
                "opencv_auto_action": "needs_manual_zone",
                "automation_confidence_band": "sem_mapeamento",
                "semantic_guardrail": GUARDRAIL,
            },
        ],
    )

    rows = read_csv(path)

    assert {"metric": "opencv_auto_action", "item": "prefill_pending_baseline", "n": "1"} in rows
    assert {"metric": "opencv_auto_action", "item": "needs_manual_zone", "n": "1"} in rows
    assert {"metric": "automation_confidence_band", "item": "media", "n": "1"} in rows
