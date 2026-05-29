#!/usr/bin/env python3
"""Rota 57: o sinal topical da PALAVRA (Rota 56) é REFERENCIAL ou de REGISTRO?

A Rota 56 achou um sinal topical FRACO-MAS-REAL no nível da PALAVRA INTEIRA:
a identidade da palavra prevê a seção ALÉM de escriba/tipo-de-locus/autocorrelação
de fólio (dentro de Currier B, estrito I_norm=0.046, z≈5.6). Crucialmente o sinal
vivia nos loci de PROSA (o controle de tipo-de-locus mostrou que RÓTULOS não o
dirigem). Esta rota fecha a pergunta que aquilo deixou em aberto:

  - REFERENCIAL: as palavras diagnósticas NOMEIAM objetos desenhados → estariam
    ligadas a RÓTULO (label_frac alto) e CONCENTRADAS nos poucos fólios que mostram
    aquele objeto (baixa entropia de fólio / alto top_folio_share).
  - REGISTRO DE PROSA: a topicalidade é só variação de vocabulário de texto corrido
    (seções diferentes escritas com vocabulário de prosa levemente diferente) → as
    palavras diagnósticas se espalham pela PROSA de muitos fólios, NÃO em rótulos.

Conjunto diagnóstico: para cada seção PRINCIPAL (herbal, balneological, recipes,
pharmaceutical, astronomical) recomputa o lift por seção exatamente como o
top_lift_by_section da Rota 56 (lift_S(palavra)=P(S|palavra)/P(S), freq>=20) e toma
as TOP 15 palavras por lift_S como o "conjunto diagnóstico" daquela seção. Une-as
como palavras DIAGNÓSTICAS; todas as outras palavras freq>=20 são BASELINE.

Para CADA palavra freq>=20, a partir de parse_corpus_with_kind:
  - label_frac = ocorrências em loci de rótulo (kind=='L') / total de ocorrências.
  - para_frac  = fração kind=='P'.
  - folio_entropy_norm = entropia de Shannon da distribuição da palavra entre
    FÓLIOS, normalizada por log2(n_fólios em que aparece). BAIXA = concentrada em
    poucos fólios (tipo-nome); ALTA = espalhada (tipo-prosa).
  - top_folio_share = fração máxima das ocorrências da palavra num único fólio.

Compara DIAGNÓSTICO vs BASELINE (médias + teste de permutação da diferença de
médias, stdlib): label_frac, folio_entropy_norm, top_folio_share; e a baseline
de label_frac do CORPUS inteiro; conta diagnósticas label-dominantes
(label_frac>0.5) e fólio-concentradas (top_folio_share>0.5).

NÃO é decifração: mede se as palavras topicais NOMEIAM objetos ou são vocabulário
de registro de prosa. Guardrail em todo CSV de saída.
"""
from __future__ import annotations

import argparse
import collections
import csv
import math
import random
from pathlib import Path

# Reusa os helpers canônicos (Rota 53/54/56) para garantir que a tokenização e a
# classificação de seção reproduzem exatamente as rotas anteriores.
from scripts.analyze_nucleus import classify_section, parse_corpus
from scripts.analyze_nucleus_context import parse_corpus_with_kind

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota57_word_grounding_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"

# Seções "principais" (mesmas da Rota 56) das quais extraímos o conjunto diagnóstico.
MAJOR_SECTIONS = ["herbal", "balneological", "recipes", "pharmaceutical", "astronomical"]
MIN_FREQ = 20       # tipos de palavra "frequentes" (idêntico à Rota 56)
TOP_PER_SECTION = 15  # top-N por lift_S por seção -> conjunto diagnóstico


def entropy(counts) -> float:
    """Entropia de Shannon (bits) de uma coleção de contagens."""
    total = sum(counts)
    if total <= 0:
        return 0.0
    h = 0.0
    for c in counts:
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


def top_lift_by_section(
    pairs: list[tuple[str, str]],
    sections: list[str],
    min_freq: int,
    top_n: int,
) -> dict[str, list[tuple[str, int, float]]]:
    """Top-N palavras por lift_S para cada seção (igual à Rota 56).

    Para a seção S: lift_S(palavra) = P(S|palavra)/P(S). Ordena palavras
    freq>=min_freq por lift_S decrescente (desempate por freq). Retorna
    {S: [(word, freq, lift_S)]}.
    """
    sec_counts: collections.Counter = collections.Counter(s for _, s in pairs)
    n = len(pairs)
    word_sec: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for word, sec in pairs:
        word_sec[word][sec] += 1
    freq = {w: sum(c.values()) for w, c in word_sec.items()}
    out: dict[str, list[tuple[str, int, float]]] = {}
    for S in sections:
        pS = sec_counts.get(S, 0) / n if n else 0.0
        if pS <= 0:
            out[S] = []
            continue
        scored = []
        for w, secs in word_sec.items():
            if freq[w] < min_freq:
                continue
            lift_S = (secs.get(S, 0) / freq[w]) / pS
            scored.append((w, freq[w], round(lift_S, 3)))
        scored.sort(key=lambda x: (-x[2], -x[1]))
        out[S] = scored[:top_n]
    return out


def diagnostic_set(
    pairs: list[tuple[str, str]],
    sections: list[str],
    min_freq: int,
    top_n: int,
) -> tuple[set[str], dict[str, str]]:
    """Pool das top-N por lift_S de cada seção principal -> conjunto DIAGNÓSTICO.

    Retorna (set de palavras diagnósticas, mapa word->seção que a elegeu). Quando
    uma palavra figura no top de mais de uma seção, fica com a de MAIOR lift_S
    (a seção que mais a "puxa"); empate quebra por ordem de `sections`.
    """
    tops = top_lift_by_section(pairs, sections, min_freq, top_n)
    best_lift: dict[str, float] = {}
    word_section: dict[str, str] = {}
    for S in sections:
        for w, _freq, lift in tops.get(S, []):
            if w not in best_lift or lift > best_lift[w]:
                best_lift[w] = lift
                word_section[w] = S
    return set(word_section), word_section


def word_grounding_metrics(
    records: list[tuple[str, str, str]], min_freq: int
) -> dict[str, dict]:
    """Por tipo de palavra freq>=min_freq: label_frac, para_frac, folio_entropy_norm,
    top_folio_share, freq.

    `records` = [(folio, locus_kind, token), ...] de parse_corpus_with_kind.
    folio_entropy_norm = H(distribuição entre fólios) / log2(n_fólios); para uma
    palavra que aparece num único fólio, log2(1)=0 → definimos 0.0 (totalmente
    concentrada). BAIXO = concentrada (tipo-nome); ALTO (→1) = espalhada (prosa).
    """
    kind_counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    folio_counts: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for folio, kind, tok in records:
        kind_counts[tok][kind] += 1
        folio_counts[tok][folio] += 1

    out: dict[str, dict] = {}
    for word, fc in folio_counts.items():
        freq = sum(fc.values())
        if freq < min_freq:
            continue
        kc = kind_counts[word]
        label_frac = kc.get("L", 0) / freq
        para_frac = kc.get("P", 0) / freq
        n_folios = len(fc)
        h_folio = entropy(fc.values())
        denom = math.log2(n_folios) if n_folios > 1 else 0.0
        folio_entropy_norm = (h_folio / denom) if denom > 0 else 0.0
        top_folio_share = max(fc.values()) / freq
        out[word] = {
            "freq": freq,
            "label_frac": label_frac,
            "para_frac": para_frac,
            "folio_entropy_norm": folio_entropy_norm,
            "top_folio_share": top_folio_share,
            "n_folios": n_folios,
        }
    return out


def perm_test_mean_diff(
    group_a: list[float], group_b: list[float], n_perm: int, seed: int
) -> tuple[float, float, float]:
    """Teste de permutação bicaudal da diferença de médias (mean_a - mean_b).

    Embaralha os rótulos de grupo entre os valores combinados, recomputa a
    diferença de médias a cada vez. Retorna (diff_observada, mean_a, p_empírico).
    p = fração de embaralhamentos com |diff| >= |diff_observada| (com +1 no num/den,
    convenção conservadora). Se um grupo está vazio, p = NaN.
    """
    na, nb = len(group_a), len(group_b)
    mean_a = sum(group_a) / na if na else float("nan")
    mean_b = sum(group_b) / nb if nb else float("nan")
    obs_diff = mean_a - mean_b
    if na == 0 or nb == 0 or n_perm <= 0:
        return obs_diff, mean_a, float("nan")
    pool = group_a + group_b
    rng = random.Random(seed)
    abs_obs = abs(obs_diff)
    hits = 0
    for _ in range(n_perm):
        rng.shuffle(pool)
        ma = sum(pool[:na]) / na
        mb = sum(pool[na:]) / nb
        if abs(ma - mb) >= abs_obs - 1e-12:
            hits += 1
    p = (hits + 1) / (n_perm + 1)
    return obs_diff, mean_a, p


def decide_verdict(
    corpus_label_frac: float,
    diag_label_frac: float,
    base_label_frac: float,
    diag_folio_entropy: float,
    base_folio_entropy: float,
    diag_top_share: float,
    base_top_share: float,
    n_diag_label_dominant: int,
    n_diag: int,
    n_diag_folio_concentrated: int = 0,
) -> str:
    """Codifica o veredito da rota a partir das ASSINATURAS falsificáveis.

    - "referential" (palavras NOMEIAM objetos): as diagnósticas mostram a assinatura
      de NOME — muito mais ligadas a rótulo que a baseline do CORPUS (label_frac
      >= 2x corpus) E concentradas em fólios (mais que baseline), com uma fração
      material label-dominante (>=20% do pool com label_frac>0.5). Esta é a única
      via que afirma referência.
    - "prose_register" (vocabulário de texto corrido): as diagnósticas NÃO têm a
      assinatura de nome — label_frac NO/ABAIXO da baseline do corpus (não inflado),
      altamente espalhadas pelos fólios (entropia de fólio alta, ~baseline) e
      essencialmente NENHUMA label-dominante nem fólio-concentrada. Diferenças
      minúsculas em top_folio_share (ambos << 0.5) não são naming.
    - "mixed": qualquer caso intermediário/ambíguo (ex.: label_frac elevado mas sem
      concentração de fólio, ou vice-versa).

    O limiar de concentração de fólio é absoluto (top_folio_share > 0.5) e casa com
    n_diag_folio_concentrated; o de rótulo é label_frac > 0.5 (label-dominante).
    """
    if n_diag == 0:
        return "mixed"
    frac_label_dominant = n_diag_label_dominant / n_diag
    frac_folio_concentrated = n_diag_folio_concentrated / n_diag

    # --- Assinatura REFERENCIAL (nome de objeto desenhado) ---
    label_bound = (
        corpus_label_frac > 0
        and diag_label_frac >= 2.0 * corpus_label_frac
        and diag_label_frac > base_label_frac
    )
    folio_concentrated = (
        diag_folio_entropy < base_folio_entropy and diag_top_share > base_top_share
    )
    many_label_dominant = frac_label_dominant >= 0.20
    if label_bound and folio_concentrated and many_label_dominant:
        return "referential"

    # --- Assinatura de REGISTRO DE PROSA (vocabulário de texto corrido) ---
    # label_frac NÃO inflado acima da baseline do corpus (tolera ruído pequeno).
    not_label_inflated = diag_label_frac <= max(1.25 * corpus_label_frac, corpus_label_frac + 0.02)
    # altamente espalhada em termos ABSOLUTOS: entropia de fólio alta (perto da
    # baseline e perto de 1) e quase nada concentrado/label-dominante.
    highly_spread = (
        diag_folio_entropy >= base_folio_entropy - 0.05
        and diag_folio_entropy >= 0.75
        and frac_folio_concentrated < 0.10
    )
    almost_no_label_dominant = frac_label_dominant < 0.10
    if not_label_inflated and highly_spread and almost_no_label_dominant:
        return "prose_register"

    return "mixed"


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def build(
    records: list[tuple[str, str, str]], min_freq: int, top_n: int
) -> dict:
    """Constrói tudo: conjunto diagnóstico, métricas por palavra, comparações.

    `records` = [(folio, locus_kind, token)] de parse_corpus_with_kind. Tokens em
    fólios sem seção interpretável ('other') ficam de fora — igual à Rota 56 — tanto
    para a eleição do conjunto diagnóstico quanto para as métricas, de modo que o
    universo de palavras coincide com o da Rota 56.
    """
    # Pares (word, section) para a eleição do conjunto diagnóstico (Rota 56),
    # restritos a seção conhecida. Métricas por palavra usam os MESMOS records.
    records_known = [(f, k, t) for f, k, t in records if classify_section(f) != "other"]
    pairs = [(t, classify_section(f)) for f, _k, t in records_known]

    diag_words, word_section = diagnostic_set(pairs, MAJOR_SECTIONS, min_freq, top_n)
    metrics = word_grounding_metrics(records_known, min_freq)

    # Baseline de label_frac do CORPUS inteiro (todas as ocorrências de seção
    # conhecida, não apenas tipos freq>=min_freq): rótulo / total.
    n_label = sum(1 for _f, k, _t in records_known if k == "L")
    n_total = len(records_known)
    corpus_label_frac = (n_label / n_total) if n_total else 0.0

    diag_rows: list[dict] = []
    diag_lab, base_lab = [], []
    diag_ent, base_ent = [], []
    diag_top, base_top = [], []
    n_diag_label_dominant = 0
    n_diag_folio_concentrated = 0
    for word, m in metrics.items():
        is_diag = word in diag_words
        section = word_section.get(word, "") if is_diag else ""
        diag_rows.append(
            {
                "word": word,
                "section": section,
                "is_diagnostic": int(is_diag),
                "freq": m["freq"],
                "label_frac": round(m["label_frac"], 4),
                "para_frac": round(m["para_frac"], 4),
                "folio_entropy_norm": round(m["folio_entropy_norm"], 4),
                "top_folio_share": round(m["top_folio_share"], 4),
                "semantic_guardrail": GUARDRAIL,
            }
        )
        if is_diag:
            diag_lab.append(m["label_frac"])
            diag_ent.append(m["folio_entropy_norm"])
            diag_top.append(m["top_folio_share"])
            if m["label_frac"] > 0.5:
                n_diag_label_dominant += 1
            if m["top_folio_share"] > 0.5:
                n_diag_folio_concentrated += 1
        else:
            base_lab.append(m["label_frac"])
            base_ent.append(m["folio_entropy_norm"])
            base_top.append(m["top_folio_share"])

    diag_rows.sort(key=lambda r: (-r["is_diagnostic"], -r["freq"]))
    return {
        "diag_words": diag_words,
        "word_section": word_section,
        "metrics": metrics,
        "corpus_label_frac": corpus_label_frac,
        "diag_rows": diag_rows,
        "diag_lab": diag_lab,
        "base_lab": base_lab,
        "diag_ent": diag_ent,
        "base_ent": base_ent,
        "diag_top": diag_top,
        "base_top": base_top,
        "n_diag_label_dominant": n_diag_label_dominant,
        "n_diag_folio_concentrated": n_diag_folio_concentrated,
        "token_coverage": n_total,
    }


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("corpus", nargs="?", default=str(DEFAULT_CORPUS))
    p.add_argument("--n-perm", type=int, default=2000)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--min-freq", type=int, default=MIN_FREQ)
    p.add_argument("--top-per-section", type=int, default=TOP_PER_SECTION)
    d = ROOT / "data" / "derived"
    p.add_argument("--out-grounding", default=str(d / "word_grounding_zl3b.csv"))
    p.add_argument("--out-summary", default=str(d / "word_grounding_summary_zl3b.csv"))
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    records = parse_corpus_with_kind(Path(args.corpus))
    b = build(records, args.min_freq, args.top_per_section)

    # Médias + teste de permutação da diferença de médias de label_frac.
    diff_label, diag_mean_label, p_label = perm_test_mean_diff(
        b["diag_lab"], b["base_lab"], args.n_perm, args.seed
    )
    base_mean_label = (
        sum(b["base_lab"]) / len(b["base_lab"]) if b["base_lab"] else float("nan")
    )
    diag_mean_ent = sum(b["diag_ent"]) / len(b["diag_ent"]) if b["diag_ent"] else float("nan")
    base_mean_ent = sum(b["base_ent"]) / len(b["base_ent"]) if b["base_ent"] else float("nan")
    diag_mean_top = sum(b["diag_top"]) / len(b["diag_top"]) if b["diag_top"] else float("nan")
    base_mean_top = sum(b["base_top"]) / len(b["base_top"]) if b["base_top"] else float("nan")

    verdict = decide_verdict(
        b["corpus_label_frac"],
        diag_mean_label,
        base_mean_label,
        diag_mean_ent,
        base_mean_ent,
        diag_mean_top,
        base_mean_top,
        b["n_diag_label_dominant"],
        len(b["diag_lab"]),
        b["n_diag_folio_concentrated"],
    )

    write_csv(
        Path(args.out_grounding),
        b["diag_rows"],
        [
            "word",
            "section",
            "is_diagnostic",
            "freq",
            "label_frac",
            "para_frac",
            "folio_entropy_norm",
            "top_folio_share",
            "semantic_guardrail",
        ],
    )

    summary_rows = [
        {"metric": "corpus_label_frac", "value": str(round(b["corpus_label_frac"], 4))},
        {"metric": "diag_mean_label_frac", "value": str(round(diag_mean_label, 4))},
        {"metric": "base_mean_label_frac", "value": str(round(base_mean_label, 4))},
        {"metric": "diag_mean_folio_entropy", "value": str(round(diag_mean_ent, 4))},
        {"metric": "base_mean_folio_entropy", "value": str(round(base_mean_ent, 4))},
        {"metric": "diag_mean_top_folio_share", "value": str(round(diag_mean_top, 4))},
        {"metric": "base_mean_top_folio_share", "value": str(round(base_mean_top, 4))},
        {"metric": "n_diag_label_dominant", "value": str(b["n_diag_label_dominant"])},
        {"metric": "n_diag_folio_concentrated", "value": str(b["n_diag_folio_concentrated"])},
        {"metric": "perm_p_label_frac_diff", "value": str(round(p_label, 6))},
        {"metric": "verdict", "value": verdict},
        {"metric": "guardrail", "value": GUARDRAIL},
    ]
    # Métricas auxiliares (transparência; não exigidas mas úteis ao coordenador).
    aux = [
        {"metric": "n_diagnostic_words", "value": str(len(b["diag_lab"]))},
        {"metric": "n_baseline_words", "value": str(len(b["base_lab"]))},
        {"metric": "label_frac_ratio_diag_over_corpus",
         "value": str(round(diag_mean_label / b["corpus_label_frac"], 3))
         if b["corpus_label_frac"] > 0 else "nan"},
        {"metric": "token_coverage", "value": str(b["token_coverage"])},
    ]
    write_csv(
        Path(args.out_summary),
        summary_rows + aux,
        ["metric", "value"],
    )

    print(
        f"token_coverage={b['token_coverage']} n_diag={len(b['diag_lab'])} "
        f"n_base={len(b['base_lab'])}"
    )
    print(
        f"corpus_label_frac={b['corpus_label_frac']:.4f} | "
        f"label_frac diag={diag_mean_label:.4f} base={base_mean_label:.4f} "
        f"(diff={diff_label:+.4f}, perm_p={p_label:.4g})"
    )
    print(
        f"folio_entropy_norm diag={diag_mean_ent:.4f} base={base_mean_ent:.4f} | "
        f"top_folio_share diag={diag_mean_top:.4f} base={base_mean_top:.4f}"
    )
    print(
        f"n_diag_label_dominant={b['n_diag_label_dominant']} "
        f"n_diag_folio_concentrated={b['n_diag_folio_concentrated']}"
    )
    print(f"VERDICT={verdict}")
    print(f"grounding_csv={args.out_grounding}")
    print(f"summary_csv={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
