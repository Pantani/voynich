#!/usr/bin/env python3
"""Audit route 39 manual fill execution without creating visual decisions."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "manual_fill_execution_audit_not_visual_evidence"
ALLOWED_MANUAL_STATUS = {"annotated", "not_visible", "uncertain"}

FIELDNAMES = [
    "route39_id",
    "route38_id",
    "route37_id",
    "route36_id",
    "route32_id",
    "route31_id",
    "route28_id",
    "folio",
    "priority_level",
    "locus_kind",
    "image_url",
    "commons_page",
    "html_reference",
    "allowed_manual_annotation_status",
    "manual_annotation_status",
    "manual_visual_notes",
    "work_order_status",
    "r36_manual_fill_status",
    "r37_status",
    "fill_execution_status",
    "chain_release_status",
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


def execution_status(
    manual_annotation_status: str,
    manual_visual_notes: str,
    manual_fill_status: str,
    r37_status: str,
) -> tuple[str, str, str]:
    has_status = bool(manual_annotation_status)
    has_notes = bool(manual_visual_notes)
    if not has_status and not has_notes:
        return (
            "manual_fill_not_executed",
            "blocked_no_manual_entry",
            "human_fill_r32_fields_from_r38_order",
        )
    if has_status != has_notes:
        return (
            "invalid_partial_manual_entry",
            "blocked_invalid_manual_entry",
            "complete_or_clear_r32_manual_fields_then_rerun_r36",
        )
    if manual_annotation_status not in ALLOWED_MANUAL_STATUS:
        return (
            "invalid_manual_annotation_status",
            "blocked_invalid_manual_entry",
            "fix_manual_annotation_status_then_rerun_r36",
        )
    if manual_fill_status == "human_entry_present_ready_for_gate_rerun" and r37_status == "ready_for_revalidation_chain":
        return (
            "ready_for_revalidation_chain_reopen",
            "ready_to_reopen_chain",
            "rerun_r34_r35_r33_r31",
        )
    return (
        "manual_entry_present_protocol_refresh_required",
        "blocked_until_r36_r37_refresh",
        "rerun_r36_r37_then_recompute_r39",
    )


def build_execution_audit_rows(
    entry_rows: list[dict[str, str]],
    work_order_rows: list[dict[str, str]],
    protocol_rows: list[dict[str, str]],
    chain_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    work_order_by_route32 = {row.get("route32_id", ""): row for row in work_order_rows}
    protocol_by_route32 = {row.get("route32_id", ""): row for row in protocol_rows}
    chain_by_route32 = {row.get("route32_id", ""): row for row in chain_rows}
    rows: list[dict[str, str]] = []
    for entry in entry_rows:
        route32_id = entry.get("route32_id", "")
        work_order = work_order_by_route32.get(route32_id, {})
        protocol = protocol_by_route32.get(route32_id, {})
        chain = chain_by_route32.get(route32_id, {})
        status = entry.get("manual_annotation_status", "")
        notes = entry.get("manual_visual_notes", "")
        fill_status, release_status, next_action = execution_status(
            status,
            notes,
            protocol.get("manual_fill_status", ""),
            chain.get("r37_status", ""),
        )
        rows.append(
            {
                "route39_id": f"R39-{len(rows) + 1:03d}",
                "route38_id": work_order.get("route38_id", ""),
                "route37_id": chain.get("route37_id", work_order.get("route37_id", "")),
                "route36_id": protocol.get("route36_id", work_order.get("route36_id", "")),
                "route32_id": route32_id,
                "route31_id": entry.get("route31_id", ""),
                "route28_id": entry.get("route28_id", ""),
                "folio": entry.get("folio", ""),
                "priority_level": entry.get("priority_level", ""),
                "locus_kind": entry.get("locus_kind", ""),
                "image_url": entry.get("image_url", ""),
                "commons_page": entry.get("commons_page", ""),
                "html_reference": work_order.get("html_reference", ""),
                "allowed_manual_annotation_status": entry.get("allowed_manual_annotation_status", ""),
                "manual_annotation_status": status,
                "manual_visual_notes": notes,
                "work_order_status": work_order.get("work_order_status", ""),
                "r36_manual_fill_status": protocol.get("manual_fill_status", ""),
                "r37_status": chain.get("r37_status", ""),
                "fill_execution_status": fill_status,
                "chain_release_status": release_status,
                "next_action": next_action,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def summarize_execution_audit_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "fill_execution_status": Counter(row.get("fill_execution_status", "") for row in rows),
        "chain_release_status": Counter(row.get("chain_release_status", "") for row in rows),
        "next_action": Counter(row.get("next_action", "") for row in rows),
        "work_order_status": Counter(row.get("work_order_status", "") for row in rows),
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
    work_order_csv: Path,
    protocol_csv: Path,
    chain_csv: Path,
    audit_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_execution_audit_rows(rows)
    lines = [
        "# Rota 39: auditoria de execucao do preenchimento humano R32",
        "",
        "Esta rota verifica se o preenchimento humano da planilha R32 foi executado. Ela nao grava decisoes, nao interpreta imagens e nao reabre a cadeia por inferencia.",
        "",
        f"Planilha R32: `{entry_csv}`.",
        f"Ordem R38: `{work_order_csv}`.",
        f"Protocolo R36: `{protocol_csv}`.",
        f"Plano R37: `{chain_csv}`.",
        f"Auditoria R39: `{audit_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens auditados: {len(rows)};",
        f"- preenchimento humano nao executado: {summary['fill_execution_status'].get('manual_fill_not_executed', 0)};",
        f"- entradas manuais presentes exigindo refresh R36/R37: {summary['fill_execution_status'].get('manual_entry_present_protocol_refresh_required', 0)};",
        f"- prontos para reabrir cadeia: {summary['fill_execution_status'].get('ready_for_revalidation_chain_reopen', 0)};",
        f"- entradas invalidas ou parciais: {summary['chain_release_status'].get('blocked_invalid_manual_entry', 0)};",
        "- planilha R32 original preservada;",
        "- guarda: `manual_fill_execution_audit_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Status de execucao", summary["fill_execution_status"]))
    lines.extend(render_counts("Status de liberacao da cadeia", summary["chain_release_status"]))
    lines.extend(render_counts("Proxima acao", summary["next_action"]))
    lines.extend(render_counts("Status R36", summary["r36_manual_fill_status"]))
    lines.extend(render_counts("Status R37", summary["r37_status"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota39|rota38|rota32|folio|execucao|liberacao|proxima acao|",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{markdown_cell(row['route39_id'])}|{markdown_cell(row['route38_id'])}|{markdown_cell(row['route32_id'])}|{markdown_cell(row['folio'])}|{markdown_cell(row['fill_execution_status'])}|{markdown_cell(row['chain_release_status'])}|{markdown_cell(row['next_action'])}|"
        )
    lines.extend(
        [
            "",
            "## Instrucao manual",
            "",
            "Enquanto `fill_execution_status=manual_fill_not_executed`, preencher manualmente na R32 somente `manual_annotation_status` e `manual_visual_notes` usando a ordem R38 e o HTML R32. Depois reexecutar R36, R37 e esta auditoria antes de rodar R34/R35/R33/R31.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entry_csv", help="Route 32 focused manual entry CSV")
    parser.add_argument("work_order_csv", help="Route 38 manual reopen work order CSV")
    parser.add_argument("protocol_csv", help="Route 36 manual fill protocol CSV")
    parser.add_argument("chain_csv", help="Route 37 revalidation chain plan CSV")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_manual_fill_execution_audit_zl3b.csv"),
        help="Route 39 audit CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_manual_fill_execution_audit_summary_zl3b.csv"),
        help="Route 39 summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_39_auditoria_execucao_preenchimento_humano_r32.md"),
        help="Route 39 Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    entry_csv = Path(args.entry_csv)
    work_order_csv = Path(args.work_order_csv)
    protocol_csv = Path(args.protocol_csv)
    chain_csv = Path(args.chain_csv)
    rows = build_execution_audit_rows(
        read_csv(entry_csv),
        read_csv(work_order_csv),
        read_csv(protocol_csv),
        read_csv(chain_csv),
    )
    summary = summarize_execution_audit_rows(rows)
    audit_csv = Path(args.csv)
    summary_csv = Path(args.summary_csv)
    md = Path(args.md)
    write_csv(audit_csv, rows, FIELDNAMES)
    write_summary_csv(summary_csv, summary)
    write_report(md, rows, entry_csv, work_order_csv, protocol_csv, chain_csv, audit_csv, summary_csv)
    print(
        f"audited_items={len(rows)} "
        f"not_executed={summary['fill_execution_status'].get('manual_fill_not_executed', 0)} "
        f"ready_to_reopen={summary['fill_execution_status'].get('ready_for_revalidation_chain_reopen', 0)} "
        f"invalid_or_partial={summary['chain_release_status'].get('blocked_invalid_manual_entry', 0)}"
    )
    print(f"csv={audit_csv.resolve()}")
    print(f"summary_csv={summary_csv.resolve()}")
    print(f"md={md.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
