# Rota 65: radial≠parágrafo confirma R50 + refino fortalece desacoplamento (visual front CLOSED)

Guardrails: `rota65a_radial_paragraph_not_decipherment`, `rota65b_cross_modal_refined_not_decipherment`.

Duas pernas em paralelo via harness — uma frente visual NOVA (texto radial vs parágrafo) e
um refino do cross-modal R64. Pré-registro cego do cryptanalyst para AMBAS antes de
qualquer número.

## Perna A — radial/circular ≠ parágrafo (com controle dentro-do-fólio)

**Pergunta:** o texto em ANEL/RADIAL/CIRCULAR (cosmológico, f67–70 e rosetas f85–86) difere
estatisticamente do parágrafo? A IVTFF já classifica via `locus_kind` (P/R/C/L); usei isso
direto no corpus (não precisa de imagem nova). Baixei f68r/f68v/f69r/f85v_86r para
grounding qualitativo (`images/raw/yale_iiif_r65/`) mas o teste é corpus-wide.

**Distribuição de prefixo (a virada decisiva):**

| classe | n | qo- | ok- | ot- | yk- | yt- |
|--------|---|-----|-----|-----|-----|-----|
| paragraph | 34 259 | **15.1%** | 5.8% | 5.2% | 1.4% | 1.2% |
| radial    |  2 383 | 2.3% | 10.7% | **16.0%** | 2.4% | 1.1% |
| label     |  1 029 | 0.9% | 16.7% | **17.2%** | 3.2% | 2.5% |

- **`qo-` colapsa fora do parágrafo** (15% → 2% → 1%) — é um marcador de PROSA.
- **`ot-` triplica** em radial e label (5% → 16% → 17%).
- **Nucleus ch/sh é mais raro** em label (22%) que em parágrafo (40%).

**Headline (within-folio universe, 10 fólios cosmológicos com AMBAS as classes; 2000 perms):**

| feature | V_global | V_within_folio | p_within_folio |
|---------|----------|----------------|----------------|
| **prefix** | 0.148 | **0.217** | **0.0005** |
| **nucleus** | 0.045 | **0.134** | **0.0005** |
| length_bucket | 0.036 | 0.033 | 0.62 (null) |

**Sobrevive** ao controle dentro-do-fólio — NÃO é artefato de vocabulário de seção/Currier.
Per-fólio: prefix p<0.05 em **6/10** fólios; nucleus p<0.05 em **6/10**. Comprimento é nulo.

**f67r2 (a R50 em escala de corpus):** label-vs-paragraph V=**0.26, p_within=0.027** —
o padrão "ot- nos rótulos da lua" da Rota 50 reproduz-se sob teste rigoroso.

**Veredito Perna A: `radial_paragraph_differ`.** O `locus_kind` (já no IVTFF) atua como
**seletor de registro** sobre o MESMO inventário de operadores. Não é uma camada NOVA — é
a casca externa do modelo em camadas operando como esperado: layout licencia distribuição
de prefixo/núcleo. Firma R47/R50.

## Perna B — refinar incertos e re-rodar cross-modal (R64 → refined)

**Refino (visual-annotator, com armadilha de viés-de-confirmação pré-registrada):**
- 38 uncertain→medium; 15 medium→high; 0 uncertain→high (honesto: nenhum incerto chegou a
  "inequívoco" no segundo olhar).
- **Uncertain caiu de 59% → 37%** (n_não-incerto 70 → 108).
- **Sem mudanças de `object_type`** — tipologia original aguentou.
- **Bias check:** elevados mean length 6.50 vs mantidos-uncertain 6.76; medianas idênticas
  (6.0); diversidade lexical similar — **sem preferência por tokens "típicos"**. Passa.
- Limites estruturais irredutíveis documentados: ninfas-em-anel zodíaco (34 linhas),
  rótulos-chevron f67r2 (6), painel f89v2 não disponível, rótulos multi-token.

**Re-teste com nulo dentro-do-fólio (3000 perms, ambos subconjuntos):**

| teste | refined | R64 | delta |
|-------|---------|-----|-------|
| gallows × classe (all rows, p_within) | **0.0560** | 0.0536 | +0.002 (afasta de 0.05) |
| gallows × classe (não-incerto, p_within) | 0.0150 | 0.2506 | -0.236 (mas não casa em all-rows) |
| pharma vessel-vs-organ (length, p_within) | **0.0073** | 0.0063 | +0.001 (sobrevive <0.01) |
| nymph cross-folio divergence (f71r vs f73r) | **0.0130** | 0.0113 | +0.002 (essencialmente igual) |

**Veredito Perna B: `decoupled_refined`.** A regra dos DOIS subconjuntos (a mesma que pegou
o lzma_artifact da R61) bloqueia o "signal" do gallows em não-incerto-só: all-rows não
corrobora. O efeito real de jarro-vs-órgão (comprimento) HOLDS robusto. Ninfas seguem
fólio-locais (não endurece, não afrouxa). **Refino fortaleceu o desacoplamento**, exatamente
como o cryptanalyst pré-registrou (~55%).

## Síntese — visual front CLOSED

> A pergunta visual cross-modal — *"os rótulos nomeiam os objetos?"* — está respondida
> **com potência (n=171) E com dados refinados (n=108 não-incerto): NÃO.** A pergunta
> visual estrutural — *"o texto radial difere do parágrafo?"* — está respondida: **SIM,
> mas como REGISTRO (locus_kind ↔ prefixo), não como semântica.** A R50 reproduziu-se em
> escala de corpus sob controle dentro-do-fólio.

**Implicações para o veredito do projeto (R43–62 + visual):** firma "morfologicamente rico,
sintaticamente fino, escriba/gerador" com mais uma camada de confirmação — o `locus_kind`
seleciona o registro de prefixo no mesmo inventário gerador; o texto não descreve as imagens
em nenhum nível testado. Priores efetivamente inalterados (gerador ~70% / construída ~22% /
cifra ~8%).

**Frente visual: encerrada** (cryptanalyst meta: "if Leg B (a) lands → declare visual front
CLOSED" — Leg B (a) `decoupled_refined` aterrissou). Avanço da pergunta "tem sentido?" exige
proveniência/material, não mais estatística sobre corpus/imagem.

Suíte: **549 testes** (535 após Perna A + 14 da Perna B Round 2).

Saídas Perna A: `scripts/analyze_radial_paragraph.py`, `tests/test_radial_paragraph.py`,
`data/derived/radial_paragraph_{distribution,test,summary}_zl3b.csv`,
`images/raw/yale_iiif_r65/` (4 fólios cosmológicos de grounding).

Saídas Perna B: `data/derived/rota65b_cross_modal_refined_zl3b.csv` (171 linhas refinadas),
`data/derived/cross_modal_{test,summary}_refined_zl3b.csv`; extensões em
`scripts/analyze_cross_modal.py` / `tests/test_cross_modal.py`.

Guardrails: `rota65a_radial_paragraph_not_decipherment`, `rota65b_cross_modal_refined_not_decipherment`.
