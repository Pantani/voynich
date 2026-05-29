#!/usr/bin/env python3
"""Prepare a fillable visual decision entry sheet for pending P0/P1 items."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

ALLOWED_MANUAL_VALUES = {
    "manual_token_seen": "yes/no/uncertain",
    "manual_new_crop_needed": "yes/no",
    "manual_image_insufficient": "yes/no",
}

ENTRY_STATUS = "awaiting_manual_entry"
OUTPUT_RULE = "copy_completed_entry_values_to_direct_visual_package"
GUARDRAIL = "entry_sheet_not_visual_evidence"

FIELDNAMES = [
    "route21_id",
    "route20_id",
    "route19_id",
    "route18_id",
    "route17_id",
    "checklist_id",
    "packet_id",
    "manual_review_id",
    "crop_id",
    "folio",
    "locus",
    "source_image",
    "crop_svg",
    "review_region",
    "priority_bucket",
    "priority_level",
    "target_type",
    "review_target",
    "entry_status",
    "allowed_manual_token_seen",
    "allowed_manual_new_crop_needed",
    "allowed_manual_image_insufficient",
    "manual_token_seen",
    "manual_new_crop_needed",
    "manual_image_insufficient",
    "manual_new_crop_x",
    "manual_new_crop_y",
    "manual_new_crop_width",
    "manual_new_crop_height",
    "manual_notes",
    "source_application_status",
    "source_next_action",
    "entry_action",
    "output_rule",
    "semantic_guardrail",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def allowed_values(field: str) -> str:
    return ALLOWED_MANUAL_VALUES.get(field, "")


def is_pending_blank_application(row: dict[str, str]) -> bool:
    return row.get("application_status") == "skipped_blank_manual_decision"


def package_indexes(rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    by_route19 = {row.get("route19_id", ""): row for row in rows if row.get("route19_id", "")}
    by_checklist = {row.get("checklist_id", ""): row for row in rows if row.get("checklist_id", "")}
    return by_route19, by_checklist


def build_entry_rows(
    application_log_rows: list[dict[str, str]],
    package_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    by_route19, by_checklist = package_indexes(package_rows)
    pending = [row for row in application_log_rows if is_pending_blank_application(row)]
    entry_rows: list[dict[str, str]] = []
    for index, log_row in enumerate(pending, start=1):
        package = by_route19.get(log_row.get("route19_id", "")) or by_checklist.get(log_row.get("checklist_id", "")) or {}

        def value(field: str) -> str:
            return package.get(field, "") or log_row.get(field, "")

        entry_rows.append(
            {
                "route21_id": f"R21-{index:03d}",
                "route20_id": log_row.get("route20_id", ""),
                "route19_id": value("route19_id"),
                "route18_id": value("route18_id"),
                "route17_id": value("route17_id"),
                "checklist_id": value("checklist_id"),
                "packet_id": value("packet_id"),
                "manual_review_id": value("manual_review_id"),
                "crop_id": value("crop_id"),
                "folio": value("folio"),
                "locus": value("locus"),
                "source_image": value("source_image"),
                "crop_svg": value("crop_svg"),
                "review_region": value("review_region"),
                "priority_bucket": value("priority_bucket"),
                "priority_level": value("priority_level"),
                "target_type": value("target_type"),
                "review_target": value("review_target"),
                "entry_status": ENTRY_STATUS,
                "allowed_manual_token_seen": allowed_values("manual_token_seen"),
                "allowed_manual_new_crop_needed": allowed_values("manual_new_crop_needed"),
                "allowed_manual_image_insufficient": allowed_values("manual_image_insufficient"),
                "manual_token_seen": "",
                "manual_new_crop_needed": "",
                "manual_image_insufficient": "",
                "manual_new_crop_x": "",
                "manual_new_crop_y": "",
                "manual_new_crop_width": "",
                "manual_new_crop_height": "",
                "manual_notes": "",
                "source_application_status": log_row.get("application_status", ""),
                "source_next_action": log_row.get("next_action", ""),
                "entry_action": "fill_allowed_manual_fields_after_source_image_review",
                "output_rule": OUTPUT_RULE,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return entry_rows


def summarize_entry_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "entry_status": Counter(row.get("entry_status", "") for row in rows),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
        "target_type": Counter(row.get("target_type", "") for row in rows),
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


def render_entry_section(row: dict[str, str]) -> str:
    lines = [
        f"## {row['route21_id']} / {row.get('route20_id', '')} / {row.get('checklist_id', '')}",
        "",
        f"- alvo: `{row.get('review_target', '')}`;",
        f"- folio: `{row.get('folio', '')}`;",
        f"- imagem fonte: `{row.get('source_image', '')}`;",
        f"- SVG de referencia: `{row.get('crop_svg', '')}`;",
        f"- regiao atual: `{row.get('review_region', '')}`;",
        f"- valores permitidos para `manual_token_seen`: `{row.get('allowed_manual_token_seen', '')}`;",
        f"- valores permitidos para `manual_new_crop_needed`: `{row.get('allowed_manual_new_crop_needed', '')}`;",
        f"- valores permitidos para `manual_image_insufficient`: `{row.get('allowed_manual_image_insufficient', '')}`;",
        f"- regra de saida: `{row.get('output_rule', '')}`;",
        f"- guarda: `{row.get('semantic_guardrail', '')}`;",
        "",
    ]
    return "\n".join(lines)


def write_report(
    path: Path,
    rows: list[dict[str, str]],
    application_log_csv: Path,
    package_csv: Path,
    output_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_entry_rows(rows)
    lines = [
        "# Rota 21: planilha de preenchimento visual P0/P1",
        "",
        "Esta rota cria uma planilha enxuta para preencher manualmente os 6 itens P0/P1 que a Rota 20 manteve em branco. Ela nao decide campos visuais e nao converte ausencia de anotacao em evidencia.",
        "",
        f"Log de aplicacao fonte: `{application_log_csv}`.",
        f"Pacote visual fonte: `{package_csv}`.",
        f"Planilha de entrada: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Valores permitidos",
        "",
        "- `manual_token_seen`: `yes/no/uncertain`;",
        "- `manual_new_crop_needed`: `yes/no`;",
        "- `manual_image_insufficient`: `yes/no`;",
        "- coordenadas de novo recorte devem ficar vazias quando `manual_new_crop_needed=no`.",
        "",
        "## Resultado curto",
        "",
        f"- linhas para preencher: {len(rows)};",
        f"- P0: {summary['priority_level'].get('P0', 0)};",
        f"- P1: {summary['priority_level'].get('P1', 0)};",
        "- campos manuais permanecem em branco;",
        "- guarda: `entry_sheet_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Status de entrada", summary["entry_status"]))
    lines.extend(render_counts("Prioridade", summary["priority_level"]))
    lines.extend(render_counts("Folios", summary["folio"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota21|rota20|rota19|checklist|prioridade|folio|alvo|imagem|SVG|",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['route21_id']}|{row['route20_id']}|{row['route19_id']}|{row['checklist_id']}|{row['priority_level']}|{row['folio']}|{row['review_target']}|`{row['source_image']}`|`{row['crop_svg']}`|"
        )
    lines.append("")
    for row in rows:
        lines.append(render_entry_section(row))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("application_log_csv", help="CSV from apply_direct_visual_decisions.py")
    parser.add_argument("direct_visual_package_csv", help="CSV from prepare_direct_visual_decision_package.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "annotations" / "visual_decision_entry_sheet_p0_p1_zl3b.csv"),
        help="Visual decision entry sheet CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "visual_decision_entry_sheet_summary_zl3b.csv"),
        help="Visual decision entry sheet summary output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_21_planilha_preenchimento_visual_p0_p1.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    application_log_csv = Path(args.application_log_csv)
    package_csv = Path(args.direct_visual_package_csv)
    rows = build_entry_rows(read_csv(application_log_csv), read_csv(package_csv))
    summary = summarize_entry_rows(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, rows, FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_report(md_path, rows, application_log_csv, package_csv, csv_path, summary_path)
    print(
        f"visual_decision_entry_rows={len(rows)} "
        f"p0={summary['priority_level'].get('P0', 0)} "
        f"p1={summary['priority_level'].get('P1', 0)}"
    )
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
