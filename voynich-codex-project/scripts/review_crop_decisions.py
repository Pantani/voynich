#!/usr/bin/env python3
"""Record conservative review decisions for R7 rough crop artifacts."""
from __future__ import annotations

import argparse
import csv
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def resolve_path(value: str) -> Path:
    path = Path(value)
    if path.is_absolute():
        return path
    if path.exists():
        return path
    return ROOT / value


def svg_status(path: Path) -> str:
    if not path.exists():
        return "svg_missing"
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError:
        return "svg_invalid"
    if root.tag.endswith("svg"):
        return "svg_ok"
    return "svg_invalid"


def region_label(row: dict[str, str]) -> str:
    return f"x={row.get('crop_x', '')} y={row.get('crop_y', '')} w={row.get('crop_width', '')} h={row.get('crop_height', '')}"


def decision_for_crop(row: dict[str, str], status: str) -> dict[str, str]:
    missing = row.get("missing_group_tokens", "")
    rough = row.get("crop_scope") == "rough_region_only"
    not_isolated = row.get("isolation_status") == "needs_exact_glyph_isolation"

    if status != "svg_ok":
        review_decision = "blocked_by_svg"
        coordinate_decision = "no_glyph_coordinates"
        reason = "SVG artifact is missing or invalid; cannot review visual region."
    elif rough or not_isolated:
        review_decision = "keep_not_isolated"
        coordinate_decision = "no_glyph_coordinates"
        reason = "R7 artifact is rough_region_only and prior status is needs_exact_glyph_isolation."
    else:
        review_decision = "manual_review_needed"
        coordinate_decision = "no_glyph_coordinates"
        reason = "No explicit glyph confirmation is present in the manifest."

    return {
        "review_decision": review_decision,
        "coordinate_decision": coordinate_decision,
        "missing_token_status": "missing_tokens_remain" if missing else "no_missing_group_tokens",
        "decision_reason": reason,
        "next_action": "open SVG and mark tighter coordinates manually or keep not-isolated",
    }


def build_decision_rows(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    decisions: list[dict[str, str]] = []
    for index, row in enumerate(rows, start=1):
        status = svg_status(resolve_path(row.get("crop_svg", "")))
        decision = decision_for_crop(row, status)
        decisions.append(
            {
                "decision_id": f"R8-{index:03d}",
                "crop_id": row.get("crop_id", ""),
                "source_review_id": row.get("source_review_id", ""),
                "folio": row.get("folio", ""),
                "locus": row.get("locus", ""),
                "prefix_family": row.get("prefix_family", ""),
                "axis_coverage": row.get("axis_coverage", ""),
                "group_tokens": row.get("group_tokens", ""),
                "matched_annotation_tokens": row.get("matched_annotation_tokens", ""),
                "missing_group_tokens": row.get("missing_group_tokens", ""),
                "previous_isolation_status": row.get("isolation_status", ""),
                "crop_scope": row.get("crop_scope", ""),
                "review_region": region_label(row),
                "crop_svg": row.get("crop_svg", ""),
                "svg_status": status,
                "review_decision": decision["review_decision"],
                "coordinate_decision": decision["coordinate_decision"],
                "missing_token_status": decision["missing_token_status"],
                "decision_reason": decision["decision_reason"],
                "next_action": decision["next_action"],
            }
        )
    return decisions


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "decision_id",
        "crop_id",
        "source_review_id",
        "folio",
        "locus",
        "prefix_family",
        "axis_coverage",
        "group_tokens",
        "matched_annotation_tokens",
        "missing_group_tokens",
        "previous_isolation_status",
        "crop_scope",
        "review_region",
        "crop_svg",
        "svg_status",
        "review_decision",
        "coordinate_decision",
        "missing_token_status",
        "decision_reason",
        "next_action",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_counts(title: str, counts: Counter[str]) -> list[str]:
    lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"|{key}|{value}|")
    lines.append("")
    return lines


def write_report(path: Path, rows: list[dict[str, str]], manifest_source: Path, output_csv: Path) -> None:
    review_counts = Counter(row["review_decision"] for row in rows)
    svg_counts = Counter(row["svg_status"] for row in rows)
    missing_counts = Counter(row["missing_token_status"] for row in rows)
    lines = [
        "# Rota 8: revisao dos recortes",
        "",
        "Esta rota registra a decisao conservadora para cada recorte da Rota 7. Ela valida os SVGs e separa regiao revisavel de coordenada de glifo confirmada.",
        "",
        f"Fonte: `{manifest_source}`.",
        f"CSV de decisoes: `{output_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- recortes avaliados: {len(rows)};",
        f"- decisoes `keep_not_isolated`: {review_counts.get('keep_not_isolated', 0)};",
        f"- SVGs validos: {svg_counts.get('svg_ok', 0)};",
        "- nenhuma coordenada de glifo foi confirmada.",
        "",
    ]
    lines.extend(render_counts("Decisoes", review_counts))
    lines.extend(render_counts("Status dos SVGs", svg_counts))
    lines.extend(render_counts("Tokens faltantes", missing_counts))
    lines.extend(
        [
            "## Decisoes por recorte",
            "",
            "|decisao|crop|review|folio|locus|tokens|faltam|svg|resultado|",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['decision_id']}|{row['crop_id']}|{row['source_review_id']}|{row['folio']}|{row['locus']}|{row['group_tokens']}|{row['missing_group_tokens']}|{row['svg_status']}|{row['review_decision']}|"
        )
    lines.extend(
        [
            "",
            "## Leitura provisoria",
            "",
            "- Os recortes sao validos como regioes revisaveis, mas continuam amplos demais para confirmar palavra/glifo.",
            "- O status `not isolated` permanece para todos os itens.",
            "- A proxima etapa deve ser uma revisao manual assistida: marcar coordenadas mais apertadas dentro dos SVGs ou registrar que o token nao pode ser isolado nessa imagem.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("crop_manifest_csv", help="CSV from prepare_review_crops.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "annotations" / "crop_review_decisions_zl3b.csv"),
        help="Review decisions CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_8_revisao_recortes.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source = Path(args.crop_manifest_csv)
    rows = read_csv(source)
    decisions = build_decision_rows(rows)
    write_csv(Path(args.csv), decisions)
    write_report(Path(args.md), decisions, source, Path(args.csv))
    print(f"review_crops={len(rows)} decisions={len(decisions)}")
    print(f"csv={args.csv}")
    print(f"md={args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
