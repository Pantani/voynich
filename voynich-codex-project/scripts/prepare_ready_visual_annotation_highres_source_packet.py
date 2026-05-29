#!/usr/bin/env python3
"""Prepare high-resolution Yale IIIF source packet for route 32 review."""
from __future__ import annotations

import argparse
import csv
import html
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "highres_source_download_not_visual_evidence"
YALE_MANIFEST_URL = "https://collections.library.yale.edu/manifests/2002046"
YALE_CATALOG_URL = "https://collections.library.yale.edu/catalog/2002046"

FIELDNAMES = [
    "route42_id",
    "route32_id",
    "route28_id",
    "folio",
    "priority_level",
    "locus_kind",
    "token_counts",
    "top_loci",
    "current_image_url",
    "current_commons_page",
    "manifest_label",
    "match_status",
    "yale_image_id",
    "yale_iiif_jpg_url",
    "yale_tiff_url",
    "yale_catalog_url",
    "yale_width",
    "yale_height",
    "local_image_path",
    "download_plan_status",
    "manual_annotation_status",
    "manual_visual_notes",
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


def folio_manifest_label_candidates(folio: str) -> list[str]:
    label = folio[1:] if folio.startswith("f") else folio
    candidates = [label]
    collapsed = re.sub(r"([rv])\d+$", r"\1", label)
    if collapsed != label:
        candidates.append(collapsed)
    return candidates


def metadata_value(canvas: dict, label: str) -> str:
    for item in canvas.get("metadata", []):
        if item.get("label", {}).get("en", [""])[0] == label:
            return item.get("value", {}).get("none", [""])[0]
    return ""


def full_size_original_url(canvas: dict) -> str:
    for item in canvas.get("rendering", []):
        if item.get("label", {}).get("en", [""])[0] == "Full size original":
            return item.get("id", "")
    return ""


def build_manifest_index(manifest: dict) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for canvas in manifest.get("items", []):
        label = canvas.get("label", {}).get("none", [""])[0]
        body = canvas.get("items", [{}])[0].get("items", [{}])[0].get("body", {})
        image_id = metadata_value(canvas, "Image ID")
        index[label] = {
            "image_id": image_id,
            "image_label": metadata_value(canvas, "Image Label") or label,
            "iiif_jpg_url": body.get("id", ""),
            "tiff_url": full_size_original_url(canvas),
            "catalog_url": metadata_value(canvas, "Link to this Image"),
            "width": str(body.get("width", "")),
            "height": str(body.get("height", "")),
        }
    return index


def find_manifest_match(folio: str, manifest_index: dict[str, dict[str, str]]) -> tuple[str, str]:
    candidates = folio_manifest_label_candidates(folio)
    for candidate in candidates:
        if candidate in manifest_index:
            status = "matched_exact_manifest_label" if candidate == candidates[0] else "matched_collapsed_folio"
            return candidate, status
    collapsed = candidates[-1]
    for label in manifest_index:
        parts = re.split(r"\s+and\s+|[,;/]+", label)
        if collapsed in [part.strip() for part in parts]:
            return label, "matched_composite_manifest_label"
    return "", "missing_yale_manifest_match"


def build_highres_source_rows(
    entry_rows: list[dict[str, str]],
    manifest_index: dict[str, dict[str, str]],
    local_image_dir: str,
) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for entry in entry_rows:
        manifest_label, match_status = find_manifest_match(entry.get("folio", ""), manifest_index)
        manifest = manifest_index.get(manifest_label, {})
        image_id = manifest.get("image_id", "")
        local_path = ""
        download_status = "source_not_found"
        if image_id:
            local_path = f"{local_image_dir.rstrip('/')}/{entry.get('folio', '')}_{image_id}.jpg"
            download_status = "downloaded" if (ROOT / local_path).exists() else "download_pending"
        rows.append(
            {
                "route42_id": f"R42-{len(rows) + 1:03d}",
                "route32_id": entry.get("route32_id", ""),
                "route28_id": entry.get("route28_id", ""),
                "folio": entry.get("folio", ""),
                "priority_level": entry.get("priority_level", ""),
                "locus_kind": entry.get("locus_kind", ""),
                "token_counts": entry.get("token_counts", ""),
                "top_loci": entry.get("top_loci", ""),
                "current_image_url": entry.get("image_url", ""),
                "current_commons_page": entry.get("commons_page", ""),
                "manifest_label": manifest_label,
                "match_status": match_status,
                "yale_image_id": image_id,
                "yale_iiif_jpg_url": manifest.get("iiif_jpg_url", ""),
                "yale_tiff_url": manifest.get("tiff_url", ""),
                "yale_catalog_url": manifest.get("catalog_url", ""),
                "yale_width": manifest.get("width", ""),
                "yale_height": manifest.get("height", ""),
                "local_image_path": local_path,
                "download_plan_status": download_status,
                "manual_annotation_status": entry.get("manual_annotation_status", ""),
                "manual_visual_notes": entry.get("manual_visual_notes", ""),
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def summarize_highres_source_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "match_status": Counter(row.get("match_status", "") for row in rows),
        "download_plan_status": Counter(row.get("download_plan_status", "") for row in rows),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "locus_kind": Counter(row.get("locus_kind", "") for row in rows),
        "manifest_label": Counter(row.get("manifest_label", "") for row in rows),
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


def write_markdown_report(
    path: Path,
    rows: list[dict[str, str]],
    entry_csv: Path,
    manifest_json: Path,
    source_csv: Path,
    summary_csv: Path,
    html_path: Path,
) -> None:
    summary = summarize_highres_source_rows(rows)
    lines = [
        "# Rota 42: fontes IIIF de alta resolucao para R32",
        "",
        "Esta rota troca o apoio visual da R32 para fontes oficiais Yale/Beinecke em IIIF. Ela nao preenche anotacoes manuais e nao cria evidencia semantica.",
        "",
        f"Planilha R32: `{entry_csv}`.",
        f"Manifesto Yale IIIF usado: `{manifest_json}`.",
        f"Fonte oficial: `{YALE_MANIFEST_URL}`.",
        f"Pagina catalogo: `{YALE_CATALOG_URL}`.",
        f"CSV R42: `{source_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        f"HTML high-res: `{html_path}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens avaliados: {len(rows)};",
        f"- matches exatos: {summary['match_status'].get('matched_exact_manifest_label', 0)};",
        f"- matches por folio colapsado: {summary['match_status'].get('matched_collapsed_folio', 0)};",
        f"- matches por pagina composta: {summary['match_status'].get('matched_composite_manifest_label', 0)};",
        f"- sem match: {summary['match_status'].get('missing_yale_manifest_match', 0)};",
        "- guarda: `highres_source_download_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Status de match", summary["match_status"]))
    lines.extend(render_counts("Status de download planejado", summary["download_plan_status"]))
    lines.extend(render_counts("Labels Yale", summary["manifest_label"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota42|rota32|folio|label Yale|imagem Yale|dimensoes|local|",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        dimensions = f"{row['yale_width']}x{row['yale_height']}" if row["yale_width"] and row["yale_height"] else ""
        lines.append(
            f"|{row['route42_id']}|{row['route32_id']}|{row['folio']}|{markdown_cell(row['manifest_label'])}|{row['yale_image_id']}|{dimensions}|`{row['local_image_path']}`|"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def image_src(row: dict[str, str]) -> str:
    local = row.get("local_image_path", "")
    if local:
        return html.escape("../" + local)
    return html.escape(row.get("yale_iiif_jpg_url", ""))


def write_html(path: Path, rows: list[dict[str, str]]) -> None:
    cards = []
    for row in rows:
        title = f"{row['route32_id']} / {row['folio']} / Yale {row['manifest_label']}"
        dimensions = f"{row['yale_width']}x{row['yale_height']}" if row["yale_width"] and row["yale_height"] else ""
        cards.append(
            f"""<article class=\"review-card\" id=\"{html.escape(row['route32_id'])}\">
  <header>
    <h2>{html.escape(title)}</h2>
    <p><strong>Match:</strong> <code>{html.escape(row['match_status'])}</code> <strong>Dimensoes:</strong> <code>{html.escape(dimensions)}</code></p>
  </header>
  <div class=\"media\"><img src=\"{image_src(row)}\" alt=\"Fonte Yale IIIF para {html.escape(row['route32_id'])} / {html.escape(row['folio'])}\"></div>
  <dl>
    <dt>Tokens</dt><dd><code>{html.escape(row['token_counts'])}</code></dd>
    <dt>Loci</dt><dd><code>{html.escape(row['top_loci'])}</code></dd>
    <dt>Imagem Yale</dt><dd><a href=\"{html.escape(row['yale_iiif_jpg_url'])}\">JPEG IIIF</a> / <a href=\"{html.escape(row['yale_tiff_url'])}\">TIFF original</a> / <a href=\"{html.escape(row['yale_catalog_url'])}\">Catalogo</a></dd>
    <dt>Imagem anterior</dt><dd><a href=\"{html.escape(row['current_image_url'])}\">Commons JPEG</a> / <a href=\"{html.escape(row['current_commons_page'])}\">pagina Commons</a></dd>
    <dt>Campos R32</dt><dd><code>manual_annotation_status manual_visual_notes</code></dd>
    <dt>Guarda</dt><dd><code>{GUARDRAIL}</code></dd>
  </dl>
</article>"""
        )
    doc = f"""<!doctype html>
<html lang=\"pt-BR\">
<head>
  <meta charset=\"utf-8\">
  <title>Rota 42 - R32 com fontes Yale IIIF high-res</title>
  <style>
    body {{ margin: 24px; font-family: -apple-system, BlinkMacSystemFont, \"Segoe UI\", sans-serif; color: #1f2933; background: #f6f3ed; }}
    .review-card {{ margin: 24px 0; padding: 16px; border: 1px solid #c7bda9; border-radius: 6px; background: #fffdfa; }}
    img {{ width: 100%; max-height: 92vh; object-fit: contain; background: #ebe3d5; border: 1px solid #d4c6af; }}
    dl {{ display: grid; grid-template-columns: max-content 1fr; gap: 6px 12px; }}
    dt {{ font-weight: 700; }}
    code {{ white-space: pre-wrap; }}
  </style>
</head>
<body>
  <h1>Rota 42 - R32 com fontes Yale IIIF high-res</h1>
  <p>Use este HTML apenas para revisao visual humana. Ele nao grava decisoes e nao substitui o preenchimento manual da R32.</p>
  {''.join(cards)}
</body>
</html>
"""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(doc, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entry_csv", help="Route 32 focused manual entry CSV")
    parser.add_argument("manifest_json", help="Yale IIIF manifest JSON")
    parser.add_argument(
        "--local-image-dir",
        default="images/raw/yale_iiif_r32",
        help="Local image directory, relative to project root",
    )
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_highres_sources_zl3b.csv"),
        help="Route 42 high-res source CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_highres_sources_summary_zl3b.csv"),
        help="Route 42 summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_42_fontes_yale_iiif_highres_r32.md"),
        help="Route 42 Markdown report output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_42_pacote_html_yale_iiif_highres_r32.html"),
        help="Route 42 high-res HTML output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    entry_csv = Path(args.entry_csv)
    manifest_json = Path(args.manifest_json)
    manifest = json.loads(manifest_json.read_text(encoding="utf-8"))
    rows = build_highres_source_rows(read_csv(entry_csv), build_manifest_index(manifest), args.local_image_dir)
    summary = summarize_highres_source_rows(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    html_path = Path(args.html)
    write_csv(csv_path, rows, FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_markdown_report(md_path, rows, entry_csv, manifest_json, csv_path, summary_path, html_path)
    write_html(html_path, rows)
    print(
        f"highres_items={len(rows)} "
        f"matched={len(rows) - summary['match_status'].get('missing_yale_manifest_match', 0)} "
        f"missing={summary['match_status'].get('missing_yale_manifest_match', 0)}"
    )
    print(f"csv={csv_path.resolve()}")
    print(f"summary_csv={summary_path.resolve()}")
    print(f"md={md_path.resolve()}")
    print(f"html={html_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
