#!/usr/bin/env python3
"""Prepare the route 17 P0/P1 pending human visual review batch."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS_TO_FILL = (
    "manual_token_seen manual_new_crop_needed manual_image_insufficient "
    "manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes"
)

PRIORITY_ORDER = {"P0": 0, "P1": 1}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def priority_level(row: dict[str, str]) -> str:
    bucket = row.get("priority_bucket", "")
    if "_" not in bucket:
        return bucket or "unranked"
    return bucket.split("_", 1)[0]


def review_focus(row: dict[str, str]) -> str:
    bucket = row.get("priority_bucket", "")
    if bucket.startswith("P0_"):
        return "operator_missing_tokens_first"
    if bucket.startswith("P1_"):
        return "core_missing_tokens_second"
    return "defer_to_later_batch"


def priority_sort_key(row: dict[str, str]) -> tuple[int, str, str]:
    level = priority_level(row)
    return (PRIORITY_ORDER.get(level, 99), row.get("packet_id", ""), row.get("route16_id", ""))


def is_priority_pending(row: dict[str, str]) -> bool:
    return (
        row.get("human_review_state") == "pending_human_review"
        and priority_level(row) in PRIORITY_ORDER
    )


def build_priority_review_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    selected = sorted((row for row in rows if is_priority_pending(row)), key=priority_sort_key)
    review_rows: list[dict[str, str]] = []
    for index, row in enumerate(selected, start=1):
        level = priority_level(row)
        review_rows.append(
            {
                "route17_id": f"R17-{index:03d}",
                "route16_id": row.get("route16_id", ""),
                "instruction_item_id": row.get("instruction_item_id", ""),
                "checklist_id": row.get("checklist_id", ""),
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
                "priority_bucket": row.get("priority_bucket", ""),
                "priority_level": level,
                "target_type": row.get("target_type", ""),
                "review_target": row.get("review_target", ""),
                "review_focus": review_focus(row),
                "review_batch": "P0_P1_pending_human_review",
                "fields_to_fill": FIELDS_TO_FILL,
                "review_action": "open_source_image_compare_svg_fill_checklist",
                "output_rule": "update_packet_item_checklist_manual_fields_only",
                "semantic_guardrail": "priority_review_not_visual_evidence",
            }
        )
    return review_rows


def summarize_priority_review(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "packet_id": Counter(row.get("packet_id", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
        "target_type": Counter(row.get("target_type", "") for row in rows),
        "review_focus": Counter(row.get("review_focus", "") for row in rows),
    }


FIELDNAMES = [
    "route17_id",
    "route16_id",
    "instruction_item_id",
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
    "priority_bucket",
    "priority_level",
    "target_type",
    "review_target",
    "review_focus",
    "review_batch",
    "fields_to_fill",
    "review_action",
    "output_rule",
    "semantic_guardrail",
]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
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


def render_review_section(row: dict[str, str]) -> str:
    lines = [
        f"## {row['route17_id']} / {row['checklist_id']} / {row['folio']}",
        "",
        f"- alvo: `{row['review_target']}`;",
        f"- imagem fonte: `{row['source_image']}`;",
        f"- SVG de referencia: `{row['crop_svg']}`;",
        f"- regiao atual: `{row.get('review_region', '')}`;",
        f"- campos a preencher: `{row['fields_to_fill']}`;",
        f"- guarda: `{row['semantic_guardrail']}`;",
        "",
        "Procedimento:",
        "",
        "- Abra a imagem fonte antes de decidir qualquer campo manual.",
        "- Use o SVG apenas para localizar a regiao aproximada.",
        "- Preencha a checklist, nao este consolidado.",
        "- Se a palavra nao estiver clara, use `manual_token_seen=uncertain` ou marque imagem insuficiente.",
        "- Nao atribua significado a `a/o` ou `r/l` nesta etapa.",
        "",
    ]
    return "\n".join(lines)


def write_report(
    path: Path,
    rows: list[dict[str, str]],
    source_csv: Path,
    output_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_priority_review(rows)
    lines = [
        "# Rota 17: revisao humana P0/P1",
        "",
        "Esta rota prepara o lote P0/P1 pendente para revisao visual humana efetiva. Ela nao preenche campos manuais e nao cria evidencia visual por inferencia.",
        "",
        f"Fonte: `{source_csv}`.",
        f"Fila P0/P1: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens P0/P1 na fila: {len(rows)};",
        f"- P0: {summary['priority_level'].get('P0', 0)};",
        f"- P1: {summary['priority_level'].get('P1', 0)};",
        "- campos manuais permanecem vazios ate revisao visual real;",
        "- guarda: `priority_review_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Prioridade", summary["priority_level"]))
    lines.extend(render_counts("Pacotes", summary["packet_id"]))
    lines.extend(render_counts("Folios", summary["folio"]))
    lines.extend(render_counts("Foco de revisao", summary["review_focus"]))
    lines.extend(
        [
            "## Fila resumida",
            "",
            "|rota17|checklist|prioridade|folio|alvo|imagem|SVG|",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['route17_id']}|{row['checklist_id']}|{row['priority_level']}|{row['folio']}|{row['review_target']}|`{row['source_image']}`|`{row['crop_svg']}`|"
        )
    lines.append("")
    for row in rows:
        lines.append(render_review_section(row))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("human_review_evidence_csv", help="CSV from consolidate_human_review_evidence.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "annotations" / "priority_human_review_p0_p1_zl3b.csv"),
        help="P0/P1 priority human review CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "priority_human_review_summary_zl3b.csv"),
        help="P0/P1 priority human review summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_17_revisao_humana_p0_p1.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = Path(args.human_review_evidence_csv)
    rows = build_priority_review_rows(read_csv(source))
    summary = summarize_priority_review(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, rows)
    write_summary_csv(summary_path, summary)
    write_report(md_path, rows, source, csv_path, summary_path)
    print(f"priority_review_rows={len(rows)} p0={summary['priority_level'].get('P0', 0)} p1={summary['priority_level'].get('P1', 0)}")
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
