# Rota 66: matriz de ataque adversarial — 13 teses modernas vs o estado FECHADO do repo

Guardrail: `rota66_external_thesis_attack_not_decipherment`.

**Guardrail global:** este relatório descreve ESTRUTURA estatística e o que cada hipótese
externa PREDIZ, não tradução. Nenhuma afirmação de sentido (`okal = Sol`, etc.) é feita.
O ataque a teses externas FORTALECE ou ENFRAQUECE hipóteses; **não converte estrutura em
sentido e não produz tradução.** Cada veredito carrega o guardrail `_not_decipherment` e
foi validado mecanicamente contra as saídas do próprio gerador (R62), não por inferência.

---

## 1. Sumário executivo

A linha "o que é o Voynichês" fechou em R62 com um achado construtivo: um **gerador LOCAL e
SEM CONTEÚDO** reproduz 13 das 14 assinaturas medidas; a ÚNICA que resiste é o `laafu_I`
(ligação token↔posição-de-linha: real **0.471** > gerador **0.303**, lacuna **0.168**). A
Rota 66 usa essa lente como árbitro adversarial: uma tese externa só faz uma **predição
genuinamente NOVA** se aposta num sinal FORA dos 13 já reproduzidos pelo gerador.

> **Manchete: 1 de 13 teses modernas prediz um sinal além do gerador sem-conteúdo (R62);
> 6 são refutadas por instrumento nomeado; 12/13 estão MORTAS ou DEGENERADAS.** A única
> que bate o gerador (Parisel, sobre `laafu_I`) provavelmente DOBRA no gerador como regra de
> layout mais rica, não como sentido. A linha de ataque externo CONFIRMA a casca: o repo já
> fechou o espaço de hipóteses na escala do token. O movimento de maior valor restante é
> EXTERNO (proveniência/material/mão-tinta), não mais estatística de corpus.

Os priores permanecem **gerador ~70% / construída ~22% / cifra ~8%** — o ataque externo
NÃO os move; apenas mostra que nenhuma tese existente fura a parcimônia do gerador.

---

## 2. Metodologia — pré-registro cego + link mecânico não-circular

Mesmo protocolo adversarial das rotas R43–65, agora apontado para fora (as 13 teses modernas
do Voynich em vez de uma hipótese interna):

1. **Cryptanalyst (cego):** para CADA tese, pré-registrou — sem ver qualquer resultado novo —
   os sinais que ela prediz e um **limiar de falsificação** (que assinatura, e em que valor,
   mataria ou salvaria a tese).
2. **Corpus-statistician:** mapeou cada sinal predito para a rota existente que JÁ o testou
   (R43–R65) e para os conjuntos *reproduzido*/*resistente* do R62; depois escreveu
   `scripts/analyze_external_thesis_attack_matrix.py` (+ teste) que valida cada veredito
   **mecanicamente contra as saídas do próprio gerador**. O link é **não-circular**: uma tese
   só pode reivindicar "resiste ao gerador" numa assinatura que esteja no conjunto resistente
   REAL do gerador (`laafu_I`) — qualquer outra reivindicação de "resistência" é rejeitada
   pelo script por construção.
3. **Paleographer:** julgou plausibilidade histórica/material por volta de ~1415 (velino,
   número de mãos, anacronismo de mecanismos nomeados).
4. **Visual-annotator:** liquidou as teses de imagem/rótulo contra R57/R63/R64/R65a/R65b.
5. **Coordinator (esta síntese):** integra. As três perspectivas independentes CONVERGIRAM, e
   o script validou a integração mecanicamente — **essa triangulação é o peso epistêmico**,
   não a opinião de qualquer especialista isolado.

Todo veredito herdou as três disciplinas das rotas anteriores: teste no corpus INTEIRO,
controles de confundidor (Currier, locus-tipo, nulo por bloco-de-fólio, dentro-do-fólio,
segundo compressor) e o guardrail `_not_decipherment`.

---

## 3. O painel de instrumentos e a âncora `laafu_I`

O ataque reusa instrumentos já calibrados nas rotas. Cada tese é morta, salva ou degenerada
por UM discriminador nomeado:

| Instrumento | Rota | Valor Voynich | Faixa de língua natural | Função no ataque |
|---|---|---|---|---|
| `char_h2` (entropia de 2ª ordem) | R58 | **2.15** | 2.5–3.6 | mata língua-natural-direta, substituição, decifrações |
| `midrange_MI` (I(d), d≈20–100) | R59 | piso em d≈15 | I de médio-alcance > 0 | mata sintaxe natural (cai ao piso na escala do token) |
| `order_gain` (compressão de ordem) | R60 | 1–3% | 12–25% | confirma sintaxe-fina; mata "ordem de plaintext escondida" |
| `bpe_resegment_gain` (2 compressores) | R61 | lzma 0.035 → bz2 0.005 | revive em AMBOS | mata cifra verbosa/Naibbe (`lzma_artifact`) |
| `topical_word_MI` | R56/R57 | I_norm=0.046 (prosa, não nome) | — | tese de tópico SOBREVIVE fraca; nomenclator NÃO |
| `currier_ao` (V Currier×a/o) | R45/R47 | 0.45 (Currier 0.44 > seção 0.25) | — | eixo confirmado; NATUREZA não decidível por corpus |
| `label_object_coupling` | R57/R63/R64/R65b | desacoplado (n=171; refinado n=108) | — | mata rótulos=nomes-de-objeto |
| **`laafu_I`** (token↔posição-de-linha) | **R62/R65a** | **0.471** | gerador atinge só **0.303** | **A ÚNICA âncora além do gerador — a única tese que a nomeia sobrevive como actionable** |

**A âncora.** O gerador R62 (mecanismos: `base` + `section_cond` + `self_citation` +
`line_edge_bias`) casa 13/14 métricas dentro da tolerância. O `line_edge_bias` empurra o
`laafu_I` de 0.205 (piso i.i.d.) para 0.303 — mas o real é **0.471** (lacuna 0.168, fora da
tolerância de 0.08). É a ÚNICA assinatura que um viés de glifo-de-borda não alcança: o corpus
prende **tokens inteiros ESPECÍFICOS** à posição de linha mais fortemente do que uma regra de
borda consegue. Para casar, o gerador precisaria de uma **tabela de posição-por-token** —
ainda um mecanismo SEM CONTEÚDO, só com mais parâmetros (layout mais rico, não sintaxe).
Esse resíduo é o único território onde uma tese externa pode predizer algo novo.

---

## 4. A matriz de ataque

Reproduzida de `data/derived/external_thesis_attack_matrix_zl3b.csv` (fonte da verdade; o
script valida cada linha contra as saídas do gerador):

| # | tese | sinais preditos (resumo) | discriminador | rota mapeada | bate gerador | veredito |
|---|------|--------------------------|---------------|--------------|:---:|----------|
| 1 | Língua natural direta | h2~2.5–3.6; midrange_MI>0; order_gain 12–25% | `midrange_MI` | R58/R59/R60/R62 | não | **refuted** |
| 2 | Substituição simples / alfabeto perdido | herda h2 natural; midrange_MI>0 | `char_h2` | R58/R59/R60 | não | **refuted** |
| 3 | Cifra homofônica/verbosa | sintaxe sub-token revive na re-segmentação (2 compressores) | `bpe_resegment_gain` | R61/R60 | não | **refuted** |
| 4 | Cardan grille / Rugg / Zandbergen | exatamente o painel R62 (saída de tabela/grelha) | none | R62 | não | **unsupported** |
| 5 | Naibbe cipher (Greshko 2024) | ordem do plaintext revive ao desfazer grupos multi-glifo | `bpe_resegment_gain` | R61/R60 | não | **refuted** |
| 6 | Auto-citação / Timm–Schinner | adjacent_repeat~0.875%; só MI de curto alcance | none | R62/R58 | não | **unsupported** |
| 7 | Topic modeling / Bowern/Sterneck/Polish | topical_word_MI>0; acoplamento referencial | `topical_word_MI` | R56/R57/R62 | não | **survives_weakly** |
| 8 | Currier A/B como escriba/dialeto/modo | currier_ao V~0.45; a/o segue escriba>seção | `currier_ao` | R45/R47 | não | **survives_weakly** |
| 9 | Parisel: restrições posicionais, camadas direcionais, Currier switch | `laafu_I` ALTO (0.471); radial≠parágrafo | `laafu_I` | R62/R65a/R47 | **SIM** | **actionable** |
| 10 | Rótulos = nomes de objetos | mesmo objeto→rótulo consistente entre fólios | `label_object_coupling` | R57/R63/R64/R65b | não | **refuted** |
| 11 | Língua construída / notação técnica | perfil morfo-rico/sintaxe-fina inteiro | none | R49/R55/R65a/R62 | não | **external_only** |
| 12 | Gerador local sem conteúdo | painel R62; laafu_I~0.303 subestima 0.471 | `laafu_I` | R62 | não | **survives_weakly** |
| 13 | Decifrações pontuais (turco/hebraico/proto-romance/latim) | uma língua natural ESPECÍFICA | `char_h2` | R58/R59/R60 | não | **refuted** |

**Contagem (validada pelo script):** refuted = **6** {1,2,3,5,10,13}; unsupported = **2** {4,6};
survives_weakly = **3** {7,8,12}; actionable = **1** {9}; external_only = **1** {11}.
**bate o gerador = 1/13** (só a tese 9, sobre `laafu_I`). **refutadas por instrumento = 6/13.**

---

## 5. Discussão por cluster

### (a) Refutadas-por-instrumento — 6 teses, cada uma com a rota que a mata

Estas predizem um sinal que o corpus NÃO tem. Não são "indistinguíveis do gerador" — são
**contraditas pelos dados** (`contradicted_by_corpus`):

- **Teses 1, 2, 13 (língua natural direta, substituição simples, decifrações pontuais)** —
  morrem no **painel de língua natural**. O `char_h2` do Voynichês é **2.15**, muito abaixo
  da faixa 2.5–3.6 de qualquer fonte natural (R58); uma bijeção (substituição) PRESERVA a
  entropia da fonte, logo 2.15 já exclui substituição de uma língua natural. Não há MI de
  médio-alcance (d≈20–100) na R59 — a "sintaxe" cai ao piso na fronteira do token. O
  `order_gain` é 1–3% vs 12–25% em prosa natural (R60). As decifrações pontuais (Cheshire,
  Bax, Gibbs) decodificam um punhado de tokens escolhidos a dedo, sem gramática que reproduza
  o corpus inteiro — `char_h2` não-reprodutível as mata em bloco.

- **Teses 3, 5 (cifra verbosa/homofônica, Naibbe)** — morrem na **R61**. A re-segmentação BPE
  produziu um ganho de ordem no `lzma` (diferencial 0.035) que COLAPSA no `bz2` (0.005): o
  mesmo `lzma_artifact` que a R61 pegou com o pré-registro cego do cryptanalyst + cross-check
  do segundo compressor. Desfazer grupos multi-glifo (a aposta do Naibbe, reconstrução de
  Greshko 2024) NÃO revive ordem de plaintext além dos controles estruturalmente casados.
  A sintaxe sub-token **estatisticamente recuperável** não ganhou apoio.

- **Tese 10 (rótulos = nomes de objetos)** — morta pela **imagem** (ver §7).

### (b) Degeneradas-vs-gerador — teses 4, 6, 7, 8, 12 (NÃO refutadas, mas não decidem sentido)

A distinção crucial: estas **reproduzem apenas sinais já cobertos pelo gerador R62** ou
descrevem **estrutura confirmada que não decide sentido**. Não são contraditas pelos dados —
são *parcimoniosamente desnecessárias* ou *absorvidas*. Por isso `unsupported`/`survives_weakly`,
não `refuted`:

- **Tese 4 (Cardan grille / Rugg)** `unsupported` — prediz EXATAMENTE o painel R62 (saída de
  tabela/grelha mecânica) e nada mais; o gerador já reproduz isso por construção. Não nomeia
  o resíduo `laafu_I`. Degenera no gerador → sem predição nova. (Anacronismo: ver §7.)

- **Tese 6 (auto-citação / Timm–Schinner)** `unsupported` — É **literalmente o mecanismo nº 3
  do gerador** (`self_citation`, p_rep=0.0046). A ablação reproduz o `adjacent_repeat`=0.875%
  exato. Uma tese cuja predição já é um botão do baseline não pode bater o baseline.

- **Tese 7 (topic modeling / Bowern, Sterneck, hipótese polonesa)** `survives_weakly` — o
  sinal topical é REAL (I_norm=0.046) mas é **reproduzido pela tabela `section_cond` do
  gerador** (vocabulário condicionado à seção, não sintaxe). A R57 mostra que é
  **registro de PROSA, não-referencial** — não nomeia objetos. Sobrevive como existência de
  deriva topical fraca; a reivindicação de língua-real-específica (ex.: polonês) e a leitura
  referencial são `external_only` (R57 já refuta o referencial).

- **Tese 8 (Currier A/B como escriba/dialeto/modo)** `survives_weakly` — o eixo é
  CONFIRMADO: V(Currier×a/o)=0.45, com Currier (0.44) > seção (0.25). Mas isso é estrutura
  absorvível como um *modo do gerador* / chave de seção. A **NATUREZA** do switch (mão vs
  dialeto vs modo) é `external_only` — só paleografia externa de mão/tinta resolve.

- **Tese 12 (gerador local sem conteúdo)** `survives_weakly` — É **a própria baseline**.
  Reproduz 13/14, falha só no `laafu_I`, e PROVA que sentido não é necessário (prova de
  existência, não de ausência-de-sentido). Sobrevive como a hipótese mais parcimoniosa
  (~70%); não é "vencida" porque é o critério.

### (c) A única actionable — tese 9 (Parisel) e o teste novo que ela gera

A tese 9 (Parisel: restrições posicionais, camadas direcionais, Currier como switch) é a
ÚNICA que **nomeia o resíduo** `laafu_I` — a única assinatura fora do gerador (real 0.471 >
gen 0.303). Ela também acerta o registro radial≠parágrafo (R65a: prefix V_within=0.217,
p=0.0005). É `resists_generator` → **actionable**: vira um teste novo (proposto como Rota 67
em §8, Bloco 3). **Caveat honesto pré-registrado:** R62 e R65a já LEEM o resíduo como LAYOUT (tabela de
posição mais rica; `locus_kind` = seletor de registro), não como camada semântica direcional —
logo o teste provavelmente DOBRA no gerador. É pré-registrado como **degenerado-provável**.

### (d) A external_only (11) e os resíduos external_only das outras

- **Tese 11 (língua construída / notação técnica)** `external_only` (primária) — encaixa no
  perfil INTEIRO (operadores templáticos R49, núcleo léxico-fixo R55, registro de layout R65a),
  mas é **degenerada com o gerador na escala do token**: um sistema desenhado-com-sentido e um
  gerador sem-conteúdo são indistinguíveis por estatística de corpus (R62). Só uma chave/crib,
  texto-irmão ou proveniência separa os dois. É o prior ~22% que a estatística de corpus
  **provadamente não pode tocar**.

- **Resíduos external_only de outras teses:** a cifra verbosa SEM assinatura (resíduo da 3),
  a atestação de período (4/5), e a natureza do Currier por mão/tinta (8/9). Todos formalmente
  possíveis, nenhum com apoio positivo no corpus.

---

## 6. Camada paleográfica

**Suporte material a um sistema deliberado.** O velino data ~1404–1438 (radiocarbono),
há >1 mão, e o programa de imagens é coerente e planejado → suporta um sistema DELIBERADO e
regular, **sem evidência física de referência semântica**. Isso é consistente com gerador,
construída ou cifra — não decide entre eles.

**Anacronismo dos mecanismos NOMEADOS.** A grelha de Cardano (tese 4) é dos anos **1550** —
PÓS-DATA o velino. O Naibbe (tese 5) é **reconstrução de 2024**. Os mecanismos nomeados
pós-datam o objeto, embora a IDEIA subjacente (cifra de expansão, grelha) seja período-adjacente.
Por isso a tese 4 é `unsupported` por intenção-de-período, além de degenerada no gerador.

**A natureza do Currier (teses 8/9) é paleografia externa.** Mão vs dialeto vs modo só se
resolve por *ductus*, tinta e mapeamento de cadernos — não por corpus. Igualmente, teses 3/11
(cifra/construída sem assinatura) e 8/9 (natureza do switch) só avançam com evidência EXTERNA.

---

## 7. Camada visual

**Tese 10 (rótulos = nomes) está MORTA pela imagem.** R57 (label_frac de palavras
diagnósticas ≈ baseline do corpus), R63→R64 `decoupled` com potência (n=171), R65b refinado
(n=108 não-incerto). A mesma ninfa recebe **rótulos fólio-locais** (f71r vs f73r, divergência
p=0.011 / 0.013 refinado). O ÚNICO correlato visual é **COMPRIMENTO jarro-vs-órgão** (pharma,
V=0.345, p_within=0.0073) — isto é ESTRUTURA (comprimento de token segue tipo de desenho),
não nomeação.

**Tese 9 (ângulo visual) — radial é REGISTRO, não camada semântica direcional.** O texto
radial/circular É um registro distinto (R65a: prefix V_within=0.217, p=0.0005; `qo-` colapsa
15%→2% fora da prosa; `ot-` triplica 5%→16%; f67r2 confirma a R50 em corpus inteiro,
V=0.26, p=0.027). Mas isso opera como **LAYOUT** (`locus_kind` seleciona distribuição de
prefixo/núcleo sobre o MESMO inventário de operadores), não como a camada direcional
**semântica** que a tese 9 pediria.

**Frente visual ENCERRADA.** Nenhum teste de imagem novo move o ponteiro (cryptanalyst meta
em R65: "if Leg B (a) lands → declare visual front CLOSED" — aterrissou). O avanço da
pergunta "tem sentido?" exige proveniência/material, não mais imagem.

---

## 8. Veredito final do R66 — os cinco blocos

### Bloco 1 — TESES MORTAS (refuted) — predizem sinal que o corpus não tem

| # | tese | instrumento que mata |
|---|------|----------------------|
| 1 | Língua natural direta | `midrange_MI` (sem médio-alcance, R59) + h2=2.15 (R58) |
| 2 | Substituição simples | `char_h2`=2.15 (bijeção preservaria a entropia da fonte, R58) |
| 3 | Cifra homofônica/verbosa | `bpe_resegment_gain` (lzma 0.035 → bz2 0.005 = `lzma_artifact`, R61) |
| 5 | Naibbe cipher | `bpe_resegment_gain` (re-agrupar não revive ordem, R61) |
| 10 | Rótulos = nomes de objetos | `label_object_coupling` (ninfa fólio-local p=0.011, R57/R63/R64/R65b) |
| 13 | Decifrações pontuais | `char_h2`=2.15 não-reprodutível; sem gramática de corpus (R58/R59/R60) |

### Bloco 2 — VIVAS MAS DEGENERADAS (unsupported + survives_weakly) — vivas só como o gerador/estrutura, não distinguem sentido

| # | tese | por que degenerada |
|---|------|--------------------|
| 4 | Cardan grille / Rugg | prediz só o painel R62; degenera no gerador (+ anacrônica) |
| 6 | Auto-citação / Timm–Schinner | É o mecanismo nº 3 do gerador (`self_citation`) |
| 7 | Topic modeling | reproduzido pela tabela `section_cond`; R57 não-referencial |
| 8 | Currier A/B escriba/dialeto/modo | eixo confirmado (V=0.45); natureza = external_only |
| 12 | Gerador local sem conteúdo | É a baseline (~70%); falha só no `laafu_I` |

### Bloco 3 — VIRAM TESTE NOVO (actionable) — tese 9

A tese 9 (Parisel) nomeia o único resíduo `laafu_I` (0.471 vs 0.303) → propõe-se a
**ROTA 67: o discriminador "laafu conteúdo-vs-layout"** — a ligação token↔posição-de-linha
carrega **conteúdo DECODIFICÁVEL**, ou é uma **regra de layout mais rica** (tabela de
posição-por-token)? **CAVEAT honesto, pré-registrado:** R62/R65a já leem o resíduo como
layout (`locus_kind` = seletor de registro; tabela de posição mais rica) → o teste
**provavelmente DOBRA no gerador**. Pré-registrar a Rota 67 como **degenerado-provável**.

### Bloco 4 — EXIGEM PROVENIÊNCIA/MATERIAL (external_only)

- **Tese 11 (construída / notação técnica)** — primária; degenerada com o gerador na escala
  do token; só chave/crib/texto-irmão/proveniência separa (o prior ~22% intocável por corpus).
- **Resíduos external_only:** cifra verbosa SEM assinatura (de 3); atestação de período (4/5);
  natureza do Currier por mão/tinta (8/9).

### Bloco 5 — RECOMENDAÇÃO DO PRÓXIMO ATAQUE

Como **12/13 teses estão mortas ou degeneradas** e a única actionable (9) provavelmente
**dobra no gerador**, o movimento honesto de MAIOR valor é **EXTERNO**: proveniência,
material, mapeamento de mão/tinta — **não** mais estatística de corpus. Se ainda assim se
quiser corpus, é a Rota 67 acima, **pré-registrada como degenerada-provável**. Reafirma-se a
conclusão do R62: **testes na escala do token são degenerados por construção** — não separam
"sem conteúdo" de "conteúdo invisível a estes testes". O ataque externo CONFIRMA a casca: o
repo já fechou o espaço; nenhuma das 13 teses fura a parcimônia do gerador.

---

## 9. Ponteiros de arquivo

- **Script:** `scripts/analyze_external_thesis_attack_matrix.py` (mapeia cada tese à rota e ao
  conjunto reproduzido/resistente do gerador; valida vereditos contra as saídas do R62).
- **Teste:** `tests/test_external_thesis_attack_matrix.py` (**11 testes**; suíte total **560**).
- **CSVs:** `data/derived/external_thesis_attack_matrix_zl3b.csv` (13 linhas — a matriz) e
  `data/derived/external_thesis_attack_matrix_summary_zl3b.csv` (contagens + manchete).
- **Insumos de grounding:** `docs/research/rota_62_generator.md` (a âncora `laafu_I`),
  `docs/research/rota_65_radial_and_refinement.md` (frente visual fechada),
  `data/derived/generator_match_zl3b.csv` (13/14; laafu real 0.471 vs gen 0.303),
  `docs/summaries/relatorio_R43_R61_natureza_do_voyniches.md` (linha estatística).
- **Guardrail:** `rota66_external_thesis_attack_not_decipherment`.

---

## REGRA DE OURO (reafirmada)

A saída do R66 **fortalece ou enfraquece hipóteses; NÃO converte estrutura em sentido e NÃO
produz tradução.** Os priores permanecem **gerador ~70% / construída ~22% / cifra ~8%** — o
ataque externo NÃO os move; apenas confirma que nenhuma das 13 teses modernas fura a parcimônia
do gerador sem-conteúdo (R62). A única assinatura além do gerador (`laafu_I`) é melhor lida
como regra de layout, não como sentido. A incerteza remanescente é de **proveniência/material**,
não estatística.

Guardrail: `rota66_external_thesis_attack_not_decipherment`.
