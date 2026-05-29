#!/usr/bin/env python3
"""Rota 47: seção vs escriba como preditor do bit a/o — falsificação de M5."""
from __future__ import annotations

import argparse
import collections
import csv
import math
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota47_section_scribe_ao_predictor_not_decipherment"
FORMS = ["okal", "okar", "okol", "okor", "otal", "otar", "otol", "otor"]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def ao_bit(suf: str) -> str | None:
    return "a" if suf in ("al", "ar") else ("o" if suf in ("ol", "or") else None)


def classify_section(folio: str, section_note: str) -> str:
    sn = (section_note or "").lower()
    f = folio.lower()
    try:
        num = int(re.search(r"\d+", f).group())
    except (ValueError, AttributeError):
        num = 0
    if any(k in sn for k in ("star", "stelle", "light star", "dotted")):
        return "astronomical"
    if any(k in sn for k in ("nymph", "lake", "pool")):
        return "balneological"
    if any(k in sn for k in ("recipe", "b@r")):
        return "recipes"
    if "zodiac" in sn:
        return "zodiac"
    if 67 <= num <= 73:
        return "astronomical"
    if 75 <= num <= 84:
        return "balneological"
    if 85 <= num <= 87:
        return "cosmological"
    if 88 <= num <= 102:
        return "pharmaceutical"
    if 103 <= num <= 116:
        return "recipes"
    if 1 <= num <= 66:
        return "herbal"
    return "other"


def cramer_v(table: dict[str, collections.Counter]) -> tuple[float, int]:
    rk = list(table.keys())
    ck = list({c for cnt in table.values() for c in cnt})
    t = [[table[r].get(c, 0) for c in ck] for r in rk]
    N = sum(sum(row) for row in t)
    if N < 4:
        return 0.0, N
    rs = [sum(row) for row in t]
    cs = [sum(t[i][j] for i in range(len(rk))) for j in range(len(ck))]
    chi2 = sum(
        (t[i][j] - rs[i] * cs[j] / N) ** 2 / (rs[i] * cs[j] / N)
        for i in range(len(rk))
        for j in range(len(ck))
        if rs[i] * cs[j] / N > 0
    )
    k = min(len(rk), len(ck))
    v = math.sqrt(chi2 / (N * (k - 1))) if N * (k - 1) > 0 else 0.0
    return v, N


def build_tables(rows: list[dict[str, str]]) -> dict:
    section_ao: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    currier_ao: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    section_currier_ao: dict[str, dict[str, collections.Counter]] = collections.defaultdict(
        lambda: collections.defaultdict(collections.Counter)
    )

    for r in rows:
        if r.get("token", "") not in FORMS:
            continue
        ao = ao_bit(r.get("suffix", ""))
        if not ao:
            continue
        sec = classify_section(r.get("folio", ""), r.get("section_note", ""))
        cur = r.get("currier", "unknown")
        section_ao[sec][ao] += 1
        currier_ao[cur][ao] += 1
        section_currier_ao[sec][cur][ao] += 1

    return {
        "section_ao": dict(section_ao),
        "currier_ao": dict(currier_ao),
        "section_currier_ao": {s: dict(d) for s, d in section_currier_ao.items()},
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_report(
    path: Path,
    tables: dict,
    v_sec: float,
    v_cur: float,
    intra_section_vs: dict[str, tuple[float, int, int, int]],
) -> None:
    lines = [
        "# Rota 47: seção vs escriba como preditor do bit a/o",
        "",
        "Esta rota testa se o bit a/o (vogal do sufixo) é determinado pelo ESCRIBA (Currier) ou pela SEÇÃO.",
        f"Guardrail: `{GUARDRAIL}`.",
        "",
        "## Resultado principal",
        "",
        f"- V(seção × ao) = **{v_sec:.4f}**",
        f"- V(Currier × ao) = **{v_cur:.4f}**",
        "",
    ]
    if v_sec < v_cur:
        lines.append("**Currier prevê ao melhor que seção** — sinal é de escriba, não de conteúdo.")
    else:
        lines.append("**Seção prevê ao melhor que Currier** — sinal é de conteúdo.")

    lines += [
        "",
        "## V(Currier × ao) DENTRO de cada seção",
        "",
        "Teste decisivo: se V permanece alto dentro da mesma seção → escriba modula ao → M3.",
        "",
        "| seção | n | A | B | V(Currier × ao) | veredito |",
        "|-------|---|---|---|-----------------|---------|",
    ]
    for sec, (v, n, na, nb) in sorted(intra_section_vs.items(), key=lambda x: -x[1][1]):
        if n < 5:
            continue
        verdict = "M3 (escriba)" if v > 0.25 else ("ambíguo" if v > 0.10 else "convergem (M5)")
        lines.append(f"| {sec} | {n} | {na} | {nb} | {v:.4f} | {verdict} |")

    lines += [
        "",
        "## Proporção a/o por seção",
        "",
        "| seção | n | %a | %o | Currier mix |",
        "|-------|---|----|----|-------------|",
    ]
    for sec, c in sorted(tables["section_ao"].items(), key=lambda x: -sum(x[1].values())):
        total = sum(c.values())
        a_pct = 100 * c.get("a", 0) // total
        o_pct = 100 * c.get("o", 0) // total
        cur_sec = tables["section_currier_ao"].get(sec, {})
        cur_str = " ".join(
            f"{cur}:{sum(cc.values())}"
            for cur, cc in sorted(cur_sec.items())
            if cur in ("A", "B", "unknown")
        )
        lines.append(f"| {sec} | {total} | {a_pct}% | {o_pct}% | {cur_str} |")

    lines += [
        "",
        "## Interpretação: modelo de três camadas",
        "",
        "Com base nas Rotas 43–47, o sufixo codifica três camadas distintas:",
        "",
        "| Camada | Bit | Preditor | Efeito |",
        "|--------|-----|----------|--------|",
        "| **a/o** (vogal) | dialeto/escriba | Currier (V≈0.45) | A=vogal-o; B=vogal-a |",
        "| **r/l** (consoante) | posição sintática | linha/locus | -l=fechamento; -r=continuação |",
        "| prefixo **qo-** | registro | locus_kind | qo-=prosa exclusivo; bare=rótulo+prosa |",
        "",
        "A borda não é um rótulo semântico do objeto — é uma composição de três sinalizadores",
        "ortogonais: quem escreve (a/o), onde está na frase (r/l), e em que registro (qo-).",
        "",
        f"Guardrail: `{GUARDRAIL}`.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "currier_csv",
        nargs="?",
        default=str(ROOT / "data" / "derived" / "exact_form_context_table_currier_zl3b.csv"),
    )
    parser.add_argument(
        "--out-section",
        default=str(ROOT / "data" / "derived" / "section_scribe_ao_zl3b.csv"),
    )
    parser.add_argument(
        "--out-intra",
        default=str(ROOT / "data" / "derived" / "section_scribe_intra_ao_zl3b.csv"),
    )
    parser.add_argument(
        "--out-summary",
        default=str(ROOT / "data" / "derived" / "section_scribe_ao_summary_zl3b.csv"),
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "research" / "rota_47_seccao_vs_escriba_ao.md"),
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    rows = read_csv(Path(args.currier_csv))
    tables = build_tables(rows)

    v_sec, _ = cramer_v(tables["section_ao"])
    v_cur, _ = cramer_v({k: v for k, v in tables["currier_ao"].items() if k in ("A", "B")})

    intra_vs: dict[str, tuple[float, int, int, int]] = {}
    for sec, cur_data in tables["section_currier_ao"].items():
        only_ab = {k: v for k, v in cur_data.items() if k in ("A", "B")}
        v, n = cramer_v(only_ab)
        na = sum(only_ab.get("A", {}).values())
        nb = sum(only_ab.get("B", {}).values())
        intra_vs[sec] = (v, n, na, nb)

    section_rows = [
        {
            "section": sec,
            "n_a": c.get("a", 0),
            "n_o": c.get("o", 0),
            "pct_a": round(100 * c.get("a", 0) / sum(c.values()), 1) if sum(c.values()) else 0,
            "semantic_guardrail": GUARDRAIL,
        }
        for sec, c in sorted(tables["section_ao"].items(), key=lambda x: -sum(x[1].values()))
    ]
    intra_rows = [
        {
            "section": sec,
            "n_ab": n,
            "n_a": na,
            "n_b": nb,
            "cramer_v_currier_ao": round(v, 4),
            "semantic_guardrail": GUARDRAIL,
        }
        for sec, (v, n, na, nb) in sorted(intra_vs.items(), key=lambda x: -x[1][1])
    ]
    summary_rows = [
        {"metric": "cramerV_section_ao", "value": str(round(v_sec, 4))},
        {"metric": "cramerV_currier_ao", "value": str(round(v_cur, 4))},
        {"metric": "predictor_of_ao", "value": "scribe" if v_cur > v_sec else "section"},
        {"metric": "herbal_v_currier_ao", "value": str(round(intra_vs.get("herbal", (0,))[0], 4))},
        {"metric": "pharma_v_currier_ao", "value": str(round(intra_vs.get("pharmaceutical", (0,))[0], 4))},
        {"metric": "semantic_guardrail", "value": GUARDRAIL},
    ]

    write_csv(Path(args.out_section), section_rows, ["section", "n_a", "n_o", "pct_a", "semantic_guardrail"])
    write_csv(Path(args.out_intra), intra_rows, ["section", "n_ab", "n_a", "n_b", "cramer_v_currier_ao", "semantic_guardrail"])
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])
    write_report(Path(args.md), tables, v_sec, v_cur, intra_vs)

    herbal_v = intra_vs.get("herbal", (0, 0, 0, 0))[0]
    pharma_v = intra_vs.get("pharmaceutical", (0, 0, 0, 0))[0]
    print(
        f"v_section_ao={v_sec:.4f} v_currier_ao={v_cur:.4f} "
        f"predictor={'scribe' if v_cur > v_sec else 'section'} "
        f"v_herbal_intra={herbal_v:.4f} v_pharma_intra={pharma_v:.4f}"
    )
    print(f"section_csv={args.out_section}")
    print(f"intra_csv={args.out_intra}")
    print(f"summary_csv={args.out_summary}")
    print(f"md={args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
