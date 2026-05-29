#!/usr/bin/env python3
"""Prepare a second-pass crop/review queue for route 11."""
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


def missing_token_count(value: str) -> int:
    return len([token for token in value.split() if token])


def priority_bucket(row: dict[str, str]) -> str:
    family = row.get("prefix_family", "")
    missing = missing_token_count(row.get("missing_group_tokens", ""))
    if family in {"ot", "ok", "qok"} and missing:
        return "P0_operator_missing_tokens"
    if family in {"ch", "d", "sh"} and missing:
        return "P1_core_missing_tokens"
    if missing:
        return "P2_other_missing_tokens"
    return "P3_tighten_existing_region"


def second_pass_focus(row: dict[str, str]) -> str:
    if missing_token_count(row.get("missing_group_tokens", "")):
        return "locate_missing_group_tokens"
    return "tighten_existing_matched_tokens"


def crop_strategy(row: dict[str, str]) -> str:
    missing = missing_token_count(row.get("missing_group_tokens", ""))
    if missing >= 2:
        return "rescan_source_image_before_new_crop"
    if missing == 1:
        return "search_single_missing_token_then_redraw_crop"
    return "tighten_current_svg_region"


def suggested_action(row: dict[str, str]) -> str:
    focus = second_pass_focus(row)
    if focus == "locate_missing_group_tokens":
        return "open source folio image and search missing tokens before marking any tighter region"
    return "open current SVG and mark a smaller region only if the matched tokens are visually clear"


def is_queue_candidate(row: dict[str, str]) -> bool:
    return (
        row.get("consolidation_outcome") == "pending_manual_review"
        and row.get("coordinate_status") == "no_manual_coordinates"
        and row.get("evidence_status") == "no_glyph_confirmation"
        and row.get("axis_test_eligibility") == "not_eligible"
    )


def priority_sort_key(row: dict[str, str]) -> tuple[int, int, str, str, str]:
    bucket_order = {
        "P0_operator_missing_tokens": 0,
        "P1_core_missing_tokens": 1,
        "P2_other_missing_tokens": 2,
        "P3_tighten_existing_region": 3,
    }
    bucket = priority_bucket(row)
    return (
        bucket_order.get(bucket, 9),
        -missing_token_count(row.get("missing_group_tokens", "")),
        row.get("folio", ""),
        row.get("locus", ""),
        row.get("route10_id", ""),
    )


def build_second_pass_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    candidates = sorted((row for row in rows if is_queue_candidate(row)), key=priority_sort_key)
    queue: list[dict[str, str]] = []
    for index, row in enumerate(candidates, start=1):
        queue.append(
            {
                "route11_id": f"R11-{index:03d}",
                "route10_id": row.get("route10_id", ""),
                "manual_review_id": row.get("manual_review_id", ""),
                "decision_id": row.get("decision_id", ""),
                "crop_id": row.get("crop_id", ""),
                "source_review_id": row.get("source_review_id", ""),
                "folio": row.get("folio", ""),
                "locus": row.get("locus", ""),
                "prefix_family": row.get("prefix_family", ""),
                "axis_coverage": row.get("axis_coverage", ""),
                "group_tokens": row.get("group_tokens", ""),
                "missing_group_tokens": row.get("missing_group_tokens", ""),
                "missing_token_count": str(missing_token_count(row.get("missing_group_tokens", ""))),
                "priority_bucket": priority_bucket(row),
                "second_pass_focus": second_pass_focus(row),
                "crop_strategy": crop_strategy(row),
                "suggested_action": suggested_action(row),
                "semantic_guardrail": "no_axis_meaning_from_queue_position",
            }
        )
    return queue


def summarize_queue(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "priority_bucket": Counter(row["priority_bucket"] for row in rows),
        "second_pass_focus": Counter(row["second_pass_focus"] for row in rows),
        "crop_strategy": Counter(row["crop_strategy"] for row in rows),
        "prefix_family": Counter(row["prefix_family"] for row in rows),
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "route11_id",
        "route10_id",
        "manual_review_id",
        "decision_id",
        "crop_id",
        "source_review_id",
        "folio",
        "locus",
        "prefix_family",
        "axis_coverage",
        "group_tokens",
        "missing_group_tokens",
        "missing_token_count",
        "priority_bucket",
        "second_pass_focus",
        "crop_strategy",
        "suggested_action",
        "semantic_guardrail",
    ]
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
    source_csv: Path,
    output_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_queue(rows)
    missing_targets = sum(int(row["missing_token_count"]) for row in rows)
    lines = [
        "# Rota 11: segunda passada de recortes melhores",
        "",
        "Esta rota transforma os itens pendentes da Rota 10 em uma fila objetiva para nova revisao visual. Ela nao interpreta os eixos da matriz.",
        "",
        f"Fonte: `{source_csv}`.",
        f"Fila de trabalho: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens na fila: {len(rows)};",
        f"- tokens faltantes a procurar: {missing_targets};",
        f"- itens com foco em tokens faltantes: {summary['second_pass_focus'].get('locate_missing_group_tokens', 0)};",
        f"- itens para apertar regiao existente: {summary['second_pass_focus'].get('tighten_existing_matched_tokens', 0)};",
        "- nenhuma linha fica elegivel para semantica por estar nesta fila.",
        "",
    ]
    lines.extend(render_counts("Prioridade", summary["priority_bucket"]))
    lines.extend(render_counts("Foco da segunda passada", summary["second_pass_focus"]))
    lines.extend(render_counts("Estrategia de recorte", summary["crop_strategy"]))
    lines.extend(render_counts("Familias", summary["prefix_family"]))
    lines.extend(
        [
            "## Fila",
            "",
            "|rota11|rota10|manual|crop|familia|folio|locus|faltam|prioridade|foco|estrategia|",
            "|---|---|---|---|---|---|---|---:|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['route11_id']}|{row['route10_id']}|{row['manual_review_id']}|{row['crop_id']}|{row['prefix_family']}|{row['folio']}|{row['locus']}|{row['missing_token_count']}|{row['priority_bucket']}|{row['second_pass_focus']}|{row['crop_strategy']}|"
        )
    lines.extend(
        [
            "",
            "## Leitura provisoria",
            "",
            "- A fila prioriza revisao operacional, nao importancia semantica.",
            "- Itens `P0` indicam operadores com tokens faltantes e devem ser conferidos primeiro.",
            "- Itens `P3` ja tinham tokens anotados, mas ainda precisam de uma regiao menor antes de qualquer teste fino.",
            "- A proxima rota pode gerar instrucoes por folio ou recortes alternativos, preservando a guarda `no_axis_meaning_from_queue_position`.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("consolidated_csv", help="CSV from consolidate_manual_svg_review.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "annotations" / "second_pass_crop_queue_zl3b.csv"),
        help="Second-pass queue CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "second_pass_crop_queue_summary_zl3b.csv"),
        help="Queue summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_11_segunda_passada_recortes.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = Path(args.consolidated_csv)
    queue = build_second_pass_rows(read_csv(source))
    summary = summarize_queue(queue)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, queue)
    write_summary_csv(summary_path, summary)
    write_report(md_path, queue, source, csv_path, summary_path)
    print(f"second_pass_queue_rows={len(queue)}")
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
