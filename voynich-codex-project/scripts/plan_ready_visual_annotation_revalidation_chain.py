#!/usr/bin/env python3
"""Plan the route 34/35/33/31 revalidation chain after route 32 manual fill."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "revalidation_chain_not_visual_evidence"
CHAIN_ORDER = "R34>R35>R33>R31"

FIELDNAMES = [
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
    "r36_manual_fill_status",
    "r36_blocking_reason",
    "chain_order",
    "r37_status",
    "chain_action",
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


def chain_status(manual_fill_status: str) -> tuple[str, str, str]:
    if manual_fill_status == "human_entry_present_ready_for_gate_rerun":
        return (
            "ready_for_revalidation_chain",
            "run_r34_r35_r33_r31_in_order",
            "rerun_chain_and_review_r31_valid_annotations",
        )
    if manual_fill_status == "awaiting_human_visual_entry":
        return (
            "blocked_no_human_entries",
            "skip_r34_r35_r33_r31_until_manual_fill",
            "fill_r32_entry_sheet_then_rerun_r36",
        )
    if manual_fill_status == "invalid_manual_entry_needs_correction":
        return (
            "blocked_invalid_manual_entries",
            "skip_r34_r35_r33_r31_until_protocol_clean",
            "fix_r32_entries_then_rerun_r36",
        )
    return (
        "blocked_unknown_protocol_status",
        "skip_r34_r35_r33_r31_until_protocol_clean",
        "inspect_r36_protocol_then_rerun_r36",
    )


def build_revalidation_chain_rows(protocol_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in protocol_rows:
        status, chain_action, next_action = chain_status(row.get("manual_fill_status", ""))
        rows.append(
            {
                "route37_id": f"R37-{len(rows) + 1:03d}",
                "route36_id": row.get("route36_id", ""),
                "route35_id": row.get("route35_id", ""),
                "route34_id": row.get("route34_id", ""),
                "route32_id": row.get("route32_id", ""),
                "route31_id": row.get("route31_id", ""),
                "route28_id": row.get("route28_id", ""),
                "folio": row.get("folio", ""),
                "priority_level": row.get("priority_level", ""),
                "locus_kind": row.get("locus_kind", ""),
                "r36_manual_fill_status": row.get("manual_fill_status", ""),
                "r36_blocking_reason": row.get("blocking_reason", ""),
                "chain_order": CHAIN_ORDER,
                "r37_status": status,
                "chain_action": chain_action,
                "next_action": next_action,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def summarize_revalidation_chain_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "r37_status": Counter(row.get("r37_status", "") for row in rows),
        "chain_action": Counter(row.get("chain_action", "") for row in rows),
        "next_action": Counter(row.get("next_action", "") for row in rows),
        "r36_manual_fill_status": Counter(row.get("r36_manual_fill_status", "") for row in rows),
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
    protocol_csv: Path,
    chain_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_revalidation_chain_rows(rows)
    lines = [
        "# Rota 37: plano de revalidacao R34/R35/R33/R31",
        "",
        "Esta rota verifica se o protocolo R36 ja permite reexecutar a cadeia R34/R35/R33/R31. Ela nao roda a cadeia quando nao ha entrada humana pronta.",
        "",
        f"Protocolo R36: `{protocol_csv}`.",
        f"Plano R37: `{chain_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens avaliados: {len(rows)};",
        f"- bloqueados sem entrada humana: {summary['r37_status'].get('blocked_no_human_entries', 0)};",
        f"- prontos para cadeia de revalidacao: {summary['r37_status'].get('ready_for_revalidation_chain', 0)};",
        f"- bloqueados por entradas invalidas: {summary['r37_status'].get('blocked_invalid_manual_entries', 0)};",
        f"- execucoes da cadeia planejadas agora: {summary['chain_action'].get('run_r34_r35_r33_r31_in_order', 0)};",
        "- ordem de cadeia: `R34>R35>R33>R31`;",
        "- guarda: `revalidation_chain_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Status R37", summary["r37_status"]))
    lines.extend(render_counts("Acao da cadeia", summary["chain_action"]))
    lines.extend(render_counts("Proxima acao", summary["next_action"]))
    lines.extend(render_counts("Status R36", summary["r36_manual_fill_status"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota37|rota36|rota32|rota28|status R36|status R37|acao|proxima acao|",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{markdown_cell(row['route37_id'])}|{markdown_cell(row['route36_id'])}|{markdown_cell(row['route32_id'])}|{markdown_cell(row['route28_id'])}|{markdown_cell(row['r36_manual_fill_status'])}|{markdown_cell(row['r37_status'])}|{markdown_cell(row['chain_action'])}|{markdown_cell(row['next_action'])}|"
        )
    lines.extend(
        [
            "",
            "## Leitura",
            "",
            "A cadeia de revalidacao esta descrita, mas deve permanecer parada enquanto R36 indicar `awaiting_human_visual_entry`. O proximo passo continua sendo preencher a planilha R32 a partir do HTML R32.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("protocol_csv", help="Route 36 manual fill protocol CSV")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_revalidation_chain_plan_zl3b.csv"),
        help="Revalidation chain plan CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_revalidation_chain_summary_zl3b.csv"),
        help="Revalidation chain summary output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_37_plano_revalidacao_r34_r35_r33_r31.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    protocol_csv = Path(args.protocol_csv)
    rows = build_revalidation_chain_rows(read_csv(protocol_csv))
    summary = summarize_revalidation_chain_rows(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, rows, FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_report(md_path, rows, protocol_csv, csv_path, summary_path)
    print(
        f"chain_items={len(rows)} "
        f"blocked_no_human={summary['r37_status'].get('blocked_no_human_entries', 0)} "
        f"ready_chain={summary['r37_status'].get('ready_for_revalidation_chain', 0)} "
        f"planned_chain_runs={summary['chain_action'].get('run_r34_r35_r33_r31_in_order', 0)}"
    )
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
