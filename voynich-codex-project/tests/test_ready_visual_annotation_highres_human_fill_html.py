from scripts.prepare_ready_visual_annotation_highres_human_fill_html import (
    GUARDRAIL,
    VISUAL_ZONE_OVERRIDES,
    build_fill_html_rows,
    render_html,
    render_html_card,
    summarize_fill_html_rows,
    validate_visual_zone_overrides,
)


def highres_row(route42_id="R42-005", route32_id="R32-005", folio="f84r"):
    return {
        "route42_id": route42_id,
        "route32_id": route32_id,
        "route28_id": "R28-023",
        "folio": folio,
        "priority_level": "P1",
        "locus_kind": "P",
        "token_counts": "okal=1|otar=1",
        "top_loci": f"{folio}.24,+P0|{folio}.29,+P0",
        "manifest_label": "84r",
        "yale_image_id": "1006226",
        "yale_iiif_jpg_url": "https://collections.library.yale.edu/iiif/2/1006226/full/full/0/default.jpg",
        "yale_tiff_url": "https://collections.library.yale.edu/download/tiff/1006226",
        "yale_catalog_url": "https://collections.library.yale.edu/catalog/2002046?child_oid=1006226",
        "yale_width": "2753",
        "yale_height": "3745",
        "local_image_path": "images/raw/yale_iiif_r32/f84r_1006226.jpg",
        "manual_annotation_status": "",
        "manual_visual_notes": "",
    }


def assist_row(route32_id="R32-005", folio="f84r"):
    return {
        "route32_id": route32_id,
        "folio": folio,
        "image_quality_assist": "high",
        "target_region_locatable_assist": "yes_region",
        "exact_token_decision_assist": "not_determined_requires_human_zoom",
        "visual_context_assist": "nymph_labels_and_body_text_visible",
        "suggested_manual_review_action": "crop_upper_pool_text_lines",
    }


def calibration_row(route32_id="R32-005", target_locus="f84r.24,+P0"):
    return {
        "route32_id": route32_id,
        "target_locus": target_locus,
        "calibration_status": "calibrated",
        "baseline_points": "12.50,31.00 82.25,30.75",
        "baseline_width_pct": "1.20",
        "manual_notes": "baseline calibrada por humano",
    }


def test_build_fill_html_rows_orders_easy_items_first_and_preserves_blank_manual_fields():
    rows = build_fill_html_rows(
        [
            highres_row("R42-002", "R32-002", "f1r"),
            highres_row("R42-008", "R32-008", "f99r"),
            highres_row("R42-005", "R32-005", "f84r"),
        ],
        [
            assist_row("R32-002", "f1r"),
            assist_row("R32-008", "f99r"),
            assist_row("R32-005", "f84r"),
        ],
        "data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv",
    )

    assert [row["folio"] for row in rows] == ["f84r", "f99r", "f1r"]
    assert rows[0]["route42b_id"] == "R42B-001"
    assert rows[0]["route32_id"] == "R32-005"
    assert rows[0]["target_csv"] == "data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv"
    assert rows[0]["manual_annotation_status"] == ""
    assert rows[0]["manual_visual_notes"] == ""
    assert rows[0]["semantic_guardrail"] == GUARDRAIL


def test_render_html_card_has_fields_and_patch_csv_metadata():
    row = build_fill_html_rows([highres_row()], [assist_row()], "target.csv")[0]

    html = render_html_card(row)

    assert 'data-route32-id="R32-005"' in html
    assert 'data-value="annotated"' in html
    assert 'data-value="not_visible"' in html
    assert 'data-value="uncertain"' in html
    assert "Pergunta principal" in html
    assert "Voce achou essas palavrinhas na imagem?" in html
    assert "Achei" in html
    assert "Nao achei" in html
    assert "Nao sei" in html
    assert "Refazer nota automatica" in html
    assert "Nota pronta" in html
    assert 'class="eva-word"' in html
    assert 'data-eva-word="okal"' in html
    assert "codigo EVA" not in html
    assert "linha 24" in html
    assert "Referencia: f84r tem 47 entradas/loci ZL3b" in html
    assert "nao sao 47 linhas visuais contadas na imagem" in html
    assert "Ver as 47 entradas ZL3b" in html
    assert "f84r.1,@Lt" in html
    assert "f84r.47,@Lt" in html
    assert "Texto de referencia" in html
    assert "Olhe este recorte primeiro" in html
    assert "Recortes reais da pagina" in html
    assert "data-crop-preview" in html
    assert "data-box-pct" in html
    assert "paintCropPreviews" not in html
    assert "pol.tar.shedy" not in html
    assert 'data-eva-word="okal"' in html
    assert 'data-eva-word="otar"' in html
    assert "eva-visual-line" in html
    assert "is-target" in html
    assert "texto acima da faixa verde" in html
    assert "texto abaixo da faixa verde" in html
    assert "line-overlay" in html
    assert "target-zone" in html
    assert "linha 24: bloco de texto superior" in html
    assert "linha 29: bloco de texto inferior" in html
    assert "zonas provaveis" in html
    assert "nao calcula posicao visual pela numeracao ZL3b" in html
    assert "Detalhes tecnicos" in html
    assert 'name="manual_annotation_status"' in html
    assert '<textarea name="manual_visual_notes"' in html
    assert "Comece pelas linhas de texto acima da area ilustrada." in html
    assert GUARDRAIL in html


def test_render_html_card_uses_calibrated_baseline_and_keeps_pending_zone_fallback():
    row = build_fill_html_rows(
        [highres_row()],
        [assist_row()],
        "target.csv",
        [calibration_row()],
    )[0]

    html = render_html_card(row)

    assert "target-baseline" in html
    assert 'points="12.50,31.00 82.25,30.75"' in html
    assert "linha 24 calibrada" in html
    assert "linha 24: bloco de texto superior" not in html
    assert "linha 29: bloco de texto inferior" in html
    assert "baselines calibradas" in html


def test_render_html_card_does_not_estimate_visual_position_from_zl3b_line_number():
    row = build_fill_html_rows([highres_row(folio="f1r")], [assist_row(folio="f1r")], "target.csv")[0]

    html = render_html_card(row)

    assert "line-marker" not in html
    assert "posicao visual ainda nao calibrada" in html
    assert "use Calibrar linhas" in html
    assert "data-zone-kind=\"needs-line-calibration\"" in html


def test_render_html_includes_static_csv_generator_and_local_storage():
    rows = build_fill_html_rows([highres_row()], [assist_row()], "target.csv")

    html = render_html(rows, "target.csv")

    assert "voynich.r42b.highres.fill" in html
    assert "generateCsv" in html
    assert "manual_annotation_status,manual_visual_notes" in html
    assert "r32PatchCsv" in html
    assert "reviewQueue" in html
    assert "paintCropPreviews" in html
    assert "zoomSlider" in html
    assert "currentCounter" in html
    assert "showItem" in html
    assert "nextPendingItem" in html
    assert "notesHelperText" in html
    assert "O que voce precisa fazer" in html
    assert "Clique em Achei, Nao achei ou Nao sei" in html
    assert "finishBanner" in html
    assert "defaultNoteForStatus" in html
    assert "Rascunho tecnico, usar so no final" in html
    assert "toggleLineGuide" in html
    assert "Esconder zonas" in html
    assert "Mostrar zonas" in html
    assert "hide-line-guides" in html
    assert "lineGuideUp" in html
    assert "lineGuideDown" in html
    assert "lineGuideReset" in html
    assert "openLineCalibration" in html
    assert "Calibrar linhas" in html
    assert "rota_42c_calibrador_linhas_baseline_r32.html" in html
    assert "openOpenCvMap" in html
    assert "Mapa OpenCV" in html
    assert "rota_42e_mapa_opencv_linhas_visuais_r32.html" in html
    assert "DEFAULT_LINE_GUIDE_SHIFT" in html
    assert "DRAFT_ZONE_VERSION" in html
    assert "lineGuideShiftFor" in html
    assert "lineGuideShift:" not in html
    assert "item.lineGuideShift" not in html


def test_f84r_visual_zone_overrides_stay_inside_text_blocks():
    validate_visual_zone_overrides()

    line24 = VISUAL_ZONE_OVERRIDES["f84r.24,+P0"]
    line29 = VISUAL_ZONE_OVERRIDES["f84r.29,+P0"]

    assert line24["top"] + line24["height"] <= 39.0
    assert line29["top"] >= 56.0


def test_summarize_fill_html_rows_counts_review_rank_and_guardrail():
    rows = build_fill_html_rows(
        [highres_row("R42-005", "R32-005", "f84r"), highres_row("R42-006", "R32-006", "f88v")],
        [assist_row("R32-005", "f84r"), assist_row("R32-006", "f88v")],
        "target.csv",
    )

    summary = summarize_fill_html_rows(rows)

    assert summary["folio"]["f84r"] == 1
    assert summary["folio"]["f88v"] == 1
    assert summary["review_group"]["first_clear_regions"] == 1
    assert summary["review_group"]["last_composite_pages"] == 1
    assert summary["semantic_guardrail"][GUARDRAIL] == 2
