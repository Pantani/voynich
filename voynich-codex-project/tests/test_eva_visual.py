from scripts.eva_visual import render_eva_text, render_eva_word_svg, tokenize_eva_text


def test_tokenize_eva_text_splits_commas_and_dots_without_showing_raw_line():
    assert tokenize_eva_text("okar,y.qokedy") == ["okar", "y", "qokedy"]


def test_render_eva_word_svg_draws_word_as_image():
    html = render_eva_word_svg("okar")

    assert '<svg class="eva-word"' in html
    assert 'data-eva-word="okar"' in html
    assert "<path" in html
    assert ">okar<" not in html


def test_render_eva_text_uses_visual_cards_for_reference_lines():
    html = render_eva_text("okar,y.qokedy", highlight_tokens="okar|y")

    assert 'class="eva-visual-line"' in html
    assert 'data-eva-word="okar"' in html
    assert 'data-eva-word="y"' in html
    assert 'data-eva-word="qokedy"' in html
    assert "is-target" in html
    assert "okar,y" not in html
