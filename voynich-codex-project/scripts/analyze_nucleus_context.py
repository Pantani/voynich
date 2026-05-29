#!/usr/bin/env python3
"""Rota 54: caracterizar o sinal de conteúdo do núcleo ch/sh (achado da Rota 53).

A Rota 53 estabeleceu que o núcleo de banco (ch=banco simples vs sh=banco com
pluma) é o PRIMEIRO elemento do token que segue CONTEÚDO (seção) e não ESCRIBA
(Currier): V(seção)=0.14 > V(Currier)=0.06, sobrevive dentro de Currier B
(V=0.157), perm p≈0.002, sobre ~14594 tokens ch-XOR-sh. Esta rota disseca o
sinal com três sub-ataques falsificáveis, reutilizando os helpers canônicos de
`scripts.analyze_nucleus` (clean_token / nucleus / classify_section / cramer_v /
permutation_p) para garantir que a contagem reproduz a Rota 53.

R54-A — Balneológico: label vs texto.
  Dentro dos fólios balneológicos (75–84), o excesso de sh está concentrado em
  loci de RÓTULO (kind L: rótulos de ninfas/partes do corpo) vs TEXTO corrido
  (kind P)? Tabela 2×2 kind(L vs P) × núcleo(ch/sh) restrita a 75–84.
  H1 = sh maior em L (sh ligado a nomear ninfas/partes); H0 = igual (sh é
  propriedade de seção inteira).

R54-B — Núcleo × operador (ortogonalidade).
  Para cada token com núcleo ch/sh definido, operador = "ok" se "ok" no token,
  senão "ot" se "ot" no token, senão "none". Tabela operador × núcleo; V de
  Cramér + perm p; e V dentro de Currier B (controle). O modelo em camadas prevê
  INDEPENDÊNCIA (V≈0, p>0.05): o conteúdo ch/sh é ortogonal à camada de registro
  ok/ot. Associação forte refutaria a ortogonalidade pura.

R54-C — Ambiente condicional / entropia.
  ch e sh abrem distribuições de ambiente diferentes? Para cada ocorrência de
  "ch" e "sh" dentro de tokens, registra o caractere imediatamente seguinte
  dentro do token (se o dígrafo termina o token, marca "$END"). Entropia de
  Shannon H(próx|ch) e H(próx|sh) em bits + top-5 continuações com prob para
  cada banco. Se H e as continuações diferem materialmente, ch e sh NÃO são
  variantes livres: carregam ambientes distintos.

NÃO é decifração: é estrutura. Guardrail em todo CSV de saída.
"""
from __future__ import annotations

import argparse
import collections
import csv
import math
import re
from pathlib import Path

from scripts.analyze_nucleus import (
    classify_section,
    clean_token,
    cramer_v,
    nucleus,
    permutation_p,
)

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota54_nucleus_context_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"

_HDR = re.compile(r"^<(f[0-9]+[rv]\d?)>")
# Locus line: <folio.unit,<marker><CODE>...>  body
# The KIND is the FIRST uppercase letter after the comma, past any marker
# char ([@+=*&~] all occur in ZL3b). Group 2 captures that KIND letter.
_LOC_KIND = re.compile(r"^<(f[0-9]+[rv]\d?)\.\d+,[^A-Z>]*([A-Z])[^>]*>\s*(.*)$")
# Fallback for any locus line lacking the comma/KIND (defensive; rare).
_LOC_BARE = re.compile(r"^<(f[0-9]+[rv]\d?)\.\d+[^>]*>\s*(.*)$")


def parse_corpus_with_kind(
    path: Path,
) -> list[tuple[str, str, str]]:
    """Return [(folio, locus_kind, clean_token), ...] from ZL3b IVTFF.

    locus_kind is one of P/L/C/R (or "?" if the locus carried no recognizable
    KIND letter). Tokenization mirrors analyze_nucleus.parse_corpus exactly
    (same clean_token, same split on '.', commas already inside the locus tag
    are not part of the body), so the ch/sh token totals reproduce Rota 53.
    """
    out: list[tuple[str, str, str]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if _HDR.match(line):
            continue
        mk = _LOC_KIND.match(line)
        if mk:
            folio, kind, body = mk.group(1), mk.group(2), mk.group(3)
        else:
            mb = _LOC_BARE.match(line)
            if not mb:
                continue
            folio, kind, body = mb.group(1), "?", mb.group(2)
        body = body.replace(",", ".")
        for raw in body.split("."):
            tok = clean_token(raw)
            if tok:
                out.append((folio, kind, tok))
    return out


def operator_of(token: str) -> str:
    """Register operator carried by a token: ok > ot > none (Rota 43/47 rule)."""
    if "ok" in token:
        return "ok"
    if "ot" in token:
        return "ot"
    return "none"


def folio_num(folio: str) -> int:
    m = re.search(r"\d+", folio.lower())
    return int(m.group()) if m else 0


def shannon_entropy(counter: collections.Counter) -> float:
    """Shannon entropy in bits of a Counter of next-char outcomes."""
    n = sum(counter.values())
    if n == 0:
        return 0.0
    h = 0.0
    for c in counter.values():
        if c:
            p = c / n
            h -= p * math.log2(p)
    return h


def _kind_pct_rows(table: dict[str, collections.Counter]) -> list[dict]:
    rows = []
    for kind, c in sorted(table.items(), key=lambda x: -sum(x[1].values())):
        n = sum(c.values())
        rows.append(
            {
                "kind": kind,
                "n": n,
                "n_ch": c.get("ch", 0),
                "n_sh": c.get("sh", 0),
                "pct_sh": round(100 * c.get("sh", 0) / n, 2) if n else 0.0,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def _operator_rows(table: dict[str, collections.Counter]) -> list[dict]:
    rows = []
    for op in ("ok", "ot", "none"):
        c = table.get(op, collections.Counter())
        n = sum(c.values())
        rows.append(
            {
                "operator": op,
                "n_ch": c.get("ch", 0),
                "n_sh": c.get("sh", 0),
                "pct_sh": round(100 * c.get("sh", 0) / n, 2) if n else 0.0,
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


def build(
    records: list[tuple[str, str, str]],
    folio_currier: dict[str, str] | None = None,
) -> dict:
    """Build the three sub-attack structures from (folio, kind, token) records.

    folio_currier is optional; when provided it enables the within-Currier-B
    control for R54-B. Tokens with no defined ch/sh nucleus are skipped (same
    binary contrast as Rota 53).
    """
    folio_currier = folio_currier or {}

    # R54-A: kind(L vs P) x nucleus, restricted to balneological folios 75-84.
    balneo: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    balneo_labeled: list[tuple[str, str]] = []

    # R54-B: operator(ok/ot/none) x nucleus (all defined-nucleus tokens).
    operator: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    operator_labeled: list[tuple[str, str]] = []
    operatorB: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)

    # R54-C: next char after each ch / each sh occurrence inside tokens.
    nxt: dict[str, collections.Counter] = {
        "ch": collections.Counter(),
        "sh": collections.Counter(),
    }

    n_chsh = 0
    for folio, kind, tok in records:
        # R54-C uses EVERY ch/sh occurrence (independent of the XOR rule):
        for bench in ("ch", "sh"):
            start = 0
            while True:
                i = tok.find(bench, start)
                if i < 0:
                    break
                j = i + 2
                nxt[bench][tok[j] if j < len(tok) else "$END"] += 1
                start = i + 1  # allow overlap (e.g. 'chch')

        nuc = nucleus(tok)
        if not nuc:
            continue
        n_chsh += 1

        if classify_section(folio) == "balneological" and kind in ("L", "P"):
            balneo[kind][nuc] += 1
            balneo_labeled.append((kind, nuc))

        op = operator_of(tok)
        operator[op][nuc] += 1
        operator_labeled.append((op, nuc))
        if folio_currier.get(folio) == "B":
            operatorB[op][nuc] += 1

    return {
        "balneo": dict(balneo),
        "balneo_labeled": balneo_labeled,
        "operator": dict(operator),
        "operator_labeled": operator_labeled,
        "operatorB": dict(operatorB),
        "next": nxt,
        "n_chsh": n_chsh,
    }


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("corpus", nargs="?", default=str(DEFAULT_CORPUS))
    p.add_argument("--n-perm", type=int, default=500)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--top-k", type=int, default=5)
    d = ROOT / "data" / "derived"
    p.add_argument("--out-balneo", default=str(d / "nucleus_context_balneo_zl3b.csv"))
    p.add_argument("--out-operator", default=str(d / "nucleus_operator_zl3b.csv"))
    p.add_argument("--out-next", default=str(d / "nucleus_next_glyph_zl3b.csv"))
    p.add_argument("--out-summary", default=str(d / "nucleus_context_summary_zl3b.csv"))
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    # Reuse analyze_nucleus.parse_corpus solely for the folio->Currier map
    # (the within-B control of R54-B). Token enumeration comes from the
    # kind-aware parser so the two stay consistent with Rota 53.
    from scripts.analyze_nucleus import parse_corpus as _parse_currier

    folio_currier, _ = _parse_currier(Path(args.corpus))
    records = parse_corpus_with_kind(Path(args.corpus))
    b = build(records, folio_currier)

    # R54-A
    v_balneo, n_balneo = cramer_v(b["balneo"])
    p_balneo = permutation_p(b["balneo_labeled"], v_balneo, args.n_perm, args.seed)
    bal = b["balneo"]
    sh_pct_L = (
        100 * bal.get("L", collections.Counter()).get("sh", 0) / sum(bal["L"].values())
        if bal.get("L") and sum(bal["L"].values())
        else 0.0
    )
    sh_pct_P = (
        100 * bal.get("P", collections.Counter()).get("sh", 0) / sum(bal["P"].values())
        if bal.get("P") and sum(bal["P"].values())
        else 0.0
    )

    # R54-B
    v_op, n_op = cramer_v(b["operator"])
    p_op = permutation_p(b["operator_labeled"], v_op, args.n_perm, args.seed)
    v_opB, n_opB = cramer_v(b["operatorB"])

    # R54-C
    h_ch = shannon_entropy(b["next"]["ch"])
    h_sh = shannon_entropy(b["next"]["sh"])

    def top(counter: collections.Counter, k: int) -> list[tuple[str, int, float]]:
        n = sum(counter.values())
        return [
            (ch, cnt, round(cnt / n, 4) if n else 0.0)
            for ch, cnt in counter.most_common(k)
        ]

    top_ch = top(b["next"]["ch"], args.top_k)
    top_sh = top(b["next"]["sh"], args.top_k)

    # --- write CSVs ---
    write_csv(
        Path(args.out_balneo),
        _kind_pct_rows(b["balneo"]),
        ["kind", "n", "n_ch", "n_sh", "pct_sh", "semantic_guardrail"],
    )
    write_csv(
        Path(args.out_operator),
        _operator_rows(b["operator"]),
        ["operator", "n_ch", "n_sh", "pct_sh", "semantic_guardrail"],
    )
    next_rows = []
    for bench in ("ch", "sh"):
        counter = b["next"][bench]
        n = sum(counter.values())
        for ch, cnt in counter.most_common():
            next_rows.append(
                {
                    "bench": bench,
                    "next_char": ch,
                    "count": cnt,
                    "prob": round(cnt / n, 6) if n else 0.0,
                    "semantic_guardrail": GUARDRAIL,
                }
            )
    write_csv(
        Path(args.out_next),
        next_rows,
        ["bench", "next_char", "count", "prob", "semantic_guardrail"],
    )

    summary_rows = [
        {"metric": "n_chsh_tokens", "value": str(b["n_chsh"])},
        {"metric": "A_cramerV_kind_balneo", "value": str(round(v_balneo, 4))},
        {"metric": "A_perm_p_kind_balneo", "value": str(round(p_balneo, 6))},
        {"metric": "A_n_balneo", "value": str(n_balneo)},
        {"metric": "A_sh_pct_label", "value": str(round(sh_pct_L, 2))},
        {"metric": "A_sh_pct_text", "value": str(round(sh_pct_P, 2))},
        {"metric": "B_cramerV_operator_nucleus", "value": str(round(v_op, 4))},
        {"metric": "B_perm_p_operator_nucleus", "value": str(round(p_op, 6))},
        {"metric": "B_n_operator", "value": str(n_op)},
        {"metric": "B_cramerV_operator_within_B", "value": str(round(v_opB, 4))},
        {"metric": "B_n_within_B", "value": str(n_opB)},
        {"metric": "C_entropy_next_ch_bits", "value": str(round(h_ch, 4))},
        {"metric": "C_entropy_next_sh_bits", "value": str(round(h_sh, 4))},
        {"metric": "C_top1_after_ch", "value": f"{top_ch[0][0]}={top_ch[0][2]}" if top_ch else ""},
        {"metric": "C_top1_after_sh", "value": f"{top_sh[0][0]}={top_sh[0][2]}" if top_sh else ""},
        {
            "metric": "A_predictor",
            "value": "label" if sh_pct_L > sh_pct_P else ("text" if sh_pct_P > sh_pct_L else "equal"),
        },
        {
            "metric": "B_orthogonal",
            "value": str(v_op < 0.10 and (math.isnan(p_op) or p_op > 0.05)),
        },
        {"metric": "C_free_variants", "value": str(abs(h_ch - h_sh) < 0.05)},
        {"metric": "semantic_guardrail", "value": GUARDRAIL},
    ]
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    print(
        f"n_chsh={b['n_chsh']} | A: V_kind={v_balneo:.4f} p={p_balneo:.4g} "
        f"n={n_balneo} sh%L={sh_pct_L:.2f} sh%P={sh_pct_P:.2f}"
    )
    print(
        f"B: V_op={v_op:.4f} p={p_op:.4g} n={n_op} V_op_within_B={v_opB:.4f} n_B={n_opB}"
    )
    print(f"C: H_ch={h_ch:.4f} bits H_sh={h_sh:.4f} bits")
    print(f"C: top_ch={top_ch}")
    print(f"C: top_sh={top_sh}")
    print(f"balneo_csv={args.out_balneo}")
    print(f"operator_csv={args.out_operator}")
    print(f"next_csv={args.out_next}")
    print(f"summary_csv={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
