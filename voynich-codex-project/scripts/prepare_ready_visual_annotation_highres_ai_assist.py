#!/usr/bin/env python3
"""Prepare an AI-assisted high-resolution visual review note for route 32."""
from __future__ import annotations

import argparse
import csv
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

GUARDRAIL = "ai_highres_visual_assist_not_human_evidence"
CHAIN_BLOCKED = "blocked_waiting_human_r32_entry"
CHAIN_HAS_MANUAL_ENTRY = "manual_entry_present_verify_with_r36_r37_r39_r40"
EXACT_TOKEN_DECISION = "not_determined_requires_human_zoom"

FIELDNAMES = [
    "route42a_id",
    "route42_id",
    "route32_id",
    "route28_id",
    "folio",
    "priority_level",
    "locus_kind",
    "token_counts",
    "top_loci",
    "manifest_label",
    "yale_image_id",
    "local_image_path",
    "image_quality_assist",
    "target_region_locatable_assist",
    "exact_token_decision_assist",
    "visual_context_assist",
    "suggested_manual_review_action",
    "chain_status",
    "manual_annotation_status",
    "manual_visual_notes",
    "semantic_guardrail",
]

FOLIO_OBSERVATIONS = {
    "f99v": {
        "image_quality_assist": "high",
        "target_region_locatable_assist": "partial",
        "visual_context_assist": "label_and_paragraph_bands_visible",
        "suggested_manual_review_action": "crop_label_rows_and_match_petersen_lines",
    },
    "f1r": {
        "image_quality_assist": "medium_faint",
        "target_region_locatable_assist": "partial",
        "visual_context_assist": "faded_paragraph_text_visible",
        "suggested_manual_review_action": "increase_contrast_crop_paragraph_starts",
    },
    "f67r2": {
        "image_quality_assist": "high",
        "target_region_locatable_assist": "partial",
        "visual_context_assist": "circular_sector_text_and_red_line_visible",
        "suggested_manual_review_action": "rotate_crop_sector_and_red_line",
    },
    "f67v1": {
        "image_quality_assist": "high",
        "target_region_locatable_assist": "partial",
        "visual_context_assist": "circular_labels_and_star_diagram_visible",
        "suggested_manual_review_action": "rotate_crop_circle_labels",
    },
    "f84r": {
        "image_quality_assist": "high",
        "target_region_locatable_assist": "yes_region",
        "visual_context_assist": "nymph_labels_and_body_text_visible",
        "suggested_manual_review_action": "crop_upper_pool_text_lines",
    },
    "f88v": {
        "image_quality_assist": "medium_composite",
        "target_region_locatable_assist": "partial_composite_page",
        "visual_context_assist": "composite_foldout_recipe_rows_visible_but_side_mapping_required",
        "suggested_manual_review_action": "crop_composite_foldout_recipe_rows",
    },
    "f89r2": {
        "image_quality_assist": "medium_composite",
        "target_region_locatable_assist": "partial_composite_page",
        "visual_context_assist": "pharmaceutical_foldout_sections_visible_but_side_mapping_required",
        "suggested_manual_review_action": "crop_composite_foldout_plant_rows",
    },
    "f99r": {
        "image_quality_assist": "high",
        "target_region_locatable_assist": "yes_region",
        "visual_context_assist": "top_label_row_and_body_text_visible",
        "suggested_manual_review_action": "crop_top_label_row",
    },
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def manual_chain_status(row: dict[str, str]) -> str:
    status = row.get("manual_annotation_status", "").strip()
    notes = row.get("manual_visual_notes", "").strip()
    if status and notes:
        return CHAIN_HAS_MANUAL_ENTRY
    return CHAIN_BLOCKED


def build_ai_assist_rows(highres_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for highres in highres_rows:
        folio = highres.get("folio", "")
        observation = FOLIO_OBSERVATIONS.get(
            folio,
            {
                "image_quality_assist": "unknown",
                "target_region_locatable_assist": "unknown",
                "visual_context_assist": "not_reviewed",
                "suggested_manual_review_action": "review_highres_source_manually",
            },
        )
        rows.append(
            {
                "route42a_id": f"R42A-{len(rows) + 1:03d}",
                "route42_id": highres.get("route42_id", ""),
                "route32_id": highres.get("route32_id", ""),
                "route28_id": highres.get("route28_id", ""),
                "folio": folio,
                "priority_level": highres.get("priority_level", ""),
                "locus_kind": highres.get("locus_kind", ""),
                "token_counts": highres.get("token_counts", ""),
                "top_loci": highres.get("top_loci", ""),
                "manifest_label": highres.get("manifest_label", ""),
                "yale_image_id": highres.get("yale_image_id", ""),
                "local_image_path": highres.get("local_image_path", ""),
                "image_quality_assist": observation["image_quality_assist"],
                "target_region_locatable_assist": observation["target_region_locatable_assist"],
                "exact_token_decision_assist": EXACT_TOKEN_DECISION,
                "visual_context_assist": observation["visual_context_assist"],
                "suggested_manual_review_action": observation["suggested_manual_review_action"],
                "chain_status": manual_chain_status(highres),
                "manual_annotation_status": highres.get("manual_annotation_status", ""),
                "manual_visual_notes": highres.get("manual_visual_notes", ""),
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def summarize_ai_assist_rows(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "image_quality_assist": Counter(row.get("image_quality_assist", "") for row in rows),
        "target_region_locatable_assist": Counter(row.get("target_region_locatable_assist", "") for row in rows),
        "exact_token_decision_assist": Counter(row.get("exact_token_decision_assist", "") for row in rows),
        "suggested_manual_review_action": Counter(row.get("suggested_manual_review_action", "") for row in rows),
        "chain_status": Counter(row.get("chain_status", "") for row in rows),
        "semantic_guardrail": Counter(row.get("semantic_guardrail", "") for row in rows),
    }


def write_summary_csv(path: Path, summary: dict[str, Counter[str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["metric", "item", "n"])
        writer.writeheader()
        for metric, counts in summary.items():
            for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
                writer.writerow({"metric": metric, "item": key, "n": value})


def markdown_cell(value: str) -> str:
    return value.replace("|", "<br>")


def render_counts(title: str, counts: Counter[str]) -> list[str]:
    lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"|{markdown_cell(key)}|{value}|")
    lines.append("")
    return lines


def write_markdown_report(path: Path, rows: list[dict[str, str]], source_csv: Path, output_csv: Path, summary_csv: Path) -> None:
    summary = summarize_ai_assist_rows(rows)
    lines = [
        "# Rota 42A: analise assistida das fontes Yale high-res para R32",
        "",
        "Esta camada registra uma leitura visual assistida das imagens Yale/Beinecke baixadas na R42. Ela serve para orientar recorte, zoom e revisao humana. Ela nao preenche a R32, nao decide `annotated/not_visible/uncertain` e nao reabre a cadeia.",
        "",
        f"Fonte R42: `{source_csv}`.",
        f"CSV R42A: `{output_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- itens avaliados: {len(rows)};",
        f"- regioes claramente localizaveis: {summary['target_region_locatable_assist'].get('yes_region', 0)};",
        f"- regioes parcialmente localizaveis: {summary['target_region_locatable_assist'].get('partial', 0)};",
        f"- paginas compostas que exigem recorte/lado: {summary['target_region_locatable_assist'].get('partial_composite_page', 0)};",
        f"- decisoes exatas de token tomadas pela IA: 0;",
        f"- cadeia ainda bloqueada: {summary['chain_status'].get(CHAIN_BLOCKED, 0)};",
        f"- guarda: `{GUARDRAIL}`.",
        "",
        "## Leitura",
        "",
        "As fontes novas melhoram o trabalho de revisao. `f84r` e `f99r` ficaram com regioes de interesse prontas para recorte local; `f99v`, `f67r2` e `f67v1` tambem ficaram uteis, mas precisam de alinhamento fino de linhas, setores ou circulos. `f1r` continua relativamente apagado. `f88v` e `f89r2` exigem cuidado extra porque usam a mesma imagem composta Yale `88v and 89r`.",
        "",
        "Nenhum item abaixo e uma anotacao manual. O proximo passo correto ainda e uma pessoa preencher `manual_annotation_status` e `manual_visual_notes` na R32 usando as fontes high-res.",
        "",
    ]
    lines.extend(render_counts("Qualidade visual assistida", summary["image_quality_assist"]))
    lines.extend(render_counts("Localizacao assistida da regiao", summary["target_region_locatable_assist"]))
    lines.extend(render_counts("Acoes manuais sugeridas", summary["suggested_manual_review_action"]))
    lines.extend(
        [
            "## Itens",
            "",
            "|rota42A|rota32|folio|qualidade|regiao|decisao exata|acao manual sugerida|",
            "|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['route42a_id']}|{row['route32_id']}|{row['folio']}|{row['image_quality_assist']}|{row['target_region_locatable_assist']}|{row['exact_token_decision_assist']}|{row['suggested_manual_review_action']}|"
        )
    lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_highres_sources_zl3b.csv"),
        help="Route 42 high-resolution source CSV",
    )
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_highres_ai_assist_zl3b.csv"),
        help="Route 42A AI-assisted analysis CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "ready_visual_annotation_highres_ai_assist_summary_zl3b.csv"),
        help="Route 42A summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_42a_analise_assistida_highres_r32.md"),
        help="Route 42A Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_csv = Path(args.source_csv)
    output_csv = Path(args.csv)
    summary_csv = Path(args.summary_csv)
    md_path = Path(args.md)
    rows = build_ai_assist_rows(read_csv(source_csv))
    summary = summarize_ai_assist_rows(rows)
    write_csv(output_csv, rows, FIELDNAMES)
    write_summary_csv(summary_csv, summary)
    write_markdown_report(md_path, rows, source_csv, output_csv, summary_csv)
    print(
        f"ai_assist_items={len(rows)} "
        f"yes_region={summary['target_region_locatable_assist'].get('yes_region', 0)} "
        f"partial={summary['target_region_locatable_assist'].get('partial', 0)} "
        f"partial_composite={summary['target_region_locatable_assist'].get('partial_composite_page', 0)} "
        f"chain_blocked={summary['chain_status'].get(CHAIN_BLOCKED, 0)}"
    )
    print(f"csv={output_csv.resolve()}")
    print(f"summary_csv={summary_csv.resolve()}")
    print(f"md={md_path.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
