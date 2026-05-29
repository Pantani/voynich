#!/usr/bin/env python3
"""Prepare a guided HTML surface for filling route 21 visual decisions."""
from __future__ import annotations

import argparse
import csv
import html
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

CSV_TARGET_FIELD_LIST = (
    "manual_token_seen manual_new_crop_needed manual_image_insufficient "
    "manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes"
)

CARD_STATUS = "ready_for_guided_manual_entry"
OUTPUT_RULE = "fill_r21_csv_manually_then_rerun_route_22"
GUARDRAIL = "guided_html_not_visual_evidence"

FIELDNAMES = [
    "route23_id",
    "route22_id",
    "route21_id",
    "route20_id",
    "route19_id",
    "route18_id",
    "route17_id",
    "checklist_id",
    "packet_id",
    "manual_review_id",
    "crop_id",
    "folio",
    "source_image",
    "crop_svg",
    "review_region",
    "priority_level",
    "target_type",
    "review_target",
    "validation_status",
    "apply_status",
    "allowed_manual_token_seen",
    "allowed_manual_new_crop_needed",
    "allowed_manual_image_insufficient",
    "csv_target_field_list",
    "html_card_status",
    "visual_action",
    "output_rule",
    "semantic_guardrail",
]


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


def validation_index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("route21_id", ""): row for row in rows if row.get("route21_id", "")}


def is_pending_validation(row: dict[str, str]) -> bool:
    return row.get("validation_status") == "pending_blank_manual_entry"


def build_guided_rows(
    entry_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    validation_by_route21 = validation_index(validation_rows)
    guided_rows: list[dict[str, str]] = []
    for entry in entry_rows:
        validation = validation_by_route21.get(entry.get("route21_id", ""), {})
        if not is_pending_validation(validation):
            continue
        guided_rows.append(
            {
                "route23_id": f"R23-{len(guided_rows) + 1:03d}",
                "route22_id": validation.get("route22_id", ""),
                "route21_id": entry.get("route21_id", ""),
                "route20_id": entry.get("route20_id", ""),
                "route19_id": entry.get("route19_id", ""),
                "route18_id": entry.get("route18_id", ""),
                "route17_id": entry.get("route17_id", ""),
                "checklist_id": entry.get("checklist_id", ""),
                "packet_id": entry.get("packet_id", ""),
                "manual_review_id": entry.get("manual_review_id", ""),
                "crop_id": entry.get("crop_id", ""),
                "folio": entry.get("folio", ""),
                "source_image": entry.get("source_image", ""),
                "crop_svg": entry.get("crop_svg", ""),
                "review_region": entry.get("review_region", ""),
                "priority_level": entry.get("priority_level", ""),
                "target_type": entry.get("target_type", ""),
                "review_target": entry.get("review_target", ""),
                "validation_status": validation.get("validation_status", ""),
                "apply_status": validation.get("apply_status", ""),
                "allowed_manual_token_seen": entry.get("allowed_manual_token_seen", ""),
                "allowed_manual_new_crop_needed": entry.get("allowed_manual_new_crop_needed", ""),
                "allowed_manual_image_insufficient": entry.get("allowed_manual_image_insufficient", ""),
                "csv_target_field_list": CSV_TARGET_FIELD_LIST,
                "html_card_status": CARD_STATUS,
                "visual_action": "open_source_image_and_svg_then_fill_r21_csv",
                "output_rule": OUTPUT_RULE,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return guided_rows


def summarize_guided_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "html_card_status": Counter(row.get("html_card_status", "") for row in rows),
        "validation_status": Counter(row.get("validation_status", "") for row in rows),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
        "target_type": Counter(row.get("target_type", "") for row in rows),
    }


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


def render_counts(title: str, counts: Counter[str]) -> list[str]:
    lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"|{key}|{value}|")
    lines.append("")
    return lines


def render_markdown_section(row: dict[str, str]) -> str:
    lines = [
        f"## {row['route23_id']} / {row.get('route21_id', '')} / {row.get('route19_id', '')}",
        "",
        f"- checklist: `{row.get('checklist_id', '')}`;",
        f"- alvo: `{row.get('review_target', '')}`;",
        f"- imagem fonte: `{row.get('source_image', '')}`;",
        f"- SVG de referencia: `{row.get('crop_svg', '')}`;",
        f"- campos no CSV R21: `{row.get('csv_target_field_list', '')}`;",
        f"- regra de saida: `{row.get('output_rule', '')}`;",
        f"- guarda: `{row.get('semantic_guardrail', '')}`;",
        "",
    ]
    return "\n".join(lines)


def render_html_card(row: dict[str, str]) -> str:
    title = html.escape(f"{row.get('route23_id', '')} / {row.get('route21_id', '')} / {row.get('route19_id', '')}")
    source = html.escape(html_image_path(row.get("source_image", "")))
    svg = html.escape(html_image_path(row.get("crop_svg", "")))
    target = html.escape(row.get("review_target", ""))
    checklist = html.escape(row.get("checklist_id", ""))
    manual_review_id = html.escape(row.get("manual_review_id", ""))
    crop_id = html.escape(row.get("crop_id", ""))
    token_seen = html.escape(row.get("allowed_manual_token_seen", ""))
    new_crop = html.escape(row.get("allowed_manual_new_crop_needed", ""))
    image_insufficient = html.escape(row.get("allowed_manual_image_insufficient", ""))
    fields = html.escape(row.get("csv_target_field_list", CSV_TARGET_FIELD_LIST))
    output_rule = html.escape(row.get("output_rule", ""))
    guardrail = html.escape(row.get("semantic_guardrail", ""))
    return f"""
    <article class="review-card" id="{html.escape(row.get('route23_id', ''))}">
      <header>
        <h2>{title}</h2>
        <p><strong>Checklist:</strong> <code>{checklist}</code> <strong>Manual:</strong> <code>{manual_review_id}</code> <strong>Crop:</strong> <code>{crop_id}</code></p>
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
      <section class="entry">
        <h3>Valores permitidos</h3>
        <dl>
          <dt>manual_token_seen</dt><dd><code>{token_seen}</code></dd>
          <dt>manual_new_crop_needed</dt><dd><code>{new_crop}</code></dd>
          <dt>manual_image_insufficient</dt><dd><code>{image_insufficient}</code></dd>
        </dl>
        <p><strong>Campos no CSV R21:</strong> <code>{fields}</code></p>
        <p><strong>Regra:</strong> <code>{output_rule}</code></p>
        <p><strong>Guarda:</strong> <code>{guardrail}</code></p>
      </section>
    </article>
    """.strip()


def write_html_report(path: Path, rows: list[dict[str, str]], entry_sheet_csv: Path) -> None:
    cards = "\n".join(render_html_card(row) for row in rows)
    document = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Rota 23 - preenchimento visual guiado R21</title>
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
    dl {{
      display: grid;
      grid-template-columns: max-content 1fr;
      gap: 6px 12px;
    }}
    dt {{ font-weight: 700; }}
    code {{ white-space: normal; }}
  </style>
</head>
<body>
  <h1>Rota 23: preenchimento visual guiado R21</h1>
  <p>Use este HTML como guia visual. Preencha manualmente o CSV <code>{html.escape(str(entry_sheet_csv))}</code> e reexecute a Rota 22.</p>
  {cards}
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="utf-8")


def write_markdown_report(
    path: Path,
    rows: list[dict[str, str]],
    entry_sheet_csv: Path,
    validation_log_csv: Path,
    manifest_csv: Path,
    summary_csv: Path,
    html_path: Path,
) -> None:
    summary = summarize_guided_rows(rows)
    lines = [
        "# Rota 23: pacote HTML guiado para preencher R21",
        "",
        "Esta rota gera uma superficie HTML para guiar o preenchimento manual da planilha R21. Ela nao grava decisoes e nao cria evidencia visual.",
        "",
        f"Planilha R21: `{entry_sheet_csv}`.",
        f"Log R22: `{validation_log_csv}`.",
        f"Manifest: `{manifest_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        f"HTML guiado: `{html_path}`.",
        "",
        "## Resultado curto",
        "",
        f"- cartoes HTML gerados: {len(rows)};",
        f"- P0: {summary['priority_level'].get('P0', 0)};",
        f"- P1: {summary['priority_level'].get('P1', 0)};",
        "- decisoes seguem fora do HTML e devem ser preenchidas no CSV R21;",
        "- guarda: `guided_html_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Status do cartao", summary["html_card_status"]))
    lines.extend(render_counts("Status R22", summary["validation_status"]))
    lines.extend(render_counts("Prioridade", summary["priority_level"]))
    lines.extend(render_counts("Folios", summary["folio"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota23|rota22|rota21|rota19|checklist|prioridade|folio|alvo|imagem|SVG|",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['route23_id']}|{row['route22_id']}|{row['route21_id']}|{row['route19_id']}|{row['checklist_id']}|{row['priority_level']}|{row['folio']}|{row['review_target']}|`{row['source_image']}`|`{row['crop_svg']}`|"
        )
    lines.append("")
    for row in rows:
        lines.append(render_markdown_section(row))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entry_sheet_csv", help="CSV from prepare_visual_decision_entry_sheet.py")
    parser.add_argument("validation_log_csv", help="CSV from validate_visual_decision_entry_sheet.py")
    parser.add_argument(
        "--manifest-csv",
        default=str(ROOT / "data" / "derived" / "guided_visual_entry_html_manifest_zl3b.csv"),
        help="Guided HTML manifest CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "guided_visual_entry_html_summary_zl3b.csv"),
        help="Guided HTML summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_23_pacote_html_preenchimento_r21.md"),
        help="Markdown report output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_23_pacote_html_preenchimento_r21.html"),
        help="Guided HTML output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    entry_sheet_csv = Path(args.entry_sheet_csv)
    validation_log_csv = Path(args.validation_log_csv)
    rows = build_guided_rows(read_csv(entry_sheet_csv), read_csv(validation_log_csv))
    summary = summarize_guided_rows(rows)
    manifest_path = Path(args.manifest_csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)
    write_csv(manifest_path, rows, FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_markdown_report(md_path, rows, entry_sheet_csv, validation_log_csv, manifest_path, summary_path, html_path)
    write_html_report(html_path, rows, entry_sheet_csv)
    print(
        f"guided_html_cards={len(rows)} "
        f"p0={summary['priority_level'].get('P0', 0)} "
        f"p1={summary['priority_level'].get('P1', 0)}"
    )
    print(f"manifest_csv={manifest_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    print(f"html={html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
