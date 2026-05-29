#!/usr/bin/env python3
"""Prepare a direct visual decision package for pending P0/P1 items."""
from __future__ import annotations

import argparse
import csv
import html
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS_TO_FILL = (
    "manual_token_seen manual_new_crop_needed manual_image_insufficient "
    "manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def html_image_path(path: str) -> str:
    if not path:
        return ""
    return f"../{path}"


def is_pending_decision(row: dict[str, str]) -> bool:
    return row.get("decision_bucket") == "pending_manual_decision"


def build_direct_visual_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    pending = [row for row in rows if is_pending_decision(row)]
    direct_rows: list[dict[str, str]] = []
    for index, row in enumerate(pending, start=1):
        direct_rows.append(
            {
                "route19_id": f"R19-{index:03d}",
                "route18_id": row.get("route18_id", ""),
                "route17_id": row.get("route17_id", ""),
                "route16_id": row.get("route16_id", ""),
                "instruction_item_id": row.get("instruction_item_id", ""),
                "checklist_id": row.get("checklist_id", ""),
                "packet_id": row.get("packet_id", ""),
                "route11_id": row.get("route11_id", ""),
                "route10_id": row.get("route10_id", ""),
                "manual_review_id": row.get("manual_review_id", ""),
                "crop_id": row.get("crop_id", ""),
                "source_review_id": row.get("source_review_id", ""),
                "folio": row.get("folio", ""),
                "locus": row.get("locus", ""),
                "source_image": row.get("source_image", ""),
                "crop_svg": row.get("crop_svg", ""),
                "review_region": row.get("review_region", ""),
                "priority_bucket": row.get("priority_bucket", ""),
                "priority_level": row.get("priority_level", ""),
                "target_type": row.get("target_type", ""),
                "review_target": row.get("review_target", ""),
                "decision_bucket": row.get("decision_bucket", ""),
                "decision_package_status": "ready_for_manual_visual_decision",
                "fields_to_fill": FIELDS_TO_FILL,
                "manual_token_seen": "",
                "manual_new_crop_needed": "",
                "manual_image_insufficient": "",
                "manual_new_crop_x": "",
                "manual_new_crop_y": "",
                "manual_new_crop_width": "",
                "manual_new_crop_height": "",
                "manual_notes": "",
                "visual_action": "open_source_image_and_svg_side_by_side",
                "output_rule": "copy_manual_values_back_to_packet_item_checklist",
                "semantic_guardrail": "direct_visual_package_not_evidence",
            }
        )
    return direct_rows


def summarize_direct_visual_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
        "packet_id": Counter(row.get("packet_id", "") for row in rows),
        "target_type": Counter(row.get("target_type", "") for row in rows),
        "decision_package_status": Counter(row.get("decision_package_status", "") for row in rows),
    }


FIELDNAMES = [
    "route19_id",
    "route18_id",
    "route17_id",
    "route16_id",
    "instruction_item_id",
    "checklist_id",
    "packet_id",
    "route11_id",
    "route10_id",
    "manual_review_id",
    "crop_id",
    "source_review_id",
    "folio",
    "locus",
    "source_image",
    "crop_svg",
    "review_region",
    "priority_bucket",
    "priority_level",
    "target_type",
    "review_target",
    "decision_bucket",
    "decision_package_status",
    "fields_to_fill",
    "manual_token_seen",
    "manual_new_crop_needed",
    "manual_image_insufficient",
    "manual_new_crop_x",
    "manual_new_crop_y",
    "manual_new_crop_width",
    "manual_new_crop_height",
    "manual_notes",
    "visual_action",
    "output_rule",
    "semantic_guardrail",
]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
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


def render_counts(title: str, counts: Counter[str]) -> list[str]:
    lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"|{key}|{value}|")
    lines.append("")
    return lines


def render_markdown_section(row: dict[str, str]) -> str:
    lines = [
        f"## {row['route19_id']} / {row['checklist_id']} / {row.get('folio', '')}",
        "",
        f"- alvo: `{row.get('review_target', '')}`;",
        f"- imagem fonte: `{row.get('source_image', '')}`;",
        f"- SVG de referencia: `{row.get('crop_svg', '')}`;",
        f"- regiao atual: `{row.get('review_region', '')}`;",
        f"- campos a preencher: `{row.get('fields_to_fill', FIELDS_TO_FILL)}`;",
        f"- regra de saida: `{row.get('output_rule', '')}`;",
        f"- guarda: `{row.get('semantic_guardrail', '')}`;",
        "",
    ]
    return "\n".join(lines)


def render_html_card(row: dict[str, str]) -> str:
    source = html.escape(html_image_path(row.get("source_image", "")))
    svg = html.escape(html_image_path(row.get("crop_svg", "")))
    title = html.escape(f"{row.get('route19_id', '')} / {row.get('checklist_id', '')} / {row.get('folio', '')}")
    target = html.escape(row.get("review_target", ""))
    fields = html.escape(row.get("fields_to_fill", FIELDS_TO_FILL))
    guardrail = html.escape(row.get("semantic_guardrail", ""))
    output_rule = html.escape(row.get("output_rule", ""))
    return f"""
    <article class="review-card">
      <header>
        <h2>{title}</h2>
        <p><strong>Alvo:</strong> <code>{target}</code></p>
      </header>
      <div class="media-grid">
        <figure>
          <figcaption>Imagem fonte</figcaption>
          <img src="{source}" alt="Imagem fonte para {title}">
        </figure>
        <figure>
          <figcaption>SVG de referencia</figcaption>
          <img src="{svg}" alt="SVG de referencia para {title}">
        </figure>
      </div>
      <section class="fields">
        <p><strong>Campos a preencher:</strong> <code>{fields}</code></p>
        <p><strong>Regra:</strong> <code>{output_rule}</code></p>
        <p><strong>Guarda:</strong> <code>{guardrail}</code></p>
      </section>
    </article>
    """.strip()


def write_markdown_report(
    path: Path,
    rows: list[dict[str, str]],
    source_csv: Path,
    output_csv: Path,
    summary_csv: Path,
    html_path: Path,
) -> None:
    summary = summarize_direct_visual_rows(rows)
    lines = [
        "# Rota 19: pacote visual direto P0/P1",
        "",
        "Esta rota cria um pacote visual direto para preencher os 6 itens P0/P1 pendentes. Ela nao decide campos manuais e nao cria evidencia visual por inferencia.",
        "",
        f"Fonte: `{source_csv}`.",
        f"Pacote CSV: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        f"Pacote HTML: `{html_path}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens no pacote visual: {len(rows)};",
        f"- P0: {summary['priority_level'].get('P0', 0)};",
        f"- P1: {summary['priority_level'].get('P1', 0)};",
        "- campos manuais permanecem em branco;",
        "- guarda: `direct_visual_package_not_evidence`.",
        "",
    ]
    lines.extend(render_counts("Prioridade", summary["priority_level"]))
    lines.extend(render_counts("Folios", summary["folio"]))
    lines.extend(render_counts("Status do pacote", summary["decision_package_status"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota19|checklist|prioridade|folio|alvo|imagem|SVG|",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['route19_id']}|{row['checklist_id']}|{row['priority_level']}|{row['folio']}|{row['review_target']}|`{row['source_image']}`|`{row['crop_svg']}`|"
        )
    lines.append("")
    for row in rows:
        lines.append(render_markdown_section(row))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_html_report(path: Path, rows: list[dict[str, str]]) -> None:
    cards = "\n".join(render_html_card(row) for row in rows)
    document = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Rota 19 - pacote visual direto P0/P1</title>
  <style>
    body {{
      margin: 24px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #1f2933;
      background: #f6f5f2;
    }}
    h1 {{ margin-bottom: 8px; }}
    .review-card {{
      margin: 24px 0;
      padding: 16px;
      border: 1px solid #c9c3b8;
      background: #fffdfa;
      border-radius: 6px;
    }}
    .media-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
      gap: 16px;
    }}
    figure {{ margin: 0; }}
    figcaption {{ font-weight: 700; margin-bottom: 8px; }}
    img {{
      width: 100%;
      max-height: 720px;
      object-fit: contain;
      background: #ebe7df;
      border: 1px solid #d8d1c7;
    }}
    code {{ white-space: normal; }}
  </style>
</head>
<body>
  <h1>Rota 19: pacote visual direto P0/P1</h1>
  <p>Use este HTML para revisar imagem fonte e SVG lado a lado. Preencha os campos manuais na checklist, nao neste arquivo.</p>
  {cards}
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("priority_decisions_csv", help="CSV from ingest_priority_human_decisions.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "annotations" / "direct_visual_decision_package_p0_p1_zl3b.csv"),
        help="Direct visual package CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "direct_visual_decision_package_summary_zl3b.csv"),
        help="Direct visual package summary output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_19_pacote_visual_direto_p0_p1.md"),
        help="Markdown report output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_19_pacote_visual_direto_p0_p1.html"),
        help="HTML visual review package output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = Path(args.priority_decisions_csv)
    rows = build_direct_visual_rows(read_csv(source))
    summary = summarize_direct_visual_rows(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)
    write_csv(csv_path, rows)
    write_summary_csv(summary_path, summary)
    write_markdown_report(md_path, rows, source, csv_path, summary_path, html_path)
    write_html_report(html_path, rows)
    print(
        f"direct_visual_package_rows={len(rows)} "
        f"p0={summary['priority_level'].get('P0', 0)} "
        f"p1={summary['priority_level'].get('P1', 0)}"
    )
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    print(f"html={html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
