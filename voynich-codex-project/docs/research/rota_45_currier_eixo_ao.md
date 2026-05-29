# Rota 45: Currier A/B — eixo a/o é o marcador de dialeto; eixo r/l é marcador de contexto

Esta rota corrige a Rota 44 (que usava regex de texto livre para detectar Currier, cobrindo apenas ~12% dos loci)
e re-roda a análise usando o código IVTFF `$L=A/B` dos headers do corpus ZL3b-n.txt.

Guardrail: `rota45_currier_axis_analysis_not_decipherment`.

## Cobertura corrigida

| Método | Currier A | Currier B | unknown |
|--------|-----------|-----------|---------|
| Regex texto livre (Rota 44) | 33 | 64 | 689 |
| IVTFF `$L=A/B` (Rota 45) | **186** | **510** | 90 |

A cobertura saltou de 12% para 88.5% das 786 ocorrências.

## Achado 1 — Efeito Currier no sufixo (sufixo completo)

| | Currier A (n=186) | Currier B (n=510) |
|---|---|---|
| `-ol` | 78 (42%) | 50 (10%) |
| `-al` | 51 (27%) | 204 (40%) |
| `-or` | 34 (18%) | 30 (6%) |
| `-ar` | 23 (12%) | 226 (44%) |

- Cramer's V (Currier × sufixo) = **0.4550** — efeito grande
- Chi² = 144.07, p_permutação = 0.0000 (nenhuma de 2000 permutações superou o real)

## Achado 2 — Decomposição em dois bits

| Eixo | Chi² | Cramer's V | A | B |
|------|------|-----------|---|---|
| **a/o** (qual vogal) | 135.28 | **0.4409** | 60% `o` | 84% `a` |
| **r/l** (qual consoante) | 21.05 | 0.1739 | 69% `l` | 50% `l`/50% `r` |

**O efeito Currier está concentrado no eixo a/o (V=0.44), não no r/l (V=0.17).**

- **Currier A = dialeto-o**: usa preferencialmente sufixos com vogal `o` (ol, or)
- **Currier B = dialeto-a**: usa preferencialmente sufixos com vogal `a` (ar, al)
- O eixo r/l tem sinal menor e mais equilibrado em B (50/50), mas A fortemente evita `-r` (31% r vs 69% l)

## Achado 3 — Correção: dotted/plain star NÃO é sinal real

A correlação "estrela dotted → otar/otal, plain → okal" da Rota 44 não sobreviveu controle:
- Chi² = 3.27, V = 0.11, p_permutação = 0.374 — não significativo
- Era artefato de leitura de percentuais com n pequeno; o sinal provável é só o efeito Currier

## Achado 4 — Pares mínimos são ambos Currier A

Os dois pares mínimos confirmados visualmente (f67v1: okal+okol; f99r: okar+okor) são ambos Currier A.
Provam distinção **intra-dialectal** de `-al/-ol` e `-ar/-or`, não inter-dialectal.

Implicação: o eixo r/l distingue contexto/posição dentro do mesmo dialeto,
enquanto o eixo a/o distingue entre dialetos.

## Achado visual — posição sequencial, não profundidade radial

O visual-annotator confirmou que em ambos os folios os pares mínimos habitam a **mesma banda
estrutural** (mesmo anel concêntrico ou mesma fila horizontal), diferindo apenas em posição sequencial.

Isso sugere que a borda codifica primariamente **SLOT/POSIÇÃO** dentro de uma série homogênea,
não hierarquia semântica de objeto.

## Interpretação consolidada

> O eixo a/o é o marcador primário de dialeto: A usa vogal-o, B usa vogal-a.
> O eixo r/l é o marcador secundário de contexto/posição dentro de cada dialeto.
> Operador (ok-/ot-) e eixo r/l variam relativamente pouco entre dialetos;
> eixo a/o é a dimensão mais modulada pelo escriba/dialeto.

Esta estrutura é consistente com um sistema de notação em que:
- O operador (ok-/ot-) e o r/l bit são convenções **estáveis** (partilhadas ou contextuais)
- O a/o bit é uma **convenção de escriba** — A encoda o-state, B encoda a-state

## Predição para Rota 46

A discriminação entre "borda = atributo-do-objeto" e "borda = convenção-de-escriba" requer:
teste de Currier × borda estratificado por tipo de objeto visual.

- Se V(a/o | objeto fixo) cai para ~0 → o bit a/o é determinado pelo objeto (M5 atributo)
- Se V(a/o | objeto fixo) permanece ~0.44 → o bit a/o segue o escriba (M3 dialeto)

O melhor terreno: seção astronômica f67–f73 (única mista A+B), com f69r (49 rótulos de estrela)
como alvo principal.

Guardrail: `rota45_currier_axis_analysis_not_decipherment`.
