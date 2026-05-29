#!/usr/bin/env python3
"""Download public starter text data for Voynich experiments.

This script intentionally downloads only small/open data useful for reproducing
some of the broad statistical attacks. For IVTFF/EVA full transcriptions, see
`docs/fontes_e_citacoes.md` and place your chosen file in `data/raw/`.
"""
from __future__ import annotations

from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw"
OUT.mkdir(parents=True, exist_ok=True)

SOURCES = [
    {
        "name": "ZL3b-n.txt",
        "url": "https://www.voynich.nu/data/ZL3b-n.txt",
        "note": "Zandbergen-Landini IVTFF 2.0/EVA transliteration, version 3b.",
    },
    {
        "name": "voy.b.paged.wds",
        "url": "https://raw.githubusercontent.com/sravanareddy/deciphervoynich/master/data/voy.b.paged.wds",
        "note": "Reddy & Knight data: Voynich B text in their encoded alphabet, pages as lines.",
    },
    {
        "name": "wsj.paged.wds",
        "url": "https://raw.githubusercontent.com/sravanareddy/deciphervoynich/master/data/wsj.paged.wds",
        "note": "Reddy & Knight comparison corpus: WSJ sample.",
    },
]


def download(url: str, out: Path) -> None:
    req = Request(url, headers={"User-Agent": "voynich-codex-project/0.1"})
    with urlopen(req, timeout=60) as resp:
        data = resp.read()
    out.write_bytes(data)
    print(f"OK {out.relative_to(ROOT)} ({len(data)} bytes)")


def main() -> int:
    failures = []
    for item in SOURCES:
        out = OUT / item["name"]
        try:
            download(item["url"], out)
        except (HTTPError, URLError, TimeoutError, OSError) as e:
            failures.append((item["name"], item["url"], str(e)))
            print(f"FAIL {item['name']}: {e}")
    if failures:
        print("\nAlguns downloads falharam. Você pode baixar manualmente pelas URLs acima.")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
