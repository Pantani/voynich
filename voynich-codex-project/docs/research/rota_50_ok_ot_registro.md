# Rota 50: ok vs ot — preferência de registro (texto vs rótulo-de-figura)

Guardrail: `rota50_ok_ot_register_preference_not_decipherment`.

## Contexto

As Rotas 48 e 49 esgotaram os eixos macro: ok/ot não correlaciona com sufixo (V=0.06),
bit a/o (V=0.02), bit r/l (V=0.05), posição na linha (V=0.08), Currier (V=0.11),
vizinhança esquerda (cosine p=0.50 NS). Os pares mínimos ok/ot co-ocorrem livremente
no mesmo locus com o mesmo sufixo (20 casos), indicando que não estão em
distribuição complementar grafotática.

## Hipótese visual (visual-annotator, f67r2)

Em f67r2, os 3 tokens ot- estão TODOS em `&Ls` (labels de figuras lunares isoladas),
enquanto os 5 tokens ok- estão em `&L0` (texto de anel contínuo), `@Pb` (bloco de
setor) e `+P0` (parágrafo e rubrica). Separação visual perfeita neste fólio.

**Hipótese**: ok- é o operador de **texto/discurso**; ot- é o operador de
**nomeação/rótulo de figura**. Isso explicaria por que todos os eixos macro são
nulos — a distinção é de registro, não de objeto, seção ou escriba.

## Teste corpus-wide (Rota 50)

Usando o campo `locus` para extrair o subtipo fino (Ls, Lf, L0, Pb etc.), em 677 tokens
ok- e 668 tokens ot- do corpus completo:

| Subtipo | n | ok% | ot% | ot/ok | Tendência |
|---------|---|-----|-----|-------|-----------|
| Pb (blocked paragraph) | 9 | 77% | 22% | 0.29 | ok domina |
| L0 (ring continuous text) | 17 | 64% | 35% | 0.55 | ok domina |
| P0 (paragraph) | 1012 | 51% | 48% | 0.93 | **balanceado** |
| Cc (circular text) | 179 | 43% | 56% | 1.31 | leve ot |
| Lz (zodiac label?) | 39 | 43% | 56% | 1.31 | leve ot |
| Lf (label format) | 21 | 38% | 61% | 1.62 | ot domina |
| Ls (symbol label) | 13 | 38% | 61% | 1.60 | ot domina |
| Lt (prominent label) | 7 | 14% | 85% | 6.00 | **ot esmagador** |

**V(subtipo × ok/ot) = 0.1290** — maior V já medido para ok/ot.

O padrão é **direcional e consistente** em todos os subtipos: ok domina texto-fluxo,
ot domina label-figura isolado.

## Limitações

- n pequeno nos subtipos críticos (Ls=13, Lf=21, Lt=7) — não é possível inferência forte
- P0 (75% do corpus) mostra 50/50 — ambos aparecem em prosa, portanto NÃO é separação categórica
- V=0.13 é o maior já medido para ok/ot mas ainda efeito fraco/moderado

## Interpretação

> ok vs ot é uma **preferência suave de registro**, não uma regra categórica:
> ok é ligeiramente mais comum em texto contínuo/discursivo (fluxo);
> ot é ligeiramente mais comum em rótulos isolados de figura.
> Ambos aparecem em todos os contextos — são variantes de um mesmo slot de operador,
> com tendência de uso e não com distribuição complementar.

Esta interpretação é consistente com:
- pares mínimos co-ocorrentes (20 casos) → não é complementaridade
- V=0.13 em vez de 0.40+ → não é regra forte
- Prosa 50/50 → ambos são gramaticalmente válidos em discurso

## Design da Rota 51

Para confirmar (ou refutar) a hipótese de registro:

1. **R51-A — Bootstrap dos subtipos críticos**: Calcular IC 95% para a proporção ot%
   em Ls e Lf separadamente. Se IC não cobre 50% → efeito real. Necessário n maior
   (buscar mais exemplos nos folios com label Ls).

2. **R51-B — Markov serial k/t**: Testar se k e t se agrupam em runs dentro da linha
   (corpus-statistician R50-A da Rota 49). Se run-length médio de k excede o esperado
   ao acaso → ok/ot tem autocorrelação serial → o padrão é de escrita, não de objeto.

3. **R51-C — yt- como variante de ot-**: O prefixo `yt-` aparece em `&Ls` ao lado de
   `ot-` em f67r2. Testar se yt- tem o mesmo perfil de subtipos que ot- (ambos preferem
   label/figura vs. texto). Se sim, yt-/ot- são variantes de um mesmo "modo de nomeação".

Guardrail: `rota50_ok_ot_register_preference_not_decipherment`.
