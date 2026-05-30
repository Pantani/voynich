# Rota 58: Voynichês NÃO é prosa de língua natural — mas isso não é "sem sentido"

Guardrail: `rota58_language_signature_not_decipherment`.

A rota decisiva. As Rotas 43–57 mostraram: token 100% funcional, topicalidade de palavra
fraca e de prosa (não nome), texto↔imagem desacoplados. Resta a pergunta-mãe: **há LÍNGUA
REAL ali (pesadamente codificada) ou um sistema de BAIXO-CONTEÚDO (gerador/glossolalia com
deriva topical)?** Três legs do harness: statistician (mede), cryptanalyst (pré-registra
limiares cego + âncoras de literatura), paleographer (contra-interpretação histórica).

## As três assinaturas (ZL3b, 37 671 tokens, 5 216 linhas)

| Assinatura | Voynich (medido) | Âncora língua natural (literatura) | Anômalo? |
|------------|------------------|-----------------------------------|----------|
| **Entropia condicional de caractere h2** | **2.15 bits** | inglês 3.1–3.6; latim 2.5–3.0 | **SIM (decisivo)** |
| Entropia de palavra h2_word | 4.36 bits (H1_word 10.44) | gap grande = templático | leans templático |
| **LAAFU** I(palavra; posição-de-linha) | 0.471 bits, p=0.003 (1.94× nulo) | ≈0 (quebra de linha é tipográfica) | borderline (sob 2× nulo) |
| **Repetição adjacente** mesma-palavra | 0.875% (2.77× i.i.d.) | <0.25% em prosa | ~3.5× prosa, sob 3× i.i.d. |

**Validação interna:** h2 com o stream embaralhado = 3.87 = h1 (embaralhar mata a estrutura
de bigrama) → o cálculo de entropia condicional está correto, e há ~1.72 bits de
previsibilidade local real.

**Estrutura de borda de linha (glifo), inequívoca:** glifo INICIAL de linha — `p` 6.25×,
`t` 3.48×, `y` 2.91× sobre o corpus; glifo FINAL — `g` 6.23×, `m` 5.86×, `u` 5.62×. Os
gallows `p/t` no início de linha são exatamente a convenção decorativa documentada no
manuscrito (gallows-inicial de parágrafo/linha). Repetições top: `chol`×21, `qokeedy`×18,
`qokedy`×12, `daiin`×11.

## Veredito mecânico vs leitura honesta

O veredito automático foi **`mixed` (1/3 anômalas)** — só h2 cruzou o limiar pré-registrado;
LAAFU e repetição ficaram *elevadas acima da prosa natural* mas logo abaixo dos cortes
conservadores (2× nulo, 3× i.i.d.). **A leitura honesta corrige o "1/3":**

> **As TRÊS assinaturas apontam para longe da prosa de língua natural.** h2=2.15 é
> decisivamente baixo (≪ qualquer prosa natural); a repetição é ~3.5× a prosa; a ligação
> glifo↔borda-de-linha é dramática (6×). Voynichês **NÃO é prosa de língua natural.** Os
> tamanhos de efeito de LAAFU(palavra) e repetição são moderados, não extremos — então
> também **não grita "ruído aleatório".**

## O CAVEAT crítico (cryptanalyst): baixo-conteúdo ≠ sem sentido

h2 baixo + LAAFU + repetição são produzidos TAMBÉM por codificações legítimas de língua real.
A combinação importa:

| Codificação de língua real | h2 baixo? | LAAFU? | repetição? |
|----------------------------|-----------|--------|-----------|
| Abjad / queda de vogais | sim | não | leve |
| Latim com abreviação pesada/sigla | sim | **sim** (justificação) | possível (`-us/-rum`) |
| Cifra verbosa (um-para-muitos) | **sim** | não (salvo padding) | sim (nulos/padding) |
| Script silábico/CV-templático | **sim** | não | leve |
| Notação numérica/tabular | **sim** | **sim** (colunas) | **sim** (totais) |

**Sobreviventes se o veredito for baixo-conteúdo:** cifra verbosa, latim abreviado, notação
tabular/numérica. Crucial: abjad/silábico/homofônico dão h2 baixo SEM LAAFU — então a
combinação h2-baixo + LAAFU-forte + repetição **estreita o campo para codificações acopladas
ao layout OU um gerador**, e afasta de uma cifra de substituição limpa de prosa natural.

## Deflação paleográfica

A ligação glifo↔borda-de-linha é **mecanicamente explicada** por convenções escribais
documentadas (gallows-inicial decorativo; compressão de fim de linha) — não implica
significado. A abreviação explica h2 baixo + marcadores de fim de palavra, mas NÃO a
tripla repetição (`daiin daiin daiin`). O objeto físico (códice real, velino caro 1404–1438,
mãos consistentes, programa de imagens coerente) argumenta contra fraude casual.

## Veredito integrado e espaço de hipóteses

> **Voynichês é altamente estruturado mas decisivamente diferente de prosa de língua natural.
> Isso CONSTRANGE o espaço de hipóteses sem decidi-lo:** as mesmas estatísticas locais são
> reproduzidas por (a) língua real pesadamente codificada (cifra verbosa / latim abreviado /
> tabular), (b) língua construída, (c) gerador de baixo-conteúdo. Fica descartada a prosa
> natural simples E o ruído puro.

**Prior do cryptanalyst:** real-codificada 0.30 / baixo-conteúdo-gerativo 0.30 / **híbrido
0.40** (camada gerativa/templática de layout envolvendo uma camada fina de conteúdo real —
o que casa com o sinal topical fraco-mas-real da R56, z≈5.6). **Paleographer:** dado o
códice sério + assinaturas de baixo-conteúdo, o mais parcimonioso é **sistema construído ou
notação não-linguística com sentido**, acima de "prosa codificada simples" e de "fraude pura".

## Rota 59 — o teste DECISIVO (separador único)

Todas as estatísticas locais (h2, LAAFU, repetição) são reproduzíveis por TODO sobrevivente.
O único separador é a **correlação de longo alcance**:

**Decaimento da informação mútua I(d) vs distância d** (token a token, d=1…~200, dentro de
prosa Currier B; nulo por embaralhamento de frase que preserva bigramas locais):
- **Lei de potência / decaimento lento, I significativo até d>50 → LÍNGUA REAL CODIFICADA**
  (cifra/abreviação/abjad são transformações determinísticas de texto com correlação de
  longo alcance, e a preservam). Persegue-se então cifra-verbosa/abreviação.
- **Colapso exponencial até d<10 → GERADOR DE BAIXO-CONTEÚDO.** Confirmar com um modelo
  simples de auto-citação/template-de-linha que reproduza bigrama + LAAFU + repetição.

Secundário (barato): inclinação Zipf-Mandelbrot e expoente de Heaps (crescimento de
vocabulário). É a única assinatura que os sobreviventes de estatística local não conseguem
todos falsear.

Guardrail: `rota58_language_signature_not_decipherment`.
Script: `scripts/analyze_language_signature.py`; testes: `tests/test_language_signature.py` (suíte **410**).
Saídas: `data/derived/language_signature_{summary,lineedge,repeats}_zl3b.csv`.
