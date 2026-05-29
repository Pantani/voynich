#!/usr/bin/env python3
"""
Validador de integridade de dados do projeto Voynich.
Analisa automaticamente: CSVs, HTMLs embebidos, imagens, corpus, pipeline.
Sem precisar de humano.

Uso (de dentro de voynich-codex-project/):
    python3 scripts/validate_data_integrity.py
"""
from __future__ import annotations

import csv
import importlib.util
import json
import os
import re
import subprocess
import sys
from pathlib import Path

# Auto-relaunch com venv se PIL não estiver disponível
try:
    from PIL import Image
    _has_pil = True
except ImportError:
    _has_pil = False
    script_dir = Path(__file__).resolve().parent
    for candidate in [script_dir / "../../.venv/bin/python3", script_dir / "../.venv/bin/python3"]:
        if candidate.exists():
            os.execv(str(candidate), [str(candidate)] + sys.argv)

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT = SCRIPT_DIR.parent
TOOLS_DIR = PROJECT / "docs" / "tools"
DATA_DERIVED = PROJECT / "data" / "derived"
DATA_ANNOTATIONS = PROJECT / "data" / "annotations"
IMAGES_DIR = PROJECT / "images" / "raw" / "yale_iiif_r32"
CORPUS = PROJECT / "data" / "raw" / "ZL3b-n.txt"

PASS, FAIL, WARN = "✓", "✗", "~"


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def load_html_json(path: Path, var_name: str) -> list[dict] | None:
    content = path.read_text(encoding="utf-8")
    m = re.search(rf"const {re.escape(var_name)} = (\[.*?\]);", content, re.DOTALL)
    if not m:
        return None
    return json.loads(m.group(1))


def parse_box(s: str) -> tuple[float, float, float, float] | None:
    try:
        x1, y1, x2, y2 = [float(v) for v in s.split(",")]
        return x1, y1, x2, y2
    except Exception:
        return None


def box_in_bounds(box: tuple) -> bool:
    return all(0.0 <= v <= 100.0 for v in box)


def boxes_overlap(a: tuple, b: tuple) -> float:
    """Retorna fração da área de b que está dentro de a (0–1)."""
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    if ix2 <= ix1 or iy2 <= iy1:
        return 0.0
    inter = (ix2 - ix1) * (iy2 - iy1)
    b_area = (bx2 - bx1) * (by2 - by1)
    return inter / b_area if b_area > 0 else 0.0


def result(ok: bool | None, label: str) -> dict:
    return {"ok": ok, "label": label}


# ─────────────────────────────────────────────────────────────
# 1. Dados embebidos nos HTMLs
# ─────────────────────────────────────────────────────────────

def check_html_data() -> list[dict]:
    results = []

    # R42F: zone coordinates, aspect ratio, loci compartilhando zona
    r42f_path = TOOLS_DIR / "rota_42f_escolha_linhas_visuais_sem_zona_r32.html"
    if r42f_path.exists():
        items = load_html_json(r42f_path, "ITEMS") or []
        bad_bounds, bad_aspect, shared_zones = 0, 0, {}

        for it in items:
            zones_str = it.get("candidate_visual_line_zones", "")
            key = zones_str[:80]  # proxy para zona única
            shared_zones.setdefault(key, []).append(it["target_locus"])

            for entry in zones_str.split("|"):
                if "=" not in entry:
                    continue
                _, coords = entry.split("=", 1)
                box = parse_box(coords)
                if not box:
                    continue
                if not box_in_bounds(box):
                    bad_bounds += 1
                w, h = box[2] - box[0], box[3] - box[1]
                # Linhas de texto devem ser largas: largura > 2× altura
                if h > 0 and w / h < 1.5:
                    bad_aspect += 1

        shared = [(k, v) for k, v in shared_zones.items() if len(v) > 1]
        results.append(result(bad_bounds == 0,
            f"R42F: coordenadas de zona dentro de [0,100] ({len(items)} items)"))
        results.append(result(bad_aspect == 0,
            f"R42F: aspect ratio das zonas ok (largura>1.5× altura)" if bad_aspect == 0
            else f"R42F: {bad_aspect} zona(s) com aspect ratio suspeito (quase quadrada)"))
        # Loci compartilhando zona = limitação do OpenCV (detecta por fólio, não por locus)
        # Não é um erro fixável, só um aviso de qualidade de dados
        results.append(result(None if shared else True,
            f"R42F: cada locus tem zona única ✓" if not shared
            else f"R42F: {len(shared)} grupo(s) de loci com mesma zona (OpenCV por fólio, não por locus) "
                 f"— limitação conhecida, ex: {shared[0][1][:2]}"))

    # R42M: fragment_union_box_pct deve estar dentro de suggested_zone_box_pct
    r42m_path = TOOLS_DIR / "rota_42m_captura_fina_linhas_r32.html"
    if r42m_path.exists():
        rows = load_html_json(r42m_path, "ROWS") or []
        frags_outside = 0
        for row in rows:
            zone = parse_box(row.get("suggested_zone_box_pct", ""))
            frag = parse_box(row.get("fragment_union_box_pct", ""))
            if zone and frag:
                overlap = boxes_overlap(zone, frag)
                if overlap < 0.5:
                    frags_outside += 1
        results.append(result(frags_outside == 0,
            f"R42M: fragmentos dentro da zona sugerida ({len(rows)} rows)" if frags_outside == 0
            else f"R42M: {frags_outside}/{len(rows)} fragmentos com <50% sobreposição com zona"))

    # R42L: best_visual_line_number deve estar em candidate_visual_lines
    r42l_path = TOOLS_DIR / "rota_42l_confirmacao_linhas_sugeridas_r32.html"
    if r42l_path.exists():
        items = load_html_json(r42l_path, "CONFIRM_ROWS") or []
        best_not_in_candidates = 0
        for it in items:
            best = it.get("best_visual_line_number") or it.get("suggested_visual_line_number", "")
            candidates = (it.get("candidate_visual_lines", "") or "").split("|")
            if best and candidates and best not in candidates:
                best_not_in_candidates += 1
        results.append(result(best_not_in_candidates == 0,
            f"R42L: linha sugerida está entre candidatas ({len(items)} items)" if best_not_in_candidates == 0
            else f"R42L: {best_not_in_candidates} item(s) com linha sugerida FORA das candidatas"))

    return results


# ─────────────────────────────────────────────────────────────
# 2. Cross-reference entre ferramentas
# ─────────────────────────────────────────────────────────────

def check_cross_references() -> list[dict]:
    results = []

    def get_ids(path: Path, var: str, id_field: str) -> set[str]:
        data = load_html_json(path, var) or []
        return {row.get(id_field, "") for row in data if row.get(id_field)}

    tools = {
        "R42F": (TOOLS_DIR / "rota_42f_escolha_linhas_visuais_sem_zona_r32.html", "ITEMS", "route42f_id"),
        "R42K": (TOOLS_DIR / "rota_42k_fila_priorizada_revisao_visual_r32.html", "QUEUE_ROWS", "route42k_id"),
        "R42L": (TOOLS_DIR / "rota_42l_confirmacao_linhas_sugeridas_r32.html", "CONFIRM_ROWS", "route42l_id"),
        "R42M": (TOOLS_DIR / "rota_42m_captura_fina_linhas_r32.html", "ROWS", "route42m_id"),
    }

    ids: dict[str, set[str]] = {}
    for name, (path, var, id_field) in tools.items():
        if path.exists():
            ids[name] = get_ids(path, var, id_field)

    # R42M referencia route42l_id e route42f_id — verificar que existem
    r42m_path = TOOLS_DIR / "rota_42m_captura_fina_linhas_r32.html"
    if r42m_path.exists():
        rows = load_html_json(r42m_path, "ROWS") or []
        broken_l, broken_f = 0, 0
        for row in rows:
            ref_l = row.get("route42l_id", "")
            ref_f = row.get("route42f_id", "")
            if ref_l and "R42L" in ids and ref_l not in ids["R42L"]:
                broken_l += 1
            if ref_f and "R42F" in ids and ref_f not in ids["R42F"]:
                broken_f += 1
        results.append(result(broken_l == 0,
            f"R42M→R42L: todas as {len(rows)} referências existem" if broken_l == 0
            else f"R42M→R42L: {broken_l} referências quebradas"))
        results.append(result(broken_f == 0,
            f"R42M→R42F: todas as {len(rows)} referências existem" if broken_f == 0
            else f"R42M→R42F: {broken_f} referências quebradas"))

    return results


# ─────────────────────────────────────────────────────────────
# 3. Arquivos de imagem
# ─────────────────────────────────────────────────────────────

def check_images() -> list[dict]:
    results = []

    jpgs = list(IMAGES_DIR.glob("*.jpg")) if IMAGES_DIR.exists() else []
    results.append(result(len(jpgs) == 8,
        f"Imagens Yale IIIF: {len(jpgs)}/8 arquivos presentes"))

    if not _has_pil:
        results.append(result(None, "PIL não disponível — skip verificação de integridade de JPEG"))
        return results

    broken, dimensions = [], {}
    for jpg in sorted(jpgs):
        try:
            img = Image.open(jpg)
            img.verify()
            img = Image.open(jpg)
            dimensions[jpg.name] = img.size
        except Exception as e:
            broken.append(f"{jpg.name}: {e}")

    results.append(result(len(broken) == 0,
        f"Integridade JPEG: todos os {len(jpgs)} arquivos abrem sem erro" if len(broken) == 0
        else f"JPEG corrompidos: {broken}"))

    if dimensions:
        widths = [w for w, h in dimensions.values()]
        min_w, max_w = min(widths), max(widths)
        results.append(result(min_w > 1000,
            f"Dimensões das imagens: {min_w}–{max_w}px largura (high-res ok)" if min_w > 1000
            else f"Imagem suspeita: largura mínima {min_w}px (esperado >1000px)"))

    return results


# ─────────────────────────────────────────────────────────────
# 4. Corpus e pipeline Python
# ─────────────────────────────────────────────────────────────

def check_corpus() -> list[dict]:
    results = []

    if not CORPUS.exists():
        results.append(result(False, f"Corpus ZL3b-n.txt: NÃO ENCONTRADO em {CORPUS}"))
        return results

    text = CORPUS.read_text(encoding="utf-8", errors="ignore")
    raw_lines = text.splitlines()
    # Conta tokens EVA corretamente: só linhas com texto (não comentários/headers)
    eva_tokens = 0
    eva_lines = 0
    for line in raw_lines:
        if not line.strip() or line.startswith("#"):
            continue
        clean = re.sub(r"<[^>]+>", "", line)   # remove tags <f1r>
        clean = re.sub(r"\{[^}]+\}", "", clean)  # remove {chars}
        toks = re.findall(r"[a-z]+", clean)
        if toks:
            eva_tokens += len(toks)
            eva_lines += 1
    results.append(result(eva_lines > 5000,
        f"Corpus: {eva_lines} linhas EVA ({eva_tokens} tokens)"))
    results.append(result(35000 < eva_tokens < 46000,
        f"Corpus: tamanho esperado (~41 000 tokens)" if 35000 < eva_tokens < 46000
        else f"Corpus: tamanho inesperado ({eva_tokens} tokens, esperado ~41 000)"))

    # Key derived CSVs existem e têm linhas
    key_csvs = [
        ("border_matrix_context_zl3b.csv", 8000),
        ("exact_form_context_table_zl3b.csv", 700),
    ]
    for csv_name, min_rows in key_csvs:
        csv_path = DATA_DERIVED / csv_name
        if not csv_path.exists():
            results.append(result(False, f"CSV ausente: {csv_name}"))
            continue
        with csv_path.open() as f:
            row_count = sum(1 for _ in f) - 1
        results.append(result(row_count >= min_rows,
            f"{csv_name}: {row_count} linhas (mín {min_rows})"))

    return results


def check_pipeline() -> list[dict]:
    results = []

    venv_python = PROJECT.parent / ".venv" / "bin" / "python3"
    if not venv_python.exists():
        results.append(result(None, "Venv não encontrado — skip testes"))
        return results

    # Rodar pytest
    r = subprocess.run(
        [str(venv_python), "-m", "pytest", "tests/", "-q", "--tb=no", "--no-header"],
        cwd=str(PROJECT), capture_output=True, text=True, timeout=120
    )
    last_line = [l for l in r.stdout.splitlines() if l.strip()][-1] if r.stdout.strip() else ""
    passed = r.returncode == 0
    results.append(result(passed,
        f"pytest: {last_line}" if last_line else f"pytest: {'ok' if passed else 'FALHOU'}"))

    # Verificar que nenhum script de rota tem SyntaxError
    scripts = sorted(SCRIPT_DIR.glob("*.py"))
    syntax_errors = []
    for s in scripts:
        r2 = subprocess.run(
            [str(venv_python), "-m", "py_compile", str(s)],
            capture_output=True, text=True
        )
        if r2.returncode != 0:
            syntax_errors.append(s.name)
    results.append(result(len(syntax_errors) == 0,
        f"Sintaxe Python: {len(scripts)} scripts sem erros" if len(syntax_errors) == 0
        else f"SyntaxError em: {syntax_errors[:5]}"))

    return results


# ─────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────

def main() -> int:
    sections = [
        ("Dados HTML (zonas, aspectos, loci)", check_html_data),
        ("Cross-references entre ferramentas", check_cross_references),
        ("Arquivos de imagem Yale IIIF", check_images),
        ("Corpus EVA + CSVs derivados", check_corpus),
        ("Pipeline Python (pytest + sintaxe)", check_pipeline),
    ]

    print("\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("  Validador de Integridade de Dados — Voynich")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    total, passed, failed = 0, 0, 0

    for title, check_fn in sections:
        print(f"── {title}")
        try:
            results = check_fn()
        except Exception as e:
            print(f"  {FAIL} Erro: {e}")
            failed += 1
            total += 1
            print()
            continue

        for r in results:
            icon = PASS if r["ok"] is True else FAIL if r["ok"] is False else WARN
            print(f"  {icon} {r['label']}")
            total += 1
            if r["ok"] is True:
                passed += 1
            elif r["ok"] is False:
                failed += 1
        print()

    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    score = round(passed / total * 100) if total > 0 else 0
    print(f"TOTAL: {passed} {PASS}  {failed} {FAIL}  de {total} verificações")
    print(f"Score: {score}%")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
