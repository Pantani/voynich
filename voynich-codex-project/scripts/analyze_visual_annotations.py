#!/usr/bin/env python3
"""Summarize visual annotations against ar/al/or/ol suffixes."""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = ("ar", "al", "or", "ol")


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows: {malformed[:10]}")
    return rows


def matrix(rows: Iterable[dict[str, str]], key: str) -> dict[str, Counter[str]]:
    out: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        value = row.get(key, "") or "(blank)"
        out[value][row["suffix"]] += 1
    return dict(out)


def summary_rows(table: dict[str, Counter[str]], dimension: str) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for key in sorted(table):
        counts = table[key]
        total = sum(counts.values())
        row = {"dimension": dimension, "value": key, "total": str(total)}
        for suffix in SUFFIXES:
            row[suffix] = str(counts[suffix])
            row[f"{suffix}_share"] = f"{counts[suffix] / total:.4f}" if total else "0.0000"
        output.append(row)
    return output


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = ["dimension", "value", "total"]
    for suffix in SUFFIXES:
        fieldnames.extend([suffix, f"{suffix}_share"])
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_matrix(title: str, table: dict[str, Counter[str]]) -> list[str]:
    lines = [f"### {title}", "", "|item|ar|al|or|ol|total|", "|---|---:|---:|---:|---:|---:|"]
    for key in sorted(table):
        counts = table[key]
        total = sum(counts.values())
        lines.append(
            f"|{key}|{counts['ar']}|{counts['al']}|{counts['or']}|{counts['ol']}|{total}|"
        )
    lines.append("")
    return lines


def write_markdown(path: Path, source: Path, rows: list[dict[str, str]]) -> None:
    by_zone = matrix(rows, "visual_zone")
    by_object = matrix(rows, "object_nearby")
    by_confidence = Counter(row["annotation_confidence"] for row in rows)
    by_folio = Counter(row["folio"] for row in rows)
    by_suffix = Counter(row["suffix"] for row in rows)

    lines = [
        "# Rota 3: cruzamento visual",
        "",
        "Este relatorio cruza a semente de anotacao visual com a matriz `ar/al/or/ol`. A amostra ainda e pequena; use como diagnostico de pipeline, nao como decifracao.",
        "",
        f"Fonte: `{source}`.",
        f"Anotacoes analisadas: {len(rows)}.",
        "",
        "## Distribuicoes",
        "",
        "|metrica|valor|",
        "|---|---|",
        f"|folios|{len(by_folio)}|",
        f"|confianca baixa|{by_confidence['low']}|",
        f"|confianca media|{by_confidence['medium']}|",
        "",
        "### Sufixos na semente",
        "",
        "|sufixo|n|",
        "|---|---:|",
    ]
    for suffix in SUFFIXES:
        lines.append(f"|{suffix}|{by_suffix[suffix]}|")
    lines.append("")
    lines.extend(render_matrix("Visual zone x sufixo", by_zone))
    lines.extend(render_matrix("Objeto proximo x sufixo", by_object))
    lines.extend(
        [
            "## Leitura provisoria",
            "",
            "- A semente confirma que o pipeline consegue cruzar texto, locus e imagem.",
            "- `label` ainda esta dominado por `ar` nesta amostra, em parte por causa do lote `f70v2`.",
            "- `circular text` esta mais balanceado entre `ar` e `ol`, mas a amostra ainda e pequena.",
            "- A proxima rodada deve reduzir baixa confianca isolando melhor a posicao exata dos tokens nas imagens.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", help="Visual annotation CSV")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "visual_annotation_summary_zl3b.csv"),
        help="Summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_3_cruzamento_visual.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = Path(args.input_csv)
    rows = read_rows(source)
    summary = []
    for dimension in ("visual_zone", "object_nearby", "annotation_confidence", "folio"):
        summary.extend(summary_rows(matrix(rows, dimension), dimension))
    write_csv(Path(args.csv), summary)
    write_markdown(Path(args.md), source, rows)
    print(f"annotations={len(rows)} summary_rows={len(summary)}")
    print(f"csv={args.csv}")
    print(f"md={args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
