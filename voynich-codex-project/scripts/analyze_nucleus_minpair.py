#!/usr/bin/env python3
"""Rota 55: ch/sh — escolha SEMÂNTICA (conteúdo) ou ALOGRAFIA (alternância)?

A Rota 53 mostrou que o banco ch/sh segue a SEÇÃO do manuscrito (V=0.14,
p≈0.002). A Rota 54 temperou: o enviesamento de seção vive na PROSA (não em
rótulos), ch/sh acopla fracamente ao operador ok/ot (V=0.11) e ch/sh são dois
valores de UM slot (mesmo inventário de sucessores, ΔH=0.38). Fica em aberto:
a escolha ch vs sh é SEMÂNTICA (conteúdo) ou uma ALOGRAFIA (alternância
fonológica/posicional)?

DESENHO DECISIVO — par mínimo por troca de banco.
  Um "esqueleto" = um token com o banco substituído por '#'.
    "chol" -> "#ol", "shol" -> "#ol"  (mesmo esqueleto).
  Um esqueleto é PAR MÍNIMO se TANTO uma forma-ch QUANTO uma forma-sh ocorrem
  no corpus. A sacada: dentro de um esqueleto fixo, todo vizinho IN-TOKEN é
  CONSTANTE por construção (só o banco muda) — logo a única coisa que pode
  variar entre ocorrências e "explicar" a escolha do banco é EXTERNA: a SEÇÃO,
  o TOKEN ANTERIOR e a POSIÇÃO NA LINHA. Perguntamos qual delas governa a
  escolha do banco, mantendo o esqueleto fixo.

MÉTRICA — informação mútua condicional (em bits, de contagens, sempre >=0):
  I(B;X|S) = H(B|S) - H(B|S,X)
    I_section   = I(banco ; seção      | esqueleto)
    I_prevchar  = I(banco ; char_anterior | esqueleto)
    I_linepos   = I(banco ; posição_linha | esqueleto)
  Computadas SÓ sobre o conjunto de pares mínimos (esqueletos com >=1 ch E
  >=1 sh). p de permutação para I_section e para max(I_prevchar,I_linepos):
  embaralha o rótulo condicionante no conjunto de pares mínimos, recomputa,
  p = fração >= observado (seed fixa, 500 perms).

VEREDITO:
  - I_section domina (I_section > max(neighbor) e p_section<0.05) -> "content/semantic"
  - vizinho domina (max neighbor > I_section e p_neighbor<0.05) -> "allography/positional"
  - ambos ~0 / não significativos -> "lexically_fixed" (vocabulário separado por
    seção explica a Rota 53, não uma regra produtiva de ch/sh)

Se os tokens de par mínimo forem poucos (<300) o teste é SUBDIMENSIONADO — e
essa contagem baixa é ela mesma informativa: significaria que o banco é
sobretudo fixo lexicalmente por palavra (nem conteúdo nem alografia produtivos).

NÃO é decifração: é estrutura. Guardrail em todo CSV de saída.
"""
from __future__ import annotations

import argparse
import collections
import csv
import math
import random
import re
from pathlib import Path

from scripts.analyze_nucleus import (
    classify_section,
    clean_token,
    nucleus,
)

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota55_minpair_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"

_HDR = re.compile(r"^<(f[0-9]+[rv]\d?)>")
_LOC = re.compile(r"^<(f[0-9]+[rv]\d?)\.\d+[^>]*>\s*(.*)$")
_LANG = re.compile(r"\$L=([A-Z?])")


def skeleton(token: str, bench: str) -> str:
    """Token with its (single) bench glyph marked '#'.

    bench is 'ch' or 'sh'. Every occurrence of that digraph is replaced so the
    skeleton is bench-agnostic: skeleton('chol','ch') == skeleton('shol','sh').
    Callers pass tokens whose nucleus is a single bench TYPE (see nucleus()),
    so only one of ch/sh is present and this is unambiguous.
    """
    return token.replace(bench, "#")


def parse_loci(path: Path) -> tuple[dict[str, str], list[tuple[str, list[str]]]]:
    """Return (folio->Currier, [(folio, [clean_token, ...]), ...]).

    Token ORDER within each locus line is preserved so the previous token is
    well defined, and each locus is its own list so prev resets at locus start.
    Tokenization mirrors analyze_nucleus.parse_corpus exactly (same clean_token,
    same '.'/',' split), so the flattened token sequence reproduces Rota 53.
    """
    folio_currier: dict[str, str] = {}
    loci: list[tuple[str, list[str]]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        mh = _HDR.match(line)
        if mh:
            cur_folio = mh.group(1)
            ml = _LANG.search(line)
            folio_currier[cur_folio] = ml.group(1) if ml else "?"
            continue
        ml = _LOC.match(line)
        if ml:
            folio, body = ml.group(1), ml.group(2).replace(",", ".")
            toks = [t for t in (clean_token(r) for r in body.split(".")) if t]
            if toks:
                loci.append((folio, toks))
    return folio_currier, loci


def line_position(idx: int, length: int) -> str:
    """initial / medial / final from token index within its locus line."""
    if length <= 1 or idx == 0:
        return "initial"
    if idx == length - 1:
        return "final"
    return "medial"


def collect(
    folio_currier: dict[str, str], loci: list[tuple[str, list[str]]]
) -> list[dict[str, str]]:
    """One record per single-bench (ch XOR sh) token, with external context.

    Records carry: skeleton, bench, section, currier, prev_char (last char of
    previous clean token in the same locus, or '^' if locus-initial), line_pos.
    Tokens with both benches or neither (nucleus()==None) are skipped — the
    same binary universe as Rota 53 (~14594 tokens).
    """
    records: list[dict[str, str]] = []
    for folio, toks in loci:
        sec = classify_section(folio)
        cur = folio_currier.get(folio, "?")
        n = len(toks)
        prev_tok: str | None = None
        for idx, tok in enumerate(toks):
            nuc = nucleus(tok)
            if nuc:
                records.append(
                    {
                        "skeleton": skeleton(tok, nuc),
                        "bench": nuc,
                        "section": sec,
                        "currier": cur,
                        "prev_char": prev_tok[-1] if prev_tok else "^",
                        "line_pos": line_position(idx, n),
                        "token": tok,
                        "folio": folio,
                    }
                )
            prev_tok = tok
    return records


def minimal_pair_skeletons(records: list[dict[str, str]]) -> set[str]:
    """Skeletons that occur with BOTH a ch-form and an sh-form in the corpus."""
    benches: dict[str, set[str]] = collections.defaultdict(set)
    for r in records:
        benches[r["skeleton"]].add(r["bench"])
    return {sk for sk, bs in benches.items() if {"ch", "sh"} <= bs}


def _entropy_from_counts(counts) -> float:
    """Shannon entropy (bits) of an iterable of nonneg counts."""
    n = sum(counts)
    if n <= 0:
        return 0.0
    h = 0.0
    for c in counts:
        if c:
            p = c / n
            h -= p * math.log2(p)
    return h


def conditional_entropy_b_given(
    pairs: list[tuple[str, str]],
) -> float:
    """H(B | C) in bits from a list of (context, bench) pairs.

    H(B|C) = Σ_c P(c) H(B | C=c). Used both for C=skeleton (giving H(B|S)) and
    for C=(skeleton, X) (giving H(B|S,X)); the caller forms the composite key.
    """
    by_ctx: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for ctx, b in pairs:
        by_ctx[ctx][b] += 1
    total = len(pairs)
    if total == 0:
        return 0.0
    h = 0.0
    for cnt in by_ctx.values():
        nc = sum(cnt.values())
        h += (nc / total) * _entropy_from_counts(cnt.values())
    return h


def conditional_mi(
    skel: list[str], bench: list[str], x: list[str]
) -> float:
    """I(B ; X | S) = H(B|S) - H(B|S,X) in bits, from parallel count lists.

    All three lists are parallel and the same length (one entry per minimal-pair
    token occurrence). S = skeleton (always the conditioning variable here),
    X = the candidate explanator (section / prev_char / line_pos). The result is
    provably >= 0; a tiny negative from float error is clamped to 0.
    """
    h_b_given_s = conditional_entropy_b_given(list(zip(skel, bench)))
    composite = [f"{s}\x00{xi}" for s, xi in zip(skel, x)]
    h_b_given_sx = conditional_entropy_b_given(list(zip(composite, bench)))
    return max(0.0, h_b_given_s - h_b_given_sx)


def permutation_p(
    skel: list[str],
    bench: list[str],
    x: list[str],
    observed: float,
    n_perm: int,
    seed: int = 0,
) -> float:
    """Fraction of label-shuffles whose I(B;X|S) >= observed.

    Shuffles the conditioning label X across the minimal-pair set (skeleton and
    bench held fixed), breaking any X->bench link while preserving the per-
    skeleton bench distribution. Small p => the observed conditional MI is
    unlikely if X were irrelevant given the skeleton.
    """
    if n_perm <= 0 or not skel:
        return float("nan")
    rng = random.Random(seed)
    x_shuf = list(x)
    hits = 0
    for _ in range(n_perm):
        rng.shuffle(x_shuf)
        if conditional_mi(skel, bench, x_shuf) >= observed:
            hits += 1
    return (hits + 1) / (n_perm + 1)


def verdict(
    i_section: float,
    i_prevchar: float,
    i_linepos: float,
    p_section: float,
    p_neighbor: float,
    alpha: float = 0.05,
) -> str:
    """Encode the Rota 55 decision rule (see module docstring)."""
    i_neighbor = max(i_prevchar, i_linepos)
    sec_sig = (not math.isnan(p_section)) and p_section < alpha
    nbr_sig = (not math.isnan(p_neighbor)) and p_neighbor < alpha
    if i_section > i_neighbor and sec_sig:
        return "content/semantic"
    if i_neighbor > i_section and nbr_sig:
        return "allography/positional"
    return "lexically_fixed"


def build(records: list[dict[str, str]]) -> dict:
    """Restrict to minimal-pair tokens and assemble the parallel context lists."""
    mp_skels = minimal_pair_skeletons(records)
    mp = [r for r in records if r["skeleton"] in mp_skels]

    skel = [r["skeleton"] for r in mp]
    bench = [r["bench"] for r in mp]
    sec = [r["section"] for r in mp]
    prev = [r["prev_char"] for r in mp]
    pos = [r["line_pos"] for r in mp]

    # per-skeleton ch/sh counts + dominant section per bench (for the CSV)
    per: dict[str, dict] = {}
    for r in mp:
        d = per.setdefault(
            r["skeleton"],
            {"n_ch": 0, "n_sh": 0,
             "sec_ch": collections.Counter(), "sec_sh": collections.Counter()},
        )
        if r["bench"] == "ch":
            d["n_ch"] += 1
            d["sec_ch"][r["section"]] += 1
        else:
            d["n_sh"] += 1
            d["sec_sh"][r["section"]] += 1

    n_chsh_total = len(records)
    return {
        "mp_skeletons": mp_skels,
        "n_minpair_skeletons": len(mp_skels),
        "n_minpair_tokens": len(mp),
        "n_chsh_total": n_chsh_total,
        "frac_in_minpairs": (len(mp) / n_chsh_total) if n_chsh_total else 0.0,
        "skel": skel,
        "bench": bench,
        "section": sec,
        "prev_char": prev,
        "line_pos": pos,
        "per_skeleton": per,
    }


def _skeleton_rows(per: dict[str, dict]) -> list[dict]:
    rows = []
    for sk, d in sorted(per.items(), key=lambda kv: -(kv[1]["n_ch"] + kv[1]["n_sh"])):
        top_ch = d["sec_ch"].most_common(1)
        top_sh = d["sec_sh"].most_common(1)
        rows.append(
            {
                "skeleton": sk,
                "n_ch": d["n_ch"],
                "n_sh": d["n_sh"],
                "top_section_ch": f"{top_ch[0][0]}({top_ch[0][1]})" if top_ch else "",
                "top_section_sh": f"{top_sh[0][0]}({top_sh[0][1]})" if top_sh else "",
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return rows


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
    d = ROOT / "data" / "derived"
    p.add_argument("--out-skeletons", default=str(d / "nucleus_minpair_skeletons_zl3b.csv"))
    p.add_argument("--out-summary", default=str(d / "nucleus_minpair_summary_zl3b.csv"))
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    folio_currier, loci = parse_loci(Path(args.corpus))
    records = collect(folio_currier, loci)
    b = build(records)

    i_section = conditional_mi(b["skel"], b["bench"], b["section"])
    i_prevchar = conditional_mi(b["skel"], b["bench"], b["prev_char"])
    i_linepos = conditional_mi(b["skel"], b["bench"], b["line_pos"])

    p_section = permutation_p(
        b["skel"], b["bench"], b["section"], i_section, args.n_perm, args.seed
    )
    # neighbor permutation tests the stronger of the two neighbor signals
    if i_prevchar >= i_linepos:
        p_neighbor = permutation_p(
            b["skel"], b["bench"], b["prev_char"], i_prevchar, args.n_perm, args.seed
        )
    else:
        p_neighbor = permutation_p(
            b["skel"], b["bench"], b["line_pos"], i_linepos, args.n_perm, args.seed
        )

    vdt = verdict(i_section, i_prevchar, i_linepos, p_section, p_neighbor)
    underpowered = b["n_minpair_tokens"] < 300

    write_csv(
        Path(args.out_skeletons),
        _skeleton_rows(b["per_skeleton"]),
        ["skeleton", "n_ch", "n_sh", "top_section_ch", "top_section_sh", "semantic_guardrail"],
    )

    summary_rows = [
        {"metric": "n_minpair_skeletons", "value": str(b["n_minpair_skeletons"])},
        {"metric": "n_minpair_tokens", "value": str(b["n_minpair_tokens"])},
        {"metric": "frac_of_chsh_in_minpairs", "value": str(round(b["frac_in_minpairs"], 4))},
        {"metric": "I_section_bits", "value": str(round(i_section, 6))},
        {"metric": "I_prevchar_bits", "value": str(round(i_prevchar, 6))},
        {"metric": "I_linepos_bits", "value": str(round(i_linepos, 6))},
        {"metric": "perm_p_section", "value": str(round(p_section, 6))},
        {"metric": "perm_p_neighbor", "value": str(round(p_neighbor, 6))},
        {"metric": "underpowered", "value": str(underpowered)},
        {"metric": "verdict", "value": vdt},
        {"metric": "guardrail", "value": GUARDRAIL},
    ]
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    flag = " [UNDERPOWERED <300 minpair tokens]" if underpowered else ""
    print(
        f"n_minpair_skeletons={b['n_minpair_skeletons']} "
        f"n_minpair_tokens={b['n_minpair_tokens']}{flag} "
        f"frac_of_chsh_in_minpairs={b['frac_in_minpairs']:.4f} "
        f"(chsh_total={b['n_chsh_total']})"
    )
    print(
        f"I_section={i_section:.6f} bits (p={p_section:.4g}) | "
        f"I_prevchar={i_prevchar:.6f} | I_linepos={i_linepos:.6f} "
        f"(neighbor p={p_neighbor:.4g})"
    )
    print(f"verdict={vdt}")
    print(f"skeletons_csv={args.out_skeletons}")
    print(f"summary_csv={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
