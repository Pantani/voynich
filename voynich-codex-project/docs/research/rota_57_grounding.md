# Rota 57: a topicalidade da palavra é PROSA, não nome de objeto — texto e imagem desacoplados

Guardrail: `rota57_word_grounding_not_decipherment`.

A Rota 56 achou um sinal topical fraco na PALAVRA (sobrevive a Currier+prosa+bloco-de-fólio,
I_norm=0.046), vivendo em loci de PROSA. A Rota 57 decide o que esse sinal É: as palavras
diagnósticas **nomeiam objetos desenhados** (referencial) ou são só **vocabulário de prosa**
que varia por tópico (registro)? Três legs independentes do harness — e convergem.

## Pré-registro cego (cryptanalyst) × resultado

Prior cego do cryptanalyst: PROSE_REGISTER 0.72, MIXED 0.20, REFERENTIAL 0.08. Já declarou
REFERENTIAL "clinicamente morto" porque a R56 mostrou que o controle de locus-tipo não
mexeu no sinal. A surpresa possível: alta concentração por fólio + baixo label_frac = "prosa
sobre o que a página mostra". **Não materializou** — ver top_folio_share abaixo.

## Leg 1 — estatística reproduzível (corpus inteiro, 37 671 tokens)

Para 75 palavras diagnósticas (top-15 por lift de 5 seções) vs 205 baseline (freq≥20):

| métrica | corpus | diagnóstica | baseline |
|---------|--------|-------------|----------|
| label_frac (fração em rótulos) | 0.0273 | **0.0264** | 0.0146 |
| folio_entropy_norm (espalhamento) | — | **0.956** | 0.962 |
| top_folio_share (concentração) | — | **0.122** | 0.086 |

- **label_frac diagnóstico (2.6%) ≈ baseline do corpus (2.7%)** — NÃO elevado (razão 0.97×).
- **n diagnósticas dominadas-por-rótulo (label_frac>0.5) = 0**; **concentradas-em-fólio
  (top_folio_share>0.5) = 0**. A mais "rotuladora" é `otaly` (0.43) — e ainda espalhada
  (top_folio_share 0.095). Todas vivem em prosa, em muitos fólios.
- Ressalva honesta: as diagnósticas são marginalmente MAIS rotuladoras que as palavras
  ultra-comuns de função (perm p=0.026), mas em termos absolutos 97% não-rótulo. Referencial
  fraco é tecnicamente vivo, clinicamente quase-morto.

**Veredito: `prose_register`.** As palavras diagnósticas de seção são vocabulário de prosa
corrida, **não nomes de objetos depictados**.

## Leg 2 — verificação cross-modal nas imagens IIIF (visual-annotator)

| Fólio | Seção | Desenhado | Layout |
|-------|-------|-----------|--------|
| f1r | herbal | 1 planta | **100% prosa** (24 P, 0 rótulos) |
| f84r | balneológico | ninfas/poças | ~52% prosa; "rótulos" são legendas de cena, não nomes de 1 token |
| f67r2 | astronômico | rodas de estrelas | rótulos radiais marcam CÉLULAS do diagrama |
| f67v1 | astro/cosmo | medalhões + sol | quase só legendas radiais |
| f99r | farmacêutico | jarros + partes de planta | **84% rótulo** — caso mais claro de rótulo-em-objeto |

**Síntese visual:** onde o sinal da R56 vive (loci de prosa de herbal/balneológico), o layout
é dominado por PROSA (f1r = 100% prosa). Rótulo-de-um-token-em-objeto existe em farmacêutico
e astronômico — seções que NÃO são onde o sinal topical está. Das palavras diagnósticas, só
`kchy` aparece em rótulo — e num rótulo ASTRONÔMICO (f67r2), não numa planta. **Ressalva de
cobertura:** este conjunto IIIF é da cadeia astronômica R32 — só 1 fólio herbal e 1
balneológico; a leitura herbal/balneológica é sugestiva, não confirmatória. A evidência
forte e em escala é o Leg 1 (corpus inteiro).

## Interpretação — texto e imagem desacoplados no nível da palavra

> A topicalidade fraca da R56 é **variação de registro de prosa** (seções diferentes são
> escritas com vocabulário de prosa levemente diferente), **não** uma nomenclatura que aponta
> para os desenhos. O texto Voynichês e suas imagens **não estão acoplados no nível da
> palavra** — as palavras que distinguem o herbal não nomeiam as plantas desenhadas.

Isso **descarta o modelo de nomenclator / diagrama-rotulado** (palavras = nomes de objetos)
para o grosso do texto. Resta o dilema central, agora afiado:

- **língua de prosa real** (prosa real sobre tópicos diferentes), OU
- **sistema de baixo-conteúdo** com deriva topical (gerador/glossolalia com viés de tópico).

A R57 não decide entre os dois — mas elimina o meio-termo referencial. **A Rota 58 decide.**

## Rota 58 — bateria real-língua vs baixo-conteúdo (próxima fase decisiva)

Proposta pelo cryptanalyst, sobre o corpus inteiro, com baselines de língua natural:
1. **Entropia condicional de caractere h1/h2**: Voynich é notoriamente rígido — h2 << línguas
   naturais → baixo-conteúdo; h2 dentro da faixa latim-abreviado → língua real.
2. **LAAFU (linha como unidade)**: P(palavra | posição-na-linha) ≫ P(palavra) com forte
   preferência início/fim → gerador-por-linha; quase invariante à posição → língua real.
3. **Repetição adjacente da mesma palavra** (`daiin daiin`): ≫ qualquer língua natural →
   baixo-conteúdo; comparável a corpora naturais → língua real.

Guardrail: `rota57_word_grounding_not_decipherment`.
Script: `scripts/analyze_word_grounding.py`; testes: `tests/test_word_grounding.py` (suíte **393**).
Saídas: `data/derived/word_grounding_{,summary_}zl3b.csv`.
