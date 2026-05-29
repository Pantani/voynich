#!/usr/bin/env python3
"""Prepare a finer OpenCV map of visual word-like fragments inside visual lines."""
from __future__ import annotations

import argparse
import csv
import html
import json
from collections import Counter
from pathlib import Path

try:
    from scripts.visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS, box_text, parse_box_pct
except ImportError:  # pragma: no cover - used when running this file directly from scripts/
    from visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS, box_text, parse_box_pct

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "opencv_visual_fragment_map_not_ocr_or_word_evidence"

FIELDNAMES = [
    "route42j_id",
    "route42e_id",
    "image_id",
    "folio_labels",
    "local_image_path",
    "visual_line_number",
    "visual_word_number",
    "word_box_pct",
    "crop_box_pct",
    "center_x_pct",
    "center_y_pct",
    "confidence",
    "source_line_box_pct",
    "target_loci_on_image",
    "word_map_status",
    "semantic_guardrail",
]


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


def write_summary_csv(path: Path, rows: list[dict[str, str]], cv2_available: bool) -> None:
    counts = {
        "opencv_available": Counter({"yes" if cv2_available else "no": 1}),
        "visual_fragment_count": Counter({"opencv_visual_fragments": len(rows)}),
        "folio": Counter(row.get("folio_labels", "") for row in rows),
        "word_map_status": Counter(row.get("word_map_status", "") for row in rows),
        "semantic_guardrail": Counter({GUARDRAIL: len(rows)}),
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


def optional_cv2():
    try:
        import cv2  # type: ignore
    except ImportError:
        return None
    return cv2


def html_image_src(local_image_path: str) -> str:
    return "../../" + local_image_path.lstrip("/") if local_image_path else ""


def clamp_percent(value: float) -> float:
    return max(0.0, min(100.0, value))


def expand_box(
    box: tuple[float, float, float, float],
    x_pad: float = 1.0,
    y_pad: float = 1.2,
) -> tuple[float, float, float, float]:
    x1, y1, x2, y2 = box
    return (
        clamp_percent(x1 - x_pad),
        clamp_percent(y1 - y_pad),
        clamp_percent(x2 + x_pad),
        clamp_percent(y2 + y_pad),
    )


def merge_components_into_word_clusters(
    components: list[dict[str, float]],
    max_gap_pct: float = 1.25,
) -> list[dict[str, float]]:
    filtered = [
        component
        for component in components
        if float(component["x2"]) > float(component["x1"]) and float(component["y2"]) > float(component["y1"])
    ]
    clusters: list[list[dict[str, float]]] = []
    current: list[dict[str, float]] = []
    current_right = 0.0
    for component in sorted(filtered, key=lambda item: (float(item["x1"]), float(item["x2"]))):
        if current and float(component["x1"]) - current_right > max_gap_pct:
            clusters.append(current)
            current = []
        current.append(component)
        current_right = max(current_right, float(component["x2"]))
    if current:
        clusters.append(current)

    output: list[dict[str, float]] = []
    for cluster in clusters:
        output.append(
            {
                "x1": min(float(item["x1"]) for item in cluster),
                "y1": min(float(item["y1"]) for item in cluster),
                "x2": max(float(item["x2"]) for item in cluster),
                "y2": max(float(item["y2"]) for item in cluster),
                "confidence": sum(float(item.get("confidence", 0.0)) for item in cluster) / len(cluster),
            }
        )
    return output


def _fill_short_false_runs(values: list[bool], max_gap: int) -> list[bool]:
    if max_gap <= 0:
        return values
    filled = values[:]
    index = 0
    while index < len(filled):
        if filled[index]:
            index += 1
            continue
        start = index
        while index < len(filled) and not filled[index]:
            index += 1
        end = index
        if start > 0 and end < len(filled) and end - start <= max_gap:
            for fill_index in range(start, end):
                filled[fill_index] = True
    return filled


def _true_runs(values: list[bool]) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    index = 0
    while index < len(values):
        if not values[index]:
            index += 1
            continue
        start = index
        while index < len(values) and values[index]:
            index += 1
        runs.append((start, index))
    return runs


def _group_projection_runs(
    runs: list[tuple[int, int]],
    word_gap_px: int,
    min_run_width_px: int,
) -> list[tuple[int, int]]:
    useful_runs = [(start, end) for start, end in runs if end - start >= min_run_width_px]
    if not useful_runs:
        return []
    groups: list[tuple[int, int]] = []
    current_start, current_end = useful_runs[0]
    for start, end in useful_runs[1:]:
        if start - current_end <= word_gap_px:
            current_end = max(current_end, end)
            continue
        groups.append((current_start, current_end))
        current_start, current_end = start, end
    groups.append((current_start, current_end))
    return groups


def _projection_fragment_boxes(
    mask,
    *,
    left: int,
    top: int,
    image_width: int,
    image_height: int,
) -> list[dict[str, float]]:
    crop_h, crop_w = mask.shape[:2]
    if crop_w < 8 or crop_h < 5:
        return []

    ink_columns = [
        count >= max(1, int(crop_h * 0.055))
        for count in (mask > 0).sum(axis=0).tolist()
    ]
    ink_columns = _fill_short_false_runs(ink_columns, max_gap=max(2, crop_w // 340))
    runs = _true_runs(ink_columns)
    groups = _group_projection_runs(
        runs,
        word_gap_px=max(6, min(28, crop_w // 90)),
        min_run_width_px=max(2, crop_w // 700),
    )

    boxes: list[dict[str, float]] = []
    crop_area = crop_w * crop_h
    for start, end in groups:
        fragment = mask[:, start:end]
        y_coords, x_coords = (fragment > 0).nonzero()
        if len(x_coords) < max(4, int(crop_area * 0.00008)):
            continue
        x = start + int(x_coords.min())
        y = int(y_coords.min())
        w = int(x_coords.max() - x_coords.min() + 1)
        h = int(y_coords.max() - y_coords.min() + 1)
        if w < max(2, crop_w * 0.003) or h < max(2, crop_h * 0.14):
            continue
        if w * h > crop_area * 0.42:
            continue
        full_x1 = ((left + x) / image_width) * 100
        full_y1 = ((top + y) / image_height) * 100
        full_x2 = ((left + x + w) / image_width) * 100
        full_y2 = ((top + y + h) / image_height) * 100
        width_pct = full_x2 - full_x1
        height_pct = full_y2 - full_y1
        if width_pct < 0.18 or height_pct < 0.12:
            continue
        confidence = min(0.96, 0.40 + min(width_pct, 7.0) / 15 + min(height_pct, 2.5) / 9)
        boxes.append(
            {
                "x1": full_x1,
                "y1": full_y1,
                "x2": full_x2,
                "y2": full_y2,
                "confidence": confidence,
            }
        )
    return boxes


def detect_components_in_line(image_path: Path, line_box: tuple[float, float, float, float]) -> list[dict[str, float]]:
    cv2 = optional_cv2()
    if cv2 is None:
        return []
    image = cv2.imread(str(image_path), cv2.IMREAD_GRAYSCALE)
    if image is None:
        return []
    height, width = image.shape[:2]
    x1, y1, x2, y2 = expand_box(line_box, x_pad=1.0, y_pad=1.25)
    left = max(0, int((x1 / 100) * width))
    top = max(0, int((y1 / 100) * height))
    right = min(width, int((x2 / 100) * width))
    bottom = min(height, int((y2 / 100) * height))
    if right <= left or bottom <= top:
        return []

    crop = image[top:bottom, left:right]
    crop_h, crop_w = crop.shape[:2]
    if crop_w < 8 or crop_h < 5:
        return []
    blurred = cv2.GaussianBlur(crop, (3, 3), 0)
    _threshold, mask = cv2.threshold(blurred, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    projection_boxes = _projection_fragment_boxes(mask, left=left, top=top, image_width=width, image_height=height)
    if len(projection_boxes) >= 2:
        return projection_boxes

    close_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (max(2, crop_w // 260), max(1, crop_h // 12)))
    connected = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, close_kernel)
    contours, _hierarchy = cv2.findContours(connected, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    components: list[dict[str, float]] = []
    crop_area = crop_w * crop_h
    for contour in contours:
        x, y, w, h = cv2.boundingRect(contour)
        if w < max(2, crop_w * 0.004) or h < max(2, crop_h * 0.16):
            continue
        if w * h > crop_area * 0.45:
            continue
        full_x1 = ((left + x) / width) * 100
        full_y1 = ((top + y) / height) * 100
        full_x2 = ((left + x + w) / width) * 100
        full_y2 = ((top + y + h) / height) * 100
        width_pct = full_x2 - full_x1
        height_pct = full_y2 - full_y1
        if width_pct < 0.18 or height_pct < 0.12:
            continue
        confidence = min(0.95, 0.35 + min(width_pct, 8.0) / 18 + min(height_pct, 2.5) / 10)
        components.append(
            {
                "x1": full_x1,
                "y1": full_y1,
                "x2": full_x2,
                "y2": full_y2,
                "confidence": confidence,
            }
        )
    return merge_components_into_word_clusters(components, max_gap_pct=0.85)


def detect_word_boxes_by_line(line_rows: list[dict[str, str]]) -> tuple[dict[str, list[dict[str, float]]], bool]:
    cv2_available = optional_cv2() is not None
    if not cv2_available:
        return {}, False
    output: dict[str, list[dict[str, float]]] = {}
    for row in line_rows:
        route42e_id = row.get("route42e_id", "")
        line_box = parse_box_pct(row.get("band_box_pct", ""))
        image_path = row.get("local_image_path", "")
        if not route42e_id or not line_box or not image_path:
            continue
        output[route42e_id] = detect_components_in_line(resolve_project_path(image_path), line_box)
    return output, True


def build_visual_word_rows(
    line_rows: list[dict[str, str]],
    word_boxes_by_line: dict[str, list[dict[str, float]]],
    cv2_available: bool,
) -> list[dict[str, str]]:
    if not cv2_available:
        return []
    rows: list[dict[str, str]] = []
    for line in line_rows:
        route42e_id = line.get("route42e_id", "")
        boxes = sorted(word_boxes_by_line.get(route42e_id, []), key=lambda box: (box["x1"], box["y1"]))
        for word_index, box in enumerate(boxes, start=1):
            crop_box = expand_box((box["x1"], box["y1"], box["x2"], box["y2"]), x_pad=1.0, y_pad=1.2)
            center_x = (float(box["x1"]) + float(box["x2"])) / 2
            center_y = (float(box["y1"]) + float(box["y2"])) / 2
            rows.append(
                {
                    "route42j_id": f"R42J-{len(rows) + 1:03d}",
                    "route42e_id": route42e_id,
                    "image_id": line.get("image_id", ""),
                    "folio_labels": line.get("folio_labels", ""),
                    "local_image_path": line.get("local_image_path", ""),
                    "visual_line_number": line.get("visual_line_number", ""),
                    "visual_word_number": str(word_index),
                    "word_box_pct": box_text((box["x1"], box["y1"], box["x2"], box["y2"])),
                    "crop_box_pct": box_text(crop_box),
                    "center_x_pct": f"{center_x:.2f}",
                    "center_y_pct": f"{center_y:.2f}",
                    "confidence": f'{float(box.get("confidence", 0.0)):.2f}',
                    "source_line_box_pct": line.get("band_box_pct", ""),
                    "target_loci_on_image": line.get("target_loci_on_image", ""),
                    "word_map_status": "opencv_visual_fragment_detected",
                    "semantic_guardrail": GUARDRAIL,
                }
            )
    return rows


def render_html(rows: list[dict[str, str]], word_map_csv: str) -> str:
    rows_json = json.dumps(
        [
            {
                **row,
                "image_src": html_image_src(row.get("local_image_path", "")),
            }
            for row in rows
        ],
        ensure_ascii=True,
    )
    static_summary = "".join(
        f'<span class="fragment-pill">{html.escape(row["folio_labels"])} / linha {html.escape(row["visual_line_number"])} / visual fragmento {html.escape(row["visual_word_number"])}</span>'
        for row in rows[:80]
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rota 42J - Fragmentos visuais OpenCV</title>
  <style>
    :root {{
      --paper: #f7f1e8;
      --panel: #fffaf2;
      --line: #d8c9b8;
      --ink: #211c18;
      --muted: #6b6259;
      --accent: #1f7668;
      --warn: #8f3f33;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; background: var(--paper); color: var(--ink); font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; }}
    button, a.button-link {{ border: 1px solid #c8baaa; border-radius: 7px; background: #fffaf2; color: var(--ink); padding: 8px 11px; font-weight: 800; text-decoration: none; cursor: pointer; }}
    button:hover, a.button-link:hover {{ background: #f1e7d8; }}
    .app {{ min-height: 100vh; display: grid; grid-template-rows: auto minmax(0, 1fr); }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 12px 16px; border-bottom: 1px solid var(--line); background: #fbf6ed; }}
    h1 {{ margin: 0; font-size: 20px; }}
    p {{ margin: 0; color: var(--muted); }}
    .nav {{ display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }}
    .workspace {{ min-height: 0; display: grid; grid-template-columns: 280px minmax(0, 1fr) 360px; }}
    .queue {{ overflow: auto; border-right: 1px solid var(--line); background: #f1e6d7; padding: 10px; }}
    .queue button {{ width: 100%; display: grid; gap: 3px; text-align: left; margin-bottom: 7px; }}
    .queue button.active {{ border-color: var(--accent); outline: 3px solid rgba(31, 118, 104, .2); }}
    .fragment-panel {{ overflow: auto; padding: 14px; background: #e5dccf; }}
    .fragment-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; }}
{VISUAL_CROP_CSS}
    .fragment-card .visual-crop-canvas {{ min-height: 62px; }}
    .side {{ overflow: auto; border-left: 1px solid var(--line); background: var(--panel); padding: 14px; }}
    .plain-box {{ border: 1px solid var(--line); border-radius: 8px; background: #fff7ea; padding: 12px; margin-bottom: 12px; }}
    .plain-box h2, .plain-box h3 {{ margin: 0 0 8px; font-size: 15px; }}
    .warning {{ color: var(--warn); font-weight: 850; }}
    .fragment-pill {{ display: block; padding: 6px 8px; border: 1px solid #dacdbc; border-radius: 7px; background: #fffdf8; font-size: 12px; margin-bottom: 6px; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; overflow-wrap: anywhere; }}
  </style>
</head>
<body>
<div class="app">
  <header class="topbar">
    <div>
      <h1>Rota 42J</h1>
      <p>Analise mais fina com computer vision: fragmentos visuais dentro das linhas. Isto nao e OCR, traducao ou palavra confirmada.</p>
    </div>
    <nav class="nav" aria-label="Navegacao entre rotas">
      <a class="button-link" href="rota_42g_ferramentas_ativas_r32.html">Ferramentas ativas</a>
      <a class="button-link" href="rota_42k_fila_priorizada_revisao_visual_r32.html">Abrir R42K</a>
      <a class="button-link" href="rota_42e_mapa_opencv_linhas_visuais_r32.html">Abrir R42E</a>
      <a class="button-link" href="rota_42f_escolha_linhas_visuais_sem_zona_r32.html">Abrir R42F</a>
      <a class="button-link" href="rota_42c_calibrador_linhas_baseline_r32.html">Abrir R42C</a>
    </nav>
  </header>
  <main class="workspace">
    <aside class="queue" id="lineQueue" aria-label="Linhas com fragmentos visuais"></aside>
    <section class="fragment-panel" aria-label="Recortes de fragmentos visuais">
      <div class="fragment-grid" id="fragmentGrid"></div>
    </section>
    <aside class="side" aria-label="Explicacao da rota 42J">
      <section class="plain-box">
        <h2 id="lineTitle">Selecione uma linha</h2>
        <p id="lineSubtitle"></p>
      </section>
      <section class="plain-box">
        <h3>Como usar</h3>
        <p>Compare estes recortes com a linha original. Eles sao pedacos de tinta agrupados por visao computacional, nao palavras lidas pela maquina.</p>
      </section>
      <section class="plain-box">
        <h3>Resumo auditavel</h3>
        <div>{static_summary or '<p class="warning">Nenhum fragmento visual detectado.</p>'}</div>
      </section>
      <section class="plain-box">
        <h3>CSV</h3>
        <p class="mono">{html.escape(word_map_csv)}</p>
      </section>
      <section class="plain-box">
        <h3>Guarda</h3>
        <p class="mono">{GUARDRAIL}</p>
        <p class="warning">Nao usar como OCR nem como evidencia de palavra. Use como lupa operacional.</p>
      </section>
    </aside>
  </main>
</div>
<script>
const FRAGMENT_ROWS = {rows_json};
let currentKey = "";

{VISUAL_CROP_JS}

function lineKey(row) {{
  return `${{row.route42e_id}}::${{row.local_image_path}}::${{row.visual_line_number}}`;
}}

function lineGroups() {{
  const groups = new Map();
  for (const row of FRAGMENT_ROWS) {{
    const key = lineKey(row);
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(row);
  }}
  return groups;
}}

function renderQueue() {{
  const queue = document.getElementById("lineQueue");
  queue.innerHTML = "";
  const groups = lineGroups();
  if (!currentKey && groups.size) currentKey = Array.from(groups.keys())[0];
  for (const [key, rows] of groups.entries()) {{
    const first = rows[0];
    const button = document.createElement("button");
    button.type = "button";
    button.className = key === currentKey ? "active" : "";
    button.innerHTML = `<strong>${{first.folio_labels}} / linha visual ${{first.visual_line_number}}</strong><small>${{rows.length}} fragmentos visuais</small>`;
    button.addEventListener("click", () => {{
      currentKey = key;
      renderAll();
    }});
    queue.appendChild(button);
  }}
  if (!groups.size) queue.innerHTML = "<p>Nenhum fragmento visual detectado.</p>";
}}

function renderFragments() {{
  const grid = document.getElementById("fragmentGrid");
  grid.innerHTML = "";
  const rows = lineGroups().get(currentKey) || [];
  for (const row of rows) {{
    const card = document.createElement("article");
    card.className = "visual-crop-card fragment-card";
    card.innerHTML = `
      <span class="visual-crop-label">visual fragmento ${{row.visual_word_number}} <small>conf. ${{row.confidence}}</small></span>
      <canvas class="visual-crop-canvas" data-crop-preview data-image-src="${{row.image_src}}" data-box-pct="${{row.crop_box_pct}}" aria-label="visual fragmento ${{row.visual_word_number}}"></canvas>
      <span class="visual-crop-note">linha visual ${{row.visual_line_number}} / ${{row.folio_labels}}</span>
    `;
    grid.appendChild(card);
  }}
  if (!rows.length) grid.innerHTML = '<p class="warning">Nenhum fragmento para esta linha.</p>';
  paintCropPreviews(grid);
}}

function renderSide() {{
  const rows = lineGroups().get(currentKey) || [];
  const first = rows[0];
  document.getElementById("lineTitle").textContent = first
    ? `${{first.folio_labels}} / linha visual ${{first.visual_line_number}}`
    : "Nenhuma linha";
  document.getElementById("lineSubtitle").textContent = first
    ? `${{rows.length}} fragmentos visuais detectados por OpenCV`
    : "sem fragmentos";
}}

function renderAll() {{
  renderQueue();
  renderFragments();
  renderSide();
}}

renderAll();
</script>
</body>
</html>"""


def render_counts(title: str, counts: Counter[str]) -> list[str]:
    lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
    for key, value in sorted(counts.items(), key=lambda pair: (-pair[1], pair[0])):
        lines.append(f"|{key}|{value}|")
    lines.append("")
    return lines


def write_markdown_report(
    path: Path,
    rows: list[dict[str, str]],
    line_map_csv: Path,
    word_map_csv: Path,
    summary_csv: Path,
    html_path: Path,
    cv2_available: bool,
) -> None:
    lines = [
        "# Rota 42J: fragmentos visuais OpenCV dentro das linhas",
        "",
        "Esta rota faz uma analise mais fina por computer vision: dentro das linhas visuais da R42E, ela separa pedacos de tinta em fragmentos visuais parecidos com palavras.",
        "",
        "Ela nao e OCR, nao le EVA, nao traduz, nao confirma palavra e nao preenche a R32.",
        "",
        f"Entrada: `{line_map_csv}`.",
        f"CSV de fragmentos: `{word_map_csv}`.",
        f"Resumo: `{summary_csv}`.",
        f"HTML: `{html_path}`.",
        "",
        "## Resultado curto",
        "",
        f"- OpenCV disponivel: {'sim' if cv2_available else 'nao'};",
        f"- fragmentos visuais detectados: {len(rows)};",
        "- uso correto: abrir R42J para comparar recortes de fragmentos dentro de uma linha visual, depois voltar para R42F/R42C;",
        f"- guarda: `{GUARDRAIL}`.",
        "",
    ]
    lines.extend(render_counts("Fragmentos por folio", Counter(row.get("folio_labels", "") for row in rows)))
    lines.extend(render_counts("Fragmentos por linha visual", Counter(f"{row.get('folio_labels', '')} linha {row.get('visual_line_number', '')}" for row in rows)))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--line-map-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_line_opencv_map_zl3b.csv"),
        help="Route 42E visual line map CSV",
    )
    parser.add_argument(
        "--word-map-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_word_opencv_map_zl3b.csv"),
        help="Route 42J visual fragment map CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_word_opencv_map_summary_zl3b.csv"),
        help="Route 42J summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_42j_fragmentos_visuais_opencv_r32.md"),
        help="Route 42J Markdown report output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_42j_fragmentos_visuais_opencv_r32.html"),
        help="Route 42J HTML output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    line_map_csv = Path(args.line_map_csv)
    word_map_csv = Path(args.word_map_csv)
    summary_csv = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)

    line_rows = read_csv(line_map_csv)
    word_boxes_by_line, cv2_available = detect_word_boxes_by_line(line_rows)
    rows = build_visual_word_rows(line_rows, word_boxes_by_line, cv2_available)

    write_csv(word_map_csv, rows, FIELDNAMES)
    write_summary_csv(summary_csv, rows, cv2_available)
    write_markdown_report(md_path, rows, line_map_csv, word_map_csv, summary_csv, html_path, cv2_available)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_html(rows, str(word_map_csv)), encoding="utf-8")

    print(
        f"opencv_available={int(cv2_available)} "
        f"visual_lines={len(line_rows)} visual_fragments={len(rows)}"
    )
    print(f"word_map_csv={word_map_csv.resolve()}")
    print(f"summary_csv={summary_csv.resolve()}")
    print(f"md={md_path.resolve()}")
    print(f"html={html_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
