#!/usr/bin/env python3
"""Prepare a missing source-image queue for blocked route 28 annotation items."""
from __future__ import annotations

import argparse
import csv
import html
from collections import Counter
from pathlib import Path
from urllib.parse import quote_plus

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "missing_source_queue_not_visual_evidence"
SOURCE_RESOLUTION_STATUS = "pending_public_source_verification"
MANIFEST_ACTION = "do_not_update_manifest_until_url_verified"
FIELDS_TO_FILL = "candidate_commons_page candidate_image_url source_notes"

FIELDNAMES = [
    "route29_id",
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
    "source_resolution_status",
    "search_query",
    "commons_search_url",
    "candidate_commons_page",
    "candidate_image_url",
    "source_notes",
    "fields_to_fill",
    "manifest_action",
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


def commons_search_url(query: str) -> str:
    encoded = quote_plus(query)
    return f"https://commons.wikimedia.org/w/index.php?search={encoded}&title=Special:MediaSearch&type=image"


def build_missing_source_rows(package_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    blocked = [row for row in package_rows if row.get("package_status") == "blocked_pending_source_image"]
    rows: list[dict[str, str]] = []
    for row in blocked:
        folio = row.get("folio", "")
        query = f"Voynich Manuscript {folio}".strip()
        rows.append(
            {
                "route29_id": f"R29-{len(rows) + 1:03d}",
                "route28_id": row.get("route28_id", ""),
                "route27_id": row.get("route27_id", ""),
                "folio": folio,
                "locus_kind": row.get("locus_kind", ""),
                "priority_level": row.get("priority_level", ""),
                "gap_rows": row.get("gap_rows", ""),
                "unique_loci": row.get("unique_loci", ""),
                "token_counts": row.get("token_counts", ""),
                "top_loci": row.get("top_loci", ""),
                "section_notes": row.get("section_notes", ""),
                "source_resolution_status": SOURCE_RESOLUTION_STATUS,
                "search_query": query,
                "commons_search_url": commons_search_url(query),
                "candidate_commons_page": "",
                "candidate_image_url": "",
                "source_notes": "",
                "fields_to_fill": FIELDS_TO_FILL,
                "manifest_action": MANIFEST_ACTION,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def summarize_missing_source_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "source_resolution_status": Counter(row.get("source_resolution_status", "") for row in rows),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "locus_kind": Counter(row.get("locus_kind", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
        "manifest_action": Counter(row.get("manifest_action", "") for row in rows),
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
    title = html.escape(f"{row.get('route29_id', '')} / {row.get('route28_id', '')} / {row.get('folio', '')}")
    search_query = html.escape(row.get("search_query", ""))
    search_url = html.escape(row.get("commons_search_url", ""))
    fields = html.escape(row.get("fields_to_fill", FIELDS_TO_FILL))
    guardrail = html.escape(row.get("semantic_guardrail", ""))
    tokens = html.escape(row.get("token_counts", ""))
    loci = html.escape(row.get("top_loci", ""))
    return f"""
    <article class="source-card" id="{html.escape(row.get('route29_id', ''))}">
      <header>
        <h2>{title}</h2>
        <p><strong>Status:</strong> <code>{html.escape(row.get('source_resolution_status', ''))}</code></p>
      </header>
      <p><strong>Busca sugerida:</strong> <code>{search_query}</code></p>
      <p><a href="{search_url}">Abrir busca no Commons</a></p>
      <dl>
        <dt>candidate_commons_page</dt><dd><code></code></dd>
        <dt>candidate_image_url</dt><dd><code></code></dd>
        <dt>source_notes</dt><dd><code></code></dd>
        <dt>Campos</dt><dd><code>{fields}</code></dd>
        <dt>Tokens</dt><dd><code>{tokens}</code></dd>
        <dt>Loci</dt><dd><code>{loci}</code></dd>
        <dt>Guarda</dt><dd><code>{guardrail}</code></dd>
      </dl>
    </article>
    """.strip()


def write_markdown_report(
    path: Path,
    rows: list[dict[str, str]],
    package_csv: Path,
    output_csv: Path,
    summary_csv: Path,
    html_path: Path,
) -> None:
    summary = summarize_missing_source_rows(rows)
    lines = [
        "# Rota 29: fila de fontes de imagem ausentes",
        "",
        "Esta rota transforma os itens bloqueados da Rota 28 em uma fila de busca de fonte publica. Ela nao adiciona URLs candidatas por inferencia e nao cria evidencia visual.",
        "",
        f"Fonte R28: `{package_csv}`.",
        f"Fila CSV: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        f"Pacote HTML: `{html_path}`.",
        "",
        "## Resultado curto",
        "",
        f"- fontes pendentes: {len(rows)};",
        f"- status: `{SOURCE_RESOLUTION_STATUS}`;",
        f"- acao de manifesto: `{MANIFEST_ACTION}`;",
        "- campos candidatos permanecem em branco;",
        "- guarda: `missing_source_queue_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Prioridade", summary["priority_level"]))
    lines.extend(render_counts("Tipo de locus", summary["locus_kind"]))
    lines.extend(render_counts("Folios", summary["folio"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota29|rota28|prioridade|folio|locus|lacunas|consulta|campos|",
            "|---|---|---|---|---|---:|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{markdown_cell(row['route29_id'])}|{markdown_cell(row['route28_id'])}|{markdown_cell(row['priority_level'])}|{markdown_cell(row['folio'])}|{markdown_cell(row['locus_kind'])}|{markdown_cell(row['gap_rows'])}|{markdown_cell(row['search_query'])}|{markdown_cell(row['fields_to_fill'])}|"
        )
    lines.extend(
        [
            "",
            "## Leitura",
            "",
            "A fila separa busca de fonte de anotacao visual. O manifesto so deve ser atualizado depois que `candidate_commons_page` e `candidate_image_url` forem verificados manualmente como fonte publica adequada.",
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
  <title>Rota 29 - fontes de imagem ausentes</title>
  <style>
    body {{
      margin: 24px;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      color: #1f2933;
      background: #f7f5f0;
    }}
    .source-card {{
      margin: 24px 0;
      padding: 16px;
      border: 1px solid #c8c0b3;
      border-radius: 6px;
      background: #fffdf8;
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
  <h1>Rota 29 - fontes de imagem ausentes</h1>
  <p>Preencher somente depois de verificar fonte publica adequada. Busca e fila nao sao evidencia visual.</p>
  {cards}
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(document, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("annotation_package_csv", help="CSV generated by prepare_exact_form_visual_annotation_package.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "annotations" / "exact_form_missing_source_queue_p0_p1_zl3b.csv"),
        help="Missing source queue CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "exact_form_missing_source_summary_zl3b.csv"),
        help="Missing source queue summary output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_29_fila_fontes_imagem_formas_exatas.md"),
        help="Markdown report output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_29_fila_fontes_imagem_formas_exatas.html"),
        help="HTML report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    package_csv = Path(args.annotation_package_csv)
    rows = build_missing_source_rows(read_csv(package_csv))
    summary = summarize_missing_source_rows(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)
    write_csv(csv_path, rows, FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_markdown_report(md_path, rows, package_csv, csv_path, summary_path, html_path)
    write_html_report(html_path, rows)
    print(
        f"missing_sources={len(rows)} "
        f"pending={summary['source_resolution_status'].get(SOURCE_RESOLUTION_STATUS, 0)}"
    )
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    print(f"html={html_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
