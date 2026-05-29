#!/usr/bin/env python3
"""Plan route 33/31 rerun after the route 34 manual gate."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "post_gate_rerun_not_visual_evidence"

FIELDNAMES = [
    "route35_id",
    "route34_id",
    "route32_id",
    "route33_id",
    "route31_id",
    "route28_id",
    "folio",
    "priority_level",
    "locus_kind",
    "r34_gate_status",
    "r34_next_action",
    "r35_status",
    "rerun_action",
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


def post_gate_status(gate_status: str) -> tuple[str, str, str]:
    if gate_status == "ready_to_rerun_r33_r31":
        return (
            "ready_for_controlled_rerun",
            "rerun_r33_then_r31_for_explicit_entries",
            "run_r33_apply_entries_then_r31_validation",
        )
    if gate_status == "blocked_pending_manual_annotation":
        return (
            "blocked_by_manual_gate",
            "skip_r33_r31_rerun_until_manual_entries",
            "fill_r32_entry_sheet_using_html_then_rerun_r34",
        )
    return (
        "blocked_by_gate_issue",
        "skip_r33_r31_rerun_until_gate_clean",
        "fix_r34_gate_issue_then_rerun_r34",
    )


def build_post_gate_rows(gate_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for row in gate_rows:
        status, rerun_action, next_action = post_gate_status(row.get("gate_status", ""))
        rows.append(
            {
                "route35_id": f"R35-{len(rows) + 1:03d}",
                "route34_id": row.get("route34_id", ""),
                "route32_id": row.get("route32_id", ""),
                "route33_id": row.get("route33_id", ""),
                "route31_id": row.get("route31_id", ""),
                "route28_id": row.get("route28_id", ""),
                "folio": row.get("folio", ""),
                "priority_level": row.get("priority_level", ""),
                "locus_kind": row.get("locus_kind", ""),
                "r34_gate_status": row.get("gate_status", ""),
                "r34_next_action": row.get("next_action", ""),
                "r35_status": status,
                "rerun_action": rerun_action,
                "next_action": next_action,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def summarize_post_gate_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "r35_status": Counter(row.get("r35_status", "") for row in rows),
        "rerun_action": Counter(row.get("rerun_action", "") for row in rows),
        "next_action": Counter(row.get("next_action", "") for row in rows),
        "r34_gate_status": Counter(row.get("r34_gate_status", "") for row in rows),
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
    gate_csv: Path,
    plan_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_post_gate_rows(rows)
    lines = [
        "# Rota 35: plano de reexecucao pos-gate R32",
        "",
        "Esta rota decide se ha base manual para reexecutar R33 e R31 apos o gate R34. Ela nao chama os scripts de aplicacao/validacao quando o gate manual esta bloqueado.",
        "",
        f"Gate R34: `{gate_csv}`.",
        f"Plano R35: `{plan_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens avaliados: {len(rows)};",
        f"- bloqueados pelo gate manual: {summary['r35_status'].get('blocked_by_manual_gate', 0)};",
        f"- prontos para reexecucao controlada: {summary['r35_status'].get('ready_for_controlled_rerun', 0)};",
        f"- bloqueados por problema de gate: {summary['r35_status'].get('blocked_by_gate_issue', 0)};",
        f"- reexecucoes R33/R31 planejadas agora: {summary['rerun_action'].get('rerun_r33_then_r31_for_explicit_entries', 0)};",
        "- guarda: `post_gate_rerun_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Status R35", summary["r35_status"]))
    lines.extend(render_counts("Acao de reexecucao", summary["rerun_action"]))
    lines.extend(render_counts("Proxima acao", summary["next_action"]))
    lines.extend(render_counts("Status R34", summary["r34_gate_status"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota35|rota34|rota32|rota28|status R34|status R35|acao|proxima acao|",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{markdown_cell(row['route35_id'])}|{markdown_cell(row['route34_id'])}|{markdown_cell(row['route32_id'])}|{markdown_cell(row['route28_id'])}|{markdown_cell(row['r34_gate_status'])}|{markdown_cell(row['r35_status'])}|{markdown_cell(row['rerun_action'])}|{markdown_cell(row['next_action'])}|"
        )
    lines.extend(
        [
            "",
            "## Leitura",
            "",
            "A Rota 35 confirma que nao ha reexecucao responsavel de R33/R31 enquanto a planilha R32 estiver vazia. O proximo passo permanece manual: preencher a planilha R32 e reexecutar R34.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate_csv", help="Route 34 manual gate CSV")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_post_gate_rerun_plan_zl3b.csv"),
        help="Post-gate rerun plan CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_post_gate_rerun_summary_zl3b.csv"),
        help="Post-gate rerun summary output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_35_plano_reexecucao_pos_gate_r32.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    gate_csv = Path(args.gate_csv)
    rows = build_post_gate_rows(read_csv(gate_csv))
    summary = summarize_post_gate_rows(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, rows, FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_report(md_path, rows, gate_csv, csv_path, summary_path)
    print(
        f"post_gate_items={len(rows)} "
        f"blocked_manual={summary['r35_status'].get('blocked_by_manual_gate', 0)} "
        f"ready_rerun={summary['r35_status'].get('ready_for_controlled_rerun', 0)} "
        f"planned_reruns={summary['rerun_action'].get('rerun_r33_then_r31_for_explicit_entries', 0)}"
    )
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
