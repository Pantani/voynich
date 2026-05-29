#!/usr/bin/env python3
"""Prepare a focused HTML/CSV package for route 28 ready manual visual annotations."""
from __future__ import annotations

import argparse
import csv
import html
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "focused_visual_annotation_html_not_evidence"
CARD_STATUS = "ready_for_focused_manual_visual_annotation"
PENDING_STATUS = "pending_blank_manual_annotation"
ALLOWED_MANUAL_STATUS = "annotated/not_visible/uncertain"
FIELDS_TO_FILL = "manual_annotation_status manual_visual_notes"
OUTPUT_RULE = "copy_completed_fields_back_to_route28_package_then_rerun_route31"

FIELDNAMES = [
    "route32_id",
    "route31_id",
    "route28_id",
    "route27_id",
    "folio",
    "locus_kind",
    "priority_level",
    "gap_rows",
    "unique_loci",
    "token_counts",
    "top_loci",
    "section_notes",
    "image_url",
    "commons_page",
    "r31_validation_status",
    "html_card_status",
    "allowed_manual_annotation_status",
    "fields_to_fill",
    "manual_annotation_status",
    "manual_visual_notes",
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


def markdown_cell(value: str) -> str:
    return value.replace("|", "<br>")


def build_ready_html_rows(
    package_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    validation_by_route28 = {row.get("route28_id", ""): row for row in validation_rows}
    rows: list[dict[str, str]] = []
    for package in package_rows:
        if package.get("package_status") != "ready_for_manual_visual_annotation":
            continue
        validation = validation_by_route28.get(package.get("route28_id", ""), {})
        if validation.get("manual_validation_status", "") != PENDING_STATUS:
            continue
        rows.append(
            {
                "route32_id": f"R32-{len(rows) + 1:03d}",
                "route31_id": validation.get("route31_id", ""),
                "route28_id": package.get("route28_id", ""),
                "route27_id": package.get("route27_id", ""),
                "folio": package.get("folio", ""),
                "locus_kind": package.get("locus_kind", ""),
                "priority_level": package.get("priority_level", ""),
                "gap_rows": package.get("gap_rows", ""),
                "unique_loci": package.get("unique_loci", ""),
                "token_counts": package.get("token_counts", ""),
                "top_loci": package.get("top_loci", ""),
                "section_notes": package.get("section_notes", ""),
                "image_url": package.get("image_url", ""),
                "commons_page": package.get("commons_page", ""),
                "r31_validation_status": validation.get("manual_validation_status", ""),
                "html_card_status": CARD_STATUS,
                "allowed_manual_annotation_status": ALLOWED_MANUAL_STATUS,
                "fields_to_fill": FIELDS_TO_FILL,
                "manual_annotation_status": "",
                "manual_visual_notes": "",
                "output_rule": OUTPUT_RULE,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def summarize_ready_html_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "html_card_status": Counter(row.get("html_card_status", "") for row in rows),
        "r31_validation_status": Counter(row.get("r31_validation_status", "") for row in rows),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "locus_kind": Counter(row.get("locus_kind", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
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
        lines.append(f"|{markdown_cell(key)}|{value}|")
    lines.append("")
    return lines


def render_markdown_section(row: dict[str, str]) -> str:
    lines = [
        f"### {row.get('route32_id', '')}: {row.get('folio', '')} / {row.get('route28_id', '')}",
        "",
        f"- R31: `{row.get('route31_id', '')}`;",
        f"- prioridade: `{row.get('priority_level', '')}`;",
        f"- locus: `{row.get('locus_kind', '')}`;",
        f"- tokens: `{row.get('token_counts', '')}`;",
        f"- valores permitidos: `{row.get('allowed_manual_annotation_status', '')}`;",
        f"- campos a preencher: `{row.get('fields_to_fill', '')}`;",
        f"- regra de saida: `{row.get('output_rule', '')}`;",
        f"- guarda: `{row.get('semantic_guardrail', '')}`.",
        "",
    ]
    return "\n".join(lines)


def render_html_card(row: dict[str, str]) -> str:
    title = html.escape(f"{row.get('route32_id', '')} / {row.get('route28_id', '')} / {row.get('folio', '')}")
    image_url = html.escape(row.get("image_url", ""))
    commons_page = html.escape(row.get("commons_page", ""))
    allowed = html.escape(row.get("allowed_manual_annotation_status", ALLOWED_MANUAL_STATUS))
    fields = html.escape(row.get("fields_to_fill", FIELDS_TO_FILL))
    guardrail = html.escape(row.get("semantic_guardrail", GUARDRAIL))
    output_rule = html.escape(row.get("output_rule", OUTPUT_RULE))
    tokens = html.escape(row.get("token_counts", ""))
    loci = html.escape(row.get("top_loci", ""))
    notes = html.escape(row.get("section_notes", ""))
    image = (
        f'<img src="{image_url}" alt="Imagem fonte para {title}">'
        if image_url
        else '<p class="source-needed">Imagem do manifesto ausente. Reexecutar R28/R31 depois de corrigir a fonte.</p>'
    )
    commons = f'<p><a href="{commons_page}">Pagina Commons</a></p>' if commons_page else ""
    return f"""
    <article class="review-card" id="{html.escape(row.get('route32_id', ''))}">
      <header>
        <h2>{title}</h2>
        <p><strong>Status R31:</strong> <code>{html.escape(row.get('r31_validation_status', ''))}</code> <strong>Prioridade:</strong> <code>{html.escape(row.get('priority_level', ''))}</code></p>
      </header>
      <div class="media">{image}{commons}</div>
      <dl>
        <dt>Tokens</dt><dd><code>{tokens}</code></dd>
        <dt>Loci</dt><dd><code>{loci}</code></dd>
        <dt>Notas de secao</dt><dd><code>{notes}</code></dd>
        <dt>Valores permitidos</dt><dd><code>{allowed}</code></dd>
        <dt>Campos CSV</dt><dd><code>{fields}</code></dd>
        <dt>Regra de saida</dt><dd><code>{output_rule}</code></dd>
        <dt>Guarda</dt><dd><code>{guardrail}</code></dd>
      </dl>
      <section class="manual-fields" aria-label="Campos manuais de apoio">
        <label>manual_annotation_status
          <select>
            <option value=""></option>
            <option value="annotated">annotated</option>
            <option value="not_visible">not_visible</option>
            <option value="uncertain">uncertain</option>
          </select>
        </label>
        <label>manual_visual_notes
          <textarea rows="4" spellcheck="false"></textarea>
        </label>
      </section>
    </article>
    """.strip()


def write_markdown_report(
    path: Path,
    rows: list[dict[str, str]],
    package_csv: Path,
    validation_csv: Path,
    entry_csv: Path,
    summary_csv: Path,
    html_path: Path,
) -> None:
    summary = summarize_ready_html_rows(rows)
    lines = [
        "# Rota 32: pacote HTML focado para anotacoes visuais prontas",
        "",
        "Esta rota cria uma superficie pequena para preencher manualmente os 8 itens da Rota 28 que ja tinham imagem no manifesto e continuam pendentes na Rota 31. O HTML/CSV nao cria evidencia visual por inferencia.",
        "",
        f"Pacote R28: `{package_csv}`.",
        f"Validacao R31: `{validation_csv}`.",
        f"Planilha manual R32: `{entry_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        f"Pacote HTML: `{html_path}`.",
        "",
        "## Resultado curto",
        "",
        f"- cartoes HTML: {len(rows)};",
        f"- pendentes R31: {summary['r31_validation_status'].get(PENDING_STATUS, 0)};",
        f"- `P0`: {summary['priority_level'].get('P0', 0)};",
        f"- `P1`: {summary['priority_level'].get('P1', 0)};",
        f"- locus `P`: {summary['locus_kind'].get('P', 0)};",
        f"- locus `L`: {summary['locus_kind'].get('L', 0)};",
        "- campos manuais permanecem em branco;",
        "- valores permitidos: `annotated/not_visible/uncertain`;",
        "- guarda: `focused_visual_annotation_html_not_evidence`.",
        "",
    ]
    lines.extend(render_counts("Status do cartao", summary["html_card_status"]))
    lines.extend(render_counts("Status R31", summary["r31_validation_status"]))
    lines.extend(render_counts("Prioridade", summary["priority_level"]))
    lines.extend(render_counts("Tipo de locus", summary["locus_kind"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota32|rota31|rota28|folio|prioridade|locus|tokens|status R31|",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{markdown_cell(row['route32_id'])}|{markdown_cell(row['route31_id'])}|{markdown_cell(row['route28_id'])}|{markdown_cell(row['folio'])}|{markdown_cell(row['priority_level'])}|{markdown_cell(row['locus_kind'])}|{markdown_cell(row['token_counts'])}|{markdown_cell(row['r31_validation_status'])}|"
        )
    lines.extend(["", "## Cartoes", ""])
    for row in rows:
        lines.append(render_markdown_section(row))
    lines.extend(
        [
            "## Leitura",
            "",
            "A rota reduz a friccao para uma revisao humana focada. Para transformar essas entradas em anotacoes derivadas, copie valores preenchidos de volta para o pacote R28 e reexecute a Rota 31.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_html_report(path: Path, rows: list[dict[str, str]], entry_csv: Path) -> None:
    cards = "\n".join(render_html_card(row) for row in rows)
    document = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Rota 32 - anotacao visual focada</title>
  <style>
    body {{
      margin: 24px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #1f2933;
      background: #f6f3ed;
    }}
    .review-card {{
      margin: 24px 0;
      padding: 16px;
      border: 1px solid #c7bda9;
      border-radius: 6px;
      background: #fffdfa;
    }}
    img {{
      width: 100%;
      max-height: 760px;
      object-fit: contain;
      background: #ebe3d5;
      border: 1px solid #d4c6af;
    }}
    dl {{
      display: grid;
      grid-template-columns: max-content 1fr;
      gap: 6px 12px;
    }}
    dt {{ font-weight: 700; }}
    code {{ white-space: pre-wrap; }}
    .manual-fields {{
      display: grid;
      gap: 10px;
      margin-top: 16px;
      padding-top: 14px;
      border-top: 1px solid #ded4c3;
    }}
    label {{
      display: grid;
      gap: 6px;
      font-weight: 700;
    }}
    select,
    textarea {{
      width: 100%;
      box-sizing: border-box;
      font: inherit;
      padding: 8px;
      border: 1px solid #b7aa96;
      border-radius: 4px;
      background: white;
    }}
    .source-needed {{
      padding: 16px;
      border: 1px dashed #9a7b4f;
      background: #fff8e6;
    }}
  </style>
</head>
<body>
  <h1>Rota 32 - anotacao visual focada</h1>
  <p>Preencher manualmente o CSV <code>{html.escape(str(entry_csv))}</code>. Este HTML mostra imagem e campos permitidos; ele nao grava decisoes automaticamente.</p>
  {cards}
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("annotation_package_csv", help="CSV generated by prepare_exact_form_visual_annotation_package.py")
    parser.add_argument("validation_csv", help="CSV generated by validate_ready_visual_annotations.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "annotations" / "ready_visual_annotation_entry_sheet_zl3b.csv"),
        help="Focused manual entry CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_html_summary_zl3b.csv"),
        help="Focused HTML package summary output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_32_pacote_html_anotacao_visual_prontos.md"),
        help="Markdown report output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_32_pacote_html_anotacao_visual_prontos.html"),
        help="HTML report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    package_csv = Path(args.annotation_package_csv)
    validation_csv = Path(args.validation_csv)
    rows = build_ready_html_rows(read_csv(package_csv), read_csv(validation_csv))
    summary = summarize_ready_html_rows(rows)
    entry_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)
    write_csv(entry_path, rows, FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_markdown_report(md_path, rows, package_csv, validation_csv, entry_path, summary_path, html_path)
    write_html_report(html_path, rows, entry_path)
    print(
        f"focused_html_cards={len(rows)} "
        f"pending_r31={summary['r31_validation_status'].get(PENDING_STATUS, 0)} "
        f"p0={summary['priority_level'].get('P0', 0)} "
        f"p1={summary['priority_level'].get('P1', 0)}"
    )
    print(f"csv={entry_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    print(f"html={html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
