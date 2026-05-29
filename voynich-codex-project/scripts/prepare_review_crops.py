#!/usr/bin/env python3
"""Prepare rough visual review crops for R6 glyph-review items.

The generated SVGs are non-destructive wrappers around the original JPGs. They
show approximate review regions, not confirmed glyph locations.
"""
from __future__ import annotations

import argparse
import csv
import html
import re
import struct
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


def jpeg_dimensions(path: Path) -> tuple[int, int]:
    with path.open("rb") as f:
        if f.read(2) != b"\xff\xd8":
            raise ValueError(f"Not a JPEG file: {path}")
        while True:
            marker_start = f.read(1)
            if not marker_start:
                break
            if marker_start != b"\xff":
                continue
            marker = f.read(1)
            while marker == b"\xff":
                marker = f.read(1)
            if marker in {b"\xd8", b"\xd9"}:
                continue
            length_bytes = f.read(2)
            if len(length_bytes) != 2:
                break
            length = struct.unpack(">H", length_bytes)[0]
            if marker in {b"\xc0", b"\xc1", b"\xc2", b"\xc3", b"\xc5", b"\xc6", b"\xc7", b"\xc9", b"\xca", b"\xcb", b"\xcd", b"\xce", b"\xcf"}:
                data = f.read(5)
                if len(data) != 5:
                    break
                height, width = struct.unpack(">HH", data[1:5])
                return width, height
            f.seek(length - 2, 1)
    raise ValueError(f"Could not read JPEG dimensions: {path}")


def clamp_box(box: tuple[int, int, int, int], image_width: int, image_height: int) -> tuple[int, int, int, int]:
    x, y, width, height = box
    x = max(0, min(x, image_width - 1))
    y = max(0, min(y, image_height - 1))
    width = max(1, min(width, image_width - x))
    height = max(1, min(height, image_height - y))
    return x, y, width, height


def proportional_box(
    image_width: int,
    image_height: int,
    x: float,
    y: float,
    width: float,
    height: float,
) -> tuple[int, int, int, int]:
    return clamp_box(
        (
            round(image_width * x),
            round(image_height * y),
            round(image_width * width),
            round(image_height * height),
        ),
        image_width,
        image_height,
    )


def rough_crop_box(row: dict[str, str], image_width: int, image_height: int) -> tuple[int, int, int, int]:
    image = row.get("image_files", "")
    folio = row.get("folio", "")
    ring = row.get("ring", "").lower()

    if "commons_f67r1_r2" in image and folio == "f67r1":
        return proportional_box(image_width, image_height, 0.02, 0.13, 0.50, 0.75)
    if "commons_f68r1_r2_r3" in image and folio == "f68r3":
        return proportional_box(image_width, image_height, 0.58, 0.07, 0.37, 0.76)
    if "commons_f70v2" in image:
        return proportional_box(image_width, image_height, 0.09, 0.07, 0.78, 0.86)
    if "commons_f84r" in image and "between green pool bands" in ring:
        return proportional_box(image_width, image_height, 0.08, 0.47, 0.78, 0.34)
    if "commons_f84r" in image:
        return proportional_box(image_width, image_height, 0.08, 0.21, 0.78, 0.33)
    return proportional_box(image_width, image_height, 0.05, 0.05, 0.90, 0.90)


def safe_part(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("_")


def crop_file_name(crop_id: str, review_id: str, folio: str) -> str:
    return f"{safe_part(crop_id)}_{safe_part(review_id)}_{safe_part(folio)}.svg"


def build_crop_manifest(
    queue_rows: list[dict[str, str]],
    image_sizes: dict[str, tuple[int, int]],
    crop_dir: str = "images/derived/review_crops",
) -> list[dict[str, str]]:
    manifest: list[dict[str, str]] = []
    for index, row in enumerate(queue_rows, start=1):
        source_image = row.get("image_files", "").split(" | ")[0]
        image_width, image_height = image_sizes[source_image]
        x, y, width, height = rough_crop_box(row, image_width, image_height)
        crop_id = f"R7-{index:03d}"
        filename = crop_file_name(crop_id, row.get("review_id", ""), row.get("folio", ""))
        manifest.append(
            {
                "crop_id": crop_id,
                "source_review_id": row.get("review_id", ""),
                "folio": row.get("folio", ""),
                "locus": row.get("locus", ""),
                "prefix_family": row.get("prefix_family", ""),
                "suffixes_present": row.get("suffixes_present", ""),
                "axis_coverage": row.get("axis_coverage", ""),
                "group_tokens": row.get("group_tokens", ""),
                "matched_annotation_tokens": row.get("matched_annotation_tokens", ""),
                "missing_group_tokens": row.get("missing_group_tokens", ""),
                "isolation_status": row.get("exact_glyph_status", ""),
                "crop_scope": "rough_region_only",
                "source_image": source_image,
                "image_width": str(image_width),
                "image_height": str(image_height),
                "crop_x": str(x),
                "crop_y": str(y),
                "crop_width": str(width),
                "crop_height": str(height),
                "crop_svg": f"{crop_dir}/{filename}",
                "review_notes": row.get("review_notes", ""),
            }
        )
    return manifest


def relative_href(from_dir: Path, source_image: str) -> str:
    target = ROOT / source_image
    return Path("../../raw") / target.name if from_dir.as_posix().endswith("images/derived/review_crops") else Path(source_image)


def svg_for_crop(row: dict[str, str], crop_dir: Path) -> str:
    x = row["crop_x"]
    y = row["crop_y"]
    width = row["crop_width"]
    height = row["crop_height"]
    image_width = row["image_width"]
    image_height = row["image_height"]
    href = html.escape(relative_href(crop_dir, row["source_image"]).as_posix())
    title = html.escape(f"{row['crop_id']} / {row['source_review_id']} / {row['folio']} / {row['locus']}")
    tokens = html.escape(row["group_tokens"])
    status = html.escape(row["isolation_status"])
    stroke_width = max(3, round(min(int(width), int(height)) * 0.008))
    font_size = max(18, round(min(int(width), int(height)) * 0.035))
    text_x = int(x) + stroke_width * 3
    text_y = int(y) + font_size + stroke_width * 2
    return "\n".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{x} {y} {width} {height}">',
            f"  <title>{title}</title>",
            f'  <image href="{href}" x="0" y="0" width="{image_width}" height="{image_height}" />',
            f'  <rect x="{x}" y="{y}" width="{width}" height="{height}" fill="none" stroke="#d12f2f" stroke-width="{stroke_width}" vector-effect="non-scaling-stroke" />',
            f'  <rect x="{text_x - stroke_width}" y="{text_y - font_size}" width="{max(300, int(width) - stroke_width * 6)}" height="{font_size * 2 + stroke_width * 2}" fill="#ffffff" fill-opacity="0.82" stroke="#d12f2f" stroke-width="{max(1, stroke_width // 2)}" vector-effect="non-scaling-stroke" />',
            f'  <text x="{text_x}" y="{text_y}" font-family="Arial, sans-serif" font-size="{font_size}" fill="#111">{title}</text>',
            f'  <text x="{text_x}" y="{text_y + font_size + stroke_width}" font-family="Arial, sans-serif" font-size="{font_size}" fill="#111">tokens: {tokens} / {status}</text>',
            "</svg>",
            "",
        ]
    )


def write_csv(path: Path, rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "crop_id",
        "source_review_id",
        "folio",
        "locus",
        "prefix_family",
        "suffixes_present",
        "axis_coverage",
        "group_tokens",
        "matched_annotation_tokens",
        "missing_group_tokens",
        "isolation_status",
        "crop_scope",
        "source_image",
        "image_width",
        "image_height",
        "crop_x",
        "crop_y",
        "crop_width",
        "crop_height",
        "crop_svg",
        "review_notes",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_svgs(crop_dir: Path, rows: list[dict[str, str]]) -> None:
    crop_dir.mkdir(parents=True, exist_ok=True)
    for row in rows:
        path = ROOT / row["crop_svg"]
        path.write_text(svg_for_crop(row, crop_dir), encoding="utf-8")


def render_counts(title: str, counts: Counter[str]) -> list[str]:
    lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
    for key, value in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        lines.append(f"|{key}|{value}|")
    lines.append("")
    return lines


def write_report(path: Path, rows: list[dict[str, str]], queue_source: Path, output_csv: Path) -> None:
    status_counts = Counter(row["isolation_status"] for row in rows)
    folio_counts = Counter(row["folio"] for row in rows)
    lines = [
        "# Rota 7: recortes de revisao",
        "",
        "Esta rota gera recortes aproximados para revisao visual. Os SVGs apenas enquadram regioes provaveis; eles nao confirmam a palavra exata.",
        "",
        f"Fonte: `{queue_source}`.",
        f"Manifesto: `{output_csv}`.",
        "",
        "## Resultado curto",
        "",
        f"- recortes SVG gerados: {len(rows)};",
        "- escopo dos recortes: `rough_region_only`;",
        "- nenhuma coordenada foi tratada como glifo confirmado.",
        "",
    ]
    lines.extend(render_counts("Status preservado", status_counts))
    lines.extend(render_counts("Folios", folio_counts))
    lines.extend(
        [
            "## Recortes",
            "",
            "|crop|review|folio|locus|tokens|faltam|status|arquivo|",
            "|---|---|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        lines.append(
            f"|{row['crop_id']}|{row['source_review_id']}|{row['folio']}|{row['locus']}|{row['group_tokens']}|{row['missing_group_tokens']}|{row['isolation_status']}|`{row['crop_svg']}`|"
        )
    lines.extend(
        [
            "",
            "## Leitura provisoria",
            "",
            "- Os recortes agora tornam a revisao visual reproduzivel por `review_id`/`crop_id`.",
            "- O status `needs_exact_glyph_isolation` foi preservado em todos os itens.",
            "- A proxima etapa deve abrir os SVGs, tentar localizar a palavra exata e registrar coordenadas melhores ou manter `not isolated`.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def image_size_map(rows: list[dict[str, str]]) -> dict[str, tuple[int, int]]:
    images = sorted({row.get("image_files", "").split(" | ")[0] for row in rows if row.get("image_files")})
    return {image: jpeg_dimensions(ROOT / image) for image in images}


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("queue_csv", help="Glyph review queue CSV from prepare_glyph_review_queue.py")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "annotations" / "review_crop_manifest_zl3b.csv"),
        help="Crop manifest CSV output",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_7_recortes_revisao.md"),
        help="Markdown report output",
    )
    parser.add_argument(
        "--crop-dir",
        default=str(ROOT / "images" / "derived" / "review_crops"),
        help="Directory for generated SVG review crops",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    queue_source = Path(args.queue_csv)
    queue_rows = read_csv(queue_source)
    crop_dir = Path(args.crop_dir)
    crop_dir_relative = crop_dir.relative_to(ROOT).as_posix()
    manifest = build_crop_manifest(queue_rows, image_size_map(queue_rows), crop_dir_relative)
    write_csv(Path(args.csv), manifest)
    write_svgs(crop_dir, manifest)
    write_report(Path(args.md), manifest, queue_source, Path(args.csv))
    print(f"queue_rows={len(queue_rows)} review_crops={len(manifest)}")
    print(f"csv={args.csv}")
    print(f"md={args.md}")
    print(f"crop_dir={crop_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
