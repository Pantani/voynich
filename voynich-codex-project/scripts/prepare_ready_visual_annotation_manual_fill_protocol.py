#!/usr/bin/env python3
"""Prepare the manual fill protocol for route 32 visual annotation entries."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "manual_fill_protocol_not_visual_evidence"
ALLOWED_MANUAL_STATUS = {"annotated", "not_visible", "uncertain"}
ALLOWED_MANUAL_STATUS_TEXT = "annotated/not_visible/uncertain"

FIELDNAMES = [
    "route36_id",
    "route35_id",
    "route34_id",
    "route32_id",
    "route31_id",
    "route28_id",
    "folio",
    "priority_level",
    "locus_kind",
    "manual_annotation_status",
    "manual_visual_notes",
    "allowed_manual_annotation_status",
    "html_reference",
    "manual_fill_status",
    "blocking_reason",
    "r35_status",
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


def manual_fill_status(status: str, notes: str) -> tuple[str, str, str]:
    if not status and not notes:
        return (
            "awaiting_human_visual_entry",
            "manual_entry_required",
            "open_r32_html_fill_status_and_notes_then_rerun_r34",
        )
    if status not in ALLOWED_MANUAL_STATUS:
        return (
            "invalid_manual_entry_needs_correction",
            "manual_annotation_status_not_allowed",
            "fix_r32_status_and_notes_then_rerun_r34",
        )
    if not notes:
        return (
            "invalid_manual_entry_needs_correction",
            "manual_visual_notes_required",
            "fix_r32_status_and_notes_then_rerun_r34",
        )
    return (
        "human_entry_present_ready_for_gate_rerun",
        "manual_entry_present",
        "rerun_r34_then_r35",
    )


def build_manual_fill_rows(
    entry_rows: list[dict[str, str]],
    post_gate_rows: list[dict[str, str]],
    html_reference: str,
) -> list[dict[str, str]]:
    post_gate_by_route32 = {row.get("route32_id", ""): row for row in post_gate_rows}
    rows: list[dict[str, str]] = []
    for entry in entry_rows:
        post_gate = post_gate_by_route32.get(entry.get("route32_id", ""), {})
        status = entry.get("manual_annotation_status", "")
        notes = entry.get("manual_visual_notes", "")
        fill_status, reason, next_action = manual_fill_status(status, notes)
        rows.append(
            {
                "route36_id": f"R36-{len(rows) + 1:03d}",
                "route35_id": post_gate.get("route35_id", ""),
                "route34_id": post_gate.get("route34_id", ""),
                "route32_id": entry.get("route32_id", ""),
                "route31_id": entry.get("route31_id", ""),
                "route28_id": entry.get("route28_id", ""),
                "folio": entry.get("folio", ""),
                "priority_level": entry.get("priority_level", ""),
                "locus_kind": entry.get("locus_kind", ""),
                "manual_annotation_status": status,
                "manual_visual_notes": notes,
                "allowed_manual_annotation_status": entry.get("allowed_manual_annotation_status", ALLOWED_MANUAL_STATUS_TEXT),
                "html_reference": html_reference,
                "manual_fill_status": fill_status,
                "blocking_reason": reason,
                "r35_status": post_gate.get("r35_status", ""),
                "next_action": next_action,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def summarize_manual_fill_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "manual_fill_status": Counter(row.get("manual_fill_status", "") for row in rows),
        "blocking_reason": Counter(row.get("blocking_reason", "") for row in rows),
        "next_action": Counter(row.get("next_action", "") for row in rows),
        "r35_status": Counter(row.get("r35_status", "") for row in rows),
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
    post_gate_csv: Path,
    html_reference: str,
    protocol_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_manual_fill_rows(rows)
    lines = [
        "# Rota 36: protocolo de preenchimento humano R32",
        "",
        "Esta rota prepara o preenchimento humano efetivo da planilha R32. Ela nao escreve decisoes na planilha original e nao interpreta imagens automaticamente.",
        "",
        f"Planilha R32: `{entry_csv}`.",
        f"Plano R35: `{post_gate_csv}`.",
        f"HTML de apoio: `{html_reference}`.",
        f"Protocolo R36: `{protocol_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens no protocolo: {len(rows)};",
        f"- aguardando anotacao humana: {summary['manual_fill_status'].get('awaiting_human_visual_entry', 0)};",
        f"- entradas prontas para reexecutar gate: {summary['manual_fill_status'].get('human_entry_present_ready_for_gate_rerun', 0)};",
        f"- entradas invalidas: {summary['manual_fill_status'].get('invalid_manual_entry_needs_correction', 0)};",
        "- planilha R32 original preservada;",
        "- guarda: `manual_fill_protocol_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Status de preenchimento", summary["manual_fill_status"]))
    lines.extend(render_counts("Motivo", summary["blocking_reason"]))
    lines.extend(render_counts("Proxima acao", summary["next_action"]))
    lines.extend(render_counts("Status R35", summary["r35_status"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota36|rota35|rota32|rota28|folio|status|motivo|proxima acao|",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{markdown_cell(row['route36_id'])}|{markdown_cell(row['route35_id'])}|{markdown_cell(row['route32_id'])}|{markdown_cell(row['route28_id'])}|{markdown_cell(row['folio'])}|{markdown_cell(row['manual_fill_status'])}|{markdown_cell(row['blocking_reason'])}|{markdown_cell(row['next_action'])}|"
        )
    lines.extend(
        [
            "",
            "## Instrucao manual",
            "",
            "Abrir o HTML R32, revisar visualmente uma linha por vez e preencher na planilha R32 somente valores humanos explicitos. `manual_annotation_status` aceita `annotated`, `not_visible` ou `uncertain`; `manual_visual_notes` e obrigatorio para qualquer status preenchido.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("entry_csv", help="Route 32 focused manual entry CSV")
    parser.add_argument("post_gate_csv", help="Route 35 post-gate plan CSV")
    parser.add_argument("html_reference", help="Route 32 HTML path used by the human reviewer")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_manual_fill_protocol_zl3b.csv"),
        help="Manual fill protocol CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_manual_fill_protocol_summary_zl3b.csv"),
        help="Manual fill protocol summary output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_36_protocolo_preenchimento_humano_r32.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    entry_csv = Path(args.entry_csv)
    post_gate_csv = Path(args.post_gate_csv)
    html_reference = args.html_reference
    rows = build_manual_fill_rows(read_csv(entry_csv), read_csv(post_gate_csv), html_reference)
    summary = summarize_manual_fill_rows(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, rows, FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_report(md_path, rows, entry_csv, post_gate_csv, html_reference, csv_path, summary_path)
    print(
        f"manual_fill_items={len(rows)} "
        f"awaiting_human={summary['manual_fill_status'].get('awaiting_human_visual_entry', 0)} "
        f"ready_gate={summary['manual_fill_status'].get('human_entry_present_ready_for_gate_rerun', 0)} "
        f"invalid={summary['manual_fill_status'].get('invalid_manual_entry_needs_correction', 0)}"
    )
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
