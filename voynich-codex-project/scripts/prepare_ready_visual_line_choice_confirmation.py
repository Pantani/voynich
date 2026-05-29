#!/usr/bin/env python3
"""Prepare Route 42L: confirm prioritized visual-line choices before applying them."""
from __future__ import annotations

import argparse
import csv
import html
import json
from collections import Counter
from pathlib import Path

try:
    from scripts.prepare_ready_visual_review_priority_queue import html_image_src, parse_candidate_zones, split_pipe
    from scripts.visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS
except ImportError:  # pragma: no cover - used when running this file directly from scripts/
    from prepare_ready_visual_review_priority_queue import html_image_src, parse_candidate_zones, split_pipe
    from visual_crop import VISUAL_CROP_CSS, VISUAL_CROP_JS

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "line_choice_confirmation_not_evidence_or_ocr"

FIELDNAMES = [
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
    "candidate_visual_lines",
    "candidate_visual_line_zones",
    "top_fragment_crop_boxes",
    "selected_visual_line_number",
    "selected_zone_box_pct",
    "confirmation_status",
    "manual_notes",
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


def zone_rows_by_route42f(zone_rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("route42f_id", ""): row for row in zone_rows if row.get("route42f_id")}


def candidate_options(queue_row: dict[str, str], zone_row: dict[str, str]) -> list[dict[str, object]]:
    zones = parse_candidate_zones(zone_row.get("candidate_visual_line_zones", ""))
    line_numbers = split_pipe(queue_row.get("candidate_visual_lines", ""))
    suggested_line = queue_row.get("best_visual_line_number", "") or queue_row.get("suggested_visual_line_number", "")
    output: list[dict[str, object]] = []
    for line_number in line_numbers:
        output.append(
            {
                "line_number": line_number,
                "box_pct": zones.get(line_number, ""),
                "is_suggested": line_number == suggested_line,
            }
        )
    return output


def build_confirmation_rows(
    queue_rows: list[dict[str, str]],
    zone_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    zones_by_route42f = zone_rows_by_route42f(zone_rows)
    rows: list[dict[str, str]] = []
    for queue in queue_rows:
        route42f_id = queue.get("route42f_id", "")
        zone = zones_by_route42f.get(route42f_id, {})
        rows.append(
            {
                "route42l_id": f"R42L-{len(rows) + 1:03d}",
                "route42k_id": queue.get("route42k_id", ""),
                "route42f_id": route42f_id,
                "route42b_id": queue.get("route42b_id", ""),
                "route32_id": queue.get("route32_id", ""),
                "folio": queue.get("folio", ""),
                "target_locus": queue.get("target_locus", ""),
                "transcription_text": queue.get("transcription_text", ""),
                "review_bucket": queue.get("review_bucket", ""),
                "review_priority_score": queue.get("review_priority_score", ""),
                "suggested_visual_line_number": queue.get("best_visual_line_number", ""),
                "suggested_zone_box_pct": queue.get("best_line_zone_box_pct", ""),
                "candidate_visual_lines": queue.get("candidate_visual_lines", ""),
                "candidate_visual_line_zones": zone.get("candidate_visual_line_zones", ""),
                "top_fragment_crop_boxes": queue.get("top_fragment_crop_boxes", ""),
                "selected_visual_line_number": "",
                "selected_zone_box_pct": "",
                "confirmation_status": "pending_human_confirmation",
                "manual_notes": "",
                "local_image_path": queue.get("local_image_path", ""),
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def write_summary_csv(path: Path, rows: list[dict[str, str]]) -> None:
    counters = {
        "confirmation_items": Counter({"pending_human_confirmation": len(rows)}),
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


def rows_for_html(rows: list[dict[str, str]]) -> list[dict[str, object]]:
    output = []
    for row in rows:
        pseudo_zone = {"route42f_id": row.get("route42f_id", ""), "candidate_visual_line_zones": row.get("candidate_visual_line_zones", "")}
        output.append(
            {
                **row,
                "image_src": html_image_src(row.get("local_image_path", "")),
                "fragment_crop_boxes": split_pipe(row.get("top_fragment_crop_boxes", "")),
                "candidate_options": candidate_options(row, pseudo_zone),
            }
        )
    return output


def render_html(rows: list[dict[str, str]], confirmation_csv: str) -> str:
    rows_json = json.dumps(rows_for_html(rows), ensure_ascii=True)
    static_rows = "".join(
        f"<li><strong>{html.escape(row['route42l_id'])}</strong> {html.escape(row['target_locus'])} "
        f"- sugerida linha {html.escape(row['suggested_visual_line_number'])}</li>"
        for row in rows[:20]
    )
    return f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Rota 42L - Confirmar linha sugerida</title>
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
    button.primary {{ background: #e8f4ef; border-color: #8bbdb6; color: #164f47; }}
    button.warn {{ background: #fbebe6; border-color: #d2aaa1; color: var(--warn); }}
    .app {{ min-height: 100vh; display: grid; grid-template-rows: auto minmax(0, 1fr); }}
    .topbar {{ display: flex; justify-content: space-between; align-items: center; gap: 16px; padding: 12px 16px; border-bottom: 1px solid var(--line); background: #fbf6ed; }}
    h1, h2 {{ margin: 0; }}
    h1 {{ font-size: 20px; }}
    p {{ margin: 0; color: var(--muted); }}
    .nav {{ display: flex; gap: 8px; flex-wrap: wrap; justify-content: flex-end; }}
    .toolbar {{ display: flex; gap: 8px; flex-wrap: wrap; padding: 10px 16px; border-bottom: 1px solid var(--line); background: #f7efe4; }}
    .workspace {{ min-height: 0; display: grid; grid-template-columns: 310px minmax(0, 1fr) 360px; }}
    .queue {{ overflow: auto; border-right: 1px solid var(--line); background: #efe4d4; padding: 10px; }}
    .queue button {{ width: 100%; display: grid; gap: 4px; text-align: left; margin-bottom: 7px; }}
    .queue button.active {{ border-color: var(--accent); outline: 3px solid rgba(31, 118, 104, .2); }}
    .main {{ overflow: auto; padding: 14px; background: #e6ddd0; }}
    .target-card {{ border: 1px solid var(--line); border-radius: 8px; background: var(--panel); padding: 14px; display: grid; gap: 12px; }}
    .meta-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(170px, 1fr)); gap: 8px; }}
    .meta {{ border: 1px solid #ded2c2; border-radius: 7px; padding: 8px; background: #fffdf8; }}
    .meta b {{ display: block; font-size: 12px; color: var(--muted); }}
    .choice-grid, .crop-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 10px; }}
    .choice-card {{ display: grid; gap: 8px; padding: 8px; border: 1px solid var(--line); border-radius: 8px; background: #fffaf2; text-align: left; }}
    .choice-card.selected {{ border-color: var(--accent); outline: 3px solid rgba(31, 118, 104, .18); background: #eef6f2; }}
    .choice-card.suggested {{ border-color: #8bbdb6; }}
{VISUAL_CROP_CSS}
    .side {{ overflow: auto; border-left: 1px solid var(--line); background: var(--panel); padding: 14px; }}
    .plain-box {{ border: 1px solid var(--line); border-radius: 8px; background: #fff7ea; padding: 12px; margin-bottom: 12px; }}
    .plain-box h3 {{ margin: 0 0 8px; font-size: 15px; }}
    .warning {{ color: var(--warn); font-weight: 850; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; overflow-wrap: anywhere; }}
    textarea {{ width: 100%; min-height: 180px; white-space: pre; border: 1px solid var(--line); border-radius: 8px; padding: 8px; background: #fffef9; }}
    ol {{ margin: 0; padding-left: 20px; color: var(--muted); }}
  </style>
</head>
<body>
<div class="app">
  <header class="topbar">
    <div>
      <h1>Rota 42L - Confirmar linha sugerida</h1>
      <p>Use a sugestao da R42K como ponto de partida. Nao aplicar automaticamente.</p>
    </div>
    <nav class="nav" aria-label="Navegacao entre rotas">
      <a class="button-link" href="rota_42g_ferramentas_ativas_r32.html">Ferramentas ativas</a>
      <a class="button-link" href="rota_42k_fila_priorizada_revisao_visual_r32.html">Abrir R42K</a>
      <a class="button-link" href="rota_42m_captura_fina_linhas_r32.html">Abrir R42M</a>
      <a class="button-link" href="rota_42f_escolha_linhas_visuais_sem_zona_r32.html">Abrir R42F</a>
      <a class="button-link" href="rota_42c_calibrador_linhas_baseline_r32.html">Abrir R42C</a>
    </nav>
  </header>
  <nav class="toolbar" aria-label="Acoes">
    <button type="button" id="prevItem">Anterior</button>
    <button type="button" id="nextItem">Proximo</button>
    <button type="button" class="primary" id="useSuggested">Usar linha sugerida</button>
    <button type="button" class="warn" id="markUncertain">Marcar duvida</button>
    <button type="button" id="generateCsv">Gerar CSV</button>
    <button type="button" id="copyCsv">Copiar CSV</button>
    <button type="button" id="downloadCsv">Baixar CSV</button>
  </nav>
  <main class="workspace">
    <aside class="queue" id="queue" aria-label="Itens para confirmar"></aside>
    <section class="main" aria-label="Confirmacao da linha">
      <article class="target-card" id="targetCard"></article>
    </section>
    <aside class="side" aria-label="CSV e instrucoes">
      <section class="plain-box">
        <h3>Como usar</h3>
        <p>Compare a linha sugerida com os fragmentos. Se estiver certa, clique em <b>Usar linha sugerida</b>. Se outra linha parecer melhor, clique nessa linha e gere o CSV.</p>
      </section>
      <section class="plain-box">
        <h3>Resumo</h3>
        <ol>{static_rows or '<li>Nenhum item para confirmar.</li>'}</ol>
      </section>
      <section class="plain-box">
        <h3>CSV de confirmação</h3>
        <p class="mono">{html.escape(confirmation_csv)}</p>
        <textarea id="csvDraft" readonly></textarea>
      </section>
      <section class="plain-box">
        <h3>Guarda</h3>
        <p class="mono">{GUARDRAIL}</p>
        <p class="warning">Nao usar como OCR nem como evidencia. Esta pagina so prepara confirmacao humana.</p>
      </section>
    </aside>
  </main>
</div>
<script>
const CONFIRM_ROWS = {rows_json};
let currentIndex = 0;
const draftById = new Map();

{VISUAL_CROP_JS}

const CSV_FIELDS = {json.dumps(FIELDNAMES, ensure_ascii=True)};

function activeRow() {{
  return CONFIRM_ROWS[currentIndex] || null;
}}

function csvEscape(value) {{
  const text = String(value ?? "");
  if (/[",\\n]/.test(text)) return `"${{text.replaceAll('"', '""')}}"`;
  return text;
}}

function rowDraft(row) {{
  return draftById.get(row.route42l_id) || row;
}}

function setDecision(row, lineNumber, boxPct, status) {{
  draftById.set(row.route42l_id, {{
    ...rowDraft(row),
    selected_visual_line_number: lineNumber || "",
    selected_zone_box_pct: boxPct || "",
    confirmation_status: status,
  }});
  renderAll();
}}

function renderQueue() {{
  const queue = document.getElementById("queue");
  queue.innerHTML = "";
  CONFIRM_ROWS.forEach((row, index) => {{
    const draft = rowDraft(row);
    const button = document.createElement("button");
    button.type = "button";
    button.className = index === currentIndex ? "active" : "";
    button.innerHTML = `
      <strong>${{row.route42l_id}} / ${{row.target_locus}}</strong>
      <small>sugerida linha ${{row.suggested_visual_line_number}} / ${{draft.confirmation_status}}</small>
    `;
    button.addEventListener("click", () => {{
      currentIndex = index;
      renderAll();
    }});
    queue.appendChild(button);
  }});
  if (!CONFIRM_ROWS.length) queue.innerHTML = "<p>Nenhum item para confirmar.</p>";
}}

function cropCanvas(label, box, row, className = "") {{
  if (!box) return "";
  return `
    <article class="visual-crop-card ${{className}}">
      <span class="visual-crop-label">${{label}}</span>
      <canvas class="visual-crop-canvas" data-crop-preview data-image-src="${{row.image_src}}" data-box-pct="${{box}}" aria-label="${{label}}"></canvas>
      <span class="visual-crop-note">${{box}}</span>
    </article>
  `;
}}

function renderCandidateOptions(row, draft) {{
  if (!row.candidate_options.length) return '<p class="warning">Sem opcoes de linha.</p>';
  return row.candidate_options.map((option) => {{
    const selected = draft.selected_visual_line_number === option.line_number;
    const classes = ["choice-card"];
    if (selected) classes.push("selected");
    if (option.is_suggested) classes.push("suggested");
    return `
      <button type="button" class="${{classes.join(" ")}}" data-line="${{option.line_number}}" data-box="${{option.box_pct}}">
        <strong>linha visual ${{option.line_number}}${{option.is_suggested ? " - sugerida" : ""}}</strong>
        ${{cropCanvas("recorte da linha " + option.line_number, option.box_pct, row)}}
      </button>
    `;
  }}).join("");
}}

function renderTarget() {{
  const card = document.getElementById("targetCard");
  const row = activeRow();
  if (!row) {{
    card.innerHTML = '<p class="warning">Nenhum item para confirmar.</p>';
    return;
  }}
  const draft = rowDraft(row);
  const fragmentCards = row.fragment_crop_boxes.map((box, index) =>
    cropCanvas("fragmento R42J " + (index + 1), box, row, "is-target")
  ).join("") || '<p class="warning">Sem fragmentos R42J para este item.</p>';
  card.innerHTML = `
    <div>
      <h2>${{row.route42l_id}} / ${{row.target_locus}}</h2>
      <p>${{row.route42f_id}} / ${{row.review_bucket}} / score ${{row.review_priority_score}}</p>
    </div>
    <div class="meta-grid">
      <div class="meta"><b>linha sugerida</b>${{row.suggested_visual_line_number || "sem sugestao"}}</div>
      <div class="meta"><b>status</b>${{draft.confirmation_status}}</div>
      <div class="meta"><b>linha selecionada</b>${{draft.selected_visual_line_number || "nenhuma"}}</div>
      <div class="meta"><b>folio</b>${{row.folio}}</div>
    </div>
    <div class="meta"><b>texto tecnico de referencia</b><span class="mono">${{row.transcription_text}}</span></div>
    <h3>Fragmentos da R42J</h3>
    <div class="crop-grid">${{fragmentCards}}</div>
    <h3>Escolha uma linha candidata</h3>
    <div class="choice-grid" id="choiceGrid">${{renderCandidateOptions(row, draft)}}</div>
  `;
  for (const button of card.querySelectorAll(".choice-card")) {{
    button.addEventListener("click", () => {{
      setDecision(row, button.dataset.line || "", button.dataset.box || "", "line_selected_pending_apply");
    }});
  }}
  paintCropPreviews(card);
}}

function generateCsv() {{
  const lines = [CSV_FIELDS.join(",")];
  for (const row of CONFIRM_ROWS) {{
    const draft = rowDraft(row);
    lines.push(CSV_FIELDS.map((field) => csvEscape(draft[field] ?? "")).join(","));
  }}
  document.getElementById("csvDraft").value = lines.join("\\n");
}}

function renderAll() {{
  renderQueue();
  renderTarget();
  generateCsv();
}}

document.getElementById("prevItem").addEventListener("click", () => {{
  currentIndex = Math.max(0, currentIndex - 1);
  renderAll();
}});
document.getElementById("nextItem").addEventListener("click", () => {{
  currentIndex = Math.min(CONFIRM_ROWS.length - 1, currentIndex + 1);
  renderAll();
}});
document.getElementById("useSuggested").addEventListener("click", () => {{
  const row = activeRow();
  if (row) setDecision(row, row.suggested_visual_line_number, row.suggested_zone_box_pct, "line_selected_pending_apply");
}});
document.getElementById("markUncertain").addEventListener("click", () => {{
  const row = activeRow();
  if (row) setDecision(row, "", "", "uncertain_needs_manual_review");
}});
document.getElementById("generateCsv").addEventListener("click", generateCsv);
document.getElementById("copyCsv").addEventListener("click", async () => {{
  generateCsv();
  await navigator.clipboard.writeText(document.getElementById("csvDraft").value);
}});
document.getElementById("downloadCsv").addEventListener("click", () => {{
  generateCsv();
  const blob = new Blob([document.getElementById("csvDraft").value], {{ type: "text/csv;charset=utf-8" }});
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "ready_visual_line_choice_confirmation_zl3b.csv";
  link.click();
  URL.revokeObjectURL(url);
}});

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
    queue_csv: Path,
    zone_choice_csv: Path,
    confirmation_csv: Path,
    summary_csv: Path,
    html_path: Path,
) -> None:
    lines = [
        "# Rota 42L: confirmacao de linhas sugeridas",
        "",
        "Esta rota transforma a fila R42K em uma tela de confirmacao humana para selecionar a linha visual antes de qualquer aplicacao.",
        "",
        "Ela nao aplica automaticamente, nao e OCR, nao le EVA, nao traduz e nao cria evidencia visual.",
        "",
        f"Entrada R42K: `{queue_csv}`.",
        f"Entrada R42F: `{zone_choice_csv}`.",
        f"CSV de confirmacao: `{confirmation_csv}`.",
        f"Resumo: `{summary_csv}`.",
        f"HTML: `{html_path}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens pendentes de confirmacao: {len(rows)};",
        f"- guarda: `{GUARDRAIL}`.",
        "",
    ]
    lines.extend(render_counts("Buckets de origem", Counter(row.get("review_bucket", "") for row in rows)))
    lines.extend(render_counts("Folios", Counter(row.get("folio", "") for row in rows)))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--queue-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_review_priority_queue_zl3b.csv"),
        help="Route 42K priority queue CSV",
    )
    parser.add_argument(
        "--zone-choice-csv",
        default=str(ROOT / "data" / "annotations" / "ready_visual_line_zone_choice_zl3b.csv"),
        help="Route 42F zone choice CSV",
    )
    parser.add_argument(
        "--confirmation-csv",
        default=str(ROOT / "data" / "annotations" / "ready_visual_line_choice_confirmation_zl3b.csv"),
        help="Route 42L confirmation CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_line_choice_confirmation_summary_zl3b.csv"),
        help="Route 42L summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_42l_confirmacao_linhas_sugeridas_r32.md"),
        help="Route 42L Markdown report output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_42l_confirmacao_linhas_sugeridas_r32.html"),
        help="Route 42L HTML output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    queue_csv = Path(args.queue_csv)
    zone_choice_csv = Path(args.zone_choice_csv)
    confirmation_csv = Path(args.confirmation_csv)
    summary_csv = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)

    queue_rows = read_csv(queue_csv)
    zone_rows = read_csv(zone_choice_csv)
    rows = build_confirmation_rows(queue_rows, zone_rows)

    write_csv(confirmation_csv, rows, FIELDNAMES)
    write_summary_csv(summary_csv, rows)
    write_markdown_report(md_path, rows, queue_csv, zone_choice_csv, confirmation_csv, summary_csv, html_path)
    html_path.parent.mkdir(parents=True, exist_ok=True)
    html_path.write_text(render_html(rows, str(confirmation_csv)), encoding="utf-8")

    print(f"confirmation_items={len(rows)}")
    print(f"confirmation_csv={confirmation_csv.resolve()}")
    print(f"summary_csv={summary_csv.resolve()}")
    print(f"md={md_path.resolve()}")
    print(f"html={html_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
