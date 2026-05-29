#!/usr/bin/env python3
"""Prepare OpenCV-assisted initial line-baseline suggestions for route 42C."""
from __future__ import annotations

import argparse
import csv
import html
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "opencv_initial_line_suggestion_not_visual_evidence"

FIELDNAMES = [
    "route42d_id",
    "route42c_id",
    "route42b_id",
    "route32_id",
    "folio",
    "target_locus",
    "line_number",
    "local_image_path",
    "suggestion_status",
    "suggested_visual_line_number",
    "suggested_baseline_points",
    "suggested_band_box_pct",
    "suggestion_confidence",
    "candidate_count",
    "opencv_auto_action",
    "automation_confidence_band",
    "human_next_step",
    "calibration_status_to_apply",
    "algorithm_notes",
    "semantic_guardrail",
]


try:
    from scripts.prepare_ready_visual_annotation_highres_human_fill_html import VISUAL_ZONE_OVERRIDES
    from scripts.visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS, parse_box_pct, render_crop_canvas
except ImportError:  # pragma: no cover - used when running this file directly from scripts/
    from prepare_ready_visual_annotation_highres_human_fill_html import VISUAL_ZONE_OVERRIDES
    from visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS, parse_box_pct, render_crop_canvas


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_summary_csv(path: Path, rows: list[dict[str, str]]) -> None:
    counts = {
        "suggestion_status": Counter(row.get("suggestion_status", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
        "opencv_auto_action": Counter(row.get("opencv_auto_action", "") for row in rows),
        "automation_confidence_band": Counter(row.get("automation_confidence_band", "") for row in rows),
        "semantic_guardrail": Counter(row.get("semantic_guardrail", "") for row in rows),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "item", "n"])
        writer.writeheader()
        for metric, counter in counts.items():
            for item, n in sorted(counter.items(), key=lambda pair: (-pair[1], pair[0])):
                writer.writerow({"metric": metric, "item": item, "n": n})


def resolve_project_path(path_value: str) -> Path:
    path = Path(path_value)
    return path if path.is_absolute() else ROOT / path


def html_image_src(local_image_path: str) -> str:
    return "../../" + local_image_path.lstrip("/") if local_image_path else ""


def optional_cv2():
    try:
        import cv2  # type: ignore
        import numpy as np  # type: ignore
    except ImportError:
        return None, None
    return cv2, np


def band_box_text(band: dict[str, float]) -> str:
    return f'{band["x1"]:.2f},{band["y1"]:.2f},{band["x2"]:.2f},{band["y2"]:.2f}'


def baseline_from_band(band: dict[str, float]) -> str:
    y = band["y2"]
    return f'{band["x1"]:.2f},{y:.2f} {band["x2"]:.2f},{y:.2f}'


def parse_zone_box_pct(value: str) -> tuple[float, float, float, float] | None:
    parts = value.split(",")
    if len(parts) != 4:
        return None
    try:
        left, top, right, bottom = [float(part) for part in parts]
    except ValueError:
        return None
    if not (0 <= left <= 100 and 0 <= right <= 100 and 0 <= top <= 100 and 0 <= bottom <= 100):
        return None
    if right <= left or bottom <= top:
        return None
    return left, top, right, bottom


def zone_choices_to_visual_zones(rows: list[dict[str, str]]) -> dict[str, dict[str, float | str]]:
    zones: dict[str, dict[str, float | str]] = {}
    for row in rows:
        if row.get("zone_status") != "zone_selected_pending_opencv":
            continue
        target_locus = row.get("target_locus", "")
        visual_line = row.get("selected_visual_line_number", "")
        box = parse_zone_box_pct(row.get("selected_zone_box_pct", ""))
        if not target_locus or not visual_line or not box:
            continue
        left, top, right, bottom = box
        zones[target_locus] = {
            "top": top,
            "left": left,
            "width": round(right - left, 2),
            "height": round(bottom - top, 2),
            "label": f"linha visual OpenCV {visual_line} escolhida na R42F",
        }
    return zones


def confidence_band(value: float | str) -> str:
    try:
        confidence = float(value)
    except (TypeError, ValueError):
        return ""
    if confidence >= 0.65:
        return "alta"
    if confidence >= 0.40:
        return "media"
    if confidence > 0:
        return "baixa"
    return ""


def fragment_width(fragment: dict[str, float]) -> float:
    return max(0.0, float(fragment["x2"]) - float(fragment["x1"]))


def cluster_fragments_by_horizontal_gap(
    fragments: list[dict[str, float]],
    max_gap_pct: float = 18.0,
) -> list[list[dict[str, float]]]:
    clusters: list[list[dict[str, float]]] = []
    current: list[dict[str, float]] = []
    current_right = 0.0
    for fragment in sorted(fragments, key=lambda item: (float(item["x1"]), float(item["x2"]))):
        if current and float(fragment["x1"]) - current_right > max_gap_pct:
            clusters.append(current)
            current = []
        current.append(fragment)
        current_right = max(current_right, float(fragment["x2"]))
    if current:
        clusters.append(current)
    return clusters


def select_main_text_cluster(fragments: list[dict[str, float]]) -> list[dict[str, float]]:
    clusters = cluster_fragments_by_horizontal_gap(fragments)
    if not clusters:
        return []

    def score(cluster: list[dict[str, float]]) -> tuple[float, float, float]:
        x1 = min(float(fragment["x1"]) for fragment in cluster)
        x2 = max(float(fragment["x2"]) for fragment in cluster)
        ink_width = sum(fragment_width(fragment) for fragment in cluster)
        edge_penalty = 0.0
        if x1 < 3.0 or x2 > 92.0:
            edge_penalty += 10.0
        if len(cluster) == 1 and (x1 < 5.0 or x2 > 88.0):
            edge_penalty += 10.0
        return (ink_width - edge_penalty, float(len(cluster)), x2 - x1)

    return max(clusters, key=score)


def build_visual_line_from_fragments(fragments: list[dict[str, float]]) -> dict[str, float]:
    return {
        "x1": min(float(fragment["x1"]) for fragment in fragments),
        "y1": min(float(fragment["y1"]) for fragment in fragments),
        "x2": max(float(fragment["x2"]) for fragment in fragments),
        "y2": max(float(fragment["y2"]) for fragment in fragments),
        "confidence": sum(float(fragment.get("confidence", 0.0)) for fragment in fragments) / len(fragments),
    }


def is_probable_page_border_noise(line: dict[str, float]) -> bool:
    width = float(line["x2"]) - float(line["x1"])
    if width < 3.0:
        return True
    if width >= 82.0 and float(line["y1"]) <= 8.0:
        return True
    if width >= 35.0 and float(line["y1"]) >= 94.0:
        return True
    if float(line["x1"]) >= 84.0 and width <= 8.0:
        return True
    return False


def merge_bands_into_visual_lines(
    bands: list[dict[str, float]],
    y_tolerance_pct: float = 1.4,
) -> list[dict[str, float]]:
    groups: list[dict[str, object]] = []
    for band in sorted(bands, key=lambda item: ((item["y1"] + item["y2"]) / 2, item["x1"])):
        center_y = (float(band["y1"]) + float(band["y2"])) / 2
        if groups and abs(center_y - float(groups[-1]["center_y"])) <= y_tolerance_pct:
            group = groups[-1]
            fragments = group["fragments"]
            assert isinstance(fragments, list)
            fragments.append({key: float(value) for key, value in band.items()})
            count = len(fragments)
            group["center_y"] = ((float(group["center_y"]) * (count - 1)) + center_y) / count
            group["fragment_count"] = float(count)
            continue
        groups.append(
            {
                "center_y": center_y,
                "fragment_count": 1.0,
                "fragments": [{key: float(value) for key, value in band.items()}],
            }
        )

    visual_lines: list[dict[str, float]] = []
    for group in groups:
        fragments = group["fragments"]
        assert isinstance(fragments, list)
        main_cluster = select_main_text_cluster(fragments)
        if not main_cluster:
            continue
        line = build_visual_line_from_fragments(main_cluster)
        if is_probable_page_border_noise(line):
            continue
        visual_lines.append(line)
    for index, line in enumerate(visual_lines, start=1):
        line["visual_line_number"] = str(index)
    return visual_lines


def choose_band_for_zone(
    bands: list[dict[str, float]],
    zone: dict[str, float],
) -> dict[str, float] | None:
    zone_x1 = float(zone["left"])
    zone_y1 = float(zone["top"])
    zone_x2 = zone_x1 + float(zone["width"])
    zone_y2 = zone_y1 + float(zone["height"])
    zone_cy = (zone_y1 + zone_y2) / 2

    ranked: list[tuple[float, dict[str, float]]] = []
    for band in bands:
        cx = (band["x1"] + band["x2"]) / 2
        cy = (band["y1"] + band["y2"]) / 2
        if not (zone_x1 <= cx <= zone_x2 and zone_y1 <= cy <= zone_y2):
            continue
        vertical_distance = abs(cy - zone_cy)
        confidence = float(band.get("confidence", 0.0))
        score = confidence - (vertical_distance / max(float(zone["height"]), 1.0))
        ranked.append((score, band))
    if not ranked:
        return None
    ranked.sort(key=lambda item: item[0], reverse=True)
    return ranked[0][1]


def detect_text_bands_with_opencv(image_path: Path) -> list[dict[str, float]]:
    cv2, _np = optional_cv2()
    if cv2 is None:
        return []
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        return []

    height, width = image.shape[:2]
    max_width = 1500
    scale = min(1.0, max_width / max(width, 1))
    if scale < 1.0:
        image = cv2.resize(image, (int(width * scale), int(height * scale)), interpolation=cv2.INTER_AREA)
    height, width = image.shape[:2]

    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    _threshold, mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(12, width // 90), 2))
    connected = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_kernel)
    connected = cv2.dilate(
        connected,
        cv2.getStructuringElement(cv2.MORPH_RECT, (max(4, width // 260), 2)),
        iterations=1,
    )
    contours, _hierarchy = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    bands: list[dict[str, float]] = []
    page_area = width * height
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w < width * 0.018 or h < 3 or h > height * 0.045:
            continue
        if w * h > page_area * 0.035:
            continue
        aspect = w / max(h, 1)
        if aspect < 2.0:
            continue
        x1 = (x / width) * 100
        y1 = (y / height) * 100
        x2 = ((x + w) / width) * 100
        y2 = ((y + h) / height) * 100
        width_pct = x2 - x1
        confidence = min(0.95, 0.30 + min(aspect, 18.0) / 40 + min(width_pct, 70.0) / 180)
        bands.append(
            {
                "x1": x1,
                "y1": y1,
                "x2": x2,
                "y2": y2,
                "confidence": confidence,
            }
        )
    return merge_bands_into_visual_lines(bands)[:120]


def detect_bands_by_image(calibration_rows: list[dict[str, str]]) -> tuple[dict[str, list[dict[str, float]]], bool]:
    cv2, _np = optional_cv2()
    if cv2 is None:
        return {}, False
    output: dict[str, list[dict[str, float]]] = {}
    for image_path in sorted({row.get("local_image_path", "") for row in calibration_rows if row.get("local_image_path")}):
        output[image_path] = detect_text_bands_with_opencv(resolve_project_path(image_path))
    return output, True


def build_suggestion_rows(
    calibration_rows: list[dict[str, str]],
    image_bands: dict[str, list[dict[str, float]]],
    visual_zones: dict[str, dict[str, float]],
    cv2_available: bool,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source in calibration_rows:
        target_locus = source.get("target_locus", "")
        image_path = source.get("local_image_path", "")
        bands = image_bands.get(image_path, [])
        zone = visual_zones.get(target_locus)
        chosen = choose_band_for_zone(bands, zone) if zone and bands else None

        status = "opencv_unavailable"
        notes = "OpenCV/NumPy nao disponiveis neste ambiente."
        auto_action = "opencv_unavailable"
        automation_band = "indisponivel"
        human_next_step = "instalar OpenCV/NumPy ou calibrar manualmente"
        if cv2_available:
            if source.get("calibration_status") == "calibrated" and source.get("baseline_points"):
                status = "manual_calibration_already_exists"
                notes = "Baseline manual existente preservada; OpenCV nao deve sobrescrever."
                auto_action = "manual_already_done"
                automation_band = "manual"
                human_next_step = "nenhuma acao; manter a baseline manual"
            elif not bands:
                status = "no_text_band_detected"
                notes = "OpenCV nao encontrou uma faixa de texto confiavel para esta imagem."
                auto_action = "needs_better_scan_or_manual_line"
                automation_band = "sem_texto"
                human_next_step = "calibrar a linha manualmente ou revisar a imagem/filtro"
            elif not zone:
                status = "opencv_candidates_detected_needs_manual_zone"
                notes = "OpenCV encontrou faixas na imagem, mas o alvo ainda nao tem zona manual de bloco."
                auto_action = "needs_manual_zone"
                automation_band = "sem_mapeamento"
                human_next_step = "desenhar uma zona simples para o alvo antes de pedir baseline"
            elif chosen:
                status = "opencv_suggested_needs_human_confirmation"
                zone_label = str(zone.get("label", "")) if zone else ""
                zone_source = "zona escolhida na R42F" if "R42F" in zone_label else "zona manual"
                notes = (
                    f"OpenCV pode pre-preencher a baseline como rascunho dentro da {zone_source}; "
                    "confirmar na R42C antes de aceitar."
                )
                auto_action = "prefill_pending_baseline"
                automation_band = confidence_band(chosen.get("confidence", 0.0))
                human_next_step = "conferir se a linha acompanha o texto e marcar calibrada se estiver certa"
            else:
                status = "opencv_candidates_detected_no_zone_match"
                notes = "OpenCV encontrou faixas, mas nenhuma caiu dentro da zona manual do alvo."
                auto_action = "needs_human_line_choice"
                automation_band = "sem_correspondencia"
                human_next_step = "ajustar a zona ou escolher a linha manualmente"

        rows.append(
            {
                "route42d_id": f"R42D-{len(rows) + 1:03d}",
                "route42c_id": source.get("route42c_id", ""),
                "route42b_id": source.get("route42b_id", ""),
                "route32_id": source.get("route32_id", ""),
                "folio": source.get("folio", ""),
                "target_locus": target_locus,
                "line_number": source.get("line_number", ""),
                "local_image_path": image_path,
                "suggestion_status": status,
                "suggested_visual_line_number": str(chosen.get("visual_line_number", "")) if chosen else "",
                "suggested_baseline_points": baseline_from_band(chosen) if chosen else "",
                "suggested_band_box_pct": band_box_text(chosen) if chosen else "",
                "suggestion_confidence": f'{chosen.get("confidence", 0.0):.2f}' if chosen else "",
                "candidate_count": str(len(bands)),
                "opencv_auto_action": auto_action,
                "automation_confidence_band": automation_band,
                "human_next_step": human_next_step,
                "calibration_status_to_apply": "pending_calibration",
                "algorithm_notes": notes,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def render_html(rows: list[dict[str, str]], suggestions_csv: str) -> str:
    auto_action_counts = Counter(row.get("opencv_auto_action", "") for row in rows)
    auto_summary = "".join(
        f"<span><b>{html.escape(action or 'sem_acao')}</b>: {count}</span>"
        for action, count in sorted(auto_action_counts.items(), key=lambda pair: (-pair[1], pair[0]))
    )
    cards = []
    for row in rows:
        visual_line = row.get("suggested_visual_line_number", "")
        visual_line_text = f"linha visual {html.escape(visual_line)}" if visual_line else "sem linha visual associada"
        crop = render_crop_canvas(
            html_image_src(row.get("local_image_path", "")),
            parse_box_pct(row.get("suggested_band_box_pct", "")),
            "Recorte real",
            note="linha sugerida pelo OpenCV",
            class_name="suggestion-crop",
        )
        cards.append(
            "<tr>"
            f"<td>{html.escape(row['route42d_id'])}</td>"
            f"<td>{html.escape(row['target_locus'])}</td>"
            f"<td>{visual_line_text}</td>"
            f"<td>{crop or 'sem recorte'}</td>"
            f"<td>{html.escape(row['suggestion_status'])}</td>"
            f"<td><code>{html.escape(row['suggested_baseline_points'])}</code></td>"
            f"<td>{html.escape(row['suggestion_confidence'])}</td>"
            f"<td>{html.escape(row.get('opencv_auto_action', ''))}</td>"
            f"<td>{html.escape(row.get('automation_confidence_band', ''))}</td>"
            f"<td>{html.escape(row.get('human_next_step', ''))}</td>"
            f"<td>{html.escape(row['algorithm_notes'])}</td>"
            "</tr>"
        )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rota 42D - sugestoes OpenCV para linhas</title>
  <style>
    body {{ margin: 0; background: #f6f0e7; color: #201a16; font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 24px; }}
    h1 {{ margin: 0 0 6px; font-size: 26px; }}
    p {{ color: #665d55; }}
    a {{ color: #17625c; font-weight: 700; }}
    nav {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 14px 0; }}
    .button-link {{ border: 1px solid #c8baaa; border-radius: 7px; background: #fffaf2; color: #201a16; padding: 8px 11px; font-weight: 800; text-decoration: none; }}
    .notice {{ margin: 16px 0; padding: 12px; border: 1px solid #cdbdaa; border-radius: 8px; background: #fffaf2; }}
    .auto-summary {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 12px 0; }}
    .auto-summary span {{ border: 1px solid #c8baaa; border-radius: 999px; background: #eef6f2; color: #164f47; padding: 6px 10px; font-weight: 800; }}
    table {{ width: 100%; border-collapse: collapse; background: #fffdf8; border: 1px solid #d6cab8; }}
    th, td {{ padding: 8px; border-bottom: 1px solid #e3d8c8; text-align: left; vertical-align: top; }}
    th {{ background: #eee4d5; font-size: 12px; text-transform: uppercase; }}
    code {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; overflow-wrap: anywhere; }}
{VISUAL_CROP_CSS}
    .suggestion-crop {{ min-width: 220px; padding: 6px; }}
    .suggestion-crop .visual-crop-canvas {{ min-height: 52px; }}
  </style>
</head>
<body>
<main>
  <h1>Rota 42D</h1>
  <p>Esta tela nao e palavra encontrada. Ela mostra quando uma linha visual OpenCV parece cair dentro da zona de um alvo ZL3b. A R42C pode mesclar a sugestao como rascunho pendente, mas ela nao preenche a R32 e nao vira calibracao sem confirmacao humana.</p>
  <nav aria-label="Navegacao entre rotas">
    <a class="button-link" href="rota_42g_ferramentas_ativas_r32.html">Ferramentas ativas</a>
    <a class="button-link" href="rota_42b_pacote_html_preenchimento_humano_r32.html">Abrir R42B</a>
    <a class="button-link" href="rota_42c_calibrador_linhas_baseline_r32.html">Abrir R42C</a>
    <a class="button-link" href="rota_42e_mapa_opencv_linhas_visuais_r32.html">Abrir R42E</a>
    <a class="button-link" href="rota_42j_fragmentos_visuais_opencv_r32.html">Abrir R42J</a>
    <a class="button-link" href="rota_42f_escolha_linhas_visuais_sem_zona_r32.html">Abrir R42F</a>
  </nav>
  <section class="notice">
    <strong>Guarda:</strong> <code>{GUARDRAIL}</code><br>
    <strong>CSV:</strong> <code>{html.escape(suggestions_csv)}</code>
  </section>
  <section class="notice">
    <strong>O que o OpenCV resolveu sozinho:</strong>
    <div class="auto-summary">{auto_summary}</div>
    <p>Mesmo quando aparece <code>prefill_pending_baseline</code>, isso e so rascunho operacional. A pessoa ainda confirma a linha na R42C.</p>
  </section>
  <table>
    <thead><tr><th>ID</th><th>Alvo ZL3b</th><th>Linha visual</th><th>Recorte real</th><th>Status</th><th>Baseline sugerida</th><th>Conf.</th><th>Acao OpenCV</th><th>Faixa</th><th>Proximo passo humano</th><th>Notas</th></tr></thead>
    <tbody>{''.join(cards)}</tbody>
  </table>
</main>
<script>
{VISUAL_CROP_JS}
paintCropPreviews();
</script>
</body>
</html>"""


def write_markdown_report(
    path: Path,
    rows: list[dict[str, str]],
    suggestions_csv: Path,
    summary_csv: Path,
    html_path: Path,
) -> None:
    status_counts = Counter(row.get("suggestion_status", "") for row in rows)
    auto_action_counts = Counter(row.get("opencv_auto_action", "") for row in rows)
    lines = [
        "# Rota 42D: sugestoes OpenCV para calibracao inicial de linhas",
        "",
        "Esta rota usa OpenCV para detectar faixas de tinta/texto nas imagens high-res e gerar sugestoes iniciais de baseline para a R42C.",
        "",
        "As sugestoes nao sao evidencia visual, nao traduzem, nao preenchem a R32 e nao mudam a R42C para `calibrated`.",
        "Quando a R42C e reexecutada depois da R42D, sugestoes validas podem ser mescladas como `baseline_points` pendentes para revisao humana.",
        "Quando a R42F tiver escolhas de linha visual, a R42D tambem consome essas zonas pequenas para gerar novas sugestoes pendentes.",
        "A pagina HTML mostra recorte real da linha sugerida quando a sugestao tem caixa visual, para diminuir a dependencia de codigo textual.",
        "",
        f"CSV: `{suggestions_csv}`.",
        f"Resumo: `{summary_csv}`.",
        f"HTML: `{html_path}`.",
        "",
        "## Status",
        "",
        "|status|n|",
        "|---|---:|",
    ]
    for status, n in sorted(status_counts.items(), key=lambda pair: (-pair[1], pair[0])):
        lines.append(f"|{status}|{n}|")
    lines.extend(
        [
            "",
            "## O que o OpenCV resolveu sozinho",
            "",
            "|acao automatica|n|",
            "|---|---:|",
        ]
    )
    for action, n in sorted(auto_action_counts.items(), key=lambda pair: (-pair[1], pair[0])):
        lines.append(f"|{action}|{n}|")
    ready_rows = [row for row in rows if row.get("suggestion_status") == "opencv_suggested_needs_human_confirmation"]
    if ready_rows:
        lines.extend(
            [
                "",
                "## Sugestoes prontas para conferir na R42C",
                "",
                "|alvo ZL3b|linha visual OpenCV|baseline sugerida|confianca|acao OpenCV|proximo passo humano|",
                "|---|---:|---|---:|---|---|",
            ]
        )
        for row in ready_rows:
            lines.append(
                f"|{row.get('target_locus', '')}|{row.get('suggested_visual_line_number', '')}|"
                f"`{row.get('suggested_baseline_points', '')}`|{row.get('suggestion_confidence', '')}|"
                f"{row.get('opencv_auto_action', '')}|{row.get('human_next_step', '')}|"
            )
    lines.extend(
        [
            "",
            f"Guarda: `{GUARDRAIL}`.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--calibration-csv",
        default=str(ROOT / "data" / "annotations" / "ready_visual_line_calibration_zl3b.csv"),
        help="Route 42C calibration CSV",
    )
    parser.add_argument(
        "--suggestions-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_line_opencv_suggestions_zl3b.csv"),
        help="OpenCV suggestion CSV output",
    )
    parser.add_argument(
        "--zone-choice-csv",
        default=str(ROOT / "data" / "annotations" / "ready_visual_line_zone_choice_zl3b.csv"),
        help="Route 42F selected visual-line zones CSV",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_line_opencv_suggestions_summary_zl3b.csv"),
        help="OpenCV suggestion summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_42d_sugestoes_opencv_linhas_r32.md"),
        help="Route 42D Markdown report output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_42d_sugestoes_opencv_linhas_r32.html"),
        help="Route 42D HTML report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    calibration_csv = Path(args.calibration_csv)
    suggestions_csv = Path(args.suggestions_csv)
    zone_choice_csv = Path(args.zone_choice_csv)
    summary_csv = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)

    calibration_rows = read_csv(calibration_csv)
    bands_by_image, cv2_available = detect_bands_by_image(calibration_rows)
    visual_zones = dict(VISUAL_ZONE_OVERRIDES)
    visual_zones.update(zone_choices_to_visual_zones(read_csv(zone_choice_csv)))
    rows = build_suggestion_rows(calibration_rows, bands_by_image, visual_zones, cv2_available)

    write_csv(suggestions_csv, rows, FIELDNAMES)
    write_summary_csv(summary_csv, rows)
    write_markdown_report(md_path, rows, suggestions_csv, summary_csv, html_path)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_html(rows, str(suggestions_csv)), encoding="utf-8")

    counts = Counter(row.get("suggestion_status", "") for row in rows)
    print(
        f"opencv_available={int(cv2_available)} "
        f"suggestion_rows={len(rows)} "
        f"suggested={counts.get('opencv_suggested_needs_human_confirmation', 0)} "
        f"needs_manual_zone={counts.get('opencv_candidates_detected_needs_manual_zone', 0)}"
    )
    print(f"suggestions_csv={suggestions_csv.resolve()}")
    print(f"summary_csv={summary_csv.resolve()}")
    print(f"md={md_path.resolve()}")
    print(f"html={html_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
