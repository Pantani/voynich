# Rota 60: Voynichês comprime como seu PRÓPRIO saco-de-palavras — textura, não sintaxe

Guardrail: `rota60_compressibility_not_decipherment`.

Teste final da linha "o que é o Voynichês". A estrutura que existe é INFORMAÇÃO ou TEXTURA?
Especificamente: a ORDEM das palavras carrega informação compressível (sintaxe → língua
codificada) ou não (saco-de-palavras → textura → construído/gerador)? 2 legs: statistician
(escada de compressão lzma/bz2) + cryptanalyst (pré-registro cego).

## A escada de compressão (bits/char)

| stream | lzma | bz2 | o que preserva |
|--------|------|-----|----------------|
| order0 (unigrama de char) | 4.03 | 4.17 | só freq. de char |
| markov2_char (trigrama de char) | 2.45 | 2.37 | estatística local de char |
| **word_unigram (SACO-DE-PALAVRAS)** | **2.39** | **2.29** | identidade+freq. de palavra, ORDEM destruída |
| **real** | **2.31** | **2.27** | tudo |

**Ganhos decisivos (lzma):**
- gain_over_markov2 = **0.055** (estrutura além de trigramas de char = identidade + ordem + repetição).
- **gain_over_wordunigram = 0.034 (lzma) / 0.008 (bz2)** ← o número decisivo: real vs seu próprio saco-de-palavras = informação de ORDEM-DE-PALAVRA.
- Decomposição: a contribuição de IDENTIDADE-de-palavra (markov2→saco) = 0.061 bpc é **~4× maior** que a de ORDEM-de-palavra (saco→real) = 0.015 bpc.

## Leitura honesta — o veredito mecânico engana

O veredito automático foi `word_order_informative` porque o ganho lzma (0.034) mal cruzou o
limiar pré-registrado de 0.03. **Mas é uma faca de gume:** o bz2 dá 0.008 (bem abaixo), os
dois compressores discordam, e o ganho fica em 0.008–0.034 conforme o método.

**Âncora de língua natural (cryptanalyst, pré-registro):** em prosa real, embaralhar as
palavras destrói MUITA redundância — o ganho de ordem-de-palavra roda **12–25%**. O
Voynichês fica em **~1–3%**, ~10× mais fraco. A predição cega do cryptanalyst (≈2%, dominado
por identidade não ordem, "sintaticamente fino") acertou em cheio.

> **Veredito integrado: Voynichês comprime essencialmente como seu PRÓPRIO saco-de-palavras.**
> A ordem das palavras carrega no máximo um traço fraquíssimo de informação — muito abaixo
> da prosa de língua natural. Confirma "sintaticamente fino" (R59) por um método independente.
> A compressibilidade vem da MORFOLOGIA/identidade da palavra (Zipf + repetição), não de sintaxe.

## A hipótese que sobrevive (caveat crítico)

"Fino na escala do TOKEN" **não** prova "sem sentido". Sobrevive a **cifra verbosa/de
expansão**: se 1 palavra de texto-claro → muitos tokens Voynich, a sintaxe vive ABAIXO da
fronteira do token e é invisível ao embaralhamento-de-palavra. A escada de compressão **não
consegue** separar "cifra verbosa com sentido" de "gerador de baixo-conteúdo" — ambos parecem
finos na escala do token. Também sobrevive: abreviação tipo-rótulo/lista (ordem livre,
identidade = conteúdo) — coerente com o registro de prosa fraco-topical da R56–57.

## Síntese cumulativa — a linha R43–60 (essencialmente fechada)

> **Voynichês é um sistema de tokens morfologicamente RICO e sintaticamente FINO:** um
> processo gerativo restrito (operadores templáticos qo-/ok-/ot- + bordas de matriz ar/al/or/ol)
> carregando uma camada fraca de tópico de prosa, com o TEXTO desacoplado das IMAGENS.

**Robustamente EXCLUÍDO:** substituição simples; prosa de língua natural direta; ruído puro;
nomenclator (palavras=nomes de objetos).
**NÃO distinguido:** "cifra verbosa com sentido" vs "gerador de baixo-conteúdo" — ambos finos
na escala do token.
- "É prosa de língua natural?" → **RESPONDIDO: não.**
- "Tem sentido?" → **não resolvível** por estatística na escala do token.

**Prior atualizado (cryptanalyst):** construído/gerador ~45–50%, língua-real-codificada
(sabor cifra-verbosa) ~30–35%, baixo-conteúdo-puro ~20%.

## Rota 61 — a única falsificação decisiva restante: sonda de SUB-TOKEN / cifra verbosa

A cifra verbosa esconde a sintaxe abaixo do token. Teste: **re-segmentar** o corpus (merges
tipo-BPE, ou chunking condicionado a Currier A/B) e re-medir MI de médio-alcance e
gain_over_wordunigram nas NOVAS unidades.
- Se a re-segmentação **revive** estrutura de médio-alcance / ganho de ordem → a sintaxe
  estava escondida pela grade de tokens → **cifra verbosa (com sentido)** sobe muito.
- Se **não revive** → não há sintaxe em nenhuma escala → **gerador** sobe.

Depois da R61, a linha está fechada à resolução que os dados permitem → consolidar R43–60
num relatório coerente.

Guardrail: `rota60_compressibility_not_decipherment`.
Script: `scripts/analyze_compressibility.py`; testes: `tests/test_compressibility.py` (suíte **442**).
Saídas: `data/derived/compressibility_{,summary_}zl3b.csv`.
