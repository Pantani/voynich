from scripts.prepare_ready_visual_line_calibration_tool import (
    GUARDRAIL,
    build_line_calibration_rows,
    display_path,
    merge_opencv_suggestions_into_calibration_rows,
    opencv_suggestion_index,
    parse_baseline_points,
    render_html,
    scan_signature_for_payload,
    summarize_line_calibration_rows,
)


def r42b_row(route42b_id="R42B-001", route32_id="R32-005", folio="f84r"):
    return {
        "route42b_id": route42b_id,
        "route42_id": "R42-005",
        "route42a_id": "R42A-005",
        "route32_id": route32_id,
        "route28_id": "R28-023",
        "folio": folio,
        "priority_level": "P1",
        "locus_kind": "P",
        "token_counts": "okal=1|otar=1",
        "top_loci": f"{folio}.24,+P0|{folio}.29,+P0",
        "manifest_label": "84r",
        "yale_image_id": "1006226",
        "yale_dimensions": "2753x3745",
        "local_image_path": "images/raw/yale_iiif_r32/f84r_1006226.jpg",
        "yale_iiif_jpg_url": "https://collections.library.yale.edu/iiif/2/1006226/full/full/0/default.jpg",
    }


def test_build_line_calibration_rows_splits_target_loci_and_preserves_transcription():
    transcription = {
        "f84r.24,+P0": "pol.tar.shedy,qokedy.okal.shey",
        "f84r.29,+P0": "qokeedy.okeey.dar.olchedy.otar.chedy",
    }

    rows = build_line_calibration_rows([r42b_row()], transcription, [])

    assert [row["route42c_id"] for row in rows] == ["R42C-001", "R42C-002"]
    assert [row["target_locus"] for row in rows] == ["f84r.24,+P0", "f84r.29,+P0"]
    assert rows[0]["line_number"] == "24"
    assert rows[0]["marker"] == "+P0"
    assert rows[0]["highlight_tokens"] == "okal|otar"
    assert rows[0]["transcription_text"] == "pol.tar.shedy,qokedy.okal.shey"
    assert rows[0]["calibration_status"] == "pending_calibration"
    assert rows[0]["baseline_points"] == ""
    assert rows[0]["semantic_guardrail"] == GUARDRAIL


def test_build_line_calibration_rows_preserves_existing_manual_calibration_by_locus():
    existing = [
        {
            "route32_id": "R32-005",
            "target_locus": "f84r.24,+P0",
            "calibration_status": "calibrated",
            "baseline_points": "12.50,31.00 82.25,30.75",
            "baseline_width_pct": "1.20",
            "manual_notes": "linha calibrada acima da faixa verde",
        }
    ]

    rows = build_line_calibration_rows([r42b_row()], {"f84r.24,+P0": "okal"}, existing)

    assert rows[0]["calibration_status"] == "calibrated"
    assert rows[0]["baseline_points"] == "12.50,31.00 82.25,30.75"
    assert rows[0]["baseline_width_pct"] == "1.20"
    assert rows[0]["manual_notes"] == "linha calibrada acima da faixa verde"
    assert rows[1]["calibration_status"] == "pending_calibration"


def test_build_line_calibration_rows_rejects_calibrated_status_without_valid_baseline():
    existing = [
        {
            "route32_id": "R32-005",
            "target_locus": "f84r.24,+P0",
            "calibration_status": "calibrated",
            "baseline_points": "",
            "baseline_width_pct": "1.20",
            "manual_notes": "marcada calibrada sem pontos por engano",
        },
        {
            "route32_id": "R32-005",
            "target_locus": "f84r.29,+P0",
            "calibration_status": "calibrated",
            "baseline_points": "12.50,31.00",
            "baseline_width_pct": "1.20",
            "manual_notes": "apenas um ponto",
        },
    ]

    rows = build_line_calibration_rows([r42b_row()], {"f84r.24,+P0": "okal"}, existing)

    assert rows[0]["calibration_status"] == "pending_calibration"
    assert rows[0]["baseline_points"] == ""
    assert rows[0]["manual_notes"] == "marcada calibrada sem pontos por engano"
    assert rows[1]["calibration_status"] == "pending_calibration"
    assert rows[1]["baseline_points"] == ""
    assert rows[1]["manual_notes"] == "apenas um ponto"


def test_parse_baseline_points_accepts_percent_pairs_and_rejects_invalid_values():
    assert parse_baseline_points("12.50,31.00 82.25,30.75") == [(12.5, 31.0), (82.25, 30.75)]
    assert parse_baseline_points("") == []
    assert parse_baseline_points("12.5,31") == []
    assert parse_baseline_points("-1,31 82,30") == []
    assert parse_baseline_points("12,31 101,30") == []


def test_display_path_handles_paths_outside_project_root():
    assert display_path("/private/tmp/r42c.csv") == "/private/tmp/r42c.csv"
    assert display_path("data/annotations/ready_visual_line_calibration_zl3b.csv") == (
        "data/annotations/ready_visual_line_calibration_zl3b.csv"
    )


def test_render_html_contains_click_to_mark_baseline_flow_and_csv_draft():
    rows = build_line_calibration_rows(
        [r42b_row()],
        {
            "f84r.24,+P0": "pol.tar.shedy,qokedy.okal.shey",
            "f84r.29,+P0": "qokeedy.okeey.dar.olchedy.otar.chedy",
        },
        [],
    )

    html = render_html(rows, "data/annotations/ready_visual_line_calibration_zl3b.csv")

    assert "Rota 42C" in html
    assert "Calibrar linha" in html
    assert "Clique no comeco e no fim da linha real" in html
    assert "eva-visual-line" in html
    assert 'data-eva-word=\\"okal\\"' in html
    assert "baselineSvg" in html
    assert "generateCsv" in html
    assert "copyCsv" in html
    assert "downloadCsv" in html
    assert "Lupa da linha" in html
    assert "linePreviewCanvas" in html
    assert "paintCropPreviews" in html
    assert "cropBoxFromPoints" in html
    assert "Abrir R42B" in html
    assert "calibratedRequiresBaseline" in html
    assert "Precisa de dois pontos para marcar como calibrada" in html
    assert "rota_42b_pacote_html_preenchimento_humano_r32.html" in html
    assert "ready_visual_line_calibration_zl3b.csv" in html
    assert "manual_annotation_status" not in html
    assert GUARDRAIL in html


def test_render_html_binds_scan_overlay_to_image_and_can_reset_stale_local_scan():
    rows = build_line_calibration_rows(
        [r42b_row()],
        {"f84r.24,+P0": "pol.tar.shedy,qokedy.okal.shey"},
        [],
    )

    html = render_html(rows, "data/annotations/ready_visual_line_calibration_zl3b.csv")

    assert ".image-stage { position: relative; display: inline-grid;" in html
    assert ".image-stage img { grid-area: 1 / 1;" in html
    assert ".baseline-svg { grid-area: 1 / 1;" in html
    assert "min-width: 560px" not in html
    assert "Resetar scan local" in html
    assert "resetLocalScan" in html


def test_render_html_keeps_zoomed_image_top_scrollable():
    rows = build_line_calibration_rows(
        [r42b_row()],
        {"f84r.24,+P0": "pol.tar.shedy,qokedy.okal.shey"},
        [],
    )

    html = render_html(rows, "data/annotations/ready_visual_line_calibration_zl3b.csv")

    assert 'id="imagePanel"' in html
    assert "Topo da imagem" in html
    assert "scrollImagePanelToTop" in html
    assert "overflow-y: auto" in html
    assert ".app { display: grid; grid-template-rows: auto auto minmax(0, 1fr); min-height: 100vh;" in html
    assert "scroll-padding: 72px" in html
    assert "overscroll-behavior: auto" in html
    assert ".app { display: grid; grid-template-rows: auto auto minmax(0, 1fr); height: 100vh;" not in html
    assert "overscroll-behavior: contain" not in html
    assert ".image-stage { position: relative; display: inline-grid;" in html


def test_render_html_has_fine_tuning_controls_for_existing_baseline_points():
    rows = build_line_calibration_rows(
        [r42b_row()],
        {"f84r.24,+P0": "pol.tar.shedy,qokedy.okal.shey"},
        [],
    )

    html = render_html(rows, "data/annotations/ready_visual_line_calibration_zl3b.csv")

    assert "Ajuste fino" in html
    assert "fineStep" in html
    assert "nudgeBaseline" in html
    assert "nudgeFineTarget" in html
    assert "Linha inteira" in html
    assert "Ponto esquerdo" in html
    assert "Ponto direito" in html
    assert "Clique nos dois pontos antes de ajustar" in html
    assert "baseline_points" in html
    assert "fine_tune" not in html


def test_render_html_has_child_simple_tracking_and_step_guidance():
    rows = build_line_calibration_rows(
        [r42b_row()],
        {"f84r.24,+P0": "pol.tar.shedy,qokedy.okal.shey"},
        [],
    )

    html = render_html(rows, "data/annotations/ready_visual_line_calibration_zl3b.csv")

    assert "Guia rapido" in html
    assert "stepGuideTitle" in html
    assert "stepGuideText" in html
    assert "progressText" in html
    assert "mousePositionText" in html
    assert "lastClickText" in html
    assert "tracking-crosshair" in html
    assert "updateMouseTracking" in html
    assert "updateStepGuide" in html
    assert "Mira fora da imagem" in html
    assert "Agora clique no comeco da linha" in html
    assert "Agora clique no fim da linha" in html


def test_scan_signature_is_stable_and_changes_when_suggestion_changes():
    payload = {
        "route32_id": "R32-005",
        "target_locus": "f84r.24,+P0",
        "local_image_path": "images/raw/yale_iiif_r32/f84r_1006226.jpg",
        "yale_image_id": "1006226",
        "opencv_suggestion_visual_line_number": "6",
        "opencv_suggestion_baseline_points": "17.00,34.46 80.07,34.46",
        "baseline_points": "17.00,34.46 80.07,34.46",
    }

    first = scan_signature_for_payload(payload)
    second = scan_signature_for_payload(dict(payload))
    changed = scan_signature_for_payload({**payload, "opencv_suggestion_visual_line_number": "7"})

    assert first == second
    assert first != changed
    assert len(first) == 16


def test_render_html_uses_scan_signature_to_reject_stale_local_drafts():
    rows = build_line_calibration_rows(
        [r42b_row()],
        {"f84r.24,+P0": "pol.tar.shedy,qokedy.okal.shey"},
        [],
    )
    suggestions = opencv_suggestion_index(
        [
            {
                "route32_id": "R32-005",
                "target_locus": "f84r.24,+P0",
                "suggestion_status": "opencv_suggested_needs_human_confirmation",
                "suggested_baseline_points": "20.00,32.50 70.00,32.50",
                "suggested_visual_line_number": "4",
                "suggestion_confidence": "0.54",
            }
        ]
    )

    html = render_html(rows, "data/annotations/ready_visual_line_calibration_zl3b.csv", suggestions)

    assert '"scan_signature":' in html
    assert "__scan_signature" in html
    assert "expectedSignature" in html
    assert "isManualUserState" in html
    assert "freshStateFor(item)" in html


def test_render_html_shows_opencv_suggestion_without_marking_calibrated():
    rows = build_line_calibration_rows(
        [r42b_row()],
        {"f84r.24,+P0": "pol.tar.shedy,qokedy.okal.shey"},
        [],
    )
    suggestions = opencv_suggestion_index(
        [
            {
                "route32_id": "R32-005",
                "target_locus": "f84r.24,+P0",
                "suggestion_status": "opencv_suggested_needs_human_confirmation",
                "suggested_baseline_points": "20.00,32.50 70.00,32.50",
                "suggested_visual_line_number": "4",
                "suggestion_confidence": "0.54",
                "opencv_auto_action": "prefill_pending_baseline",
                "human_next_step": "conferir se a linha acompanha o texto e marcar calibrada se estiver certa",
                "automation_confidence_band": "media",
            }
        ]
    )

    html = render_html(rows, "data/annotations/ready_visual_line_calibration_zl3b.csv", suggestions)

    assert "Sugestao OpenCV" in html
    assert "Computador ja ajudou" in html
    assert "Ele colocou uma linha em rascunho" in html
    assert "opencvAutoActionText" in html
    assert "opencvHumanStepText" in html
    assert "Recolocar sugestao" in html
    assert "useOpenCvSuggestion" in html
    assert "baseline-suggestion" in html
    assert "baseline-draft" in html
    assert "Pontos em rascunho" in html
    assert "linha visual OpenCV" in html
    assert '"opencv_suggestion_visual_line_number": "4"' in html
    assert '"opencv_auto_action": "prefill_pending_baseline"' in html
    assert '"opencv_human_next_step": "conferir se a linha acompanha o texto e marcar calibrada se estiver certa"' in html
    assert '"opencv_confidence_band": "media"' in html
    assert "Abrir mapa OpenCV" in html
    assert "Abrir sugestoes OpenCV" in html
    assert "Abrir escolha de linhas" in html
    assert "rota_42f_escolha_linhas_visuais_sem_zona_r32.html" in html
    assert "Texto de referencia visual" in html
    assert "20.00,32.50 70.00,32.50" in html
    assert "A sugestao nao marca calibrada sozinha" in html


def test_merge_opencv_suggestions_prefills_missing_points_but_keeps_pending_status():
    rows = build_line_calibration_rows(
        [r42b_row()],
        {"f84r.24,+P0": "pol.tar.shedy,qokedy.okal.shey"},
        [],
    )
    suggestions = opencv_suggestion_index(
        [
            {
                "route32_id": "R32-005",
                "target_locus": "f84r.24,+P0",
                "suggestion_status": "opencv_suggested_needs_human_confirmation",
                "suggested_baseline_points": "20.00,32.50 70.00,32.50",
                "suggestion_confidence": "0.54",
            }
        ]
    )

    merged = merge_opencv_suggestions_into_calibration_rows(rows, suggestions)

    assert merged[0]["baseline_points"] == "20.00,32.50 70.00,32.50"
    assert merged[0]["calibration_status"] == "pending_calibration"
    assert merged[0]["baseline_width_pct"] == "1.20"
    assert "Sugestao OpenCV inicial" in merged[0]["manual_notes"]
    assert "Acao OpenCV: prefill_pending_baseline" in merged[0]["manual_notes"]
    assert merged[1]["baseline_points"] == ""


def test_merge_opencv_suggestions_does_not_overwrite_manual_or_calibrated_points():
    rows = build_line_calibration_rows(
        [r42b_row()],
        {"f84r.24,+P0": "pol.tar.shedy,qokedy.okal.shey"},
        [
            {
                "route32_id": "R32-005",
                "target_locus": "f84r.24,+P0",
                "calibration_status": "calibrated",
                "baseline_points": "12.50,31.00 82.25,30.75",
                "baseline_width_pct": "1.20",
                "manual_notes": "baseline manual",
            }
        ],
    )
    suggestions = opencv_suggestion_index(
        [
            {
                "route32_id": "R32-005",
                "target_locus": "f84r.24,+P0",
                "suggestion_status": "opencv_suggested_needs_human_confirmation",
                "suggested_baseline_points": "20.00,32.50 70.00,32.50",
            }
        ]
    )

    merged = merge_opencv_suggestions_into_calibration_rows(rows, suggestions)

    assert merged[0]["baseline_points"] == "12.50,31.00 82.25,30.75"
    assert merged[0]["calibration_status"] == "calibrated"
    assert merged[0]["manual_notes"] == "baseline manual"


def test_merge_opencv_suggestions_refreshes_existing_pending_opencv_draft_points():
    rows = build_line_calibration_rows(
        [r42b_row()],
        {"f84r.24,+P0": "pol.tar.shedy,qokedy.okal.shey"},
        [
            {
                "route32_id": "R32-005",
                "target_locus": "f84r.24,+P0",
                "calibration_status": "pending_calibration",
                "baseline_points": "20.07,32.55 27.07,32.55",
                "baseline_width_pct": "1.20",
                "manual_notes": "Sugestao OpenCV inicial; confirmar visualmente na R42C antes de marcar calibrada. Confianca OpenCV: 0.54.",
            }
        ],
    )
    suggestions = opencv_suggestion_index(
        [
            {
                "route32_id": "R32-005",
                "target_locus": "f84r.24,+P0",
                "suggestion_status": "opencv_suggested_needs_human_confirmation",
                "suggested_baseline_points": "17.00,34.46 80.07,34.46",
                "suggested_visual_line_number": "7",
                "suggestion_confidence": "0.41",
            }
        ]
    )

    merged = merge_opencv_suggestions_into_calibration_rows(rows, suggestions)

    assert merged[0]["baseline_points"] == "17.00,34.46 80.07,34.46"
    assert merged[0]["calibration_status"] == "pending_calibration"
    assert "Linha visual OpenCV: 7" in merged[0]["manual_notes"]
    assert "Confianca OpenCV: 0.41" in merged[0]["manual_notes"]
    assert merged[0]["manual_notes"].count("Sugestao OpenCV inicial") == 1


def test_summarize_line_calibration_rows_counts_status_and_folio():
    rows = build_line_calibration_rows([r42b_row()], {"f84r.24,+P0": "okal"}, [])
    rows[0]["baseline_points"] = "20.00,32.50 70.00,32.50"
    summary = summarize_line_calibration_rows(rows)

    assert summary["folio"]["f84r"] == 2
    assert summary["calibration_status"]["pending_calibration"] == 2
    assert summary["baseline_points"]["with_baseline_points"] == 1
    assert summary["baseline_points"]["missing_baseline_points"] == 1
    assert summary["semantic_guardrail"][GUARDRAIL] == 2
