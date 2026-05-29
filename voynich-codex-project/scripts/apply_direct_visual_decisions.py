#!/usr/bin/env python3
"""Apply filled route 19 direct visual decisions to a derived checklist."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANUAL_FIELDS = [
    "manual_token_seen",
    "manual_new_crop_needed",
    "manual_image_insufficient",
    "manual_new_crop_x",
    "manual_new_crop_y",
    "manual_new_crop_width",
    "manual_new_crop_height",
    "manual_notes",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def read_fieldnames(path: Path) -> list[str]:
    with path.open(encoding="utf-8", newline="") as f:
        reader = csv.reader(f)
        return next(reader)


def has_manual_values(row: dict[str, str]) -> bool:
    return any(row.get(field, "") != "" for field in MANUAL_FIELDS)


def application_status(package_row: dict[str, str], checklist_exists: bool) -> str:
    if not checklist_exists:
        return "missing_checklist_row"
    if has_manual_values(package_row):
        return "applied_manual_values"
    return "skipped_blank_manual_decision"


def package_index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("checklist_id", ""): row for row in rows if row.get("checklist_id", "")}


def apply_decision_rows(
    checklist_rows: list[dict[str, str]],
    package_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    package_by_id = package_index(package_rows)
    updated: list[dict[str, str]] = []
    for row in checklist_rows:
        new_row = dict(row)
        package = package_by_id.get(row.get("checklist_id", ""))
        if package and has_manual_values(package):
            for field in MANUAL_FIELDS:
                value = package.get(field, "")
                if value != "":
                    new_row[field] = value
        updated.append(new_row)
    return updated


def build_application_log(
    checklist_rows: list[dict[str, str]],
    package_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    checklist_ids = {row.get("checklist_id", "") for row in checklist_rows}
    log_rows: list[dict[str, str]] = []
    for index, row in enumerate(package_rows, start=1):
        checklist_id = row.get("checklist_id", "")
        exists = checklist_id in checklist_ids
        status = application_status(row, exists)
        log_rows.append(
            {
                "route20_id": f"R20-{index:03d}",
                "route19_id": row.get("route19_id", ""),
                "route18_id": row.get("route18_id", ""),
                "route17_id": row.get("route17_id", ""),
                "checklist_id": checklist_id,
                "packet_id": row.get("packet_id", ""),
                "manual_review_id": row.get("manual_review_id", ""),
                "crop_id": row.get("crop_id", ""),
                "folio": row.get("folio", ""),
                "priority_level": row.get("priority_level", ""),
                "target_type": row.get("target_type", ""),
                "review_target": row.get("review_target", ""),
                "manual_token_seen": row.get("manual_token_seen", ""),
                "manual_new_crop_needed": row.get("manual_new_crop_needed", ""),
                "manual_image_insufficient": row.get("manual_image_insufficient", ""),
                "manual_new_crop_x": row.get("manual_new_crop_x", ""),
                "manual_new_crop_y": row.get("manual_new_crop_y", ""),
                "manual_new_crop_width": row.get("manual_new_crop_width", ""),
                "manual_new_crop_height": row.get("manual_new_crop_height", ""),
                "manual_notes": row.get("manual_notes", ""),
                "application_status": status,
                "next_action": next_action(status),
                "semantic_guardrail": "applied_values_are_manual_not_axis_meaning",
            }
        )
    return log_rows


def next_action(status: str) -> str:
    if status == "applied_manual_values":
        return "rerun priority decision ingestion and checklist consolidation"
    if status == "missing_checklist_row":
        return "restore matching checklist row before applying manual values"
    return "fill direct visual package fields before applying"


def summarize_application_log(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "application_status": Counter(row.get("application_status", "") for row in rows),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
        "target_type": Counter(row.get("target_type", "") for row in rows),
    }


LOG_FIELDNAMES = [
    "route20_id",
    "route19_id",
    "route18_id",
    "route17_id",
    "checklist_id",
    "packet_id",
    "manual_review_id",
    "crop_id",
    "folio",
    "priority_level",
    "target_type",
    "review_target",
    "manual_token_seen",
    "manual_new_crop_needed",
    "manual_image_insufficient",
    "manual_new_crop_x",
    "manual_new_crop_y",
    "manual_new_crop_width",
    "manual_new_crop_height",
    "manual_notes",
    "application_status",
    "next_action",
    "semantic_guardrail",
]


def write_rows(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
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
    log_rows: list[dict[str, str]],
    package_csv: Path,
    checklist_csv: Path,
    output_checklist: Path,
    output_log: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_application_log(log_rows)
    applied = summary["application_status"].get("applied_manual_values", 0)
    skipped = summary["application_status"].get("skipped_blank_manual_decision", 0)
    lines = [
        "# Rota 20: aplicacao do pacote visual na checklist",
        "",
        "Esta rota aplica somente valores manuais preenchidos no pacote visual Rota 19 a uma checklist derivada. A checklist original nao e sobrescrita.",
        "",
        f"Pacote visual: `{package_csv}`.",
        f"Checklist fonte: `{checklist_csv}`.",
        f"Checklist derivada: `{output_checklist}`.",
        f"Log de aplicacao: `{output_log}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- linhas no pacote: {len(log_rows)};",
        f"- aplicadas: {applied};",
        f"- ignoradas por campos vazios: {skipped};",
        "- nenhum campo vazio foi usado para apagar valor existente;",
        "- guarda: `applied_values_are_manual_not_axis_meaning`.",
        "",
    ]
    lines.extend(render_counts("Status de aplicacao", summary["application_status"]))
    lines.extend(render_counts("Prioridade", summary["priority_level"]))
    lines.extend(render_counts("Folios", summary["folio"]))
    lines.extend(
        [
            "## Log",
            "",
            "|rota20|rota19|checklist|prioridade|folio|alvo|status|proxima acao|",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in log_rows:
        lines.append(
            f"|{row['route20_id']}|{row['route19_id']}|{row['checklist_id']}|{row['priority_level']}|{row['folio']}|{row['review_target']}|{row['application_status']}|{row['next_action']}|"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("direct_visual_package_csv", help="CSV from prepare_direct_visual_decision_package.py")
    parser.add_argument("checklist_csv", help="Source packet item checklist CSV")
    parser.add_argument(
        "--updated-checklist-csv",
        default=str(ROOT / "data" / "derived" / "packet_item_checklist_after_direct_visual_p0_p1_zl3b.csv"),
        help="Derived checklist CSV output",
    )
    parser.add_argument(
        "--application-log-csv",
        default=str(ROOT / "data" / "derived" / "direct_visual_decision_application_log_zl3b.csv"),
        help="Application log CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "direct_visual_decision_application_summary_zl3b.csv"),
        help="Application summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_20_aplicacao_decisoes_pacote_visual.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    package_csv = Path(args.direct_visual_package_csv)
    checklist_csv = Path(args.checklist_csv)
    checklist_rows = read_csv(checklist_csv)
    package_rows = read_csv(package_csv)
    updated = apply_decision_rows(checklist_rows, package_rows)
    log_rows = build_application_log(checklist_rows, package_rows)
    summary = summarize_application_log(log_rows)
    checklist_fieldnames = read_fieldnames(checklist_csv)
    updated_path = Path(args.updated_checklist_csv)
    log_path = Path(args.application_log_csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_rows(updated_path, updated, checklist_fieldnames)
    write_rows(log_path, log_rows, LOG_FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_report(md_path, log_rows, package_csv, checklist_csv, updated_path, log_path, summary_path)
    print(
        f"application_rows={len(log_rows)} "
        f"applied={summary['application_status'].get('applied_manual_values', 0)} "
        f"skipped_blank={summary['application_status'].get('skipped_blank_manual_decision', 0)}"
    )
    print(f"updated_checklist_csv={updated_path}")
    print(f"application_log_csv={log_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
