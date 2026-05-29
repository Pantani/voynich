#!/usr/bin/env python3
"""Prepare a simple visual-line choice tool for route 42D missing zones."""
from __future__ import annotations

import argparse
import csv
import html
import json
from collections import Counter, defaultdict
from pathlib import Path

try:
    from scripts.eva_visual import EVA_VISUAL_CSS, render_eva_text
    from scripts.visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS
except ImportError:  # pragma: no cover - used when running this file directly from scripts/
    from eva_visual import EVA_VISUAL_CSS, render_eva_text
    from visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "line_zone_choice_not_visual_evidence"
STORAGE_KEY = "voynich.r42f.lineZoneChoice"

FIELDNAMES = [
    "route42f_id",
    "route42c_id",
    "route42b_id",
    "route32_id",
    "folio",
    "target_locus",
    "line_number",
    "transcription_text",
    "local_image_path",
    "candidate_count",
    "candidate_visual_lines",
    "candidate_visual_line_zones",
    "selected_visual_line_number",
    "selected_zone_box_pct",
    "zone_status",
    "manual_zone_notes",
    "semantic_guardrail",
]

ZONE_STATUS_PENDING = "pending_zone_choice"
ZONE_STATUS_SELECTED = "zone_selected_pending_opencv"


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
        "zone_status": Counter(row.get("zone_status", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
        "semantic_guardrail": Counter(row.get("semantic_guardrail", "") for row in rows),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "item", "n"])
        writer.writeheader()
        for metric, counter in counts.items():
            for item, n in sorted(counter.items(), key=lambda pair: (-pair[1], pair[0])):
                writer.writerow({"metric": metric, "item": item, "n": n})


def html_image_src(local_image_path: str) -> str:
    return "../../" + local_image_path.lstrip("/") if local_image_path else ""


def parse_box(value: str) -> tuple[float, float, float, float] | None:
    parts = value.split(",")
    if len(parts) != 4:
        return None
    try:
        x1, y1, x2, y2 = [float(part) for part in parts]
    except ValueError:
        return None
    if not (0 <= x1 <= 100 and 0 <= x2 <= 100 and 0 <= y1 <= 100 and 0 <= y2 <= 100):
        return None
    if x2 <= x1 or y2 <= y1:
        return None
    return x1, y1, x2, y2


def selected_zone_from_line_map(line_row: dict[str, str]) -> str:
    box = parse_box(line_row.get("band_box_pct", ""))
    if not box:
        return ""
    x1, y1, x2, y2 = box
    left = max(0.0, x1 - 1.5)
    top = max(0.0, y1 - 1.2)
    right = min(100.0, x2 + 1.5)
    bottom = min(100.0, y2 + 1.2)
    return f"{left:.2f},{top:.2f},{right:.2f},{bottom:.2f}"


def line_rows_by_image(line_map_rows: list[dict[str, str]]) -> dict[str, list[dict[str, str]]]:
    grouped: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in line_map_rows:
        image_path = row.get("local_image_path", "")
        visual_line = row.get("visual_line_number", "")
        if image_path and visual_line:
            grouped[image_path].append(row)
    for rows in grouped.values():
        rows.sort(key=lambda row: int(row.get("visual_line_number", "0") or 0))
    return grouped


def existing_choice_index(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    index: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        route32_id = row.get("route32_id", "")
        target_locus = row.get("target_locus", "")
        if route32_id and target_locus:
            index[(route32_id, target_locus)] = row
    return index


def line_map_index(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    index: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        image_path = row.get("local_image_path", "")
        visual_line = row.get("visual_line_number", "")
        if image_path and visual_line:
            index[(image_path, visual_line)] = row
    return index


def build_zone_choice_rows(
    calibration_rows: list[dict[str, str]],
    suggestion_rows: list[dict[str, str]],
    line_map_rows: list[dict[str, str]],
    existing_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    calibration_by_key = {
        (row.get("route32_id", ""), row.get("target_locus", "")): row
        for row in calibration_rows
        if row.get("route32_id") and row.get("target_locus")
    }
    existing_by_key = existing_choice_index(existing_rows)
    lines_by_image = line_rows_by_image(line_map_rows)
    line_by_image_number = line_map_index(line_map_rows)

    rows: list[dict[str, str]] = []
    for suggestion in suggestion_rows:
        if suggestion.get("opencv_auto_action") != "needs_manual_zone":
            continue
        key = (suggestion.get("route32_id", ""), suggestion.get("target_locus", ""))
        source = calibration_by_key.get(key, suggestion)
        image_path = source.get("local_image_path", "") or suggestion.get("local_image_path", "")
        candidates = lines_by_image.get(image_path, [])
        candidate_visual_lines = "|".join(row.get("visual_line_number", "") for row in candidates)
        candidate_visual_line_zones = "|".join(
            f"{row.get('visual_line_number', '')}={selected_zone_from_line_map(row)}"
            for row in candidates
            if row.get("visual_line_number") and selected_zone_from_line_map(row)
        )
        existing = existing_by_key.get(key, {})
        selected_visual_line = existing.get("selected_visual_line_number", "").strip()
        selected_line = line_by_image_number.get((image_path, selected_visual_line)) if selected_visual_line else None
        selected_zone = selected_zone_from_line_map(selected_line) if selected_line else ""
        zone_status = existing.get("zone_status", "").strip() or ZONE_STATUS_PENDING
        if selected_visual_line and selected_zone:
            zone_status = ZONE_STATUS_SELECTED if zone_status == ZONE_STATUS_PENDING else zone_status

        rows.append(
            {
                "route42f_id": f"R42F-{len(rows) + 1:03d}",
                "route42c_id": source.get("route42c_id", ""),
                "route42b_id": source.get("route42b_id", ""),
                "route32_id": source.get("route32_id", ""),
                "folio": source.get("folio", ""),
                "target_locus": source.get("target_locus", ""),
                "line_number": source.get("line_number", ""),
                "transcription_text": source.get("transcription_text", ""),
                "local_image_path": image_path,
                "candidate_count": str(len(candidates)),
                "candidate_visual_lines": candidate_visual_lines,
                "candidate_visual_line_zones": candidate_visual_line_zones,
                "selected_visual_line_number": selected_visual_line,
                "selected_zone_box_pct": selected_zone,
                "zone_status": zone_status,
                "manual_zone_notes": existing.get("manual_zone_notes", ""),
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def render_html(rows: list[dict[str, str]], zone_choice_csv: str) -> str:
    payload_rows = []
    for row in rows:
        payload = dict(row)
        payload["image_src"] = html_image_src(row.get("local_image_path", ""))
        payload["transcription_visual_html"] = render_eva_text(row.get("transcription_text", ""), compact=True)
        payload_rows.append(payload)
    rows_json = json.dumps(payload_rows, ensure_ascii=True)
    fieldnames_json = json.dumps(FIELDNAMES)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rota 42F - Escolher linhas visuais faltantes</title>
  <style>
    :root {{
      --paper: #f8f3ea;
      --panel: #fffaf2;
      --line: #d7cabb;
      --ink: #241f1a;
      --muted: #6f675f;
      --accent: #1f7668;
      --draft: #8f3f33;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; background: var(--paper); color: var(--ink); font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; }}
    button, .button-link {{ border: 1px solid #c8baaa; border-radius: 7px; background: #fffaf2; color: var(--ink); padding: 9px 12px; font-weight: 800; text-decoration: none; cursor: pointer; }}
    button:hover, .button-link:hover {{ background: #f1e7d8; }}
    button.primary {{ border-color: var(--accent); background: var(--accent); color: #f8fbfa; }}
    .app {{ min-height: 100vh; display: grid; grid-template-rows: auto auto minmax(0, 1fr); }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 12px 16px; border-bottom: 1px solid var(--line); background: #fbf6ed; }}
    h1 {{ margin: 0; font-size: 19px; }}
    p {{ margin: 0; color: var(--muted); }}
    .nav {{ display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }}
    .toolbar {{ display: flex; gap: 8px; padding: 10px 16px; border-bottom: 1px solid var(--line); background: #eee4d5; overflow-x: auto; }}
    .workspace {{ display: grid; grid-template-columns: 280px minmax(0, 1fr) 390px; min-height: 0; }}
    .queue {{ overflow: auto; border-right: 1px solid var(--line); background: #f2e8d9; padding: 10px; }}
    .queue button {{ width: 100%; display: grid; gap: 2px; margin-bottom: 7px; text-align: left; }}
    .queue button.active {{ border-color: var(--draft); outline: 3px solid rgba(231, 182, 87, .45); }}
    .image-panel {{ min-width: 0; min-height: 0; overflow: auto; padding: 72px; background: #e5dccf; }}
    .image-stage {{ position: relative; display: inline-grid; background: #1c1b19; border-radius: 8px; overflow: hidden; }}
    .image-stage img {{ grid-area: 1 / 1; display: block; width: clamp(520px, calc(100vw - 720px), 980px); max-width: 100%; height: auto; user-select: none; }}
    .overlay {{ grid-area: 1 / 1; position: absolute; inset: 0; pointer-events: none; }}
    .line-zone-choice {{ position: absolute; border: 2px solid rgba(143, 63, 51, .86); background: rgba(143, 63, 51, .08); border-radius: 3px; min-height: 4px; min-width: 4px; }}
    .line-zone-choice::before {{ content: attr(data-label); position: absolute; left: 0; top: -18px; padding: 2px 7px; border-radius: 999px; border: 1px solid rgba(143, 63, 51, .55); background: #fffaf2; color: var(--draft); font-size: 12px; font-weight: 900; white-space: nowrap; }}
    .line-zone-choice.selected {{ border-color: rgba(31, 118, 104, .96); background: rgba(31, 118, 104, .12); }}
    .line-zone-choice.selected::before {{ color: var(--accent); border-color: rgba(31, 118, 104, .55); }}
    .side {{ overflow: auto; border-left: 1px solid var(--line); background: var(--panel); padding: 14px; }}
    .plain-box {{ margin-bottom: 12px; padding: 12px; border: 1px solid var(--line); border-radius: 8px; background: #fff7ea; }}
    .plain-box h2, .plain-box h3 {{ margin: 0 0 8px; font-size: 15px; }}
    .guide {{ border-color: #b5d2cb; background: #eef6f2; }}
    .guide strong {{ display: block; font-size: 20px; line-height: 1.15; }}
    .line-buttons {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 8px; }}
    .line-buttons button.selected {{ border-color: var(--accent); background: #eef6f2; color: #164f47; }}
    textarea {{ width: 100%; min-height: 86px; resize: vertical; border: 1px solid var(--line); border-radius: 8px; background: #fffef9; color: var(--ink); padding: 9px; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; }}
{EVA_VISUAL_CSS}
{VISUAL_CROP_CSS}
    .line-crop-card {{ min-height: 132px; text-align: left; padding: 8px; background: #fffaf2; }}
    .line-crop-card.selected {{ border-color: var(--accent); background: #eef6f2; color: #164f47; }}
    .line-crop-card .visual-crop-label {{ font-size: 13px; }}
    #csvDraft {{ min-height: 180px; white-space: pre; }}
  </style>
</head>
<body>
<div class="app">
  <header class="topbar">
    <div>
      <h1>Rota 42F</h1>
      <p>Escolha a linha visual quando o OpenCV achou texto, mas nao sabe qual locus ZL3b combina. Isto nao preenche a R32.</p>
    </div>
    <nav class="nav" aria-label="Navegacao entre rotas">
      <a class="button-link" href="rota_42g_ferramentas_ativas_r32.html">Ferramentas ativas</a>
      <a class="button-link" href="rota_42k_fila_priorizada_revisao_visual_r32.html">Abrir R42K</a>
      <a class="button-link" href="rota_42l_confirmacao_linhas_sugeridas_r32.html">Abrir R42L</a>
      <a class="button-link" href="rota_42c_calibrador_linhas_baseline_r32.html">Abrir R42C</a>
      <a class="button-link" href="rota_42d_sugestoes_opencv_linhas_r32.html">Abrir R42D</a>
      <a class="button-link" href="rota_42e_mapa_opencv_linhas_visuais_r32.html">Abrir R42E</a>
      <a class="button-link" href="rota_42j_fragmentos_visuais_opencv_r32.html">Abrir R42J</a>
    </nav>
  </header>
  <nav class="toolbar" aria-label="Controles">
    <button type="button" id="prevItem">Anterior</button>
    <button type="button" id="nextItem">Proxima</button>
    <button type="button" id="nextPending">Proxima pendente</button>
    <button type="button" id="clearChoice">Limpar escolha</button>
    <button type="button" id="generateCsv">Gerar CSV</button>
    <button type="button" id="copyCsv">Copiar CSV</button>
    <button type="button" id="downloadCsv">Baixar CSV</button>
  </nav>
  <main class="workspace">
    <aside class="queue" id="queue" aria-label="Alvos sem zona"></aside>
    <section class="image-panel" aria-label="Imagem high-res">
      <div class="image-stage">
        <img id="sourceImage" alt="Imagem high-res do alvo">
        <div class="overlay" id="lineOverlay"></div>
      </div>
    </section>
    <aside class="side" aria-label="Escolha da linha visual">
      <div class="plain-box guide">
        <strong>Escolha a linha que combina</strong>
        <p>Clique no recorte que bate com o desenho de referencia. Nao precisa ler codigo.</p>
      </div>
      <div class="plain-box">
        <h2 id="itemTitle">Nenhum alvo</h2>
        <p class="mono" id="choiceStatus">pendente</p>
      </div>
      <div class="plain-box">
        <h3>Texto de referencia visual</h3>
        <div id="transcriptionText"></div>
      </div>
      <div class="plain-box">
        <h3>Linhas que o OpenCV encontrou</h3>
        <div class="line-buttons" id="lineButtons"></div>
      </div>
      <div class="plain-box">
        <h3>Escolha atual</h3>
        <p class="mono" id="selectedText">sem escolha</p>
      </div>
      <div class="plain-box">
        <h3>Nota manual</h3>
        <textarea id="manualZoneNotes" placeholder="Ex.: parece a segunda linha do bloco pequeno."></textarea>
      </div>
      <details>
        <summary>Rascunho CSV para {html.escape(zone_choice_csv)}</summary>
        <textarea id="csvDraft" class="mono" spellcheck="false"></textarea>
      </details>
      <div class="plain-box">
        <h3>Guarda</h3>
        <p class="mono">{GUARDRAIL}</p>
      </div>
    </aside>
  </main>
</div>
<script>
const ITEMS = {rows_json};
const FIELDNAMES = {fieldnames_json};
const STORAGE_KEY = "{STORAGE_KEY}";
let currentIndex = 0;
let draft = readDraft();

{VISUAL_CROP_JS}

function csvEscape(value) {{
  const text = value == null ? "" : String(value);
  return /[",\\n\\r]/.test(text) ? '"' + text.replaceAll('"', '""') + '"' : text;
}}

function readDraft() {{
  try {{
    return JSON.parse(localStorage.getItem(STORAGE_KEY) || "{{}}");
  }} catch (_error) {{
    return {{}};
  }}
}}

function writeDraft() {{
  localStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
}}

function keyFor(item) {{
  return `${{item.route32_id}}::${{item.target_locus}}`;
}}

function stateFor(item) {{
  const key = keyFor(item);
  if (!draft[key]) {{
    draft[key] = {{
      selected_visual_line_number: item.selected_visual_line_number || "",
      selected_zone_box_pct: item.selected_zone_box_pct || "",
      zone_status: item.zone_status || "pending_zone_choice",
      manual_zone_notes: item.manual_zone_notes || ""
    }};
  }}
  return draft[key];
}}

function lineNumbers(item) {{
  return (item.candidate_visual_lines || "").split("|").filter(Boolean);
}}

function lineZoneMap(item) {{
  const output = {{}};
  for (const entry of (item.candidate_visual_line_zones || "").split("|")) {{
    const [visualLine, zone] = entry.split("=");
    if (visualLine && zone) output[visualLine] = zone;
  }}
  return output;
}}

function zoneCenterY(zone) {{
  const parts = String(zone || "").split(",").map(Number);
  if (parts.length !== 4 || parts.some((value) => !Number.isFinite(value))) return null;
  return (parts[1] + parts[3]) / 2;
}}

function zoneToRect(zone) {{
  const parts = String(zone || "").split(",").map(Number);
  if (parts.length !== 4 || parts.some((v) => !Number.isFinite(v))) return null;
  const [x1, y1, x2, y2] = parts;
  return {{ left: x1, top: y1, width: Math.max(x2 - x1, 2), height: Math.max(y2 - y1, 2) }};
}}

function zoneFromLineNumber(item, visualLine) {{
  return lineZoneMap(item)[visualLine] || "";
}}

function activeItem() {{
  return ITEMS[currentIndex];
}}

function renderQueue() {{
  const queue = document.getElementById("queue");
  queue.innerHTML = "";
  ITEMS.forEach((item, index) => {{
    const state = stateFor(item);
    const button = document.createElement("button");
    button.type = "button";
    button.className = index === currentIndex ? "active" : "";
    button.innerHTML = `<b>${{item.route42f_id}} / ${{item.target_locus}}</b><small>${{state.zone_status}}</small>`;
    button.addEventListener("click", () => showItem(index));
    queue.appendChild(button);
  }});
}}

function renderOverlay(item, state) {{
  const overlay = document.getElementById("lineOverlay");
  overlay.innerHTML = "";
  const numbers = lineNumbers(item);
  const zones = lineZoneMap(item);
  numbers.forEach((line, index) => {{
    const marker = document.createElement("span");
    marker.className = "line-zone-choice" + (state.selected_visual_line_number === line ? " selected" : "");
    marker.dataset.label = `linha visual ${{line}}`;
    const rect = zoneToRect(zones[line]);
    if (rect) {{
      marker.style.left = `${{rect.left}}%`;
      marker.style.top = `${{rect.top}}%`;
      marker.style.width = `${{rect.width}}%`;
      marker.style.height = `${{rect.height}}%`;
    }} else {{
      const fallbackY = ((index + 0.5) / Math.max(numbers.length, 1)) * 100;
      marker.style.left = "8%";
      marker.style.width = "84%";
      marker.style.top = `${{fallbackY}}%`;
      marker.style.height = "4px";
    }}
    overlay.appendChild(marker);
  }});
}}

function renderLineButtons(item, state) {{
  const box = document.getElementById("lineButtons");
  box.innerHTML = "";
  for (const visualLine of lineNumbers(item)) {{
    const button = document.createElement("button");
    button.type = "button";
    const selected = state.selected_visual_line_number === visualLine;
    const zone = zoneFromLineNumber(item, visualLine);
    button.className = `visual-crop-card line-crop-card${{selected ? " selected" : ""}}`;
    button.innerHTML = `
      <span class="visual-crop-label">linha visual ${{visualLine}}</span>
      <canvas class="visual-crop-canvas" data-crop-preview data-image-src="${{item.image_src}}" data-box-pct="${{zone}}" aria-label="recorte real da linha visual ${{visualLine}}"></canvas>
      <span class="visual-crop-note">Essa e a linha</span>
    `;
    button.addEventListener("click", () => selectLine(visualLine));
    box.appendChild(button);
  }}
  paintCropPreviews(box);
}}

function showItem(index) {{
  if (!ITEMS.length) return;
  currentIndex = Math.max(0, Math.min(ITEMS.length - 1, index));
  const item = activeItem();
  const state = stateFor(item);
  document.getElementById("sourceImage").src = item.image_src;
  document.getElementById("itemTitle").textContent = `${{item.route42f_id}} / ${{item.target_locus}}`;
  document.getElementById("choiceStatus").textContent = state.zone_status;
  document.getElementById("transcriptionText").innerHTML = item.transcription_visual_html || "sem transcricao";
  document.getElementById("selectedText").textContent = state.selected_visual_line_number
    ? `linha visual ${{state.selected_visual_line_number}} / zona ${{state.selected_zone_box_pct || "sem zona"}}`
    : "sem escolha";
  document.getElementById("manualZoneNotes").value = state.manual_zone_notes || "";
  renderOverlay(item, state);
  renderLineButtons(item, state);
  renderQueue();
  generateCsv();
}}

function selectLine(visualLine) {{
  const item = activeItem();
  const state = stateFor(item);
  state.selected_visual_line_number = visualLine;
  state.selected_zone_box_pct = zoneFromLineNumber(item, visualLine);
  state.zone_status = "zone_selected_pending_opencv";
  writeDraft();
  showItem(currentIndex);
}}

function clearChoice() {{
  const state = stateFor(activeItem());
  state.selected_visual_line_number = "";
  state.selected_zone_box_pct = "";
  state.zone_status = "pending_zone_choice";
  writeDraft();
  showItem(currentIndex);
}}

function generateCsv() {{
  const rows = [FIELDNAMES.join(",")];
  for (const item of ITEMS) {{
    const state = stateFor(item);
    const output = {{ ...item, ...state, semantic_guardrail: "{GUARDRAIL}" }};
    rows.push(FIELDNAMES.map((field) => csvEscape(output[field] || "")).join(","));
  }}
  const text = rows.join("\\n");
  document.getElementById("csvDraft").value = text;
  return text;
}}

async function copyCsv() {{
  const text = generateCsv();
  const textarea = document.getElementById("csvDraft");
  try {{
    await navigator.clipboard.writeText(text);
  }} catch (_error) {{
    textarea.focus();
    textarea.select();
  }}
}}

function downloadCsv() {{
  const text = generateCsv();
  const blob = new Blob([text], {{ type: "text/csv;charset=utf-8" }});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "ready_visual_line_zone_choice_zl3b.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}}

document.getElementById("prevItem").addEventListener("click", () => showItem(currentIndex - 1));
document.getElementById("nextItem").addEventListener("click", () => showItem(currentIndex + 1));
document.getElementById("nextPending").addEventListener("click", () => {{
  const start = currentIndex + 1;
  const next = ITEMS.findIndex((item, index) => index >= start && stateFor(item).zone_status === "pending_zone_choice");
  showItem(next >= 0 ? next : 0);
}});
document.getElementById("clearChoice").addEventListener("click", clearChoice);
document.getElementById("generateCsv").addEventListener("click", generateCsv);
document.getElementById("copyCsv").addEventListener("click", copyCsv);
document.getElementById("downloadCsv").addEventListener("click", downloadCsv);
document.getElementById("manualZoneNotes").addEventListener("input", (event) => {{
  const state = stateFor(activeItem());
  state.manual_zone_notes = event.target.value;
  writeDraft();
  generateCsv();
}});

if (ITEMS.length) {{
  showItem(0);
}} else {{
  document.getElementById("queue").innerHTML = "<p>Nenhum alvo sem zona.</p>";
}}
</script>
</body>
</html>
"""


def render_counts(title: str, counts: Counter[str]) -> list[str]:
    lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"|{key}|{value}|")
    lines.append("")
    return lines


def write_markdown_report(path: Path, rows: list[dict[str, str]], zone_choice_csv: Path, summary_csv: Path, html_path: Path) -> None:
    lines = [
        "# Rota 42F: escolha simples de linhas visuais sem zona",
        "",
        "Esta rota cria uma ferramenta local para resolver os casos em que o OpenCV encontrou linhas na imagem, mas ainda nao sabe qual linha corresponde ao locus ZL3b.",
        "",
        "A escolha gera zonas pequenas para a R42D consumir depois. Ela nao preenche a R32, nao traduz e nao confirma evidencia visual sozinha.",
        "",
        f"CSV: `{zone_choice_csv}`.",
        f"Resumo: `{summary_csv}`.",
        f"HTML: `{html_path}`.",
        "",
        "## Resultado curto",
        "",
        f"- alvos que precisam escolher linha visual: {len(rows)};",
        "- fluxo: abrir a pagina, comparar recortes reais das linhas com o desenho de referencia, clicar no recorte `Essa e a linha`, copiar/baixar o CSV e reexecutar a R42D;",
        f"- guarda: `{GUARDRAIL}`.",
        "",
    ]
    lines.extend(render_counts("Status", Counter(row.get("zone_status", "") for row in rows)))
    lines.extend(render_counts("Folios", Counter(row.get("folio", "") for row in rows)))
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
        "--opencv-suggestions-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_line_opencv_suggestions_zl3b.csv"),
        help="Route 42D OpenCV suggestions CSV",
    )
    parser.add_argument(
        "--line-map-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_line_opencv_map_zl3b.csv"),
        help="Route 42E OpenCV visual-line map CSV",
    )
    parser.add_argument(
        "--zone-choice-csv",
        default=str(ROOT / "data" / "annotations" / "ready_visual_line_zone_choice_zl3b.csv"),
        help="Manual visual-line zone choice CSV, preserved on rerun",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_line_zone_choice_summary_zl3b.csv"),
        help="Route 42F summary CSV",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_42f_escolha_linhas_visuais_sem_zona_r32.md"),
        help="Route 42F Markdown report output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_42f_escolha_linhas_visuais_sem_zona_r32.html"),
        help="Route 42F HTML output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    calibration_csv = Path(args.calibration_csv)
    suggestions_csv = Path(args.opencv_suggestions_csv)
    line_map_csv = Path(args.line_map_csv)
    zone_choice_csv = Path(args.zone_choice_csv)
    summary_csv = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)

    rows = build_zone_choice_rows(
        read_csv(calibration_csv),
        read_csv(suggestions_csv),
        read_csv(line_map_csv),
        read_csv(zone_choice_csv),
    )
    write_csv(zone_choice_csv, rows, FIELDNAMES)
    write_summary_csv(summary_csv, rows)
    write_markdown_report(md_path, rows, zone_choice_csv, summary_csv, html_path)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_html(rows, str(zone_choice_csv)), encoding="utf-8")

    summary = Counter(row.get("zone_status", "") for row in rows)
    print(
        f"zone_choice_items={len(rows)} "
        f"pending={summary.get(ZONE_STATUS_PENDING, 0)} "
        f"selected={summary.get(ZONE_STATUS_SELECTED, 0)}"
    )
    print(f"zone_choice_csv={zone_choice_csv.resolve()}")
    print(f"summary_csv={summary_csv.resolve()}")
    print(f"md={md_path.resolve()}")
    print(f"html={html_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
