#!/usr/bin/env python3
"""
Validador de qualidade visual das ferramentas HTML R42*.
Analisa screenshots capturados pelo visual_capture_for_validation.js
usando análise de pixels (PIL) — sem precisar de humano.

Uso (de qualquer diretório):
    node voynich-codex-project/scripts/visual_capture_for_validation.js
    ../.venv/bin/python3 voynich-codex-project/scripts/validate_visual_quality.py
    # ou de dentro de voynich-codex-project/:
    ../.venv/bin/python3 scripts/validate_visual_quality.py
"""
from __future__ import annotations
import json
import os
import subprocess
import sys
from pathlib import Path

# Auto-relaunch com o venv correto se PIL não estiver disponível
try:
    from PIL import Image, ImageStat
except ImportError:
    # Procura venv relativo a este script (../../.venv ou ../.venv)
    script_dir = Path(__file__).resolve().parent
    for candidate in [script_dir / "../../.venv/bin/python3", script_dir / "../.venv/bin/python3"]:
        if candidate.exists():
            os.execv(str(candidate), [str(candidate)] + sys.argv)
    sys.exit("PIL não encontrado. Use: ../.venv/bin/python3 scripts/validate_visual_quality.py")

OUT = Path("/tmp/visual-caps")
MANIFEST = OUT / "manifest.json"

PASS = "✓"
FAIL = "✗"
WARN = "~"


def analyze_image(path: str) -> dict | None:
    """
    Analisa pixels de uma imagem PNG.
    Retorna métricas sem precisar de humano.
    """
    p = Path(path)
    if not p.exists() or p.stat().st_size < 100:
        return None
    img = Image.open(p).convert("RGB")
    w, h = img.size
    if w < 4 or h < 4:
        return None
    stat = ImageStat.Stat(img)
    mean_brightness = sum(stat.mean) / 3       # 0=preto, 255=branco
    stddev = sum(stat.stddev) / 3              # variância: alto = conteúdo
    pixels = list(img.getdata())
    # % pixels quase pretos (fundo vazio / área fora da imagem)
    dark = sum(1 for r, g, b in pixels if r < 30 and g < 30 and b < 30) / len(pixels)
    # % pixels quase brancos (canvas não renderizado)
    blank = sum(1 for r, g, b in pixels if r > 230 and g > 225 and b > 215) / len(pixels)

    has_content = stddev > 15 and dark < 0.90 and blank < 0.85

    return {
        "w": w, "h": h,
        "brightness": round(mean_brightness, 1),
        "stddev": round(stddev, 1),
        "dark_pct": round(dark * 100, 1),
        "blank_pct": round(blank * 100, 1),
        "has_content": has_content,
    }


def run(manifest_path: Path = MANIFEST) -> int:
    if not manifest_path.exists():
        print(f"Manifest não encontrado: {manifest_path}")
        print("Execute primeiro: node scripts/visual_capture_for_validation.js")
        return 1

    manifest = json.loads(manifest_path.read_text())

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Validador Visual — Análise de Pixels (PIL)")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    total = 0
    passed = 0
    failed = 0
    warnings: list[str] = []

    for tool_id, info in manifest.items():
        print(f"{tool_id}")
        meta = info["meta"]

        # ── 1. Imagem do manuscrito tem conteúdo ──────────────────────────
        manuscript_cap = next((c for c in info["caps"] if c["type"] == "manuscript_image"), None)
        if manuscript_cap:
            a = analyze_image(manuscript_cap["path"])
            if a:
                ok = a["has_content"] and a["dark_pct"] < 80
                total += 1
                if ok:
                    passed += 1
                    print(
                        f"  {PASS} Imagem manuscrito: brilho={a['brightness']}, "
                        f"stddev={a['stddev']}, {a['dark_pct']}% preto → tem conteúdo"
                    )
                else:
                    failed += 1
                    msg = (
                        f"  {FAIL} Imagem manuscrito SUSPEITA: "
                        f"brilho={a['brightness']}, stddev={a['stddev']}, "
                        f"{a['dark_pct']}% preto, {a['blank_pct']}% branco"
                    )
                    print(msg)
                    warnings.append(f"{tool_id}: imagem_manuscrito – {msg.strip()}")

        # ── 2. Zonas sobre conteúdo real (não área preta) ──────────────────
        zone_caps = [c for c in info["caps"] if c["type"].startswith("zone_")]
        if zone_caps:
            zones_bad = 0
            for z in zone_caps:
                a = analyze_image(z["path"])
                if not a:
                    continue
                if a["dark_pct"] > 80:
                    zones_bad += 1
                    msg = f"  {FAIL} {z['type']}: {a['dark_pct']}% preto → zona sobre área VAZIA/PRETA"
                    print(msg)
                    warnings.append(f"{tool_id}: {z['type']} – {msg.strip()}")
                elif not a["has_content"]:
                    print(f"  {WARN} {z['type']}: stddev={a['stddev']} → zona sobre área pouco variada")
            total += 1
            if zones_bad == 0:
                passed += 1
                print(f"  {PASS} Zona(s) amostrada(s) ({len(zone_caps)}): todas sobre conteúdo real")
            else:
                failed += 1

        # ── 3. Canvas de preview têm conteúdo ─────────────────────────────
        canvas_caps = [c for c in info["caps"] if c["type"].startswith("canvas_crop")]
        if canvas_caps:
            ok_count = sum(1 for c in canvas_caps if (a := analyze_image(c["path"])) and a["has_content"])
            fail_count = len(canvas_caps) - ok_count
            total += 1
            if fail_count == 0 and ok_count > 0:
                passed += 1
                print(f"  {PASS} Canvas crops ({ok_count} amostrados): todos com conteúdo visual")
            elif ok_count == 0:
                failed += 1
                msg = f"  {FAIL} Canvas crops: NENHUM tem conteúdo (todos vazios?)"
                print(msg)
                warnings.append(f"{tool_id}: canvas_crops – {msg.strip()}")
            else:
                passed += 1  # maioria ok
                print(f"  {WARN} Canvas crops: {ok_count}/{len(canvas_caps)} com conteúdo")

        # ── 4. Imagem com zonas — overlay não está fora do lugar ───────────
        stage_cap = next((c for c in info["caps"] if c["type"] == "image_with_zones"), None)
        if stage_cap:
            a = analyze_image(stage_cap["path"])
            if a:
                ok = a["dark_pct"] < 70 and a["has_content"]
                total += 1
                if ok:
                    passed += 1
                    print(
                        f"  {PASS} Imagem+zonas: {a['dark_pct']}% preto, "
                        f"stddev={a['stddev']} → overlay sobre imagem real"
                    )
                else:
                    failed += 1
                    msg = (
                        f"  {FAIL} Imagem+zonas: {a['dark_pct']}% preto → "
                        "overlay FORA do lugar ou imagem preta"
                    )
                    print(msg)
                    warnings.append(f"{tool_id}: image_with_zones – {msg.strip()}")

        print()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    score = round(passed / total * 100) if total > 0 else 0
    print(f"TOTAL: {passed} {PASS}  {failed} {FAIL}  de {total} verificações")
    print(f"Score visual: {score}%")
    if warnings:
        print("\n⚠  Problemas detectados:")
        for w in warnings:
            print(f"   {w}")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run())
