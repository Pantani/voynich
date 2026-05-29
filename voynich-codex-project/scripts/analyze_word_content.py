#!/usr/bin/env python3
"""Rota 56: o CONTEÚDO topical (seção) vive no nível da PALAVRA INTEIRA?

Pivot decisivo. As Rotas 43–55 dissecaram o TOKEN e mostraram que cada peça é
marcação funcional/lexical: qo-=registro, ok/ot=registro brando, vogal a/o=escriba
(Currier), consoante r/l=posição, e (Rota 55, par mínimo) o núcleo ch/sh é
LÉXICO FIXO — não conteúdo produtivo. Não há camada de conteúdo DENTRO do token.
Logo, se Voynichês tem conteúdo topical, ele tem de estar no nível da PALAVRA
INTEIRA (qual palavra = qual conceito). Esta rota testa isso.

Pergunta falsificável: a identidade da PALAVRA carrega conteúdo topical (seção)
ALÉM do que o escriba (Currier A/B) explica?

Controle crítico (lição recorrente do projeto): seção é correlacionada com Currier
(A≈herbal; B≈balneológico/recipes/pharma). Uma palavra pode parecer
"diagnóstica de seção" sendo na verdade "vocabulário de escriba/dialeto" (como foi
a vogal a/o). Portanto separamos conteúdo topical de dialeto restringindo a
Currier B (multi-seção dentro de UMA mão). E: a informação mútua com muitos
valores-de-palavra é POSITIVAMENTE ENVIESADA em amostras finitas (isso nos mordeu
na Rota 55 — o MI observado ficou no piso de viés do embaralhamento). Por isso
calibramos TUDO contra um nulo de permutação; o sinal é observado_MI − nulo_médio,
a significância é o p empírico.

Métricas (bits):
  1. I(seção ; palavra) sobre ocorrências de token. Nulo de permutação: embaralha
     os rótulos de seção entre ocorrências, recomputa; reporta observado, média e
     desvio do nulo, p empírico, e I_norm = max(0, obs−nulo_médio)/H(seção).
  2. Controle decisivo: restringe a Currier B (multi-seção numa só mão) com seu
     PRÓPRIO nulo. Se palavra→seção SOBREVIVE em B (obs ≫ nulo), o conteúdo topical
     é real e não só dialeto. Também computa em A para contraste.
  3. Vocabulário diagnóstico: para tipos com freq ≥ 20, lift(palavra,seção)=
     P(seção|palavra)/P(seção). Top palavras por lift por seção principal.
  4. Marcador vs não-marcador: diagnosticidade média de palavras qo-/ok-/ot- vs
     outras. A teoria funcional prevê que marcadores são MAIS PLANOS.

CONTROLES PRÉ-REGISTRADOS (cryptanalyst). O veredito `topical_vocabulary` não
pode ser confiado até dois confundidores serem tratados:

  CONTROLE 1 — TIPO DE LOCUS (rótulo vs prosa). Seções diferem na composição
    rótulo/prosa (herbal/astronômico são ricos em rótulo; recipes é prosa). Tokens
    de rótulo têm distribuições distintas, então I(seção;palavra) pode inflar por
    MISTURA de tipo-de-locus, não por tópico. CORREÇÃO: restringe a tokens de
    PROSA (locus_kind == 'P' via parse_corpus_with_kind) e recomputa I_norm
    agrupado E dentro-de-B com seus nulos de permutação.

  CONTROLE 2 — PERMUTAÇÃO POR BLOCO-DE-FÓLIO (autocorrelação / LAAFU). O nulo de
    token embaralha rótulos de seção no nível do TOKEN, quebrando a repetição de
    palavra dentro do fólio e deixando o nulo APERTADO DEMAIS (p otimista). Seção é
    função determinística do fólio. CORREÇÃO: nulo de BLOCO-DE-FÓLIO — embaralha a
    LISTA de rótulos-de-seção ENTRE FÓLIOS (cada fólio mantém seu saco inteiro de
    tokens; só troca qual rótulo de seção recai sobre ele). Preserva a estrutura de
    repetição intra-fólio; é o nulo CONSERVADOR. Aplicado a dentro-de-B (e agrupado).

NÃO é tradução: mede onde (se em algum lugar) a estrutura de conteúdo reside.
"""
from __future__ import annotations

import argparse
import collections
import csv
import math
import random
from pathlib import Path

# Reusa o parser canônico (Rota 53). parse_corpus(path) -> (folio->currier,
# [(folio, clean_token)]); classify_section(folio) -> string da seção.
from scripts.analyze_nucleus import classify_section, parse_corpus

# Reusa o parser que conhece o TIPO de locus (Rota 54). parse_corpus_with_kind ->
# [(folio, locus_kind, clean_token)] na MESMA ordem/tokenização de parse_corpus
# (verificado: sequência idêntica de (folio, token)); locus_kind[0] = P/L/C/R.
# Usado para o CONTROLE 1 (restrição a prosa, kind == 'P').
from scripts.analyze_nucleus_context import parse_corpus_with_kind

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota56_word_content_not_decipherment"
DEFAULT_CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"

# Seções "principais" para o relatório de vocabulário diagnóstico (Métrica 3).
MAJOR_SECTIONS = ["herbal", "balneological", "recipes", "pharmaceutical", "astronomical"]
# Prefixos de marcador funcional (Métrica 4).
MARKER_PREFIXES = ("qo", "ok", "ot")
MIN_FREQ = 20  # tipos de palavra "frequentes" para lift/diagnosticidade


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


def mutual_information(pairs: list[tuple[str, str]]) -> float:
    """I(seção ; palavra) em bits, sobre ocorrências (palavra, seção).

    I = H(seção) − H(seção | palavra). Igual a sum p(x,y) log2 p(x,y)/(p(x)p(y)).
    Computado como H(seção) − H(seção|palavra) por estabilidade e clareza.
    """
    if not pairs:
        return 0.0
    sec_counts: collections.Counter = collections.Counter()
    word_sec: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for word, sec in pairs:
        sec_counts[sec] += 1
        word_sec[word][sec] += 1
    n = len(pairs)
    h_sec = entropy(sec_counts.values())
    # H(seção | palavra) = sum_w p(w) * H(seção | palavra=w)
    h_cond = 0.0
    for word, secs in word_sec.items():
        nw = sum(secs.values())
        h_cond += (nw / n) * entropy(secs.values())
    return max(0.0, h_sec - h_cond)


def permutation_null(
    pairs: list[tuple[str, str]], n_perm: int, seed: int
) -> tuple[float, float, float, float]:
    """Nulo de permutação para I(seção ; palavra).

    Embaralha os rótulos de SEÇÃO entre as ocorrências (mantém as palavras e as
    frequências marginais de seção fixas), recomputa I a cada vez. Em amostras
    finitas com muitos tipos de palavra, I é positivamente enviesado, então o
    nulo NÃO é zero — é o piso de viés que o sinal real precisa superar.

    Retorna (observado, nulo_médio, nulo_desvio, p_empírico).
    p = fração de embaralhamentos com I >= observado (estimativa conservadora
    com +1 no numerador e denominador).
    """
    observed = mutual_information(pairs)
    if n_perm <= 0 or not pairs:
        return observed, float("nan"), float("nan"), float("nan")
    rng = random.Random(seed)
    words = [w for w, _ in pairs]
    secs = [s for _, s in pairs]
    null_vals: list[float] = []
    hits = 0
    for _ in range(n_perm):
        rng.shuffle(secs)
        mi = mutual_information(list(zip(words, secs)))
        null_vals.append(mi)
        if mi >= observed:
            hits += 1
    mean = sum(null_vals) / len(null_vals)
    var = sum((v - mean) ** 2 for v in null_vals) / len(null_vals)
    std = math.sqrt(var)
    p = (hits + 1) / (n_perm + 1)
    return observed, mean, std, p


def folio_block_null(
    triples: list[tuple[str, str, str]], n_perm: int, seed: int
) -> tuple[float, float, float, float]:
    """Nulo de BLOCO-DE-FÓLIO para I(seção ; palavra) — CONTROLE 2 (LAAFU).

    `triples` é [(folio, word, section), ...]. Seção é função determinística do
    fólio, então cada fólio carrega UM rótulo de seção e um SACO inteiro de
    palavras. O nulo de token (permutation_null) embaralha seção no nível do
    token, o que destrói a repetição de palavra dentro do fólio (autocorrelação /
    LAAFU) e produz um nulo apertado demais (p otimista).

    Este nulo, em vez disso, mantém cada fólio INTACTO (seu saco de palavras) e
    apenas PERMUTA a lista de rótulos-de-seção ENTRE os fólios. Como vários fólios
    compartilham a mesma seção, embaralhar a lista de rótulos preserva exatamente
    quantos FÓLIOS caem em cada seção (a marginal de seção por-fólio é fixa),
    enquanto reatribui o rótulo de cada fólio. A marginal de seção por-TOKEN pode
    variar levemente (fólios têm tamanhos diferentes), refletindo o tamanho-de-
    bloco real — é exatamente esse ruído de bloco que torna o nulo conservador.

    Retorna (observado, nulo_médio, nulo_desvio, p_empírico) com a mesma convenção
    de permutation_null (p = (hits+1)/(n_perm+1), hits = nulo >= observado).
    """
    # Saco de palavras por fólio (preserva repetição intra-fólio) e o rótulo de
    # seção real de cada fólio.
    folio_words: dict[str, list[str]] = collections.defaultdict(list)
    folio_section: dict[str, str] = {}
    for folio, word, sec in triples:
        folio_words[folio].append(word)
        folio_section[folio] = sec  # determinístico; última escrita == qualquer

    folios = list(folio_words.keys())
    observed = mutual_information([(w, folio_section[f]) for f in folios for w in folio_words[f]])
    if n_perm <= 0 or not folios:
        return observed, float("nan"), float("nan"), float("nan")

    labels = [folio_section[f] for f in folios]
    rng = random.Random(seed)
    null_vals: list[float] = []
    hits = 0
    for _ in range(n_perm):
        rng.shuffle(labels)
        # Reatribui o rótulo embaralhado a cada fólio; o saco de palavras do fólio
        # vai inteiro com o novo rótulo (bloco intacto).
        pairs = [
            (w, labels[i])
            for i, f in enumerate(folios)
            for w in folio_words[f]
        ]
        mi = mutual_information(pairs)
        null_vals.append(mi)
        if mi >= observed:
            hits += 1
    mean = sum(null_vals) / len(null_vals)
    var = sum((v - mean) ** 2 for v in null_vals) / len(null_vals)
    std = math.sqrt(var)
    p = (hits + 1) / (n_perm + 1)
    return observed, mean, std, p


def i_norm(observed: float, null_mean: float, h_sec: float) -> float:
    """Fração corrigida-por-viés da incerteza de seção explicada pela palavra.

    max(0, observado − nulo_médio) / H(seção). 0 = nada além do viés; 1 = palavra
    determina seção perfeitamente.
    """
    if not (h_sec > 0) or math.isnan(null_mean):
        return 0.0
    return max(0.0, observed - null_mean) / h_sec


def build_records(
    folio_currier: dict[str, str], tokens: list[tuple[str, str]]
) -> dict:
    """Constrói as estruturas centrais a partir do corpus.

    Retorna:
      pairs_all   : [(word, section)] para TODAS as ocorrências (seção conhecida)
      pairs_B     : [(word, section)] restrito a Currier B
      pairs_A     : [(word, section)] restrito a Currier A
      word_cur    : word -> Counter({'A':, 'B':, '?':}) (para currier_skew)
    """
    pairs_all: list[tuple[str, str]] = []
    pairs_B: list[tuple[str, str]] = []
    pairs_A: list[tuple[str, str]] = []
    word_cur: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for folio, tok in tokens:
        sec = classify_section(folio)
        if sec == "other":
            # sem seção interpretável (fólios fora das faixas) — fora do teste
            continue
        cur = folio_currier.get(folio, "?")
        pairs_all.append((tok, sec))
        word_cur[tok][cur] += 1
        if cur == "B":
            pairs_B.append((tok, sec))
        elif cur == "A":
            pairs_A.append((tok, sec))
    return {
        "pairs_all": pairs_all,
        "pairs_B": pairs_B,
        "pairs_A": pairs_A,
        "word_cur": word_cur,
    }


def build_records_with_kind(
    folio_currier: dict[str, str], records: list[tuple[str, str, str]]
) -> dict:
    """Como build_records, mas a partir de (folio, locus_kind, token) e carregando
    o FÓLIO e o KIND para os dois controles pré-registrados.

    `records` vem de parse_corpus_with_kind (mesma tokenização de parse_corpus).
    Retorna, além das estruturas de build_records sobre TODAS as ocorrências:
      pairs_P       : [(word, section)] só PROSA (kind == 'P')          (Controle 1)
      pairs_BP      : [(word, section)] Currier B E prosa               (Controle 1)
      triples_all   : [(folio, word, section)] todas as ocorrências     (Controle 2)
      triples_B     : [(folio, word, section)] Currier B
      triples_P     : [(folio, word, section)] só prosa
      triples_BP    : [(folio, word, section)] Currier B E prosa  (mais ESTRITO)
    A seção 'other' (fólios fora das faixas) fica fora de tudo, como em build_records.
    """
    pairs_all: list[tuple[str, str]] = []
    pairs_B: list[tuple[str, str]] = []
    pairs_A: list[tuple[str, str]] = []
    pairs_P: list[tuple[str, str]] = []
    pairs_BP: list[tuple[str, str]] = []
    triples_all: list[tuple[str, str, str]] = []
    triples_B: list[tuple[str, str, str]] = []
    triples_P: list[tuple[str, str, str]] = []
    triples_BP: list[tuple[str, str, str]] = []
    word_cur: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for folio, kind, tok in records:
        sec = classify_section(folio)
        if sec == "other":
            continue
        cur = folio_currier.get(folio, "?")
        is_P = kind == "P"
        pairs_all.append((tok, sec))
        triples_all.append((folio, tok, sec))
        word_cur[tok][cur] += 1
        if cur == "B":
            pairs_B.append((tok, sec))
            triples_B.append((folio, tok, sec))
        elif cur == "A":
            pairs_A.append((tok, sec))
        if is_P:
            pairs_P.append((tok, sec))
            triples_P.append((folio, tok, sec))
            if cur == "B":
                pairs_BP.append((tok, sec))
                triples_BP.append((folio, tok, sec))
    return {
        "pairs_all": pairs_all,
        "pairs_B": pairs_B,
        "pairs_A": pairs_A,
        "pairs_P": pairs_P,
        "pairs_BP": pairs_BP,
        "triples_all": triples_all,
        "triples_B": triples_B,
        "triples_P": triples_P,
        "triples_BP": triples_BP,
        "word_cur": word_cur,
    }


def diagnostic_rows(
    pairs: list[tuple[str, str]],
    word_cur: dict[str, collections.Counter],
    min_freq: int,
    guardrail: str,
) -> list[dict]:
    """Linhas por tipo de palavra (freq>=min_freq) com lift e diagnosticidade.

    Usa word_cur (palavra->Counter de Currier) para currier_skew.
    """
    sec_counts: collections.Counter = collections.Counter()
    word_sec: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for word, sec in pairs:
        sec_counts[sec] += 1
        word_sec[word][sec] += 1
    n = len(pairs)
    p_sec = {s: c / n for s, c in sec_counts.items()}
    h_sec = entropy(sec_counts.values())
    rows: list[dict] = []
    for word, secs in word_sec.items():
        freq = sum(secs.values())
        if freq < min_freq:
            continue
        lifts = {s: (cnt / freq) / p_sec[s] for s, cnt in secs.items()}
        top_section = max(lifts, key=lifts.get)
        lift_top = lifts[top_section]
        sec_ent_norm = entropy(secs.values()) / h_sec if h_sec > 0 else 0.0
        cur = word_cur.get(word, collections.Counter())
        ab = cur.get("A", 0) + cur.get("B", 0)
        skew = abs(cur.get("B", 0) - cur.get("A", 0)) / ab if ab else 0.0
        rows.append(
            {
                "word": word,
                "freq": freq,
                "top_section": top_section,
                "lift_top": round(lift_top, 3),
                "section_entropy_norm": round(sec_ent_norm, 4),
                "currier_skew": round(skew, 3),
                "semantic_guardrail": guardrail,
            }
        )
    rows.sort(key=lambda r: -r["freq"])
    return rows


def top_lift_by_section(
    diag_rows: list[dict],
    pairs: list[tuple[str, str]],
    sections: list[str],
    top_n: int = 10,
) -> dict[str, list[tuple[str, int, float]]]:
    """Top-N palavras por lift para cada seção (lift recomputado por seção-alvo).

    Para a seção S: lift_S(palavra) = P(S|palavra)/P(S). Ordena palavras
    freq>=MIN_FREQ por lift_S decrescente. Retorna {S: [(word, freq, lift_S)]}.
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
            if freq[w] < MIN_FREQ:
                continue
            lift_S = (secs.get(S, 0) / freq[w]) / pS
            scored.append((w, freq[w], round(lift_S, 3)))
        scored.sort(key=lambda x: (-x[2], -x[1]))
        out[S] = scored[:top_n]
    return out


def flattest_words(
    diag_rows: list[dict], top_n: int = 10
) -> list[tuple[str, int, float]]:
    """Palavras de alta freq mais PLANAS por seção (candidatas a função).

    section_entropy_norm próximo de 1 = distribuição de seção quase uniforme.
    Retorna as top_n com maior entropia normalizada (desempate por freq).
    """
    ranked = sorted(diag_rows, key=lambda r: (-r["section_entropy_norm"], -r["freq"]))
    return [(r["word"], r["freq"], r["section_entropy_norm"]) for r in ranked[:top_n]]


def marker_vs_nonmarker(diag_rows: list[dict]) -> tuple[float, float, int, int]:
    """Diagnosticidade média (1 − section_entropy_norm) de marcadores vs resto.

    Marcador = palavra que começa com qo-/ok-/ot-. Diagnosticidade alta = palavra
    concentrada numa seção. A teoria funcional prevê marcadores MAIS PLANOS, i.e.
    diagnosticidade MENOR que não-marcadores.

    Retorna (média_marcador, média_nao_marcador, n_marcador, n_nao_marcador).
    """
    mk, nm = [], []
    for r in diag_rows:
        diag = 1.0 - r["section_entropy_norm"]
        if r["word"].startswith(MARKER_PREFIXES):
            mk.append(diag)
        else:
            nm.append(diag)
    mk_mean = sum(mk) / len(mk) if mk else float("nan")
    nm_mean = sum(nm) / len(nm) if nm else float("nan")
    return mk_mean, nm_mean, len(mk), len(nm)


def decide_verdict(
    i_obs: float, i_null_mean: float, i_p: float, inorm_B: float, b_p: float
) -> str:
    """Codifica o veredito conforme o protocolo da rota.

    - obs ≫ nulo (p pequeno) E sobrevive em B (inorm_B materialmente > 0,
      p_B pequeno) -> "topical_vocabulary"
    - colapsa sob o controle B (inorm_B ~ 0) -> "scribe_vocabulary"
    - I ~ nulo mesmo agrupado -> "no_topical_signal"
    """
    pooled_real = (not math.isnan(i_p)) and i_p < 0.05 and i_obs > i_null_mean
    b_real = (not math.isnan(b_p)) and b_p < 0.05 and inorm_B > 0.01
    if not pooled_real:
        return "no_topical_signal"
    if b_real:
        return "topical_vocabulary"
    return "scribe_vocabulary"


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("corpus", nargs="?", default=str(DEFAULT_CORPUS))
    p.add_argument("--n-perm", type=int, default=300)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--min-freq", type=int, default=MIN_FREQ)
    p.add_argument(
        "--out-diagnostic",
        default=str(ROOT / "data" / "derived" / "word_section_diagnostic_zl3b.csv"),
    )
    p.add_argument(
        "--out-summary",
        default=str(ROOT / "data" / "derived" / "word_section_summary_zl3b.csv"),
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    folio_currier, tokens = parse_corpus(Path(args.corpus))
    rec = build_records(folio_currier, tokens)
    pairs_all = rec["pairs_all"]
    pairs_B = rec["pairs_B"]
    pairs_A = rec["pairs_A"]
    word_cur = rec["word_cur"]

    h_sec = entropy(collections.Counter(s for _, s in pairs_all).values())

    # Métrica 1: I(seção;palavra) agrupado + nulo de permutação
    i_obs, i_null_mean, i_null_std, i_p = permutation_null(
        pairs_all, args.n_perm, args.seed
    )
    i_norm_all = i_norm(i_obs, i_null_mean, h_sec)

    # Métrica 2: controle decisivo dentro de Currier B (e contraste em A)
    h_sec_B = entropy(collections.Counter(s for _, s in pairs_B).values())
    b_obs, b_null_mean, b_null_std, b_p = permutation_null(
        pairs_B, args.n_perm, args.seed + 1
    )
    i_norm_B = i_norm(b_obs, b_null_mean, h_sec_B)

    h_sec_A = entropy(collections.Counter(s for _, s in pairs_A).values())
    a_obs, a_null_mean, _a_std, _a_p = permutation_null(
        pairs_A, args.n_perm, args.seed + 2
    )
    i_norm_A = i_norm(a_obs, a_null_mean, h_sec_A)

    # Métrica 3: vocabulário diagnóstico (freq >= min_freq)
    diag_rows = diagnostic_rows(pairs_all, word_cur, args.min_freq, GUARDRAIL)

    # Métrica 4: marcador vs não-marcador
    mk_mean, nm_mean, n_mk, n_nm = marker_vs_nonmarker(diag_rows)

    verdict = decide_verdict(i_obs, i_null_mean, i_p, i_norm_B, b_p)

    # ====================================================================
    # CONTROLES PRÉ-REGISTRADOS (cryptanalyst) — não removem nada acima.
    # Reparse com KIND para isolar prosa (Controle 1) e blocos de fólio
    # (Controle 2). A sequência (folio, token) é idêntica à de parse_corpus.
    # ====================================================================
    records_kind = parse_corpus_with_kind(Path(args.corpus))
    rk = build_records_with_kind(folio_currier, records_kind)
    pairs_P = rk["pairs_P"]      # só prosa (kind == P)
    pairs_BP = rk["pairs_BP"]    # Currier B E prosa

    # CONTROLE 1 — agrupado, só prosa (token-perm).
    h_sec_P = entropy(collections.Counter(s for _, s in pairs_P).values())
    p_obs, p_null_mean, _p_std, p_p = permutation_null(
        pairs_P, args.n_perm, args.seed + 3
    )
    i_norm_P = i_norm(p_obs, p_null_mean, h_sec_P)

    # CONTROLE 1 — dentro de B, só prosa (token-perm).
    h_sec_BP = entropy(collections.Counter(s for _, s in pairs_BP).values())
    bp_obs, bp_null_mean, _bp_std, bp_p = permutation_null(
        pairs_BP, args.n_perm, args.seed + 4
    )
    i_norm_BP = i_norm(bp_obs, bp_null_mean, h_sec_BP)

    # CONTROLE 2 — dentro de B, nulo de BLOCO-DE-FÓLIO (todos os kinds).
    fb_obs, fb_null_mean, _fb_std, fb_p = folio_block_null(
        rk["triples_B"], args.n_perm, args.seed + 5
    )

    # ESTRITÍSSIMO — dentro de B + prosa + nulo de bloco-de-fólio.
    fbp_obs, fbp_null_mean, _fbp_std, fbp_p = folio_block_null(
        rk["triples_BP"], args.n_perm, args.seed + 6
    )
    i_norm_BP_fb = i_norm(fbp_obs, fbp_null_mean, h_sec_BP)

    # Veredito controlado: usa os números dentro-de-B MAIS ESTRITOS
    # (prosa para o sinal pooled; prosa + bloco-de-fólio para a sobrevivência B).
    verdict_controlled = decide_verdict(
        p_obs, p_null_mean, p_p, i_norm_BP_fb, fbp_p
    )

    # ---- escreve CSV diagnóstico ----
    write_csv(
        Path(args.out_diagnostic),
        diag_rows,
        [
            "word",
            "freq",
            "top_section",
            "lift_top",
            "section_entropy_norm",
            "currier_skew",
            "semantic_guardrail",
        ],
    )

    # ---- escreve CSV de resumo ----
    summary_rows = [
        {"metric": "H_section_bits", "value": str(round(h_sec, 4))},
        {"metric": "I_section_word_obs", "value": str(round(i_obs, 4))},
        {"metric": "I_null_mean", "value": str(round(i_null_mean, 4))},
        {"metric": "I_null_std", "value": str(round(i_null_std, 4))},
        {"metric": "I_perm_p", "value": str(round(i_p, 6))},
        {"metric": "I_norm", "value": str(round(i_norm_all, 4))},
        {"metric": "I_within_B_obs", "value": str(round(b_obs, 4))},
        {"metric": "I_within_B_null_mean", "value": str(round(b_null_mean, 4))},
        {"metric": "I_within_B_perm_p", "value": str(round(b_p, 6))},
        {"metric": "I_within_B_norm", "value": str(round(i_norm_B, 4))},
        {"metric": "I_within_A_norm", "value": str(round(i_norm_A, 4))},
        {"metric": "marker_mean_diag", "value": str(round(mk_mean, 4))},
        {"metric": "nonmarker_mean_diag", "value": str(round(nm_mean, 4))},
        {"metric": "n_marker_types", "value": str(n_mk)},
        {"metric": "n_nonmarker_types", "value": str(n_nm)},
        {"metric": "n_types_freq20", "value": str(len(diag_rows))},
        {"metric": "token_coverage", "value": str(len(pairs_all))},
        {"metric": "verdict", "value": verdict},
        # ---- CONTROLE 1: restrição a prosa (kind == P) ----
        {"metric": "I_paragraph_only_norm", "value": str(round(i_norm_P, 4))},
        {"metric": "I_paragraph_only_p", "value": str(round(p_p, 6))},
        {"metric": "I_within_B_paragraph_norm", "value": str(round(i_norm_BP, 4))},
        {"metric": "I_within_B_paragraph_p", "value": str(round(bp_p, 6))},
        # ---- CONTROLE 2: nulo de bloco-de-fólio (dentro de B) ----
        {"metric": "I_within_B_folioblock_p", "value": str(round(fb_p, 6))},
        # ---- ESTRITÍSSIMO: dentro de B + prosa + bloco-de-fólio ----
        {"metric": "I_within_B_paragraph_folioblock_p", "value": str(round(fbp_p, 6))},
        {"metric": "I_within_B_paragraph_folioblock_norm", "value": str(round(i_norm_BP_fb, 4))},
        {"metric": "verdict_controlled", "value": verdict_controlled},
        # token coverage dos subconjuntos controlados (transparência)
        {"metric": "token_coverage_paragraph", "value": str(len(pairs_P))},
        {"metric": "token_coverage_within_B_paragraph", "value": str(len(pairs_BP))},
        {"metric": "semantic_guardrail", "value": GUARDRAIL},
    ]
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    # ---- log para o coordenador ----
    top_lift = top_lift_by_section(diag_rows, pairs_all, MAJOR_SECTIONS)
    flat = flattest_words(diag_rows)
    # Top-lift recomputado SÓ NA PROSA (Controle 1) para checar se o vocabulário
    # diagnóstico de herbal/balneológico muda quando rótulos são removidos.
    diag_rows_P = diagnostic_rows(pairs_P, rk["word_cur"], args.min_freq, GUARDRAIL)
    top_lift_P = top_lift_by_section(diag_rows_P, pairs_P, MAJOR_SECTIONS)
    print(
        f"H_section={h_sec:.4f} I_obs={i_obs:.4f} I_null_mean={i_null_mean:.4f} "
        f"I_null_std={i_null_std:.4f} I_p={i_p:.4g} I_norm={i_norm_all:.4f}"
    )
    print(
        f"within_B: obs={b_obs:.4f} null_mean={b_null_mean:.4f} p={b_p:.4g} "
        f"I_norm_B={i_norm_B:.4f} | within_A I_norm_A={i_norm_A:.4f}"
    )
    print(
        f"marker_mean_diag={mk_mean:.4f} (n={n_mk}) "
        f"nonmarker_mean_diag={nm_mean:.4f} (n={n_nm})"
    )
    print(f"n_types_freq{args.min_freq}={len(diag_rows)} token_coverage={len(pairs_all)}")
    print(f"VERDICT={verdict}")
    # --- bloco dos CONTROLES pré-registrados ---
    print(
        f"[CTRL1 paragraph-only pooled] obs={p_obs:.4f} null={p_null_mean:.4f} "
        f"p={p_p:.4g} I_norm_P={i_norm_P:.4f} (cov={len(pairs_P)})"
    )
    print(
        f"[CTRL1 within-B paragraph token-perm] obs={bp_obs:.4f} null={bp_null_mean:.4f} "
        f"p={bp_p:.4g} I_norm_BP={i_norm_BP:.4f} (cov={len(pairs_BP)})"
    )
    print(
        f"[CTRL2 within-B folio-block] obs={fb_obs:.4f} null={fb_null_mean:.4f} p={fb_p:.4g}"
    )
    print(
        f"[STRICTEST within-B paragraph + folio-block] obs={fbp_obs:.4f} "
        f"null={fbp_null_mean:.4f} p={fbp_p:.4g} I_norm={i_norm_BP_fb:.4f}"
    )
    print(f"VERDICT_CONTROLLED={verdict_controlled}")
    for S in ("herbal", "balneological"):
        tops = ", ".join(f"{w}(f{fr},L{lf})" for w, fr, lf in top_lift.get(S, [])[:5])
        topsP = ", ".join(f"{w}(f{fr},L{lf})" for w, fr, lf in top_lift_P.get(S, [])[:5])
        print(f"top_lift[{S}] ALL: {tops}")
        print(f"top_lift[{S}] PARAGRAPH-ONLY: {topsP}")
    print("flattest(function-candidates): " + ", ".join(f"{w}(f{fr},Hn{hn})" for w, fr, hn in flat[:5]))
    print(f"diagnostic_csv={args.out_diagnostic}")
    print(f"summary_csv={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
