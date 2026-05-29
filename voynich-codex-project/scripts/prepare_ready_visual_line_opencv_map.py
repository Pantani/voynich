#!/usr/bin/env python3
"""Prepare an OpenCV visual-line map for route 42C calibration."""
from __future__ import annotations

import argparse
import csv
import html
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "opencv_visual_line_map_not_word_evidence"

FIELDNAMES = [
    "route42e_id",
    "image_id",
    "folio_labels",
    "local_image_path",
    "visual_line_number",
    "band_box_pct",
    "baseline_points",
    "center_y_pct",
    "confidence",
    "target_loci_on_image",
    "source_candidate_count",
    "line_map_status",
    "semantic_guardrail",
]

IMAGE_FIELDNAMES = [
    "image_id",
    "folio_labels",
    "local_image_path",
    "image_src",
    "target_loci",
    "detected_visual_lines",
    "semantic_guardrail",
]


try:
    from scripts.prepare_ready_visual_line_opencv_suggestions import VISUAL_ZONE_OVERRIDES, detect_bands_by_image
    from scripts.visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS
except ImportError:  # pragma: no cover - used when running this file directly from scripts/
    from prepare_ready_visual_line_opencv_suggestions import VISUAL_ZONE_OVERRIDES, detect_bands_by_image
    from visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS


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


def write_summary_csv(path: Path, image_rows: list[dict[str, str]], line_rows: list[dict[str, str]]) -> None:
    counts = {
        "image_count": Counter({"images": len(image_rows)}),
        "visual_line_count": Counter({"opencv_visual_lines": len(line_rows)}),
        "folio": Counter(row.get("folio_labels", "") for row in image_rows),
        "line_map_status": Counter(row.get("line_map_status", "") for row in line_rows),
        "semantic_guardrail": Counter({GUARDRAIL: len(image_rows) + len(line_rows)}),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "item", "n"])
        writer.writeheader()
        for metric, counter in counts.items():
            for item, n in sorted(counter.items(), key=lambda pair: (-pair[1], pair[0])):
                writer.writerow({"metric": metric, "item": item, "n": n})


def unique_image_records(calibration_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    records: list[dict[str, str]] = []
    by_path: dict[str, dict[str, set[str]]] = {}
    for row in calibration_rows:
        image_path = row.get("local_image_path", "")
        if not image_path:
            continue
        if image_path not in by_path:
            by_path[image_path] = {"folios": set(), "targets": set()}
            records.append({"local_image_path": image_path})
        if row.get("folio"):
            by_path[image_path]["folios"].add(row["folio"])
        if row.get("target_locus"):
            by_path[image_path]["targets"].add(row["target_locus"])
    for index, record in enumerate(records, start=1):
        image_path = record["local_image_path"]
        record["image_id"] = f"R42EIMG-{index:03d}"
        record["folio_labels"] = ", ".join(sorted(by_path[image_path]["folios"]))
        record["target_loci"] = "|".join(sorted(by_path[image_path]["targets"]))
    return records


def band_box_text(band: dict[str, float]) -> str:
    return f'{band["x1"]:.2f},{band["y1"]:.2f},{band["x2"]:.2f},{band["y2"]:.2f}'


def baseline_from_band(band: dict[str, float]) -> str:
    y = band["y2"]
    return f'{band["x1"]:.2f},{y:.2f} {band["x2"]:.2f},{y:.2f}'


def build_line_map_rows(
    calibration_rows: list[dict[str, str]],
    image_bands: dict[str, list[dict[str, float]]],
    cv2_available: bool,
) -> list[dict[str, str]]:
    if not cv2_available:
        return []
    line_rows: list[dict[str, str]] = []
    for image in unique_image_records(calibration_rows):
        image_path = image["local_image_path"]
        bands = sorted(image_bands.get(image_path, []), key=lambda band: (band["y1"], band["x1"]))
        for line_index, band in enumerate(bands, start=1):
            center_y = (float(band["y1"]) + float(band["y2"])) / 2
            line_rows.append(
                {
                    "route42e_id": f"R42E-{len(line_rows) + 1:03d}",
                    "image_id": image["image_id"],
                    "folio_labels": image["folio_labels"],
                    "local_image_path": image_path,
                    "visual_line_number": str(line_index),
                    "band_box_pct": band_box_text(band),
                    "baseline_points": baseline_from_band(band),
                    "center_y_pct": f"{center_y:.2f}",
                    "confidence": f'{float(band.get("confidence", 0.0)):.2f}',
                    "target_loci_on_image": image["target_loci"],
                    "source_candidate_count": str(len(bands)),
                    "line_map_status": "opencv_visual_line_detected",
                    "semantic_guardrail": GUARDRAIL,
                }
            )
    return line_rows


def html_image_src(local_image_path: str) -> str:
    return "../../" + local_image_path.lstrip("/") if local_image_path else ""


def build_image_inventory(
    calibration_rows: list[dict[str, str]],
    line_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    line_count_by_image = Counter(row.get("local_image_path", "") for row in line_rows)
    inventory: list[dict[str, str]] = []
    for image in unique_image_records(calibration_rows):
        image_path = image["local_image_path"]
        inventory.append(
            {
                "image_id": image["image_id"],
                "folio_labels": image["folio_labels"],
                "local_image_path": image_path,
                "image_src": html_image_src(image_path),
                "target_loci": image["target_loci"],
                "detected_visual_lines": str(line_count_by_image.get(image_path, 0)),
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return inventory


def build_target_zone_rows(calibration_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    zone_rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for row in calibration_rows:
        target_locus = row.get("target_locus", "")
        image_path = row.get("local_image_path", "")
        zone = VISUAL_ZONE_OVERRIDES.get(target_locus)
        if not zone or not image_path:
            continue
        key = (image_path, target_locus)
        if key in seen:
            continue
        seen.add(key)
        zone_rows.append(
            {
                "local_image_path": image_path,
                "target_locus": target_locus,
                "top": f'{float(zone["top"]):.2f}',
                "left": f'{float(zone["left"]):.2f}',
                "width": f'{float(zone["width"]):.2f}',
                "height": f'{float(zone["height"]):.2f}',
                "label": str(zone["label"]),
            }
        )
    return zone_rows


def render_html(
    image_rows: list[dict[str, str]],
    line_rows: list[dict[str, str]],
    line_map_csv: str,
    target_zone_rows: list[dict[str, str]] | None = None,
) -> str:
    images_json = json.dumps(image_rows, ensure_ascii=True)
    lines_json = json.dumps(line_rows, ensure_ascii=True)
    target_zones_json = json.dumps(target_zone_rows or [], ensure_ascii=True)
    static_line_summary = "".join(
        '<span class="line-pill" '
        f'data-visual-line-number="{html.escape(row["visual_line_number"])}">'
        f'linha visual {html.escape(row["visual_line_number"])} '
        f'/ {html.escape(row["folio_labels"])} '
        f'/ conf. {html.escape(row["confidence"])}'
        "</span>"
        for row in line_rows[:80]
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rota 42E - Mapa OpenCV de linhas visuais</title>
  <style>
    :root {{
      --paper: #f7f1e8;
      --panel: #fffaf2;
      --line: #d8c9b8;
      --ink: #211c18;
      --muted: #6b6259;
      --accent: #1f7668;
      --draft: #8f3f33;
      --focus: #e6b85d;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; background: var(--paper); color: var(--ink); font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; }}
    button, a.button-link {{ border: 1px solid #c8baaa; border-radius: 7px; background: #fffaf2; color: var(--ink); padding: 8px 11px; font-weight: 800; text-decoration: none; cursor: pointer; }}
    button:hover, a.button-link:hover {{ background: #f1e7d8; }}
    .app {{ height: 100vh; display: grid; grid-template-rows: auto minmax(0, 1fr); }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 12px 16px; border-bottom: 1px solid var(--line); background: #fbf6ed; }}
    h1 {{ margin: 0; font-size: 20px; }}
    p {{ margin: 0; color: var(--muted); }}
    .nav {{ display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }}
    .workspace {{ min-height: 0; display: grid; grid-template-columns: 270px minmax(0, 1fr) 360px; }}
    .queue {{ overflow: auto; border-right: 1px solid var(--line); background: #f1e6d7; padding: 10px; }}
    .queue button {{ width: 100%; display: grid; gap: 3px; text-align: left; margin-bottom: 7px; }}
    .queue button.active {{ border-color: var(--draft); outline: 3px solid rgba(230, 184, 93, .42); }}
    .image-panel {{ min-width: 0; min-height: 0; overflow: auto; padding: 14px; background: #e5dccf; }}
    .image-stage {{ position: relative; display: inline-grid; background: #1c1b19; border-radius: 8px; overflow: hidden; }}
    .image-stage img {{ grid-area: 1 / 1; display: block; width: clamp(520px, calc(100vw - 700px), 1050px); max-width: 100%; height: auto; user-select: none; }}
    .overlay {{ grid-area: 1 / 1; position: absolute; inset: 0; pointer-events: none; }}
    .visual-line-box {{ position: absolute; height: 0; border-top: 2px solid rgba(143, 63, 51, .95); background: transparent; }}
    .visual-line-box::before {{ content: attr(data-label); position: absolute; left: 0; top: -13px; padding: 2px 6px; border-radius: 999px; border: 1px solid rgba(143, 63, 51, .55); background: #fffaf2; color: var(--draft); font-size: 12px; font-weight: 900; white-space: nowrap; }}
    .target-zone {{ position: absolute; border: 2px dashed rgba(31, 118, 104, .88); background: rgba(31, 118, 104, .08); border-radius: 6px; }}
    .target-zone::before {{ content: attr(data-label); position: absolute; left: 7px; top: 7px; padding: 2px 7px; border-radius: 999px; border: 1px solid rgba(31, 118, 104, .45); background: #fffaf2; color: var(--accent); font-size: 12px; font-weight: 900; white-space: nowrap; }}
    .side {{ overflow: auto; border-left: 1px solid var(--line); background: var(--panel); padding: 14px; }}
    .plain-box {{ border: 1px solid var(--line); border-radius: 8px; background: #fff7ea; padding: 12px; margin-bottom: 12px; }}
    .plain-box h2, .plain-box h3 {{ margin: 0 0 8px; font-size: 15px; }}
    .warning {{ color: #7c3029; font-weight: 850; }}
    .mode-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px; }}
    .mode-row button.active {{ border-color: var(--accent); background: #e8f4ef; color: #15584e; }}
    .line-list {{ display: grid; gap: 6px; }}
    .line-pill {{ display: flex; justify-content: space-between; gap: 10px; padding: 6px 8px; border: 1px solid #dacdbc; border-radius: 7px; background: #fffdf8; font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; }}
{VISUAL_CROP_CSS}
    .line-crop-mini {{ padding: 7px; }}
    .line-crop-mini .visual-crop-canvas {{ min-height: 48px; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; overflow-wrap: anywhere; }}
  </style>
</head>
<body>
<div class="app">
  <header class="topbar">
    <div>
      <h1>Rota 42E</h1>
      <p>Mapa OpenCV de linhas visuais. OpenCV conta faixas de texto; ele nao confirma palavra, traducao ou locus ZL3b.</p>
    </div>
    <nav class="nav" aria-label="Navegacao entre rotas">
      <a class="button-link" href="rota_42g_ferramentas_ativas_r32.html">Ferramentas ativas</a>
      <a class="button-link" href="rota_42b_pacote_html_preenchimento_humano_r32.html">Abrir R42B</a>
      <a class="button-link" href="rota_42c_calibrador_linhas_baseline_r32.html">Abrir R42C</a>
      <a class="button-link" href="rota_42d_sugestoes_opencv_linhas_r32.html">Abrir R42D</a>
      <a class="button-link" href="rota_42j_fragmentos_visuais_opencv_r32.html">Abrir R42J</a>
    </nav>
  </header>
  <main class="workspace">
    <aside class="queue" id="imageQueue" aria-label="Paginas mapeadas por OpenCV"></aside>
    <section class="image-panel" aria-label="Imagem com linhas visuais numeradas">
      <div class="image-stage">
        <img id="sourceImage" alt="Imagem high-res com linhas numeradas">
        <div class="overlay" id="lineOverlay" aria-label="Linhas visuais OpenCV"></div>
      </div>
    </section>
    <aside class="side" aria-label="Explicacao e linhas detectadas">
      <section class="plain-box">
        <h2 id="imageTitle">Selecione uma imagem</h2>
        <p id="imageSubtitle"></p>
      </section>
      <section class="plain-box">
        <h3>Como usar</h3>
        <p>O modo inicial mostra so as zonas R32 conhecidas e as reguas OpenCV que caem nelas. Use o mapa bruto apenas para auditoria.</p>
        <div class="mode-row" aria-label="Modo de exibicao">
          <button type="button" id="focusMode">Mostrar zonas R32</button>
          <button type="button" id="rawMode">Mapa bruto</button>
        </div>
      </section>
      <section class="plain-box">
        <h3>Alvos ZL3b nesta imagem</h3>
        <p class="mono" id="targetLoci"></p>
      </section>
      <section class="plain-box">
        <h3>Recortes das linhas</h3>
        <div id="lineList" class="line-list"></div>
      </section>
      <section class="plain-box">
        <h3>Resumo auditavel</h3>
        <div class="line-list">{static_line_summary or '<p class="warning">Nenhuma linha visual detectada.</p>'}</div>
      </section>
      <section class="plain-box">
        <h3>Guarda</h3>
        <p class="mono">{GUARDRAIL}</p>
        <p class="warning">Nao use estes numeros como prova automatica. Eles sao um mapa para calibracao humana.</p>
      </section>
      <section class="plain-box">
        <h3>CSV</h3>
        <p class="mono">{html.escape(line_map_csv)}</p>
      </section>
    </aside>
  </main>
</div>
<script>
const IMAGE_ROWS = {images_json};
const LINE_ROWS = {lines_json};
const TARGET_ZONE_ROWS = {target_zones_json};
let currentIndex = 0;
let showRawMap = false;

{VISUAL_CROP_JS}

function linesForImage(image) {{
  return LINE_ROWS.filter((row) => row.local_image_path === image.local_image_path);
}}

function zonesForImage(image) {{
  return TARGET_ZONE_ROWS.filter((row) => row.local_image_path === image.local_image_path);
}}

function renderQueue() {{
  const queue = document.getElementById("imageQueue");
  queue.innerHTML = "";
  IMAGE_ROWS.forEach((image, index) => {{
    const button = document.createElement("button");
    button.type = "button";
    button.className = index === currentIndex ? "active" : "";
    button.innerHTML = `<strong>${{image.image_id}} / ${{image.folio_labels}}</strong><small>${{image.detected_visual_lines}} linhas visuais detectadas</small>`;
    button.addEventListener("click", () => showImage(index));
    queue.appendChild(button);
  }});
}}

function parseBox(value) {{
  const parts = String(value || "").split(",").map(Number);
  return parts.length === 4 && parts.every(Number.isFinite) ? parts : null;
}}

function lineTouchesZone(line, zone) {{
  const box = parseBox(line.band_box_pct);
  if (!box) return false;
  const [x1, y1, x2, y2] = box;
  const cx = (x1 + x2) / 2;
  const cy = (y1 + y2) / 2;
  const left = Number(zone.left);
  const top = Number(zone.top);
  const right = left + Number(zone.width);
  const bottom = top + Number(zone.height);
  return cx >= left - 2 && cx <= right + 2 && cy >= top - 2 && cy <= bottom + 2;
}}

function visibleLinesForImage(image) {{
  const lines = linesForImage(image);
  const zones = zonesForImage(image);
  if (showRawMap || !zones.length) return lines;
  const focused = lines.filter((line) => zones.some((zone) => lineTouchesZone(line, zone)));
  return focused.length ? focused : lines;
}}

function showImage(index) {{
  if (!IMAGE_ROWS.length) return;
  currentIndex = Math.max(0, Math.min(IMAGE_ROWS.length - 1, index));
  const image = IMAGE_ROWS[currentIndex];
  const allLines = linesForImage(image);
  const lines = visibleLinesForImage(image);
  const zones = zonesForImage(image);
  document.getElementById("sourceImage").src = image.image_src;
  document.getElementById("imageTitle").textContent = `${{image.image_id}} / ${{image.folio_labels}}`;
  document.getElementById("imageSubtitle").textContent = showRawMap
    ? `${{allLines.length}} linhas visuais no mapa bruto`
    : `${{lines.length}} de ${{allLines.length}} linhas visuais dentro das zonas R32 conhecidas`;
  document.getElementById("targetLoci").textContent = image.target_loci || "sem alvo ZL3b listado";
  const overlay = document.getElementById("lineOverlay");
  overlay.innerHTML = "";
  for (const zone of zones) {{
    const marker = document.createElement("div");
    marker.className = "target-zone";
    marker.dataset.label = zone.label || zone.target_locus;
    marker.style.left = `${{zone.left}}%`;
    marker.style.top = `${{zone.top}}%`;
    marker.style.width = `${{zone.width}}%`;
    marker.style.height = `${{zone.height}}%`;
    overlay.appendChild(marker);
  }}
  const list = document.getElementById("lineList");
  list.innerHTML = "";
  for (const line of lines) {{
    const box = parseBox(line.band_box_pct);
    if (box) {{
      const [x1, y1, x2, y2] = box;
      const marker = document.createElement("div");
      marker.className = "visual-line-box";
      marker.dataset.visualLineNumber = line.visual_line_number;
      marker.dataset.label = `linha visual ${{line.visual_line_number}}`;
      marker.style.left = `${{x1}}%`;
      marker.style.top = `${{y2}}%`;
      marker.style.width = `${{x2 - x1}}%`;
      overlay.appendChild(marker);
    }}
    const pill = document.createElement("div");
    pill.className = "visual-crop-card line-crop-mini";
    pill.innerHTML = `
      <span class="visual-crop-label">linha visual ${{line.visual_line_number}} <small>conf. ${{line.confidence}}</small></span>
      <canvas class="visual-crop-canvas" data-crop-preview data-image-src="${{image.image_src}}" data-box-pct="${{line.band_box_pct}}" aria-label="recorte real da linha visual ${{line.visual_line_number}}"></canvas>
    `;
    list.appendChild(pill);
  }}
  if (!lines.length) {{
    list.innerHTML = '<p class="warning">OpenCV nao detectou linhas visuais confiaveis nesta imagem.</p>';
  }}
  paintCropPreviews(list);
  renderQueue();
  document.getElementById("focusMode").className = showRawMap ? "" : "active";
  document.getElementById("rawMode").className = showRawMap ? "active" : "";
}}

document.getElementById("focusMode").addEventListener("click", () => {{
  showRawMap = false;
  showImage(currentIndex);
}});
document.getElementById("rawMode").addEventListener("click", () => {{
  showRawMap = true;
  showImage(currentIndex);
}});
showImage(0);
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
    image_rows: list[dict[str, str]],
    line_rows: list[dict[str, str]],
    line_map_csv: Path,
    image_inventory_csv: Path,
    summary_csv: Path,
    html_path: Path,
) -> None:
    lines = [
        "# Rota 42E: mapa OpenCV de linhas visuais",
        "",
        "Esta rota conta e numera faixas de texto detectadas por OpenCV nas imagens high-res usadas pela R42C/R42B.",
        "",
        "Ela nao encontra palavras, nao traduz, nao preenche a R32 e nao prova que uma linha ZL3b corresponde ao mesmo numero visual.",
        "",
        f"CSV de linhas: `{line_map_csv}`.",
        f"CSV de imagens: `{image_inventory_csv}`.",
        f"Resumo: `{summary_csv}`.",
        f"HTML: `{html_path}`.",
        "",
        "## Resultado curto",
        "",
        f"- imagens mapeadas: {len(image_rows)};",
        f"- linhas visuais detectadas: {len(line_rows)};",
        "- uso correto: abrir R42E no modo focado de zonas R32, usar os recortes das linhas para auditar rapidamente, depois confirmar/corrigir na R42C;",
        "- auditoria: usar o botao `Mapa bruto` somente para ver todos os candidatos OpenCV;",
        f"- guarda: `{GUARDRAIL}`.",
        "",
    ]
    lines.extend(render_counts("Linhas por imagem", Counter(row["folio_labels"] for row in image_rows)))
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
        "--line-map-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_line_opencv_map_zl3b.csv"),
        help="Route 42E visual line map CSV output",
    )
    parser.add_argument(
        "--image-inventory-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_line_opencv_map_images_zl3b.csv"),
        help="Route 42E image inventory CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_line_opencv_map_summary_zl3b.csv"),
        help="Route 42E summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_42e_mapa_opencv_linhas_visuais_r32.md"),
        help="Route 42E Markdown report output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_42e_mapa_opencv_linhas_visuais_r32.html"),
        help="Route 42E HTML output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    calibration_csv = Path(args.calibration_csv)
    line_map_csv = Path(args.line_map_csv)
    image_inventory_csv = Path(args.image_inventory_csv)
    summary_csv = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)

    calibration_rows = read_csv(calibration_csv)
    bands_by_image, cv2_available = detect_bands_by_image(calibration_rows)
    line_rows = build_line_map_rows(calibration_rows, bands_by_image, cv2_available)
    image_rows = build_image_inventory(calibration_rows, line_rows)
    target_zone_rows = build_target_zone_rows(calibration_rows)

    write_csv(line_map_csv, line_rows, FIELDNAMES)
    write_csv(image_inventory_csv, image_rows, IMAGE_FIELDNAMES)
    write_summary_csv(summary_csv, image_rows, line_rows)
    write_markdown_report(md_path, image_rows, line_rows, line_map_csv, image_inventory_csv, summary_csv, html_path)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_html(image_rows, line_rows, str(line_map_csv), target_zone_rows), encoding="utf-8")

    print(
        f"opencv_available={int(cv2_available)} "
        f"images={len(image_rows)} visual_lines={len(line_rows)}"
    )
    print(f"line_map_csv={line_map_csv.resolve()}")
    print(f"image_inventory_csv={image_inventory_csv.resolve()}")
    print(f"summary_csv={summary_csv.resolve()}")
    print(f"md={md_path.resolve()}")
    print(f"html={html_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
