#!/usr/bin/env python3
"""Prepare a high-resolution HTML form for human route 32 entries."""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
from collections import Counter
from pathlib import Path

try:
    from scripts.eva_visual import EVA_VISUAL_CSS, render_eva_text, render_eva_word_card
    from scripts.visual_crop import (
        VISUAL_CROP_CSS,
        VISUAL_CROP_JS,
        baseline_box_from_points,
        box_from_zone,
        render_crop_canvas,
    )
except ImportError:  # pragma: no cover - used when running this file directly from scripts/
    from eva_visual import EVA_VISUAL_CSS, render_eva_text, render_eva_word_card
    from visual_crop import (
        VISUAL_CROP_CSS,
        VISUAL_CROP_JS,
        baseline_box_from_points,
        box_from_zone,
        render_crop_canvas,
    )

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "highres_human_fill_html_not_visual_evidence"
ALLOWED_STATUS = "annotated/not_visible/uncertain"
TARGET_FIELDS = "manual_annotation_status manual_visual_notes"
STORAGE_KEY = "voynich.r42b.highres.fill"
DRAFT_ZONE_VERSION = 3
RAW_TRANSCRIPTION = ROOT / "data" / "raw" / "ZL3b-n.txt"
LINE_CALIBRATION_CSV = ROOT / "data" / "annotations" / "ready_visual_line_calibration_zl3b.csv"
LINE_CALIBRATION_GUARDRAIL = "line_calibration_tool_not_visual_evidence"
LOCUS_TRANSCRIPTION_RE = re.compile(r"^<(?P<locus>[^>]+)>\s+(?:<[^>]*>)?(?P<text>.*)$")

VISUAL_ZONE_OVERRIDES = {
    "f84r.24,+P0": {
        "top": 27.0,
        "left": 8.0,
        "width": 80.0,
        "height": 11.0,
        "label": "linha 24: bloco de texto superior",
    },
    "f84r.29,+P0": {
        "top": 58.0,
        "left": 8.0,
        "width": 80.0,
        "height": 8.0,
        "label": "linha 29: bloco de texto inferior",
    },
}

VISUAL_ZONE_GUARDS = {
    "f84r.24,+P0": {
        "min_top": 24.0,
        "max_bottom": 39.0,
        "reason": "linha 24 deve ficar no texto acima da faixa verde central",
    },
    "f84r.29,+P0": {
        "min_top": 56.0,
        "max_bottom": 70.0,
        "reason": "linha 29 deve ficar no bloco de escrita abaixo da faixa verde central",
    },
}

LOCUS_VISUAL_NOTES = {
    "f84r.24,+P0": "Posicao visual esperada: texto acima da faixa verde, nao em cima da imagem.",
    "f84r.29,+P0": "Posicao visual esperada: texto abaixo da faixa verde, no bloco de escrita.",
}


def validate_visual_zone_overrides() -> None:
    for raw, zone in VISUAL_ZONE_OVERRIDES.items():
        top = float(zone["top"])
        left = float(zone["left"])
        width = float(zone["width"])
        height = float(zone["height"])
        bottom = top + height
        right = left + width
        if top < 0 or left < 0 or bottom > 100 or right > 100:
            raise ValueError(f"{raw} visual zone is outside the image bounds")
        if height <= 0 or width <= 0:
            raise ValueError(f"{raw} visual zone must have positive width and height")
        guard = VISUAL_ZONE_GUARDS.get(raw)
        if not guard:
            continue
        min_top = float(guard["min_top"])
        max_bottom = float(guard["max_bottom"])
        if top < min_top or bottom > max_bottom:
            raise ValueError(f"{raw} visual zone violates guard: {guard['reason']}")


GROUP_LABELS = {
    "first_clear_regions": "comece por aqui",
    "middle_partial_regions": "precisa de mais zoom",
    "faint_source": "imagem apagada",
    "last_composite_pages": "pagina composta",
}

QUALITY_LABELS = {
    "high": "boa imagem",
    "medium_faint": "imagem fraca",
    "medium_composite": "pagina dupla/composta",
}

LOCATABLE_LABELS = {
    "yes_region": "regiao localizada",
    "partial": "regiao aproximada",
    "partial_composite_page": "regiao aproximada em pagina composta",
}

ACTION_HINTS = {
    "crop_upper_pool_text_lines": "Comece pelas linhas de texto acima da area ilustrada.",
    "crop_top_label_row": "Comece pela linha de rotulo no topo da pagina.",
    "crop_label_rows_and_match_petersen_lines": "Compare as faixas de rotulo com as linhas indicadas.",
    "rotate_crop_sector_and_red_line": "Use rotacao e procure o setor circular com a linha vermelha.",
    "rotate_crop_circle_labels": "Use rotacao e procure os rotulos ao redor do circulo.",
    "increase_contrast_crop_paragraph_starts": "Aumente contraste e procure o inicio dos paragrafos indicados.",
    "crop_composite_foldout_recipe_rows": "Na pagina composta, procure as linhas de receita indicadas.",
    "crop_composite_foldout_plant_rows": "Na pagina composta, procure as linhas de plantas indicadas.",
}

REVIEW_ORDER = {
    "f84r": (1, "first_clear_regions"),
    "f99r": (2, "first_clear_regions"),
    "f99v": (3, "middle_partial_regions"),
    "f67r2": (4, "middle_partial_regions"),
    "f67v1": (5, "middle_partial_regions"),
    "f1r": (6, "faint_source"),
    "f88v": (7, "last_composite_pages"),
    "f89r2": (8, "last_composite_pages"),
}

FIELDNAMES = [
    "route42b_id",
    "route42_id",
    "route42a_id",
    "route32_id",
    "route28_id",
    "folio",
    "priority_level",
    "locus_kind",
    "token_counts",
    "top_loci",
    "manifest_label",
    "yale_image_id",
    "yale_dimensions",
    "local_image_path",
    "yale_iiif_jpg_url",
    "yale_tiff_url",
    "yale_catalog_url",
    "image_quality_assist",
    "target_region_locatable_assist",
    "visual_context_assist",
    "suggested_manual_review_action",
    "review_rank",
    "review_group",
    "target_csv",
    "allowed_manual_annotation_status",
    "target_fields",
    "line_calibration_status",
    "line_calibration_json",
    "manual_annotation_status",
    "manual_visual_notes",
    "semantic_guardrail",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def read_optional_csv(path: Path) -> list[dict[str, str]]:
    return read_csv(path) if path.exists() else []


def parse_locus_line(value: str) -> tuple[str, int] | None:
    left = value.split(",", 1)[0]
    if "." not in left:
        return None
    folio, line_text = left.rsplit(".", 1)
    if not line_text.isdigit():
        return None
    return folio, int(line_text)


def load_locus_transcriptions(path: Path) -> tuple[dict[str, str], dict[str, int], dict[str, list[dict[str, str]]]]:
    texts: dict[str, str] = {}
    line_totals: dict[str, int] = {}
    locus_entries: dict[str, list[dict[str, str]]] = {}
    if not path.exists():
        return texts, line_totals, locus_entries
    for line in path.read_text(encoding="utf-8").splitlines():
        match = LOCUS_TRANSCRIPTION_RE.match(line)
        if not match:
            continue
        locus = match.group("locus")
        parsed = parse_locus_line(locus)
        if not parsed:
            continue
        folio, line_number = parsed
        text = match.group("text").strip()
        marker = locus.split(",", 1)[1] if "," in locus else ""
        texts[locus] = text
        line_totals[folio] = max(line_totals.get(folio, 0), line_number)
        locus_entries.setdefault(folio, []).append(
            {
                "locus": locus,
                "line_number": str(line_number),
                "marker": marker,
                "text": text,
            }
        )
    return texts, line_totals, locus_entries


LOCUS_TEXTS, FOLIO_LINE_TOTALS, FOLIO_LOCUS_ENTRIES = load_locus_transcriptions(RAW_TRANSCRIPTION)


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def dimensions(row: dict[str, str]) -> str:
    width = row.get("yale_width", "")
    height = row.get("yale_height", "")
    return f"{width}x{height}" if width and height else ""


def split_pipe(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip()]


def parse_baseline_points(value: str) -> list[tuple[float, float]]:
    value = value.strip()
    if not value:
        return []
    points: list[tuple[float, float]] = []
    for pair in value.split():
        if pair.count(",") != 1:
            return []
        raw_x, raw_y = pair.split(",", 1)
        try:
            x = float(raw_x)
            y = float(raw_y)
        except ValueError:
            return []
        if not (0 <= x <= 100 and 0 <= y <= 100):
            return []
        points.append((x, y))
    return points if len(points) >= 2 else []


def build_calibration_index(calibration_rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    index: dict[tuple[str, str], dict[str, str]] = {}
    for row in calibration_rows:
        if row.get("calibration_status") != "calibrated":
            continue
        points = row.get("baseline_points", "")
        if not parse_baseline_points(points):
            continue
        route32_id = row.get("route32_id", "")
        target_locus = row.get("target_locus", "")
        if route32_id and target_locus:
            index[(route32_id, target_locus)] = row
    return index


def line_calibration_payload(
    route32_id: str,
    top_loci: str,
    calibration_index: dict[tuple[str, str], dict[str, str]],
) -> tuple[str, str]:
    payload: dict[str, dict[str, str]] = {}
    calibrated = 0
    pending = 0
    for raw in split_pipe(top_loci):
        row = calibration_index.get((route32_id, raw))
        if row:
            payload[raw] = {
                "baseline_points": row.get("baseline_points", ""),
                "baseline_width_pct": row.get("baseline_width_pct", ""),
                "manual_notes": row.get("manual_notes", ""),
                "guardrail": LINE_CALIBRATION_GUARDRAIL,
            }
            calibrated += 1
        else:
            pending += 1
    status = f"calibrated={calibrated}|pending={pending}" if calibrated or pending else ""
    return status, json.dumps(payload, ensure_ascii=True, sort_keys=True)


def build_fill_html_rows(
    highres_rows: list[dict[str, str]],
    assist_rows: list[dict[str, str]],
    target_csv: str,
    calibration_rows: list[dict[str, str]] | None = None,
) -> list[dict[str, str]]:
    assist_by_route32 = {row.get("route32_id", ""): row for row in assist_rows}
    calibration_index = build_calibration_index(calibration_rows or [])
    staged_rows: list[dict[str, str]] = []
    for highres in highres_rows:
        route32_id = highres.get("route32_id", "")
        folio = highres.get("folio", "")
        rank, group = REVIEW_ORDER.get(folio, (99, "unranked_manual_review"))
        assist = assist_by_route32.get(route32_id, {})
        calibration_status, calibration_json = line_calibration_payload(
            route32_id, highres.get("top_loci", ""), calibration_index
        )
        staged_rows.append(
            {
                "route42b_id": "",
                "route42_id": highres.get("route42_id", ""),
                "route42a_id": assist.get("route42a_id", ""),
                "route32_id": route32_id,
                "route28_id": highres.get("route28_id", ""),
                "folio": folio,
                "priority_level": highres.get("priority_level", ""),
                "locus_kind": highres.get("locus_kind", ""),
                "token_counts": highres.get("token_counts", ""),
                "top_loci": highres.get("top_loci", ""),
                "manifest_label": highres.get("manifest_label", ""),
                "yale_image_id": highres.get("yale_image_id", ""),
                "yale_dimensions": dimensions(highres),
                "local_image_path": highres.get("local_image_path", ""),
                "yale_iiif_jpg_url": highres.get("yale_iiif_jpg_url", ""),
                "yale_tiff_url": highres.get("yale_tiff_url", ""),
                "yale_catalog_url": highres.get("yale_catalog_url", ""),
                "image_quality_assist": assist.get("image_quality_assist", ""),
                "target_region_locatable_assist": assist.get("target_region_locatable_assist", ""),
                "visual_context_assist": assist.get("visual_context_assist", ""),
                "suggested_manual_review_action": assist.get("suggested_manual_review_action", ""),
                "review_rank": str(rank),
                "review_group": group,
                "target_csv": target_csv,
                "allowed_manual_annotation_status": ALLOWED_STATUS,
                "target_fields": TARGET_FIELDS,
                "line_calibration_status": calibration_status,
                "line_calibration_json": calibration_json,
                "manual_annotation_status": highres.get("manual_annotation_status", ""),
                "manual_visual_notes": highres.get("manual_visual_notes", ""),
                "semantic_guardrail": GUARDRAIL,
            }
        )
    staged_rows.sort(key=lambda row: (int(row["review_rank"]), row["route32_id"]))
    for index, row in enumerate(staged_rows, start=1):
        row["route42b_id"] = f"R42B-{index:03d}"
    return staged_rows


def summarize_fill_html_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "folio": Counter(row.get("folio", "") for row in rows),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "locus_kind": Counter(row.get("locus_kind", "") for row in rows),
        "review_group": Counter(row.get("review_group", "") for row in rows),
        "image_quality_assist": Counter(row.get("image_quality_assist", "") for row in rows),
        "target_region_locatable_assist": Counter(row.get("target_region_locatable_assist", "") for row in rows),
        "semantic_guardrail": Counter(row.get("semantic_guardrail", "") for row in rows),
    }


def write_summary_csv(path: Path, summary: dict[str, Counter[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "item", "n"])
        writer.writeheader()
        for metric, counts in summary.items():
            for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
                writer.writerow({"metric": metric, "item": key, "n": value})


def markdown_cell(value: str) -> str:
    return value.replace("|", "<br>")


def render_counts(title: str, counts: Counter[str]) -> list[str]:
    lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"|{markdown_cell(key)}|{value}|")
    lines.append("")
    return lines


def image_src(row: dict[str, str]) -> str:
    local = row.get("local_image_path", "")
    if local:
        return "../" + local
    return row.get("yale_iiif_jpg_url", "")


def token_items(value: str) -> list[str]:
    items: list[str] = []
    for raw in split_pipe(value):
        token, _, count = raw.partition("=")
        label = token.strip()
        if count.strip():
            label = f"{label} ({count.strip()}x)"
        if label:
            items.append(label)
    return items


def token_word_items(value: str) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for raw in split_pipe(value):
        token, _, count = raw.partition("=")
        token = token.strip()
        if token:
            items.append((token, count.strip()))
    return items


def locus_items(value: str) -> list[tuple[str, str]]:
    items: list[tuple[str, str]] = []
    for raw in split_pipe(value):
        left, _, marker = raw.partition(",")
        line = left.rsplit(".", 1)[-1] if "." in left else left
        label = f"linha {line}" if line else left
        if marker.strip():
            label = f"{label} ({marker.strip()})"
        items.append((label, raw))
    return items


def locus_line_marker_items(value: str) -> list[tuple[int, str, str]]:
    items: list[tuple[int, str, str]] = []
    seen: set[tuple[int, str]] = set()
    for raw in split_pipe(value):
        left, _, marker = raw.partition(",")
        line_text = left.rsplit(".", 1)[-1] if "." in left else ""
        if not line_text.isdigit():
            continue
        line_number = int(line_text)
        marker = marker.strip()
        key = (line_number, marker)
        if key in seen:
            continue
        seen.add(key)
        items.append((line_number, marker, raw))
    return items


def load_line_calibrations(value: str) -> dict[str, dict[str, str]]:
    if not value:
        return {}
    try:
        decoded = json.loads(value)
    except json.JSONDecodeError:
        return {}
    if not isinstance(decoded, dict):
        return {}
    output: dict[str, dict[str, str]] = {}
    for locus, payload in decoded.items():
        if isinstance(locus, str) and isinstance(payload, dict):
            points = str(payload.get("baseline_points", ""))
            if parse_baseline_points(points):
                output[locus] = {str(key): str(value) for key, value in payload.items()}
    return output


def render_baseline_marker(raw: str, line_number: int, marker: str, calibration: dict[str, str]) -> str:
    points = calibration.get("baseline_points", "")
    parsed_points = parse_baseline_points(points)
    if not parsed_points:
        return ""
    first_x, first_y = parsed_points[0]
    marker_suffix = f" {marker}" if marker else ""
    return (
        '<svg class="target-baseline" viewBox="0 0 100 100" preserveAspectRatio="none" '
        f'aria-label="linha {line_number} calibrada" data-zone-id="{html.escape(raw)}" '
        'data-zone-kind="calibrated-baseline">'
        f'<polyline points="{html.escape(points)}"></polyline>'
        "</svg>"
        '<span class="target-baseline-label" '
        f'style="left:{first_x:.2f}%; top:{first_y:.2f}%;" title="{html.escape(raw)}">'
        f'<b>linha {line_number} calibrada</b>'
        f'<small>{html.escape(marker_suffix.strip())}</small>'
        "</span>"
    )


def render_needs_calibration_marker(raw: str, line_number: int, marker: str, index: int) -> str:
    marker_suffix = f" {marker}" if marker else ""
    top = 42 + min(index, 5) * 6
    return (
        '<span class="needs-calibration-badge" '
        f'style="top:{top:.2f}%;" title="{html.escape(raw)}" data-zone-id="{html.escape(raw)}" '
        'data-zone-kind="needs-line-calibration">'
        f'<b>linha {line_number}{html.escape(marker_suffix)}</b>'
        "<small>posicao visual ainda nao calibrada: use Calibrar linhas</small>"
        "</span>"
    )


def render_line_overlay(value: str, calibration_json: str = "") -> str:
    items = locus_line_marker_items(value)
    if not items:
        return ""
    calibrations = load_line_calibrations(calibration_json)
    markers: list[str] = []
    pending_without_position = 0
    has_probable_zone = False
    has_calibrated_baseline = False
    for index, (line_number, marker, raw) in enumerate(items):
        marker_suffix = f" {marker}" if marker else ""
        calibration = calibrations.get(raw)
        if calibration:
            has_calibrated_baseline = True
            markers.append(render_baseline_marker(raw, line_number, marker, calibration))
            continue
        zone = VISUAL_ZONE_OVERRIDES.get(raw)
        if zone:
            has_probable_zone = True
            markers.append(
                '<span class="target-zone" '
                f'style="top:{zone["top"]:.2f}%; left:{zone["left"]:.2f}%; '
                f'width:{zone["width"]:.2f}%; height:{zone["height"]:.2f}%;" '
                f'title="{html.escape(raw)}" data-zone-id="{html.escape(raw)}" '
                'data-zone-kind="probable-text-block">'
                f'<b>{html.escape(zone["label"])}</b>'
                f'<small>{html.escape(marker_suffix.strip())}</small>'
                "</span>"
            )
            continue
        pending_without_position += 1
        markers.append(render_needs_calibration_marker(raw, line_number, marker, index))
    note_parts: list[str] = []
    if has_calibrated_baseline:
        note_parts.append("baselines calibradas R42C")
    if has_probable_zone:
        note_parts.append("zonas provaveis de bloco")
    if pending_without_position:
        note_parts.append("linhas sem posicao calibrada")
    note = " + ".join(note_parts) if note_parts else "sem posicao visual calibrada"
    return (
        '<div class="line-overlay" aria-label="Apoio visual dos alvos">'
        f'<span class="line-guide-note">{html.escape(note)}</span>'
        + "".join(markers)
        + "</div>"
    )


def render_token_chips(value: str) -> str:
    items = token_word_items(value)
    if not items:
        return '<span class="target-chip muted-chip">sem token definido</span>'
    cards: list[str] = []
    for token, count in items:
        count_label = f"{count}x" if count else "1x"
        cards.append(render_eva_word_card(token, count_label=count_label, is_target=True))
    return "\n".join(cards)


def render_locus_chips(value: str) -> str:
    items = locus_items(value)
    if not items:
        return '<span class="target-chip muted-chip">sem linha definida</span>'
    return "\n".join(
        f'<span class="target-chip" title="{html.escape(raw)}">{html.escape(label)}</span>' for label, raw in items
    )


def highlight_target_tokens(text: str, token_counts: str) -> str:
    tokens = "|".join(token for token, _count in token_word_items(token_counts))
    return render_eva_text(text, highlight_tokens=tokens, compact=True)


def render_line_reference(row: dict[str, str]) -> str:
    folio = row.get("folio", "")
    line_numbers = [line for line, _marker, _raw in locus_line_marker_items(row.get("top_loci", ""))]
    total = FOLIO_LINE_TOTALS.get(folio)
    if not total and not line_numbers:
        return ""
    target_text = ", ".join(f"linha {line}" for line in line_numbers) if line_numbers else "sem alvo definido"
    total_text = f"{total} entradas/loci ZL3b" if total else "total de entradas ZL3b nao encontrado"
    explanation = (
        " Isso nao sao 47 linhas visuais contadas na imagem; inclui rotulos pequenos e blocos de transcricao."
        if total
        else ""
    )
    return (
        '<p class="line-reference">'
        f'Referencia: {html.escape(folio)} tem {html.escape(total_text)}. {html.escape(explanation.strip())} '
        f'Alvos: {html.escape(target_text)}.'
        "</p>"
    )


def render_folio_locus_source(folio: str) -> str:
    entries = FOLIO_LOCUS_ENTRIES.get(folio, [])
    if not entries:
        return ""
    rows: list[str] = []
    for entry in entries:
        rows.append(
            '<div class="folio-locus-row">'
            f'<code>{html.escape(entry["locus"])}</code>'
            f'<span>{render_eva_text(entry["text"], compact=True)}</span>'
            "</div>"
        )
    return (
        '<details class="folio-locus-source">'
        f'<summary>Ver as {len(entries)} entradas ZL3b</summary>'
        "<p>Esta lista e a origem do total mostrado acima. Ela vem da transcricao ZL3b, nao de uma contagem visual direta da imagem.</p>"
        + "".join(rows)
        + "</details>"
    )


def render_locus_text_hints(top_loci: str, token_counts: str) -> str:
    rows: list[str] = []
    for label, raw in locus_items(top_loci):
        text = LOCUS_TEXTS.get(raw)
        if not text:
            continue
        note = LOCUS_VISUAL_NOTES.get(raw, "")
        note_html = f'<em>{html.escape(note)}</em>' if note else ""
        rows.append(
            '<div class="line-text-row">'
            f'<span>{html.escape(label)}</span>'
            f'<div>{highlight_target_tokens(text, token_counts)}{note_html}</div>'
            "</div>"
        )
    if not rows:
        return ""
    return (
        '<div class="line-text-hints" aria-label="Texto transcrito das linhas alvo">'
        "<strong>Texto de referencia</strong>"
        + "".join(rows)
        + "</div>"
    )


def render_focus_crop_previews(row: dict[str, str], src: str) -> str:
    calibrations = load_line_calibrations(row.get("line_calibration_json", ""))
    crops: list[str] = []
    for line_number, marker, raw in locus_line_marker_items(row.get("top_loci", "")):
        marker_suffix = f" {marker}" if marker else ""
        calibration = calibrations.get(raw)
        if calibration:
            box = baseline_box_from_points(calibration.get("baseline_points", ""))
            label = f"linha {line_number}{marker_suffix}: recorte real calibrado"
            note = "Olhe este recorte primeiro; ele vem da linha ajustada na R42C."
        else:
            zone = VISUAL_ZONE_OVERRIDES.get(raw)
            box = box_from_zone(zone) if zone else None
            label = str(zone.get("label", f"linha {line_number}{marker_suffix}: recorte real")) if zone else ""
            note = "Olhe este recorte primeiro; e a zona visual conhecida para este alvo."
        if box:
            crops.append(render_crop_canvas(src, box, label, note=note, class_name="focus-crop", is_target=True))
    if not crops:
        return ""
    return (
        '<section class="focus-crops visual-crop-grid" aria-label="Recortes reais da pagina">'
        "<h3>Recortes reais da pagina</h3>"
        '<p class="plain-hint">Olhe este recorte primeiro. Depois use a imagem grande so se precisar confirmar contexto.</p>'
        + "".join(crops)
        + "</section>"
    )


def readable_label(value: str, labels: dict[str, str]) -> str:
    if not value:
        return ""
    return labels.get(value, value.replace("_", " "))


def render_html_card(row: dict[str, str]) -> str:
    route32 = html.escape(row.get("route32_id", ""))
    title = html.escape(f"{row.get('route42b_id', '')} / {row.get('route32_id', '')} / {row.get('folio', '')}")
    src = html.escape(image_src(row))
    folio = html.escape(row.get("folio", ""))
    tokens = html.escape(row.get("token_counts", ""))
    loci = html.escape(row.get("top_loci", ""))
    dimensions_text = html.escape(row.get("yale_dimensions", ""))
    quality_raw = row.get("image_quality_assist", "")
    locatable_raw = row.get("target_region_locatable_assist", "")
    quality = html.escape(readable_label(quality_raw, QUALITY_LABELS))
    locatable = html.escape(readable_label(locatable_raw, LOCATABLE_LABELS))
    visual_context = html.escape(row.get("visual_context_assist", ""))
    manual_action_raw = row.get("suggested_manual_review_action", "")
    manual_action = html.escape(readable_label(manual_action_raw, ACTION_HINTS))
    guardrail = html.escape(row.get("semantic_guardrail", GUARDRAIL))
    iiif = html.escape(row.get("yale_iiif_jpg_url", ""))
    tiff = html.escape(row.get("yale_tiff_url", ""))
    catalog = html.escape(row.get("yale_catalog_url", ""))
    target_csv = html.escape(row.get("target_csv", ""))
    group_label = html.escape(readable_label(row.get("review_group", ""), GROUP_LABELS))
    token_chips = render_token_chips(row.get("token_counts", ""))
    technical_token_chips = render_token_chips(row.get("token_counts", ""))
    locus_chips = render_locus_chips(row.get("top_loci", ""))
    line_reference = render_line_reference(row)
    folio_locus_source = render_folio_locus_source(row.get("folio", ""))
    line_text_hints = render_locus_text_hints(row.get("top_loci", ""), row.get("token_counts", ""))
    line_overlay = render_line_overlay(row.get("top_loci", ""), row.get("line_calibration_json", ""))
    focus_crops = render_focus_crop_previews(row, src)
    return f"""
<article class="review-card" data-route32-id="{route32}" data-folio="{folio}">
  <section class="image-panel" aria-label="Imagem high-res {route32}">
    <div class="image-stage">
      <div class="image-wrap">
        <img src="{src}" alt="Fonte Yale high-res para {route32}">
        {line_overlay}
      </div>
    </div>
  </section>
  <aside class="decision-panel">
    <header class="card-head">
      <div>
        <p class="eyebrow">{group_label}</p>
        <h2>{title}</h2>
      </div>
      <span class="status-pill">{html.escape(row.get('priority_level', ''))} / {html.escape(row.get('locus_kind', ''))}</span>
    </header>
    <section class="focus-question" aria-label="Pergunta principal">
      <p class="step-label">Pergunta principal</p>
      <h3>Voce achou essas palavrinhas na imagem?</h3>
      <p>Nao precisa traduzir. So olhe, compare e clique em uma resposta.</p>
    </section>
    <section class="target-block target-brief">
      <h3>Palavrinhas para procurar</h3>
      <div class="brief-row">
        <span class="brief-label">Desenho</span>
        <div class="chip-row">{token_chips}</div>
      </div>
      <div class="brief-row">
        <span class="brief-label">Linhas</span>
        <div class="chip-row">{locus_chips}</div>
      </div>
      {line_reference}
      {folio_locus_source}
      {line_text_hints}
      {focus_crops}
      <p class="plain-hint">A imagem so mostra baseline calibrada pela R42C ou zona aproximada de bloco. Ela nao calcula posicao visual pela numeracao ZL3b.</p>
    </section>
    <section class="target-block">
      <h3>Dica de onde olhar</h3>
      <p class="plain-hint">{manual_action}</p>
      <div class="mini-facts">
        <span>{quality}</span>
        <span>{locatable}</span>
      </div>
    </section>
    <section class="decision-block" aria-label="Decisao humana">
      <h3>Clique em uma resposta</h3>
      <div class="decision-buttons">
        <button type="button" class="decision-button" data-value="annotated">
          <strong>Achei</strong>
          <span>Use quando voce conseguiu ver o alvo na pagina.</span>
          <code>annotated</code>
        </button>
        <button type="button" class="decision-button" data-value="not_visible">
          <strong>Nao achei</strong>
          <span>Use quando voce olhou e nao encontrou o alvo.</span>
          <code>not_visible</code>
        </button>
        <button type="button" class="decision-button" data-value="uncertain">
          <strong>Nao sei</strong>
          <span>Use quando parece que pode estar ali, mas voce nao tem certeza.</span>
          <code>uncertain</code>
        </button>
      </div>
      <input type="hidden" name="manual_annotation_status" value="">
      <label>Nota pronta
        <span class="auto-note-badge">aparece sozinha</span>
        <span class="notes-helper" data-notes-helper>Clique em Achei, Nao achei ou Nao sei. A nota sera preenchida automaticamente.</span>
        <textarea name="manual_visual_notes" rows="7" spellcheck="false" placeholder="A nota aparece aqui depois que voce clicar em uma resposta."></textarea>
      </label>
      <div class="note-actions">
        <button type="button" class="template-button" data-fill-note>Refazer nota automatica</button>
      </div>
    </section>
    <details class="technical-details">
      <summary>Detalhes tecnicos</summary>
      <dl>
        <dt>Tokens em imagem</dt><dd>{technical_token_chips}</dd>
        <dt>Loci brutos</dt><dd><code>{loci}</code></dd>
        <dt>Dimensoes</dt><dd><code>{dimensions_text}</code></dd>
        <dt>Contexto R42A</dt><dd><code>{visual_context}</code></dd>
        <dt>Acao R42A</dt><dd><code>{html.escape(manual_action_raw)}</code></dd>
      </dl>
    </details>
    <section class="target-block source-links">
      <h3>Fontes</h3>
      <a href="{iiif}">JPEG IIIF</a>
      <a href="{tiff}">TIFF</a>
      <a href="{catalog}">Catalogo</a>
    </section>
    <footer>
      <code>{target_csv}</code>
      <code>{guardrail}</code>
    </footer>
  </aside>
</article>
""".strip()


def render_queue_item(row: dict[str, str], index: int) -> str:
    route32 = html.escape(row.get("route32_id", ""))
    folio = html.escape(row.get("folio", ""))
    group = html.escape(readable_label(row.get("review_group", ""), GROUP_LABELS))
    return f"""
<button type="button" class="queue-item" data-index="{index}" data-route32-id="{route32}">
  <span class="queue-number">{index + 1}</span>
  <span class="queue-main">
    <strong>{folio}</strong>
    <small>{route32} / {group}</small>
  </span>
  <span class="queue-status" data-status-label>pendente</span>
</button>
""".strip()


def render_html(rows: list[dict[str, str]], target_csv: str) -> str:
    cards = "\n".join(render_html_card(row) for row in rows)
    queue = "\n".join(render_queue_item(row, index) for index, row in enumerate(rows))
    total = len(rows)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rota 42B - Revisao humana guiada R32 high-res</title>
  <style>
    :root {{ color-scheme: light; --ink: #172026; --muted: #60707b; --line: #c9c0b2; --paper: #fffdf8; --bg: #f3efe6; --accent: #17625c; --accent-ink: #0b3934; --danger: #8f3f33; --shadow: 0 16px 42px rgba(41, 34, 22, 0.12); }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: var(--ink); background: var(--bg); }}
    button, input, textarea {{ font: inherit; }}
    button {{ min-height: 36px; border: 1px solid #9fb8b2; border-radius: 6px; background: #e8f1ef; color: var(--accent-ink); padding: 0 12px; cursor: pointer; }}
    button:hover {{ border-color: var(--accent); }}
    button:focus-visible, textarea:focus-visible, input:focus-visible {{ outline: 3px solid rgba(23, 98, 92, 0.22); outline-offset: 2px; }}
    a {{ color: #145c56; }}
    .button-link {{ display: inline-flex; align-items: center; min-height: 36px; border: 1px solid var(--line); border-radius: 6px; background: #f7f3eb; color: var(--ink); padding: 0 12px; font-weight: 680; text-decoration: none; }}
    .button-link:hover {{ border-color: var(--accent); background: #f2eadb; }}
    code {{ white-space: pre-wrap; overflow-wrap: anywhere; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; }}
    h1, h2, h3, p {{ margin: 0; letter-spacing: 0; }}
    h1 {{ font-size: 25px; line-height: 1.12; }}
    h2 {{ font-size: 21px; line-height: 1.18; }}
    h3 {{ font-size: 14px; line-height: 1.2; }}
    p {{ color: var(--muted); }}
    .app-shell {{ min-height: 100vh; display: grid; grid-template-columns: 292px minmax(0, 1fr); }}
    .side-panel {{ position: sticky; top: 0; height: 100vh; overflow: auto; padding: 18px 14px; border-right: 1px solid var(--line); background: #fbf7ef; }}
    .brand-block {{ display: grid; gap: 8px; padding: 4px 2px 16px; }}
    .simple-guide {{ display: grid; gap: 10px; margin: 0 0 16px; padding: 12px; border: 1px solid #a9c6bd; border-radius: 8px; background: #edf5f2; }}
    .simple-guide h2 {{ font-size: 16px; }}
    .guide-list {{ display: grid; gap: 8px; margin: 0; padding: 0; list-style: none; }}
    .guide-list li {{ display: grid; grid-template-columns: 24px minmax(0, 1fr); gap: 8px; align-items: start; color: var(--ink); font-size: 13px; line-height: 1.35; }}
    .guide-list b {{ display: grid; place-items: center; width: 22px; height: 22px; border-radius: 999px; background: var(--accent); color: #f8fbfa; font-size: 12px; }}
    .decision-cheat {{ display: grid; gap: 6px; margin: 0 0 16px; padding: 10px; border: 1px solid var(--line); border-radius: 8px; background: #fffaf1; color: var(--muted); font-size: 13px; line-height: 1.35; }}
    .progress-block {{ display: grid; gap: 8px; margin: 0 0 16px; }}
    .progress-row {{ display: flex; justify-content: space-between; gap: 12px; color: var(--muted); font-size: 13px; }}
    .progress-track {{ height: 8px; overflow: hidden; border: 1px solid var(--line); border-radius: 999px; background: #eee6d8; }}
    .progress-fill {{ width: 0%; height: 100%; background: var(--accent); transition: width 180ms ease; }}
    .review-queue {{ display: grid; gap: 8px; }}
    .queue-item {{ display: grid; grid-template-columns: 30px minmax(0, 1fr) auto; gap: 8px; align-items: center; width: 100%; min-height: 58px; padding: 8px; text-align: left; background: #fffaf1; border-color: var(--line); color: var(--ink); }}
    .queue-item.active {{ border-color: var(--accent); background: #edf5f2; box-shadow: inset 3px 0 0 var(--accent); }}
    .queue-number {{ display: grid; place-items: center; width: 28px; height: 28px; border-radius: 999px; background: #eee5d6; color: var(--muted); font-size: 13px; }}
    .queue-main {{ min-width: 0; display: grid; gap: 2px; }}
    .queue-main strong {{ font-size: 14px; }}
    .queue-main small {{ overflow: hidden; text-overflow: ellipsis; white-space: nowrap; color: var(--muted); font-size: 12px; }}
    .queue-status {{ min-width: 70px; padding: 4px 7px; border: 1px solid var(--line); border-radius: 999px; background: #f8f2e8; color: var(--muted); text-align: center; font-size: 12px; }}
    .queue-item.done .queue-status {{ border-color: #9fc2b6; background: #e7f3ee; color: #225b50; }}
    .main-panel {{ min-width: 0; display: grid; grid-template-rows: auto minmax(0, 1fr) auto; height: 100vh; }}
    .topbar {{ position: sticky; top: 0; z-index: 5; display: grid; gap: 12px; padding: 14px 18px; border-bottom: 1px solid var(--line); background: rgba(255, 253, 248, 0.96); backdrop-filter: blur(8px); }}
    .topbar-main {{ display: flex; align-items: center; justify-content: space-between; gap: 16px; }}
    .current-counter {{ display: inline-flex; align-items: center; min-height: 32px; padding: 0 10px; border: 1px solid var(--line); border-radius: 999px; background: #f8f2e8; white-space: nowrap; }}
    .finish-banner {{ padding: 10px 12px; border: 1px solid #9fc2b6; border-radius: 8px; background: #e7f3ee; color: #225b50; }}
    .tool-row {{ display: flex; flex-wrap: wrap; gap: 8px; align-items: center; }}
    .tool-row button {{ background: #f7f3eb; border-color: var(--line); color: var(--ink); }}
    .zoom-control {{ display: inline-flex; gap: 8px; align-items: center; min-height: 36px; padding: 0 10px; border: 1px solid var(--line); border-radius: 6px; background: #fffaf1; }}
    .zoom-control input {{ width: 160px; accent-color: var(--accent); }}
    .card-stack {{ min-height: 0; overflow: hidden; }}
    .review-card {{ --line-guide-shift: 0px; display: none; grid-template-columns: minmax(0, 1fr) 390px; gap: 0; height: 100%; min-height: 0; background: var(--paper); }}
    .review-card.active {{ display: grid; }}
    .image-panel {{ min-width: 0; min-height: 0; display: grid; padding: 14px; background: #ded6c8; }}
    .image-stage {{ min-width: 0; min-height: 0; display: grid; place-items: center; overflow: auto; border: 1px solid var(--line); border-radius: 8px; background: #efe8dc; box-shadow: var(--shadow); }}
    .image-wrap {{ position: relative; display: block; width: min(100%, 980px); transform-origin: center center; transition: transform 120ms ease, filter 120ms ease; }}
    .image-stage img {{ display: block; width: 100%; max-width: none; height: auto; }}
    .line-overlay {{ position: absolute; inset: 0; pointer-events: none; }}
    .hide-line-guides .line-overlay {{ display: none; }}
    .line-guide-note {{ position: absolute; top: 8px; left: 8px; padding: 4px 7px; border: 1px solid rgba(58, 38, 27, 0.36); border-radius: 999px; background: rgba(255, 250, 241, 0.88); color: #3a261b; font-size: 12px; }}
    .target-zone {{ position: absolute; display: flex; align-items: start; justify-content: flex-end; gap: 6px; padding: 5px; transform: translateY(var(--line-guide-shift)); border: 2px solid rgba(143, 63, 51, 0.68); border-radius: 8px; background: rgba(255, 224, 138, 0.10); box-shadow: inset 0 0 0 1px rgba(255, 253, 248, 0.52); color: #3a261b; }}
    .target-zone b {{ padding: 3px 7px; border: 1px solid rgba(143, 63, 51, 0.58); border-radius: 999px; background: rgba(255, 245, 242, 0.94); font-size: 12px; }}
    .target-zone small {{ padding: 2px 5px; border-radius: 999px; background: rgba(255, 250, 241, 0.88); color: var(--muted); font-size: 10px; }}
    .target-baseline {{ position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }}
    .target-baseline polyline {{ fill: none; stroke: rgba(31, 118, 104, 0.96); stroke-width: 0.55; vector-effect: non-scaling-stroke; filter: drop-shadow(0 1px 0 rgba(255, 253, 248, 0.82)); }}
    .target-baseline-label {{ position: absolute; display: inline-flex; align-items: center; gap: 5px; transform: translateY(-105%); color: #174d44; }}
    .target-baseline-label b {{ padding: 3px 7px; border: 1px solid rgba(31, 118, 104, 0.58); border-radius: 999px; background: rgba(237, 245, 242, 0.94); font-size: 12px; }}
    .target-baseline-label small {{ padding: 2px 5px; border-radius: 999px; background: rgba(255, 250, 241, 0.88); color: var(--muted); font-size: 10px; }}
    .needs-calibration-badge {{ position: absolute; left: 8px; max-width: min(360px, 72%); display: grid; gap: 3px; padding: 7px 9px; border: 1px solid rgba(143, 63, 51, 0.58); border-radius: 8px; background: rgba(255, 250, 241, 0.92); color: #3a261b; transform: translateY(var(--line-guide-shift)); }}
    .needs-calibration-badge b {{ font-size: 12px; line-height: 1.15; }}
    .needs-calibration-badge small {{ color: var(--danger); font-size: 11px; line-height: 1.25; }}
    .decision-panel {{ min-width: 0; overflow: auto; display: grid; align-content: start; gap: 14px; padding: 18px; border-left: 1px solid var(--line); background: #fffdf8; }}
    .card-head {{ display: grid; gap: 10px; padding-bottom: 6px; border-bottom: 1px solid var(--line); }}
    .eyebrow {{ margin-bottom: 4px; font-size: 12px; color: var(--accent); text-transform: uppercase; }}
    .status-pill {{ display: inline-flex; align-items: center; width: fit-content; min-height: 28px; padding: 0 9px; border: 1px solid var(--line); border-radius: 999px; background: #f8f5ee; font-size: 13px; white-space: nowrap; }}
    .focus-question {{ display: grid; gap: 8px; padding: 14px; border: 1px solid #a9c6bd; border-radius: 8px; background: #edf5f2; }}
    .focus-question h3 {{ font-size: 22px; line-height: 1.15; }}
    .step-label {{ color: var(--accent); font-size: 12px; font-weight: 750; text-transform: uppercase; }}
    .target-block, .decision-block {{ display: grid; gap: 8px; }}
    .target-brief {{ padding: 12px; border: 1px solid var(--line); border-radius: 8px; background: #fffaf1; }}
    .brief-row {{ display: grid; grid-template-columns: 62px minmax(0, 1fr); gap: 8px; align-items: start; }}
    .brief-label {{ color: var(--muted); font-size: 13px; padding-top: 5px; }}
    .chip-row {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .target-chip {{ display: inline-flex; align-items: center; min-height: 28px; padding: 0 8px; border: 1px solid var(--line); border-radius: 999px; background: #f7f3eb; font-size: 13px; }}
    .muted-chip {{ color: var(--muted); }}
    .line-reference {{ padding: 8px 10px; border: 1px solid #d6cbb9; border-radius: 6px; background: #fbf7ef; color: var(--muted); font-size: 13px; line-height: 1.35; }}
    .folio-locus-source {{ border: 1px solid #d6cbb9; border-radius: 6px; background: #fbf7ef; padding: 8px 10px; }}
    .folio-locus-source summary {{ cursor: pointer; color: var(--ink); font-size: 13px; font-weight: 750; }}
    .folio-locus-source p {{ margin: 8px 0; font-size: 12px; line-height: 1.35; }}
    .folio-locus-row {{ display: grid; grid-template-columns: 98px minmax(0, 1fr); gap: 8px; padding: 5px 0; border-top: 1px solid rgba(201, 192, 178, 0.65); }}
    .folio-locus-row code {{ color: var(--accent-ink); }}
    .folio-locus-row span {{ min-width: 0; color: var(--muted); font-size: 12px; line-height: 1.35; overflow-wrap: anywhere; }}
    .line-text-hints {{ display: grid; gap: 7px; padding: 10px; border: 1px solid #d6cbb9; border-radius: 6px; background: #fbf7ef; }}
    .line-text-hints strong {{ font-size: 13px; color: var(--ink); }}
    .line-text-row {{ display: grid; grid-template-columns: 76px minmax(0, 1fr); gap: 8px; align-items: start; }}
    .line-text-row span {{ color: var(--muted); font-size: 12px; padding-top: 2px; }}
    .line-text-row code {{ display: block; font-size: 12px; line-height: 1.35; }}
    .line-text-row em {{ display: block; margin-top: 4px; color: #8f3f33; font-size: 12px; font-style: normal; line-height: 1.3; }}
    .line-text-row mark {{ padding: 0 2px; border-radius: 3px; background: #ffe08a; color: #3a261b; }}
{EVA_VISUAL_CSS}
{VISUAL_CROP_CSS}
    .word-card {{ display: grid; gap: 4px; min-width: 142px; padding: 8px; border: 1px solid var(--line); border-radius: 8px; background: #f7f3eb; }}
    .eva-word {{ display: block; width: 100%; height: 48px; }}
    .eva-word path {{ fill: none; stroke: #3a261b; stroke-width: 3.2; stroke-linecap: round; stroke-linejoin: round; }}
    .eva-fallback {{ fill: #3a261b; font: 28px Georgia, serif; }}
    .word-code {{ color: var(--muted); font-size: 12px; }}
    .word-count {{ width: fit-content; min-height: 20px; padding: 1px 7px; border: 1px solid var(--line); border-radius: 999px; color: var(--muted); font-size: 11px; }}
    .plain-hint {{ padding: 10px; border: 1px solid var(--line); border-radius: 6px; background: #fbf7ef; color: var(--ink); }}
    .mini-facts {{ display: flex; flex-wrap: wrap; gap: 6px; }}
    .mini-facts span {{ min-height: 26px; padding: 4px 8px; border: 1px solid var(--line); border-radius: 999px; background: #f8f2e8; color: var(--muted); font-size: 12px; }}
    dl {{ display: grid; grid-template-columns: max-content minmax(0, 1fr); gap: 6px 12px; margin: 0; }}
    dt {{ color: var(--muted); }}
    dd {{ margin: 0; min-width: 0; }}
    .decision-buttons {{ display: grid; grid-template-columns: 1fr; gap: 8px; }}
    .decision-button {{ display: grid; gap: 4px; min-height: 86px; padding: 12px; background: #f7f3eb; border-color: var(--line); color: var(--ink); text-align: left; }}
    .decision-button strong {{ font-size: 19px; line-height: 1.1; }}
    .decision-button span {{ color: var(--muted); font-size: 13px; line-height: 1.25; }}
    .decision-button code {{ display: none; }}
    .decision-button.selected {{ background: var(--accent); border-color: var(--accent); color: #f8fbfa; }}
    .decision-button.selected span, .decision-button.selected code {{ color: #d8e9e5; }}
    label {{ display: grid; gap: 6px; font-weight: 650; font-size: 14px; }}
    .notes-helper {{ color: var(--muted); font-weight: 400; font-size: 13px; line-height: 1.35; }}
    .note-actions {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .template-button {{ background: #edf5f2; border-color: #a9c6bd; color: var(--accent-ink); }}
    .auto-note-badge {{ display: inline-flex; width: fit-content; min-height: 24px; align-items: center; padding: 3px 8px; border: 1px solid #9fc2b6; border-radius: 999px; background: #e7f3ee; color: #225b50; font-size: 12px; font-weight: 650; }}
    textarea {{ width: 100%; min-height: 136px; resize: vertical; border: 1px solid var(--line); border-radius: 6px; padding: 10px; background: #fff; color: var(--ink); }}
    .technical-details {{ border: 1px solid var(--line); border-radius: 8px; background: #fbf7ef; padding: 10px; }}
    .technical-details summary {{ cursor: pointer; color: var(--muted); font-size: 13px; }}
    .technical-details dl {{ margin-top: 10px; }}
    .source-links {{ grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 8px; }}
    .source-links h3 {{ grid-column: 1 / -1; }}
    .source-links a {{ display: grid; place-items: center; min-height: 36px; border: 1px solid var(--line); border-radius: 6px; background: #f7f3eb; text-decoration: none; }}
    footer {{ display: grid; gap: 6px; color: var(--muted); }}
    .csv-drawer {{ border-top: 1px solid var(--line); background: #fbf7ef; padding: 12px 18px 18px; }}
    .csv-drawer summary {{ cursor: pointer; color: var(--muted); font-weight: 650; }}
    .csv-drawer[open] summary {{ margin-bottom: 10px; }}
    .csv-actions {{ display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 12px; margin-bottom: 8px; }}
    textarea#r32PatchCsv {{ width: 100%; min-height: 92px; border: 1px solid var(--line); border-radius: 6px; padding: 10px; background: #fff; color: var(--ink); font: 13px ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; }}
    .secondary {{ background: #f7f3eb; border-color: var(--line); color: var(--ink); }}
    .danger {{ background: #fff5f2; border-color: #d6aaa1; color: var(--danger); }}
    @media (max-width: 1100px) {{
      .app-shell {{ grid-template-columns: 1fr; }}
      .side-panel {{ position: static; height: auto; border-right: 0; border-bottom: 1px solid var(--line); }}
      .review-queue {{ grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .main-panel {{ height: auto; min-height: 100vh; }}
      .review-card, .review-card.active {{ grid-template-columns: 1fr; }}
      .decision-panel {{ border-left: 0; border-top: 1px solid var(--line); }}
      .image-panel {{ min-height: 58vh; }}
      .card-stack {{ overflow: visible; }}
    }}
    @media (max-width: 680px) {{
      .review-queue {{ grid-template-columns: 1fr; }}
      .topbar-main {{ display: grid; }}
      .tool-row {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); }}
      .zoom-control {{ grid-column: 1 / -1; justify-content: space-between; }}
      .zoom-control input {{ width: min(58vw, 220px); }}
      .decision-buttons, .source-links {{ grid-template-columns: 1fr; }}
      .image-panel {{ padding: 8px; }}
    }}
  </style>
</head>
<body>
<main class="app-shell">
  <aside class="side-panel">
    <section class="brand-block">
      <h1>Rota 42B</h1>
      <p>Revisao humana guiada para preencher a R32 com fontes Yale high-res.</p>
    </section>
    <section class="simple-guide" aria-label="Guia rapido">
      <h2>O que voce precisa fazer</h2>
      <ol class="guide-list">
        <li><b>1</b><span>Olhe o desenho das palavrinhas que aparecem no cartao.</span></li>
        <li><b>2</b><span>Procure um desenho parecido na imagem.</span></li>
        <li><b>3</b><span>Clique em Achei, Nao achei ou Nao sei. A nota aparece sozinha.</span></li>
      </ol>
    </section>
    <section class="decision-cheat" aria-label="Quando usar cada resposta">
      <strong>Como escolher:</strong>
      <span><b>Achei</b>: voce viu as palavrinhas no lugar indicado.</span>
      <span><b>Nao achei</b>: voce procurou e nao encontrou.</span>
      <span><b>Nao sei</b>: voce ficou em duvida.</span>
    </section>
    <section class="progress-block" aria-label="Progresso">
      <div class="progress-row">
        <strong id="progressText">0 de {total} decididos</strong>
        <span>{html.escape(target_csv)}</span>
      </div>
      <div class="progress-track" aria-hidden="true"><div class="progress-fill" id="progressFill"></div></div>
    </section>
    <nav id="reviewQueue" class="review-queue" aria-label="Fila de revisao">
      {queue}
    </nav>
  </aside>
  <section class="main-panel">
    <header class="topbar">
      <div class="topbar-main">
        <div>
          <h2>Faca so uma coisa por vez</h2>
          <p>Compare o desenho da palavrinha com a imagem. Clique em uma resposta. Va para o proximo item.</p>
        </div>
        <strong id="currentCounter" class="current-counter">1 de {total}</strong>
      </div>
      <div id="finishBanner" class="finish-banner" hidden>Todos os itens tem uma resposta. Confira o rascunho CSV no rodape antes de usar na R32.</div>
      <div class="tool-row" aria-label="Ferramentas da imagem">
        <button type="button" id="previousItem" class="secondary">Anterior</button>
        <button type="button" id="nextItem">Proximo</button>
        <button type="button" id="nextPendingItem">Proximo pendente</button>
        <span class="zoom-control">
          <label for="zoomSlider">Zoom</label>
          <input id="zoomSlider" type="range" min="60" max="240" step="10" value="100">
        </span>
        <button type="button" id="zoomOut" class="secondary">-</button>
        <button type="button" id="zoomIn" class="secondary">+</button>
        <button type="button" id="contrastToggle" class="secondary">Contraste</button>
        <button type="button" id="toggleLineGuide" class="secondary">Esconder zonas</button>
        <button type="button" id="lineGuideUp" class="secondary">Subir zonas</button>
        <button type="button" id="lineGuideDown" class="secondary">Descer zonas</button>
        <button type="button" id="lineGuideReset" class="secondary">Resetar zonas</button>
        <a id="openActiveTools" class="button-link" href="rota_42g_ferramentas_ativas_r32.html">Ferramentas ativas</a>
        <a id="openLineCalibration" class="button-link" href="rota_42c_calibrador_linhas_baseline_r32.html">Calibrar linhas</a>
        <a id="openOpenCvMap" class="button-link" href="rota_42e_mapa_opencv_linhas_visuais_r32.html">Mapa OpenCV</a>
        <a id="openVisualFragments" class="button-link" href="rota_42j_fragmentos_visuais_opencv_r32.html">Fragmentos</a>
        <button type="button" id="rotateLeft" class="secondary">Girar -</button>
        <button type="button" id="rotateRight" class="secondary">Girar +</button>
        <button type="button" id="resetView" class="secondary">Resetar vista</button>
      </div>
    </header>
    <section class="card-stack">
      {cards}
    </section>
    <details class="csv-drawer">
      <summary>Rascunho tecnico, usar so no final</summary>
      <div class="csv-actions">
        <div>
          <h3>Rascunho CSV</h3>
          <p>Cole estes valores na planilha R32 apenas depois de revisar tudo.</p>
        </div>
        <div class="tool-row">
          <button type="button" id="generateCsv">Atualizar CSV</button>
          <button type="button" class="danger" id="clearDraft">Limpar rascunho local</button>
        </div>
      </div>
      <textarea id="r32PatchCsv" spellcheck="false">route32_id,manual_annotation_status,manual_visual_notes</textarea>
    </details>
  </section>
</main>
<script>
const STORAGE_KEY = "{STORAGE_KEY}";
const cards = Array.from(document.querySelectorAll(".review-card"));
const queueItems = Array.from(document.querySelectorAll(".queue-item"));
const output = document.getElementById("r32PatchCsv");
const currentCounter = document.getElementById("currentCounter");
const progressText = document.getElementById("progressText");
const progressFill = document.getElementById("progressFill");
const finishBanner = document.getElementById("finishBanner");
const zoomSlider = document.getElementById("zoomSlider");
const toggleLineGuide = document.getElementById("toggleLineGuide");
let currentIndex = 0;
let viewState = {{ zoom: 100, rotate: 0, contrast: false }};
const DRAFT_ZONE_VERSION = {DRAFT_ZONE_VERSION};
const DEFAULT_LINE_GUIDE_SHIFT = 0;
const LINE_GUIDE_STEP = 12;
const LINE_GUIDE_LIMIT = 180;
let lineGuideShifts = {{}};

{VISUAL_CROP_JS}

function csvEscape(value) {{
  const text = value == null ? "" : String(value);
  if (/[",\\n\\r]/.test(text)) {{
    return '"' + text.replaceAll('"', '""') + '"';
  }}
  return text;
}}

function readDraft() {{
  try {{
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{{}}");
  }} catch (_error) {{
    return {{}};
  }}
}}

function writeDraft(draft) {{
  localStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
}}

function activeCard() {{
  return cards[currentIndex];
}}

function lineGuideShiftFor(card) {{
  const route32 = card?.dataset.route32Id || "";
  const value = Number(lineGuideShifts[route32]);
  return Number.isFinite(value) ? value : DEFAULT_LINE_GUIDE_SHIFT;
}}

function applyLineGuideShift(card = activeCard()) {{
  if (!card) return;
  card.style.setProperty("--line-guide-shift", `${{lineGuideShiftFor(card)}}px`);
}}

function setLineGuideShift(value) {{
  const card = activeCard();
  if (!card) return;
  const route32 = card.dataset.route32Id;
  lineGuideShifts[route32] = Math.max(-LINE_GUIDE_LIMIT, Math.min(LINE_GUIDE_LIMIT, value));
  applyLineGuideShift(card);
}}

function nudgeLineGuide(delta) {{
  const card = activeCard();
  if (!card) return;
  setLineGuideShift(lineGuideShiftFor(card) + delta);
}}

function applyView() {{
  const card = activeCard();
  if (!card) return;
  const imageWrap = card.querySelector(".image-wrap");
  imageWrap.style.transform = `scale(${{viewState.zoom / 100}}) rotate(${{viewState.rotate}}deg)`;
  imageWrap.style.filter = viewState.contrast ? "contrast(1.42) saturate(0.88)" : "";
  zoomSlider.value = String(viewState.zoom);
}}

function resetViewState() {{
  viewState = {{ zoom: 100, rotate: 0, contrast: false }};
  applyView();
}}

function collectDraft() {{
  const draft = {{ __zoneVersion: DRAFT_ZONE_VERSION }};
  for (const card of cards) {{
    const route32 = card.dataset.route32Id;
    draft[route32] = {{
      status: card.querySelector('[name="manual_annotation_status"]').value,
      notes: card.querySelector('[name="manual_visual_notes"]').value
    }};
  }}
  return draft;
}}

function notesHelperText(value) {{
  if (value === "annotated") return "Pronto: a ferramenta escreveu uma nota dizendo que voce achou o alvo.";
  if (value === "not_visible") return "Pronto: a ferramenta escreveu uma nota dizendo que voce nao achou o alvo.";
  if (value === "uncertain") return "Pronto: a ferramenta escreveu uma nota dizendo que voce ficou em duvida.";
  return "Clique em Achei, Nao achei ou Nao sei. A nota sera preenchida automaticamente.";
}}

function defaultNoteForStatus(card, status) {{
  const folio = card.dataset.folio || "folio";
  if (status === "annotated") return `Achei o alvo em ${{folio}} na imagem high-res. Nao fiz traducao semantica.`;
  if (status === "not_visible") return `Nao achei o alvo em ${{folio}} na imagem high-res. Nao fiz traducao semantica.`;
  if (status === "uncertain") return `Fiquei em duvida em ${{folio}}. A imagem pode ter o alvo, mas nao confirmei com seguranca. Nao fiz traducao semantica.`;
  return "Escolhi uma resposta visual. Nao fiz traducao semantica.";
}}

function syncDecisionUI(card, status) {{
  card.querySelector('[name="manual_annotation_status"]').value = status || "";
  card.querySelector("[data-notes-helper]").textContent = notesHelperText(status || "");
  for (const button of card.querySelectorAll(".decision-button")) {{
    button.classList.toggle("selected", button.dataset.value === status);
  }}
}}

function setDecision(card, value) {{
  syncDecisionUI(card, value);
  const notes = card.querySelector('[name="manual_visual_notes"]');
  if (!notes.value || notes.dataset.autoNote === "yes") {{
    notes.value = defaultNoteForStatus(card, value);
    notes.dataset.autoNote = "yes";
  }}
  generateCsv();
  updateProgress();
}}

function restoreDraft() {{
  const draft = readDraft();
  for (const card of cards) {{
    const route32 = card.dataset.route32Id;
    const item = draft[route32] || {{}};
    const status = item.status || "";
    lineGuideShifts[route32] = DEFAULT_LINE_GUIDE_SHIFT;
    applyLineGuideShift(card);
    card.querySelector('[name="manual_visual_notes"]').value = item.notes || "";
    syncDecisionUI(card, status);
  }}
}}

function statusLabel(value) {{
  if (value === "annotated") return "anotado";
  if (value === "not_visible") return "nao visivel";
  if (value === "uncertain") return "incerto";
  return "pendente";
}}

function updateProgress() {{
  let decided = 0;
  for (const [index, card] of cards.entries()) {{
    const status = card.querySelector('[name="manual_annotation_status"]').value;
    if (status) decided += 1;
    queueItems[index].classList.toggle("done", Boolean(status));
    queueItems[index].querySelector("[data-status-label]").textContent = statusLabel(status);
  }}
  progressText.textContent = `${{decided}} de ${{cards.length}} decididos`;
  progressFill.style.width = cards.length ? `${{Math.round((decided / cards.length) * 100)}}%` : "0%";
  finishBanner.hidden = decided !== cards.length;
}}

function generateCsv() {{
  const draft = collectDraft();
  writeDraft(draft);
  const lines = ["route32_id,manual_annotation_status,manual_visual_notes"];
  for (const card of cards) {{
    const route32 = card.dataset.route32Id;
    const item = draft[route32] || {{}};
    lines.push([route32, item.status || "", item.notes || ""].map(csvEscape).join(","));
  }}
  output.value = lines.join("\\n");
}}

function showItem(index) {{
  if (!cards.length) return;
  currentIndex = Math.max(0, Math.min(cards.length - 1, index));
  for (const [cardIndex, card] of cards.entries()) {{
    card.classList.toggle("active", cardIndex === currentIndex);
  }}
  for (const [itemIndex, item] of queueItems.entries()) {{
    item.classList.toggle("active", itemIndex === currentIndex);
  }}
  currentCounter.textContent = `${{currentIndex + 1}} de ${{cards.length}}`;
  resetViewState();
  applyLineGuideShift();
  paintCropPreviews(activeCard());
}}

function showNextPending() {{
  if (!cards.length) return;
  for (let offset = 1; offset <= cards.length; offset += 1) {{
    const index = (currentIndex + offset) % cards.length;
    const status = cards[index].querySelector('[name="manual_annotation_status"]').value;
    if (!status) {{
      showItem(index);
      return;
    }}
  }}
}}

for (const [index, item] of queueItems.entries()) {{
  item.addEventListener("click", () => showItem(index));
}}

for (const card of cards) {{
  for (const button of card.querySelectorAll(".decision-button")) {{
    button.addEventListener("click", () => setDecision(card, button.dataset.value));
  }}
  card.querySelector('[name="manual_visual_notes"]').addEventListener("input", () => {{
    card.querySelector('[name="manual_visual_notes"]').dataset.autoNote = "no";
    generateCsv();
    updateProgress();
  }});
  card.querySelector("[data-fill-note]").addEventListener("click", () => {{
    const status = card.querySelector('[name="manual_annotation_status"]').value;
    const helper = card.querySelector("[data-notes-helper]");
    if (!status) {{
      helper.textContent = "Escolha uma das tres respostas antes de preencher a nota simples.";
      return;
    }}
    const notes = card.querySelector('[name="manual_visual_notes"]');
    notes.value = defaultNoteForStatus(card, status);
    notes.dataset.autoNote = "yes";
    generateCsv();
    updateProgress();
  }});
}}

document.getElementById("previousItem").addEventListener("click", () => showItem(currentIndex - 1));
document.getElementById("nextItem").addEventListener("click", () => showItem(currentIndex + 1));
document.getElementById("nextPendingItem").addEventListener("click", showNextPending);
zoomSlider.addEventListener("input", () => {{
  viewState.zoom = Number(zoomSlider.value);
  applyView();
}});
document.getElementById("zoomOut").addEventListener("click", () => {{
  viewState.zoom = Math.max(60, viewState.zoom - 10);
  applyView();
}});
document.getElementById("zoomIn").addEventListener("click", () => {{
  viewState.zoom = Math.min(240, viewState.zoom + 10);
  applyView();
}});
document.getElementById("contrastToggle").addEventListener("click", () => {{
  viewState.contrast = !viewState.contrast;
  applyView();
}});
toggleLineGuide.addEventListener("click", () => {{
  document.body.classList.toggle("hide-line-guides");
  toggleLineGuide.textContent = document.body.classList.contains("hide-line-guides")
    ? "Mostrar zonas"
    : "Esconder zonas";
}});
document.getElementById("lineGuideUp").addEventListener("click", () => nudgeLineGuide(-LINE_GUIDE_STEP));
document.getElementById("lineGuideDown").addEventListener("click", () => nudgeLineGuide(LINE_GUIDE_STEP));
document.getElementById("lineGuideReset").addEventListener("click", () => setLineGuideShift(DEFAULT_LINE_GUIDE_SHIFT));
document.getElementById("rotateLeft").addEventListener("click", () => {{
  viewState.rotate -= 90;
  applyView();
}});
document.getElementById("rotateRight").addEventListener("click", () => {{
  viewState.rotate += 90;
  applyView();
}});
document.getElementById("resetView").addEventListener("click", resetViewState);
document.getElementById("generateCsv").addEventListener("click", generateCsv);
document.getElementById("clearDraft").addEventListener("click", () => {{
  localStorage.removeItem(STORAGE_KEY);
  lineGuideShifts = {{}};
  for (const card of cards) {{
    card.querySelector('[name="manual_visual_notes"]').value = "";
    card.querySelector('[name="manual_visual_notes"]').dataset.autoNote = "";
    lineGuideShifts[card.dataset.route32Id] = DEFAULT_LINE_GUIDE_SHIFT;
    applyLineGuideShift(card);
    syncDecisionUI(card, "");
  }}
  generateCsv();
  updateProgress();
}});
restoreDraft();
updateProgress();
showItem(0);
generateCsv();
</script>
</body>
</html>
"""


def write_markdown_report(
    path: Path,
    rows: list[dict[str, str]],
    highres_csv: Path,
    assist_csv: Path,
    output_csv: Path,
    summary_csv: Path,
    html_path: Path,
    target_csv: str,
) -> None:
    summary = summarize_fill_html_rows(rows)
    lines = [
        "# Rota 42B: ferramenta guiada de preenchimento humano R32 high-res",
        "",
        "Esta rota cria um HTML estatico e guiado para preencher manualmente a R32 usando as imagens Yale/Beinecke high-res da R42, a orientacao assistida da R42A e, quando disponiveis, as baselines calibradas da R42C. A ferramenta mostra um item por vez e reduz a decisao para `Achei`, `Nao achei` ou `Nao sei`. Ela oferece zoom, contraste, rotacao, fila de revisao, guia rapido, alvo simplificado por tokens/linhas, total de entradas/loci ZL3b por folio, lista auditavel das entradas que originam esse total, texto de referencia das linhas alvo, cartoes visuais EVA para comparar o desenho da palavra com a imagem, recortes reais da pagina para olhar primeiro, baselines calibradas ou zonas visuais provaveis dos blocos alvo, nota automatica acionada pelo clique do revisor, detalhes tecnicos recolhidos e rascunho CSV escondido ate o final. O HTML nao grava a planilha R32 e nao cria evidencia visual sozinho; ajustes visuais de zona sao temporarios e voltam ao mapa calibrado ao recarregar.",
        "",
        f"Fontes R42: `{highres_csv}`.",
        f"Orientacao R42A: `{assist_csv}`.",
        f"Alvo humano: `{target_csv}`.",
        f"CSV R42B: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        f"HTML: `{html_path}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens de revisao guiada: {len(rows)};",
        f"- primeiro bloco claro: {summary['review_group'].get('first_clear_regions', 0)};",
        f"- bloco intermediario parcial: {summary['review_group'].get('middle_partial_regions', 0)};",
        f"- fonte apagada: {summary['review_group'].get('faint_source', 0)};",
        f"- paginas compostas finais: {summary['review_group'].get('last_composite_pages', 0)};",
        "- controles: fila lateral, item ativo, proximo pendente, zoom, contraste, rotacao, mostrar/esconder zonas, subir/descer zonas, reset de vista e atalho para calibrar linhas na R42C;",
        "- modo ultrassimples: guia rapido, pergunta `Voce achou essas palavrinhas?`, cartoes visuais EVA, recortes reais da pagina, total de entradas/loci ZL3b por folio, lista auditavel das entradas que originam o total, texto de referencia das linhas alvo, baselines calibradas quando R42C estiver preenchida, zonas provaveis quando a linha ainda estiver pendente, botoes `Achei`/`Nao achei`/`Nao sei`, nota automatica e detalhes tecnicos recolhidos;",
        "- observacao: as baselines R42C sao apoio operacional de localizacao, nao evidencia automatica; quando uma baseline ainda nao existe, as zonas visuais continuam sendo orientacao aproximada de bloco, nao linha exata ou coordenada exata; a ferramenta nao calcula posicao visual por proporcao da numeracao ZL3b; o total por folio segue entradas/loci ZL3b e nao e uma contagem visual direta da imagem; deslocamentos de zona nao sao gravados no rascunho local para manter recarga idempotente;",
        "- campos gerados: `manual_annotation_status` e `manual_visual_notes`;",
        f"- guarda: `{GUARDRAIL}`.",
        "",
    ]
    lines.extend(render_counts("Grupos de revisao", summary["review_group"]))
    lines.extend(render_counts("Qualidade assistida", summary["image_quality_assist"]))
    lines.extend(render_counts("Regiao assistida", summary["target_region_locatable_assist"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota42B|rota32|folio|grupo|qualidade|acao sugerida|",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['route42b_id']}|{row['route32_id']}|{row['folio']}|{row['review_group']}|{row['image_quality_assist']}|{row['suggested_manual_review_action']}|"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--highres-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_highres_sources_zl3b.csv"),
        help="Route 42 high-resolution source CSV",
    )
    parser.add_argument(
        "--assist-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_highres_ai_assist_zl3b.csv"),
        help="Route 42A AI-assisted review CSV",
    )
    parser.add_argument(
        "--target-csv",
        default="data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv",
        help="Manual route 32 CSV target, relative to project root",
    )
    parser.add_argument(
        "--line-calibration-csv",
        default=str(LINE_CALIBRATION_CSV),
        help="Route 42C manual baseline calibration CSV; calibrated rows refine the visual overlay",
    )
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_highres_human_fill_html_zl3b.csv"),
        help="Route 42B derived CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_highres_human_fill_html_summary_zl3b.csv"),
        help="Route 42B summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_42b_preenchimento_humano_highres_r32.md"),
        help="Route 42B Markdown report output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_42b_pacote_html_preenchimento_humano_r32.html"),
        help="Route 42B HTML output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    validate_visual_zone_overrides()
    highres_csv = Path(args.highres_csv)
    assist_csv = Path(args.assist_csv)
    line_calibration_csv = Path(args.line_calibration_csv)
    output_csv = Path(args.csv)
    summary_csv = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)
    rows = build_fill_html_rows(
        read_csv(highres_csv),
        read_csv(assist_csv),
        args.target_csv,
        read_optional_csv(line_calibration_csv),
    )
    summary = summarize_fill_html_rows(rows)
    write_csv(output_csv, rows, FIELDNAMES)
    write_summary_csv(summary_csv, summary)
    write_markdown_report(md_path, rows, highres_csv, assist_csv, output_csv, summary_csv, html_path, args.target_csv)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_html(rows, args.target_csv), encoding="utf-8")
    print(
        f"fill_html_items={len(rows)} "
        f"first_clear={summary['review_group'].get('first_clear_regions', 0)} "
        f"middle_partial={summary['review_group'].get('middle_partial_regions', 0)} "
        f"faint={summary['review_group'].get('faint_source', 0)} "
        f"composite={summary['review_group'].get('last_composite_pages', 0)}"
    )
    print(f"csv={output_csv.resolve()}")
    print(f"summary_csv={summary_csv.resolve()}")
    print(f"md={md_path.resolve()}")
    print(f"html={html_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
