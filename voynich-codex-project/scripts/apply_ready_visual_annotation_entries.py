#!/usr/bin/env python3
"""Apply explicit route 32 manual visual entries to a derived route 28 package."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "ready_visual_entry_application_not_visual_evidence"
ALLOWED_MANUAL_STATUS = {"annotated", "not_visible", "uncertain"}

LOG_FIELDNAMES = [
    "route33_id",
    "route32_id",
    "route31_id",
    "route28_id",
    "route27_id",
    "folio",
    "locus_kind",
    "priority_level",
    "old_manual_annotation_status",
    "new_manual_annotation_status",
    "old_manual_visual_notes",
    "new_manual_visual_notes",
    "manual_entry_valid",
    "validation_status",
    "validation_reason",
    "apply_status",
    "package_action",
    "semantic_guardrail",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def markdown_cell(value: str) -> str:
    return value.replace("|", "<br>")


def validate_entry_fields(status: str, notes: str) -> tuple[str, str, str, str, str]:
    if not status and not notes:
        return (
            "no",
            "pending_blank_manual_annotation",
            "manual_fields_blank",
            "skipped_blank_manual_annotation",
            "no_package_change",
        )
    if not status:
        return (
            "no",
            "invalid_manual_annotation",
            "manual_annotation_status_required_for_notes",
            "skipped_invalid_manual_annotation",
            "no_package_change",
        )
    if status not in ALLOWED_MANUAL_STATUS:
        return (
            "no",
            "invalid_manual_annotation",
            "manual_annotation_status_not_allowed",
            "skipped_invalid_manual_annotation",
            "no_package_change",
        )
    if not notes:
        return (
            "no",
            "invalid_manual_annotation",
            "manual_visual_notes_required_for_filled_status",
            "skipped_invalid_manual_annotation",
            "no_package_change",
        )
    return (
        "yes",
        "valid_manual_annotation",
        "manual_annotation_fields_valid",
        "applied_manual_annotation_to_derived_package",
        "updated_derived_package_row",
    )


def log_row(
    route33_id: str,
    entry: dict[str, str],
    package: dict[str, str] | None,
    valid: str,
    validation_status: str,
    reason: str,
    apply_status: str,
    package_action: str,
    new_status: str = "",
    new_notes: str = "",
) -> dict[str, str]:
    package = package or {}
    old_status = package.get("manual_annotation_status", "")
    old_notes = package.get("manual_visual_notes", "")
    return {
        "route33_id": route33_id,
        "route32_id": entry.get("route32_id", ""),
        "route31_id": entry.get("route31_id", ""),
        "route28_id": entry.get("route28_id", ""),
        "route27_id": package.get("route27_id", ""),
        "folio": package.get("folio", ""),
        "locus_kind": package.get("locus_kind", ""),
        "priority_level": package.get("priority_level", ""),
        "old_manual_annotation_status": old_status,
        "new_manual_annotation_status": new_status if package_action == "updated_derived_package_row" else old_status,
        "old_manual_visual_notes": old_notes,
        "new_manual_visual_notes": new_notes if package_action == "updated_derived_package_row" else old_notes,
        "manual_entry_valid": valid,
        "validation_status": validation_status,
        "validation_reason": reason,
        "apply_status": apply_status,
        "package_action": package_action,
        "semantic_guardrail": GUARDRAIL,
    }


def apply_ready_entry_rows(
    entry_rows: list[dict[str, str]],
    package_rows: list[dict[str, str]],
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    updated_package_rows = [dict(row) for row in package_rows]
    package_by_route28 = {row.get("route28_id", ""): row for row in updated_package_rows}
    log_rows: list[dict[str, str]] = []
    for entry in entry_rows:
        route33_id = f"R33-{len(log_rows) + 1:03d}"
        route28_id = entry.get("route28_id", "")
        package = package_by_route28.get(route28_id)
        if not package:
            log_rows.append(
                log_row(
                    route33_id,
                    entry,
                    None,
                    "no",
                    "invalid_manual_annotation",
                    "package_item_missing_for_route32_entry",
                    "skipped_missing_package_item",
                    "no_package_change",
                )
            )
            continue
        if package.get("package_status", "") != "ready_for_manual_visual_annotation":
            log_rows.append(
                log_row(
                    route33_id,
                    entry,
                    package,
                    "no",
                    "invalid_manual_annotation",
                    "package_item_not_ready_for_manual_visual_annotation",
                    "skipped_not_ready_package_item",
                    "no_package_change",
                )
            )
            continue
        status = entry.get("manual_annotation_status", "")
        notes = entry.get("manual_visual_notes", "")
        valid, validation_status, reason, apply_status, package_action = validate_entry_fields(status, notes)
        if valid == "yes":
            package["manual_annotation_status"] = status
            package["manual_visual_notes"] = notes
        log_rows.append(
            log_row(
                route33_id,
                entry,
                package,
                valid,
                validation_status,
                reason,
                apply_status,
                package_action,
                status,
                notes,
            )
        )
    return updated_package_rows, log_rows


def summarize_application_log_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "validation_status": Counter(row.get("validation_status", "") for row in rows),
        "apply_status": Counter(row.get("apply_status", "") for row in rows),
        "package_action": Counter(row.get("package_action", "") for row in rows),
        "manual_entry_valid": Counter(row.get("manual_entry_valid", "") for row in rows),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "locus_kind": Counter(row.get("locus_kind", "") for row in rows),
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
        lines.append(f"|{markdown_cell(key)}|{value}|")
    lines.append("")
    return lines


def write_report(
    path: Path,
    log_rows: list[dict[str, str]],
    entry_csv: Path,
    package_csv: Path,
    derived_package_csv: Path,
    log_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_application_log_rows(log_rows)
    lines = [
        "# Rota 33: aplicacao das entradas visuais R32",
        "",
        "Esta rota aplica somente valores manuais explicitos da planilha R32 a uma copia derivada do pacote R28. Campos vazios, invalidos ou itens fora do alvo nao alteram o pacote.",
        "",
        f"Planilha R32: `{entry_csv}`.",
        f"Pacote R28 original: `{package_csv}`.",
        f"Pacote R28 derivado: `{derived_package_csv}`.",
        f"Log de aplicacao: `{log_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- entradas R32 avaliadas: {len(log_rows)};",
        f"- pendentes vazias: {summary['validation_status'].get('pending_blank_manual_annotation', 0)};",
        f"- validas: {summary['validation_status'].get('valid_manual_annotation', 0)};",
        f"- invalidas: {summary['validation_status'].get('invalid_manual_annotation', 0)};",
        f"- linhas atualizadas no pacote derivado: {summary['package_action'].get('updated_derived_package_row', 0)};",
        "- pacote R28 original nao foi alterado;",
        "- guarda: `ready_visual_entry_application_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Status de validacao", summary["validation_status"]))
    lines.extend(render_counts("Aplicacao", summary["apply_status"]))
    lines.extend(render_counts("Acao no pacote", summary["package_action"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota33|rota32|rota28|status|aplicacao|acao|motivo|",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in log_rows:
        lines.append(
            f"|{markdown_cell(row['route33_id'])}|{markdown_cell(row['route32_id'])}|{markdown_cell(row['route28_id'])}|{markdown_cell(row['validation_status'])}|{markdown_cell(row['apply_status'])}|{markdown_cell(row['package_action'])}|{markdown_cell(row['validation_reason'])}|"
        )
    lines.extend(
        [
            "",
            "## Leitura",
            "",
            "A infraestrutura de aplicacao esta pronta. Como a planilha R32 ainda esta vazia, o pacote derivado preserva os campos manuais em branco e a Rota 31 continuara sem anotacoes derivadas ate existir preenchimento humano.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entry_csv", help="CSV generated by prepare_ready_visual_annotation_html.py")
    parser.add_argument("annotation_package_csv", help="Original route 28 package CSV")
    parser.add_argument(
        "--derived-package-csv",
        default=str(ROOT / "data" / "derived" / "exact_form_visual_annotation_package_after_ready_entries_zl3b.csv"),
        help="Derived route 28 package output",
    )
    parser.add_argument(
        "--log-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_entry_application_log_zl3b.csv"),
        help="Application log output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_entry_application_summary_zl3b.csv"),
        help="Application summary output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_33_aplicacao_entradas_visuais_r32.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    entry_csv = Path(args.entry_csv)
    package_csv = Path(args.annotation_package_csv)
    package_rows = read_csv(package_csv)
    entry_rows = read_csv(entry_csv)
    updated_package_rows, log_rows = apply_ready_entry_rows(entry_rows, package_rows)
    summary = summarize_application_log_rows(log_rows)
    package_fieldnames = list(package_rows[0].keys()) if package_rows else []
    derived_package_path = Path(args.derived_package_csv)
    log_path = Path(args.log_csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(derived_package_path, updated_package_rows, package_fieldnames)
    write_csv(log_path, log_rows, LOG_FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_report(md_path, log_rows, entry_csv, package_csv, derived_package_path, log_path, summary_path)
    print(
        f"entry_rows={len(log_rows)} "
        f"blank={summary['validation_status'].get('pending_blank_manual_annotation', 0)} "
        f"valid={summary['validation_status'].get('valid_manual_annotation', 0)} "
        f"updated={summary['package_action'].get('updated_derived_package_row', 0)}"
    )
    print(f"derived_package_csv={derived_package_path}")
    print(f"log_csv={log_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
