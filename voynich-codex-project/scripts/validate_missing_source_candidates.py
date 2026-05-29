#!/usr/bin/env python3
"""Validate candidate source-image URLs and apply verified rows to a derived manifest."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "source_validation_not_visual_evidence"

FIELDNAMES = [
    "route30_id",
    "route29_id",
    "route28_id",
    "route27_id",
    "folio",
    "locus_kind",
    "priority_level",
    "gap_rows",
    "unique_loci",
    "token_counts",
    "candidate_commons_page",
    "candidate_image_url",
    "candidate_source_valid",
    "source_validation_status",
    "validation_reason",
    "apply_status",
    "manifest_action",
    "semantic_guardrail",
]

MANIFEST_FIELDNAMES = [
    "folio",
    "theme",
    "commons_page",
    "image_url",
    "why_included",
    "license_note",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def is_commons_file_page(url: str) -> bool:
    parsed = urlparse(url)
    return (
        parsed.scheme == "https"
        and parsed.netloc == "commons.wikimedia.org"
        and parsed.path.startswith("/wiki/File:")
    )


def is_commons_upload_image(url: str) -> bool:
    parsed = urlparse(url)
    suffix = parsed.path.lower()
    return (
        parsed.scheme == "https"
        and parsed.netloc == "upload.wikimedia.org"
        and parsed.path.startswith("/wikipedia/commons/")
        and suffix.endswith((".jpg", ".jpeg", ".png"))
    )


def validate_candidate(commons_page: str, image_url: str) -> tuple[str, str, str, str]:
    if not commons_page and not image_url:
        return (
            "no",
            "pending_blank_source_candidate",
            "candidate_fields_blank",
            "skipped_blank_source_candidate",
        )
    if not commons_page or not image_url:
        return (
            "no",
            "invalid_candidate_source",
            "candidate_source_fields_incomplete",
            "skipped_invalid_source_candidate",
        )
    if not is_commons_file_page(commons_page):
        return (
            "no",
            "invalid_candidate_source",
            "candidate_commons_page_not_commons_file",
            "skipped_invalid_source_candidate",
        )
    if not is_commons_upload_image(image_url):
        return (
            "no",
            "invalid_candidate_source",
            "candidate_image_url_not_commons_upload_image",
            "skipped_invalid_source_candidate",
        )
    return (
        "yes",
        "valid_candidate_source",
        "candidate_source_structurally_valid",
        "manifest_row_appended",
    )


def build_source_validation_rows(source_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for source in source_rows:
        commons_page = source.get("candidate_commons_page", "")
        image_url = source.get("candidate_image_url", "")
        valid, status, reason, apply_status = validate_candidate(commons_page, image_url)
        rows.append(
            {
                "route30_id": f"R30-{len(rows) + 1:03d}",
                "route29_id": source.get("route29_id", ""),
                "route28_id": source.get("route28_id", ""),
                "route27_id": source.get("route27_id", ""),
                "folio": source.get("folio", ""),
                "locus_kind": source.get("locus_kind", ""),
                "priority_level": source.get("priority_level", ""),
                "gap_rows": source.get("gap_rows", ""),
                "unique_loci": source.get("unique_loci", ""),
                "token_counts": source.get("token_counts", ""),
                "candidate_commons_page": commons_page,
                "candidate_image_url": image_url,
                "candidate_source_valid": valid,
                "source_validation_status": status,
                "validation_reason": reason,
                "apply_status": apply_status,
                "manifest_action": "append_to_derived_manifest_only" if valid == "yes" else "no_manifest_change",
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def apply_validated_sources_to_manifest(
    manifest_rows: list[dict[str, str]],
    validation_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    existing_folios = {row.get("folio", "") for row in manifest_rows}
    updated = [dict(row) for row in manifest_rows]
    for row in validation_rows:
        folio = row.get("folio", "")
        if row.get("candidate_source_valid") != "yes" or folio in existing_folios:
            continue
        updated.append(
            {
                "folio": folio,
                "theme": "route30 verified source",
                "commons_page": row.get("candidate_commons_page", ""),
                "image_url": row.get("candidate_image_url", ""),
                "why_included": f"{row.get('route30_id', '')} verified candidate for exact ok/ot visual annotation package",
                "license_note": "Commons: consultar licença na página do arquivo; crédito recomendado Yale/Beinecke",
            }
        )
        existing_folios.add(folio)
    return updated


def summarize_source_validation_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "source_validation_status": Counter(row.get("source_validation_status", "") for row in rows),
        "apply_status": Counter(row.get("apply_status", "") for row in rows),
        "candidate_source_valid": Counter(row.get("candidate_source_valid", "") for row in rows),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "locus_kind": Counter(row.get("locus_kind", "") for row in rows),
        "manifest_action": Counter(row.get("manifest_action", "") for row in rows),
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
    source_queue_csv: Path,
    manifest_csv: Path,
    validation_csv: Path,
    derived_manifest_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_source_validation_rows(validation_rows)
    lines = [
        "# Rota 30: validacao de fontes candidatas",
        "",
        "Esta rota valida candidatos da Rota 29 e aplica somente fontes estruturalmente validas a uma copia derivada do manifesto. Ela nao confirma conteudo visual nem atualiza o manifesto original.",
        "",
        f"Fila R29: `{source_queue_csv}`.",
        f"Manifesto original: `{manifest_csv}`.",
        f"Log de validacao: `{validation_csv}`.",
        f"Manifesto derivado: `{derived_manifest_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- candidatos avaliados: {len(validation_rows)};",
        f"- pendentes vazios: {summary['source_validation_status'].get('pending_blank_source_candidate', 0)};",
        f"- validos estruturalmente: {summary['source_validation_status'].get('valid_candidate_source', 0)};",
        f"- invalidos: {summary['source_validation_status'].get('invalid_candidate_source', 0)};",
        f"- linhas anexadas ao manifesto derivado: {summary['apply_status'].get('manifest_row_appended', 0)};",
        "- guarda: `source_validation_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Status de validacao", summary["source_validation_status"]))
    lines.extend(render_counts("Aplicacao", summary["apply_status"]))
    lines.extend(render_counts("Validade do candidato", summary["candidate_source_valid"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota30|rota29|folio|status|aplicacao|motivo|",
            "|---|---|---|---|---|---|",
        ]
    )
    for row in validation_rows:
        lines.append(
            f"|{row['route30_id']}|{row['route29_id']}|{row['folio']}|{row['source_validation_status']}|{row['apply_status']}|{row['validation_reason']}|"
        )
    lines.extend(
        [
            "",
            "## Leitura",
            "",
            "Campos vazios continuam pendentes. URLs com formato correto ainda sao apenas fontes candidatas estruturalmente validas; a anotacao visual continua exigindo revisao separada.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source_queue_csv", help="CSV generated by prepare_missing_source_image_queue.py")
    parser.add_argument("manifest_csv", help="Existing commons image manifest CSV")
    parser.add_argument(
        "--validation-csv",
        default=str(ROOT / "data" / "derived" / "missing_source_candidate_validation_zl3b.csv"),
        help="Validation log CSV output",
    )
    parser.add_argument(
        "--derived-manifest-csv",
        dest="derived_manifest_csv",
        default=str(ROOT / "data" / "derived" / "commons_image_sources_after_source_validation_zl3b.csv"),
        help="Derived manifest output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "missing_source_candidate_validation_summary_zl3b.csv"),
        help="Validation summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_30_validacao_fontes_candidatas.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_queue_csv = Path(args.source_queue_csv)
    original_manifest_csv = Path(args.manifest_csv)
    validation_rows = build_source_validation_rows(read_csv(source_queue_csv))
    derived_manifest_rows = apply_validated_sources_to_manifest(read_csv(original_manifest_csv), validation_rows)
    summary = summarize_source_validation_rows(validation_rows)
    validation_csv = Path(args.validation_csv)
    derived_manifest_csv = Path(args.derived_manifest_csv)
    summary_csv = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(validation_csv, validation_rows, FIELDNAMES)
    write_csv(derived_manifest_csv, derived_manifest_rows, MANIFEST_FIELDNAMES)
    write_summary_csv(summary_csv, summary)
    write_report(md_path, validation_rows, source_queue_csv, original_manifest_csv, validation_csv, derived_manifest_csv, summary_csv)
    print(
        f"candidate_rows={len(validation_rows)} "
        f"pending_blank={summary['source_validation_status'].get('pending_blank_source_candidate', 0)} "
        f"manifest_appended={summary['apply_status'].get('manifest_row_appended', 0)}"
    )
    print(f"validation_csv={validation_csv}")
    print(f"manifest_csv={derived_manifest_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
