#!/usr/bin/env python3
"""Consolidate filled route 15 human review instructions into evidence categories."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COORDINATE_FIELDS = [
    "manual_new_crop_x",
    "manual_new_crop_y",
    "manual_new_crop_width",
    "manual_new_crop_height",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def normalize_flag(value: str) -> str:
    value = value.strip().lower()
    if value == "":
        return "blank"
    if value in {"yes", "no", "uncertain"}:
        return value
    return "invalid"


def parse_positive_number(value: str) -> float | None:
    if value == "":
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    if number <= 0:
        return None
    return number


def coordinate_status(row: dict[str, str]) -> str:
    values = [row.get(field, "") for field in COORDINATE_FIELDS]
    crop_flag = normalize_flag(row.get("manual_new_crop_needed", ""))
    has_any = any(value != "" for value in values)
    has_all = all(value != "" for value in values)

    if not has_any:
        return "no_new_crop_coordinates"
    if crop_flag != "yes":
        return "coordinates_without_new_crop_flag"
    if not has_all:
        return "incomplete_new_crop_coordinates"
    if all(parse_positive_number(value) is not None for value in values):
        return "new_crop_coordinates_complete"
    return "invalid_new_crop_coordinates"


def classify_human_evidence(row: dict[str, str]) -> dict[str, str]:
    token_seen = normalize_flag(row.get("manual_token_seen", ""))
    crop_needed = normalize_flag(row.get("manual_new_crop_needed", ""))
    image_insufficient = normalize_flag(row.get("manual_image_insufficient", ""))
    coords = coordinate_status(row)

    if "invalid" in {token_seen, crop_needed, image_insufficient}:
        return {
            "coordinate_status": coords,
            "human_review_state": "invalid_human_entry",
            "evidence_category": "no_human_visual_evidence",
            "crop_generation_action": "no_crop_generation",
            "axis_test_readiness": "not_ready",
            "next_action": "fix human yes/no/uncertain fields before evidence consolidation",
        }

    if token_seen == "blank" and crop_needed == "blank" and image_insufficient == "blank":
        return {
            "coordinate_status": coords,
            "human_review_state": "pending_human_review",
            "evidence_category": "no_human_visual_evidence",
            "crop_generation_action": "no_crop_generation",
            "axis_test_readiness": "not_ready",
            "next_action": "fill human review fields from source image inspection",
        }

    if image_insufficient == "yes":
        return {
            "coordinate_status": coords,
            "human_review_state": "image_insufficient",
            "evidence_category": "no_human_visual_evidence",
            "crop_generation_action": "seek_alternate_image",
            "axis_test_readiness": "not_ready",
            "next_action": "seek alternate image source or suspend item",
        }

    if token_seen == "yes" and crop_needed == "yes" and coords == "new_crop_coordinates_complete":
        return {
            "coordinate_status": coords,
            "human_review_state": "human_confirmed_new_crop_candidate",
            "evidence_category": "human_seen_with_new_crop_coordinates",
            "crop_generation_action": "generate_new_crop_candidate",
            "axis_test_readiness": "ready_after_new_crop_review",
            "next_action": "generate new crop candidate and review before axis testing",
        }

    if token_seen == "yes" and crop_needed == "yes":
        return {
            "coordinate_status": coords,
            "human_review_state": "human_seen_incomplete_new_crop",
            "evidence_category": "human_seen_but_crop_coordinates_not_ready",
            "crop_generation_action": "no_crop_generation",
            "axis_test_readiness": "not_ready",
            "next_action": "complete positive numeric crop coordinates",
        }

    if token_seen == "yes" and crop_needed in {"no", "blank"}:
        return {
            "coordinate_status": coords,
            "human_review_state": "human_seen_without_new_crop",
            "evidence_category": "human_seen_no_new_crop_coordinates",
            "crop_generation_action": "no_crop_generation",
            "axis_test_readiness": "not_ready",
            "next_action": "explain in notes why no new crop is needed or add coordinates",
        }

    if token_seen == "no":
        return {
            "coordinate_status": coords,
            "human_review_state": "human_token_not_seen",
            "evidence_category": "human_not_seen",
            "crop_generation_action": "no_crop_generation",
            "axis_test_readiness": "not_ready",
            "next_action": "keep item outside glyph-level axis tests",
        }

    if token_seen == "uncertain":
        return {
            "coordinate_status": coords,
            "human_review_state": "uncertain_human_review",
            "evidence_category": "uncertain_human_visual_evidence",
            "crop_generation_action": "no_crop_generation",
            "axis_test_readiness": "not_ready",
            "next_action": "review again or seek alternate image",
        }

    return {
        "coordinate_status": coords,
        "human_review_state": "incomplete_human_decision",
        "evidence_category": "no_human_visual_evidence",
        "crop_generation_action": "no_crop_generation",
        "axis_test_readiness": "not_ready",
        "next_action": "complete token_seen/new_crop_needed/image_insufficient fields",
    }


def checklist_index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("checklist_id", ""): row for row in rows if row.get("checklist_id", "")}


def missing_checklist_outcome() -> dict[str, str]:
    return {
        "coordinate_status": "no_new_crop_coordinates",
        "human_review_state": "missing_checklist_row",
        "evidence_category": "no_human_visual_evidence",
        "crop_generation_action": "no_crop_generation",
        "axis_test_readiness": "not_ready",
        "next_action": "restore checklist row before consolidation",
    }


def build_evidence_rows(
    instruction_items: list[dict[str, str]],
    checklist_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    checklist_by_id = checklist_index(checklist_rows)
    evidence_rows: list[dict[str, str]] = []

    for index, instruction in enumerate(instruction_items, start=1):
        checklist_id = instruction.get("checklist_id", "")
        checklist = checklist_by_id.get(checklist_id, {})
        outcome = classify_human_evidence(checklist) if checklist else missing_checklist_outcome()
        evidence_rows.append(
            {
                "route16_id": f"R16-{index:03d}",
                "instruction_item_id": instruction.get("instruction_item_id", ""),
                "checklist_id": checklist_id,
                "packet_id": instruction.get("packet_id", ""),
                "route11_id": instruction.get("route11_id", ""),
                "route10_id": instruction.get("route10_id", ""),
                "manual_review_id": instruction.get("manual_review_id", ""),
                "crop_id": instruction.get("crop_id", ""),
                "source_review_id": instruction.get("source_review_id", ""),
                "folio": instruction.get("folio", ""),
                "locus": instruction.get("locus", ""),
                "source_image": instruction.get("source_image", ""),
                "crop_svg": instruction.get("crop_svg", ""),
                "review_region": instruction.get("review_region", ""),
                "priority_bucket": instruction.get("priority_bucket", checklist.get("priority_bucket", "")),
                "target_type": instruction.get("target_type", ""),
                "review_target": instruction.get("review_target", ""),
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
                "evidence_category": outcome["evidence_category"],
                "crop_generation_action": outcome["crop_generation_action"],
                "axis_test_readiness": outcome["axis_test_readiness"],
                "next_action": outcome["next_action"],
                "semantic_guardrail": "human_review_evidence_not_axis_meaning",
            }
        )

    return evidence_rows


def summarize_evidence_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "human_review_state": Counter(row.get("human_review_state", "") for row in rows),
        "evidence_category": Counter(row.get("evidence_category", "") for row in rows),
        "coordinate_status": Counter(row.get("coordinate_status", "") for row in rows),
        "crop_generation_action": Counter(row.get("crop_generation_action", "") for row in rows),
        "axis_test_readiness": Counter(row.get("axis_test_readiness", "") for row in rows),
        "packet_id": Counter(row.get("packet_id", "") for row in rows),
        "target_type": Counter(row.get("target_type", "") for row in rows),
    }


FIELDNAMES = [
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


def write_report(
    path: Path,
    rows: list[dict[str, str]],
    instruction_items_csv: Path,
    checklist_csv: Path,
    output_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_evidence_rows(rows)
    ready = summary["axis_test_readiness"].get("ready_after_new_crop_review", 0)
    pending = summary["human_review_state"].get("pending_human_review", 0)
    lines = [
        "# Rota 16: consolidacao da revisao humana",
        "",
        "Esta rota cruza os itens de instrucao humana da Rota 15 com os campos manuais da checklist. Campos vazios continuam como pendencia e nao viram evidencia visual.",
        "",
        f"Instrucoes item-a-item: `{instruction_items_csv}`.",
        f"Checklist com campos manuais: `{checklist_csv}`.",
        f"Consolidado: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens consolidados: {len(rows)};",
        f"- pendentes de revisao humana: {pending};",
        f"- prontos para novo recorte apos revisao: {ready};",
        "- nenhum campo vazio foi interpretado como confirmacao ou rejeicao;",
        "- nenhuma linha autoriza significado para `a/o` ou `r/l`.",
        "- guarda: `human_review_evidence_not_axis_meaning`.",
        "",
    ]
    lines.extend(render_counts("Estado da revisao humana", summary["human_review_state"]))
    lines.extend(render_counts("Categoria de evidencia", summary["evidence_category"]))
    lines.extend(render_counts("Status de coordenadas", summary["coordinate_status"]))
    lines.extend(render_counts("Acao de recorte", summary["crop_generation_action"]))
    lines.extend(render_counts("Prontidao para eixo", summary["axis_test_readiness"]))
    lines.extend(
        [
            "## Linhas consolidadas",
            "",
            "|rota16|instrucao|checklist|pacote|folio|alvo|estado|evidencia|acao|",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['route16_id']}|{row['instruction_item_id']}|{row['checklist_id']}|{row['packet_id']}|{row['folio']}|{row['review_target']}|{row['human_review_state']}|{row['evidence_category']}|{row['crop_generation_action']}|"
        )
    lines.extend(
        [
            "",
            "## Leitura provisoria",
            "",
            "- A Rota 16 e uma consolidacao operacional das respostas humanas, nao uma etapa semantica.",
            "- Somente linhas com token visto e coordenadas completas podem seguir para geracao/revisao de novo recorte.",
            "- Mesmo um novo recorte revisado ainda precisara de teste separado antes de qualquer leitura dos eixos.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("instruction_items_csv", help="CSV from prepare_human_review_instructions.py")
    parser.add_argument("checklist_csv", help="CSV from prepare_packet_item_checklist.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "human_review_evidence_consolidated_zl3b.csv"),
        help="Consolidated human review evidence CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "human_review_evidence_summary_zl3b.csv"),
        help="Human review evidence summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_16_consolidacao_revisao_humana.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    instruction_items_csv = Path(args.instruction_items_csv)
    checklist_csv = Path(args.checklist_csv)
    rows = build_evidence_rows(read_csv(instruction_items_csv), read_csv(checklist_csv))
    summary = summarize_evidence_rows(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, rows)
    write_summary_csv(summary_path, summary)
    write_report(md_path, rows, instruction_items_csv, checklist_csv, csv_path, summary_path)
    ready = summary["axis_test_readiness"].get("ready_after_new_crop_review", 0)
    print(f"human_review_evidence_rows={len(rows)} ready_after_new_crop_review={ready}")
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
