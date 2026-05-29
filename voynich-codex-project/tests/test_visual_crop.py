from scripts.visual_crop import (
    VISUAL_CROP_JS,
    baseline_box_from_points,
    box_text,
    parse_box_pct,
    render_crop_canvas,
)


def test_parse_box_pct_accepts_valid_percent_box_only():
    assert parse_box_pct("10.50,20.00,70.25,24.50") == (10.5, 20.0, 70.25, 24.5)
    assert parse_box_pct("70,20,10,24") is None
    assert parse_box_pct("10,20,70") is None
    assert parse_box_pct("bad") is None


def test_baseline_box_from_points_expands_line_into_readable_crop():
    box = baseline_box_from_points("12.50,31.00 82.25,30.75", vertical_pad=3.0, horizontal_pad=2.0)

    assert box == (10.5, 27.875, 84.25, 33.875)
    assert box_text(box) == "10.50,27.88,84.25,33.88"


def test_render_crop_canvas_is_real_image_placeholder_for_browser_painting():
    html = render_crop_canvas(
        "../images/raw/yale_iiif_r32/f84r_1006226.jpg",
        (10.5, 27.875, 84.25, 33.875),
        "linha 24 em recorte real",
        note="compare aqui primeiro",
        class_name="focus-crop",
    )

    assert "data-crop-preview" in html
    assert 'data-image-src="../images/raw/yale_iiif_r32/f84r_1006226.jpg"' in html
    assert 'data-box-pct="10.50,27.88,84.25,33.88"' in html
    assert "linha 24 em recorte real" in html
    assert "compare aqui primeiro" in html
    assert "paintCropPreviews" in VISUAL_CROP_JS
