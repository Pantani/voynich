from scripts.prepare_ready_visual_word_opencv_map import (
    GUARDRAIL,
    _fill_short_false_runs,
    _group_projection_runs,
    build_visual_word_rows,
    expand_box,
    merge_components_into_word_clusters,
    render_html,
)


def line_row(number="7", route42e_id="R42E-010"):
    return {
        "route42e_id": route42e_id,
        "image_id": "R42EIMG-001",
        "folio_labels": "f84r",
        "local_image_path": "images/raw/yale_iiif_r32/f84r_1006226.jpg",
        "visual_line_number": number,
        "band_box_pct": "12.00,30.00,76.00,31.40",
        "confidence": "0.72",
        "target_loci_on_image": "f84r.24,+P0|f84r.29,+P0",
    }


def test_expand_box_adds_small_padding_without_leaving_percent_bounds():
    assert expand_box((12.0, 30.0, 76.0, 31.4), x_pad=1.0, y_pad=1.2) == (
        11.0,
        28.8,
        77.0,
        32.6,
    )
    assert expand_box((0.2, 0.4, 99.5, 99.9), x_pad=2.0, y_pad=2.0) == (0.0, 0.0, 100.0, 100.0)


def test_merge_components_into_word_clusters_merges_near_strokes_and_splits_wide_gaps():
    clusters = merge_components_into_word_clusters(
        [
            {"x1": 12.0, "y1": 30.0, "x2": 13.0, "y2": 31.0, "confidence": 0.55},
            {"x1": 13.4, "y1": 30.1, "x2": 15.0, "y2": 31.1, "confidence": 0.65},
            {"x1": 20.0, "y1": 30.0, "x2": 22.0, "y2": 31.2, "confidence": 0.75},
        ],
        max_gap_pct=1.0,
    )

    assert len(clusters) == 2
    assert clusters[0]["x1"] == 12.0
    assert clusters[0]["x2"] == 15.0
    assert round(clusters[0]["confidence"], 2) == 0.60
    assert clusters[1]["x1"] == 20.0


def test_projection_helpers_fill_glyph_gaps_then_split_word_sized_gaps():
    assert _fill_short_false_runs([True, False, False, True, False, False, False, True], max_gap=2) == [
        True,
        True,
        True,
        True,
        False,
        False,
        False,
        True,
    ]

    groups = _group_projection_runs(
        [(2, 5), (7, 10), (26, 30), (31, 34), (60, 61)],
        word_gap_px=4,
        min_run_width_px=2,
    )

    assert groups == [(2, 10), (26, 34)]


def test_build_visual_word_rows_numbers_fragments_inside_each_visual_line():
    rows = build_visual_word_rows(
        [line_row()],
        {
            "R42E-010": [
                {"x1": 12.0, "y1": 30.0, "x2": 15.0, "y2": 31.1, "confidence": 0.60},
                {"x1": 20.0, "y1": 30.1, "x2": 22.0, "y2": 31.2, "confidence": 0.75},
            ]
        },
        cv2_available=True,
    )

    assert [row["route42j_id"] for row in rows] == ["R42J-001", "R42J-002"]
    assert [row["visual_word_number"] for row in rows] == ["1", "2"]
    assert rows[0]["route42e_id"] == "R42E-010"
    assert rows[0]["word_box_pct"] == "12.00,30.00,15.00,31.10"
    assert rows[0]["crop_box_pct"] == "11.00,28.80,16.00,32.30"
    assert rows[0]["word_map_status"] == "opencv_visual_fragment_detected"
    assert rows[0]["semantic_guardrail"] == GUARDRAIL


def test_render_html_shows_fine_cv_fragments_as_real_crops_not_ocr():
    rows = build_visual_word_rows(
        [line_row()],
        {
            "R42E-010": [
                {"x1": 12.0, "y1": 30.0, "x2": 15.0, "y2": 31.1, "confidence": 0.60},
            ]
        },
        cv2_available=True,
    )

    html = render_html(rows, "data/derived/ready_visual_word_opencv_map_zl3b.csv")

    assert "Rota 42J" in html
    assert "fragmentos visuais" in html
    assert "nao e OCR" in html
    assert "data-crop-preview" in html
    assert "visual fragmento 1" in html
    assert "paintCropPreviews" in html
    assert "Abrir R42E" in html
    assert "Ferramentas ativas" in html
    assert GUARDRAIL in html
