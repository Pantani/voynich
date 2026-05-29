#!/usr/bin/env python3
"""Download key Voynich manuscript images from manifests.

Usage:
    python scripts/download_images.py

By default this downloads public-domain Commons files listed in
`data/commons_image_sources.csv` into `images/raw/`.

It also detects `data/image_sources.csv` with VIB/Yale preview URLs and can download
those as supplemental images if `--include-supplemental` is passed.
"""
from __future__ import annotations

import argparse
import csv
import re
import sys
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

ROOT = Path(__file__).resolve().parents[1]
COMMONS_MANIFEST = ROOT / "data" / "commons_image_sources.csv"
SUPPLEMENTAL_MANIFEST = ROOT / "data" / "image_sources.csv"
OUT_DIR = ROOT / "images" / "raw"


def safe_name(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("_")


def download(url: str, out_path: Path) -> None:
    req = Request(url, headers={"User-Agent": "voynich-codex-project/0.1"})
    with urlopen(req, timeout=30) as resp:
        content = resp.read()
        ctype = resp.headers.get("content-type", "")
    if not content:
        raise RuntimeError("empty response")
    if "png" in ctype:
        ext = ".png"
    elif "jpeg" in ctype or "jpg" in ctype:
        ext = ".jpg"
    elif out_path.suffix:
        ext = out_path.suffix
    else:
        ext = ".img"
    if out_path.suffix != ext:
        out_path = out_path.with_suffix(ext)
    out_path.write_bytes(content)
    print(f"OK {out_path.relative_to(ROOT)} ({len(content)} bytes)")


def load_rows(manifest: Path, source_label: str) -> list[dict[str, str]]:
    if not manifest.exists():
        return []
    rows: list[dict[str, str]] = []
    with manifest.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            row["_source_label"] = source_label
            rows.append(row)
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--include-supplemental", action="store_true", help="também baixa previews VIB/Yale de data/image_sources.csv")
    args = parser.parse_args(argv)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    rows = load_rows(COMMONS_MANIFEST, "commons")
    if args.include_supplemental:
        rows.extend(load_rows(SUPPLEMENTAL_MANIFEST, "supplemental"))

    if not rows:
        print("No image manifest found.", file=sys.stderr)
        return 2

    failures = []
    for row in rows:
        folio = safe_name(row.get("folio", row.get("id", "image")))
        url = row.get("image_url") or row.get("direct_image_url")
        if not url:
            print(f"Skipping {folio}: no image_url", file=sys.stderr)
            continue
        prefix = row["_source_label"]
        out_path = OUT_DIR / f"{prefix}_{folio}.jpg"
        try:
            download(url, out_path)
        except (URLError, HTTPError, RuntimeError, TimeoutError, OSError) as e:
            failures.append((folio, url, str(e)))
            print(f"FAIL {folio}: {e}", file=sys.stderr)

    if failures:
        print("\nFailures:", file=sys.stderr)
        for folio, url, err in failures:
            print(f"- {folio}: {url} :: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
