# Pré-registro CEGO — assinatura textual por MÃO / campanha de tinta (R72, frente externa #4)

*Cryptanalyst · Perna C · Beinecke MS 408 · corpus ZL3b-n.txt · 2026-05-30*

**Guardrail:** `rota72_hand_campaign_prereg_not_decipherment`.

**Status de cegueira:** este documento foi escrito **ANTES** de qualquer número da Perna B
existir. Eu **não** li, rodei ou inspecionei `data/derived/hand_campaign_*` nem
`scripts/analyze_hand_campaign.py`. Todas as predições derivam apenas da teoria e do estado
congelado R62/R67/R68. A cegueira **é** o valor do papel: meu método já pegou os falsos
positivos de R56 (inflação por confundidor), R61 (`lzma_artifact`) e R69 (nulo ingênuo de
páginas espelhadas). O risco aqui é o **mesmo de R56** — e o confundidor já está nomeado e
quantificado *a priori*: **V(mão×Currier)=0,980** (R68 §4.3).

---

## 0. A armadilha central, declarada de saída

A mão é **quase colinear** com Currier (V=0,980) e fortemente colinear com seção
(V(seção×Currier)=0,665). Da R68 §4.3: **mão 1 = 112 A / 0 B**; **mãos 2 e 5 = 100 % B**
(46 e 7); **mão 3 = 28 B / 2 A**. Logo:

> Qualquer V(mão) **marginal** (sem condicionar) sobre uma estatística textual é, em ~98 %,
> a **mesma variância de Currier A/B com outro rótulo**. Uma "assinatura por mão" marginal é
> o falso positivo **garantido** desta rota. Currier A/B já é conhecido (R68, e V(Currier×a/o)
> =0,45); reembrulhá-lo como "campanha de escriba" não é achado novo.

**Portanto o único teste que conta é o residual:** a variação entre mãos **que sobra depois
de fixar Currier E seção**, comparada ao **gerador R62 content-free** como nulo. Isto é
declarado **antes** dos números justamente para que ele não possa ser escolhido depois.

---

## 1. PERNA B — assinatura textual por mão: o que cada hipótese prediz

Estatísticas-alvo (as assinaturas R62, agora medidas **por mão**): **h2** (entropia
condicional / previsibilidade), **taxa de repetição** (token e linha, ex. `daiin daiin`),
**perfil de prefixos** `qo- / ok- / ot- / ch- / sh-`, e bordas `-dy/-y/-aiin`. Para cada uma
mede-se a dispersão **entre mãos** e — decisivamente — a dispersão entre mãos **dentro do
mesmo Currier e dentro da mesma seção** (within-Currier within-section, abreviado **WCWS**).

### 1.1 gerador (~70 %) — predição PRIMÁRIA

Um processo gerativo restrito (operadores templáticos + bordas de matriz) parametrizado por
**modo/dialeto** produz:

- **Marginal:** V(mão) sobre h2/repetição/prefixos **moderado a alto** — mas isso é
  **esperado e não-informativo**, porque é Currier A/B re-rotulado (mão↔Currier a 0,98).
- **WCWS (o teste real):** a variação entre mãos **colapsa para o piso** ao fixar Currier+
  seção. Predição quantitativa: **V(mão | Currier, seção) ≤ ~0,10** sobre o perfil de prefixos
  e **|Δh2| entre mãos co-Currier ≤ ~0,05 bits**. O gerador R62, **estratificado pela mesma
  partição de mãos**, **reproduz** a V(mão) residual observada — distância real−gerador
  **pequena** (mesma lógica de R69: `dir_edge` real 0,676 ≈ gen 0,686). Veredito esperado:
  **`hand_collinear_with_currier`** (re-rotulação), **não** campanhas com norma própria.
- Diferenças residuais mínimas que sobrarem são atribuíveis a **mão como variável de superfície**
  (preferência caligráfica/ortográfica de escriba: leve viés de `-y` vs `-dy`, densidade de
  `daiin`), **não** a uma camada de conteúdo. Mão é "textura de escriba", como `dir_edge` foi
  "morfologia de sufixo".

### 1.2 construída (~22 %) — predição DIFERENTE

Uma língua/notação artificial com **inventário único** mas executada por vários copistas:

- Predição **igual ao gerador no piso de conteúdo** (sem camada de sentido detectável por mão),
  **porém** poderia mostrar uma **assinatura de COPISTA estável e idiossincrática**: cada mão
  com um viés ortográfico **próprio e consistente** (ex.: mão X sistematicamente `-y`, mão Y
  `-dy`) que **persiste WCWS** mas é **pequeno** (V(mão|C,seção) na faixa **~0,10–0,20**).
- **Distinção-chave vs gerador:** se a variação residual por mão for **estruturada como estilo
  de cópia** (poucos eixos, consistente dentro de cada mão, reproduzível) **e** o gerador
  R62 **não** a reproduzir (distância real−gen **> ~0,10**), isso favorece **escribas copiando
  um exemplar fixo** — fraco a favor de construída/cifra sobre gerador puro. Ainda assim
  **não** é sentido: é regularidade de mão.

### 1.3 cifra (~8 %) — predição DIFERENTE

Cifra (chave aplicada a um texto-base):

- Se as mãos forem **operadores de cifra diferentes** (ex.: chaves/tabelas distintas por
  campanha), prediz **descontinuidade abrupta** no perfil de prefixos/bordas **na fronteira de
  mão** que **sobrevive WCWS** e que o gerador **não** reproduz — V(mão|C,seção) **> ~0,20** com
  **estrutura categórica** (não gradiente). Análogo de "texto-irmão interno": uma mão seria um
  **sub-sistema** destacável.
- **Mais provável (consistente com R61/R68):** mesmo na cifra, as mãos compartilham o **mesmo**
  inventário de operadores (a oficina é unificada, R68 `interleaved_production`), então cifra
  também **degenera** para o piso WCWS. Cifra só ganharia tração se uma mão isolasse um
  sub-sistema puro — exatamente o que R26–R61 procuraram e **não** acharam.

### 1.4 LIMIARES NUMÉRICOS PRÉ-REGISTRADOS (decisão da Perna B)

Métrica de decisão = **V(mão | Currier, seção)** sobre o **perfil de prefixos** (vetor
`qo/ok/ot/ch/sh` + bordas), e a **distância real−gerador** da V(mão) residual estratificada.
Limiares fixados **agora**:

| V(mão \| Currier, seção) | Distância real−gerador (V residual) | Veredito pré-registrado |
|---|---|---|
| **≤ 0,10** | qualquer | **`hand_collinear_with_currier`** — re-rotulação de Currier; gerador suficiente; prior **CONGELA** |
| **0,10 – 0,20** | **≤ 0,05** (gen reproduz) | **`scribe_surface_texture`** — viés de copista, **não** conteúdo; prior **CONGELA** |
| **0,10 – 0,20** | **> 0,10** (gen NÃO reproduz) | **`copyist_signature`** — estilo de cópia estável; **fraco** a favor de construída/cifra; **não** move prior sozinho (precisa #1/#6) |
| **> 0,20** | **> 0,10**, estrutura **categórica** na fronteira de mão | **`campaigns_with_own_norm`** — campanhas com norma própria; **único** resultado que JUSTIFICA reabrir; ainda assim só #1/#6 confirma sentido |
| **> 0,20** | **≤ 0,05** | **artefato de colinearidade** (mão ainda carregando Currier residual) — **CONGELA** |

**Padrão de nulo que EXIJO rodar (inegociável):**
1. **Nulo do gerador R62 estratificado:** rodar o gerador content-free, particioná-lo pela
   **mesma estrutura de mãos** (mesmos tamanhos/proporções A/B), medir a **mesma** V(mão|C,seção).
   O veredito é a **distância real−gerador**, não o valor absoluto (lição de R69).
2. **Nulo de permutação WCWS:** permutar rótulos de mão **dentro de cada estrato Currier×seção**
   (preserva Currier e seção; quebra só a identidade de mão). Se a V(mão) observada **não**
   exceder esse nulo permutado, é **ruído** → `hand_collinear_with_currier`.
3. **Nulo de fólio (anti-autocorrelação):** permutação em **blocos de fólio** (não token a
   token), porque mão é atribuída por fólio inteiro (ver §3).

Sem **os três** nulos, qualquer V(mão) positiva é **não-interpretável** e o veredito-padrão é
**CONGELA**.

---

## 2. PERNA A — dossiê material/tinta/proveniência: predição por hipótese

Dado instrumental-alvo (R68 §2.1, #4 da tabela de decisão): **homogeneidade de tinta entre
mãos** (1 vs N campanhas de tinta), e existência de **chave/irmão** (#1/#2).

| Hipótese | Prediz para tinta entre mãos | Prediz para chave/irmão |
|---|---|---|
| **gerador (~70 %)** | **Indiferente.** Tinta única OU N campanhas são **ambas** compatíveis — disciplina de produção ≠ sentido (R68 §4.6). Espera-se tinta ferrogálica genérica, sem assinatura de oficina. | **Nenhum** texto-irmão jamais aparece; **nenhuma** chave existe (não há o que cifrar). |
| **construída (~22 %)** | Indiferente quanto a 1 vs N (uma língua pode ser copiada em sessões/tintas distintas). | Poderia existir **gramática/léxico** (não chave); **texto-irmão** (#2) é o sinal forte — outro doc no mesmo sistema. |
| **cifra (~8 %)** | Indiferente. | **Chave documentada (#1)** é o sinal decisivo; campanhas de tinta correlacionadas a **mudança de chave** seriam sugestivas (mas não suficientes). |

### 2.1 O que MOVERIA o prior vs o que é só "artefato sério" (CONGELA)

**MOVE o prior (alça real):**
- **#1 chave/crib documentada** (cifra ⇒ chave; construída ⇒ gramática/léxico) — máximo, só
  **reconhecível**.
- **#6 decode que prediz fólios held-out** — máximo, decisivo contra o gerador.
- **#2 texto-irmão** (2º documento no mesmo sistema) — alta força de **refutação do gerador**.

**NÃO move — só "artefato sério" (CONGELA em 70/22/8):**
- **Tinta homogênea (1 campanha)** entre todas as mãos → reforça "oficina unificada/produção
  séria" (consistente com R68 `interleaved_production`); **não** toca sentido.
- **N campanhas de tinta** correlacionadas às mãos → reforça **estrutura de produção** (mais
  detalhe codicológico); ainda **consistente com gerador** executado em sessões. **Não** move.
- **Marca d'água / ID de mão / oficina (#3)** → origem/prática, **não** sentido.
- Qualquer correlação tinta×mão×Currier → é o **mesmo eixo de produção já conhecido**.

**Regra:** material/codicologia caracteriza o **OBJETO**; só evidência dos tipos **#1/#6 (e #2
como refutação do gerador)** toca a pergunta do sentido. Tudo o mais **CONGELA**.

---

## 3. Reafirmação da barra R68 e o risco de degenerescência

**Por que esta frente PROVAVELMENTE CONGELA 70/22/8, independentemente do resultado:**

1. **R62/R67:** o gerador content-free reproduz **14/14** assinaturas. Mão é um **eixo de
   estratificação**, não uma assinatura nova — particionar um sistema sem conteúdo por escriba
   **continua** sem conteúdo. Como R69 mostrou para direção (`dir_edge` = morfologia), a
   expectativa é **mão = textura de escriba**.
2. **R68 §4.6 (a barra):** seriedade/estrutura de produção é **consistente com AMBOS** os
   modelos sobreviventes. Mão×Currier=0,98 já diz que mão **é** o eixo de produção Currier —
   medir de novo por mão não adiciona um eixo independente.
3. **Tabela de decisão R68 §3.1:** **só #1 ou #6** move o sentido. Perna B (corpus) e a parte
   tinta da Perna A (#4/#3) são, por construção, **incapazes** de confirmar sentido.

**A ÚNICA exceção — o resultado ESPECÍFICO que NÃO degeneraria:**

> **`campaigns_with_own_norm`**: V(mão|Currier,seção) **> 0,20** sobre o perfil de prefixos,
> com **estrutura categórica** na fronteira de mão (descontinuidade abrupta, não gradiente),
> **que o gerador R62 estratificado NÃO reproduz** (distância real−gerador **> 0,10**) **E**
> que sobrevive ao nulo de permutação WCWS **e** ao nulo de blocos-de-fólio.

Isso indicaria que **mãos carregam uma norma independente de Currier/seção** — um sub-sistema
destacável (análogo a um "texto-irmão interno"). Mesmo assim: **reabriria a investigação, mas
NÃO confirmaria sentido** (continua precisando de #1/#6). É um gatilho de **reabertura**, não
de **mudança de prior**. Eu aposto, a priori, que **não** ocorrerá — a oficina é unificada
(R68) e o inventário é compartilhado (R26–R61).

---

## 4. Caça a falsos positivos — confundidores que o statistician PODE não controlar

Listados **antes** de ver os dados, para travar a interpretação:

1. **Colinearidade mão↔Currier↔seção (V=0,980 / 0,665).** *O confundidor-mestre.* Qualquer
   V(mão) marginal **é** Currier re-rotulado. **Controle exigido:** condicionar em **Currier E
   seção** (WCWS). Reportar V(mão) marginal **e** V(mão|C,seção); só a segunda decide. **Se só
   a marginal for reportada → resultado INVÁLIDO, veredito-padrão CONGELA.**
2. **Autocorrelação de fólio (mão atribuída por fólio inteiro).** Tokens do mesmo fólio
   **não** são independentes; n efetivo ≈ nº de **fólios**, não de tokens. Inflаciona toda
   significância. **Controle exigido:** unidade = fólio (ou nulo de **permutação em blocos de
   fólio**, não token-a-token); IC por bootstrap **de fólios**. Sem isto, p-valores são
   **otimistas demais** (mesma classe do `lzma_artifact` de R61 e do nulo ingênuo de R69).
3. **Nº de mãos desbalanceado + amostra minúscula por mão.** R68: mão 1 ≈ 112 fólios; **mão 5
   = 7**; mão 3 = 30. Estatísticas por mão (h2, perfil de prefixos) têm **variância enorme** nas
   mãos pequenas → "diferença entre mãos" pode ser **só ruído amostral** das mãos pequenas.
   **Controle exigido:** (a) **piso de amostra** por mão (ex.: ≥ ~500 tokens / ≥ ~5 fólios) ou
   reportar IC largo; (b) **rarefação/subamostragem** ao menor n comum antes de comparar h2
   (h2 é **enviesado por tamanho** — mão pequena parece ter h2 menor por amostragem, não por
   estrutura); (c) **excluir ou marcar** mãos abaixo do piso. Sem rarefação, qualquer Δh2
   entre mãos de tamanhos diferentes é **suspeito por construção**.
4. **Mãos puras-em-um-Currier não têm estrato cruzado.** Mão 1 = 100 % A; mãos 2/5 = 100 % B.
   Para essas, **não existe** comparação WCWS (não há A e B na mesma mão) → a única comparação
   honesta é **dentro da seção herbal**, onde A e B coexistem entre mãos. **Controle exigido:**
   restringir o teste residual à(s) **seção(ões) com mistura A/B** (herbal); fora dela, mão e
   Currier são **inseparáveis** e nada pode ser concluído.
5. **Comprimento de token/linha por seção como confundidor de repetição.** Repetição (`daiin
   daiin`) e bordas variam por **tipo de locus** (R50/R65: radial vs parágrafo). Se as mãos
   diferem em **mix de locus_kind**, a "assinatura de mão" é **locus**, não mão. **Controle
   exigido:** condicionar (ou estratificar) também por **locus_kind** quando disponível.
6. **Múltiplas comparações.** Com 5 mãos × várias métricas (h2, repetição, 5 prefixos, 3
   bordas), há **muitos testes** → algum "significativo" por acaso. **Controle exigido:**
   correção (Holm/FDR) **ou** uma **única** métrica de decisão pré-registrada (escolho **V(mão|
   C,seção) sobre o vetor de prefixos** como a estatística primária; o resto é exploratório).
7. **Atribuição de mão é ela própria incerta/contestada.** R68 §2.1: a **natureza** mão/dialeto/
   modo é "contestada"; ~5 mãos é de "bolsa posterior". Erro de rótulo de mão **atenua** ou
   **fabrica** estrutura. **Controle exigido:** tratar o nº de mãos como dado externo ruidoso;
   não sobre-interpretar fronteiras de mão finas.

---

## 5. Resumo executivo (≤25 linhas)

1. **Cegueira confirmada:** escrito antes de qualquer número; não toquei `hand_campaign_*` nem
   o script da Perna B. Predições só de teoria + estado congelado.
2. **Armadilha-mestra nomeada a priori:** V(mão×Currier)=0,980 ⇒ qualquer V(mão) **marginal**
   é **Currier A/B re-rotulado** = falso positivo garantido (classe de R56).
3. **Métrica de decisão pré-registrada:** **V(mão | Currier, seção)** sobre o vetor de prefixos
   `qo/ok/ot/ch/sh`+bordas, julgada pela **distância real−gerador R62 estratificado** (nulo
   correto = gerador, não acaso; lição de R69).
4. **Limiares fixados:** ≤0,10 → `hand_collinear_with_currier` (CONGELA); 0,10–0,20 com gen
   reproduzindo → `scribe_surface_texture` (CONGELA); 0,10–0,20 com gen **não** reproduzindo →
   `copyist_signature` (fraco, não move sozinho); **>0,20 + categórico + gen não reproduz +
   sobrevive nulos** → `campaigns_with_own_norm` (**única** exceção que reabre, ainda sem
   confirmar sentido).
5. **Predição por hipótese:** gerador → colapso WCWS ao piso (PRIMÁRIA); construída → possível
   `copyist_signature` pequeno e estável; cifra → só ganha se uma mão isolar sub-sistema puro
   (improvável, oficina unificada R68).
6. **Nulos EXIGIDOS (3):** gerador R62 estratificado pela mesma estrutura de mãos; permutação
   WCWS (dentro de Currier×seção); permutação em **blocos de fólio** (anti-autocorrelação).
   Faltando qualquer um → veredito-padrão CONGELA.
7. **Perna A (material):** tinta 1-vs-N campanhas é **indiferente** ao sentido — só "artefato
   sério" → CONGELA. Só **#1 (chave/crib)**, **#6 (decode held-out)** movem o prior; **#2
   (texto-irmão)** refuta o gerador. Tinta/marca d'água/ID-de-mão = OBJETO, não sentido.
8. **Barra R68 reafirmada:** produção séria ≠ sentido; mão é eixo de **estratificação**, não
   assinatura nova. Esta frente **CONGELA 70/22/8** salvo a exceção do item 4.
9. **Confundidores que o statistician pode perder:** (i) colinearidade mão/Currier/seção →
   exigir WCWS; (ii) autocorrelação de fólio → n efetivo = fólios, nulo em blocos de fólio;
   (iii) desbalanço (mão 5 = 7 fólios) + viés de tamanho em h2 → **rarefação** ao menor n;
   (iv) mãos puras-em-um-Currier não têm estrato cruzado → restringir o teste à herbal (mista
   A/B); (v) `locus_kind` como confundidor de repetição; (vi) múltiplas comparações → 1
   métrica primária; (vii) rótulo de mão é ruidoso/contestado.
10. **Aposta a priori:** degenerescência. Espero `hand_collinear_with_currier` ou
    `scribe_surface_texture`, distância real−gerador pequena, priores **inalterados 70/22/8**.

**Guardrail:** `rota72_hand_campaign_prereg_not_decipherment`. Tudo aqui caracteriza
SEQUÊNCIA/OBJETO e os limiares de decisão. **Nada afirma sentido.** Só #1 ou #6 move o prior.

*Fim do pré-registro cego (Perna C).*
