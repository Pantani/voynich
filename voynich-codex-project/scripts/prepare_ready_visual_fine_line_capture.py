#!/usr/bin/env python3
"""Prepare Route 42M: fine visual-line capture suggestions from R42L/R42J data."""
from __future__ import annotations

import argparse
import csv
import html
import json
from collections import Counter
from pathlib import Path

try:
    from scripts.visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS
except ImportError:  # pragma: no cover - used when running this file directly from scripts/
    from visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "fine_line_capture_not_ocr_or_evidence"

FIELDNAMES = [
    "route42m_id",
    "route42l_id",
    "route42k_id",
    "route42f_id",
    "route42b_id",
    "route32_id",
    "folio",
    "target_locus",
    "transcription_text",
    "review_bucket",
    "review_priority_score",
    "suggested_visual_line_number",
    "suggested_zone_box_pct",
    "fragment_union_box_pct",
    "refined_capture_box_pct",
    "refined_baseline_points",
    "fragment_count",
    "area_reduction_pct",
    "confidence_band",
    "fine_capture_status",
    "selected_visual_line_number",
    "selected_zone_box_pct",
    "human_next_step",
    "local_image_path",
    "semantic_guardrail",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [index + 2 for index, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def split_pipe(value: str) -> list[str]:
    return [item.strip() for item in value.split("|") if item.strip()]


def parse_box(value: str) -> tuple[float, float, float, float] | None:
    parts = [part.strip() for part in value.split(",")]
    if len(parts) != 4:
        return None
    try:
        left, top, right, bottom = [float(part) for part in parts]
    except ValueError:
        return None
    if right <= left or bottom <= top:
        return None
    if min(left, top, right, bottom) < 0 or max(left, top, right, bottom) > 100:
        return None
    return left, top, right, bottom


def box_text(box: tuple[float, float, float, float]) -> str:
    return ",".join(f"{value:.2f}" for value in box)


def box_area(box: tuple[float, float, float, float]) -> float:
    left, top, right, bottom = box
    return max(0.0, right - left) * max(0.0, bottom - top)


def intersect_box(
    first: tuple[float, float, float, float],
    second: tuple[float, float, float, float],
) -> tuple[float, float, float, float] | None:
    left = max(first[0], second[0])
    top = max(first[1], second[1])
    right = min(first[2], second[2])
    bottom = min(first[3], second[3])
    if right <= left or bottom <= top:
        return None
    return left, top, right, bottom


def union_box(boxes: list[tuple[float, float, float, float]]) -> tuple[float, float, float, float] | None:
    if not boxes:
        return None
    return (
        min(box[0] for box in boxes),
        min(box[1] for box in boxes),
        max(box[2] for box in boxes),
        max(box[3] for box in boxes),
    )


def expand_within_zone(
    box: tuple[float, float, float, float],
    zone: tuple[float, float, float, float],
    *,
    x_pad: float = 0.40,
    y_pad: float = 0.0,
) -> tuple[float, float, float, float]:
    return (
        max(zone[0], box[0] - x_pad),
        max(zone[1], box[1] - y_pad),
        min(zone[2], box[2] + x_pad),
        min(zone[3], box[3] + y_pad),
    )


def baseline_from_capture(box: tuple[float, float, float, float]) -> str:
    left, top, right, bottom = box
    y = top + ((bottom - top) * 0.78)
    return f"{left:.2f},{y:.2f} {right:.2f},{y:.2f}"


def confidence_band(fragment_count: int, area_reduction: float) -> str:
    if fragment_count >= 4 and area_reduction >= 12:
        return "alta"
    if fragment_count >= 2:
        return "media"
    return "baixa"


def compute_refined_capture(row: dict[str, str]) -> dict[str, str]:
    zone = parse_box(row.get("suggested_zone_box_pct", ""))
    if zone is None:
        return {
            "fragment_union_box_pct": "",
            "refined_capture_box_pct": "",
            "refined_baseline_points": "",
            "fragment_count": "0",
            "area_reduction_pct": "0.00",
            "confidence_band": "baixa",
            "fine_capture_status": "needs_manual_capture_review",
            "semantic_guardrail": GUARDRAIL,
        }

    fragments = [parse_box(value) for value in split_pipe(row.get("top_fragment_crop_boxes", ""))]
    clipped_fragments = [intersect_box(fragment, zone) for fragment in fragments if fragment]
    usable_fragments = [fragment for fragment in clipped_fragments if fragment]
    fragment_union = union_box(usable_fragments)

    if fragment_union is None:
        return {
            "fragment_union_box_pct": "",
            "refined_capture_box_pct": box_text(zone),
            "refined_baseline_points": baseline_from_capture(zone),
            "fragment_count": "0",
            "area_reduction_pct": "0.00",
            "confidence_band": "baixa",
            "fine_capture_status": "needs_manual_capture_review",
            "semantic_guardrail": GUARDRAIL,
        }

    refined = expand_within_zone(fragment_union, zone)
    zone_area = box_area(zone)
    refined_area = box_area(refined)
    area_reduction = max(0.0, (1 - (refined_area / zone_area)) * 100) if zone_area else 0.0
    fragment_count = len(usable_fragments)
    return {
        "fragment_union_box_pct": box_text(fragment_union),
        "refined_capture_box_pct": box_text(refined),
        "refined_baseline_points": baseline_from_capture(refined),
        "fragment_count": str(fragment_count),
        "area_reduction_pct": f"{area_reduction:.2f}",
        "confidence_band": confidence_band(fragment_count, area_reduction),
        "fine_capture_status": "fine_capture_ready_needs_human_confirmation",
        "semantic_guardrail": GUARDRAIL,
    }


def build_fine_capture_rows(confirmation_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for row in confirmation_rows:
        refined = compute_refined_capture(row)
        output.append(
            {
                "route42m_id": f"R42M-{len(output) + 1:03d}",
                "route42l_id": row.get("route42l_id", ""),
                "route42k_id": row.get("route42k_id", ""),
                "route42f_id": row.get("route42f_id", ""),
                "route42b_id": row.get("route42b_id", ""),
                "route32_id": row.get("route32_id", ""),
                "folio": row.get("folio", ""),
                "target_locus": row.get("target_locus", ""),
                "transcription_text": row.get("transcription_text", ""),
                "review_bucket": row.get("review_bucket", ""),
                "review_priority_score": row.get("review_priority_score", ""),
                "suggested_visual_line_number": row.get("suggested_visual_line_number", ""),
                "suggested_zone_box_pct": row.get("suggested_zone_box_pct", ""),
                "fragment_union_box_pct": refined["fragment_union_box_pct"],
                "refined_capture_box_pct": refined["refined_capture_box_pct"],
                "refined_baseline_points": refined["refined_baseline_points"],
                "fragment_count": refined["fragment_count"],
                "area_reduction_pct": refined["area_reduction_pct"],
                "confidence_band": refined["confidence_band"],
                "fine_capture_status": refined["fine_capture_status"],
                "selected_visual_line_number": "",
                "selected_zone_box_pct": "",
                "human_next_step": "confirmar visualmente na R42L antes de aplicar na R42F",
                "local_image_path": row.get("local_image_path", ""),
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return output


def write_summary_csv(path: Path, rows: list[dict[str, str]]) -> None:
    counters = {
        "fine_capture_items": Counter({"items": len(rows)}),
        "fine_capture_status": Counter(row.get("fine_capture_status", "") for row in rows),
        "confidence_band": Counter(row.get("confidence_band", "") for row in rows),
        "review_bucket": Counter(row.get("review_bucket", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
        "semantic_guardrail": Counter({GUARDRAIL: len(rows)}),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "item", "n"])
        writer.writeheader()
        for metric, counter in counters.items():
            for item, count in sorted(counter.items(), key=lambda pair: (-pair[1], pair[0])):
                writer.writerow({"metric": metric, "item": item, "n": count})


def html_image_src(local_image_path: str) -> str:
    return "../../" + local_image_path.lstrip("/") if local_image_path else ""


def rows_for_html(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    output = []
    for row in rows:
        output.append({**row, "image_src": html_image_src(row.get("local_image_path", ""))})
    return output


def render_html(rows: list[dict[str, str]], fine_capture_csv: str) -> str:
    rows_json = json.dumps(rows_for_html(rows), ensure_ascii=True)
    static_items = "".join(
        f"<li><strong>{html.escape(row['route42m_id'])}</strong> {html.escape(row['target_locus'])} "
        f"- captura {html.escape(row['confidence_band'])} / {html.escape(row['fine_capture_status'])}</li>"
        for row in rows[:20]
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rota 42M - Captura fina de linhas</title>
  <style>
    :root {{
      --paper: #f6f0e7;
      --panel: #fffaf2;
      --line: #d6c8b8;
      --ink: #211d19;
      --muted: #6d645b;
      --accent: #1f7668;
      --warn: #8a3f32;
    }}
    * {{ box-sizing: border-box; }}
    body {{ margin: 0; min-height: 100vh; background: var(--paper); color: var(--ink); font: 14px/1.45 -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif; }}
    button, a.button-link {{ border: 1px solid #c8baaa; border-radius: 7px; background: #fffaf2; color: var(--ink); padding: 8px 11px; font-weight: 800; text-decoration: none; cursor: pointer; }}
    button:hover, a.button-link:hover {{ background: #f1e7d8; }}
    .app {{ min-height: 100vh; display: grid; grid-template-rows: auto minmax(0, 1fr); }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 12px 16px; border-bottom: 1px solid var(--line); background: #fbf6ed; }}
    h1, h2, h3 {{ margin: 0; }}
    h1 {{ font-size: 20px; }}
    p {{ margin: 0; color: var(--muted); }}
    .nav {{ display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }}
    .workspace {{ min-height: 0; display: grid; grid-template-columns: 300px minmax(0, 1fr) 340px; }}
    .queue {{ overflow: auto; border-right: 1px solid var(--line); background: #efe4d4; padding: 10px; }}
    .queue button {{ width: 100%; display: grid; gap: 4px; text-align: left; margin-bottom: 7px; }}
    .queue button.active {{ border-color: var(--accent); outline: 3px solid rgba(31, 118, 104, .2); }}
    .main {{ overflow: auto; padding: 14px; background: #e6ddd0; }}
    .target-card {{ border: 1px solid var(--line); border-radius: 8px; background: var(--panel); padding: 14px; display: grid; gap: 12px; }}
    .meta-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px; }}
    .meta {{ border: 1px solid #ded2c2; border-radius: 7px; padding: 8px; background: #fffdf8; }}
    .meta b {{ display: block; font-size: 12px; color: var(--muted); }}
    .crop-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(240px, 1fr)); gap: 10px; }}
{VISUAL_CROP_CSS}
    .side {{ overflow: auto; border-left: 1px solid var(--line); background: var(--panel); padding: 14px; }}
    .plain-box {{ border: 1px solid var(--line); border-radius: 8px; background: #fff7ea; padding: 12px; margin-bottom: 12px; }}
    .plain-box h3 {{ margin-bottom: 8px; font-size: 15px; }}
    .warning {{ color: var(--warn); font-weight: 850; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; overflow-wrap: anywhere; }}
    ol {{ margin: 0; padding-left: 20px; color: var(--muted); }}
  </style>
</head>
<body>
<div class="app">
  <header class="topbar">
    <div>
      <h1>Rota 42M - Captura fina</h1>
      <p>Alinha a captura pela uniao dos fragmentos visuais, mas nao e OCR e nao confirma palavra.</p>
    </div>
    <nav class="nav" aria-label="Navegacao entre rotas">
      <a class="button-link" href="rota_42g_ferramentas_ativas_r32.html">Ferramentas ativas</a>
      <a class="button-link" href="rota_42l_confirmacao_linhas_sugeridas_r32.html">Abrir R42L</a>
      <a class="button-link" href="rota_42c_calibrador_linhas_baseline_r32.html">Abrir R42C</a>
      <a class="button-link" href="rota_42j_fragmentos_visuais_opencv_r32.html">Abrir R42J</a>
    </nav>
  </header>
  <main class="workspace">
    <aside class="queue" id="queue" aria-label="Capturas finas"></aside>
    <section class="main" aria-label="Comparacao da captura">
      <article class="target-card" id="targetCard"></article>
    </section>
    <aside class="side" aria-label="Resumo">
      <section class="plain-box">
        <h3>Como usar</h3>
        <p>Compare a zona sugerida com a captura fina. Se a captura fina estiver alinhada, volte para a R42L e confirme a linha antes de aplicar qualquer coisa.</p>
      </section>
      <section class="plain-box">
        <h3>Itens</h3>
        <ol>{static_items or '<li>Nenhuma captura fina.</li>'}</ol>
      </section>
      <section class="plain-box">
        <h3>CSV gerado</h3>
        <p class="mono">{html.escape(fine_capture_csv)}</p>
      </section>
      <section class="plain-box">
        <h3>Guarda</h3>
        <p class="mono">{GUARDRAIL}</p>
        <p class="warning">Isto e alinhamento visual auxiliar, nao evidencia, nao traducao e nao OCR.</p>
      </section>
    </aside>
  </main>
</div>
<script>
const ROWS = {rows_json};
let activeIndex = 0;

function cropCard(label, imageSrc, box, note) {{
  if (!box) return `<article class="visual-crop-card"><span class="visual-crop-label">${{label}}</span><p class="visual-crop-note">sem caixa</p></article>`;
  return `<article class="visual-crop-card" data-image-src="${{imageSrc}}" data-crop-box="${{box}}">
    <span class="visual-crop-label">${{label}}</span>
    <canvas class="visual-crop-canvas" data-crop-preview aria-label="${{label}}"></canvas>
    <span class="visual-crop-note">${{note}}</span>
  </article>`;
}}

function renderQueue() {{
  const queue = document.getElementById("queue");
  queue.innerHTML = "";
  ROWS.forEach((row, index) => {{
    const button = document.createElement("button");
    button.type = "button";
    button.className = index === activeIndex ? "active" : "";
    button.innerHTML = `<strong>${{row.route42m_id}}</strong><span>${{row.target_locus}}</span><small>${{row.confidence_band}} - ${{row.fine_capture_status}}</small>`;
    button.addEventListener("click", () => {{
      activeIndex = index;
      renderAll();
    }});
    queue.appendChild(button);
  }});
}}

function renderTarget() {{
  const row = ROWS[activeIndex] || {{}};
  const imageSrc = row.image_src || "";
  document.getElementById("targetCard").innerHTML = `
    <h2>${{row.route42m_id || ""}} / ${{row.target_locus || ""}}</h2>
    <div class="meta-grid">
      <div class="meta"><b>linha sugerida</b>${{row.suggested_visual_line_number || "n/a"}}</div>
      <div class="meta"><b>fragmentos usados</b>${{row.fragment_count || "0"}}</div>
      <div class="meta"><b>reducao de area</b>${{row.area_reduction_pct || "0.00"}}%</div>
      <div class="meta"><b>confianca</b>${{row.confidence_band || "baixa"}}</div>
      <div class="meta"><b>baseline sugerida</b><span class="mono">${{row.refined_baseline_points || "n/a"}}</span></div>
    </div>
    <div class="crop-grid">
      ${{cropCard("zona sugerida original", imageSrc, row.suggested_zone_box_pct, "caixa maior vinda da R42L/R42F")}}
      ${{cropCard("captura fina R42M", imageSrc, row.refined_capture_box_pct, "recorte alinhado pelos fragmentos")}}
      ${{cropCard("uniao dos fragmentos", imageSrc, row.fragment_union_box_pct, "base mecanica da captura fina")}}
    </div>
    <p><strong>Proximo passo:</strong> ${{row.human_next_step || ""}}</p>
    <p class="mono">${{row.semantic_guardrail || ""}}</p>
  `;
  paintCropPreviews(document.getElementById("targetCard"));
}}

function renderAll() {{
  renderQueue();
  renderTarget();
}}

{VISUAL_CROP_JS}
renderAll();
</script>
</body>
</html>
"""


def markdown_counts(title: str, counter: Counter[str]) -> list[str]:
    lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
    for item, count in sorted(counter.items(), key=lambda pair: (-pair[1], pair[0])):
        lines.append(f"|{item}|{count}|")
    lines.append("")
    return lines


def write_markdown_report(path: Path, rows: list[dict[str, str]], fine_capture_csv: str, summary_csv: str, html_path: str) -> None:
    lines = [
        "# Rota 42M: captura fina de linhas R32",
        "",
        "Esta rota alinha recortes mais estreitos a partir da R42L e dos fragmentos visuais já detectados.",
        "",
        "Ela nao aplica automaticamente, nao e OCR, nao le EVA, nao traduz e nao cria evidencia visual.",
        "",
        f"CSV de captura fina: `{fine_capture_csv}`.",
        f"Resumo: `{summary_csv}`.",
        f"HTML: `{html_path}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens de captura fina: {len(rows)};",
        f"- guarda: `{GUARDRAIL}`.",
        "",
    ]
    lines.extend(markdown_counts("Status", Counter(row["fine_capture_status"] for row in rows)))
    lines.extend(markdown_counts("Confianca", Counter(row["confidence_band"] for row in rows)))
    lines.extend(markdown_counts("Folios", Counter(row["folio"] for row in rows)))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--confirmation-csv",
        default=str(ROOT / "data" / "annotations" / "ready_visual_line_choice_confirmation_zl3b.csv"),
    )
    parser.add_argument(
        "--fine-capture-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_fine_line_capture_zl3b.csv"),
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_fine_line_capture_summary_zl3b.csv"),
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_42m_captura_fina_linhas_r32.md"),
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_42m_captura_fina_linhas_r32.html"),
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    confirmation_csv = Path(args.confirmation_csv)
    fine_capture_csv = Path(args.fine_capture_csv)
    summary_csv = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)

    rows = build_fine_capture_rows(read_csv(confirmation_csv))
    write_csv(fine_capture_csv, rows, FIELDNAMES)
    write_summary_csv(summary_csv, rows)
    write_markdown_report(md_path, rows, str(fine_capture_csv), str(summary_csv), str(html_path))
    html_path.write_text(render_html(rows, str(fine_capture_csv)), encoding="utf-8")

    print(f"fine_capture_items={len(rows)}")
    print(f"fine_capture_csv={fine_capture_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"md={md_path}")
    print(f"html={html_path}")


if __name__ == "__main__":
    main()
