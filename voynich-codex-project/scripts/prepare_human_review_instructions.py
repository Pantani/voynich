#!/usr/bin/env python3
"""Generate human-readable packet review instructions for route 15."""
from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIELDS_TO_FILL = (
    "manual_token_seen manual_new_crop_needed manual_image_insufficient "
    "manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes"
)


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    malformed = [i + 2 for i, row in enumerate(rows) if row.get(None)]
    if malformed:
        raise ValueError(f"Malformed CSV rows in {path}: {malformed[:10]}")
    return rows


def fields_to_fill() -> str:
    return FIELDS_TO_FILL


def instruction_mode(packet: dict[str, str]) -> str:
    goal = packet.get("packet_goal", "")
    if goal == "review_source_image_first":
        return "open_source_image_before_svg"
    if goal == "search_tokens_then_redraw_crop":
        return "search_tokens_then_redraw_crop"
    return "tighten_current_svg_regions"


def unique_join(values: list[str]) -> str:
    return " ".join(dict.fromkeys(value for value in values if value))


def checklist_sort_key(row: dict[str, str]) -> tuple[str, str, str]:
    return (row.get("packet_id", ""), row.get("priority_bucket", ""), row.get("checklist_id", ""))


def build_instruction_packets(
    packet_rows: list[dict[str, str]],
    checklist_rows: list[dict[str, str]],
) -> list[dict[str, str]]:
    items_by_packet: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in sorted(checklist_rows, key=checklist_sort_key):
        items_by_packet[row.get("packet_id", "")].append(row)

    packets: list[dict[str, str]] = []
    for index, packet in enumerate(packet_rows, start=1):
        packet_id = packet.get("packet_id", "")
        items = items_by_packet.get(packet_id, [])
        packets.append(
            {
                "instruction_id": f"R15-{index:03d}",
                "packet_id": packet_id,
                "folio": packet.get("folio", ""),
                "source_image": packet.get("source_image", ""),
                "item_count": str(len(items)),
                "missing_token_count": packet.get("missing_token_count", ""),
                "checklist_ids": unique_join([item.get("checklist_id", "") for item in items]),
                "instruction_mode": instruction_mode(packet),
                "fields_to_fill": fields_to_fill(),
                "human_instruction": packet.get("packet_instruction", ""),
                "semantic_guardrail": "human_instruction_not_visual_evidence",
            }
        )
    return packets


def build_instruction_items(checklist_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    items: list[dict[str, str]] = []
    for index, row in enumerate(sorted(checklist_rows, key=checklist_sort_key), start=1):
        items.append(
            {
                "instruction_item_id": f"R15I-{index:03d}",
                "checklist_id": row.get("checklist_id", ""),
                "packet_id": row.get("packet_id", ""),
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
                "priority_bucket": row.get("priority_bucket", ""),
                "target_type": row.get("target_type", ""),
                "review_target": row.get("review_target", ""),
                "fields_to_fill": fields_to_fill(),
                "semantic_guardrail": "human_instruction_not_visual_evidence",
            }
        )
    return items


def summarize_instructions(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    return {
        "instruction_mode": Counter(row["instruction_mode"] for row in rows),
        "folio": Counter(row["folio"] for row in rows),
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


def render_packet_section(packet: dict[str, str], items: list[dict[str, str]]) -> str:
    packet_items = [item for item in items if item.get("packet_id") == packet.get("packet_id")]
    lines = [
        f"## {packet['instruction_id']} / {packet['packet_id']} / {packet['folio']}",
        "",
        f"- imagem fonte: `{packet['source_image']}`;",
        f"- modo: `{packet['instruction_mode']}`;",
        f"- campos a preencher: `{packet['fields_to_fill']}`;",
        f"- guarda: `{packet['semantic_guardrail']}`;",
        "",
        "|checklist|prioridade|alvo|tipo|SVG|",
        "|---|---|---|---|---|",
    ]
    for item in packet_items:
        lines.append(
            f"|{item['checklist_id']}|{item.get('priority_bucket', '')}|{item.get('review_target', '')}|{item.get('target_type', '')}|`{item.get('crop_svg', '')}`|"
        )
    lines.extend(
        [
            "",
            "Preenchimento:",
            "",
            "- Abra primeiro a imagem fonte quando o modo pedir `open_source_image_before_svg`.",
            "- Use o SVG apenas como referencia de regiao, nao como confirmacao automatica.",
            "- Marque `manual_token_seen=yes/no/uncertain` depois da revisao visual.",
            "- Preencha coordenadas novas somente quando `manual_new_crop_needed=yes`.",
            "- Nao atribua significado a `a/o` ou `r/l` nesta etapa.",
            "",
        ]
    )
    return "\n".join(lines)


def write_report(
    path: Path,
    packet_instructions: list[dict[str, str]],
    item_instructions: list[dict[str, str]],
    packet_csv: Path,
    checklist_csv: Path,
    output_packets: Path,
    output_items: Path,
    summary_csv: Path,
) -> None:
    summary = summarize_instructions(packet_instructions)
    lines = [
        "# Rota 15: instrucoes humanas por pacote",
        "",
        "Esta rota gera instrucoes de revisao humana para preencher a checklist Rota 13. As instrucoes nao alteram a checklist e nao criam evidencia visual por si mesmas.",
        "",
        f"Pacotes de entrada: `{packet_csv}`.",
        f"Checklist de entrada: `{checklist_csv}`.",
        f"Instrucoes por pacote: `{output_packets}`.",
        f"Instrucoes item-a-item: `{output_items}`.",
        f"Resumo derivado: `{summary_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- pacotes instruidos: {len(packet_instructions)};",
        f"- itens instruidos: {len(item_instructions)};",
        "- nenhum campo manual foi preenchido automaticamente;",
        "- nenhuma instrucao autoriza leitura semantica dos eixos.",
        "",
    ]
    lines.extend(render_counts("Modo de instrucao", summary["instruction_mode"]))
    lines.extend(render_counts("Folios", summary["folio"]))
    for packet in packet_instructions:
        lines.append(render_packet_section(packet, item_instructions))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


PACKET_FIELDNAMES = [
    "instruction_id",
    "packet_id",
    "folio",
    "source_image",
    "item_count",
    "missing_token_count",
    "checklist_ids",
    "instruction_mode",
    "fields_to_fill",
    "human_instruction",
    "semantic_guardrail",
]

ITEM_FIELDNAMES = [
    "instruction_item_id",
    "checklist_id",
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
    "priority_bucket",
    "target_type",
    "review_target",
    "fields_to_fill",
    "semantic_guardrail",
]


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("packet_csv", help="CSV from prepare_folio_review_packets.py")
    parser.add_argument("checklist_csv", help="CSV from prepare_packet_item_checklist.py")
    parser.add_argument(
        "--packets-csv",
        default=str(ROOT / "data" / "annotations" / "human_review_instructions_zl3b.csv"),
        help="Packet-level instruction CSV output",
    )
    parser.add_argument(
        "--items-csv",
        default=str(ROOT / "data" / "annotations" / "human_review_instruction_items_zl3b.csv"),
        help="Item-level instruction CSV output",
    )
    parser.add_argument(
        "--summary-csv",
        default=str(ROOT / "data" / "derived" / "human_review_instruction_summary_zl3b.csv"),
        help="Instruction summary CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_15_instrucoes_revisao_humana.md"),
        help="Markdown report output",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    packet_csv = Path(args.packet_csv)
    checklist_csv = Path(args.checklist_csv)
    packets = build_instruction_packets(read_csv(packet_csv), read_csv(checklist_csv))
    items = build_instruction_items(read_csv(checklist_csv))
    summary = summarize_instructions(packets)
    packets_path = Path(args.packets_csv)
    items_path = Path(args.items_csv)
    summary_path = Path(args.summary_csv)
    md_path = Path(args.md)
    write_csv(packets_path, packets, PACKET_FIELDNAMES)
    write_csv(items_path, items, ITEM_FIELDNAMES)
    write_summary_csv(summary_path, summary)
    write_report(md_path, packets, items, packet_csv, checklist_csv, packets_path, items_path, summary_path)
    print(f"human_review_packets={len(packets)} human_review_items={len(items)}")
    print(f"packets_csv={packets_path}")
    print(f"items_csv={items_path}")
    print(f"summary_csv={summary_path}")
    print(f"md={md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
