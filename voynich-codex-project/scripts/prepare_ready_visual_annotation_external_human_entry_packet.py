#!/usr/bin/env python3
"""Prepare route 41 external human entry packet for route 32."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "external_human_entry_packet_not_visual_evidence"
ALLOWED_MANUAL_STATUS = {"annotated", "not_visible", "uncertain"}
TARGET_FIELDS = "manual_annotation_status manual_visual_notes"

FIELDNAMES = [
    "route41_id",
    "route40_id",
    "route39_id",
    "route38_id",
    "route32_id",
    "route31_id",
    "route28_id",
    "folio",
    "priority_level",
    "locus_kind",
    "image_url",
    "commons_page",
    "html_reference",
    "target_csv",
    "target_fields",
    "allowed_manual_annotation_status",
    "manual_annotation_status",
    "manual_visual_notes",
    "reopen_plan_status",
    "external_entry_status",
    "reviewer_action",
    "post_entry_action",
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


def external_entry_status(
    manual_annotation_status: str,
    manual_visual_notes: str,
    reopen_plan_status: str,
) -> tuple[str, str, str]:
    has_status = bool(manual_annotation_status)
    has_notes = bool(manual_visual_notes)
    if not has_status and not has_notes:
        return (
            "external_human_entry_required",
            "fill_r32_manual_annotation_status_and_notes",
            "do_not_modify_derived_outputs",
        )
    if has_status != has_notes:
        return (
            "invalid_partial_r32_manual_entry",
            "complete_or_clear_r32_manual_fields",
            "rerun_r36_r37_r39_r40_after_fix",
        )
    if manual_annotation_status not in ALLOWED_MANUAL_STATUS:
        return (
            "invalid_manual_annotation_status",
            "use_allowed_status_annotated_not_visible_uncertain",
            "rerun_r36_r37_r39_r40_after_fix",
        )
    if reopen_plan_status == "ready_to_run_revalidation_chain":
        return (
            "external_human_entry_already_released",
            "no_manual_edit_needed_now",
            "execute_r40_chain_plan",
        )
    return (
        "external_human_entry_present",
        "rerun_r36_r37_r39_r40",
        "do_not_run_chain_until_r40_ready",
    )


def build_external_human_entry_rows(
    entry_rows: list[dict[str, str]],
    work_order_rows: list[dict[str, str]],
    plan_rows: list[dict[str, str]],
    target_csv: str,
) -> list[dict[str, str]]:
    work_order_by_route32 = {row.get("route32_id", ""): row for row in work_order_rows}
    plan_by_route32 = {row.get("route32_id", ""): row for row in plan_rows}
    rows: list[dict[str, str]] = []
    for entry in entry_rows:
        route32_id = entry.get("route32_id", "")
        work_order = work_order_by_route32.get(route32_id, {})
        plan = plan_by_route32.get(route32_id, {})
        status = entry.get("manual_annotation_status", "")
        notes = entry.get("manual_visual_notes", "")
        entry_status, reviewer_action, post_entry_action = external_entry_status(
            status,
            notes,
            plan.get("reopen_plan_status", ""),
        )
        rows.append(
            {
                "route41_id": f"R41-{len(rows) + 1:03d}",
                "route40_id": plan.get("route40_id", ""),
                "route39_id": plan.get("route39_id", ""),
                "route38_id": work_order.get("route38_id", plan.get("route38_id", "")),
                "route32_id": route32_id,
                "route31_id": entry.get("route31_id", ""),
                "route28_id": entry.get("route28_id", ""),
                "folio": entry.get("folio", ""),
                "priority_level": entry.get("priority_level", ""),
                "locus_kind": entry.get("locus_kind", ""),
                "image_url": entry.get("image_url", ""),
                "commons_page": entry.get("commons_page", ""),
                "html_reference": work_order.get("html_reference", ""),
                "target_csv": target_csv,
                "target_fields": TARGET_FIELDS,
                "allowed_manual_annotation_status": entry.get("allowed_manual_annotation_status", "annotated/not_visible/uncertain"),
                "manual_annotation_status": status,
                "manual_visual_notes": notes,
                "reopen_plan_status": plan.get("reopen_plan_status", ""),
                "external_entry_status": entry_status,
                "reviewer_action": reviewer_action,
                "post_entry_action": post_entry_action,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def summarize_external_human_entry_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "external_entry_status": Counter(row.get("external_entry_status", "") for row in rows),
        "reviewer_action": Counter(row.get("reviewer_action", "") for row in rows),
        "post_entry_action": Counter(row.get("post_entry_action", "") for row in rows),
        "reopen_plan_status": Counter(row.get("reopen_plan_status", "") for row in rows),
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
    plan_csv: Path,
    packet_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_external_human_entry_rows(rows)
    lines = [
        "# Rota 41: pacote de entrada humana externa na R32",
        "",
        "Esta rota prepara o pacote para revisao visual humana externa. Ela nao preenche a R32, nao interpreta imagem e nao altera arquivos derivados.",
        "",
        f"Planilha alvo R32: `{entry_csv}`.",
        f"Ordem R38: `{work_order_csv}`.",
        f"Plano R40: `{plan_csv}`.",
        f"Pacote R41: `{packet_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens no pacote: {len(rows)};",
        f"- exigem entrada humana externa: {summary['external_entry_status'].get('external_human_entry_required', 0)};",
        f"- entradas humanas presentes: {summary['external_entry_status'].get('external_human_entry_present', 0)};",
        f"- entradas invalidas ou parciais: {summary['external_entry_status'].get('invalid_partial_r32_manual_entry', 0) + summary['external_entry_status'].get('invalid_manual_annotation_status', 0)};",
        "- planilha R32 original preservada;",
        "- guarda: `external_human_entry_packet_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Status de entrada externa", summary["external_entry_status"]))
    lines.extend(render_counts("Acao do revisor", summary["reviewer_action"]))
    lines.extend(render_counts("Acao pos-entrada", summary["post_entry_action"]))
    lines.extend(render_counts("Status R40", summary["reopen_plan_status"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota41|rota40|rota38|rota32|folio|alvo|status|acao do revisor|",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{markdown_cell(row['route41_id'])}|{markdown_cell(row['route40_id'])}|{markdown_cell(row['route38_id'])}|{markdown_cell(row['route32_id'])}|{markdown_cell(row['folio'])}|{markdown_cell(row['target_fields'])}|{markdown_cell(row['external_entry_status'])}|{markdown_cell(row['reviewer_action'])}|"
        )
    lines.extend(
        [
            "",
            "## Instrucao manual",
            "",
            "Para cada item, abrir o HTML R32 e a imagem fonte, revisar visualmente e preencher na planilha R32 somente `manual_annotation_status` e `manual_visual_notes`. Valores permitidos: `annotated`, `not_visible`, `uncertain`. Depois reexecutar R36, R37, R39 e R40 antes de qualquer reabertura da cadeia.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entry_csv", help="Route 32 focused manual entry CSV")
    parser.add_argument("work_order_csv", help="Route 38 manual work order CSV")
    parser.add_argument("plan_csv", help="Route 40 conditional reopen plan CSV")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_external_human_entry_packet_zl3b.csv"),
        help="Route 41 packet CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_external_human_entry_summary_zl3b.csv"),
        help="Route 41 summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_41_pacote_entrada_humana_externa_r32.md"),
        help="Route 41 Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    entry_csv = Path(args.entry_csv)
    work_order_csv = Path(args.work_order_csv)
    plan_csv = Path(args.plan_csv)
    rows = build_external_human_entry_rows(
        read_csv(entry_csv),
        read_csv(work_order_csv),
        read_csv(plan_csv),
        str(entry_csv),
    )
    summary = summarize_external_human_entry_rows(rows)
    packet_csv = Path(args.csv)
    summary_csv = Path(args.summary_csv)
    md = Path(args.md)
    write_csv(packet_csv, rows, FIELDNAMES)
    write_summary_csv(summary_csv, summary)
    write_report(md, rows, entry_csv, work_order_csv, plan_csv, packet_csv, summary_csv)
    invalid = summary["external_entry_status"].get("invalid_partial_r32_manual_entry", 0) + summary["external_entry_status"].get(
        "invalid_manual_annotation_status", 0
    )
    print(
        f"packet_items={len(rows)} "
        f"external_required={summary['external_entry_status'].get('external_human_entry_required', 0)} "
        f"external_present={summary['external_entry_status'].get('external_human_entry_present', 0)} "
        f"invalid={invalid}"
    )
    print(f"csv={packet_csv.resolve()}")
    print(f"summary_csv={summary_csv.resolve()}")
    print(f"md={md.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
