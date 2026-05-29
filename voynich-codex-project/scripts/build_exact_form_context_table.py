#!/usr/bin/env python3
"""Build an expanded context table for exact ok/ot matrix forms."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXACT_FORMS = ("okar", "okal", "okor", "okol", "otar", "otal", "otor", "otol")
GUARDRAIL = "exact_form_context_not_decipherment"

FIELDNAMES = [
    "route26_id",
    "source",
    "folio",
    "locus",
    "section_note",
    "locus_kind",
    "locus_code",
    "visual_context",
    "token",
    "prefix",
    "suffix",
    "line_position",
    "token_index",
    "line_token_count",
    "previous_token",
    "next_token",
    "line_tokens",
    "image_file_or_url",
    "visual_zone",
    "ring",
    "sector",
    "radius",
    "object_nearby",
    "visual_notes",
    "annotation_confidence",
    "visual_match_status",
    "semantic_guardrail",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def visual_annotation_index(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], dict[str, str]]:
    return {
        (row.get("folio", ""), row.get("locus", ""), row.get("token", "")): row
        for row in rows
        if row.get("folio") and row.get("locus") and row.get("token")
    }


def build_exact_form_rows(
    context_rows: list[dict[str, str]],
    visual_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    visual_by_key = visual_annotation_index(visual_rows)
    rows: list[dict[str, str]] = []
    for context in context_rows:
        token = context.get("token", "")
        if token not in EXACT_FORMS:
            continue
        visual = visual_by_key.get((context.get("folio", ""), context.get("locus", ""), token), {})
        rows.append(
            {
                "route26_id": f"R26-{len(rows) + 1:04d}",
                "source": context.get("source", ""),
                "folio": context.get("folio", ""),
                "locus": context.get("locus", ""),
                "section_note": context.get("note", ""),
                "locus_kind": context.get("locus_kind", ""),
                "locus_code": context.get("locus_code", ""),
                "visual_context": context.get("visual_context", ""),
                "token": token,
                "prefix": context.get("prefix", ""),
                "suffix": context.get("suffix", ""),
                "line_position": context.get("line_position", ""),
                "token_index": context.get("token_index", ""),
                "line_token_count": context.get("line_token_count", ""),
                "previous_token": context.get("previous_token", ""),
                "next_token": context.get("next_token", ""),
                "line_tokens": context.get("line_tokens", ""),
                "image_file_or_url": visual.get("image_file_or_url", ""),
                "visual_zone": visual.get("visual_zone", ""),
                "ring": visual.get("ring", ""),
                "sector": visual.get("sector", ""),
                "radius": visual.get("radius", ""),
                "object_nearby": visual.get("object_nearby", ""),
                "visual_notes": visual.get("visual_notes", ""),
                "annotation_confidence": visual.get("annotation_confidence", ""),
                "visual_match_status": "matched_visual_annotation" if visual else "no_visual_annotation",
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def summarize_exact_form_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "token": Counter(row.get("token", "") for row in rows),
        "prefix": Counter(row.get("prefix", "") for row in rows),
        "suffix": Counter(row.get("suffix", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
        "locus_kind": Counter(row.get("locus_kind", "") for row in rows),
        "line_position": Counter(row.get("line_position", "") for row in rows),
        "visual_match_status": Counter(row.get("visual_match_status", "") for row in rows),
        "visual_zone": Counter(row.get("visual_zone", "") or "(blank)" for row in rows),
        "object_nearby": Counter(row.get("object_nearby", "") or "(blank)" for row in rows),
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


def write_report(
    path: Path,
    rows: list[dict[str, str]],
    context_csv: Path,
    visual_csv: Path,
    output_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_exact_form_rows(rows)
    lines = [
        "# Rota 26: tabela ampliada das formas exatas ok/ot",
        "",
        "Esta rota isola `okar/okal/okor/okol/otar/otal/otor/otol` e junta contexto textual com anotacao visual quando existe chave exata folio/locus/token.",
        "",
        f"Contexto textual: `{context_csv}`.",
        f"Anotacao visual: `{visual_csv}`.",
        f"Tabela ampliada: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- ocorrencias exatas: {len(rows)};",
        f"- `ok*`: {summary['prefix'].get('ok', 0)};",
        f"- `ot*`: {summary['prefix'].get('ot', 0)};",
        f"- com anotacao visual exata: {summary['visual_match_status'].get('matched_visual_annotation', 0)};",
        f"- sem anotacao visual exata: {summary['visual_match_status'].get('no_visual_annotation', 0)};",
        "- guarda: `exact_form_context_not_decipherment`.",
        "",
    ]
    lines.extend(render_counts("Formas", summary["token"]))
    lines.extend(render_counts("Prefixos", summary["prefix"]))
    lines.extend(render_counts("Sufixos", summary["suffix"]))
    lines.extend(render_counts("Locus", summary["locus_kind"]))
    lines.extend(render_counts("Posicao na linha", summary["line_position"]))
    lines.extend(render_counts("Match visual", summary["visual_match_status"]))
    lines.extend(
        [
            "## Primeiras ocorrencias",
            "",
            "|rota26|token|folio|locus|locus_kind|posicao|visual_zone|objeto proximo|match|",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows[:30]:
        lines.append(
            f"|{row['route26_id']}|{row['token']}|{row['folio']}|{row['locus']}|{row['locus_kind']}|{row['line_position']}|{row['visual_zone']}|{row['object_nearby']}|{row['visual_match_status']}|"
        )
    lines.extend(
        [
            "",
            "## Leitura",
            "",
            "A tabela melhora a rastreabilidade das oito formas exatas, mas nao atribui significado aos eixos `ok/ot` ou `ar/al/or/ol`. Linhas sem anotacao visual permanecem como lacuna, nao como evidencia negativa.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("context_csv", help="CSV from build_matrix_context_table.py")
    parser.add_argument("visual_annotations_csv", help="Visual annotation seed CSV")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "exact_form_context_table_zl3b.csv"),
        help="Exact form context table output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "exact_form_context_summary_zl3b.csv"),
        help="Exact form context summary output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_26_tabela_contexto_formas_exatas.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    context_csv = Path(args.context_csv)
    visual_csv = Path(args.visual_annotations_csv)
    rows = build_exact_form_rows(read_csv(context_csv), read_csv(visual_csv))
    summary = summarize_exact_form_rows(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, rows, FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_report(md_path, rows, context_csv, visual_csv, csv_path, summary_path)
    print(
        f"exact_form_rows={len(rows)} "
        f"ok={summary['prefix'].get('ok', 0)} "
        f"ot={summary['prefix'].get('ot', 0)} "
        f"visual_matched={summary['visual_match_status'].get('matched_visual_annotation', 0)}"
    )
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
