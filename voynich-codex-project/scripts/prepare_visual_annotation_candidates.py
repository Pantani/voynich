#!/usr/bin/env python3
"""Prepare a visual-annotation candidate list from matrix context rows."""
from __future__ import annotations

import argparse
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
KEY_TOKENS = {
    "okar",
    "okal",
    "okor",
    "okol",
    "otar",
    "otal",
    "otor",
    "otol",
    "qokar",
    "qokal",
    "qokor",
    "qokol",
    "ar",
    "al",
    "or",
    "ol",
}
VISUAL_LOCUS_KINDS = {"C", "R", "L", "rubrica"}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def manifest_folios(paths: list[Path]) -> set[str]:
    folios: set[str] = set()
    for path in paths:
        if not path.exists():
            continue
        for row in read_csv(path):
            value = row.get("folio", "")
            for part in value.replace("-", "_").split("_"):
                if part.startswith("f"):
                    folios.add(part)
            if value.startswith("f"):
                folios.add(value)
    return folios


def score_row(row: dict[str, str], image_folios: set[str]) -> int:
    score = 0
    if row["locus_kind"] in VISUAL_LOCUS_KINDS:
        score += 5
    if row["target_status"] == "exact":
        score += 4
    elif row["target_status"] == "standalone":
        score += 3
    if row["token"] in KEY_TOKENS:
        score += 3
    if row["line_position"] in {"start", "end", "single"}:
        score += 1
    if row["folio"] in image_folios:
        score += 2
    if row["locus_kind"] == "C" and row["suffix"] == "ar":
        score += 2
    if row["locus_kind"] == "P" and row["suffix"] == "ol":
        score += 1
    return score


def select_candidates(rows: list[dict[str, str]], image_folios: set[str], limit: int) -> list[dict[str, str]]:
    scored: list[tuple[int, dict[str, str]]] = []
    for row in rows:
        score = score_row(row, image_folios)
        if score >= 6:
            scored.append((score, row))
    scored.sort(
        key=lambda item: (
            -item[0],
            item[1]["locus_kind"],
            item[1]["folio"],
            item[1]["locus"],
            item[1]["token"],
        )
    )

    selected: list[dict[str, str]] = []
    seen_loci: set[tuple[str, str, str]] = set()
    for score, row in scored:
        key = (row["folio"], row["locus"], row["token"])
        if key in seen_loci:
            continue
        seen_loci.add(key)
        selected.append(
            {
                "score": str(score),
                "folio": row["folio"],
                "locus": row["locus"],
                "locus_kind": row["locus_kind"],
                "visual_context_from_locus": row["visual_context"],
                "token": row["token"],
                "target_status": row["target_status"],
                "prefix": row["prefix"],
                "suffix": row["suffix"],
                "line_position": row["line_position"],
                "previous_token": row["previous_token"],
                "next_token": row["next_token"],
                "line_tokens": row["line_tokens"],
                "image_checked": "",
                "image_file_or_url": "",
                "ink_color": "",
                "visual_zone": "",
                "ring": "",
                "sector": "",
                "radius": "",
                "object_nearby": "",
                "visual_notes": "",
                "annotation_confidence": "",
            }
        )
        if len(selected) >= limit:
            break
    return selected


def write_candidates(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "score",
        "folio",
        "locus",
        "locus_kind",
        "visual_context_from_locus",
        "token",
        "target_status",
        "prefix",
        "suffix",
        "line_position",
        "previous_token",
        "next_token",
        "line_tokens",
        "image_checked",
        "image_file_or_url",
        "ink_color",
        "visual_zone",
        "ring",
        "sector",
        "radius",
        "object_nearby",
        "visual_notes",
        "annotation_confidence",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_report(path: Path, candidates: list[dict[str, str]], source_csv: Path) -> None:
    folios = sorted({row["folio"] for row in candidates})
    lines = [
        "# Rota 3: preparacao da anotacao visual",
        "",
        "Este arquivo prepara a anotacao visual manual sem preencher campos por suposicao. A lista abaixo foi ranqueada a partir da tabela contextual e dos controles da Rota 2.",
        "",
        f"Fonte: `{source_csv}`.",
        f"Candidatos selecionados: {len(candidates)}.",
        f"Folios cobertos: {', '.join(folios[:60])}.",
        "",
        "CSV de trabalho:",
        "",
        "- `data/annotations/visual_annotation_candidates_zl3b.csv`",
        "",
        "## Como anotar",
        "",
        "Preencher manualmente, olhando a imagem do folio:",
        "",
        "- `image_checked`: `yes` quando a imagem foi conferida;",
        "- `image_file_or_url`: arquivo local ou URL usada;",
        "- `ink_color`: marrom, vermelho, azul, verde etc.;",
        "- `visual_zone`: anel, setor, raio, margem, rótulo, corpo do paragrafo;",
        "- `ring`, `sector`, `radius`: quando aplicavel;",
        "- `object_nearby`: estrela, lua, planta, recipiente, figura, linha radial etc.;",
        "- `visual_notes`: observacao curta sem interpretar como traducao;",
        "- `annotation_confidence`: baixa, media ou alta.",
        "",
        "## Primeiros candidatos",
        "",
        "|score|folio|locus|kind|token|suffix|status|line_position|",
        "|---:|---|---|---|---|---|---|---|",
    ]
    for row in candidates[:40]:
        lines.append(
            f"|{row['score']}|{row['folio']}|{row['locus']}|{row['locus_kind']}|{row['token']}|{row['suffix']}|{row['target_status']}|{row['line_position']}|"
        )
    lines.extend(
        [
            "",
            "## Criterio de selecao",
            "",
            "- priorizar `C`, `R`, `L` e rubricas;",
            "- priorizar tokens exatos e valores standalone;",
            "- priorizar familias `ok/ot/qok` e valores `ar/al/or/ol`;",
            "- dar leve bonus a folios que ja estao nos manifests de imagem;",
            "- nao preencher nenhum campo visual automaticamente.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", help="Context CSV from build_matrix_context_table.py")
    parser.add_argument(
        "--out",
        default=str(ROOT / "data" / "annotations" / "visual_annotation_candidates_zl3b.csv"),
        help="Candidate CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_3_anotacao_visual.md"),
        help="Markdown report output",
    )
    parser.add_argument("--limit", type=int, default=160, help="Maximum candidate rows")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    source_csv = Path(args.input_csv)
    image_folios = manifest_folios(
        [ROOT / "data" / "image_sources.csv", ROOT / "data" / "commons_image_sources.csv"]
    )
    rows = read_csv(source_csv)
    candidates = select_candidates(rows, image_folios, args.limit)
    write_candidates(Path(args.out), candidates)
    write_report(Path(args.md), candidates, source_csv)
    print(f"rows={len(rows)} candidates={len(candidates)}")
    print(f"csv={args.out}")
    print(f"md={args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
