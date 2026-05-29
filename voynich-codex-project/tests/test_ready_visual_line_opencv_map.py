from scripts.prepare_ready_visual_line_opencv_map import (
    GUARDRAIL,
    build_image_inventory,
    build_line_map_rows,
    build_target_zone_rows,
    render_html,
)


def calibration_row(folio="f84r", target_locus="f84r.24,+P0", local_image_path="images/raw/yale_iiif_r32/f84r_1006226.jpg"):
    return {
        "route42c_id": "R42C-001",
        "route42b_id": "R42B-001",
        "route32_id": "R32-005",
        "folio": folio,
        "target_locus": target_locus,
        "line_number": target_locus.split(".", 1)[1].split(",", 1)[0],
        "local_image_path": local_image_path,
    }


def test_build_line_map_rows_numbers_detected_visual_lines_per_image_top_to_bottom():
    rows = build_line_map_rows(
        [calibration_row(), calibration_row(target_locus="f84r.29,+P0")],
        {
            "images/raw/yale_iiif_r32/f84r_1006226.jpg": [
                {"x1": 20.0, "y1": 38.0, "x2": 70.0, "y2": 39.2, "confidence": 0.62},
                {"x1": 12.0, "y1": 30.0, "x2": 76.0, "y2": 31.4, "confidence": 0.72},
            ]
        },
        cv2_available=True,
    )

    assert [row["route42e_id"] for row in rows] == ["R42E-001", "R42E-002"]
    assert [row["visual_line_number"] for row in rows] == ["1", "2"]
    assert rows[0]["baseline_points"] == "12.00,31.40 76.00,31.40"
    assert rows[0]["line_map_status"] == "opencv_visual_line_detected"
    assert rows[0]["semantic_guardrail"] == GUARDRAIL


def test_build_image_inventory_keeps_targets_even_when_no_visual_line_was_detected():
    inventory = build_image_inventory(
        [
            calibration_row(),
            calibration_row(folio="f99r", target_locus="f99r.2,@Lf", local_image_path="images/raw/yale_iiif_r32/f99r_1006246.jpg"),
        ],
        [],
    )

    assert inventory[0]["image_id"] == "R42EIMG-001"
    assert inventory[0]["folio_labels"] == "f84r"
    assert inventory[0]["detected_visual_lines"] == "0"
    assert inventory[0]["target_loci"] == "f84r.24,+P0"
    assert inventory[1]["folio_labels"] == "f99r"


def test_build_target_zone_rows_keeps_known_manual_zones_for_focused_map():
    zones = build_target_zone_rows([calibration_row()])

    assert zones[0]["target_locus"] == "f84r.24,+P0"
    assert zones[0]["local_image_path"] == "images/raw/yale_iiif_r32/f84r_1006226.jpg"
    assert zones[0]["top"] == "27.00"
    assert zones[0]["label"] == "linha 24: bloco de texto superior"


def test_render_html_shows_numbered_line_map_navigation_and_warning():
    line_rows = build_line_map_rows(
        [calibration_row()],
        {
            "images/raw/yale_iiif_r32/f84r_1006226.jpg": [
                {"x1": 12.0, "y1": 30.0, "x2": 76.0, "y2": 31.4, "confidence": 0.72}
            ]
        },
        cv2_available=True,
    )
    inventory = build_image_inventory([calibration_row()], line_rows)

    zones = build_target_zone_rows([calibration_row()])

    html = render_html(inventory, line_rows, "data/derived/ready_visual_line_opencv_map_zl3b.csv", zones)

    assert "Rota 42E" in html
    assert "Mapa OpenCV de linhas visuais" in html
    assert "linha visual 1" in html
    assert "Recortes das linhas" in html
    assert "line-crop-mini" in html
    assert "data-crop-preview" in html
    assert "paintCropPreviews" in html
    assert "OpenCV conta faixas de texto; ele nao confirma palavra" in html
    assert "Abrir R42B" in html
    assert "Abrir R42C" in html
    assert "Abrir R42D" in html
    assert "Mostrar zonas R32" in html
    assert "Mapa bruto" in html
    assert "target-zone" in html
    assert ".image-stage { position: relative; display: inline-grid;" in html
    assert ".image-stage img { grid-area: 1 / 1;" in html
    assert "min-width: 560px" not in html
    assert "data-visual-line-number=\"1\"" in html
    assert GUARDRAIL in html
