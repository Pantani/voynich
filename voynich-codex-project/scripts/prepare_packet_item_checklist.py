#!/usr/bin/env python3
"""Prepare item-level checklist sheets for route 13 folio review packets."""
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


def review_target_type(row: dict[str, str]) -> str:
    if row.get("second_pass_focus") == "locate_missing_group_tokens":
        return "missing_group_tokens"
    return "matched_group_tokens"


def review_target(row: dict[str, str]) -> str:
    if review_target_type(row) == "missing_group_tokens":
        return row.get("missing_group_tokens", "")
    return row.get("group_tokens", "")


def checklist_template(row: dict[str, str], index: int) -> dict[str, str]:
    return {
        "checklist_id": f"R13-{index:03d}",
        "packet_id": row.get("packet_id", ""),
        "route11_id": row.get("route11_id", ""),
        "route10_id": row.get("route10_id", ""),
        "manual_review_id": row.get("manual_review_id", ""),
        "crop_id": row.get("crop_id", ""),
        "source_review_id": row.get("source_review_id", ""),
        "folio": row.get("folio", ""),
        "locus": row.get("locus", ""),
        "source_image": row.get("source_image", ""),
        "crop_svg": row.get("crop_svg", ""),
        "review_region": row.get("review_region", ""),
        "prefix_family": row.get("prefix_family", ""),
        "axis_coverage": row.get("axis_coverage", ""),
        "priority_bucket": row.get("priority_bucket", ""),
        "second_pass_focus": row.get("second_pass_focus", ""),
        "crop_strategy": row.get("crop_strategy", ""),
        "group_tokens": row.get("group_tokens", ""),
        "missing_group_tokens": row.get("missing_group_tokens", ""),
        "target_type": review_target_type(row),
        "review_target": review_target(row),
        "initial_check_status": "pending_visual_check",
        "manual_token_seen": "",
        "manual_new_crop_needed": "",
        "manual_image_insufficient": "",
        "manual_new_crop_x": "",
        "manual_new_crop_y": "",
        "manual_new_crop_width": "",
        "manual_new_crop_height": "",
        "manual_notes": "",
        "semantic_guardrail": "checklist_item_not_axis_evidence",
    }


def sort_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (row.get("packet_id", ""), row.get("priority_bucket", ""), row.get("route11_id", ""))


def build_checklist_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    sorted_rows = sorted(rows, key=sort_key)
    return [checklist_template(row, index) for index, row in enumerate(sorted_rows, start=1)]


def summarize_checklist(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "packet_id": Counter(row["packet_id"] for row in rows),
        "target_type": Counter(row["target_type"] for row in rows),
        "initial_check_status": Counter(row["initial_check_status"] for row in rows),
        "priority_bucket": Counter(row["priority_bucket"] for row in rows),
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "checklist_id",
        "packet_id",
        "route11_id",
        "route10_id",
        "manual_review_id",
        "crop_id",
        "source_review_id",
        "folio",
        "locus",
        "source_image",
        "crop_svg",
        "review_region",
        "prefix_family",
        "axis_coverage",
        "priority_bucket",
        "second_pass_focus",
        "crop_strategy",
        "group_tokens",
        "missing_group_tokens",
        "target_type",
        "review_target",
        "initial_check_status",
        "manual_token_seen",
        "manual_new_crop_needed",
        "manual_image_insufficient",
        "manual_new_crop_x",
        "manual_new_crop_y",
        "manual_new_crop_width",
        "manual_new_crop_height",
        "manual_notes",
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


def write_report(path: Path, rows: list[dict[str, str]], source_csv: Path, output_csv: Path, summary_csv: Path) -> None:
    summary = summarize_checklist(rows)
    lines = [
        "# Rota 13: checklist item-a-item por pacote",
        "",
        "Esta rota gera uma folha preenchivel para revisar cada item dos pacotes Rota 12. Ela preserva rastreabilidade e deixa campos manuais vazios por desenho.",
        "",
        f"Fonte: `{source_csv}`.",
        f"Checklist: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens na checklist: {len(rows)};",
        f"- itens para procurar tokens faltantes: {summary['target_type'].get('missing_group_tokens', 0)};",
        f"- itens para apertar tokens ja anotados: {summary['target_type'].get('matched_group_tokens', 0)};",
        "- todos os campos manuais ficam vazios ate revisao visual real;",
        "- nenhuma linha autoriza leitura semantica dos eixos.",
        "",
    ]
    lines.extend(render_counts("Itens por pacote", summary["packet_id"]))
    lines.extend(render_counts("Tipo de alvo", summary["target_type"]))
    lines.extend(render_counts("Status inicial", summary["initial_check_status"]))
    lines.extend(render_counts("Prioridade", summary["priority_bucket"]))
    lines.extend(
        [
            "## Checklist",
            "",
            "|checklist|pacote|rota11|folio|locus|alvo|tipo|status|",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['checklist_id']}|{row['packet_id']}|{row['route11_id']}|{row['folio']}|{row['locus']}|{row['review_target']}|{row['target_type']}|{row['initial_check_status']}|"
        )
    lines.extend(
        [
            "",
            "## Como preencher",
            "",
            "- `manual_token_seen`: use `yes`, `no` ou `uncertain` depois de olhar a imagem.",
            "- `manual_new_crop_needed`: use `yes` somente se houver base visual para novo recorte.",
            "- `manual_image_insufficient`: use `yes` quando a imagem atual nao permitir decisao.",
            "- Coordenadas novas devem ser preenchidas apenas quando um recorte menor for realmente visivel.",
            "- `checklist_item_not_axis_evidence` significa que a linha ainda nao prova nada sobre `a/o` ou `r/l`.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet_items_csv", help="CSV from prepare_folio_review_packets.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "annotations" / "packet_item_checklist_zl3b.csv"),
        help="Checklist CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "packet_item_checklist_summary_zl3b.csv"),
        help="Checklist summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_13_checklist_pacotes.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = Path(args.packet_items_csv)
    rows = build_checklist_rows(read_csv(source))
    summary = summarize_checklist(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, rows)
    write_summary_csv(summary_path, summary)
    write_report(md_path, rows, source, csv_path, summary_path)
    print(f"checklist_rows={len(rows)}")
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
