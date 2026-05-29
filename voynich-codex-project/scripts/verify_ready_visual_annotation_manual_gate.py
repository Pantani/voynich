#!/usr/bin/env python3
"""Verify the manual gate for focused route 32 visual annotations."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "manual_visual_gate_not_evidence"
HTML_GUARDRAIL = "focused_visual_annotation_html_not_evidence"
ALLOWED_MANUAL_STATUS = {"annotated", "not_visible", "uncertain"}
ALLOWED_MANUAL_STATUS_TEXT = "annotated/not_visible/uncertain"

FIELDNAMES = [
    "route34_id",
    "route32_id",
    "route33_id",
    "route31_id",
    "route28_id",
    "folio",
    "priority_level",
    "locus_kind",
    "html_card_check",
    "allowed_values_check",
    "manual_entry_status",
    "manual_notes_status",
    "r33_apply_status",
    "r33_package_action",
    "gate_status",
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


def markdown_cell(value: str) -> str:
    return value.replace("|", "<br>")


def html_card_check(entry: dict[str, str], html_text: str) -> str:
    required = [entry.get("route32_id", ""), entry.get("route28_id", ""), entry.get("folio", "")]
    return "present" if all(value and value in html_text for value in required) else "missing"


def allowed_values_check(entry: dict[str, str], html_text: str) -> str:
    allowed = entry.get("allowed_manual_annotation_status", ALLOWED_MANUAL_STATUS_TEXT)
    return "present" if allowed in html_text and HTML_GUARDRAIL in html_text else "missing"


def manual_entry_status(status: str, notes: str) -> str:
    if not status and not notes:
        return "pending_blank_manual_annotation"
    if status not in ALLOWED_MANUAL_STATUS:
        return "invalid_manual_annotation_entry"
    if not notes:
        return "invalid_manual_annotation_entry"
    return "manual_annotation_filled"


def manual_notes_status(notes: str) -> str:
    return "notes_present" if notes else "notes_blank"


def gate_status(
    status: str,
    notes: str,
    card_check: str,
    apply_status: str,
) -> tuple[str, str]:
    del apply_status
    if card_check != "present":
        return "blocked_missing_html_card", "regenerate_r32_html_before_manual_fill"
    entry_status = manual_entry_status(status, notes)
    if entry_status == "pending_blank_manual_annotation":
        return (
            "blocked_pending_manual_annotation",
            "fill_r32_entry_sheet_using_html_then_rerun_r33_r31",
        )
    if entry_status == "invalid_manual_annotation_entry":
        return (
            "blocked_invalid_manual_annotation",
            "fix_r32_entry_sheet_values_then_rerun_r33_r31",
        )
    return "ready_to_rerun_r33_r31", "rerun_r33_then_r31_validation"


def build_manual_gate_rows(
    entry_rows: list[dict[str, str]],
    application_log_rows: list[dict[str, str]],
    html_text: str,
) -> list[dict[str, str]]:
    log_by_route32 = {row.get("route32_id", ""): row for row in application_log_rows}
    rows: list[dict[str, str]] = []
    for entry in entry_rows:
        route32_id = entry.get("route32_id", "")
        log = log_by_route32.get(route32_id, {})
        card_check = html_card_check(entry, html_text)
        values_check = allowed_values_check(entry, html_text)
        status = entry.get("manual_annotation_status", "")
        notes = entry.get("manual_visual_notes", "")
        if values_check != "present" and card_check == "present":
            gate, action = "blocked_missing_allowed_values", "regenerate_r32_html_before_manual_fill"
        else:
            gate, action = gate_status(status, notes, card_check, log.get("apply_status", ""))
        rows.append(
            {
                "route34_id": f"R34-{len(rows) + 1:03d}",
                "route32_id": route32_id,
                "route33_id": log.get("route33_id", ""),
                "route31_id": entry.get("route31_id", ""),
                "route28_id": entry.get("route28_id", ""),
                "folio": entry.get("folio", ""),
                "priority_level": entry.get("priority_level", ""),
                "locus_kind": entry.get("locus_kind", ""),
                "html_card_check": card_check,
                "allowed_values_check": values_check,
                "manual_entry_status": manual_entry_status(status, notes),
                "manual_notes_status": manual_notes_status(notes),
                "r33_apply_status": log.get("apply_status", ""),
                "r33_package_action": log.get("package_action", ""),
                "gate_status": gate,
                "next_action": action,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def summarize_manual_gate_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "gate_status": Counter(row.get("gate_status", "") for row in rows),
        "next_action": Counter(row.get("next_action", "") for row in rows),
        "manual_entry_status": Counter(row.get("manual_entry_status", "") for row in rows),
        "html_card_check": Counter(row.get("html_card_check", "") for row in rows),
        "allowed_values_check": Counter(row.get("allowed_values_check", "") for row in rows),
        "r33_apply_status": Counter(row.get("r33_apply_status", "") for row in rows),
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
    rows: list[dict[str, str]],
    entry_csv: Path,
    html_path: Path,
    application_log_csv: Path,
    gate_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_manual_gate_rows(rows)
    lines = [
        "# Rota 34: gate manual de anotacao visual R32",
        "",
        "Esta rota verifica se a planilha R32 ja recebeu anotacao humana suficiente para reexecutar R33 e R31. Ela nao interpreta imagens nem cria evidencia visual.",
        "",
        f"Planilha R32: `{entry_csv}`.",
        f"HTML R32: `{html_path}`.",
        f"Log R33: `{application_log_csv}`.",
        f"Gate CSV: `{gate_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens verificados: {len(rows)};",
        f"- bloqueados por anotacao manual pendente: {summary['gate_status'].get('blocked_pending_manual_annotation', 0)};",
        f"- prontos para reexecutar R33/R31: {summary['gate_status'].get('ready_to_rerun_r33_r31', 0)};",
        f"- bloqueados por valores invalidos: {summary['gate_status'].get('blocked_invalid_manual_annotation', 0)};",
        f"- cartoes HTML presentes: {summary['html_card_check'].get('present', 0)};",
        f"- valores permitidos presentes no HTML: {summary['allowed_values_check'].get('present', 0)};",
        "- guarda: `manual_visual_gate_not_evidence`.",
        "",
    ]
    lines.extend(render_counts("Status do gate", summary["gate_status"]))
    lines.extend(render_counts("Proxima acao", summary["next_action"]))
    lines.extend(render_counts("Status manual", summary["manual_entry_status"]))
    lines.extend(render_counts("HTML", summary["html_card_check"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota34|rota32|rota33|rota28|folio|status manual|gate|proxima acao|",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{markdown_cell(row['route34_id'])}|{markdown_cell(row['route32_id'])}|{markdown_cell(row['route33_id'])}|{markdown_cell(row['route28_id'])}|{markdown_cell(row['folio'])}|{markdown_cell(row['manual_entry_status'])}|{markdown_cell(row['gate_status'])}|{markdown_cell(row['next_action'])}|"
        )
    lines.extend(
        [
            "",
            "## Leitura",
            "",
            "O material operacional esta pronto, mas o gate permanece bloqueado por falta de anotacao visual humana. O proximo passo nao e inferir: e preencher `manual_annotation_status` e `manual_visual_notes` na planilha R32 usando o HTML R32.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entry_csv", help="Route 32 focused manual entry CSV")
    parser.add_argument("html", help="Route 32 focused HTML")
    parser.add_argument("application_log_csv", help="Route 33 application log CSV")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_manual_gate_zl3b.csv"),
        help="Manual gate CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_manual_gate_summary_zl3b.csv"),
        help="Manual gate summary output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_34_gate_manual_anotacao_visual_r32.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    entry_csv = Path(args.entry_csv)
    html_path = Path(args.html)
    application_log_csv = Path(args.application_log_csv)
    rows = build_manual_gate_rows(
        read_csv(entry_csv),
        read_csv(application_log_csv),
        html_path.read_text(encoding="utf-8"),
    )
    summary = summarize_manual_gate_rows(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, rows, FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_report(md_path, rows, entry_csv, html_path, application_log_csv, csv_path, summary_path)
    print(
        f"gate_items={len(rows)} "
        f"blocked_pending={summary['gate_status'].get('blocked_pending_manual_annotation', 0)} "
        f"ready={summary['gate_status'].get('ready_to_rerun_r33_r31', 0)} "
        f"html_present={summary['html_card_check'].get('present', 0)}"
    )
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
