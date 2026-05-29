#!/usr/bin/env python3
"""Prepare a conservative glyph-level review queue for annotated matrix groups."""
from __future__ import annotations

import argparse
import csv
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


def split_tokens(value: str) -> list[str]:
    return [token for token in value.split() if token]


def matching_annotations(pair: dict[str, str], annotations: list[dict[str, str]]) -> list[dict[str, str]]:
    tokens = set(split_tokens(pair.get("tokens", "")))
    return [
        row
        for row in annotations
        if row.get("folio") == pair.get("folio")
        and row.get("locus") == pair.get("locus")
        and row.get("token") in tokens
    ]


def missing_tokens(pair: dict[str, str], matched_annotations: list[dict[str, str]]) -> list[str]:
    matched_tokens = {row.get("token", "") for row in matched_annotations}
    return [token for token in split_tokens(pair.get("tokens", "")) if token not in matched_tokens]


def exact_glyph_status(annotations: list[dict[str, str]]) -> str:
    if not annotations:
        return "no_direct_annotation"
    notes = " ".join(row.get("visual_notes", "").lower() for row in annotations)
    if "not isolated" in notes or "not isolated at glyph" in notes:
        return "needs_exact_glyph_isolation"
    if "exact glyph located" in notes or "glyph position confirmed" in notes:
        return "glyph_position_confirmed"
    return "needs_manual_review"


def join_values(values: list[str]) -> str:
    return " | ".join(sorted({value for value in values if value}))


def review_next_action(status: str, missing: list[str]) -> str:
    if status == "glyph_position_confirmed" and not missing:
        return "record coordinates and compare axis values"
    if missing:
        return "locate missing group tokens in image, then crop/zoom all matched tokens"
    return "crop/zoom image and isolate exact glyph positions"


def build_review_queue(
    pairs: list[dict[str, str]],
    annotations: list[dict[str, str]],
) -> list[dict[str, str]]:
    queue: list[dict[str, str]] = []
    annotated_pairs = [row for row in pairs if int(row.get("annotated_tokens") or "0") > 0]
    annotated_pairs.sort(key=lambda row: (-int(row.get("priority_score") or "0"), row["folio"], row["locus"]))

    for index, pair in enumerate(annotated_pairs, start=1):
        matched = matching_annotations(pair, annotations)
        missing = missing_tokens(pair, matched)
        status = exact_glyph_status(matched)
        queue.append(
            {
                "review_id": f"R6-{index:03d}",
                "priority_score": pair.get("priority_score", ""),
                "folio": pair.get("folio", ""),
                "locus": pair.get("locus", ""),
                "locus_kind": pair.get("locus_kind", ""),
                "prefix_family": pair.get("prefix_family", ""),
                "suffixes_present": pair.get("suffixes_present", ""),
                "axis_coverage": pair.get("axis_coverage", ""),
                "group_tokens": pair.get("tokens", ""),
                "matched_annotation_tokens": " ".join(sorted({row.get("token", "") for row in matched if row.get("token")})),
                "missing_group_tokens": " ".join(missing),
                "exact_glyph_status": status,
                "image_files": join_values([row.get("image_file_or_url", "") for row in matched]),
                "ink_colors": join_values([row.get("ink_color", "") for row in matched]),
                "visual_zones": join_values([row.get("visual_zone", "") for row in matched]) or pair.get("visual_zones", ""),
                "ring": join_values([row.get("ring", "") for row in matched]),
                "sector": join_values([row.get("sector", "") for row in matched]),
                "radius": join_values([row.get("radius", "") for row in matched]),
                "object_nearby": join_values([row.get("object_nearby", "") for row in matched]) or pair.get("object_nearby", ""),
                "annotation_confidence": join_values([row.get("annotation_confidence", "") for row in matched])
                or pair.get("annotation_confidence", ""),
                "review_next_action": review_next_action(status, missing),
                "review_notes": join_values([row.get("visual_notes", "") for row in matched]),
            }
        )
    return queue


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "review_id",
        "priority_score",
        "folio",
        "locus",
        "locus_kind",
        "prefix_family",
        "suffixes_present",
        "axis_coverage",
        "group_tokens",
        "matched_annotation_tokens",
        "missing_group_tokens",
        "exact_glyph_status",
        "image_files",
        "ink_colors",
        "visual_zones",
        "ring",
        "sector",
        "radius",
        "object_nearby",
        "annotation_confidence",
        "review_next_action",
        "review_notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_count_table(title: str, counts: Counter[str]) -> list[str]:
    lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"|{key}|{value}|")
    lines.append("")
    return lines


def write_markdown(path: Path, rows: list[dict[str, str]], pairs_source: Path, visual_source: Path, output_csv: Path) -> None:
    status_counts = Counter(row["exact_glyph_status"] for row in rows)
    folio_counts = Counter(row["folio"] for row in rows)
    image_counts = Counter(row["image_files"] for row in rows)
    lines = [
        "# Rota 6: conferencia fina dos glifos",
        "",
        "Esta rota pega somente os grupos locais que ja tem anotacao visual direta. Ela nao afirma posicao exata de glifo quando a anotacao anterior so localizou a camada/folio.",
        "",
        f"Fonte dos grupos: `{pairs_source}`.",
        f"Fonte visual: `{visual_source}`.",
        f"CSV de revisao: `{output_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- grupos na fila: {len(rows)};",
        f"- status dominante: {status_counts.most_common(1)[0][0] if status_counts else 'none'};",
        "- nenhuma atribuicao semantica nova foi feita nesta rota.",
        "",
    ]
    lines.extend(render_count_table("Status de isolamento", status_counts))
    lines.extend(render_count_table("Folios na fila", folio_counts))
    lines.extend(render_count_table("Arquivos de imagem", image_counts))
    lines.extend(
        [
            "## Fila de revisao",
            "",
            "|id|score|folio|locus|familia|sufixos|eixo|tokens anotados|faltam|status|acao|",
            "|---|---:|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['review_id']}|{row['priority_score']}|{row['folio']}|{row['locus']}|{row['prefix_family']}|{row['suffixes_present']}|{row['axis_coverage']}|{row['matched_annotation_tokens']}|{row['missing_group_tokens']}|{row['exact_glyph_status']}|{row['review_next_action']}|"
        )
    lines.extend(
        [
            "",
            "## Leitura provisoria",
            "",
            "- A Rota 5 achou pares locais; a Rota 6 mostra que a evidencia visual ainda esta em nivel de camada, nao de glifo.",
            "- Todos os itens desta fila devem ser tratados como tarefas de zoom/crop antes de qualquer leitura de eixo.",
            "- Os melhores alvos iniciais sao `f67r1`, `f70v2`, `f68r3` e `f84r`, porque ja possuem imagem local e anotacao media.",
            "- A proxima etapa deve produzir recortes ou coordenadas aproximadas, preservando o status `not isolated` quando a palavra exata nao puder ser localizada.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pairs_csv", help="CSV from analyze_same_context_pairs.py")
    parser.add_argument("visual_csv", help="Visual annotation CSV")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "annotations" / "glyph_review_queue_zl3b.csv"),
        help="Glyph review queue CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_6_conferencia_glifos.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    pairs_source = Path(args.pairs_csv)
    visual_source = Path(args.visual_csv)
    pairs = read_csv(pairs_source)
    annotations = read_csv(visual_source)
    queue = build_review_queue(pairs, annotations)
    csv_path = Path(args.csv)
    md_path = Path(args.md)
    write_csv(csv_path, queue)
    write_markdown(md_path, queue, pairs_source, visual_source, csv_path)
    print(f"pairs={len(pairs)} visual_rows={len(annotations)} review_queue={len(queue)}")
    print(f"csv={csv_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
