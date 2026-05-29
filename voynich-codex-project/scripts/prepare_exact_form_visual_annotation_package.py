#!/usr/bin/env python3
"""Prepare a P0/P1 visual annotation package from exact ok/ot gap queue rows."""
from __future__ import annotations

import argparse
import csv
import html
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "visual_annotation_package_not_evidence"
FIELDS_TO_FILL = "manual_annotation_status manual_source_image_url manual_visual_notes"

FIELDNAMES = [
    "route28_id",
    "route27_id",
    "folio",
    "locus_kind",
    "priority_level",
    "gap_rows",
    "unique_loci",
    "token_counts",
    "prefix_counts",
    "suffix_counts",
    "line_position_counts",
    "top_loci",
    "section_notes",
    "image_source_status",
    "image_manifest_folio",
    "image_url",
    "commons_page",
    "workstream",
    "package_status",
    "fields_to_fill",
    "manual_annotation_status",
    "manual_source_image_url",
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


def package_status(image_source_status: str) -> tuple[str, str, str]:
    if image_source_status == "manifest_available":
        return (
            "annotate_from_manifest_image",
            "ready_for_manual_visual_annotation",
            "open_manifest_image_and_record_manual_visual_annotation",
        )
    return (
        "source_image_required",
        "blocked_pending_source_image",
        "locate_or_download_source_image_before_annotation",
    )


def build_annotation_package_rows(queue_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected = [row for row in queue_rows if row.get("priority_level") in {"P0", "P1"}]
    package_rows: list[dict[str, str]] = []
    for row in selected:
        workstream, status, output_rule = package_status(row.get("image_source_status", ""))
        package_rows.append(
            {
                "route28_id": f"R28-{len(package_rows) + 1:03d}",
                "route27_id": row.get("route27_id", ""),
                "folio": row.get("folio", ""),
                "locus_kind": row.get("locus_kind", ""),
                "priority_level": row.get("priority_level", ""),
                "gap_rows": row.get("gap_rows", ""),
                "unique_loci": row.get("unique_loci", ""),
                "token_counts": row.get("token_counts", ""),
                "prefix_counts": row.get("prefix_counts", ""),
                "suffix_counts": row.get("suffix_counts", ""),
                "line_position_counts": row.get("line_position_counts", ""),
                "top_loci": row.get("top_loci", ""),
                "section_notes": row.get("section_notes", ""),
                "image_source_status": row.get("image_source_status", ""),
                "image_manifest_folio": row.get("image_manifest_folio", ""),
                "image_url": row.get("image_url", ""),
                "commons_page": row.get("commons_page", ""),
                "workstream": workstream,
                "package_status": status,
                "fields_to_fill": FIELDS_TO_FILL,
                "manual_annotation_status": "",
                "manual_source_image_url": "",
                "manual_visual_notes": "",
                "output_rule": output_rule,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return package_rows


def summarize_annotation_package_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "image_source_status": Counter(row.get("image_source_status", "") for row in rows),
        "workstream": Counter(row.get("workstream", "") for row in rows),
        "package_status": Counter(row.get("package_status", "") for row in rows),
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


def render_html_card(row: dict[str, str]) -> str:
    title = html.escape(f"{row.get('route28_id', '')} / {row.get('route27_id', '')} / {row.get('folio', '')}")
    tokens = html.escape(row.get("token_counts", ""))
    loci = html.escape(row.get("top_loci", ""))
    notes = html.escape(row.get("section_notes", ""))
    status = html.escape(row.get("package_status", ""))
    guardrail = html.escape(row.get("semantic_guardrail", ""))
    fields = html.escape(row.get("fields_to_fill", FIELDS_TO_FILL))
    image_url = row.get("image_url", "")
    if image_url:
        media = f'<img src="{html.escape(image_url)}" alt="Imagem fonte para {title}">'
    else:
        media = '<p class="source-needed">Imagem ainda nao esta no manifesto. Registrar ou baixar a fonte antes da anotacao visual.</p>'
    commons_page = row.get("commons_page", "")
    commons_link = (
        f'<p><a href="{html.escape(commons_page)}">Pagina Commons</a></p>'
        if commons_page
        else ""
    )
    return f"""
    <article class="review-card" id="{html.escape(row.get('route28_id', ''))}">
      <header>
        <h2>{title}</h2>
        <p><strong>Prioridade:</strong> <code>{html.escape(row.get('priority_level', ''))}</code> <strong>Status:</strong> <code>{status}</code></p>
      </header>
      <div class="media">{media}{commons_link}</div>
      <dl>
        <dt>Tokens</dt><dd><code>{tokens}</code></dd>
        <dt>Loci</dt><dd><code>{loci}</code></dd>
        <dt>Notas</dt><dd><code>{notes}</code></dd>
        <dt>Campos manuais</dt><dd><code>{fields}</code></dd>
        <dt>Guarda</dt><dd><code>{guardrail}</code></dd>
      </dl>
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
    summary = summarize_annotation_package_rows(rows)
    lines = [
        "# Rota 28: pacote de anotacao visual das formas exatas P0/P1",
        "",
        "Esta rota transforma a fila P0/P1 da Rota 27 em um pacote de anotacao. Ela separa itens com imagem pronta dos itens que exigem fonte de imagem e nao preenche evidencia visual por inferencia.",
        "",
        f"Fonte R27: `{source_csv}`.",
        f"Pacote CSV: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        f"Pacote HTML: `{html_path}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens no pacote: {len(rows)};",
        f"- P0: {summary['priority_level'].get('P0', 0)};",
        f"- P1: {summary['priority_level'].get('P1', 0)};",
        f"- prontos para anotacao manual: {summary['package_status'].get('ready_for_manual_visual_annotation', 0)};",
        f"- bloqueados por falta de imagem: {summary['package_status'].get('blocked_pending_source_image', 0)};",
        "- campos manuais permanecem em branco;",
        "- guarda: `visual_annotation_package_not_evidence`.",
        "",
    ]
    lines.extend(render_counts("Prioridade", summary["priority_level"]))
    lines.extend(render_counts("Status do pacote", summary["package_status"]))
    lines.extend(render_counts("Fluxo de trabalho", summary["workstream"]))
    lines.extend(render_counts("Tipo de locus", summary["locus_kind"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota28|rota27|prioridade|folio|locus|lacunas|tokens|status|",
            "|---|---|---|---|---|---:|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{markdown_cell(row['route28_id'])}|{markdown_cell(row['route27_id'])}|{markdown_cell(row['priority_level'])}|{markdown_cell(row['folio'])}|{markdown_cell(row['locus_kind'])}|{markdown_cell(row['gap_rows'])}|{markdown_cell(row['token_counts'])}|{markdown_cell(row['package_status'])}|"
        )
    lines.extend(
        [
            "",
            "## Leitura",
            "",
            "O pacote define trabalho revisavel. Itens bloqueados precisam primeiro de imagem fonte; itens prontos ainda dependem de anotacao manual explicita.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def write_html_report(path: Path, rows: list[dict[str, str]]) -> None:
    cards = "\n".join(render_html_card(row) for row in rows)
    document = f"""<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <title>Rota 28 - pacote de anotacao visual P0/P1</title>
  <style>
    body {{
      margin: 24px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #1f2933;
      background: #f7f5f0;
    }}
    .review-card {{
      margin: 24px 0;
      padding: 16px;
      border: 1px solid #c8c0b3;
      border-radius: 6px;
      background: #fffdf8;
    }}
    img {{
      width: 100%;
      max-height: 720px;
      object-fit: contain;
      background: #ece6dc;
      border: 1px solid #d5cbbb;
    }}
    .source-needed {{
      padding: 16px;
      border: 1px dashed #9a7b4f;
      background: #fff8e6;
    }}
    dl {{
      display: grid;
      grid-template-columns: max-content 1fr;
      gap: 6px 12px;
    }}
    dt {{ font-weight: 700; }}
    code {{ white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h1>Rota 28 - pacote de anotacao visual P0/P1</h1>
  <p>Preencher somente por revisao visual humana. Prioridade e disponibilidade de imagem sao sinais operacionais, nao evidencia.</p>
  {cards}
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gap_queue_csv", help="CSV generated by prepare_exact_form_visual_gap_queue.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "annotations" / "exact_form_visual_annotation_package_p0_p1_zl3b.csv"),
        help="Annotation package CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "exact_form_visual_annotation_package_summary_zl3b.csv"),
        help="Annotation package summary output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_28_pacote_anotacao_visual_formas_exatas.md"),
        help="Markdown report output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_28_pacote_anotacao_visual_formas_exatas.html"),
        help="HTML report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_csv = Path(args.gap_queue_csv)
    rows = build_annotation_package_rows(read_csv(source_csv))
    summary = summarize_annotation_package_rows(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)
    write_csv(csv_path, rows, FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_markdown_report(md_path, rows, source_csv, csv_path, summary_path, html_path)
    write_html_report(html_path, rows)
    print(
        f"package_items={len(rows)} "
        f"ready={summary['package_status'].get('ready_for_manual_visual_annotation', 0)} "
        f"blocked={summary['package_status'].get('blocked_pending_source_image', 0)}"
    )
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    print(f"html={html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
