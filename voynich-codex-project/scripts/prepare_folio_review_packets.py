#!/usr/bin/env python3
"""Group second-pass crop targets into folio-level guided review packets."""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def attach_manifest_fields(
    queue_rows: list[dict[str, str]],
    manifest_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    manifest_by_crop = {row.get("crop_id", ""): row for row in manifest_rows}
    attached: list[dict[str, str]] = []
    for row in queue_rows:
        manifest = manifest_by_crop.get(row.get("crop_id", ""), {})
        enriched = dict(row)
        enriched["source_image"] = manifest.get("source_image", "")
        enriched["crop_svg"] = manifest.get("crop_svg", "")
        enriched["review_region"] = manifest.get("review_region", "")
        if not enriched["review_region"] and manifest:
            enriched["review_region"] = (
                f"x={manifest.get('crop_x', '')} y={manifest.get('crop_y', '')} "
                f"w={manifest.get('crop_width', '')} h={manifest.get('crop_height', '')}"
            )
        attached.append(enriched)
    return attached


def unique_join(values: list[str]) -> str:
    return " ".join(dict.fromkeys(value for value in values if value))


def packet_goal(rows: list[dict[str, str]]) -> str:
    strategies = {row.get("crop_strategy", "") for row in rows}
    if "rescan_source_image_before_new_crop" in strategies:
        return "review_source_image_first"
    if "search_single_missing_token_then_redraw_crop" in strategies:
        return "search_tokens_then_redraw_crop"
    return "tighten_current_svg_regions"


def packet_instruction(goal: str) -> str:
    if goal == "review_source_image_first":
        return "Open the source image, search missing tokens, then decide whether a new crop is justified."
    if goal == "search_tokens_then_redraw_crop":
        return "Search each listed missing token and redraw only if the word is visually located."
    return "Use the current SVGs only to mark smaller regions for already matched tokens."


def packet_sort_key(group: list[dict[str, str]]) -> tuple[int, int, str]:
    goal_order = {
        "review_source_image_first": 0,
        "search_tokens_then_redraw_crop": 1,
        "tighten_current_svg_regions": 2,
    }
    goal = packet_goal(group)
    missing_total = sum(int(row.get("missing_token_count", "0") or "0") for row in group)
    folio = group[0].get("folio", "")
    return (goal_order.get(goal, 9), -missing_total, folio)


def build_packets(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    grouped: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        grouped[(row.get("folio", ""), row.get("source_image", ""))].append(row)

    groups = sorted(grouped.values(), key=packet_sort_key)
    packets: list[dict[str, str]] = []
    for index, group in enumerate(groups, start=1):
        goal = packet_goal(group)
        missing_total = sum(int(row.get("missing_token_count", "0") or "0") for row in group)
        packets.append(
            {
                "packet_id": f"R12-{index:03d}",
                "folio": group[0].get("folio", ""),
                "source_image": group[0].get("source_image", ""),
                "item_count": str(len(group)),
                "missing_token_count": str(missing_total),
                "route11_ids": unique_join([row.get("route11_id", "") for row in group]),
                "priority_buckets": unique_join([row.get("priority_bucket", "") for row in group]),
                "focuses": unique_join([row.get("second_pass_focus", "") for row in group]),
                "crop_strategies": unique_join([row.get("crop_strategy", "") for row in group]),
                "packet_goal": goal,
                "packet_instruction": packet_instruction(goal),
                "semantic_guardrail": "folio_packet_is_operational_not_semantic",
            }
        )
    return packets


def build_packet_items(packets: list[dict[str, str]], rows: list[dict[str, str]]) -> list[dict[str, str]]:
    packet_by_route11: dict[str, str] = {}
    for packet in packets:
        for route11_id in packet.get("route11_ids", "").split():
            packet_by_route11[route11_id] = packet.get("packet_id", "")

    items: list[dict[str, str]] = []
    for row in rows:
        items.append(
            {
                "packet_id": packet_by_route11.get(row.get("route11_id", ""), ""),
                "route11_id": row.get("route11_id", ""),
                "route10_id": row.get("route10_id", ""),
                "manual_review_id": row.get("manual_review_id", ""),
                "crop_id": row.get("crop_id", ""),
                "source_review_id": row.get("source_review_id", ""),
                "folio": row.get("folio", ""),
                "locus": row.get("locus", ""),
                "source_image": row.get("source_image", ""),
                "crop_svg": row.get("crop_svg", ""),
                "review_region": row.get("review_region", ""),
                "prefix_family": row.get("prefix_family", ""),
                "axis_coverage": row.get("axis_coverage", ""),
                "group_tokens": row.get("group_tokens", ""),
                "missing_group_tokens": row.get("missing_group_tokens", ""),
                "priority_bucket": row.get("priority_bucket", ""),
                "second_pass_focus": row.get("second_pass_focus", ""),
                "crop_strategy": row.get("crop_strategy", ""),
                "semantic_guardrail": row.get("semantic_guardrail", ""),
            }
        )
    return items


def summarize_packets(packets: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "packet_goal": Counter(packet["packet_goal"] for packet in packets),
        "folio": Counter(packet["folio"] for packet in packets),
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
    packets: list[dict[str, str]],
    items: list[dict[str, str]],
    queue_csv: Path,
    manifest_csv: Path,
    packets_csv: Path,
    items_csv: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_packets(packets)
    missing_total = sum(int(packet["missing_token_count"]) for packet in packets)
    lines = [
        "# Rota 12: pacotes por folio para revisao guiada",
        "",
        "Esta rota agrupa a fila Rota 11 por folio e imagem fonte. Os pacotes sao unidades operacionais de revisao visual, nao evidencias semanticas.",
        "",
        f"Fila de entrada: `{queue_csv}`.",
        f"Manifesto de recortes: `{manifest_csv}`.",
        f"Pacotes: `{packets_csv}`.",
        f"Itens por pacote: `{items_csv}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- pacotes por folio/imagem: {len(packets)};",
        f"- itens preservados nos pacotes: {len(items)};",
        f"- tokens faltantes agregados: {missing_total};",
        "- nenhum pacote autoriza leitura dos eixos `a/o` ou `r/l`.",
        "",
    ]
    lines.extend(render_counts("Objetivo do pacote", summary["packet_goal"]))
    lines.extend(render_counts("Folios", summary["folio"]))
    lines.extend(
        [
            "## Pacotes",
            "",
            "|pacote|folio|imagem|itens|faltam|objetivo|rotas R11|",
            "|---|---|---|---:|---:|---|---|",
        ]
    )
    for packet in packets:
        lines.append(
            f"|{packet['packet_id']}|{packet['folio']}|`{packet['source_image']}`|{packet['item_count']}|{packet['missing_token_count']}|{packet['packet_goal']}|{packet['route11_ids']}|"
        )
    lines.extend(
        [
            "",
            "## Leitura provisoria",
            "",
            "- Pacotes com `review_source_image_first` devem abrir a imagem fonte antes de redesenhar recortes.",
            "- Pacotes com `tighten_current_svg_regions` ainda nao confirmam glifo; apenas indicam onde tentar reduzir a regiao.",
            "- O campo `folio_packet_is_operational_not_semantic` impede usar o agrupamento como prova de significado.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


PACKET_FIELDNAMES = [
    "packet_id",
    "folio",
    "source_image",
    "item_count",
    "missing_token_count",
    "route11_ids",
    "priority_buckets",
    "focuses",
    "crop_strategies",
    "packet_goal",
    "packet_instruction",
    "semantic_guardrail",
]

ITEM_FIELDNAMES = [
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
    "prefix_family",
    "axis_coverage",
    "group_tokens",
    "missing_group_tokens",
    "priority_bucket",
    "second_pass_focus",
    "crop_strategy",
    "semantic_guardrail",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("second_pass_queue_csv", help="CSV from prepare_second_pass_crop_queue.py")
    parser.add_argument("crop_manifest_csv", help="CSV from prepare_review_crops.py")
    parser.add_argument(
        "--packets-csv",
        default=str(ROOT / "data" / "annotations" / "folio_review_packets_zl3b.csv"),
        help="Folio packets CSV output",
    )
    parser.add_argument(
        "--items-csv",
        default=str(ROOT / "data" / "annotations" / "folio_review_packet_items_zl3b.csv"),
        help="Packet items CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "folio_review_packet_summary_zl3b.csv"),
        help="Packet summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_12_pacotes_revisao_guiada.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    queue_csv = Path(args.second_pass_queue_csv)
    manifest_csv = Path(args.crop_manifest_csv)
    rows = attach_manifest_fields(read_csv(queue_csv), read_csv(manifest_csv))
    packets = build_packets(rows)
    items = build_packet_items(packets, rows)
    summary = summarize_packets(packets)
    packets_csv = Path(args.packets_csv)
    items_csv = Path(args.items_csv)
    summary_csv = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(packets_csv, packets, PACKET_FIELDNAMES)
    write_csv(items_csv, items, ITEM_FIELDNAMES)
    write_summary_csv(summary_csv, summary)
    write_report(md_path, packets, items, queue_csv, manifest_csv, packets_csv, items_csv, summary_csv)
    print(f"folio_packets={len(packets)} packet_items={len(items)}")
    print(f"packets_csv={packets_csv}")
    print(f"items_csv={items_csv}")
    print(f"summary_csv={summary_csv}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
