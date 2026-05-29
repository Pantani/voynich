#!/usr/bin/env python3
"""Prepare manual SVG review sheets for route 9."""
from __future__ import annotations

import argparse
import csv
import html
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def family_priority(family: str) -> int:
    order = {
        "ot": 0,
        "ok": 1,
        "qok": 2,
        "ch": 3,
        "d": 3,
        "sh": 4,
        "standalone": 9,
    }
    return order.get(family, 8)


def manual_review_template(row: dict[str, str], index: int) -> dict[str, str]:
    return {
        "manual_review_id": f"R9-{index:03d}",
        "decision_id": row.get("decision_id", ""),
        "crop_id": row.get("crop_id", ""),
        "source_review_id": row.get("source_review_id", ""),
        "folio": row.get("folio", ""),
        "locus": row.get("locus", ""),
        "prefix_family": row.get("prefix_family", ""),
        "axis_coverage": row.get("axis_coverage", ""),
        "group_tokens": row.get("group_tokens", ""),
        "matched_annotation_tokens": row.get("matched_annotation_tokens", ""),
        "missing_group_tokens": row.get("missing_group_tokens", ""),
        "review_region": row.get("review_region", ""),
        "crop_svg": row.get("crop_svg", ""),
        "previous_review_decision": row.get("review_decision", ""),
        "manual_tighter_x": "",
        "manual_tighter_y": "",
        "manual_tighter_width": "",
        "manual_tighter_height": "",
        "manual_target_tokens_seen": "",
        "manual_missing_tokens_seen": "",
        "manual_final_status": "pending_manual_review",
        "manual_notes": "",
    }


def build_manual_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    sorted_rows = sorted(
        rows,
        key=lambda row: (
            family_priority(row.get("prefix_family", "")),
            0 if row.get("missing_group_tokens") else 1,
            row.get("folio", ""),
            row.get("locus", ""),
            row.get("crop_id", ""),
        ),
    )
    return [manual_review_template(row, index) for index, row in enumerate(sorted_rows, start=1)]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "manual_review_id",
        "decision_id",
        "crop_id",
        "source_review_id",
        "folio",
        "locus",
        "prefix_family",
        "axis_coverage",
        "group_tokens",
        "matched_annotation_tokens",
        "missing_group_tokens",
        "review_region",
        "crop_svg",
        "previous_review_decision",
        "manual_tighter_x",
        "manual_tighter_y",
        "manual_tighter_width",
        "manual_tighter_height",
        "manual_target_tokens_seen",
        "manual_missing_tokens_seen",
        "manual_final_status",
        "manual_notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def html_svg_src(crop_svg: str) -> str:
    return "../" + crop_svg


def render_html(rows: list[dict[str, str]]) -> str:
    cards = []
    for row in rows:
        title = f"{row['manual_review_id']} / {row['crop_id']} / {row['folio']} / {row['locus']}"
        cards.append(
            "\n".join(
                [
                    '<section class="review-card">',
                    f"<h2>{html.escape(title)}</h2>",
                    '<div class="meta">',
                    f"<span>familia: <strong>{html.escape(row['prefix_family'])}</strong></span>",
                    f"<span>eixo: <strong>{html.escape(row.get('axis_coverage', ''))}</strong></span>",
                    f"<span>tokens: <strong>{html.escape(row['group_tokens'])}</strong></span>",
                    f"<span>faltam: <strong>{html.escape(row['missing_group_tokens'] or '(none)')}</strong></span>",
                    f"<span>status: <strong>{html.escape(row['manual_final_status'])}</strong></span>",
                    "</div>",
                    f'<object class="crop" data="{html.escape(html_svg_src(row["crop_svg"]))}" type="image/svg+xml"></object>',
                    '<table class="fields">',
                    "<tr><th>campo</th><th>valor a preencher</th></tr>",
                    '<tr><td>manual_tighter_x</td><td></td></tr>',
                    '<tr><td>manual_tighter_y</td><td></td></tr>',
                    '<tr><td>manual_tighter_width</td><td></td></tr>',
                    '<tr><td>manual_tighter_height</td><td></td></tr>',
                    '<tr><td>manual_target_tokens_seen</td><td></td></tr>',
                    '<tr><td>manual_missing_tokens_seen</td><td></td></tr>',
                    '<tr><td>manual_final_status</td><td>confirmed_tighter_region | keep_not_isolated | unusable_crop</td></tr>',
                    '<tr><td>manual_notes</td><td></td></tr>',
                    "</table>",
                    "</section>",
                ]
            )
        )
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="pt-BR">',
            "<head>",
            '<meta charset="utf-8">',
            "<title>Rota 9 - Revisao manual assistida</title>",
            "<style>",
            "body{font-family:Arial,sans-serif;margin:24px;background:#f6f3ee;color:#1f1b16}",
            "h1{font-size:28px;margin:0 0 8px}",
            ".note{max-width:920px;line-height:1.45}",
            ".review-card{margin:24px 0;padding:16px;border:1px solid #b9aa96;background:#fff;border-radius:6px}",
            ".meta{display:flex;flex-wrap:wrap;gap:10px 18px;margin:10px 0 14px;font-size:14px}",
            ".crop{width:100%;height:720px;border:1px solid #8d806f;background:#eee}",
            ".fields{width:100%;border-collapse:collapse;margin-top:12px;font-size:14px}",
            ".fields th,.fields td{border:1px solid #d2c6b7;padding:8px;text-align:left}",
            ".fields th{background:#eee4d8}",
            "</style>",
            "</head>",
            "<body>",
            "<h1>Rota 9: revisao manual assistida dos SVGs</h1>",
            '<p class="note">Use esta folha para tentar coordenadas mais apertadas dentro dos recortes. Se a palavra exata nao puder ser localizada, mantenha <code>keep_not_isolated</code>. Nenhum campo em branco deve ser interpretado como confirmacao.</p>',
            "\n".join(cards),
            "</body>",
            "</html>",
            "",
        ]
    )


def write_html(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_html(rows), encoding="utf-8")


def render_counts(title: str, counts: Counter[str]) -> list[str]:
    lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"|{key}|{value}|")
    lines.append("")
    return lines


def write_report(path: Path, rows: list[dict[str, str]], source_csv: Path, output_csv: Path, output_html: Path) -> None:
    family_counts = Counter(row["prefix_family"] for row in rows)
    status_counts = Counter(row["manual_final_status"] for row in rows)
    lines = [
        "# Rota 9: revisao manual assistida",
        "",
        "Esta rota prepara uma folha de revisao para coordenadas mais apertadas. Ela nao confirma glifos automaticamente.",
        "",
        f"Fonte: `{source_csv}`.",
        f"CSV de trabalho: `{output_csv}`.",
        f"HTML de revisao: `{output_html}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens para revisar: {len(rows)};",
        "- campos de coordenada foram deixados vazios de proposito;",
        "- status inicial: `pending_manual_review` para todos os itens;",
        "- prioridade: `ot`, depois `ch/d`, depois `standalone`.",
        "",
    ]
    lines.extend(render_counts("Familias na fila", family_counts))
    lines.extend(render_counts("Status inicial", status_counts))
    lines.extend(
        [
            "## Ordem de revisao",
            "",
            "|manual|decisao|crop|familia|folio|locus|tokens|faltam|",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['manual_review_id']}|{row['decision_id']}|{row['crop_id']}|{row['prefix_family']}|{row['folio']}|{row['locus']}|{row['group_tokens']}|{row['missing_group_tokens']}|"
        )
    lines.extend(
        [
            "",
            "## Como preencher",
            "",
            "- Use `manual_tighter_x/y/width/height` apenas quando uma regiao menor for realmente visivel.",
            "- Use `manual_final_status=confirmed_tighter_region` somente para regiao melhorada, nao para significado.",
            "- Use `manual_final_status=keep_not_isolated` se a palavra exata nao puder ser isolada.",
            "- Nao transformar coordenada visual em traducao.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("decision_csv", help="CSV from review_crop_decisions.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "annotations" / "manual_svg_review_zl3b.csv"),
        help="Manual review CSV output",
    )
    parser.add_argument(
        "--html",
        default=str(ROOT / "docs" / "rota_9_revisao_manual.html"),
        help="Manual review HTML output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_9_revisao_manual.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = Path(args.decision_csv)
    rows = build_manual_rows(read_csv(source))
    csv_path = Path(args.csv)
    html_path = Path(args.html)
    md_path = Path(args.md)
    write_csv(csv_path, rows)
    write_html(html_path, rows)
    write_report(md_path, rows, source, csv_path, html_path)
    print(f"decision_rows={len(rows)} manual_review_rows={len(rows)}")
    print(f"csv={csv_path}")
    print(f"html={html_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
