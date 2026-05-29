#!/usr/bin/env python3
"""Consolidate filled route 13 packet item checklist decisions."""
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


def final_outcome(row: dict[str, str]) -> dict[str, str]:
    token_seen = normalize_flag(row.get("manual_token_seen", ""))
    crop_needed = normalize_flag(row.get("manual_new_crop_needed", ""))
    image_insufficient = normalize_flag(row.get("manual_image_insufficient", ""))
    coords = coordinate_status(row)

    if "invalid" in {token_seen, crop_needed, image_insufficient}:
        return {
            "consolidation_outcome": "invalid_manual_flag",
            "coordinate_status": coords,
            "visual_evidence_status": "no_new_visual_evidence",
            "axis_test_eligibility": "not_eligible",
            "next_action": "fix manual yes/no/uncertain fields before interpreting",
        }

    if token_seen == "blank" and crop_needed == "blank" and image_insufficient == "blank":
        return {
            "consolidation_outcome": "pending_visual_check",
            "coordinate_status": coords,
            "visual_evidence_status": "no_new_visual_evidence",
            "axis_test_eligibility": "not_eligible",
            "next_action": "complete checklist fields after visual review",
        }

    if image_insufficient == "yes":
        return {
            "consolidation_outcome": "image_insufficient",
            "coordinate_status": coords,
            "visual_evidence_status": "no_new_visual_evidence",
            "axis_test_eligibility": "not_eligible",
            "next_action": "seek alternate image source or suspend item",
        }

    if token_seen == "yes" and crop_needed == "yes" and coords == "new_crop_coordinates_complete":
        return {
            "consolidation_outcome": "token_seen_new_crop_ready",
            "coordinate_status": coords,
            "visual_evidence_status": "new_crop_candidate",
            "axis_test_eligibility": "eligible_after_crop_generation",
            "next_action": "generate candidate crop and review before axis testing",
        }

    if token_seen == "yes" and crop_needed in {"no", "blank"}:
        return {
            "consolidation_outcome": "token_seen_without_new_crop",
            "coordinate_status": coords,
            "visual_evidence_status": "token_seen_no_crop_coordinates",
            "axis_test_eligibility": "not_eligible",
            "next_action": "mark coordinates or explain why no crop is needed",
        }

    if token_seen == "no":
        return {
            "consolidation_outcome": "token_not_seen",
            "coordinate_status": coords,
            "visual_evidence_status": "no_new_visual_evidence",
            "axis_test_eligibility": "not_eligible",
            "next_action": "keep item out of glyph-level tests",
        }

    if token_seen == "uncertain":
        return {
            "consolidation_outcome": "uncertain_visual_check",
            "coordinate_status": coords,
            "visual_evidence_status": "uncertain_visual_evidence",
            "axis_test_eligibility": "not_eligible",
            "next_action": "review again or seek alternate image",
        }

    return {
        "consolidation_outcome": "incomplete_manual_decision",
        "coordinate_status": coords,
        "visual_evidence_status": "no_new_visual_evidence",
        "axis_test_eligibility": "not_eligible",
        "next_action": "complete token_seen/new_crop_needed/image_insufficient fields",
    }


def build_consolidated_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    consolidated: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        outcome = final_outcome(row)
        consolidated.append(
            {
                "route14_id": f"R14-{index:03d}",
                "checklist_id": row.get("checklist_id", ""),
                "packet_id": row.get("packet_id", ""),
                "route11_id": row.get("route11_id", ""),
                "route10_id": row.get("route10_id", ""),
                "manual_review_id": row.get("manual_review_id", ""),
                "crop_id": row.get("crop_id", ""),
                "source_review_id": row.get("source_review_id", ""),
                "folio": row.get("folio", ""),
                "locus": row.get("locus", ""),
                "target_type": row.get("target_type", ""),
                "review_target": row.get("review_target", ""),
                "manual_token_seen": row.get("manual_token_seen", ""),
                "manual_new_crop_needed": row.get("manual_new_crop_needed", ""),
                "manual_image_insufficient": row.get("manual_image_insufficient", ""),
                "manual_new_crop_x": row.get("manual_new_crop_x", ""),
                "manual_new_crop_y": row.get("manual_new_crop_y", ""),
                "manual_new_crop_width": row.get("manual_new_crop_width", ""),
                "manual_new_crop_height": row.get("manual_new_crop_height", ""),
                "consolidation_outcome": outcome["consolidation_outcome"],
                "coordinate_status": outcome["coordinate_status"],
                "visual_evidence_status": outcome["visual_evidence_status"],
                "axis_test_eligibility": outcome["axis_test_eligibility"],
                "next_action": outcome["next_action"],
                "semantic_guardrail": "checklist_consolidation_not_axis_evidence",
            }
        )
    return consolidated


def summarize_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "consolidation_outcome": Counter(row["consolidation_outcome"] for row in rows),
        "coordinate_status": Counter(row["coordinate_status"] for row in rows),
        "visual_evidence_status": Counter(row["visual_evidence_status"] for row in rows),
        "axis_test_eligibility": Counter(row["axis_test_eligibility"] for row in rows),
        "target_type": Counter(row["target_type"] for row in rows),
        "packet_id": Counter(row["packet_id"] for row in rows),
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "route14_id",
        "checklist_id",
        "packet_id",
        "route11_id",
        "route10_id",
        "manual_review_id",
        "crop_id",
        "source_review_id",
        "folio",
        "locus",
        "target_type",
        "review_target",
        "manual_token_seen",
        "manual_new_crop_needed",
        "manual_image_insufficient",
        "manual_new_crop_x",
        "manual_new_crop_y",
        "manual_new_crop_width",
        "manual_new_crop_height",
        "consolidation_outcome",
        "coordinate_status",
        "visual_evidence_status",
        "axis_test_eligibility",
        "next_action",
        "semantic_guardrail",
    ]
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
        lines.append(f"|{key}|{value}|")
    lines.append("")
    return lines


def write_report(path: Path, rows: list[dict[str, str]], source_csv: Path, output_csv: Path, summary_csv: Path) -> None:
    summary = summarize_rows(rows)
    eligible = summary["axis_test_eligibility"].get("eligible_after_crop_generation", 0)
    lines = [
        "# Rota 14: consolidacao da checklist preenchida",
        "",
        "Esta rota consolida os campos manuais da checklist Rota 13. Com a checklist ainda vazia, ela registra pendencia e impede leitura semantica prematura.",
        "",
        f"Fonte: `{source_csv}`.",
        f"Consolidado: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens consolidados: {len(rows)};",
        f"- itens elegiveis apos geracao de recorte: {eligible};",
        f"- pendentes: {summary['consolidation_outcome'].get('pending_visual_check', 0)};",
        "- nenhuma evidencia visual nova foi criada por inferencia.",
        "",
    ]
    lines.extend(render_counts("Resultado de consolidacao", summary["consolidation_outcome"]))
    lines.extend(render_counts("Status de coordenadas", summary["coordinate_status"]))
    lines.extend(render_counts("Evidencia visual", summary["visual_evidence_status"]))
    lines.extend(render_counts("Elegibilidade", summary["axis_test_eligibility"]))
    lines.extend(render_counts("Tipo de alvo", summary["target_type"]))
    lines.extend(
        [
            "## Linhas consolidadas",
            "",
            "|rota14|checklist|pacote|folio|alvo|resultado|evidencia|elegivel|",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['route14_id']}|{row['checklist_id']}|{row['packet_id']}|{row['folio']}|{row['review_target']}|{row['consolidation_outcome']}|{row['visual_evidence_status']}|{row['axis_test_eligibility']}|"
        )
    lines.extend(
        [
            "",
            "## Leitura provisoria",
            "",
            "- Campos manuais vazios continuam sendo pendencia, nao negativa nem confirmacao.",
            "- Coordenadas novas so podem ser usadas quando `manual_new_crop_needed=yes` e todos os campos numericos estiverem completos.",
            "- A guarda `checklist_consolidation_not_axis_evidence` impede usar esta consolidacao como significado de `a/o` ou `r/l`.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("checklist_csv", help="CSV from prepare_packet_item_checklist.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "packet_item_checklist_consolidated_zl3b.csv"),
        help="Consolidated checklist CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "packet_item_checklist_consolidation_summary_zl3b.csv"),
        help="Consolidation summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_14_consolidacao_checklist.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = Path(args.checklist_csv)
    consolidated = build_consolidated_rows(read_csv(source))
    summary = summarize_rows(consolidated)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, consolidated)
    write_summary_csv(summary_path, summary)
    write_report(md_path, consolidated, source, csv_path, summary_path)
    eligible = summary["axis_test_eligibility"].get("eligible_after_crop_generation", 0)
    print(f"consolidated_rows={len(consolidated)} eligible_after_crop_generation={eligible}")
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
