#!/usr/bin/env python3
"""Ingest filled route 17 P0/P1 checklist decisions into evidence classes."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

try:
    from scripts.consolidate_human_review_evidence import classify_human_evidence
except ModuleNotFoundError:  # pragma: no cover - used when executed as a script path
    from consolidate_human_review_evidence import classify_human_evidence

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def checklist_index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("checklist_id", ""): row for row in rows if row.get("checklist_id", "")}


def decision_bucket(row: dict[str, str]) -> str:
    state = row.get("human_review_state", "")
    if state == "pending_human_review":
        return "pending_manual_decision"
    if state == "human_confirmed_new_crop_candidate":
        return "new_crop_candidate"
    if state == "human_token_not_seen":
        return "token_not_seen"
    if state == "image_insufficient":
        return "image_insufficient"
    if state == "uncertain_human_review":
        return "uncertain_manual_decision"
    if state == "missing_checklist_row":
        return "missing_source_data"
    if state == "invalid_human_entry":
        return "invalid_manual_entry"
    return "incomplete_manual_decision"


def missing_checklist_decision() -> dict[str, str]:
    return {
        "coordinate_status": "no_new_crop_coordinates",
        "human_review_state": "missing_checklist_row",
        "evidence_category": "no_human_visual_evidence",
        "crop_generation_action": "no_crop_generation",
        "axis_test_readiness": "not_ready",
        "decision_bucket": "missing_source_data",
        "next_action": "restore checklist row before ingesting priority decision",
    }


def classify_priority_decision(checklist: dict[str, str]) -> dict[str, str]:
    outcome = classify_human_evidence(checklist)
    outcome["decision_bucket"] = decision_bucket(outcome)
    return outcome


def build_priority_decision_rows(
    priority_rows: list[dict[str, str]],
    checklist_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    checklist_by_id = checklist_index(checklist_rows)
    decision_rows: list[dict[str, str]] = []

    for index, priority in enumerate(priority_rows, start=1):
        checklist_id = priority.get("checklist_id", "")
        checklist = checklist_by_id.get(checklist_id, {})
        outcome = classify_priority_decision(checklist) if checklist else missing_checklist_decision()
        decision_rows.append(
            {
                "route18_id": f"R18-{index:03d}",
                "route17_id": priority.get("route17_id", ""),
                "route16_id": priority.get("route16_id", ""),
                "instruction_item_id": priority.get("instruction_item_id", ""),
                "checklist_id": checklist_id,
                "packet_id": priority.get("packet_id", ""),
                "route11_id": priority.get("route11_id", ""),
                "route10_id": priority.get("route10_id", ""),
                "manual_review_id": priority.get("manual_review_id", ""),
                "crop_id": priority.get("crop_id", ""),
                "source_review_id": priority.get("source_review_id", ""),
                "folio": priority.get("folio", ""),
                "locus": priority.get("locus", ""),
                "source_image": priority.get("source_image", ""),
                "crop_svg": priority.get("crop_svg", ""),
                "review_region": priority.get("review_region", ""),
                "priority_bucket": priority.get("priority_bucket", ""),
                "priority_level": priority.get("priority_level", ""),
                "target_type": priority.get("target_type", ""),
                "review_target": priority.get("review_target", ""),
                "manual_token_seen": checklist.get("manual_token_seen", ""),
                "manual_new_crop_needed": checklist.get("manual_new_crop_needed", ""),
                "manual_image_insufficient": checklist.get("manual_image_insufficient", ""),
                "manual_new_crop_x": checklist.get("manual_new_crop_x", ""),
                "manual_new_crop_y": checklist.get("manual_new_crop_y", ""),
                "manual_new_crop_width": checklist.get("manual_new_crop_width", ""),
                "manual_new_crop_height": checklist.get("manual_new_crop_height", ""),
                "manual_notes": checklist.get("manual_notes", ""),
                "coordinate_status": outcome["coordinate_status"],
                "human_review_state": outcome["human_review_state"],
                "decision_bucket": outcome["decision_bucket"],
                "evidence_category": outcome["evidence_category"],
                "crop_generation_action": outcome["crop_generation_action"],
                "axis_test_readiness": outcome["axis_test_readiness"],
                "next_action": outcome["next_action"],
                "semantic_guardrail": "priority_decision_not_axis_meaning",
            }
        )

    return decision_rows


def summarize_priority_decisions(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "decision_bucket": Counter(row.get("decision_bucket", "") for row in rows),
        "human_review_state": Counter(row.get("human_review_state", "") for row in rows),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "packet_id": Counter(row.get("packet_id", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
        "crop_generation_action": Counter(row.get("crop_generation_action", "") for row in rows),
        "axis_test_readiness": Counter(row.get("axis_test_readiness", "") for row in rows),
    }


FIELDNAMES = [
    "route18_id",
    "route17_id",
    "route16_id",
    "instruction_item_id",
    "checklist_id",
    "packet_id",
    "route11_id",
    "route10_id",
    "manual_review_id",
    "crop_id",
    "source_review_id",
    "folio",
    "locus",
    "source_image",
    "crop_svg",
    "review_region",
    "priority_bucket",
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
    "coordinate_status",
    "human_review_state",
    "decision_bucket",
    "evidence_category",
    "crop_generation_action",
    "axis_test_readiness",
    "next_action",
    "semantic_guardrail",
]


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
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


def render_decision_section(row: dict[str, str]) -> str:
    lines = [
        f"## {row['route18_id']} / {row['route17_id']} / {row['checklist_id']}",
        "",
        f"- folio: `{row.get('folio', '')}`;",
        f"- alvo: `{row.get('review_target', '')}`;",
        f"- manual_token_seen: `{row.get('manual_token_seen', '')}`;",
        f"- manual_new_crop_needed: `{row.get('manual_new_crop_needed', '')}`;",
        f"- manual_image_insufficient: `{row.get('manual_image_insufficient', '')}`;",
        f"- decisao: `{row.get('decision_bucket', '')}`;",
        f"- proxima acao: `{row.get('next_action', '')}`;",
        f"- guarda: `{row.get('semantic_guardrail', '')}`;",
        "",
    ]
    return "\n".join(lines)


def write_report(
    path: Path,
    rows: list[dict[str, str]],
    priority_csv: Path,
    checklist_csv: Path,
    output_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_priority_decisions(rows)
    ready = summary["decision_bucket"].get("new_crop_candidate", 0)
    pending = summary["decision_bucket"].get("pending_manual_decision", 0)
    lines = [
        "# Rota 18: ingestao das decisoes P0/P1",
        "",
        "Esta rota ingere a fila P0/P1 da Rota 17 contra a checklist. Ela classifica somente campos ja preenchidos e mantem campos vazios como pendencia.",
        "",
        f"Fila P0/P1: `{priority_csv}`.",
        f"Checklist: `{checklist_csv}`.",
        f"Consolidado: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens ingeridos: {len(rows)};",
        f"- pendentes: {pending};",
        f"- candidatos a novo recorte: {ready};",
        "- campos vazios nao foram convertidos em evidencia;",
        "- guarda: `priority_decision_not_axis_meaning`.",
        "",
    ]
    lines.extend(render_counts("Decisoes", summary["decision_bucket"]))
    lines.extend(render_counts("Estado humano", summary["human_review_state"]))
    lines.extend(render_counts("Prioridade", summary["priority_level"]))
    lines.extend(render_counts("Acao de recorte", summary["crop_generation_action"]))
    lines.extend(render_counts("Prontidao para eixo", summary["axis_test_readiness"]))
    lines.extend(
        [
            "## Linhas ingeridas",
            "",
            "|rota18|rota17|checklist|prioridade|folio|alvo|decisao|acao|",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['route18_id']}|{row['route17_id']}|{row['checklist_id']}|{row['priority_level']}|{row['folio']}|{row['review_target']}|{row['decision_bucket']}|{row['crop_generation_action']}|"
        )
    lines.append("")
    for row in rows:
        lines.append(render_decision_section(row))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("priority_review_csv", help="CSV from prepare_priority_human_review.py")
    parser.add_argument("checklist_csv", help="CSV from prepare_packet_item_checklist.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "priority_human_decisions_p0_p1_zl3b.csv"),
        help="P0/P1 ingested decision CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "priority_human_decisions_summary_zl3b.csv"),
        help="P0/P1 decision summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_18_ingestao_decisoes_p0_p1.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    priority_csv = Path(args.priority_review_csv)
    checklist_csv = Path(args.checklist_csv)
    rows = build_priority_decision_rows(read_csv(priority_csv), read_csv(checklist_csv))
    summary = summarize_priority_decisions(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, rows)
    write_summary_csv(summary_path, summary)
    write_report(md_path, rows, priority_csv, checklist_csv, csv_path, summary_path)
    print(
        f"priority_decision_rows={len(rows)} "
        f"pending={summary['decision_bucket'].get('pending_manual_decision', 0)} "
        f"new_crop_candidates={summary['decision_bucket'].get('new_crop_candidate', 0)}"
    )
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
