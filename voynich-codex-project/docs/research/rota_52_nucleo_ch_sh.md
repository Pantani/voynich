# Rota 52: O núcleo ch/sh segue CONTEÚDO, não escriba — primeiro candidato lexical

Guardrail: `rota52_core_glyph_signal_not_decipherment`.

## Contexto

As Rotas 43–51 mapearam a CASCA do token (`qo-` + ok/ot + a/o + r/l).
Todos os 4 elementos da casca provaram ser marcadores funcionais não-lexicais:
- qo- = registro/prosa
- ok/ot = preferência de registro (suave)  
- a/o = assinatura do escriba (V=0.45 por Currier)
- r/l = posição sintática

A Rota 52 atacou o NÚCLEO (elemento ch/sh entre operador e borda), que ainda era opaco.

## Resultado principal

| Preditor | V para ch/sh | Comparação com a/o |
|----------|-------------|-------------------|
| **Currier (escriba)** | **0.0861** | a/o=0.44 — MUITO menor |
| **Seção (conteúdo)** | **0.1294** | a/o=0.09 por seção — **MAIOR** |

**O núcleo ch/sh é o primeiro elemento do token que segue o CONTEÚDO, não o escriba.**

Este é o teste-de-tornassol que o cryptanalyst prescreveu:
- Se Currier > seção → convenção de mão → conteúdo não está no núcleo
- Se seção > Currier → **primeiro candidato a carga lexical** ← ESTE É O RESULTADO

## Distribuição ch/sh por seção

| Seção | n | ch% | sh% | ratio ch/sh |
|-------|---|-----|-----|-------------|
| Herbal | 1188 | 76% | 23% | 3.3 |
| Astronômico | 917 | 76% | 23% | 3.3 |
| Farmacêutico | 385 | 74% | 25% | 3.0 |
| **Balneológico** | **261** | **60%** | **39%** | **1.5** |
| Other | 137 | 64% | 35% | 1.8 |
| **Receitas** | **56** | **55%** | **44%** | **1.2** |

**Padrão**: receitas e balneológico (processos de corpo/fluidos/preparação) → mais sh.
Herbal/astronômico/farmacêutico (plantas/estrelas/objetos sólidos) → mais ch.

## Distribuição ch/sh por Currier

| Currier | n | ch% | sh% |
|---------|---|-----|-----|
| A | 1521 | 76% | 23% |
| B | 1215 | 69% | 30% |

O escriba tem ALGUM efeito (A prefere ch mais que B), mas MUITO menor que a/o (V=0.09 vs V=0.44).
O sinal de seção (V=0.13) supera o sinal de escriba para ch/sh.

## Quadro comparativo dos elementos do token

| Elemento | V(Currier) | V(seção) | Quem vence | Interpretação |
|----------|-----------|---------|-----------|---------------|
| qo- | alto | — | escriba/registro | prosa |
| ok/ot | 0.11 | 0.05 | escriba (fraco) | variação livre |
| a/o | **0.44** | 0.25 | **escriba** | assinatura dialetal |
| r/l | 0.17 | — | escriba (fraco) | posição sintática |
| **ch/sh** | **0.09** | **0.13** | **seção/conteúdo** | **candidato lexical** |

## Interpretação

> O núcleo ch/sh é a primeira dimensão do token que responde ao CONTEÚDO do manuscrito.
> ch parece associado a contextos de objeto/planta/céleste (herbal, astronômico).
> sh parece associado a contextos de processo/fluido/corpo (balneológico, receitas).

**Ressalvas importantes:**
1. V=0.13 é efeito moderado-fraco — não é o sinal de um lexema diretamente
2. O padrão de seção pode ser confundido com Currier (balneológico é 100% B, receitas é 100% B)
3. Precisa de controle: V(ch/sh | seção), controlando por Currier, para separar os dois efeitos
4. "segue conteúdo" não é "tem semântica conhecida" — é estrutura, não tradução

## Próximo passo — Rota 53

Controlar por Currier dentro das seções para isolar efeito de conteúdo puro:
- V(ch/sh × seção | Currier B) — dentro de B, herbal vs balneológico vs receitas
- Balneológico e receitas são 100% B → comparação direta sem confounder
- Herbal tem A e B → teste within-B herbal vs balneológico

Se V permanece após controle → ch/sh carrega sinal de conteúdo independente do escriba.
Se colapsa → era artefato da correlação seção↔Currier.

Guardrail: `rota52_core_glyph_signal_not_decipherment`.
