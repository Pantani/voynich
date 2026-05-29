"""Small SVG renderer for EVA-like Voynich reference tokens."""

from __future__ import annotations

import html
import re


EVA_GLYPHS = {
    "a": {"w": 24, "paths": ["M6 27 C6 19 16 18 18 25 C21 34 8 38 6 30", "M18 23 C18 29 19 33 22 36"]},
    "c": {"w": 22, "paths": ["M18 18 C11 14 5 19 5 27 C5 35 13 38 19 32"]},
    "d": {"w": 27, "paths": ["M9 8 C14 16 14 26 10 36", "M10 24 C17 18 23 21 23 28 C23 35 15 38 9 34"]},
    "e": {"w": 21, "paths": ["M17 20 C11 15 5 20 5 27 C5 34 12 38 19 32", "M7 26 L18 26"]},
    "f": {"w": 28, "paths": ["M15 7 C9 12 9 23 12 36", "M8 15 L24 15", "M10 25 L21 25"]},
    "g": {"w": 28, "paths": ["M20 22 C17 16 8 17 6 25 C4 33 12 38 19 33", "M19 26 C23 34 21 41 13 42"]},
    "h": {"w": 29, "paths": ["M8 8 C12 17 12 27 9 37", "M11 25 C16 18 24 21 24 36"]},
    "i": {"w": 13, "paths": ["M7 18 C9 24 9 31 6 37", "M8 11 L8 11"]},
    "k": {"w": 30, "paths": ["M10 7 L10 37", "M10 9 C17 6 25 9 25 17 C25 23 18 24 12 21", "M12 22 C18 27 22 32 25 37"]},
    "l": {"w": 22, "paths": ["M12 7 C6 14 7 25 10 33 C12 38 17 37 18 31"]},
    "m": {"w": 34, "paths": ["M6 36 C8 26 8 21 6 17", "M9 25 C13 18 18 19 18 36", "M19 25 C24 18 29 20 29 36"]},
    "n": {"w": 26, "paths": ["M6 36 C8 26 8 21 6 17", "M9 25 C14 18 21 20 21 36"]},
    "o": {"w": 24, "paths": ["M12 15 C18 15 21 19 21 25 C21 32 16 36 10 34 C4 32 3 25 6 20 C8 17 10 15 12 15Z"]},
    "p": {"w": 28, "paths": ["M9 15 C11 25 10 35 7 42", "M10 21 C18 15 25 20 24 28 C23 36 14 37 9 32"]},
    "q": {"w": 30, "paths": ["M13 15 C20 15 24 20 23 27 C22 35 13 37 8 32 C3 27 5 18 13 15Z", "M20 31 C24 35 27 37 30 38"]},
    "r": {"w": 22, "paths": ["M6 31 C9 20 17 16 19 23 C21 30 12 30 12 36"]},
    "s": {"w": 23, "paths": ["M18 19 C13 15 7 17 7 23 C7 28 18 27 18 33 C18 38 9 39 5 34"]},
    "t": {"w": 30, "paths": ["M10 7 L10 37", "M10 9 L25 9", "M25 9 C25 17 23 23 17 25"]},
    "y": {"w": 26, "paths": ["M6 20 C9 29 12 35 17 34", "M20 18 C17 27 14 35 9 42"]},
}

EVA_VISUAL_CSS = """
    .eva-visual-line { display: flex; flex-wrap: wrap; gap: 6px; align-items: center; min-width: 0; }
    .eva-visual-card { display: grid; gap: 3px; min-width: 74px; max-width: 172px; padding: 7px; border: 1px solid var(--line, #d7cabb); border-radius: 8px; background: #f7f3eb; }
    .eva-visual-card.compact { min-width: 58px; padding: 5px; }
    .eva-visual-card.is-target { border-color: #d6a645; background: #fff5cf; box-shadow: inset 0 0 0 1px rgba(214, 166, 69, 0.25); }
    .eva-word { display: block; width: 100%; height: 48px; }
    .eva-visual-card.compact .eva-word { height: 38px; }
    .eva-word path { fill: none; stroke: #3a261b; stroke-width: 3.2; stroke-linecap: round; stroke-linejoin: round; }
    .eva-fallback { fill: #3a261b; font: 28px Georgia, serif; }
    .eva-visual-count { width: fit-content; min-height: 20px; padding: 1px 7px; border: 1px solid var(--line, #d7cabb); border-radius: 999px; color: var(--muted, #6f675f); font-size: 11px; }
    .eva-visual-empty { color: var(--muted, #6f675f); font-size: 13px; }
"""


def tokenize_eva_text(value: str) -> list[str]:
    return re.findall(r"[A-Za-z]+", value)


def highlight_token_set(value: str) -> set[str]:
    tokens: set[str] = set()
    for raw in re.split(r"[|\s,.;]+", value):
        token = raw.split("=", 1)[0].strip().lower()
        if token:
            tokens.add(token)
    return tokens


def render_eva_word_svg(token: str) -> str:
    x = 2
    parts: list[str] = []
    for letter in token.lower():
        glyph = EVA_GLYPHS.get(letter)
        if glyph is None:
            parts.append(
                f'<text x="{x}" y="32" class="eva-fallback">{html.escape(letter)}</text>'
            )
            x += 18
            continue
        for path in glyph["paths"]:
            parts.append(f'<path d="{path}" transform="translate({x} 0)"></path>')
        x += int(glyph["w"])
    width = max(56, x + 4)
    escaped = html.escape(token)
    return (
        f'<svg class="eva-word" data-eva-word="{escaped}" '
        f'viewBox="0 0 {width} 46" role="img" aria-label="Guia visual EVA {escaped}">'
        + "".join(parts)
        + "</svg>"
    )


def render_eva_word_card(
    token: str,
    *,
    count_label: str = "",
    is_target: bool = False,
    compact: bool = False,
) -> str:
    classes = ["eva-visual-card"]
    if is_target:
        classes.append("is-target")
    if compact:
        classes.append("compact")
    count_html = f'<span class="eva-visual-count">{html.escape(count_label)}</span>' if count_label else ""
    return (
        f'<span class="{" ".join(classes)}">'
        f"{render_eva_word_svg(token)}"
        f"{count_html}"
        "</span>"
    )


def render_eva_text(
    value: str,
    *,
    highlight_tokens: str = "",
    compact: bool = True,
    empty_label: str = "sem transcricao",
) -> str:
    tokens = tokenize_eva_text(value)
    if not tokens:
        return f'<span class="eva-visual-empty">{html.escape(empty_label)}</span>'
    targets = highlight_token_set(highlight_tokens)
    cards = [
        render_eva_word_card(
            token,
            is_target=token.lower() in targets,
            compact=compact,
        )
        for token in tokens
    ]
    return '<div class="eva-visual-line" aria-label="Texto EVA renderizado como imagem">' + "".join(cards) + "</div>"
