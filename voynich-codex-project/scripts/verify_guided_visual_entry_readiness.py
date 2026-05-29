#!/usr/bin/env python3
"""Verify route 23 guided HTML is ready for manual route 21 filling."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MANUAL_FIELDS = [
    "manual_token_seen",
    "manual_new_crop_needed",
    "manual_image_insufficient",
    "manual_new_crop_x",
    "manual_new_crop_y",
    "manual_new_crop_width",
    "manual_new_crop_height",
    "manual_notes",
]

GUARDRAIL = "readiness_check_not_visual_evidence"

FIELDNAMES = [
    "route24_id",
    "route23_id",
    "route22_id",
    "route21_id",
    "route19_id",
    "checklist_id",
    "manual_review_id",
    "crop_id",
    "folio",
    "priority_level",
    "target_type",
    "review_target",
    "source_image",
    "source_image_status",
    "crop_svg",
    "crop_svg_status",
    "html_card_check",
    "allowed_values_check",
    "manual_entry_status",
    "readiness_status",
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


def has_manual_values(row: dict[str, str]) -> bool:
    return any(row.get(field, "").strip() != "" for field in MANUAL_FIELDS)


def entry_index(rows: list[dict[str, str]]) -> dict[str, dict[str, str]]:
    return {row.get("route21_id", ""): row for row in rows if row.get("route21_id", "")}


def path_status(rel_path: str, existing_paths: set[str] | None = None, root: Path = ROOT) -> str:
    if not rel_path:
        return "missing"
    if existing_paths is not None:
        return "present" if rel_path in existing_paths else "missing"
    return "present" if (root / rel_path).exists() else "missing"


def html_card_status(row: dict[str, str], html_text: str) -> str:
    required = [row.get("route23_id", ""), row.get("route21_id", ""), row.get("route19_id", "")]
    return "present" if all(value and value in html_text for value in required) else "missing"


def allowed_values_status(row: dict[str, str], html_text: str) -> str:
    allowed = [
        row.get("allowed_manual_token_seen", ""),
        row.get("allowed_manual_new_crop_needed", ""),
        row.get("allowed_manual_image_insufficient", ""),
    ]
    return "present" if all(value and value in html_text for value in allowed) else "missing"


def manual_entry_status(entry: dict[str, str]) -> str:
    return "has_manual_entry" if has_manual_values(entry) else "blank_manual_entry"


def readiness_status(row: dict[str, str]) -> str:
    if row.get("source_image_status") != "present" or row.get("crop_svg_status") != "present":
        return "blocked_missing_asset"
    if row.get("html_card_check") != "present" or row.get("allowed_values_check") != "present":
        return "blocked_missing_html_card"
    if row.get("manual_entry_status") == "has_manual_entry":
        return "manual_entry_already_present"
    return "ready_for_manual_fill"


def next_action(status: str) -> str:
    if status == "manual_entry_already_present":
        return "rerun_route_22_to_validate_manual_entries"
    if status == "blocked_missing_asset":
        return "repair_missing_image_or_svg_before_manual_fill"
    if status == "blocked_missing_html_card":
        return "regenerate_guided_html_before_manual_fill"
    return "fill_r21_csv_manually_using_guided_html_then_rerun_route_22"


def build_readiness_rows(
    manifest_rows: list[dict[str, str]],
    entry_rows: list[dict[str, str]],
    html_text: str,
    existing_paths: set[str] | None = None,
) -> list[dict[str, str]]:
    entries_by_route21 = entry_index(entry_rows)
    rows: list[dict[str, str]] = []
    for index, manifest in enumerate(manifest_rows, start=1):
        entry = entries_by_route21.get(manifest.get("route21_id", ""), {})
        row = {
            "route24_id": f"R24-{index:03d}",
            "route23_id": manifest.get("route23_id", ""),
            "route22_id": manifest.get("route22_id", ""),
            "route21_id": manifest.get("route21_id", ""),
            "route19_id": manifest.get("route19_id", ""),
            "checklist_id": manifest.get("checklist_id", ""),
            "manual_review_id": manifest.get("manual_review_id", ""),
            "crop_id": manifest.get("crop_id", ""),
            "folio": manifest.get("folio", ""),
            "priority_level": manifest.get("priority_level", ""),
            "target_type": manifest.get("target_type", ""),
            "review_target": manifest.get("review_target", ""),
            "source_image": manifest.get("source_image", ""),
            "source_image_status": path_status(manifest.get("source_image", ""), existing_paths=existing_paths),
            "crop_svg": manifest.get("crop_svg", ""),
            "crop_svg_status": path_status(manifest.get("crop_svg", ""), existing_paths=existing_paths),
            "html_card_check": html_card_status(manifest, html_text),
            "allowed_values_check": allowed_values_status(manifest, html_text),
            "manual_entry_status": manual_entry_status(entry),
            "semantic_guardrail": GUARDRAIL,
        }
        status = readiness_status(row)
        row["readiness_status"] = status
        row["next_action"] = next_action(status)
        rows.append(row)
    return rows


def summarize_readiness_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "readiness_status": Counter(row.get("readiness_status", "") for row in rows),
        "source_image_status": Counter(row.get("source_image_status", "") for row in rows),
        "crop_svg_status": Counter(row.get("crop_svg_status", "") for row in rows),
        "html_card_check": Counter(row.get("html_card_check", "") for row in rows),
        "manual_entry_status": Counter(row.get("manual_entry_status", "") for row in rows),
        "priority_level": Counter(row.get("priority_level", "") for row in rows),
        "folio": Counter(row.get("folio", "") for row in rows),
        "target_type": Counter(row.get("target_type", "") for row in rows),
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


def render_readiness_section(row: dict[str, str]) -> str:
    lines = [
        f"## {row['route24_id']} / {row.get('route23_id', '')} / {row.get('route21_id', '')}",
        "",
        f"- prontidao: `{row.get('readiness_status', '')}`;",
        f"- imagem fonte: `{row.get('source_image_status', '')}`;",
        f"- SVG: `{row.get('crop_svg_status', '')}`;",
        f"- cartao HTML: `{row.get('html_card_check', '')}`;",
        f"- entrada manual: `{row.get('manual_entry_status', '')}`;",
        f"- proxima acao: `{row.get('next_action', '')}`;",
        f"- guarda: `{row.get('semantic_guardrail', '')}`;",
        "",
    ]
    return "\n".join(lines)


def write_report(
    path: Path,
    rows: list[dict[str, str]],
    manifest_csv: Path,
    entry_sheet_csv: Path,
    html_path: Path,
    output_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_readiness_rows(rows)
    lines = [
        "# Rota 24: prontidao para preenchimento visual R21",
        "",
        "Esta rota verifica se o pacote HTML R23 esta pronto para preencher manualmente a planilha R21. Ela nao interpreta glifos e nao grava decisoes.",
        "",
        f"Manifest R23: `{manifest_csv}`.",
        f"Planilha R21: `{entry_sheet_csv}`.",
        f"HTML guiado: `{html_path}`.",
        f"Checklist de prontidao: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens verificados: {len(rows)};",
        f"- prontos para preenchimento manual: {summary['readiness_status'].get('ready_for_manual_fill', 0)};",
        f"- ja preenchidos: {summary['readiness_status'].get('manual_entry_already_present', 0)};",
        f"- bloqueados por asset: {summary['readiness_status'].get('blocked_missing_asset', 0)};",
        f"- bloqueados por HTML: {summary['readiness_status'].get('blocked_missing_html_card', 0)};",
        "- guarda: `readiness_check_not_visual_evidence`.",
        "",
    ]
    lines.extend(render_counts("Prontidao", summary["readiness_status"]))
    lines.extend(render_counts("Imagem fonte", summary["source_image_status"]))
    lines.extend(render_counts("SVG", summary["crop_svg_status"]))
    lines.extend(render_counts("Entrada manual", summary["manual_entry_status"]))
    lines.extend(render_counts("Prioridade", summary["priority_level"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota24|rota23|rota21|checklist|prioridade|folio|imagem|svg|html|entrada|prontidao|",
            "|---|---|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['route24_id']}|{row['route23_id']}|{row['route21_id']}|{row['checklist_id']}|{row['priority_level']}|{row['folio']}|{row['source_image_status']}|{row['crop_svg_status']}|{row['html_card_check']}|{row['manual_entry_status']}|{row['readiness_status']}|"
        )
    lines.append("")
    for row in rows:
        lines.append(render_readiness_section(row))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("guided_manifest_csv", help="CSV from prepare_guided_visual_entry_html.py")
    parser.add_argument("entry_sheet_csv", help="Route 21 visual decision entry sheet CSV")
    parser.add_argument("guided_html", help="Route 23 guided HTML")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "guided_visual_entry_readiness_zl3b.csv"),
        help="Readiness CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "guided_visual_entry_readiness_summary_zl3b.csv"),
        help="Readiness summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_24_prontidao_preenchimento_visual.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    manifest_csv = Path(args.guided_manifest_csv)
    entry_sheet_csv = Path(args.entry_sheet_csv)
    html_path = Path(args.guided_html)
    rows = build_readiness_rows(read_csv(manifest_csv), read_csv(entry_sheet_csv), html_path.read_text(encoding="utf-8"))
    summary = summarize_readiness_rows(rows)
    csv_path = Path(args.csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(csv_path, rows, FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_report(md_path, rows, manifest_csv, entry_sheet_csv, html_path, csv_path, summary_path)
    print(
        f"readiness_rows={len(rows)} "
        f"ready={summary['readiness_status'].get('ready_for_manual_fill', 0)} "
        f"manual_present={summary['readiness_status'].get('manual_entry_already_present', 0)} "
        f"blocked_asset={summary['readiness_status'].get('blocked_missing_asset', 0)} "
        f"blocked_html={summary['readiness_status'].get('blocked_missing_html_card', 0)}"
    )
    print(f"csv={csv_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
