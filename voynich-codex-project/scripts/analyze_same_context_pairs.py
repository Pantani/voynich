#!/usr/bin/env python3
"""Find comparable ar/al/or/ol groups inside the same local context."""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MATRIX_SUFFIXES = ("ar", "al", "or", "ol")
VISUAL_LOCUS_KINDS = {"C", "R", "L", "rubrica"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def prefix_family(row: dict[str, str]) -> str:
    if row.get("target_status") == "standalone":
        return "standalone"
    return row.get("prefix") or "(blank)"


def axis_coverage(suffixes: set[str]) -> str:
    has_a = bool(suffixes & {"ar", "al"})
    has_o = bool(suffixes & {"or", "ol"})
    has_r = bool(suffixes & {"ar", "or"})
    has_l = bool(suffixes & {"al", "ol"})
    axes = []
    if has_a and has_o:
        axes.append("ao")
    if has_r and has_l:
        axes.append("rl")
    return "+".join(axes) if axes else "none"


def visual_lookup(rows: list[dict[str, str]]) -> dict[tuple[str, str, str], list[dict[str, str]]]:
    lookup: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (row.get("folio", ""), row.get("locus", ""), row.get("token", ""))
        lookup[key].append(row)
    return dict(lookup)


def join_values(values: set[str]) -> str:
    clean = sorted(value for value in values if value)
    return " | ".join(clean)


def status_counts(rows: list[dict[str, str]]) -> str:
    counts = Counter(row.get("target_status", "") or "(blank)" for row in rows)
    return "; ".join(f"{key}:{counts[key]}" for key in sorted(counts))


def priority_score(rows: list[dict[str, str]], suffixes: set[str], annotations: list[dict[str, str]]) -> int:
    statuses = Counter(row.get("target_status", "") for row in rows)
    confidences = Counter(row.get("annotation_confidence", "") for row in annotations)
    score = len(suffixes) * 10
    score += statuses["exact"] * 4
    score += statuses["standalone"] * 3
    score += len(annotations) * 4
    score += confidences["medium"] * 2
    if rows[0].get("locus_kind") in VISUAL_LOCUS_KINDS:
        score += 5
    if axis_coverage(suffixes) == "ao+rl":
        score += 4
    return score


def comparable_groups(
    rows: list[dict[str, str]],
    annotations_by_token: dict[tuple[str, str, str], list[dict[str, str]]],
    min_suffixes: int = 2,
) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        family = prefix_family(row)
        key = (
            row.get("folio", ""),
            row.get("locus", ""),
            row.get("locus_kind", ""),
            family,
        )
        grouped[key].append(row)

    output: list[dict[str, str]] = []
    for (folio, locus, locus_kind, family), group_rows in grouped.items():
        suffixes = {row.get("suffix", "") for row in group_rows if row.get("suffix") in MATRIX_SUFFIXES}
        if len(suffixes) < min_suffixes:
            continue

        suffix_counts = Counter(row["suffix"] for row in group_rows if row.get("suffix") in MATRIX_SUFFIXES)
        annotations: list[dict[str, str]] = []
        for row in group_rows:
            annotations.extend(annotations_by_token.get((folio, locus, row.get("token", "")), []))

        visual_zones = {row.get("visual_zone", "") for row in annotations}
        objects = {row.get("object_nearby", "") for row in annotations}
        confidences = {row.get("annotation_confidence", "") for row in annotations}
        tokens = {row.get("token", "") for row in group_rows}
        line_positions = {row.get("line_position", "") for row in group_rows}
        visual_contexts = {row.get("visual_context", "") for row in group_rows}

        output.append(
            {
                "priority_score": str(priority_score(group_rows, suffixes, annotations)),
                "folio": folio,
                "locus": locus,
                "locus_kind": locus_kind,
                "prefix_family": family,
                "distinct_suffixes": str(len(suffixes)),
                "suffixes_present": " ".join(sorted(suffixes)),
                "axis_coverage": axis_coverage(suffixes),
                "total_candidates": str(len(group_rows)),
                "ar": str(suffix_counts["ar"]),
                "al": str(suffix_counts["al"]),
                "or": str(suffix_counts["or"]),
                "ol": str(suffix_counts["ol"]),
                "tokens": " ".join(sorted(tokens)),
                "target_status_counts": status_counts(group_rows),
                "line_positions": " ".join(sorted(line_positions)),
                "visual_contexts": join_values(visual_contexts),
                "annotated_tokens": str(len(annotations)),
                "visual_zones": join_values(visual_zones),
                "object_nearby": join_values(objects),
                "annotation_confidence": join_values(confidences),
            }
        )

    output.sort(
        key=lambda row: (
            -int(row["priority_score"]),
            row["folio"],
            row["locus"],
            row["prefix_family"],
        )
    )
    return output


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "priority_score",
        "folio",
        "locus",
        "locus_kind",
        "prefix_family",
        "distinct_suffixes",
        "suffixes_present",
        "axis_coverage",
        "total_candidates",
        "ar",
        "al",
        "or",
        "ol",
        "tokens",
        "target_status_counts",
        "line_positions",
        "visual_contexts",
        "annotated_tokens",
        "visual_zones",
        "object_nearby",
        "annotation_confidence",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def count_by(rows: list[dict[str, str]], field: str) -> Counter[str]:
    return Counter(row.get(field, "") or "(blank)" for row in rows)


def render_counts(title: str, counts: Counter[str]) -> list[str]:
    lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"|{key}|{value}|")
    lines.append("")
    return lines


def write_markdown(
    path: Path,
    rows: list[dict[str, str]],
    context_source: Path,
    visual_source: Path,
    output_csv: Path,
) -> None:
    axis_counts = count_by(rows, "axis_coverage")
    family_counts = count_by(rows, "prefix_family")
    annotated_count = sum(1 for row in rows if int(row["annotated_tokens"]) > 0)
    lines = [
        "# Rota 5: pares comparaveis no mesmo contexto",
        "",
        "Esta rota reduz falso sinal comparando valores da matriz apenas dentro do mesmo folio, locus e familia de prefixo.",
        "",
        f"Corpus textual: `{context_source}`.",
        f"Semente visual: `{visual_source}`.",
        f"CSV gerado: `{output_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- grupos comparaveis encontrados: {len(rows)};",
        f"- grupos com anotacao visual direta: {annotated_count};",
        f"- eixo/cobertura mais comum: {axis_counts.most_common(1)[0][0] if axis_counts else 'none'}.",
        "",
    ]
    lines.extend(render_counts("Cobertura de eixo", axis_counts))
    lines.extend(render_counts("Familias de prefixo", family_counts))
    lines.extend(
        [
            "## Grupos com anotacao visual direta",
            "",
            "|score|folio|locus|kind|familia|sufixos|eixo|tokens|visual|objeto|",
            "|---:|---|---|---|---|---|---|---|---|---|",
        ]
    )
    annotated_rows = [row for row in rows if int(row["annotated_tokens"]) > 0]
    for row in annotated_rows[:30]:
        visual = row["visual_zones"] or row["visual_contexts"]
        lines.append(
            f"|{row['priority_score']}|{row['folio']}|{row['locus']}|{row['locus_kind']}|{row['prefix_family']}|{row['suffixes_present']}|{row['axis_coverage']}|{row['tokens']}|{visual}|{row['object_nearby']}|"
        )
    lines.extend(
        [
            "",
            "## Grupos prioritarios",
            "",
            "|score|folio|locus|kind|familia|sufixos|eixo|tokens|visual|",
            "|---:|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows[:40]:
        visual = row["visual_zones"] or row["visual_contexts"]
        lines.append(
            f"|{row['priority_score']}|{row['folio']}|{row['locus']}|{row['locus_kind']}|{row['prefix_family']}|{row['suffixes_present']}|{row['axis_coverage']}|{row['tokens']}|{visual}|"
        )
    lines.extend(
        [
            "",
            "## Leitura provisoria",
            "",
            "- Grupos `standalone` ajudam a separar valores da matriz de tokens com nucleo.",
            "- Grupos `ok`, `ot` e `qok` sao melhores candidatos para pares minimos porque preservam uma familia de prefixo.",
            "- `ao+rl` e o caso mais informativo: a comparacao cruza os dois eixos dentro do mesmo contexto.",
            "- Grupos sem anotacao visual continuam uteis textualmente, mas nao devem ser usados para inferir direcao, anel, setor ou objeto.",
            "- O proximo passo deve escolher poucos grupos de alta prioridade e conferir a posicao exata dos glifos na imagem.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("context_csv", help="Context CSV from build_matrix_context_table.py")
    parser.add_argument("visual_csv", help="Visual annotation CSV")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "same_context_matrix_pairs_zl3b.csv"),
        help="Comparable group CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_5_pares_comparaveis.md"),
        help="Markdown report output",
    )
    parser.add_argument(
        "--min-suffixes",
        type=int,
        default=2,
        help="Minimum distinct matrix suffixes in the same group",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    context_source = Path(args.context_csv)
    visual_source = Path(args.visual_csv)
    context_rows = read_csv(context_source)
    visual_rows = read_csv(visual_source)
    groups = comparable_groups(context_rows, visual_lookup(visual_rows), min_suffixes=args.min_suffixes)
    csv_path = Path(args.csv)
    md_path = Path(args.md)
    write_csv(csv_path, groups)
    write_markdown(md_path, groups, context_source, visual_source, csv_path)
    print(f"context_rows={len(context_rows)} visual_rows={len(visual_rows)} comparable_groups={len(groups)}")
    print(f"csv={csv_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
