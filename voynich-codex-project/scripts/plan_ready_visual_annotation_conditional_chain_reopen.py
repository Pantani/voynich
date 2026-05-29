#!/usr/bin/env python3
"""Plan conditional R34/R35/R33/R31 reopening after route 39 audit."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "conditional_chain_reopen_plan_not_visual_evidence"
CHAIN_ORDER = "R34>R35>R33>R31"

FIELDNAMES = [
    "route40_id",
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
    "fill_execution_status",
    "chain_release_status",
    "reopen_plan_status",
    "chain_order",
    "planned_chain_action",
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


def chain_reopen_plan_status(
    fill_execution_status: str,
    chain_release_status: str,
    audit_next_action: str,
) -> tuple[str, str, str]:
    if fill_execution_status == "ready_for_revalidation_chain_reopen" and chain_release_status == "ready_to_reopen_chain":
        return (
            "ready_to_run_revalidation_chain",
            "run_R34_R35_R33_R31",
            "execute_chain_and_validate_outputs",
        )
    if chain_release_status == "blocked_invalid_manual_entry":
        return (
            "blocked_invalid_manual_entry",
            "do_not_run_revalidation_chain",
            audit_next_action,
        )
    if chain_release_status == "blocked_until_r36_r37_refresh":
        return (
            "blocked_pending_protocol_refresh",
            "do_not_run_revalidation_chain",
            "rerun_r36_r37_r39_before_chain",
        )
    if chain_release_status == "blocked_no_manual_entry":
        return (
            "blocked_waiting_human_entry",
            "do_not_run_revalidation_chain",
            "fill_r32_manual_fields_then_rerun_r36_r37_r39",
        )
    return (
        "blocked_unknown_r39_state",
        "do_not_run_revalidation_chain",
        "inspect_r39_audit_state_before_chain",
    )


def build_conditional_reopen_rows(audit_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for audit in audit_rows:
        plan_status, planned_action, next_action = chain_reopen_plan_status(
            audit.get("fill_execution_status", ""),
            audit.get("chain_release_status", ""),
            audit.get("next_action", ""),
        )
        rows.append(
            {
                "route40_id": f"R40-{len(rows) + 1:03d}",
                "route39_id": audit.get("route39_id", ""),
                "route38_id": audit.get("route38_id", ""),
                "route37_id": audit.get("route37_id", ""),
                "route36_id": audit.get("route36_id", ""),
                "route32_id": audit.get("route32_id", ""),
                "route31_id": audit.get("route31_id", ""),
                "route28_id": audit.get("route28_id", ""),
                "folio": audit.get("folio", ""),
                "priority_level": audit.get("priority_level", ""),
                "locus_kind": audit.get("locus_kind", ""),
                "fill_execution_status": audit.get("fill_execution_status", ""),
                "chain_release_status": audit.get("chain_release_status", ""),
                "reopen_plan_status": plan_status,
                "chain_order": CHAIN_ORDER,
                "planned_chain_action": planned_action,
                "next_action": next_action,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def summarize_conditional_reopen_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "reopen_plan_status": Counter(row.get("reopen_plan_status", "") for row in rows),
        "planned_chain_action": Counter(row.get("planned_chain_action", "") for row in rows),
        "next_action": Counter(row.get("next_action", "") for row in rows),
        "fill_execution_status": Counter(row.get("fill_execution_status", "") for row in rows),
        "chain_release_status": Counter(row.get("chain_release_status", "") for row in rows),
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
    audit_csv: Path,
    plan_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_conditional_reopen_rows(rows)
    lines = [
        "# Rota 40: plano condicional de reabertura da cadeia R34/R35/R33/R31",
        "",
        "Esta rota decide se a cadeia de revalidacao pode ser reaberta a partir da auditoria R39. Ela nao preenche a R32, nao interpreta imagens e nao executa a cadeia quando a R39 permanece bloqueada.",
        "",
        f"Auditoria R39: `{audit_csv}`.",
        f"Plano R40: `{plan_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        f"Ordem da cadeia: `{CHAIN_ORDER}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens planejados: {len(rows)};",
        f"- bloqueados aguardando entrada humana: {summary['reopen_plan_status'].get('blocked_waiting_human_entry', 0)};",
        f"- bloqueados aguardando refresh R36/R37/R39: {summary['reopen_plan_status'].get('blocked_pending_protocol_refresh', 0)};",
        f"- prontos para rodar cadeia: {summary['reopen_plan_status'].get('ready_to_run_revalidation_chain', 0)};",
        f"- entradas invalidas: {summary['reopen_plan_status'].get('blocked_invalid_manual_entry', 0)};",
        "- guarda: `conditional_chain_reopen_plan_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Status do plano", summary["reopen_plan_status"]))
    lines.extend(render_counts("Acao de cadeia planejada", summary["planned_chain_action"]))
    lines.extend(render_counts("Proxima acao", summary["next_action"]))
    lines.extend(render_counts("Status de execucao R39", summary["fill_execution_status"]))
    lines.extend(render_counts("Liberacao R39", summary["chain_release_status"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota40|rota39|rota32|folio|status do plano|acao da cadeia|proxima acao|",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{markdown_cell(row['route40_id'])}|{markdown_cell(row['route39_id'])}|{markdown_cell(row['route32_id'])}|{markdown_cell(row['folio'])}|{markdown_cell(row['reopen_plan_status'])}|{markdown_cell(row['planned_chain_action'])}|{markdown_cell(row['next_action'])}|"
        )
    lines.extend(
        [
            "",
            "## Regra de liberacao",
            "",
            "Executar `R34>R35>R33>R31` somente quando `reopen_plan_status=ready_to_run_revalidation_chain`. Qualquer outro status preserva o bloqueio manual.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audit_csv", help="Route 39 manual fill execution audit CSV")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_conditional_chain_reopen_plan_zl3b.csv"),
        help="Route 40 conditional chain reopen plan CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_conditional_chain_reopen_summary_zl3b.csv"),
        help="Route 40 summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_40_plano_condicional_reabertura_cadeia_r39.md"),
        help="Route 40 Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    audit_csv = Path(args.audit_csv)
    rows = build_conditional_reopen_rows(read_csv(audit_csv))
    summary = summarize_conditional_reopen_rows(rows)
    plan_csv = Path(args.csv)
    summary_csv = Path(args.summary_csv)
    md = Path(args.md)
    write_csv(plan_csv, rows, FIELDNAMES)
    write_summary_csv(summary_csv, summary)
    write_report(md, rows, audit_csv, plan_csv, summary_csv)
    print(
        f"planned_items={len(rows)} "
        f"blocked_waiting_human={summary['reopen_plan_status'].get('blocked_waiting_human_entry', 0)} "
        f"ready_to_run_chain={summary['reopen_plan_status'].get('ready_to_run_revalidation_chain', 0)} "
        f"invalid={summary['reopen_plan_status'].get('blocked_invalid_manual_entry', 0)}"
    )
    print(f"csv={plan_csv.resolve()}")
    print(f"summary_csv={summary_csv.resolve()}")
    print(f"md={md.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
