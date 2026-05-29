#!/usr/bin/env python3
"""Prepare a priority queue for visual annotation gaps in exact ok/ot forms."""
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "visual_gap_priority_not_evidence"
FOLIO_RE = re.compile(r"^(f\d+)([rv]\d*)$")

FIELDNAMES = [
    "route27_id",
    "folio",
    "locus_kind",
    "gap_rows",
    "unique_loci",
    "token_counts",
    "prefix_counts",
    "suffix_counts",
    "line_position_counts",
    "top_loci",
    "section_notes",
    "image_source_status",
    "image_manifest_folio",
    "image_url",
    "commons_page",
    "priority_level",
    "priority_reason",
    "review_action",
    "semantic_guardrail",
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def expand_manifest_folios(folio_key: str) -> set[str]:
    parts = [part for part in folio_key.split("_") if part]
    if not parts:
        return set()
    expanded: set[str] = set()
    current_prefix = ""
    for part in parts:
        match = FOLIO_RE.match(part)
        if match:
            current_prefix = match.group(1)
            expanded.add(part)
            continue
        if current_prefix and re.match(r"^[rv]\d*$", part):
            expanded.add(f"{current_prefix}{part}")
    return expanded or {folio_key}


def image_manifest_index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    index: dict[str, dict[str, str]] = {}
    for row in rows:
        manifest_folio = row.get("folio", "")
        for folio in expand_manifest_folios(manifest_folio):
            indexed = dict(row)
            indexed["manifest_folio"] = manifest_folio
            index[folio] = indexed
    return index


def count_string(counter: Counter[str]) -> str:
    return "|".join(f"{key}={value}" for key, value in sorted(counter.items(), key=lambda item: (-item[1], item[0])))


def compact_values(values: list[str], limit: int = 5) -> str:
    unique = []
    seen = set()
    for value in values:
        if not value or value in seen:
            continue
        unique.append(value)
        seen.add(value)
        if len(unique) >= limit:
            break
    return "|".join(unique)


def markdown_cell(value: str) -> str:
    return value.replace("|", "<br>")


def priority_level(gap_rows: int, image_source_status: str) -> str:
    if image_source_status == "manifest_available" and gap_rows >= 5:
        return "P0"
    if image_source_status == "manifest_available" and gap_rows >= 2:
        return "P1"
    if image_source_status != "manifest_available" and gap_rows >= 10:
        return "P1"
    if image_source_status == "manifest_available":
        return "P2"
    return "P3"


def priority_reason(level: str, gap_rows: int, image_source_status: str) -> str:
    if level == "P0":
        return "many_gaps_and_manifest_image_available"
    if level == "P1" and image_source_status == "manifest_available":
        return "some_gaps_and_manifest_image_available"
    if level == "P1":
        return "many_gaps_but_no_manifest_image"
    if level == "P2":
        return "single_gap_with_manifest_image_available"
    return "low_count_and_no_manifest_image"


def build_gap_queue_rows(
    exact_rows: list[dict[str, str]],
    manifest_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    manifest_by_folio = image_manifest_index(manifest_rows)
    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in exact_rows:
        if row.get("visual_match_status") != "no_visual_annotation":
            continue
        groups[(row.get("folio", ""), row.get("locus_kind", ""))].append(row)

    queue: list[dict[str, str]] = []
    for (folio, locus_kind), rows in groups.items():
        manifest = manifest_by_folio.get(folio, {})
        image_source_status = "manifest_available" if manifest else "not_in_manifest"
        gap_count = len(rows)
        level = priority_level(gap_count, image_source_status)
        loci = [row.get("locus", "") for row in rows]
        notes = [row.get("section_note", "") for row in rows]
        queue.append(
            {
                "route27_id": "",
                "folio": folio,
                "locus_kind": locus_kind,
                "gap_rows": str(gap_count),
                "unique_loci": str(len({locus for locus in loci if locus})),
                "token_counts": count_string(Counter(row.get("token", "") for row in rows)),
                "prefix_counts": count_string(Counter(row.get("prefix", "") for row in rows)),
                "suffix_counts": count_string(Counter(row.get("suffix", "") for row in rows)),
                "line_position_counts": count_string(Counter(row.get("line_position", "") for row in rows)),
                "top_loci": compact_values(loci),
                "section_notes": compact_values(notes, limit=3),
                "image_source_status": image_source_status,
                "image_manifest_folio": manifest.get("manifest_folio", ""),
                "image_url": manifest.get("image_url", ""),
                "commons_page": manifest.get("commons_page", ""),
                "priority_level": level,
                "priority_reason": priority_reason(level, gap_count, image_source_status),
                "review_action": "open_manifest_image_and_add_visual_annotations_for_exact_forms"
                if image_source_status == "manifest_available"
                else "find_or_download_source_image_before_annotation",
                "semantic_guardrail": GUARDRAIL,
            }
        )

    priority_rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    queue.sort(
        key=lambda row: (
            priority_rank.get(row["priority_level"], 9),
            -int(row["gap_rows"]),
            row["folio"],
            row["locus_kind"],
        )
    )
    for index, row in enumerate(queue, start=1):
        row["route27_id"] = f"R27-{index:03d}"
    return queue


def summarize_gap_queue_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "image_source_status": Counter(row.get("image_source_status", "") for row in rows),
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
    rows: list[dict[str, str]],
    exact_table_csv: Path,
    manifest_csv: Path,
    output_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_gap_queue_rows(rows)
    p0 = summary["priority_level"].get("P0", 0)
    p1 = summary["priority_level"].get("P1", 0)
    lines = [
        "# Rota 27: fila de lacunas visuais das formas exatas",
        "",
        "Esta rota prioriza folios/loci das oito formas exatas que ainda nao possuem anotacao visual. Ela cria uma fila de trabalho, nao evidencia.",
        "",
        f"Tabela R26: `{exact_table_csv}`.",
        f"Manifesto de imagens: `{manifest_csv}`.",
        f"Fila: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- grupos de lacuna visual: {len(rows)};",
        f"- P0: {p0};",
        f"- P1: {p1};",
        f"- com imagem no manifesto: {summary['image_source_status'].get('manifest_available', 0)};",
        f"- sem imagem no manifesto: {summary['image_source_status'].get('not_in_manifest', 0)};",
        "- guarda: `visual_gap_priority_not_evidence`.",
        "",
    ]
    lines.extend(render_counts("Prioridade", summary["priority_level"]))
    lines.extend(render_counts("Imagem", summary["image_source_status"]))
    lines.extend(render_counts("Tipo de locus", summary["locus_kind"]))
    lines.extend(
        [
            "## Top 30",
            "",
            "|rota27|prioridade|folio|locus_kind|lacunas|loci|tokens|imagem|acao|",
            "|---|---|---|---|---:|---:|---|---|---|",
        ]
    )
    for row in rows[:30]:
        lines.append(
            f"|{markdown_cell(row['route27_id'])}|{markdown_cell(row['priority_level'])}|{markdown_cell(row['folio'])}|{markdown_cell(row['locus_kind'])}|{markdown_cell(row['gap_rows'])}|{markdown_cell(row['unique_loci'])}|{markdown_cell(row['token_counts'])}|{markdown_cell(row['image_source_status'])}|{markdown_cell(row['review_action'])}|"
        )
    lines.extend(
        [
            "",
            "## Leitura",
            "",
            "A fila seleciona alvos de anotacao visual com base em densidade e disponibilidade de imagem. Ela nao resolve a R21 nem interpreta `ok/ot` ou os sufixos.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("exact_form_context_csv", help="CSV from build_exact_form_context_table.py")
    parser.add_argument("image_manifest_csv", help="Image manifest CSV")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "exact_form_visual_gap_queue_zl3b.csv"),
        help="Visual gap queue CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "exact_form_visual_gap_summary_zl3b.csv"),
        help="Visual gap queue summary output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_27_fila_lacunas_visuais_formas_exatas.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    exact_csv = Path(args.exact_form_context_csv)
    manifest_csv = Path(args.image_manifest_csv)
    rows = build_gap_queue_rows(read_csv(exact_csv), read_csv(manifest_csv))
    summary = summarize_gap_queue_rows(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, rows, FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_report(md_path, rows, exact_csv, manifest_csv, csv_path, summary_path)
    print(
        f"gap_groups={len(rows)} "
        f"p0={summary['priority_level'].get('P0', 0)} "
        f"p1={summary['priority_level'].get('P1', 0)} "
        f"manifest_available={summary['image_source_status'].get('manifest_available', 0)}"
    )
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
