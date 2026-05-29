#!/usr/bin/env python3
"""Prepare a manual work order to fill route 32 and reopen the revalidation chain."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "manual_reopen_work_order_not_visual_evidence"
FIELDS_TO_FILL = "manual_annotation_status manual_visual_notes"
ALLOWED_MANUAL_STATUS_TEXT = "annotated/not_visible/uncertain"

FIELDNAMES = [
    "route38_id",
    "route37_id",
    "route36_id",
    "route35_id",
    "route34_id",
    "route32_id",
    "route31_id",
    "route28_id",
    "folio",
    "priority_level",
    "locus_kind",
    "image_url",
    "commons_page",
    "html_reference",
    "fields_to_fill",
    "allowed_manual_annotation_status",
    "manual_annotation_status",
    "manual_visual_notes",
    "r36_manual_fill_status",
    "r37_status",
    "work_order_status",
    "chain_reopen_action",
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


def work_order_status(
    manual_annotation_status: str,
    manual_visual_notes: str,
    manual_fill_status: str,
    r37_status: str,
) -> tuple[str, str, str]:
    if manual_fill_status == "human_entry_present_ready_for_gate_rerun" and r37_status == "ready_for_revalidation_chain":
        return (
            "ready_to_reopen_revalidation_chain",
            "reopen_chain_after_r36_r37_refresh",
            "rerun_r36_r37_r34_r35_r33_r31",
        )
    if manual_fill_status == "invalid_manual_entry_needs_correction" or r37_status == "blocked_invalid_manual_entries":
        return (
            "blocked_by_invalid_manual_entry",
            "do_not_reopen_chain_until_r32_corrected",
            "fix_r32_entry_then_rerun_r36",
        )
    if not manual_annotation_status and not manual_visual_notes:
        return (
            "manual_fill_required",
            "do_not_reopen_chain_until_r32_filled",
            "fill_manual_annotation_status_and_notes_in_r32",
        )
    return (
        "blocked_by_protocol_mismatch",
        "do_not_reopen_chain_until_protocol_refreshed",
        "rerun_r36_then_r37_before_chain",
    )


def build_reopen_work_order_rows(
    entry_rows: list[dict[str, str]],
    protocol_rows: list[dict[str, str]],
    chain_rows: list[dict[str, str]],
    html_reference: str,
) -> list[dict[str, str]]:
    protocol_by_route32 = {row.get("route32_id", ""): row for row in protocol_rows}
    chain_by_route32 = {row.get("route32_id", ""): row for row in chain_rows}
    rows: list[dict[str, str]] = []
    for entry in entry_rows:
        route32_id = entry.get("route32_id", "")
        protocol = protocol_by_route32.get(route32_id, {})
        chain = chain_by_route32.get(route32_id, {})
        status, reopen_action, next_action = work_order_status(
            entry.get("manual_annotation_status", ""),
            entry.get("manual_visual_notes", ""),
            protocol.get("manual_fill_status", ""),
            chain.get("r37_status", ""),
        )
        rows.append(
            {
                "route38_id": f"R38-{len(rows) + 1:03d}",
                "route37_id": chain.get("route37_id", ""),
                "route36_id": protocol.get("route36_id", ""),
                "route35_id": protocol.get("route35_id", ""),
                "route34_id": protocol.get("route34_id", ""),
                "route32_id": route32_id,
                "route31_id": entry.get("route31_id", ""),
                "route28_id": entry.get("route28_id", ""),
                "folio": entry.get("folio", ""),
                "priority_level": entry.get("priority_level", ""),
                "locus_kind": entry.get("locus_kind", ""),
                "image_url": entry.get("image_url", ""),
                "commons_page": entry.get("commons_page", ""),
                "html_reference": html_reference,
                "fields_to_fill": FIELDS_TO_FILL,
                "allowed_manual_annotation_status": entry.get(
                    "allowed_manual_annotation_status",
                    ALLOWED_MANUAL_STATUS_TEXT,
                ),
                "manual_annotation_status": entry.get("manual_annotation_status", ""),
                "manual_visual_notes": entry.get("manual_visual_notes", ""),
                "r36_manual_fill_status": protocol.get("manual_fill_status", ""),
                "r37_status": chain.get("r37_status", ""),
                "work_order_status": status,
                "chain_reopen_action": reopen_action,
                "next_action": next_action,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def summarize_reopen_work_order_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "work_order_status": Counter(row.get("work_order_status", "") for row in rows),
        "chain_reopen_action": Counter(row.get("chain_reopen_action", "") for row in rows),
        "next_action": Counter(row.get("next_action", "") for row in rows),
        "r36_manual_fill_status": Counter(row.get("r36_manual_fill_status", "") for row in rows),
        "r37_status": Counter(row.get("r37_status", "") for row in rows),
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
    protocol_csv: Path,
    chain_csv: Path,
    html_reference: str,
    work_order_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_reopen_work_order_rows(rows)
    lines = [
        "# Rota 38: ordem de trabalho para preencher R32 e reabrir cadeia",
        "",
        "Esta rota organiza o preenchimento humano da planilha R32 para reabrir a cadeia R34/R35/R33/R31. Ela nao grava decisoes nem interpreta imagem automaticamente.",
        "",
        f"Planilha R32: `{entry_csv}`.",
        f"Protocolo R36: `{protocol_csv}`.",
        f"Plano R37: `{chain_csv}`.",
        f"HTML de apoio: `{html_reference}`.",
        f"Ordem de trabalho R38: `{work_order_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens na ordem de trabalho: {len(rows)};",
        f"- exigem preenchimento manual: {summary['work_order_status'].get('manual_fill_required', 0)};",
        f"- prontos para reabrir cadeia: {summary['work_order_status'].get('ready_to_reopen_revalidation_chain', 0)};",
        f"- bloqueados por entrada invalida: {summary['work_order_status'].get('blocked_by_invalid_manual_entry', 0)};",
        "- planilha R32 original preservada;",
        "- guarda: `manual_reopen_work_order_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Status da ordem", summary["work_order_status"]))
    lines.extend(render_counts("Acao de reabertura", summary["chain_reopen_action"]))
    lines.extend(render_counts("Proxima acao", summary["next_action"]))
    lines.extend(render_counts("Status R36", summary["r36_manual_fill_status"]))
    lines.extend(render_counts("Status R37", summary["r37_status"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota38|rota37|rota36|rota32|folio|campos|status|proxima acao|",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{markdown_cell(row['route38_id'])}|{markdown_cell(row['route37_id'])}|{markdown_cell(row['route36_id'])}|{markdown_cell(row['route32_id'])}|{markdown_cell(row['folio'])}|{markdown_cell(row['fields_to_fill'])}|{markdown_cell(row['work_order_status'])}|{markdown_cell(row['next_action'])}|"
        )
    lines.extend(
        [
            "",
            "## Instrucao manual",
            "",
            "Para cada linha, abrir o HTML R32, verificar a imagem fonte e preencher na planilha R32 somente `manual_annotation_status` e `manual_visual_notes`. Valores permitidos: `annotated`, `not_visible`, `uncertain`. Depois, reexecutar R36 e R37 antes de reabrir R34/R35/R33/R31.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entry_csv", help="Route 32 focused manual entry CSV")
    parser.add_argument("protocol_csv", help="Route 36 manual fill protocol CSV")
    parser.add_argument("chain_csv", help="Route 37 revalidation chain plan CSV")
    parser.add_argument("html_reference", help="Route 32 HTML path used by the human reviewer")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_manual_reopen_work_order_zl3b.csv"),
        help="Manual reopen work order CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_manual_reopen_work_order_summary_zl3b.csv"),
        help="Manual reopen work order summary output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_38_ordem_trabalho_preencher_r32_reabrir_cadeia.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    entry_csv = Path(args.entry_csv)
    protocol_csv = Path(args.protocol_csv)
    chain_csv = Path(args.chain_csv)
    html_reference = args.html_reference
    rows = build_reopen_work_order_rows(
        read_csv(entry_csv),
        read_csv(protocol_csv),
        read_csv(chain_csv),
        html_reference,
    )
    summary = summarize_reopen_work_order_rows(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, rows, FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_report(md_path, rows, entry_csv, protocol_csv, chain_csv, html_reference, csv_path, summary_path)
    print(
        f"work_order_items={len(rows)} "
        f"manual_required={summary['work_order_status'].get('manual_fill_required', 0)} "
        f"ready_reopen={summary['work_order_status'].get('ready_to_reopen_revalidation_chain', 0)} "
        f"invalid={summary['work_order_status'].get('blocked_by_invalid_manual_entry', 0)}"
    )
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
