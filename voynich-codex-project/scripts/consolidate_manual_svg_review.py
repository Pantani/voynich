#!/usr/bin/env python3
"""Consolidate manual SVG review outcomes for route 10."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

COORDINATE_FIELDS = [
    "manual_tighter_x",
    "manual_tighter_y",
    "manual_tighter_width",
    "manual_tighter_height",
]

ALLOWED_FINAL_STATUS = {
    "pending_manual_review",
    "confirmed_tighter_region",
    "keep_not_isolated",
    "unusable_crop",
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


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
    if all(value == "" for value in values):
        return "no_manual_coordinates"
    if any(value == "" for value in values):
        return "incomplete_manual_coordinates"
    if all(parse_positive_number(value) is not None for value in values):
        return "manual_coordinates_complete"
    return "invalid_manual_coordinates"


def final_outcome(row: dict[str, str]) -> dict[str, str]:
    manual_status = row.get("manual_final_status", "")
    coords = coordinate_status(row)

    if manual_status not in ALLOWED_FINAL_STATUS:
        return {
            "consolidation_outcome": "invalid_manual_status",
            "coordinate_status": coords,
            "evidence_status": "no_glyph_confirmation",
            "axis_test_eligibility": "not_eligible",
            "next_action": "fix manual_final_status before interpreting this row",
        }

    if manual_status == "confirmed_tighter_region":
        if coords == "manual_coordinates_complete":
            return {
                "consolidation_outcome": "confirmed_tighter_region",
                "coordinate_status": coords,
                "evidence_status": "tighter_region_confirmed",
                "axis_test_eligibility": "eligible_after_manual_review",
                "next_action": "use only as coordinate evidence, not as translation",
            }
        return {
            "consolidation_outcome": "invalid_confirmed_region",
            "coordinate_status": coords,
            "evidence_status": "no_glyph_confirmation",
            "axis_test_eligibility": "not_eligible",
            "next_action": "confirmed_tighter_region requires all coordinate fields",
        }

    if manual_status == "keep_not_isolated":
        return {
            "consolidation_outcome": "keep_not_isolated",
            "coordinate_status": coords,
            "evidence_status": "no_glyph_confirmation",
            "axis_test_eligibility": "not_eligible",
            "next_action": "exclude from glyph-level axis tests until better evidence exists",
        }

    if manual_status == "unusable_crop":
        return {
            "consolidation_outcome": "unusable_crop",
            "coordinate_status": coords,
            "evidence_status": "no_glyph_confirmation",
            "axis_test_eligibility": "not_eligible",
            "next_action": "regenerate crop or drop from glyph-level visual testing",
        }

    return {
        "consolidation_outcome": "pending_manual_review",
        "coordinate_status": coords,
        "evidence_status": "no_glyph_confirmation",
        "axis_test_eligibility": "not_eligible",
        "next_action": "complete manual review before assigning visual evidence",
    }


def build_consolidated_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    consolidated: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        outcome = final_outcome(row)
        consolidated.append(
            {
                "route10_id": f"R10-{index:03d}",
                "manual_review_id": row.get("manual_review_id", ""),
                "decision_id": row.get("decision_id", ""),
                "crop_id": row.get("crop_id", ""),
                "source_review_id": row.get("source_review_id", ""),
                "folio": row.get("folio", ""),
                "locus": row.get("locus", ""),
                "prefix_family": row.get("prefix_family", ""),
                "axis_coverage": row.get("axis_coverage", ""),
                "group_tokens": row.get("group_tokens", ""),
                "missing_group_tokens": row.get("missing_group_tokens", ""),
                "manual_final_status": row.get("manual_final_status", ""),
                "manual_tighter_x": row.get("manual_tighter_x", ""),
                "manual_tighter_y": row.get("manual_tighter_y", ""),
                "manual_tighter_width": row.get("manual_tighter_width", ""),
                "manual_tighter_height": row.get("manual_tighter_height", ""),
                "manual_target_tokens_seen": row.get("manual_target_tokens_seen", ""),
                "manual_missing_tokens_seen": row.get("manual_missing_tokens_seen", ""),
                "consolidation_outcome": outcome["consolidation_outcome"],
                "coordinate_status": outcome["coordinate_status"],
                "evidence_status": outcome["evidence_status"],
                "axis_test_eligibility": outcome["axis_test_eligibility"],
                "next_action": outcome["next_action"],
            }
        )
    return consolidated


def summarize_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "consolidation_outcome": Counter(row["consolidation_outcome"] for row in rows),
        "coordinate_status": Counter(row["coordinate_status"] for row in rows),
        "evidence_status": Counter(row["evidence_status"] for row in rows),
        "axis_test_eligibility": Counter(row["axis_test_eligibility"] for row in rows),
        "prefix_family": Counter(row.get("prefix_family", "") for row in rows),
    }


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "route10_id",
        "manual_review_id",
        "decision_id",
        "crop_id",
        "source_review_id",
        "folio",
        "locus",
        "prefix_family",
        "axis_coverage",
        "group_tokens",
        "missing_group_tokens",
        "manual_final_status",
        "manual_tighter_x",
        "manual_tighter_y",
        "manual_tighter_width",
        "manual_tighter_height",
        "manual_target_tokens_seen",
        "manual_missing_tokens_seen",
        "consolidation_outcome",
        "coordinate_status",
        "evidence_status",
        "axis_test_eligibility",
        "next_action",
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


def write_report(
    path: Path,
    rows: list[dict[str, str]],
    source_csv: Path,
    output_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_rows(rows)
    eligible = summary["axis_test_eligibility"].get("eligible_after_manual_review", 0)
    pending = summary["consolidation_outcome"].get("pending_manual_review", 0)
    lines = [
        "# Rota 10: consolidacao da revisao manual",
        "",
        "Esta rota consolida a folha manual da Rota 9. Ela valida status e coordenadas, mas nao cria confirmacao visual por inferencia.",
        "",
        f"Fonte: `{source_csv}`.",
        f"CSV consolidado: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens consolidados: {len(rows)};",
        f"- itens ainda pendentes: {pending};",
        f"- itens elegiveis para teste visual dos eixos: {eligible};",
        "- nenhuma leitura semantica foi atribuida.",
        "",
    ]
    lines.extend(render_counts("Resultado de consolidacao", summary["consolidation_outcome"]))
    lines.extend(render_counts("Status de coordenada", summary["coordinate_status"]))
    lines.extend(render_counts("Evidencia visual", summary["evidence_status"]))
    lines.extend(render_counts("Elegibilidade para teste dos eixos", summary["axis_test_eligibility"]))
    lines.extend(
        [
            "## Linhas consolidadas",
            "",
            "|rota10|manual|crop|familia|folio|locus|status manual|resultado|coordenada|elegivel|",
            "|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['route10_id']}|{row['manual_review_id']}|{row['crop_id']}|{row['prefix_family']}|{row['folio']}|{row['locus']}|{row['manual_final_status']}|{row['consolidation_outcome']}|{row['coordinate_status']}|{row['axis_test_eligibility']}|"
        )
    lines.extend(
        [
            "",
            "## Leitura provisoria",
            "",
            "- A Rota 10 confirma apenas o estado da revisao, nao o glifo.",
            "- Com todos os itens ainda pendentes, nenhum par deve entrar em teste visual fino dos eixos `a/o` ou `r/l`.",
            "- A proxima etapa pode preencher a folha manual ou ampliar a busca por recortes melhores nos mesmos folios.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manual_review_csv", help="CSV from prepare_manual_svg_review.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "manual_svg_review_consolidated_zl3b.csv"),
        help="Consolidated per-row CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "manual_review_status_summary_zl3b.csv"),
        help="Status summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_10_consolidacao_manual.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = Path(args.manual_review_csv)
    consolidated = build_consolidated_rows(read_csv(source))
    summary = summarize_rows(consolidated)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, consolidated)
    write_summary_csv(summary_path, summary)
    write_report(md_path, consolidated, source, csv_path, summary_path)
    eligible = summary["axis_test_eligibility"].get("eligible_after_manual_review", 0)
    print(f"manual_rows={len(consolidated)} eligible_for_axis_tests={eligible}")
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
