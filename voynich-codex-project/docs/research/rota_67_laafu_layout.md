# Rota 67: o único resíduo aberto (LAAFU) é, em ~98%, LAYOUT — não conteúdo

Guardrail: `rota67_laafu_layout_not_decipherment`.
Guardrail global: este relatório decide **ESTRUTURA** (layout vs conteúdo), **nunca tradução**.
Nenhuma palavra Voynichesa recebe sentido aqui; "layout" significa uma regra posicional
SEM CONTEÚDO, não um decode.

## Sumário executivo

O gerador content-free da R62 reproduziu 13/14 assinaturas; o **único** resistente era o
`laafu_I` (ligação token↔posição-de-linha: real 0,471 vs gerador 0,303). A R66 marcou esse
resíduo como o ÚNICO ponto onde uma tese externa (Parisel, tese 9) poderia fazer uma predição
NOVA. A R67 decide **empiricamente** se esse resíduo é uma regra de **LAYOUT** sem conteúdo
(hábito caligráfico → dobra no gerador) ou se carrega **CONTEÚDO** condicionado a tópico (uma
fenda genuína). O controle pré-registrado decisivo — subtração da cabeça caligráfica — fecha
**97,6%** do excesso como hábito de escrita. O veredito mecânico é `laafu_mixed`, mas a leitura
é **layout**: o gerador da R62 chega efetivamente a **14/14** com um viés de borda ciente da
identidade da cabeça. A lead acionável de Parisel **dobra no gerador**, como pré-registrado.

## 1. A pergunta — e por que ela importa

A R62 estabeleceu uma **prova de existência**: um processo gerativo LOCAL e SEM CONTEÚDO
reproduz quase todo o perfil estatístico do Voynichês. Logo, **sentido não é NECESSÁRIO**
para explicar as estatísticas. Das 14 assinaturas medidas, 13 casaram. A única que resistiu
foi o **LAAFU** — a informação mútua entre a identidade do token e sua posição de linha
(`I(palavra; posição)`): real **0,471**, gerador **0,303** (Δ 0,168). O gerador produzia LAAFU
bem acima de zero (via viés de glifo-de-borda), mas não alcançava o real: o corpus liga
**tokens inteiros específicos** à borda de linha mais forte do que um viés de glifo consegue.

A R66 auditou 13 teses modernas contra o estado fechado e concluiu que **12/13 estão mortas ou
degeneradas** na escala do token; apenas a tese 9 (Parisel) ainda tocava algo que o gerador
NÃO reproduz — precisamente o `laafu_I`. Por construção, esse resíduo é o **único lugar do
mapa** onde uma tese poderia produzir uma predição nova e falsificável. Tudo o mais já está
contado pelo gerador. A R67 existe para fechar essa última casa: o resíduo é layout (caligrafia,
dobra no gerador) ou é a primeira pista de conteúdo posicional (uma fenda real)?

## 2. Método — harness de 2 pernas, pré-registro cego

Mesmo protocolo da R62: **statistician** mede o LAAFU **exatamente como a R62**
(`mutual_information(laafu_pairs(lines))`) e roda as quatro análises pré-registradas pelo
**cryptanalyst** ANTES de ver qualquer resultado. Decisões metodológicas fixadas no
pré-registro:

- **Pré-registro cego** do cryptanalyst: estimativa apostada **82% layout**.
- **Estimador desviesado** (Miller–Madow) ao lado do estimador-plug-in, para separar ligação
  REAL de inflação de amostra-finita (artefato de tamanho de vocabulário).
- **Nulos por permutação dentro-do-fólio** (within-folio): a posição é embaralhada preservando
  a estrutura de fólio, isolando o sinal posicional de confundidores de fólio/seção.
- **Sempre dentro-de-Currier** (A e B nunca agrupados): impede que a divisão de vocabulário
  A/B finja uma ligação posicional inexistente.

O veredito final é uma função pura de **três booleanos** — `head` (a cabeça explica o gap?),
`sparse` (o sinal é concentrado em poucos tokens?), `invariant` (a borda é invariante entre
seções?). `laafu_is_layout` requer os três; aqui só **`head`** vale limpo.

## 3. As quatro análises pré-registradas (números exatos)

| Análise | Medida | Valor | Leitura |
|---|---|---|---|
| — | `laafu_real` (plug-in, = R62) | **0,4709** | ligação confirmada (casa o 0,471 da R62) |
| — | `laafu` Miller–Madow (desviesado) | **0,4395** | NÃO é inflação de amostra-finita; ainda acima do baseline 0,303 |
| **A1 — subtração da cabeça** | `laafu_headless` (colapsa IDs da cabeça caligráfica) | **0,3070** | ≈ baseline R62 (0,303); a cabeça explica **97,6%** do gap → resíduo é LAYOUT |
| **A2 — curva de fechamento** | k50 / k70 / k90 (tokens p/ 50/70/90% do LAAFU) | **1015 / 2116 / 3733** | sinal DIFUSO em milhares de tokens — **não esparso** |
| **A3 — invariância de seção** | overlap de token-de-borda entre seções; p(JS) vs nulo | **0,020**; p=**0,018** | overlap baixo, mas p borderline (< 0,05, > 0,01) — banda ambígua |
| **A4 — dentro-de-Currier** | `laafu_I_A` (n=1815) / `laafu_I_B` (n=2646) | **0,589 / 0,487** | ligação REAL em cada modo escribal — não é artefato de agrupamento A/B |
| — | **veredito** | **`laafu_mixed`** | head ∧ sparse ∧ invariant; só `head` vale limpo |

**A1 — subtração da cabeça paleográfica (o controle DECISIVO).** Colapsa-se a IDENTIDADE dos
tokens da CABEÇA caligráfica: gallows line-iniciais `p`/`t` (a *littera notabilior* — letra
maiúscula ornamental de início de linha) e finais `-m`/`-g`/`-dy` (hábito de justificação de
margem). Com essas identidades neutralizadas, o LAAFU cai para **0,3070** — praticamente o
baseline 0,303 do gerador da R62. A cabeça explica **97,6%** do gap de 0,168. Ou seja: o resíduo
que o gerador não alcançou é, esmagadoramente, um **artefato caligráfico de LAYOUT**, não
conteúdo.

**A2 — curva de fechamento esparso.** O LAAFU TOTAL é diffuso: são precisos 1015 tokens para
50% do sinal, 3733 para 90%. Nuance crucial: esse bulk difuso é, em sua quase totalidade, **o
0,303 que o gerador JÁ reproduz** (morfologia rígida de token, espalhada por todo o léxico). O
*gap residual* — a parte que a A1 mostra ser carregada pela cabeça — é o que estava em aberto.
Portanto "não esparso" descreve o SINAL INTEIRO, não o resíduo de layout. (É por isso que o
booleano `sparse` falha: a concentração mediria o sinal todo, mas a parte do gerador é
deliberadamente difusa.)

**A3 — invariância de seção das bordas.** O overlap de tokens-de-topo entre seções é baixo
(0,020), mas a divergência Jensen–Shannon dá **p=0,018** contra o nulo within-folio —
**borderline**: abaixo de 0,05, acima do estrito 0,01. Cai na banda ambígua. O overlap baixo é
plausivelmente um confundidor de **VOCABULÁRIO-de-seção** (as palavras comuns de cada seção
diferem — herbal usa `pcho/qot/otchol`, balneológico usa `qok-/sol-`, etc.; ver
`laafu_layout_section_zl3b.csv`), **não** um sinal limpo de posição-carrega-conteúdo.

**A4 — dentro-de-Currier (nunca agrupado).** A ligação é REAL em cada mão: `laafu_I_A`=**0,589**
(n=1815), `laafu_I_B`=**0,487** (n=2646). Não é artefato do agrupamento da divisão de vocabulário
A/B. A ligação token↔posição é genuína dentro de cada modo escribal — o que é exatamente
consistente com um hábito caligráfico estável por escriba.

## 4. Síntese honesta — `mixed` mecânico vs. controle-decisivo = layout

O veredito mecânico é `laafu_mixed` (a regra dos três booleanos só satisfaz `head`). MAS o
controle pré-registrado DECISIVO — a subtração da cabeça — é enfático: **~98% do resíduo que
bateu o gerador da R62 é um hábito caligráfico de LAYOUT** (gallows inicial *littera
notabilior* + justificação de margem line-final). A leitura correta é: **a única assinatura
aberta basicamente FECHA como layout** — uma regra de posição-de-linha mais rica, porém AINDA
SEM CONTEÚDO, exatamente como a R62 antecipou ("uma tabela de posição-de-linha por token, ainda
sem conteúdo").

Em consequência, o gerador da R62 alcançaria efetivamente **14/14** com um viés de borda ciente
da IDENTIDADE da cabeça (não apenas da classe de glifo). Isto **REFORÇA** a tese central da
R62: **sentido não é necessário para explicar as estatísticas.** O acréscimo é paramétrico
(uma tabela de identidade-de-cabeça por posição), não sintático — continua um mecanismo
content-free.

O veredito é `mixed` (e não "layout limpo") por dois motivos, ambos benignos: (i) o fechamento
é **difuso** (A2), e (ii) o sinal de seção é **sub-limiar/borderline** (A3, p=0,018) — mais
plausivelmente um **confundidor de vocabulário-de-seção**, NÃO conteúdo condicionado a tópico.
Nenhum dos dois indica conteúdo: indicam apenas que a estatística não cravou o último decimal.

Portanto: a **lead acionável de Parisel (R66 tese 9) dobra, em sua quase totalidade, NO
GERADOR**, como pré-registrado (o caso "degenerado-provável" se concretizou). As priores são
**nudge, não move**: deslizam levemente em direção ao gerador (o último resíduo ≈ fecha), mas
**não se movem materialmente**, porque a R62 já contava o LAAFU como "layout mais rico, não
conteúdo". Priores:

> **gerador ~70% / construída ~22% / cifra ~8%** — essencialmente inalteradas.

Mesmo o remanescente borderline, **se** for real, significaria apenas que "a ligação posicional
é condicionada a tópico" — **NUNCA** um decode. A diferença entre "topic-conditioned position
binding" e "tradução" continua intransponível por estatística de corpus.

## 5. O que a R67 fecha — e o que resta

**Fecha:** a última casa aberta no mapa estatístico. O resíduo de LAAFU — a ÚNICA assinatura
além do gerador R62, e a única lead da matriz de teses externas da R66 — é, em ~98%, layout
caligráfico. O gerador content-free é efetivamente completo (14/14). Sentido não-necessário
sai **fortalecido**.

**Resta (benigno):** um resíduo borderline de seção (p=0,018), mais provavelmente um
**confundidor de vocabulário-de-seção** do que conteúdo posicional. Não é uma fenda; é o nível
de ruído esperado de um teste de divergência entre seções com léxicos distintos. Mesmo no
melhor caso para a tese, ele só reposicionaria a regra de layout (de "por token" para "por
token × tópico"), permanecendo content-free.

**A fronteira continua EXTERNA à estatística de corpus.** Como na R62, o avanço real exige
evidência **física/proveniência** (mão, tinta, datação, processo escribal), não mais um teste de
token. A próxima rota a tratar dessa fronteira é a **R68** (linha externa). A R67 encerra
definitivamente a pergunta "o resíduo de LAAFU é conteúdo?" com: **não — é layout.**

## 6. Ponteiros

- Script: `scripts/analyze_laafu_layout.py`
- Testes: `tests/test_laafu_layout.py` (**15 testes**; suíte **593**)
- Saídas: `data/derived/laafu_layout_summary_zl3b.csv`, `…_closure_zl3b.csv`, `…_section_zl3b.csv`
- Guardrail: `rota67_laafu_layout_not_decipherment`

---

**REGRA DE OURO (reafirmada):** a R67 decide **ESTRUTURA** — layout (regra posicional
content-free) vs. conteúdo (ligação condicionada a tópico) —, **não sentido**. O veredito é
`laafu_mixed` com leitura de **layout**; nenhuma palavra recebe tradução. A linha entre
estrutura confirmada e especulação é mantida: o resíduo fecha como caligrafia, não como
mensagem.
