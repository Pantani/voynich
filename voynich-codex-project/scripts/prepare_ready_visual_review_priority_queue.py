#!/usr/bin/env python3
"""Prepare Route 42K: a prioritized queue for visual review choices."""
from __future__ import annotations

import argparse
import csv
import html
import json
from collections import Counter, defaultdict
from pathlib import Path

try:
    from scripts.visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS
except ImportError:  # pragma: no cover - used when running this file directly from scripts/
    from visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "visual_review_priority_not_evidence_or_ocr"

FIELDNAMES = [
    "route42k_id",
    "route42f_id",
    "route42b_id",
    "route32_id",
    "folio",
    "target_locus",
    "transcription_text",
    "priority_level",
    "image_quality_assist",
    "target_region_locatable_assist",
    "candidate_count",
    "candidate_visual_lines",
    "fragment_candidate_count",
    "best_visual_line_number",
    "best_line_fragment_count",
    "best_line_avg_confidence",
    "review_priority_score",
    "review_bucket",
    "human_next_step",
    "local_image_path",
    "best_line_zone_box_pct",
    "top_fragment_ids",
    "top_fragment_crop_boxes",
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


def parse_int(value: str, default: int = 0) -> int:
    try:
        return int(str(value).strip())
    except (TypeError, ValueError):
        return default


def parse_float(value: str, default: float = 0.0) -> float:
    try:
        return float(str(value).strip())
    except (TypeError, ValueError):
        return default


def parse_candidate_zones(value: str) -> dict[str, str]:
    zones: dict[str, str] = {}
    for chunk in str(value or "").split("|"):
        if "=" not in chunk:
            continue
        line_number, box = chunk.split("=", 1)
        line_number = line_number.strip()
        box = box.strip()
        if line_number and box:
            zones[line_number] = box
    return zones


def split_pipe(value: str) -> list[str]:
    return [item.strip() for item in str(value or "").split("|") if item.strip()]


def html_image_src(local_image_path: str) -> str:
    return "../" + local_image_path.lstrip("/") if local_image_path else ""


def score_zone_choice(
    *,
    candidate_count: int,
    fragment_candidate_count: int,
    best_line_avg_confidence: float,
    priority_level: str,
    image_quality_assist: str,
) -> tuple[int, str]:
    score = 0
    if candidate_count <= 1:
        score += 36
    elif candidate_count <= 2:
        score += 30
    elif candidate_count <= 4:
        score += 24
    elif candidate_count <= 6:
        score += 18
    elif candidate_count <= 10:
        score += 10
    else:
        score += 2

    if fragment_candidate_count >= 3:
        score += 22
    elif fragment_candidate_count >= 1:
        score += 14
    else:
        score -= 8

    score += round(max(0.0, min(1.0, best_line_avg_confidence)) * 20)

    if priority_level == "P0":
        score += 8
    elif priority_level == "P1":
        score += 4

    if image_quality_assist.startswith("high"):
        score += 6
    elif image_quality_assist.startswith("medium"):
        score += 2
    elif image_quality_assist:
        score -= 2

    score = max(0, min(100, int(score)))
    if score >= 70:
        return score, "revisar_primeiro"
    if score >= 58:
        return score, "revisar_depois"
    return score, "revisao_dificil"


def index_context_rows(context_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("route42b_id", ""): row for row in context_rows if row.get("route42b_id")}


def index_fragment_rows(fragment_rows: list[dict[str, str]]) -> dict[tuple[str, str], list[dict[str, str]]]:
    indexed: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in fragment_rows:
        key = (row.get("local_image_path", ""), row.get("visual_line_number", ""))
        if key[0] and key[1]:
            indexed[key].append(row)
    return indexed


def choose_best_line(
    *,
    local_image_path: str,
    candidate_lines: list[str],
    fragments_by_line: dict[tuple[str, str], list[dict[str, str]]],
) -> tuple[str, list[dict[str, str]], float]:
    best_line = candidate_lines[0] if candidate_lines else ""
    best_fragments: list[dict[str, str]] = []
    best_confidence = 0.0
    best_rank: tuple[int, float, int] | None = None

    for line_number in candidate_lines:
        fragments = fragments_by_line.get((local_image_path, line_number), [])
        avg_confidence = (
            sum(parse_float(row.get("confidence", "0")) for row in fragments) / len(fragments)
            if fragments
            else 0.0
        )
        rank = (len(fragments), avg_confidence, -parse_int(line_number, 9999))
        if best_rank is None or rank > best_rank:
            best_rank = rank
            best_line = line_number
            best_fragments = fragments
            best_confidence = avg_confidence

    top_fragments = sorted(
        best_fragments,
        key=lambda row: (parse_float(row.get("confidence", "0")), row.get("route42j_id", "")),
        reverse=True,
    )[:4]
    return best_line, top_fragments, best_confidence


def build_priority_rows(
    zone_rows: list[dict[str, str]],
    fragment_rows: list[dict[str, str]],
    context_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    context_by_route42b = index_context_rows(context_rows)
    fragments_by_line = index_fragment_rows(fragment_rows)
    output: list[dict[str, str]] = []

    for zone in zone_rows:
        if zone.get("zone_status") != "pending_zone_choice":
            continue
        context = context_by_route42b.get(zone.get("route42b_id", ""), {})
        candidate_lines = split_pipe(zone.get("candidate_visual_lines", ""))
        candidate_count = parse_int(zone.get("candidate_count", ""), len(candidate_lines))
        local_image_path = zone.get("local_image_path", "")
        best_line, top_fragments, best_confidence = choose_best_line(
            local_image_path=local_image_path,
            candidate_lines=candidate_lines,
            fragments_by_line=fragments_by_line,
        )
        fragment_candidate_count = sum(
            len(fragments_by_line.get((local_image_path, line_number), []))
            for line_number in candidate_lines
        )
        score, bucket = score_zone_choice(
            candidate_count=candidate_count,
            fragment_candidate_count=fragment_candidate_count,
            best_line_avg_confidence=best_confidence,
            priority_level=context.get("priority_level", ""),
            image_quality_assist=context.get("image_quality_assist", ""),
        )
        candidate_zones = parse_candidate_zones(zone.get("candidate_visual_line_zones", ""))
        output.append(
            {
                "route42k_id": "",
                "route42f_id": zone.get("route42f_id", ""),
                "route42b_id": zone.get("route42b_id", ""),
                "route32_id": zone.get("route32_id", ""),
                "folio": zone.get("folio", ""),
                "target_locus": zone.get("target_locus", ""),
                "transcription_text": zone.get("transcription_text", ""),
                "priority_level": context.get("priority_level", ""),
                "image_quality_assist": context.get("image_quality_assist", ""),
                "target_region_locatable_assist": context.get("target_region_locatable_assist", ""),
                "candidate_count": str(candidate_count),
                "candidate_visual_lines": "|".join(candidate_lines),
                "fragment_candidate_count": str(fragment_candidate_count),
                "best_visual_line_number": best_line,
                "best_line_fragment_count": str(len(top_fragments)),
                "best_line_avg_confidence": f"{best_confidence:.2f}",
                "review_priority_score": str(score),
                "review_bucket": bucket,
                "human_next_step": human_next_step(bucket, candidate_count, fragment_candidate_count),
                "local_image_path": local_image_path,
                "best_line_zone_box_pct": candidate_zones.get(best_line, ""),
                "top_fragment_ids": "|".join(row.get("route42j_id", "") for row in top_fragments),
                "top_fragment_crop_boxes": "|".join(row.get("crop_box_pct", "") for row in top_fragments),
                "semantic_guardrail": GUARDRAIL,
            }
        )

    output.sort(
        key=lambda row: (
            -parse_int(row.get("review_priority_score", "")),
            parse_int(row.get("candidate_count", "")),
            row.get("folio", ""),
            row.get("target_locus", ""),
        )
    )
    for index, row in enumerate(output, start=1):
        row["route42k_id"] = f"R42K-{index:03d}"
    return output


def human_next_step(bucket: str, candidate_count: int, fragment_candidate_count: int) -> str:
    if bucket == "revisar_primeiro":
        return "abrir R42K, comparar os recortes sugeridos e escolher a linha correspondente na R42F"
    if fragment_candidate_count == 0:
        return "abrir R42E/R42F e decidir pela linha visual inteira, pois a R42J nao trouxe fragmentos uteis"
    if candidate_count > 10:
        return "reduzir pela visao geral na R42F antes de confiar nos fragmentos"
    return "usar os fragmentos como lupa e confirmar a linha na R42F"


def write_summary_csv(path: Path, rows: list[dict[str, str]]) -> None:
    counters = {
        "queue_items": Counter({"pending_zone_choice_ranked": len(rows)}),
        "review_bucket": Counter(row.get("review_bucket", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "semantic_guardrail": Counter({GUARDRAIL: len(rows)}),
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "item", "n"])
        writer.writeheader()
        for metric, counter in counters.items():
            for item, count in sorted(counter.items(), key=lambda pair: (-pair[1], pair[0])):
                writer.writerow({"metric": metric, "item": item, "n": count})


def rows_for_html(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    html_rows = []
    for row in rows:
        crop_boxes = split_pipe(row.get("top_fragment_crop_boxes", ""))
        html_rows.append(
            {
                **row,
                "image_src": html_image_src(row.get("local_image_path", "")),
                "crop_boxes": crop_boxes,
            }
        )
    return html_rows


def render_html(rows: list[dict[str, str]], queue_csv: str) -> str:
    rows_json = json.dumps(rows_for_html(rows), ensure_ascii=True)
    static_rows = "".join(
        f"<li><strong>{html.escape(row['route42k_id'])}</strong> {html.escape(row['target_locus'])} "
        f"- score {html.escape(row['review_priority_score'])} - {html.escape(row['review_bucket'])}</li>"
        for row in rows[:20]
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rota 42K - Fila priorizada de revisao visual</title>
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
    h1 {{ margin: 0; font-size: 20px; }}
    p {{ margin: 0; color: var(--muted); }}
    .nav {{ display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }}
    .workspace {{ min-height: 0; display: grid; grid-template-columns: 320px minmax(0, 1fr) 340px; }}
    .queue {{ overflow: auto; border-right: 1px solid var(--line); background: #efe4d4; padding: 10px; }}
    .queue button {{ width: 100%; display: grid; gap: 4px; text-align: left; margin-bottom: 7px; }}
    .queue button.active {{ border-color: var(--accent); outline: 3px solid rgba(31, 118, 104, .2); }}
    .score {{ font-size: 13px; color: var(--accent); font-weight: 900; }}
    .main {{ overflow: auto; padding: 14px; background: #e6ddd0; }}
    .target-card {{ border: 1px solid var(--line); border-radius: 8px; background: var(--panel); padding: 14px; display: grid; gap: 12px; }}
    .meta-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px; }}
    .meta {{ border: 1px solid #ded2c2; border-radius: 7px; padding: 8px; background: #fffdf8; }}
    .meta b {{ display: block; font-size: 12px; color: var(--muted); }}
    .crops {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; }}
{VISUAL_CROP_CSS}
    .side {{ overflow: auto; border-left: 1px solid var(--line); background: var(--panel); padding: 14px; }}
    .plain-box {{ border: 1px solid var(--line); border-radius: 8px; background: #fff7ea; padding: 12px; margin-bottom: 12px; }}
    .plain-box h2, .plain-box h3 {{ margin: 0 0 8px; font-size: 15px; }}
    .warning {{ color: var(--warn); font-weight: 850; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; overflow-wrap: anywhere; }}
    ol {{ margin: 0; padding-left: 20px; color: var(--muted); }}
  </style>
</head>
<body>
<div class="app">
  <header class="topbar">
    <div>
      <h1>Rota 42K - Fila priorizada</h1>
      <p>Ordem pratica para revisar as escolhas pendentes. Nao e OCR, traducao ou evidencia de palavra.</p>
    </div>
    <nav class="nav" aria-label="Navegacao entre rotas">
      <a class="button-link" href="rota_42g_ferramentas_ativas_r32.html">Ferramentas ativas</a>
      <a class="button-link" href="rota_42l_confirmacao_linhas_sugeridas_r32.html">Abrir R42L</a>
      <a class="button-link" href="rota_42f_escolha_linhas_visuais_sem_zona_r32.html">Abrir R42F</a>
      <a class="button-link" href="rota_42j_fragmentos_visuais_opencv_r32.html">Abrir R42J</a>
      <a class="button-link" href="rota_42c_calibrador_linhas_baseline_r32.html">Abrir R42C</a>
    </nav>
  </header>
  <main class="workspace">
    <aside class="queue" id="queue" aria-label="Fila priorizada"></aside>
    <section class="main" aria-label="Item selecionado">
      <article class="target-card" id="targetCard"></article>
    </section>
    <aside class="side" aria-label="Explicacao da rota 42K">
      <section class="plain-box">
        <h2>Como usar</h2>
        <p>Comece pelo primeiro item. Olhe os recortes, depois abra a R42L para confirmar a linha sugerida antes de aplicar qualquer coisa na R42F.</p>
      </section>
      <section class="plain-box">
        <h3>Resumo auditavel</h3>
        <ol>{static_rows or '<li>Nenhum item pendente.</li>'}</ol>
      </section>
      <section class="plain-box">
        <h3>CSV</h3>
        <p class="mono">{html.escape(queue_csv)}</p>
      </section>
      <section class="plain-box">
        <h3>Guarda</h3>
        <p class="mono">{GUARDRAIL}</p>
        <p class="warning">Nao usar como OCR nem como evidencia. Use apenas para escolher a proxima revisao humana.</p>
      </section>
    </aside>
  </main>
</div>
<script>
const QUEUE_ROWS = {rows_json};
let currentIndex = 0;

{VISUAL_CROP_JS}

function activeRow() {{
  return QUEUE_ROWS[currentIndex] || null;
}}

function renderQueue() {{
  const queue = document.getElementById("queue");
  queue.innerHTML = "";
  QUEUE_ROWS.forEach((row, index) => {{
    const button = document.createElement("button");
    button.type = "button";
    button.className = index === currentIndex ? "active" : "";
    button.innerHTML = `
      <strong>${{row.route42k_id}} / ${{row.target_locus}}</strong>
      <span class="score">score ${{row.review_priority_score}} / ${{row.review_bucket}}</span>
      <small>${{row.folio}} / candidatos ${{row.candidate_count}} / fragmentos ${{row.fragment_candidate_count}}</small>
    `;
    button.addEventListener("click", () => {{
      currentIndex = index;
      renderAll();
    }});
    queue.appendChild(button);
  }});
  if (!QUEUE_ROWS.length) queue.innerHTML = "<p>Nenhum item pendente.</p>";
}}

function cropCards(row) {{
  if (!row.crop_boxes.length) {{
    return '<p class="warning">Sem recorte de fragmento para este alvo. Use a R42F pela linha inteira.</p>';
  }}
  return row.crop_boxes.map((box, index) => `
    <article class="visual-crop-card">
      <span class="visual-crop-label">fragmento sugerido ${{index + 1}}</span>
      <canvas class="visual-crop-canvas" data-crop-preview data-image-src="${{row.image_src}}" data-box-pct="${{box}}" aria-label="fragmento sugerido ${{index + 1}}"></canvas>
      <span class="visual-crop-note">linha visual sugerida ${{row.best_visual_line_number}}</span>
    </article>
  `).join("");
}}

function renderTarget() {{
  const card = document.getElementById("targetCard");
  const row = activeRow();
  if (!row) {{
    card.innerHTML = '<p class="warning">Nenhum item pendente.</p>';
    return;
  }}
  card.innerHTML = `
    <div>
      <h2>${{row.route42k_id}} / ${{row.target_locus}}</h2>
      <p>${{row.human_next_step}}</p>
    </div>
    <div class="meta-grid">
      <div class="meta"><b>score</b>${{row.review_priority_score}} / ${{row.review_bucket}}</div>
      <div class="meta"><b>candidatos</b>${{row.candidate_visual_lines}}</div>
      <div class="meta"><b>linha sugerida para olhar primeiro</b>${{row.best_visual_line_number || "sem sugestao"}}</div>
      <div class="meta"><b>fragmentos na fila</b>${{row.fragment_candidate_count}}</div>
      <div class="meta"><b>prioridade</b>${{row.priority_level || "sem prioridade"}}</div>
      <div class="meta"><b>qualidade</b>${{row.image_quality_assist || "sem dado"}}</div>
    </div>
    <div class="meta"><b>texto de referencia tecnico</b><span class="mono">${{row.transcription_text}}</span></div>
    <div class="crops">${{cropCards(row)}}</div>
  `;
  paintCropPreviews(card);
}}

function renderAll() {{
  renderQueue();
  renderTarget();
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
    zone_choice_csv: Path,
    fragment_csv: Path,
    queue_csv: Path,
    summary_csv: Path,
    html_path: Path,
) -> None:
    lines = [
        "# Rota 42K: fila priorizada para revisao visual",
        "",
        "Esta rota cruza as pendencias da R42F com os fragmentos visuais da R42J para ordenar a proxima revisao humana.",
        "",
        "Ela nao escolhe linha sozinha, nao e OCR, nao le EVA, nao traduz e nao cria evidencia de palavra.",
        "",
        f"Entrada R42F: `{zone_choice_csv}`.",
        f"Entrada R42J: `{fragment_csv}`.",
        f"CSV da fila: `{queue_csv}`.",
        f"Resumo: `{summary_csv}`.",
        f"HTML: `{html_path}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens pendentes priorizados: {len(rows)};",
        f"- revisar primeiro: {sum(1 for row in rows if row.get('review_bucket') == 'revisar_primeiro')};",
        f"- revisar depois: {sum(1 for row in rows if row.get('review_bucket') == 'revisar_depois')};",
        f"- revisao dificil: {sum(1 for row in rows if row.get('review_bucket') == 'revisao_dificil')};",
        f"- guarda: `{GUARDRAIL}`.",
        "",
    ]
    lines.extend(render_counts("Buckets", Counter(row.get("review_bucket", "") for row in rows)))
    lines.extend(render_counts("Folios", Counter(row.get("folio", "") for row in rows)))
    lines.extend(render_counts("Prioridade", Counter(row.get("priority_level", "") for row in rows)))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--zone-choice-csv",
        default=str(ROOT / "data" / "annotations" / "ready_visual_line_zone_choice_zl3b.csv"),
        help="Route 42F pending zone choices CSV",
    )
    parser.add_argument(
        "--fragment-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_word_opencv_map_zl3b.csv"),
        help="Route 42J visual fragment map CSV",
    )
    parser.add_argument(
        "--context-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_highres_human_fill_html_zl3b.csv"),
        help="Route 42B high-resolution context CSV",
    )
    parser.add_argument(
        "--queue-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_review_priority_queue_zl3b.csv"),
        help="Route 42K queue CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_review_priority_queue_summary_zl3b.csv"),
        help="Route 42K summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_42k_fila_priorizada_revisao_visual_r32.md"),
        help="Route 42K Markdown report output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_42k_fila_priorizada_revisao_visual_r32.html"),
        help="Route 42K HTML output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    zone_choice_csv = Path(args.zone_choice_csv)
    fragment_csv = Path(args.fragment_csv)
    context_csv = Path(args.context_csv)
    queue_csv = Path(args.queue_csv)
    summary_csv = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)

    zone_rows = read_csv(zone_choice_csv)
    fragment_rows = read_csv(fragment_csv)
    context_rows = read_csv(context_csv)
    rows = build_priority_rows(zone_rows, fragment_rows, context_rows)

    write_csv(queue_csv, rows, FIELDNAMES)
    write_summary_csv(summary_csv, rows)
    write_markdown_report(md_path, rows, zone_choice_csv, fragment_csv, queue_csv, summary_csv, html_path)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_html(rows, str(queue_csv)), encoding="utf-8")

    print(f"priority_queue_items={len(rows)}")
    print(f"queue_csv={queue_csv.resolve()}")
    print(f"summary_csv={summary_csv.resolve()}")
    print(f"md={md_path.resolve()}")
    print(f"html={html_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
