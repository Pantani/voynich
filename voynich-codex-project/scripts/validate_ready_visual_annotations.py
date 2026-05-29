#!/usr/bin/env python3
"""Validate manual visual annotations for route 28 ready items."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "manual_visual_annotation_not_axis_meaning"
ALLOWED_MANUAL_STATUS = {"annotated", "not_visible", "uncertain"}

FIELDNAMES = [
    "route31_id",
    "route28_id",
    "route27_id",
    "folio",
    "locus_kind",
    "priority_level",
    "gap_rows",
    "unique_loci",
    "token_counts",
    "top_loci",
    "image_url",
    "commons_page",
    "manual_annotation_status",
    "manual_source_image_url",
    "manual_visual_notes",
    "manual_annotation_valid",
    "manual_validation_status",
    "validation_reason",
    "apply_status",
    "semantic_guardrail",
]

VALID_ANNOTATION_FIELDNAMES = [
    "route31_id",
    "route28_id",
    "route27_id",
    "folio",
    "locus_kind",
    "priority_level",
    "gap_rows",
    "unique_loci",
    "token_counts",
    "top_loci",
    "image_url",
    "commons_page",
    "manual_annotation_status",
    "manual_source_image_url",
    "manual_visual_notes",
    "semantic_guardrail",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def validate_manual_fields(status: str, notes: str) -> tuple[str, str, str, str]:
    if not status and not notes:
        return (
            "no",
            "pending_blank_manual_annotation",
            "manual_fields_blank",
            "skipped_blank_manual_annotation",
        )
    if status not in ALLOWED_MANUAL_STATUS:
        return (
            "no",
            "invalid_manual_annotation",
            "manual_annotation_status_not_allowed",
            "skipped_invalid_manual_annotation",
        )
    if not notes:
        return (
            "no",
            "invalid_manual_annotation",
            "manual_visual_notes_required_for_filled_status",
            "skipped_invalid_manual_annotation",
        )
    return (
        "yes",
        "valid_manual_annotation",
        "manual_annotation_fields_valid",
        "manual_annotation_recorded",
    )


def build_manual_annotation_rows(package_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    ready = [row for row in package_rows if row.get("package_status") == "ready_for_manual_visual_annotation"]
    rows: list[dict[str, str]] = []
    for row in ready:
        status = row.get("manual_annotation_status", "")
        notes = row.get("manual_visual_notes", "")
        valid, validation_status, reason, apply_status = validate_manual_fields(status, notes)
        rows.append(
            {
                "route31_id": f"R31-{len(rows) + 1:03d}",
                "route28_id": row.get("route28_id", ""),
                "route27_id": row.get("route27_id", ""),
                "folio": row.get("folio", ""),
                "locus_kind": row.get("locus_kind", ""),
                "priority_level": row.get("priority_level", ""),
                "gap_rows": row.get("gap_rows", ""),
                "unique_loci": row.get("unique_loci", ""),
                "token_counts": row.get("token_counts", ""),
                "top_loci": row.get("top_loci", ""),
                "image_url": row.get("image_url", ""),
                "commons_page": row.get("commons_page", ""),
                "manual_annotation_status": status,
                "manual_source_image_url": row.get("manual_source_image_url", ""),
                "manual_visual_notes": notes,
                "manual_annotation_valid": valid,
                "manual_validation_status": validation_status,
                "validation_reason": reason,
                "apply_status": apply_status,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def build_valid_manual_annotations(validation_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    valid_rows: list[dict[str, str]] = []
    for row in validation_rows:
        if row.get("manual_annotation_valid") != "yes":
            continue
        valid_rows.append({field: row.get(field, "") for field in VALID_ANNOTATION_FIELDNAMES})
    return valid_rows


def summarize_manual_annotation_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "manual_validation_status": Counter(row.get("manual_validation_status", "") for row in rows),
        "apply_status": Counter(row.get("apply_status", "") for row in rows),
        "manual_annotation_valid": Counter(row.get("manual_annotation_valid", "") for row in rows),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "locus_kind": Counter(row.get("locus_kind", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
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
        lines.append(f"|{key}|{value}|")
    lines.append("")
    return lines


def write_report(
    path: Path,
    validation_rows: list[dict[str, str]],
    valid_rows: list[dict[str, str]],
    package_csv: Path,
    validation_csv: Path,
    valid_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_manual_annotation_rows(validation_rows)
    lines = [
        "# Rota 31: validacao de anotacoes visuais manuais prontas",
        "",
        "Esta rota valida somente os itens da Rota 28 que ja tinham imagem no manifesto. Campos manuais vazios continuam pendentes e nenhuma anotacao visual e criada por inferencia.",
        "",
        f"Pacote R28: `{package_csv}`.",
        f"Log de validacao: `{validation_csv}`.",
        f"Anotacoes validas derivadas: `{valid_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens prontos avaliados: {len(validation_rows)};",
        f"- pendentes vazios: {summary['manual_validation_status'].get('pending_blank_manual_annotation', 0)};",
        f"- validos: {summary['manual_validation_status'].get('valid_manual_annotation', 0)};",
        f"- invalidos: {summary['manual_validation_status'].get('invalid_manual_annotation', 0)};",
        f"- anotacoes derivadas gravadas: {len(valid_rows)};",
        "- guarda: `manual_visual_annotation_not_axis_meaning`.",
        "",
    ]
    lines.extend(render_counts("Status de validacao", summary["manual_validation_status"]))
    lines.extend(render_counts("Aplicacao", summary["apply_status"]))
    lines.extend(render_counts("Validade manual", summary["manual_annotation_valid"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota31|rota28|folio|status|aplicacao|motivo|",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in validation_rows:
        lines.append(
            f"|{row['route31_id']}|{row['route28_id']}|{row['folio']}|{row['manual_validation_status']}|{row['apply_status']}|{row['validation_reason']}|"
        )
    lines.extend(
        [
            "",
            "## Leitura",
            "",
            "A rota deixa pronta a validacao das anotacoes dos 8 itens com imagem. Enquanto os campos manuais estiverem vazios, nada entra na tabela derivada de anotacoes.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("annotation_package_csv", help="CSV generated by prepare_exact_form_visual_annotation_package.py")
    parser.add_argument(
        "--validation-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_validation_zl3b.csv"),
        help="Validation log CSV output",
    )
    parser.add_argument(
        "--valid-csv",
        default=str(ROOT / "data" / "derived" / "ready_manual_visual_annotations_zl3b.csv"),
        help="Valid manual annotations output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_validation_summary_zl3b.csv"),
        help="Validation summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_31_validacao_anotacoes_visuais_prontas.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    package_csv = Path(args.annotation_package_csv)
    validation_rows = build_manual_annotation_rows(read_csv(package_csv))
    valid_rows = build_valid_manual_annotations(validation_rows)
    summary = summarize_manual_annotation_rows(validation_rows)
    validation_csv = Path(args.validation_csv)
    valid_csv = Path(args.valid_csv)
    summary_csv = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(validation_csv, validation_rows, FIELDNAMES)
    write_csv(valid_csv, valid_rows, VALID_ANNOTATION_FIELDNAMES)
    write_summary_csv(summary_csv, summary)
    write_report(md_path, validation_rows, valid_rows, package_csv, validation_csv, valid_csv, summary_csv)
    print(
        f"ready_items={len(validation_rows)} "
        f"pending_blank={summary['manual_validation_status'].get('pending_blank_manual_annotation', 0)} "
        f"valid_annotations={len(valid_rows)}"
    )
    print(f"validation_csv={validation_csv}")
    print(f"valid_csv={valid_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
