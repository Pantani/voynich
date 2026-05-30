#!/usr/bin/env python3
"""Rota 63 (frente visual): a ESTRUTURA do token-rótulo corresponde ao TIPO
VISUAL do objeto que ele rotula?

Entrada: data/derived/rota63_cross_modal_labels_zl3b.csv — codificação cross-modal
do visual-annotator (folio, object_type, label_token, annotation_confidence, ...),
59 linhas, ~46% annotation_confidence=uncertain. É um PILOTO subdimensionado.

PERGUNTA FALSIFIÁVEL
  (A) sim -> primeiro elo cross-modal texto<->imagem / rótulo-como-nome.
  (B) não -> rótulos também desacoplados, estendendo o desacoplamento de R57.

O CONFUNDIDOR CRÍTICO (exigência pré-registrada do cryptanalyst)
  object_type é largamente DETERMINADO PELO FÓLIO (fólios pharma=raízes/folhas/
  recipientes, astro=estrelas/roundéis), e pharma vs astro diferem em AMBOS o
  inventário de objetos E o vocabulário de rótulos. Logo um V GLOBAL
  (feature × coarse_class) sobretudo re-mede o vocabulário de fólio/seção — um
  sinal espúrio. Qualquer sinal cross-modal real DEVE sobreviver a um
  EMBARALHAMENTO DE RÓTULOS DENTRO DO FÓLIO (análogo ao controle de Currier no
  arco textual).

DESENHO
  - coarse_class: organ={leaf,root,stem,flower,spray}, whole_plant,
    vessel={container}, sky={star,figure_roundel}. (commitado ANTES de testar
    p/ evitar inflação de df.)
  - features do token (limpo p/ letras EVA puras): first_glyph; prefix4 ∈
    {qo,ok,ot,yk,yt,o-other,other}; gallows_present (k/t/p/f); gallows_class
    (gallows líder k/t/p/f/none); length_bucket (short<=4/mid5-6/long>=7);
    nucleus (ch/sh/none); vowel_present (a/o).
  - p/ cada feature F: V(F × coarse_class) + DOIS p de permutação (>=2000, seed):
      p_global       = embaralha coarse_class entre TODOS os elementos.
      p_within_folio = embaralha coarse_class só DENTRO de cada fólio (decisivo).
  - contraste limpo controlado por fólio: dentro dos fólios PHARMA (f88v,f99r,
    f99v) só, vessel (container) vs organ — rótulos de recipiente diferem
    estruturalmente dos de parte-de-planta NO MESMO fólio?
  - robustez: re-roda os testes-cabeça no subconjunto NÃO-uncertain.

VEREDITO
  - "cross_modal_correspondence" SÓ SE alguma feature tem p_within_folio < 0.05
    E se mantém no subconjunto non-uncertain.
  - "decoupled_pilot" se nenhuma feature bate o nulo within-folio (consistente
    com R57; mas PILOTO/subdimensionado — declarar).

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

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota63_cross_modal_not_decipherment"
DEFAULT_INPUT = ROOT / "data" / "derived" / "rota63_cross_modal_labels_zl3b.csv"
N_PERM = 2000
SEED = 63

# Fólios farmacêuticos (recipientes + partes de planta no MESMO fólio).
PHARMA_FOLIOS = ("f88v", "f99r", "f99v")
# f89r2 está na lista de fólios-pharma do desenho mas não tem linhas nos dados.

# --- mapeamento grosso commitado ANTES de testar (evita inflação de df) ---
COARSE_MAP = {
    "leaf": "organ",
    "root": "organ",
    "stem": "organ",
    "flower": "organ",
    "spray": "organ",
    "whole_plant": "whole_plant",
    "container": "vessel",
    "star": "sky",
    "figure_roundel": "sky",
}

# ==========================================================================
# Rota 64 — MODO COMBINADO (amplia o piloto R63: ~3x a amostra)
# ==========================================================================
# Concatena AMBAS as anotações cross-modal (rota63 n=59 + rota64 n=112 = 171),
# 12 fólios, com nymph agora GRANDE (zodíaco f71r/f73r). Re-roda o MESMO teste
# controlado-dentro-do-fólio com mais potência: o veredito de desacoplamento
# de R63 (rótulos desacoplados do tipo de objeto, sob embaralhamento within-folio)
# se MANTÉM, ou emerge um sinal que o piloto não tinha potência p/ ver?
GUARDRAIL_COMBINED = "rota64_cross_modal_not_decipherment"
SEED_COMBINED = 64
N_PERM_COMBINED = 3000  # >=3000 shuffles (mais potência que o piloto R63).

COMBINED_INPUTS = (
    ROOT / "data" / "derived" / "rota63_cross_modal_labels_zl3b.csv",
    ROOT / "data" / "derived" / "rota64_cross_modal_labels_zl3b.csv",
)

# Mapeamento grosso COMBINADO, commitado ANTES de testar. Diferenças vs R63:
#   - nymph (agora GRANDE: 44 rótulos de zodíaco) e figure_roundel -> 'figure'.
#   - star + ring_segment -> 'sky' (ring_segment não está nos dados atuais mas
#     fica no mapa para robustez de schema).
# 'other' (1 rótulo, f88r.17 folhagem ambígua) NÃO está no mapa -> coarse 'other'
# e é excluído dos testes de classe (só figura na contagem n).
COARSE_MAP_COMBINED = {
    "leaf": "organ",
    "root": "organ",
    "stem": "organ",
    "flower": "organ",
    "spray": "organ",
    "whole_plant": "whole_plant",
    "container": "vessel",
    "nymph": "figure",
    "figure_roundel": "figure",
    "star": "sky",
    "ring_segment": "sky",
}

# Fólios PHARMA com recipiente + parte-de-planta NO MESMO fólio (teste de
# tipo-de-objeto mais limpo, controlado por fólio). Determinado pelos dados:
# f100r/f100v só têm organ/whole_plant (sem recipiente) -> não contribuem p/
# o contraste vessel-vs-organ within-folio e ficam de fora deste sub-teste.
PHARMA_FOLIOS_COMBINED = ("f88r", "f88v", "f89v1", "f89v2", "f99r", "f99v")

# Os 2 fólios de zodíaco que carregam os ~44 rótulos de nymph quase-tipo-constante.
NYMPH_FOLIOS = ("f71r", "f73r")

GALLOWS = set("ktpf")
NUCLEI = ("ch", "sh")
VOWELS = set("ao")
# letras EVA centrais (limpeza descarta pontuação, dígitos, separadores).
_EVA_KEEP = re.compile(r"[a-z]")


def coarse_class(object_type: str) -> str:
    """object_type -> classe grossa (organ/whole_plant/vessel/sky)."""
    return COARSE_MAP.get((object_type or "").strip().lower(), "other")


def clean_token(token: str) -> str:
    """Reduz o rótulo a letras EVA minúsculas puras.

    Os rótulos podem trazer locus embutido com ponto ('okar.y', 'otar.arody'),
    maiúsculas ou ruído; mantemos só [a-z]. 'okar.y' -> 'okary'.
    """
    return "".join(_EVA_KEEP.findall((token or "").lower()))


def first_glyph(tok: str) -> str:
    return tok[0] if tok else "none"


def prefix4(tok: str) -> str:
    """Bucket de prefixo do operador: qo/ok/ot/yk/yt/o-other/other."""
    if not tok:
        return "other"
    p2 = tok[:2]
    if p2 in ("qo", "ok", "ot", "yk", "yt"):
        return p2
    if tok[0] == "o":
        return "o-other"
    return "other"


def gallows_present(tok: str) -> str:
    """'yes' se qualquer gallows (k/t/p/f) aparece no token, senão 'no'."""
    return "yes" if any(c in GALLOWS for c in tok) else "no"


def gallows_class(tok: str) -> str:
    """Primeira gallows do token (k/t/p/f) ou 'none'."""
    for c in tok:
        if c in GALLOWS:
            return c
    return "none"


def length_bucket(tok: str) -> str:
    n = len(tok)
    if n <= 4:
        return "short"
    if n <= 6:
        return "mid"
    return "long"


def nucleus(tok: str) -> str:
    """Banco ch/sh presente (primeiro encontrado) ou 'none'."""
    for nuc in NUCLEI:
        if nuc in tok:
            return nuc
    return "none"


def vowel_present(tok: str) -> str:
    return "yes" if any(c in VOWELS for c in tok) else "no"


# nome -> extrator de feature (ordem = ordem de relato).
FEATURES: dict[str, "callable"] = {
    "first_glyph": first_glyph,
    "prefix4": prefix4,
    "gallows_present": gallows_present,
    "gallows_class": gallows_class,
    "length_bucket": length_bucket,
    "nucleus": nucleus,
    "vowel_present": vowel_present,
}


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def coarse_class_combined(object_type: str) -> str:
    """object_type -> classe grossa do MODO COMBINADO (R64).

    Inclui figure={nymph,figure_roundel} e sky={star,ring_segment}; 'other'
    desconhecido vira 'other' (excluído dos testes de classe).
    """
    return COARSE_MAP_COMBINED.get((object_type or "").strip().lower(), "other")


def build_elements(
    rows: list[dict[str, str]], coarse_fn=coarse_class
) -> list[dict[str, str]]:
    """Cada elemento: folio, coarse, object_type, confidence, tok + features.

    ``coarse_fn`` mapeia object_type -> classe grossa. Default = ``coarse_class``
    (mapa R63). Para o modo combinado R64 passe ``coarse_class_combined``.
    """
    elements: list[dict[str, str]] = []
    for r in rows:
        tok = clean_token(r.get("label_token", ""))
        if not tok:
            continue
        coarse = coarse_fn(r.get("object_type", ""))
        el = {
            "folio": (r.get("folio", "") or "").strip(),
            "object_type": (r.get("object_type", "") or "").strip().lower(),
            "coarse": coarse,
            "confidence": (r.get("annotation_confidence", "") or "").strip().lower(),
            "token": tok,
        }
        for name, fn in FEATURES.items():
            el[name] = fn(tok)
        elements.append(el)
    return elements


def load_combined(paths=COMBINED_INPUTS) -> list[dict[str, str]]:
    """Concatena as linhas brutas das anotações cross-modal R63 + R64.

    Mesmo schema de 8 colunas nas duas; concatena na ordem dada (R63 depois R64).
    """
    rows: list[dict[str, str]] = []
    for p in paths:
        rows.extend(read_csv(Path(p)))
    return rows


def cramer_v(table: dict[str, collections.Counter]) -> tuple[float, int]:
    """Cramer's V de uma tabela de contingência {linha: Counter(coluna->n)}.

    Mesma forma do scripts/analyze_section_scribe.py. Retorna (V, N). N<4 -> 0.
    """
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


def _table(feat_vals: list[str], class_vals: list[str]) -> dict[str, collections.Counter]:
    """Constrói tabela feature(linha) × classe(coluna) de listas pareadas."""
    table: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for fv, cv in zip(feat_vals, class_vals):
        table[fv][cv] += 1
    return table


def observed_v(elements: list[dict[str, str]], feature: str) -> tuple[float, int]:
    feat_vals = [el[feature] for el in elements]
    class_vals = [el["coarse"] for el in elements]
    return cramer_v(_table(feat_vals, class_vals))


def _global_shuffle(class_vals: list[str], rng: random.Random) -> list[str]:
    """Embaralha as classes entre TODOS os elementos."""
    shuffled = class_vals[:]
    rng.shuffle(shuffled)
    return shuffled


def _within_folio_shuffle(
    class_vals: list[str], folios: list[str], rng: random.Random
) -> list[str]:
    """Embaralha as classes SÓ dentro de cada fólio.

    Preserva a contagem por-fólio de cada classe (controle decisivo): cada fólio
    mantém exatamente seu próprio multiconjunto de classes, só as associações
    rótulo<->classe são reembaralhadas internamente.
    """
    idx_by_folio: dict[str, list[int]] = collections.defaultdict(list)
    for i, fo in enumerate(folios):
        idx_by_folio[fo].append(i)
    out = class_vals[:]
    for idxs in idx_by_folio.values():
        vals = [class_vals[i] for i in idxs]
        rng.shuffle(vals)
        for i, v in zip(idxs, vals):
            out[i] = v
    return out


def permutation_pvalues(
    elements: list[dict[str, str]], feature: str, n_perm: int, seed: int
) -> tuple[float, float, float, int]:
    """Retorna (V_obs, p_global, p_within_folio, N).

    p = (#perms com V >= V_obs + 1) / (n_perm + 1) — convenção +1 (nunca 0).
    Cada controle usa seu próprio RNG seedado de forma determinística.
    """
    feat_vals = [el[feature] for el in elements]
    folios = [el["folio"] for el in elements]
    v_obs, n = cramer_v(_table(feat_vals, [el["coarse"] for el in elements]))
    class_vals = [el["coarse"] for el in elements]

    rng_g = random.Random(seed)
    ge_global = 0
    for _ in range(n_perm):
        perm = _global_shuffle(class_vals, rng_g)
        v, _ = cramer_v(_table(feat_vals, perm))
        if v >= v_obs - 1e-12:
            ge_global += 1

    rng_w = random.Random(seed + 1)
    ge_within = 0
    for _ in range(n_perm):
        perm = _within_folio_shuffle(class_vals, folios, rng_w)
        v, _ = cramer_v(_table(feat_vals, perm))
        if v >= v_obs - 1e-12:
            ge_within += 1

    p_global = (ge_global + 1) / (n_perm + 1)
    p_within = (ge_within + 1) / (n_perm + 1)
    return v_obs, p_global, p_within, n


def run_feature_tests(
    elements: list[dict[str, str]],
    subset_label: str,
    n_perm: int,
    seed: int,
    guardrail: str = GUARDRAIL,
) -> list[dict]:
    """Roda todas as features sobre um conjunto de elementos; lista de dict-linha."""
    out: list[dict] = []
    for fi, feature in enumerate(FEATURES):
        v, p_g, p_w, n = permutation_pvalues(elements, feature, n_perm, seed + 7 * fi)
        out.append(
            {
                "feature": feature,
                "n": n,
                "cramer_v": round(v, 4),
                "p_global": round(p_g, 4),
                "p_within_folio": round(p_w, 4),
                "subset": subset_label,
                "semantic_guardrail": guardrail,
            }
        )
    return out


def pharma_vessel_vs_organ(
    elements: list[dict[str, str]], n_perm: int, seed: int
) -> dict:
    """Contraste limpo controlado por fólio dentro dos fólios PHARMA.

    Subconjunto: elementos em PHARMA_FOLIOS com coarse ∈ {vessel, organ}. Para
    cada feature, V(feature × {vessel|organ}) + p de permutação within-folio.
    Reporta a MELHOR feature (maior V). p within-folio é o controle honesto:
    embaralha vessel/organ só dentro de cada fólio pharma.
    """
    sub = [
        el
        for el in elements
        if el["folio"] in PHARMA_FOLIOS and el["coarse"] in ("vessel", "organ")
    ]
    n = len(sub)
    if n < 4 or len({el["coarse"] for el in sub}) < 2:
        return {
            "n": n,
            "best_feature": "n/a",
            "cramer_v": 0.0,
            "p_within_folio": 1.0,
            "n_vessel": sum(1 for el in sub if el["coarse"] == "vessel"),
            "n_organ": sum(1 for el in sub if el["coarse"] == "organ"),
        }
    best = None
    for fi, feature in enumerate(FEATURES):
        v, _p_g, p_w, _n = permutation_pvalues(sub, feature, n_perm, seed + 100 + fi)
        cand = (v, feature, p_w)
        if best is None or v > best[0]:
            best = cand
    v, feature, p_w = best
    return {
        "n": n,
        "best_feature": feature,
        "cramer_v": round(v, 4),
        "p_within_folio": round(p_w, 4),
        "n_vessel": sum(1 for el in sub if el["coarse"] == "vessel"),
        "n_organ": sum(1 for el in sub if el["coarse"] == "organ"),
    }


def pharma_object_type_test(
    elements: list[dict[str, str]],
    pharma_folios: tuple[str, ...],
    n_perm: int,
    seed: int,
) -> dict:
    """SUB-TESTE A (R64) — variância de TIPO-DE-OBJETO nos fólios PHARMA.

    Idêntico a ``pharma_vessel_vs_organ`` mas com o conjunto de fólios pharma
    PARAMETRIZADO (combinado: 6 fólios com recipiente+parte-de-planta no mesmo
    fólio). Restringe a vessel|organ, e p_within_folio embaralha vessel/organ só
    DENTRO de cada fólio pharma — o teste de tipo-de-objeto mais limpo possível.
    Reporta a MELHOR feature (maior V) e seu p_within_folio.
    """
    sub = [
        el
        for el in elements
        if el["folio"] in pharma_folios and el["coarse"] in ("vessel", "organ")
    ]
    n = len(sub)
    n_vessel = sum(1 for el in sub if el["coarse"] == "vessel")
    n_organ = sum(1 for el in sub if el["coarse"] == "organ")
    if n < 4 or len({el["coarse"] for el in sub}) < 2:
        return {
            "n": n,
            "best_feature": "n/a",
            "cramer_v": 0.0,
            "p_within_folio": 1.0,
            "n_vessel": n_vessel,
            "n_organ": n_organ,
            "n_folios": len({el["folio"] for el in sub}),
        }
    best = None
    for fi, feature in enumerate(FEATURES):
        v, _p_g, p_w, _n = permutation_pvalues(sub, feature, n_perm, seed + 100 + fi)
        if best is None or v > best[0]:
            best = (v, feature, p_w)
    v, feature, p_w = best
    return {
        "n": n,
        "best_feature": feature,
        "cramer_v": round(v, 4),
        "p_within_folio": round(p_w, 4),
        "n_vessel": n_vessel,
        "n_organ": n_organ,
        "n_folios": len({el["folio"] for el in sub}),
    }


def _feature_profile(elements: list[dict[str, str]], feature: str) -> dict[str, float]:
    """Distribuição normalizada dos valores de uma feature (soma=1, ou vazio)."""
    cnt = collections.Counter(el[feature] for el in elements)
    tot = sum(cnt.values())
    if tot == 0:
        return {}
    return {k: v / tot for k, v in cnt.items()}


def _tv_distance(p: dict[str, float], q: dict[str, float]) -> float:
    """Distância de variação total entre dois perfis: 0.5 * sum|p-q| ∈ [0,1]."""
    keys = set(p) | set(q)
    return 0.5 * sum(abs(p.get(k, 0.0) - q.get(k, 0.0)) for k in keys)


def nymph_profile_divergence(
    nymph_els: list[dict[str, str]], folio_a: str, folio_b: str
) -> tuple[float, list[float]]:
    """Divergência de perfil entre nymphs de folio_a vs folio_b, por feature.

    Retorna (média das TV-distances entre os perfis dos dois fólios, lista por
    feature). Um NOME-DE-OBJETO real daria perfis SEMELHANTES nos dois fólios
    (divergência baixa); vocabulário folio-local daria perfis diferentes (alta).
    """
    a = [el for el in nymph_els if el["folio"] == folio_a]
    b = [el for el in nymph_els if el["folio"] == folio_b]
    dists = []
    for feature in FEATURES:
        dists.append(_tv_distance(_feature_profile(a, feature), _feature_profile(b, feature)))
    mean = sum(dists) / len(dists) if dists else 0.0
    return mean, dists


def nymph_consistency(
    elements: list[dict[str, str]],
    nymph_folios: tuple[str, ...],
    n_perm: int,
    seed: int,
) -> dict:
    """SUB-TESTE B (R64) — os NYMPHS recebem nomes CONSISTENTES entre fólios?

    Duas perguntas:
      (1) ESTRUTURA: rótulos de nymph são estruturalmente mais parecidos ENTRE SI
          do que com não-nymphs? -> V(is_nymph × feature) p/ cada feature; reporta
          a MAIOR V e um p de permutação (embaralha o rótulo is_nymph entre TODOS
          os elementos; sinal real = is_nymph prediz a feature acima do acaso).
      (2) CONSISTÊNCIA CROSS-FÓLIO: o perfil de feature dos nymphs em f71r e f73r
          é o MESMO? Distância de variação total média OBSERVADA entre os perfis
          dos dois fólios vs um nulo que embaralha o rótulo de fólio (f71r/f73r)
          entre os elementos de nymph. Teste UNILATERAL de EXCESSO de divergência:
              p_divergent = fração de perms com divergência >= observada.
          p_divergent PEQUENO (<0.05) -> os perfis são MAIS divergentes que o
          acaso -> vocabulário FÓLIO-LOCAL (um nome-de-objeto real daria perfis
          SEMELHANTES, divergência dentro do acaso). p_divergent ALTO (>=0.05) ->
          divergência compatível com o acaso -> perfis CONSISTENTES.

    Veredito 'consistent' SÓ SE: (1) is_nymph estrutura uma feature acima do
    acaso (struct_p<0.05) E (2) os perfis cross-fólio NÃO são mais divergentes
    que o acaso (p_divergent>=0.05) E há nymphs nos 2 fólios. Caso contrário
    'folio_local' (estruturado mas com vocabulário local) ou 'unstructured'.
    """
    nymph_els = [el for el in elements if el["object_type"] == "nymph"]
    n_nymph = len(nymph_els)
    folios_present = sorted({el["folio"] for el in nymph_els} & set(nymph_folios))

    # (1) estrutura: is_nymph × feature sobre TODOS os elementos.
    is_nymph = ["nymph" if el["object_type"] == "nymph" else "non_nymph" for el in elements]
    best_struct = None
    rng_s = random.Random(seed + 500)
    for _fi, feature in enumerate(FEATURES):
        feat_vals = [el[feature] for el in elements]
        v_obs, _n = cramer_v(_table(feat_vals, is_nymph))
        ge = 0
        for _ in range(n_perm):
            perm = is_nymph[:]
            rng_s.shuffle(perm)
            v, _ = cramer_v(_table(feat_vals, perm))
            if v >= v_obs - 1e-12:
                ge += 1
        p = (ge + 1) / (n_perm + 1)
        if best_struct is None or v_obs > best_struct[0]:
            best_struct = (v_obs, feature, p)
    struct_v, struct_feature, struct_p = best_struct if best_struct else (0.0, "n/a", 1.0)
    structured = struct_p < 0.05

    # (2) consistência cross-fólio dos perfis de nymph entre os 2 fólios.
    if len(folios_present) < 2:
        return {
            "n_nymph": n_nymph,
            "n_folios": len(folios_present),
            "struct_feature": struct_feature,
            "struct_v": round(struct_v, 4),
            "struct_p": round(struct_p, 4),
            "profile_divergence": float("nan"),
            "p_divergent": float("nan"),
            "result": "insufficient_folios",
        }
    fa, fb = folios_present[0], folios_present[1]
    obs_div, _per_feat = nymph_profile_divergence(nymph_els, fa, fb)
    folios = [el["folio"] for el in nymph_els]
    rng_c = random.Random(seed + 900)
    ge_div = 0  # perms com divergência >= observada (teste de EXCESSO)
    for _ in range(n_perm):
        perm_folios = folios[:]
        rng_c.shuffle(perm_folios)
        shuffled = [dict(el, folio=pf) for el, pf in zip(nymph_els, perm_folios)]
        div, _ = nymph_profile_divergence(shuffled, fa, fb)
        if div >= obs_div - 1e-12:
            ge_div += 1
    p_divergent = (ge_div + 1) / (n_perm + 1)

    consistent_profiles = p_divergent >= 0.05  # obs NÃO mais divergente que acaso
    if structured and consistent_profiles:
        result = "consistent"
    elif structured:
        result = "folio_local"  # estruturado, mas vocabulário difere entre fólios
    else:
        result = "unstructured"
    return {
        "n_nymph": n_nymph,
        "n_folios": len(folios_present),
        "struct_feature": struct_feature,
        "struct_v": round(struct_v, 4),
        "struct_p": round(struct_p, 4),
        "profile_divergence": round(obs_div, 4),
        "p_divergent": round(p_divergent, 4),
        "result": result,
    }


def decide_verdict_combined(
    all_rows: list[dict], nonunc_rows: list[dict], nymph: dict
) -> tuple[str, str, float]:
    """Veredito do MODO COMBINADO (R64) + melhor feature headline + seu p_within.

    cross_modal_correspondence SE:
      (a) alguma feature tem p_within_folio<0.05 em TODAS as linhas E a MESMA
          feature <0.05 no subconjunto non-uncertain (headline), OU
      (b) os perfis cross-fólio de nymph são CONSISTENTES E estruturados acima do
          acaso (nymph['result']=='consistent').
    Senão 'decoupled' (agora melhor-potenciado que o piloto R63).
    """
    best_row = min(all_rows, key=lambda r: r["p_within_folio"]) if all_rows else None
    best_feature = best_row["feature"] if best_row else "n/a"
    best_p = best_row["p_within_folio"] if best_row else 1.0

    nonunc_p = {r["feature"]: r["p_within_folio"] for r in nonunc_rows}
    headline = any(
        r["p_within_folio"] < 0.05 and nonunc_p.get(r["feature"], 1.0) < 0.05
        for r in all_rows
    )
    nymph_signal = nymph.get("result") == "consistent"
    verdict = "cross_modal_correspondence" if (headline or nymph_signal) else "decoupled"
    return verdict, best_feature, best_p


def decide_verdict(all_rows: list[dict], nonunc_rows: list[dict]) -> tuple[str, str, float]:
    """Veredito + nome da melhor feature + seu p_within_folio (todas as linhas).

    cross_modal_correspondence SÓ SE alguma feature tem p_within_folio<0.05 em
    TODAS as linhas E essa mesma feature também <0.05 no subconjunto non-uncertain.
    Senão decoupled_pilot (subdimensionado).
    """
    best_row = min(all_rows, key=lambda r: r["p_within_folio"]) if all_rows else None
    best_feature = best_row["feature"] if best_row else "n/a"
    best_p = best_row["p_within_folio"] if best_row else 1.0

    nonunc_p = {r["feature"]: r["p_within_folio"] for r in nonunc_rows}
    survives = [
        r["feature"]
        for r in all_rows
        if r["p_within_folio"] < 0.05 and nonunc_p.get(r["feature"], 1.0) < 0.05
    ]
    verdict = "cross_modal_correspondence" if survives else "decoupled_pilot"
    return verdict, best_feature, best_p


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input_csv", nargs="?", default=str(DEFAULT_INPUT))
    p.add_argument(
        "--out-test",
        default=str(ROOT / "data" / "derived" / "cross_modal_test_zl3b.csv"),
    )
    p.add_argument(
        "--out-summary",
        default=str(ROOT / "data" / "derived" / "cross_modal_summary_zl3b.csv"),
    )
    p.add_argument("--n-perm", type=int, default=N_PERM)
    p.add_argument("--seed", type=int, default=SEED)
    # ---- modo combinado R64 (amplia o piloto R63 p/ n=171) ----
    p.add_argument(
        "--combined",
        action="store_true",
        help="MODO COMBINADO R64: concatena rota63+rota64 (n=171); ignora input_csv.",
    )
    p.add_argument(
        "--out-test-combined",
        default=str(ROOT / "data" / "derived" / "cross_modal_test_combined_zl3b.csv"),
    )
    p.add_argument(
        "--out-summary-combined",
        default=str(ROOT / "data" / "derived" / "cross_modal_summary_combined_zl3b.csv"),
    )
    return p.parse_args(argv)


def run_combined(
    out_test: str,
    out_summary: str,
    n_perm: int,
    seed: int,
    inputs=COMBINED_INPUTS,
) -> dict:
    """MODO COMBINADO R64: re-roda o teste cross-modal de R63 em n=171.

    Concatena as anotações R63+R64, mapeia coarse com o mapa combinado (inclui
    classe 'figure'), roda o teste headline (feature × coarse_class, p_global +
    p_within_folio) sobre TODAS as linhas E o subconjunto non-uncertain, o
    SUB-TESTE A (pharma vessel-vs-organ within-folio nos 6 fólios pharma) e o
    SUB-TESTE B (consistência cross-fólio dos nomes de nymph). Escreve os 2 CSVs
    e devolve um dict com os números-chave (também usado pelos testes).
    """
    rows = load_combined(inputs)
    elements = build_elements(rows, coarse_fn=coarse_class_combined)
    nonunc = [el for el in elements if el["confidence"] != "uncertain"]

    n_total = len(elements)
    n_nonunc = len(nonunc)
    n_folios = len({el["folio"] for el in elements})

    all_rows = run_feature_tests(elements, "all", n_perm, seed, GUARDRAIL_COMBINED)
    nonunc_rows = run_feature_tests(
        nonunc, "non_uncertain", n_perm, seed, GUARDRAIL_COMBINED
    )
    test_rows = all_rows + nonunc_rows

    pharma = pharma_object_type_test(elements, PHARMA_FOLIOS_COMBINED, n_perm, seed)
    nymph = nymph_consistency(elements, NYMPH_FOLIOS, n_perm, seed)
    verdict, best_feature, best_p = decide_verdict_combined(all_rows, nonunc_rows, nymph)

    summary_rows = [
        {"metric": "n_total", "value": str(n_total)},
        {"metric": "n_non_uncertain", "value": str(n_nonunc)},
        {"metric": "n_folios", "value": str(n_folios)},
        {"metric": "best_feature", "value": best_feature},
        {"metric": "best_p_within_folio", "value": f"{best_p:.4f}"},
        {"metric": "pharma_test_n", "value": str(pharma["n"])},
        {"metric": "pharma_test_best_feature", "value": pharma["best_feature"]},
        {"metric": "pharma_test_V", "value": f"{pharma['cramer_v']:.4f}"},
        {"metric": "pharma_test_p_within_folio", "value": f"{pharma['p_within_folio']:.4f}"},
        {"metric": "pharma_test_result", "value": (
            "object_type_signal"
            if pharma["p_within_folio"] < 0.05
            else "no_object_type_signal"
        )},
        {"metric": "nymph_n", "value": str(nymph["n_nymph"])},
        {"metric": "nymph_struct_feature", "value": nymph["struct_feature"]},
        {"metric": "nymph_struct_V", "value": f"{nymph['struct_v']:.4f}"},
        {"metric": "nymph_struct_p", "value": f"{nymph['struct_p']:.4f}"},
        {"metric": "nymph_profile_divergence", "value": f"{nymph['profile_divergence']:.4f}"},
        {"metric": "nymph_p_divergent", "value": f"{nymph['p_divergent']:.4f}"},
        {"metric": "nymph_consistency_result", "value": nymph["result"]},
        {"metric": "verdict", "value": verdict},
        {"metric": "semantic_guardrail", "value": GUARDRAIL_COMBINED},
    ]

    write_csv(
        Path(out_test),
        test_rows,
        ["feature", "n", "cramer_v", "p_global", "p_within_folio", "subset", "semantic_guardrail"],
    )
    write_csv(Path(out_summary), summary_rows, ["metric", "value"])

    print(
        f"[combined] n_total={n_total} n_non_uncertain={n_nonunc} n_folios={n_folios} "
        f"best_feature={best_feature} best_p_within_folio={best_p:.4f}"
    )
    print(
        f"[combined] pharma n={pharma['n']} (vessel={pharma['n_vessel']} "
        f"organ={pharma['n_organ']}) best={pharma['best_feature']} "
        f"V={pharma['cramer_v']:.4f} p_within={pharma['p_within_folio']:.4f}"
    )
    print(
        f"[combined] nymph n={nymph['n_nymph']} struct={nymph['struct_feature']} "
        f"V={nymph['struct_v']:.4f} p={nymph['struct_p']:.4f} "
        f"profile_div={nymph['profile_divergence']:.4f} "
        f"p_divergent={nymph['p_divergent']:.4f} -> {nymph['result']}"
    )
    print(f"[combined] verdict={verdict}")
    print(f"test_csv={out_test}")
    print(f"summary_csv={out_summary}")
    return {
        "n_total": n_total,
        "n_non_uncertain": n_nonunc,
        "n_folios": n_folios,
        "all_rows": all_rows,
        "nonunc_rows": nonunc_rows,
        "pharma": pharma,
        "nymph": nymph,
        "verdict": verdict,
        "best_feature": best_feature,
        "best_p_within_folio": best_p,
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if args.combined:
        run_combined(
            args.out_test_combined,
            args.out_summary_combined,
            args.n_perm if args.n_perm != N_PERM else N_PERM_COMBINED,
            args.seed if args.seed != SEED else SEED_COMBINED,
        )
        return 0
    rows = read_csv(Path(args.input_csv))
    elements = build_elements(rows)
    nonunc = [el for el in elements if el["confidence"] != "uncertain"]

    n_total = len(elements)
    n_nonunc = len(nonunc)

    all_rows = run_feature_tests(elements, "all", args.n_perm, args.seed)
    nonunc_rows = run_feature_tests(nonunc, "non_uncertain", args.n_perm, args.seed)
    test_rows = all_rows + nonunc_rows

    pharma = pharma_vessel_vs_organ(elements, args.n_perm, args.seed)
    verdict, best_feature, best_p = decide_verdict(all_rows, nonunc_rows)

    summary_rows = [
        {"metric": "n_total", "value": str(n_total)},
        {"metric": "n_non_uncertain", "value": str(n_nonunc)},
        {"metric": "best_feature", "value": best_feature},
        {"metric": "best_p_within_folio", "value": f"{best_p:.4f}"},
        {"metric": "pharma_vessel_vs_organ_best_feature", "value": pharma["best_feature"]},
        {"metric": "pharma_vessel_vs_organ_n", "value": str(pharma["n"])},
        {"metric": "pharma_vessel_vs_organ_V", "value": f"{pharma['cramer_v']:.4f}"},
        {
            "metric": "pharma_vessel_vs_organ_p_within_folio",
            "value": f"{pharma['p_within_folio']:.4f}",
        },
        {"metric": "verdict", "value": verdict},
        {"metric": "semantic_guardrail", "value": GUARDRAIL},
    ]

    write_csv(
        Path(args.out_test),
        test_rows,
        ["feature", "n", "cramer_v", "p_global", "p_within_folio", "subset", "semantic_guardrail"],
    )
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    print(
        f"n_total={n_total} n_non_uncertain={n_nonunc} "
        f"best_feature={best_feature} best_p_within_folio={best_p:.4f} "
        f"pharma_V={pharma['cramer_v']:.4f} pharma_p_within={pharma['p_within_folio']:.4f} "
        f"verdict={verdict}"
    )
    print(f"test_csv={args.out_test}")
    print(f"summary_csv={args.out_summary}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
