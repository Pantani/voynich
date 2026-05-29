#!/usr/bin/env python3
"""Prepare a local baseline calibration tool for route 42B target lines."""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import json
import re
from collections import Counter
from pathlib import Path

try:
    from scripts.eva_visual import EVA_VISUAL_CSS, render_eva_text
    from scripts.visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS
except ImportError:  # pragma: no cover - used when running this file directly from scripts/
    from eva_visual import EVA_VISUAL_CSS, render_eva_text
    from visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "line_calibration_tool_not_visual_evidence"
STORAGE_KEY = "voynich.r42c.lineCalibration"
DRAFT_VERSION = 2
SCAN_SIGNATURE_VERSION = "r42c-scan-signature-v1"
OPENCV_INITIAL_NOTE = "Sugestao OpenCV inicial; confirmar visualmente na R42C antes de marcar calibrada."
RAW_TRANSCRIPTION = ROOT / "data" / "raw" / "ZL3b-n.txt"
LOCUS_TRANSCRIPTION_RE = re.compile(r"^<(?P<locus>[^>]+)>\s+(?:<[^>]*>)?(?P<text>.*)$")
TARGET_LOCUS_RE = re.compile(r"^(?P<folio>f[^.]+)\.(?P<line>\d+),(?P<marker>.+)$")

ALLOWED_CALIBRATION_STATUS = {
    "pending_calibration",
    "calibrated",
    "uncertain",
    "not_calibratable",
}

FIELDNAMES = [
    "route42c_id",
    "route42b_id",
    "route42_id",
    "route42a_id",
    "route32_id",
    "route28_id",
    "folio",
    "priority_level",
    "locus_kind",
    "token_counts",
    "highlight_tokens",
    "target_locus",
    "line_number",
    "marker",
    "transcription_text",
    "manifest_label",
    "yale_image_id",
    "yale_dimensions",
    "local_image_path",
    "yale_iiif_jpg_url",
    "calibration_status",
    "baseline_points",
    "baseline_width_pct",
    "manual_notes",
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


def split_target_loci(value: str) -> list[str]:
    return [part.strip() for part in value.split("|") if part.strip()]


def parse_target_locus(raw: str) -> tuple[str, str, str]:
    match = TARGET_LOCUS_RE.match(raw)
    if not match:
        return "", "", ""
    return match.group("folio"), match.group("line"), match.group("marker")


def token_names(token_counts: str) -> list[str]:
    tokens: list[str] = []
    for part in token_counts.split("|"):
        token = part.split("=", 1)[0].strip()
        if token and token not in tokens:
            tokens.append(token)
    return tokens


def read_transcriptions(path: Path = RAW_TRANSCRIPTION) -> dict[str, str]:
    if not path.exists():
        return {}
    transcriptions: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        match = LOCUS_TRANSCRIPTION_RE.match(line)
        if match:
            transcriptions[match.group("locus")] = match.group("text").strip()
    return transcriptions


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


def existing_calibration_index(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    index: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        key = (row.get("route32_id", ""), row.get("target_locus", ""))
        if key[0] and key[1]:
            index[key] = row
    return index


def preserved_calibration_fields(
    route32_id: str,
    target_locus: str,
    existing: dict[tuple[str, str], dict[str, str]],
) -> dict[str, str]:
    row = existing.get((route32_id, target_locus), {})
    status = row.get("calibration_status", "")
    baseline_points = row.get("baseline_points", "")
    if status not in ALLOWED_CALIBRATION_STATUS:
        status = "pending_calibration"
    valid_baseline = parse_baseline_points(baseline_points)
    if status == "calibrated" and not valid_baseline:
        baseline_points = ""
        status = "pending_calibration"
    elif baseline_points and not valid_baseline:
        baseline_points = ""
        if status == "calibrated":
            status = "pending_calibration"
    return {
        "calibration_status": status or "pending_calibration",
        "baseline_points": baseline_points,
        "baseline_width_pct": row.get("baseline_width_pct", ""),
        "manual_notes": row.get("manual_notes", ""),
    }


def build_line_calibration_rows(
    r42b_rows: list[dict[str, str]],
    transcriptions: dict[str, str],
    existing_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    existing = existing_calibration_index(existing_rows)
    rows: list[dict[str, str]] = []
    for source in r42b_rows:
        tokens = "|".join(token_names(source.get("token_counts", "")))
        for raw_locus in split_target_loci(source.get("top_loci", "")):
            locus_folio, line_number, marker = parse_target_locus(raw_locus)
            preserved = preserved_calibration_fields(source.get("route32_id", ""), raw_locus, existing)
            rows.append(
                {
                    "route42c_id": f"R42C-{len(rows) + 1:03d}",
                    "route42b_id": source.get("route42b_id", ""),
                    "route42_id": source.get("route42_id", ""),
                    "route42a_id": source.get("route42a_id", ""),
                    "route32_id": source.get("route32_id", ""),
                    "route28_id": source.get("route28_id", ""),
                    "folio": locus_folio or source.get("folio", ""),
                    "priority_level": source.get("priority_level", ""),
                    "locus_kind": source.get("locus_kind", ""),
                    "token_counts": source.get("token_counts", ""),
                    "highlight_tokens": tokens,
                    "target_locus": raw_locus,
                    "line_number": line_number,
                    "marker": marker,
                    "transcription_text": transcriptions.get(raw_locus, ""),
                    "manifest_label": source.get("manifest_label", ""),
                    "yale_image_id": source.get("yale_image_id", ""),
                    "yale_dimensions": source.get("yale_dimensions", ""),
                    "local_image_path": source.get("local_image_path", ""),
                    "yale_iiif_jpg_url": source.get("yale_iiif_jpg_url", ""),
                    "semantic_guardrail": GUARDRAIL,
                    **preserved,
                }
            )
    return rows


def summarize_line_calibration_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "folio": Counter(row.get("folio", "") for row in rows),
        "calibration_status": Counter(row.get("calibration_status", "") for row in rows),
        "baseline_points": Counter(
            "with_baseline_points" if parse_baseline_points(row.get("baseline_points", "")) else "missing_baseline_points"
            for row in rows
        ),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "semantic_guardrail": Counter(row.get("semantic_guardrail", "") for row in rows),
    }


def opencv_suggestion_index(rows: list[dict[str, str]]) -> dict[tuple[str, str], dict[str, str]]:
    index: dict[tuple[str, str], dict[str, str]] = {}
    for row in rows:
        if row.get("suggestion_status") != "opencv_suggested_needs_human_confirmation":
            continue
        points = row.get("suggested_baseline_points", "")
        if not parse_baseline_points(points):
            continue
        route32_id = row.get("route32_id", "")
        target_locus = row.get("target_locus", "")
        if route32_id and target_locus:
            index[(route32_id, target_locus)] = row
    return index


def merge_opencv_suggestions_into_calibration_rows(
    rows: list[dict[str, str]],
    suggestions: dict[tuple[str, str], dict[str, str]],
) -> list[dict[str, str]]:
    def notes_without_opencv_draft_note(value: str) -> str:
        marker = value.find(OPENCV_INITIAL_NOTE)
        if marker < 0:
            return value.strip()
        return value[:marker].strip()

    merged: list[dict[str, str]] = []
    for row in rows:
        next_row = dict(row)
        key = (next_row.get("route32_id", ""), next_row.get("target_locus", ""))
        suggestion = suggestions.get(key)
        manual_notes = next_row.get("manual_notes", "").strip()
        is_opencv_draft = OPENCV_INITIAL_NOTE in manual_notes
        if (
            suggestion
            and next_row.get("calibration_status") == "pending_calibration"
            and (not next_row.get("baseline_points", "").strip() or is_opencv_draft)
        ):
            points = suggestion.get("suggested_baseline_points", "").strip()
            if parse_baseline_points(points):
                next_row["baseline_points"] = points
                if not next_row.get("baseline_width_pct", "").strip():
                    next_row["baseline_width_pct"] = "1.20"
                confidence = suggestion.get("suggestion_confidence", "").strip()
                visual_line = suggestion.get("suggested_visual_line_number", "").strip()
                note = OPENCV_INITIAL_NOTE
                if visual_line:
                    note = f"{note} Linha visual OpenCV: {visual_line}."
                if confidence:
                    note = f"{note} Confianca OpenCV: {confidence}."
                auto_action = suggestion.get("opencv_auto_action", "").strip() or "prefill_pending_baseline"
                note = f"{note} Acao OpenCV: {auto_action}."
                manual_notes = notes_without_opencv_draft_note(manual_notes)
                next_row["manual_notes"] = f"{manual_notes} {note}".strip() if manual_notes else note
        merged.append(next_row)
    return merged


def highlight_transcription(text: str, tokens: str) -> str:
    return render_eva_text(text, highlight_tokens=tokens, compact=True)


def html_image_src(local_image_path: str) -> str:
    if not local_image_path:
        return ""
    return "../" + local_image_path.lstrip("/")


def display_path(path: str | Path) -> str:
    value = Path(path)
    try:
        return str(value.relative_to(ROOT))
    except ValueError:
        return str(value)


def scan_signature_for_payload(payload: dict[str, str]) -> str:
    parts = [
        SCAN_SIGNATURE_VERSION,
        payload.get("route32_id", ""),
        payload.get("target_locus", ""),
        payload.get("local_image_path", ""),
        payload.get("yale_image_id", ""),
        payload.get("opencv_suggestion_visual_line_number", ""),
        payload.get("opencv_suggestion_baseline_points", ""),
        payload.get("baseline_points", ""),
    ]
    return hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()[:16]


def render_html(
    rows: list[dict[str, str]],
    calibration_csv: str,
    opencv_suggestions: dict[tuple[str, str], dict[str, str]] | None = None,
) -> str:
    opencv_suggestions = opencv_suggestions or {}
    payload_rows = []
    for row in rows:
        payload = dict(row)
        payload["image_src"] = html_image_src(row.get("local_image_path", ""))
        payload["transcription_html"] = highlight_transcription(
            row.get("transcription_text", ""), row.get("highlight_tokens", "")
        )
        suggestion = opencv_suggestions.get((row.get("route32_id", ""), row.get("target_locus", "")))
        if suggestion:
            payload["opencv_suggestion_baseline_points"] = suggestion.get("suggested_baseline_points", "")
            payload["opencv_suggestion_visual_line_number"] = suggestion.get("suggested_visual_line_number", "")
            payload["opencv_suggestion_confidence"] = suggestion.get("suggestion_confidence", "")
            payload["opencv_suggestion_status"] = suggestion.get("suggestion_status", "")
            payload["opencv_auto_action"] = suggestion.get("opencv_auto_action", "")
            payload["opencv_human_next_step"] = suggestion.get("human_next_step", "")
            payload["opencv_confidence_band"] = suggestion.get("automation_confidence_band", "")
        else:
            payload["opencv_suggestion_baseline_points"] = ""
            payload["opencv_suggestion_visual_line_number"] = ""
            payload["opencv_suggestion_confidence"] = ""
            payload["opencv_suggestion_status"] = ""
            payload["opencv_auto_action"] = ""
            payload["opencv_human_next_step"] = ""
            payload["opencv_confidence_band"] = ""
        payload["scan_signature"] = scan_signature_for_payload(payload)
        payload_rows.append(payload)
    rows_json = json.dumps(payload_rows, ensure_ascii=True)
    fieldnames_json = json.dumps(FIELDNAMES)
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rota 42C - Calibrador de linhas R32</title>
  <style>
    :root {{
      --paper: #f8f3ea;
      --panel: #fffaf2;
      --line: #d7cabb;
      --ink: #241f1a;
      --muted: #6f675f;
      --accent: #8f3f33;
      --accent-2: #1f7668;
      --focus: #e7b657;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; overflow-y: auto; background: var(--paper); color: var(--ink); font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; }}
    button, textarea, input, select {{ font: inherit; }}
    button {{ border: 1px solid #c8baaa; border-radius: 7px; background: #fffaf2; color: var(--ink); padding: 9px 12px; font-weight: 700; cursor: pointer; }}
    button:hover {{ background: #f1e7d8; }}
    button.primary {{ border-color: var(--accent-2); background: var(--accent-2); color: #f8fbfa; }}
    button.danger {{ color: #7c3029; }}
    .button-link {{ display: inline-flex; align-items: center; min-height: 38px; border: 1px solid #c8baaa; border-radius: 7px; background: #fffaf2; color: var(--ink); padding: 0 12px; font-weight: 700; text-decoration: none; }}
    .button-link:hover {{ background: #f1e7d8; }}
    .app {{ display: grid; grid-template-rows: auto auto minmax(0, 1fr); min-height: 100vh; }}
    .topbar {{ display: flex; align-items: center; justify-content: space-between; gap: 16px; padding: 12px 16px; border-bottom: 1px solid var(--line); background: #fbf6ed; }}
    .topbar h1 {{ margin: 0; font-size: 18px; }}
    .topbar p {{ margin: 2px 0 0; color: var(--muted); }}
    .top-actions {{ display: inline-flex; align-items: center; gap: 8px; }}
    .counter {{ padding: 5px 10px; border: 1px solid var(--line); border-radius: 999px; background: var(--panel); font-weight: 800; white-space: nowrap; }}
    .progress-text {{ padding: 5px 10px; border: 1px solid var(--line); border-radius: 999px; background: #eef6f2; color: #164f47; font-weight: 900; white-space: nowrap; }}
    .toolbar {{ display: flex; gap: 8px; align-items: center; padding: 10px 16px; border-bottom: 1px solid var(--line); background: #eee4d5; overflow-x: auto; }}
    .workspace {{ display: grid; grid-template-columns: 280px minmax(0, 1fr) 390px; min-height: 0; }}
    .queue {{ overflow: auto; border-right: 1px solid var(--line); background: #f2e8d9; padding: 10px; }}
    .queue button {{ width: 100%; display: grid; gap: 2px; margin-bottom: 7px; text-align: left; background: var(--panel); }}
    .queue button.active {{ outline: 3px solid rgba(231, 182, 87, 0.55); border-color: var(--accent); }}
    .queue small {{ color: var(--muted); }}
    .image-panel {{ min-width: 0; min-height: 0; overflow: auto; padding: 72px 72px 120px; scroll-padding: 72px; overscroll-behavior: auto; background: #e5dccf; }}
    .image-stage {{ position: relative; display: inline-grid; background: #1c1b19; border-radius: 8px; overflow: hidden; box-shadow: 0 1px 0 rgba(0,0,0,0.08); }}
    .image-stage img {{ grid-area: 1 / 1; display: block; width: clamp(520px, calc(100vw - 720px), 980px); max-width: 100%; height: auto; user-select: none; }}
    .baseline-svg {{ grid-area: 1 / 1; position: absolute; inset: 0; width: 100%; height: 100%; cursor: crosshair; }}
    .baseline-line {{ fill: none; stroke: rgba(31, 118, 104, 0.95); stroke-width: 0.45; vector-effect: non-scaling-stroke; }}
    .baseline-hit {{ fill: none; stroke: rgba(231, 182, 87, 0.45); stroke-width: 2.2; vector-effect: non-scaling-stroke; }}
    .baseline-suggestion {{ fill: none; stroke: rgba(31, 118, 104, 0.82); stroke-width: 0.42; stroke-dasharray: 1.4 1.1; vector-effect: non-scaling-stroke; }}
    .baseline-draft {{ fill: none; stroke: rgba(143, 63, 51, 0.92); stroke-width: 0.45; stroke-dasharray: 1.8 1.1; vector-effect: non-scaling-stroke; }}
    .baseline-point {{ fill: #fffaf2; stroke: var(--accent-2); stroke-width: 0.45; vector-effect: non-scaling-stroke; }}
    .tracking-crosshair {{ stroke: rgba(231, 182, 87, 0.95); stroke-width: 0.32; stroke-dasharray: 0.8 0.9; vector-effect: non-scaling-stroke; pointer-events: none; }}
    .side {{ overflow: auto; border-left: 1px solid var(--line); background: var(--panel); padding: 14px; }}
    .eyebrow {{ margin: 0 0 3px; color: var(--accent-2); font-size: 11px; font-weight: 900; letter-spacing: .03em; text-transform: uppercase; }}
    .side h2 {{ margin: 0; font-size: 21px; line-height: 1.15; }}
    .plain-box {{ margin-top: 12px; padding: 12px; border: 1px solid var(--line); border-radius: 8px; background: #fff7ea; }}
    .plain-box h3 {{ margin: 0 0 8px; font-size: 14px; }}
    .plain-box p {{ margin: 0; color: var(--muted); }}
    .guide-box {{ border-color: #b5d2cb; background: #eef6f2; }}
    .guide-title {{ color: var(--ink) !important; font-size: 18px; font-weight: 900; line-height: 1.2; }}
    .guide-step {{ margin-top: 7px !important; font-size: 15px; color: #31544e !important; }}
    .tracking-box p + p {{ margin-top: 5px; }}
    .suggestion-box {{ margin-top: 12px; padding: 12px; border: 1px dashed var(--accent-2); border-radius: 8px; background: #eef6f2; }}
    .suggestion-box h3 {{ margin: 0 0 8px; font-size: 14px; }}
    .suggestion-box p {{ margin: 0 0 8px; color: var(--muted); }}
    .decision-row {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; margin-top: 10px; }}
    .decision-row .wide {{ grid-column: 1 / -1; }}
    .fine-row {{ display: flex; align-items: center; justify-content: space-between; gap: 10px; margin-top: 8px; }}
    .fine-row select {{ min-height: 34px; border: 1px solid var(--line); border-radius: 7px; background: #fffef9; color: var(--ink); padding: 0 8px; }}
    .fine-targets {{ display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 6px; margin-top: 8px; }}
    .fine-targets button {{ padding: 8px 6px; font-size: 12px; }}
    .fine-targets button.active {{ border-color: var(--accent-2); background: #eef6f2; color: #164f47; }}
    .nudge-grid {{ display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 6px; margin-top: 8px; }}
    .nudge-grid button {{ min-height: 36px; }}
    .status-pill {{ display: inline-flex; align-items: center; gap: 6px; margin-top: 8px; padding: 4px 8px; border: 1px solid var(--line); border-radius: 999px; background: #fbf6ed; color: var(--muted); font-weight: 800; }}
    .warning {{ margin-top: 8px; color: #7c3029; font-weight: 800; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; }}
    .transcription {{ overflow-wrap: anywhere; }}
    mark {{ background: rgba(231, 182, 87, 0.55); padding: 0 2px; border-radius: 3px; }}
{EVA_VISUAL_CSS}
{VISUAL_CROP_CSS}
    .line-preview-crop {{ margin-top: 8px; }}
    textarea {{ width: 100%; min-height: 82px; resize: vertical; border: 1px solid var(--line); border-radius: 8px; background: #fffef9; color: var(--ink); padding: 9px; }}
    details {{ margin-top: 12px; }}
    summary {{ cursor: pointer; font-weight: 900; }}
    #csvDraft {{ min-height: 180px; white-space: pre; }}
    .empty {{ padding: 24px; color: var(--muted); }}
  </style>
</head>
<body>
<div class="app">
  <header class="topbar">
    <div>
      <h1>Rota 42C</h1>
      <p>Calibrar linhas reais por baseline. Isto nao traduz e nao preenche a R32.</p>
    </div>
    <div class="top-actions">
      <a class="button-link" id="openActiveTools" href="rota_42g_ferramentas_ativas_r32.html">Ferramentas ativas</a>
      <a class="button-link" id="openR42B" href="rota_42b_pacote_html_preenchimento_humano_r32.html">Abrir R42B</a>
      <a class="button-link" id="openR42D" href="rota_42d_sugestoes_opencv_linhas_r32.html">Abrir sugestoes OpenCV</a>
      <a class="button-link" id="openR42E" href="rota_42e_mapa_opencv_linhas_visuais_r32.html">Abrir mapa OpenCV</a>
      <a class="button-link" id="openR42J" href="rota_42j_fragmentos_visuais_opencv_r32.html">Abrir fragmentos</a>
      <a class="button-link" id="openR42F" href="rota_42f_escolha_linhas_visuais_sem_zona_r32.html">Abrir escolha de linhas</a>
      <div class="progress-text" id="progressText">0 prontas</div>
      <div class="counter" id="counter">0 de 0</div>
    </div>
  </header>
  <nav class="toolbar" aria-label="Controles">
    <button type="button" id="prevItem">Anterior</button>
    <button type="button" id="nextItem">Proxima</button>
    <button type="button" id="nextPending">Proxima pendente</button>
    <button type="button" id="undoPoint">Desfazer ponto</button>
    <button type="button" id="clearPoints" class="danger">Limpar pontos</button>
    <button type="button" id="scrollImageTop">Topo da imagem</button>
    <button type="button" id="resetLocalScan" class="danger">Resetar scan local</button>
    <button type="button" id="generateCsv">Gerar CSV</button>
    <button type="button" id="copyCsv">Copiar CSV</button>
    <button type="button" id="downloadCsv">Baixar CSV</button>
  </nav>
  <main class="workspace">
    <aside class="queue" id="queue" aria-label="Linhas para calibrar"></aside>
    <section class="image-panel" id="imagePanel" aria-label="Imagem high-res">
      <div class="image-stage" id="imageStage">
        <img id="sourceImage" alt="Imagem high-res da linha alvo">
        <svg id="baselineSvg" class="baseline-svg" viewBox="0 0 100 100" preserveAspectRatio="none" aria-label="Clique no comeco e no fim da linha real"></svg>
      </div>
    </section>
    <aside class="side" aria-label="Painel de calibracao">
      <p class="eyebrow">Calibrar linha</p>
      <h2 id="itemTitle">Selecione uma linha</h2>
      <span class="status-pill" id="statusPill">pendente</span>
      <div class="plain-box guide-box">
        <h3>Guia rapido</h3>
        <p class="guide-title" id="stepGuideTitle">Vamos com calma</p>
        <p class="guide-step" id="stepGuideText">Agora clique no comeco da linha.</p>
        <p class="mono" id="pointCountText">0 de 2 pontos</p>
      </div>
      <div class="plain-box tracking-box">
        <h3>Rastreamento</h3>
        <p class="mono" id="mousePositionText">Mira fora da imagem</p>
        <p class="mono" id="lastClickText">Nenhum clique ainda</p>
      </div>
      <div class="plain-box">
        <h3>O que fazer</h3>
        <p>Clique no comeco e no fim da linha real na imagem. Se a linha for torta, use os dois pontos que melhor representam a base do texto.</p>
      </div>
      <div class="plain-box">
        <h3>Texto de referencia visual</h3>
        <div class="transcription" id="transcription"></div>
      </div>
      <div class="plain-box">
        <h3>Lupa da linha</h3>
        <p>Este recorte vem dos pontos atuais ou da sugestao OpenCV. Use para conferir sem procurar a pagina inteira.</p>
        <article class="visual-crop-card line-preview-crop">
          <span class="visual-crop-label" id="linePreviewLabel">sem recorte ainda</span>
          <canvas class="visual-crop-canvas" id="linePreviewCanvas" data-crop-preview aria-label="lupa da linha atual"></canvas>
          <span class="visual-crop-note" id="linePreviewNote">adicione dois pontos ou use uma sugestao para ver o recorte</span>
        </article>
      </div>
      <div class="plain-box">
        <h3>Pontos da baseline</h3>
        <p class="mono" id="pointsText">sem pontos</p>
        <p class="mono" id="scanSignatureText">scan sem assinatura</p>
        <p class="warning" id="calibrationWarning" hidden>Precisa de dois pontos para marcar como calibrada.</p>
        <p class="warning" id="draftWarning" hidden>Pontos em rascunho; confira na imagem e marque calibrada so depois de ajustar.</p>
      </div>
      <div class="plain-box">
        <h3>Ajuste fino</h3>
        <p>Depois de ter dois pontos, mova a linha ou apenas uma ponta em passos pequenos.</p>
        <div class="fine-row">
          <label for="fineStep">Passo</label>
          <select id="fineStep">
            <option value="0.10">0.10%</option>
            <option value="0.25" selected>0.25%</option>
            <option value="0.50">0.50%</option>
            <option value="1.00">1.00%</option>
          </select>
        </div>
        <div class="fine-targets" aria-label="Escolher parte da baseline para ajustar">
          <button type="button" data-fine-target="line" class="active">Linha inteira</button>
          <button type="button" data-fine-target="left">Ponto esquerdo</button>
          <button type="button" data-fine-target="right">Ponto direito</button>
        </div>
        <div class="nudge-grid" aria-label="Mover baseline">
          <button type="button" data-nudge-dx="-1" data-nudge-dy="0">Esquerda</button>
          <button type="button" data-nudge-dx="1" data-nudge-dy="0">Direita</button>
          <button type="button" data-nudge-dx="0" data-nudge-dy="-1">Cima</button>
          <button type="button" data-nudge-dx="0" data-nudge-dy="1">Baixo</button>
        </div>
        <p class="warning" id="fineTuneWarning" hidden>Clique nos dois pontos antes de ajustar.</p>
      </div>
      <div class="suggestion-box" id="opencvSuggestionBox" hidden>
        <h3>Computador ja ajudou (Sugestao OpenCV)</h3>
        <p id="opencvSuggestionText">sem sugestao</p>
        <p id="opencvAutoActionText">sem acao automatica</p>
        <p id="opencvHumanStepText">sem proximo passo</p>
        <button type="button" id="useOpenCvSuggestion">Recolocar sugestao</button>
        <p>A sugestao nao marca calibrada sozinha. Ela e uma linha visual candidata, nao palavra encontrada. Confira na imagem antes de marcar.</p>
      </div>
      <div class="decision-row">
        <button type="button" id="markCalibrated" class="primary">Marcar calibrada</button>
        <button type="button" id="markUncertain">Incerta</button>
        <button type="button" id="markNotCalibratable" class="wide">Nao calibravel</button>
      </div>
      <div class="plain-box">
        <h3>Nota manual da calibracao</h3>
        <textarea id="manualNotes" placeholder="Ex.: baseline no texto acima da faixa verde, ponto inicial ajustado pela margem."></textarea>
      </div>
      <details>
        <summary>Rascunho CSV para {html.escape(calibration_csv)}</summary>
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
const DRAFT_VERSION = {DRAFT_VERSION};
let currentIndex = 0;
let draft = readDraft();
let nudgeFineTarget = "line";

{VISUAL_CROP_JS}

function csvEscape(value) {{
  const text = value == null ? "" : String(value);
  return /[",\\n\\r]/.test(text) ? '"' + text.replaceAll('"', '""') + '"' : text;
}}

function readDraft() {{
  try {{
    const raw = JSON.parse(localStorage.getItem(STORAGE_KEY) || "{{}}");
    return raw.__version === DRAFT_VERSION ? raw : {{ __version: DRAFT_VERSION }};
  }} catch (_error) {{
    return {{ __version: DRAFT_VERSION }};
  }}
}}

function writeDraft() {{
  localStorage.setItem(STORAGE_KEY, JSON.stringify(draft));
}}

function keyFor(item) {{
  return `${{item.route32_id}}::${{item.target_locus}}`;
}}

function expectedSignatureFor(item) {{
  return item.scan_signature || "";
}}

function freshStateFor(item) {{
  const expectedSignature = expectedSignatureFor(item);
  return {{
    calibration_status: item.calibration_status || "pending_calibration",
    baseline_points: item.baseline_points || "",
    baseline_width_pct: item.baseline_width_pct || "1.20",
    manual_notes: item.manual_notes || "",
    __scan_signature: expectedSignature
  }};
}}

function isManualUserState(state) {{
  return state.calibration_status === "calibrated"
    && calibratedRequiresBaseline(state);
}}

function stateFor(item) {{
  const key = keyFor(item);
  const expectedSignature = expectedSignatureFor(item);
  let changed = false;
  if (!draft[key]) {{
    draft[key] = freshStateFor(item);
    changed = true;
  }} else if ((draft[key].__scan_signature || "") !== expectedSignature) {{
    if (isManualUserState(draft[key])) {{
      draft[key].__scan_signature = expectedSignature;
    }} else {{
      draft[key] = freshStateFor(item);
    }}
    changed = true;
  }}
  const beforeNormalize = JSON.stringify(draft[key]);
  normalizeState(draft[key]);
  if (JSON.stringify(draft[key]) !== beforeNormalize) {{
    changed = true;
  }}
  if ((draft[key].__scan_signature || "") !== expectedSignature) {{
    draft[key].__scan_signature = expectedSignature;
    changed = true;
  }}
  if (changed) writeDraft();
  return draft[key];
}}

function calibratedRequiresBaseline(state) {{
  return parsePoints(state.baseline_points).length >= 2;
}}

function normalizeState(state) {{
  if (state.calibration_status === "calibrated" && !calibratedRequiresBaseline(state)) {{
    state.calibration_status = "pending_calibration";
    state.baseline_points = "";
  }}
}}

function parsePoints(value) {{
  if (!value) return [];
  const points = [];
  for (const pair of value.trim().split(/\\s+/)) {{
    const bits = pair.split(",");
    if (bits.length !== 2) return [];
    const x = Number(bits[0]);
    const y = Number(bits[1]);
    if (!Number.isFinite(x) || !Number.isFinite(y) || x < 0 || x > 100 || y < 0 || y > 100) return [];
    points.push([x, y]);
  }}
  return points.length >= 2 ? points : points;
}}

function clampPercent(value) {{
  return Math.max(0, Math.min(100, value));
}}

function formatPoints(points) {{
  return points.map(([x, y]) => `${{x.toFixed(2)}},${{y.toFixed(2)}}`).join(" ");
}}

function pointerPercentFromEvent(event) {{
  const rect = event.currentTarget.getBoundingClientRect();
  return {{
    x: clampPercent(((event.clientX - rect.left) / rect.width) * 100),
    y: clampPercent(((event.clientY - rect.top) / rect.height) * 100)
  }};
}}

function formatPointLabel(point) {{
  return `${{point.x.toFixed(2)}}%, ${{point.y.toFixed(2)}}%`;
}}

function ensureTrackingCrosshair() {{
  const svg = document.getElementById("baselineSvg");
  let horizontal = document.getElementById("trackingCrosshairHorizontal");
  let vertical = document.getElementById("trackingCrosshairVertical");
  if (!horizontal) {{
    horizontal = document.createElementNS("http://www.w3.org/2000/svg", "line");
    horizontal.setAttribute("id", "trackingCrosshairHorizontal");
    horizontal.setAttribute("class", "tracking-crosshair");
    horizontal.hidden = true;
    svg.appendChild(horizontal);
  }}
  if (!vertical) {{
    vertical = document.createElementNS("http://www.w3.org/2000/svg", "line");
    vertical.setAttribute("id", "trackingCrosshairVertical");
    vertical.setAttribute("class", "tracking-crosshair");
    vertical.hidden = true;
    svg.appendChild(vertical);
  }}
  return {{ horizontal, vertical }};
}}

function setTrackingCrosshair(point) {{
  const {{ horizontal, vertical }} = ensureTrackingCrosshair();
  if (!point) {{
    horizontal.hidden = true;
    vertical.hidden = true;
    return;
  }}
  horizontal.hidden = false;
  vertical.hidden = false;
  horizontal.setAttribute("x1", "0");
  horizontal.setAttribute("y1", String(point.y));
  horizontal.setAttribute("x2", "100");
  horizontal.setAttribute("y2", String(point.y));
  vertical.setAttribute("x1", String(point.x));
  vertical.setAttribute("y1", "0");
  vertical.setAttribute("x2", String(point.x));
  vertical.setAttribute("y2", "100");
}}

function updateMouseTracking(event) {{
  const point = pointerPercentFromEvent(event);
  document.getElementById("mousePositionText").textContent = `Mira: ${{formatPointLabel(point)}}`;
  setTrackingCrosshair(point);
}}

function hideMouseTracking() {{
  document.getElementById("mousePositionText").textContent = "Mira fora da imagem";
  setTrackingCrosshair(null);
}}

function updateProgressSummary() {{
  const done = ITEMS.filter((item) => stateFor(item).calibration_status !== "pending_calibration").length;
  document.getElementById("progressText").textContent = `${{done}} de ${{ITEMS.length}} prontas`;
}}

function updateStepGuide(item, state) {{
  const points = parsePoints(state.baseline_points);
  const status = state.calibration_status;
  const title = document.getElementById("stepGuideTitle");
  const text = document.getElementById("stepGuideText");
  const count = document.getElementById("pointCountText");
  count.textContent = `${{Math.min(points.length, 2)}} de 2 pontos`;
  if (status === "calibrated") {{
    title.textContent = "Linha pronta";
    text.textContent = "Confira se a linha acompanha o texto e siga para a proxima.";
    return;
  }}
  if (status === "uncertain") {{
    title.textContent = "Linha marcada como incerta";
    text.textContent = "Siga para a proxima ou ajuste os pontos se quiser tentar de novo.";
    return;
  }}
  if (status === "not_calibratable") {{
    title.textContent = "Linha nao calibravel";
    text.textContent = "Siga para a proxima linha da fila.";
    return;
  }}
  if (points.length === 0) {{
    title.textContent = "1. Primeiro ponto";
    text.textContent = "Agora clique no comeco da linha.";
    return;
  }}
  if (points.length === 1) {{
    title.textContent = "2. Segundo ponto";
    text.textContent = "Agora clique no fim da linha.";
    return;
  }}
  title.textContent = "3. Conferir e ajustar";
  text.textContent = "Use o ajuste fino; se a linha estiver certa, marque calibrada.";
}}

function fineStepValue() {{
  const step = Number(document.getElementById("fineStep").value);
  return Number.isFinite(step) && step > 0 ? step : 0.25;
}}

function updateFineTargetButtons() {{
  document.querySelectorAll("[data-fine-target]").forEach((button) => {{
    button.classList.toggle("active", button.dataset.fineTarget === nudgeFineTarget);
  }});
}}

function setFineTarget(target) {{
  nudgeFineTarget = ["line", "left", "right"].includes(target) ? target : "line";
  updateFineTargetButtons();
}}

function nudgeBaseline(dx, dy) {{
  const state = stateFor(activeItem());
  const points = parsePoints(state.baseline_points);
  const warning = document.getElementById("fineTuneWarning");
  if (points.length < 2) {{
    warning.hidden = false;
    return;
  }}
  warning.hidden = true;
  const step = fineStepValue();
  updateActiveState((nextState) => {{
    const nextPoints = parsePoints(nextState.baseline_points);
    const targetIndexes = nudgeFineTarget === "left" ? [0] : nudgeFineTarget === "right" ? [1] : [0, 1];
    for (const index of targetIndexes) {{
      nextPoints[index] = [
        clampPercent(nextPoints[index][0] + dx * step),
        clampPercent(nextPoints[index][1] + dy * step)
      ];
    }}
    nextState.baseline_points = formatPoints(nextPoints);
  }});
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
    button.innerHTML = `<b>${{item.route42c_id}} / linha ${{item.line_number}}</b><small>${{item.folio}} - ${{state.calibration_status}}</small>`;
    button.addEventListener("click", () => showItem(index));
    queue.appendChild(button);
  }});
}}

function drawBaseline() {{
  const item = activeItem();
  const state = stateFor(item);
  const points = parsePoints(state.baseline_points);
  const suggestionPoints = parsePoints(item.opencv_suggestion_baseline_points || "");
  const svg = document.getElementById("baselineSvg");
  svg.innerHTML = "";
  if (!points.length && suggestionPoints.length >= 2) {{
    const suggestion = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
    suggestion.setAttribute("points", suggestionPoints.map(([x, y]) => `${{x}},${{y}}`).join(" "));
    suggestion.setAttribute("class", "baseline-suggestion");
    svg.appendChild(suggestion);
  }}
  if (!points.length) return;
  const polylinePoints = points.map(([x, y]) => `${{x}},${{y}}`).join(" ");
  if (points.length >= 2) {{
    const hit = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
    hit.setAttribute("points", polylinePoints);
    hit.setAttribute("class", "baseline-hit");
    svg.appendChild(hit);
    const line = document.createElementNS("http://www.w3.org/2000/svg", "polyline");
    line.setAttribute("points", polylinePoints);
    line.setAttribute("class", state.calibration_status === "calibrated" ? "baseline-line" : "baseline-draft");
    svg.appendChild(line);
  }}
  for (const [x, y] of points) {{
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", String(x));
    circle.setAttribute("cy", String(y));
    circle.setAttribute("r", "1.25");
    circle.setAttribute("class", "baseline-point");
    svg.appendChild(circle);
  }}
  ensureTrackingCrosshair();
}}

function updateLinePreview(item, state) {{
  const canvas = document.getElementById("linePreviewCanvas");
  const label = document.getElementById("linePreviewLabel");
  const note = document.getElementById("linePreviewNote");
  const points = state.baseline_points || item.opencv_suggestion_baseline_points || "";
  const box = cropBoxFromPoints(points, 3.8, 2.2);
  canvas.dataset.imageSrc = item.image_src || item.yale_iiif_jpg_url || "";
  canvas.dataset.boxPct = box;
  if (box) {{
    label.textContent = state.baseline_points ? "recorte pelos pontos atuais" : "recorte pela sugestao OpenCV";
    note.textContent = "confira se a linha verde acompanha a base do texto";
    paintCropPreviews(document.getElementById("linePreviewCanvas").parentElement);
  }} else {{
    label.textContent = "sem recorte ainda";
    note.textContent = "adicione dois pontos ou use uma sugestao para ver o recorte";
    canvas.removeAttribute("data-box-pct");
    canvas.closest(".visual-crop-card").dataset.cropStatus = "";
    const ctx = canvas.getContext("2d");
    ctx.clearRect(0, 0, canvas.width, canvas.height);
  }}
}}

function statusLabel(value) {{
  if (value === "calibrated") return "calibrada";
  if (value === "uncertain") return "incerta";
  if (value === "not_calibratable") return "nao calibravel";
  return "pendente";
}}

function showItem(index) {{
  if (!ITEMS.length) return;
  currentIndex = Math.max(0, Math.min(ITEMS.length - 1, index));
  const item = activeItem();
  const state = stateFor(item);
  document.getElementById("counter").textContent = `${{currentIndex + 1}} de ${{ITEMS.length}}`;
  document.getElementById("itemTitle").textContent = `${{item.route42c_id}} / ${{item.target_locus}}`;
  document.getElementById("statusPill").textContent = statusLabel(state.calibration_status);
  updateProgressSummary();
  updateStepGuide(item, state);
  document.getElementById("sourceImage").src = item.image_src || item.yale_iiif_jpg_url;
  document.getElementById("transcription").innerHTML = item.transcription_html || "sem transcricao encontrada";
  document.getElementById("pointsText").textContent = state.baseline_points || "sem pontos";
  document.getElementById("scanSignatureText").textContent = item.scan_signature ? `scan ${{item.scan_signature}}` : "scan sem assinatura";
  document.getElementById("mousePositionText").textContent = "Mira fora da imagem";
  document.getElementById("lastClickText").textContent = "Nenhum clique neste item";
  document.getElementById("calibrationWarning").hidden = true;
  document.getElementById("draftWarning").hidden = !(state.baseline_points && state.calibration_status !== "calibrated");
  document.getElementById("fineTuneWarning").hidden = true;
  const suggestionBox = document.getElementById("opencvSuggestionBox");
  const suggestionText = document.getElementById("opencvSuggestionText");
  const autoActionText = document.getElementById("opencvAutoActionText");
  const humanStepText = document.getElementById("opencvHumanStepText");
  if (item.opencv_suggestion_baseline_points) {{
    suggestionBox.hidden = false;
    const visualLine = item.opencv_suggestion_visual_line_number ? `linha visual OpenCV ${{item.opencv_suggestion_visual_line_number}}; ` : "";
    suggestionText.textContent = `${{visualLine}}baseline sugerida: ${{item.opencv_suggestion_baseline_points}}; confianca ${{item.opencv_suggestion_confidence || "n/a"}}`;
    const autoAction = item.opencv_auto_action || "prefill_pending_baseline";
    if (autoAction === "prefill_pending_baseline") {{
      autoActionText.textContent = "Ele colocou uma linha em rascunho. Voce so precisa conferir.";
    }} else {{
      autoActionText.textContent = `Acao OpenCV: ${{autoAction}}`;
    }}
    const band = item.opencv_confidence_band ? ` confianca ${{item.opencv_confidence_band}}.` : "";
    humanStepText.textContent = `${{item.opencv_human_next_step || "confira visualmente antes de aceitar."}}${{band}}`;
  }} else {{
    suggestionBox.hidden = true;
    suggestionText.textContent = "sem sugestao";
    autoActionText.textContent = "sem acao automatica";
    humanStepText.textContent = "sem proximo passo";
  }}
  document.getElementById("manualNotes").value = state.manual_notes || "";
  updateFineTargetButtons();
  drawBaseline();
  updateLinePreview(item, state);
  renderQueue();
  generateCsv();
}}

function updateActiveState(mutator) {{
  const item = activeItem();
  const state = stateFor(item);
  mutator(state);
  writeDraft();
  showItem(currentIndex);
}}

function addPointFromEvent(event) {{
  const point = pointerPercentFromEvent(event);
  updateActiveState((state) => {{
    const points = parsePoints(state.baseline_points);
    const next = points.length >= 2 ? [[point.x, point.y]] : [...points, [point.x, point.y]];
    state.baseline_points = formatPoints(next);
    if (next.length >= 2 && state.calibration_status === "pending_calibration") {{
      state.calibration_status = "calibrated";
    }}
  }});
  document.getElementById("lastClickText").textContent = `Ultimo clique: ${{formatPointLabel(point)}}`;
}}

function setStatus(status) {{
  updateActiveState((state) => {{
    if (status === "calibrated" && !calibratedRequiresBaseline(state)) {{
      document.getElementById("calibrationWarning").hidden = false;
      state.calibration_status = "pending_calibration";
      return;
    }}
    state.calibration_status = status;
  }});
}}

function useOpenCvSuggestion() {{
  const item = activeItem();
  if (!item.opencv_suggestion_baseline_points) return;
  updateActiveState((state) => {{
    state.baseline_points = item.opencv_suggestion_baseline_points;
    if (state.calibration_status === "calibrated" && !calibratedRequiresBaseline(state)) {{
      state.calibration_status = "pending_calibration";
    }}
  }});
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
  link.download = "ready_visual_line_calibration_zl3b.csv";
  document.body.appendChild(link);
  link.click();
  link.remove();
  URL.revokeObjectURL(url);
}}

function resetLocalScan() {{
  localStorage.removeItem(STORAGE_KEY);
  draft = {{ __version: DRAFT_VERSION }};
  showItem(currentIndex);
}}

function scrollImagePanelToTop() {{
  const panel = document.getElementById("imagePanel");
  panel.scrollTo({{ top: 0, left: 0, behavior: "smooth" }});
}}

document.getElementById("baselineSvg").addEventListener("click", addPointFromEvent);
document.getElementById("baselineSvg").addEventListener("mousemove", updateMouseTracking);
document.getElementById("baselineSvg").addEventListener("mouseleave", hideMouseTracking);
document.getElementById("manualNotes").addEventListener("input", (event) => {{
  const state = stateFor(activeItem());
  state.manual_notes = event.target.value;
  writeDraft();
  renderQueue();
  generateCsv();
}});
document.getElementById("prevItem").addEventListener("click", () => showItem(currentIndex - 1));
document.getElementById("nextItem").addEventListener("click", () => showItem(currentIndex + 1));
document.getElementById("nextPending").addEventListener("click", () => {{
  const start = currentIndex + 1;
  const next = ITEMS.findIndex((item, index) => index >= start && stateFor(item).calibration_status === "pending_calibration");
  showItem(next >= 0 ? next : 0);
}});
document.getElementById("undoPoint").addEventListener("click", () => updateActiveState((state) => {{
  const points = parsePoints(state.baseline_points);
  points.pop();
  state.baseline_points = formatPoints(points);
  if (points.length < 2 && state.calibration_status === "calibrated") state.calibration_status = "pending_calibration";
}}));
document.getElementById("clearPoints").addEventListener("click", () => updateActiveState((state) => {{
  state.baseline_points = "";
  if (state.calibration_status === "calibrated") state.calibration_status = "pending_calibration";
}}));
document.getElementById("scrollImageTop").addEventListener("click", scrollImagePanelToTop);
document.getElementById("resetLocalScan").addEventListener("click", resetLocalScan);
document.querySelectorAll("[data-fine-target]").forEach((button) => {{
  button.addEventListener("click", () => setFineTarget(button.dataset.fineTarget));
}});
document.querySelectorAll("[data-nudge-dx]").forEach((button) => {{
  button.addEventListener("click", () => nudgeBaseline(Number(button.dataset.nudgeDx), Number(button.dataset.nudgeDy)));
}});
document.getElementById("markCalibrated").addEventListener("click", () => setStatus("calibrated"));
document.getElementById("markUncertain").addEventListener("click", () => setStatus("uncertain"));
document.getElementById("markNotCalibratable").addEventListener("click", () => setStatus("not_calibratable"));
document.getElementById("useOpenCvSuggestion").addEventListener("click", useOpenCvSuggestion);
document.getElementById("generateCsv").addEventListener("click", generateCsv);
document.getElementById("copyCsv").addEventListener("click", copyCsv);
document.getElementById("downloadCsv").addEventListener("click", downloadCsv);

if (ITEMS.length) {{
  showItem(0);
}} else {{
  document.getElementById("queue").innerHTML = '<div class="empty">Nenhuma linha para calibrar.</div>';
}}
</script>
</body>
</html>
"""


def render_counts(title: str, counts: Counter[str]) -> list[str]:
    lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"|{markdown_cell(key)}|{value}|")
    lines.append("")
    return lines


def write_markdown_report(
    path: Path,
    rows: list[dict[str, str]],
    source_csv: Path,
    calibration_csv: Path,
    summary_csv: Path,
    html_path: Path,
) -> None:
    summary = summarize_line_calibration_rows(rows)
    lines = [
        "# Rota 42C: calibracao manual de linhas/baselines R32 high-res",
        "",
        "Esta rota cria uma ferramenta local para calibrar baselines visuais das linhas alvo da R42B. Ela transforma zonas grandes em linhas manuais mais precisas, mas nao traduz, nao decide anotacao visual e nao preenche a R32.",
        "",
        f"Fonte R42B: `{source_csv}`.",
        f"Planilha de calibracao: `{calibration_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        f"HTML: `{html_path}`.",
        "",
        "## Resultado curto",
        "",
        f"- linhas/loci alvo para calibrar: {len(rows)};",
        "- interacao: selecionar locus, seguir `Guia rapido`, rastrear a mira com coordenadas percentuais, clicar no comeco e no fim da linha real, usar `Ajuste fino` para mover a linha inteira ou uma ponta em passos pequenos, marcar calibrada/incerta/nao calibravel;",
        "- usabilidade infantil: o HTML mostra progresso, passo atual, contagem de pontos, mira/ultimo clique, lupa de recorte real da linha e mensagens simples do que fazer agora;",
        "- zoom/scroll: o painel da imagem tem respiro proprio para zoom alto, nao prende o gesto de scroll no topo, e tem botao `Topo da imagem` para voltar ao canto superior;",
        "- exportacao: o HTML mostra rascunho CSV e oferece copiar/baixar CSV para aplicar na planilha de calibracao;",
        "- navegacao: o HTML tem atalhos para R42B, R42D, R42E e R42F;",
        "- apoio OpenCV: quando a R42D gerar sugestao inicial, o script preenche `baseline_points` como rascunho pendente, registra `Acao OpenCV: prefill_pending_baseline`, e o HTML mostra `Computador ja ajudou` com o proximo passo humano antes de marcar como calibrada;",
        "- maturidade do scan: o overlay SVG fica preso ao canvas real da imagem, cada item recebe uma assinatura deterministica do scan, e o botao `Resetar scan local` limpa rascunhos antigos do navegador;",
        "- persistencia: o HTML usa rascunho local e gera CSV; o script preserva baseline manual existente se rodar novamente;",
        "- resiliencia: status `calibrated` sem pelo menos dois pontos validos volta para `pending_calibration`, inclusive quando vem de CSV ou de rascunho local antigo;",
        "- guarda: `line_calibration_tool_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Folios", summary["folio"]))
    lines.extend(render_counts("Status de calibracao", summary["calibration_status"]))
    lines.extend(render_counts("Pontos de baseline", summary["baseline_points"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota42C|rota32|folio|locus|status|",
            "|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['route42c_id']}|{row['route32_id']}|{row['folio']}|{row['target_locus']}|{row['calibration_status']}|"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_highres_human_fill_html_zl3b.csv"),
        help="Route 42B guided human-fill CSV",
    )
    parser.add_argument(
        "--calibration-csv",
        default=str(ROOT / "data" / "annotations" / "ready_visual_line_calibration_zl3b.csv"),
        help="Manual line calibration CSV, preserved on rerun",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_line_calibration_summary_zl3b.csv"),
        help="Route 42C summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_42c_calibracao_linhas_baseline_r32.md"),
        help="Route 42C Markdown report output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_42c_calibrador_linhas_baseline_r32.html"),
        help="Route 42C HTML output",
    )
    parser.add_argument(
        "--opencv-suggestions-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_line_opencv_suggestions_zl3b.csv"),
        help="Optional route 42D OpenCV suggestion CSV",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_csv = Path(args.source_csv)
    calibration_csv = Path(args.calibration_csv)
    summary_csv = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)
    opencv_suggestions_csv = Path(args.opencv_suggestions_csv)
    suggestions = opencv_suggestion_index(read_csv(opencv_suggestions_csv))
    rows = build_line_calibration_rows(read_csv(source_csv), read_transcriptions(), read_csv(calibration_csv))
    rows = merge_opencv_suggestions_into_calibration_rows(rows, suggestions)
    summary = summarize_line_calibration_rows(rows)
    write_csv(calibration_csv, rows, FIELDNAMES)
    write_summary_csv(summary_csv, summary)
    write_markdown_report(md_path, rows, source_csv, calibration_csv, summary_csv, html_path)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_html(rows, display_path(calibration_csv), suggestions), encoding="utf-8")
    print(
        f"line_calibration_items={len(rows)} "
        f"pending={summary['calibration_status'].get('pending_calibration', 0)} "
        f"calibrated={summary['calibration_status'].get('calibrated', 0)} "
        f"uncertain={summary['calibration_status'].get('uncertain', 0)}"
    )
    print(f"calibration_csv={calibration_csv.resolve()}")
    print(f"summary_csv={summary_csv.resolve()}")
    print(f"md={md_path.resolve()}")
    print(f"html={html_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
