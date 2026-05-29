#!/usr/bin/env python3
"""Validate and apply explicit route 21 visual decision entries."""
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

RECT_FIELDS = [
    "manual_new_crop_x",
    "manual_new_crop_y",
    "manual_new_crop_width",
    "manual_new_crop_height",
]

ALLOWED_VALUES = {
    "manual_token_seen": {"", "yes", "no", "uncertain"},
    "manual_new_crop_needed": {"", "yes", "no"},
    "manual_image_insufficient": {"", "yes", "no"},
}

GUARDRAIL = "validated_values_are_manual_not_axis_meaning"

LOG_FIELDNAMES = [
    "route22_id",
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
    "source_image",
    "crop_svg",
    "review_region",
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
    "validation_status",
    "validation_errors",
    "apply_status",
    "next_action",
    "semantic_guardrail",
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


def add_error(errors: list[str], error: str) -> None:
    if error not in errors:
        errors.append(error)


def parse_int(value: str) -> int | None:
    try:
        return int(value)
    except ValueError:
        return None


def validate_entry_row(row: dict[str, str]) -> list[str]:
    errors: list[str] = []
    for field, allowed in ALLOWED_VALUES.items():
        if row.get(field, "").strip() not in allowed:
            add_error(errors, f"{field}_invalid")

    rect_values = {field: row.get(field, "").strip() for field in RECT_FIELDS}
    has_any_rect = any(rect_values.values())
    has_all_rect = all(rect_values.values())
    crop_needed = row.get("manual_new_crop_needed", "").strip()

    if (crop_needed == "yes" and not has_all_rect) or (has_any_rect and not has_all_rect):
        add_error(errors, "new_crop_rect_incomplete")
    if crop_needed == "no" and has_any_rect:
        add_error(errors, "new_crop_rect_must_be_blank_when_not_needed")
    if has_any_rect and crop_needed != "yes":
        add_error(errors, "new_crop_rect_requires_manual_new_crop_needed_yes")

    for field in ("manual_new_crop_x", "manual_new_crop_y"):
        value = rect_values[field]
        if not value:
            continue
        parsed = parse_int(value)
        if parsed is None or parsed < 0:
            add_error(errors, f"{field}_must_be_nonnegative_integer")

    for field in ("manual_new_crop_width", "manual_new_crop_height"):
        value = rect_values[field]
        if not value:
            continue
        parsed = parse_int(value)
        if parsed is None or parsed <= 0:
            add_error(errors, f"{field}_must_be_positive_integer")

    return errors


def has_manual_values(row: dict[str, str]) -> bool:
    return any(row.get(field, "").strip() != "" for field in MANUAL_FIELDS)


def validation_status(row: dict[str, str]) -> str:
    if validate_entry_row(row):
        return "invalid_manual_entry"
    if has_manual_values(row):
        return "valid_manual_entry"
    return "pending_blank_manual_entry"


def apply_status_for(status: str) -> str:
    if status == "valid_manual_entry":
        return "ready_to_apply_manual_values"
    if status == "invalid_manual_entry":
        return "blocked_invalid_manual_entry"
    return "skipped_blank_manual_entry"


def next_action_for(status: str) -> str:
    if status == "valid_manual_entry":
        return "run route 20 applicator using the derived direct visual package"
    if status == "invalid_manual_entry":
        return "fix invalid manual fields before applying"
    return "fill R21 entry sheet or keep item pending"


def build_validation_log(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    log_rows: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        errors = validate_entry_row(row)
        status = "invalid_manual_entry" if errors else ("valid_manual_entry" if has_manual_values(row) else "pending_blank_manual_entry")
        log_rows.append(
            {
                "route22_id": f"R22-{index:03d}",
                "route21_id": row.get("route21_id", ""),
                "route20_id": row.get("route20_id", ""),
                "route19_id": row.get("route19_id", ""),
                "route18_id": row.get("route18_id", ""),
                "route17_id": row.get("route17_id", ""),
                "checklist_id": row.get("checklist_id", ""),
                "packet_id": row.get("packet_id", ""),
                "manual_review_id": row.get("manual_review_id", ""),
                "crop_id": row.get("crop_id", ""),
                "folio": row.get("folio", ""),
                "source_image": row.get("source_image", ""),
                "crop_svg": row.get("crop_svg", ""),
                "review_region": row.get("review_region", ""),
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
                "validation_status": status,
                "validation_errors": "|".join(errors),
                "apply_status": apply_status_for(status),
                "next_action": next_action_for(status),
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return log_rows


def entry_indexes(rows: list[dict[str, str]]) -> tuple[dict[str, dict[str, str]], dict[str, dict[str, str]]]:
    valid_rows = [row for row in rows if validation_status(row) == "valid_manual_entry"]
    by_route19 = {row.get("route19_id", ""): row for row in valid_rows if row.get("route19_id", "")}
    by_checklist = {row.get("checklist_id", ""): row for row in valid_rows if row.get("checklist_id", "")}
    return by_route19, by_checklist


def apply_valid_entries_to_package(
    package_rows: list[dict[str, str]],
    entry_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    by_route19, by_checklist = entry_indexes(entry_rows)
    updated: list[dict[str, str]] = []
    for package in package_rows:
        new_row = dict(package)
        entry = by_route19.get(package.get("route19_id", "")) or by_checklist.get(package.get("checklist_id", ""))
        if entry:
            for field in MANUAL_FIELDS:
                value = entry.get(field, "").strip()
                if value:
                    new_row[field] = value
        updated.append(new_row)
    return updated


def summarize_validation_log(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "validation_status": Counter(row.get("validation_status", "") for row in rows),
        "apply_status": Counter(row.get("apply_status", "") for row in rows),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
        "target_type": Counter(row.get("target_type", "") for row in rows),
    }


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


def render_log_section(row: dict[str, str]) -> str:
    lines = [
        f"## {row['route22_id']} / {row.get('route21_id', '')} / {row.get('route19_id', '')}",
        "",
        f"- checklist: `{row.get('checklist_id', '')}`;",
        f"- validacao: `{row.get('validation_status', '')}`;",
        f"- erros: `{row.get('validation_errors', '')}`;",
        f"- aplicacao: `{row.get('apply_status', '')}`;",
        f"- proxima acao: `{row.get('next_action', '')}`;",
        f"- guarda: `{row.get('semantic_guardrail', '')}`;",
        "",
    ]
    return "\n".join(lines)


def write_report(
    path: Path,
    log_rows: list[dict[str, str]],
    entry_sheet_csv: Path,
    package_csv: Path,
    derived_package_csv: Path,
    validation_log_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_validation_log(log_rows)
    lines = [
        "# Rota 22: validacao da planilha visual R21",
        "",
        "Esta rota valida os campos preenchidos na planilha R21 e copia somente valores manuais validos para um pacote visual derivado. Campos vazios continuam pendentes.",
        "",
        f"Planilha R21: `{entry_sheet_csv}`.",
        f"Pacote visual fonte: `{package_csv}`.",
        f"Pacote visual derivado: `{derived_package_csv}`.",
        f"Log de validacao: `{validation_log_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- linhas validadas: {len(log_rows)};",
        f"- entradas validas: {summary['validation_status'].get('valid_manual_entry', 0)};",
        f"- entradas pendentes: {summary['validation_status'].get('pending_blank_manual_entry', 0)};",
        f"- entradas invalidas: {summary['validation_status'].get('invalid_manual_entry', 0)};",
        "- campos vazios nao apagam valores existentes;",
        "- guarda: `validated_values_are_manual_not_axis_meaning`.",
        "",
    ]
    lines.extend(render_counts("Status de validacao", summary["validation_status"]))
    lines.extend(render_counts("Status de aplicacao", summary["apply_status"]))
    lines.extend(render_counts("Prioridade", summary["priority_level"]))
    lines.extend(render_counts("Folios", summary["folio"]))
    lines.extend(
        [
            "## Log",
            "",
            "|rota22|rota21|rota19|checklist|prioridade|folio|status|aplicacao|erros|",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in log_rows:
        lines.append(
            f"|{row['route22_id']}|{row['route21_id']}|{row['route19_id']}|{row['checklist_id']}|{row['priority_level']}|{row['folio']}|{row['validation_status']}|{row['apply_status']}|{row['validation_errors']}|"
        )
    lines.append("")
    for row in log_rows:
        lines.append(render_log_section(row))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entry_sheet_csv", help="CSV from prepare_visual_decision_entry_sheet.py")
    parser.add_argument("direct_visual_package_csv", help="Route 19 direct visual package CSV")
    parser.add_argument(
        "--derived-package-csv",
        default=str(ROOT / "data" / "derived" / "direct_visual_package_after_entry_sheet_p0_p1_zl3b.csv"),
        help="Derived direct visual package after valid R21 entries",
    )
    parser.add_argument(
        "--validation-log-csv",
        default=str(ROOT / "data" / "derived" / "visual_decision_entry_validation_log_zl3b.csv"),
        help="Validation log CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "visual_decision_entry_validation_summary_zl3b.csv"),
        help="Validation summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_22_validacao_planilha_visual.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    entry_sheet_csv = Path(args.entry_sheet_csv)
    package_csv = Path(args.direct_visual_package_csv)
    entry_rows = read_csv(entry_sheet_csv)
    package_rows = read_csv(package_csv)
    log_rows = build_validation_log(entry_rows)
    summary = summarize_validation_log(log_rows)
    derived_package = apply_valid_entries_to_package(package_rows, entry_rows)
    package_fieldnames = read_fieldnames(package_csv)
    derived_package_path = Path(args.derived_package_csv)
    validation_log_path = Path(args.validation_log_csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_rows(derived_package_path, derived_package, package_fieldnames)
    write_rows(validation_log_path, log_rows, LOG_FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_report(md_path, log_rows, entry_sheet_csv, package_csv, derived_package_path, validation_log_path, summary_path)
    print(
        f"validation_rows={len(log_rows)} "
        f"valid={summary['validation_status'].get('valid_manual_entry', 0)} "
        f"pending={summary['validation_status'].get('pending_blank_manual_entry', 0)} "
        f"invalid={summary['validation_status'].get('invalid_manual_entry', 0)}"
    )
    print(f"derived_package_csv={derived_package_path}")
    print(f"validation_log_csv={validation_log_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
