#!/usr/bin/env python3
"""Analyze the two axes implied by ar/al/or/ol.

The working model treats ar/al/or/ol as a 2x2 matrix:

        r   l
    a  ar  al
    o  or  ol

This script tests the two axes separately:
- a/o axis: ar+al versus or+ol
- r/l axis: ar+or versus al+ol
"""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

from analyze_matrix_controls import chi_square_independence

ROOT = Path(__file__).resolve().parents[1]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def ao_axis(suffix: str) -> str:
    if suffix in {"ar", "al"}:
        return "a"
    if suffix in {"or", "ol"}:
        return "o"
    return "?"


def rl_axis(suffix: str) -> str:
    if suffix in {"ar", "or"}:
        return "r"
    if suffix in {"al", "ol"}:
        return "l"
    return "?"


def axis_table(rows: list[dict[str, str]], dimension: str, axis: str) -> dict[str, Counter[str]]:
    table: dict[str, Counter[str]] = defaultdict(Counter)
    axis_fn = ao_axis if axis == "ao" else rl_axis
    for row in rows:
        key = row.get(dimension, "") or "(blank)"
        table[key][axis_fn(row["suffix"])] += 1
    return dict(table)


def summary_rows(rows: list[dict[str, str]], dimensions: list[str]) -> list[dict[str, str]]:
    output: list[dict[str, str]] = []
    for dimension in dimensions:
        for axis in ("ao", "rl"):
            table = axis_table(rows, dimension, axis)
            result = chi_square_independence(table)
            for value in sorted(table):
                counts = table[value]
                total = sum(counts.values())
                if axis == "ao":
                    left, right = "a", "o"
                else:
                    left, right = "r", "l"
                output.append(
                    {
                        "dimension": dimension,
                        "axis": axis,
                        "value": value,
                        "total": str(total),
                        left: str(counts[left]),
                        right: str(counts[right]),
                        f"{left}_share": f"{counts[left] / total:.4f}" if total else "0.0000",
                        f"{right}_share": f"{counts[right] / total:.4f}" if total else "0.0000",
                        "chi_square_for_dimension_axis": f"{result.statistic:.6f}",
                        "degrees_of_freedom": str(result.degrees_of_freedom),
                        "cramers_v": f"{result.cramers_v:.6f}",
                    }
                )
    return output


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "dimension",
        "axis",
        "value",
        "total",
        "a",
        "o",
        "a_share",
        "o_share",
        "r",
        "l",
        "r_share",
        "l_share",
        "chi_square_for_dimension_axis",
        "degrees_of_freedom",
        "cramers_v",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_axis_table(title: str, table: dict[str, Counter[str]], labels: tuple[str, str]) -> list[str]:
    left, right = labels
    lines = [
        f"### {title}",
        "",
        f"|item|{left}|{right}|total|{left}_share|{right}_share|",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for key in sorted(table):
        counts = table[key]
        total = sum(counts.values())
        left_share = counts[left] / total if total else 0
        right_share = counts[right] / total if total else 0
        lines.append(
            f"|{key}|{counts[left]}|{counts[right]}|{total}|{left_share:.3f}|{right_share:.3f}|"
        )
    lines.append("")
    return lines


def result_line(rows: list[dict[str, str]], dimension: str, axis: str) -> str:
    table = axis_table(rows, dimension, axis)
    result = chi_square_independence(table)
    return f"chi2={result.statistic:.3f}, df={result.degrees_of_freedom}, Cramer's V={result.cramers_v:.4f}"


def write_markdown(
    path: Path,
    context_rows: list[dict[str, str]],
    visual_rows: list[dict[str, str]],
    context_source: Path,
    visual_source: Path,
) -> None:
    lines = [
        "# Rota 4: teste dos eixos da matriz",
        "",
        "Este relatorio separa `ar/al/or/ol` em dois eixos binarios. Ele mede associacao, nao significado.",
        "",
        f"Corpus textual: `{context_source}` ({len(context_rows)} candidatos).",
        f"Semente visual: `{visual_source}` ({len(visual_rows)} anotacoes).",
        "",
        "## Resultados no corpus textual",
        "",
        "|dimensao|eixo a/o|eixo r/l|",
        "|---|---|---|",
    ]
    for dimension in ("locus_kind", "prefix", "line_position"):
        lines.append(
            f"|{dimension}|{result_line(context_rows, dimension, 'ao')}|{result_line(context_rows, dimension, 'rl')}|"
        )
    lines.extend(
        [
            "",
            "## Resultados na semente visual",
            "",
            "|dimensao|eixo a/o|eixo r/l|",
            "|---|---|---|",
        ]
    )
    for dimension in ("visual_zone", "object_nearby", "annotation_confidence", "folio"):
        lines.append(
            f"|{dimension}|{result_line(visual_rows, dimension, 'ao')}|{result_line(visual_rows, dimension, 'rl')}|"
        )
    lines.append("")
    lines.extend(render_axis_table("Corpus: locus_kind x eixo a/o", axis_table(context_rows, "locus_kind", "ao"), ("a", "o")))
    lines.extend(render_axis_table("Corpus: locus_kind x eixo r/l", axis_table(context_rows, "locus_kind", "rl"), ("r", "l")))
    lines.extend(render_axis_table("Visual: visual_zone x eixo a/o", axis_table(visual_rows, "visual_zone", "ao"), ("a", "o")))
    lines.extend(render_axis_table("Visual: visual_zone x eixo r/l", axis_table(visual_rows, "visual_zone", "rl"), ("r", "l")))
    lines.extend(
        [
            "## Leitura provisoria",
            "",
            "- No corpus grande, prefixo deve ser o principal fator a observar: se o eixo muda por prefixo, parte da matriz e morfologica/template.",
            "- Locus e posicao de linha continuam importantes se seus eixos mantiverem efeito mesmo quando o prefixo for controlado.",
            "- Na semente visual, o resultado ainda e exploratorio: a amostra e pequena e enviesada para `f70v2`, `f67r1` e `f84r`.",
            "- O proximo passo deve testar os eixos em pares comparaveis dentro do mesmo folio/locus, nao entre paginas muito diferentes.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("context_csv", help="Contextual matrix CSV")
    parser.add_argument("visual_csv", help="Visual annotation CSV")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "matrix_axis_summary_zl3b.csv"),
        help="Axis summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_4_eixos_matriz.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    context_source = Path(args.context_csv)
    visual_source = Path(args.visual_csv)
    context_rows = read_rows(context_source)
    visual_rows = read_rows(visual_source)
    rows = []
    rows.extend(summary_rows(context_rows, ["locus_kind", "prefix", "line_position"]))
    rows.extend(summary_rows(visual_rows, ["visual_zone", "object_nearby", "annotation_confidence", "folio"]))
    write_csv(Path(args.csv), rows)
    write_markdown(Path(args.md), context_rows, visual_rows, context_source, visual_source)
    print(f"context_rows={len(context_rows)} visual_rows={len(visual_rows)} summary_rows={len(rows)}")
    print(f"csv={args.csv}")
    print(f"md={args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
