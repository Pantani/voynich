# Relatório consolidado — A natureza do Voynichês (Rotas 43–61)

*Time de especialistas Voynich · corpus ZL3b-n.txt (Zandbergen-Landini, EVA/IVTFF) ·
5.385 loci, ~41.005 tokens · 479 testes pytest · 2026-05-29 · inclui capstone R62*

**Guardrail global:** este relatório descreve ESTRUTURA estatística, não tradução. Nenhuma
afirmação de sentido (`okal = Sol`, etc.) é feita. Cada rota carrega um guardrail
`_not_decipherment` em suas saídas.

---

## 1. Sumário executivo

Dezenove rotas de análise falsificável (R43–61) convergem para uma caracterização coerente:

> **O Voynichês é um sistema de tokens morfologicamente RICO e sintaticamente FINO, sem
> estrutura de ordem re-segmentável escondida.** Cada token é uma composição de camadas
> funcionais (operador `qo-/ok-/ot-` + núcleo `ch/sh` + vogal `a/o` + consoante `r/l`); o
> conteúdo, se existe, aparece apenas como um sinal topical FRACO no nível da palavra inteira,
> de registro de PROSA (não nomeação); e o texto está DESACOPLADO das imagens. Em escala de
> língua, NÃO é prosa de língua natural, e NÃO é ruído.

A pergunta *"é prosa de língua natural?"* foi **respondida: não** (decisivo). A pergunta
*"tem sentido proposicional?"* é, em princípio, **indecidível por estatística na escala do
token** — a fronteira epistêmica desta linha de investigação.

**Capstone (R62):** um gerador LOCAL e SEM CONTEÚDO reproduz 13 das 14 assinaturas medidas
(h2, repetição, decaimento de I(d), Zipf/Heaps, compressibilidade de ordem) — logo **sentido
NÃO é NECESSÁRIO para explicar as estatísticas** (prova de existência, não de unicidade; não
prova que o texto é sem sentido). A única assinatura que resiste é o LAAFU (ligação de tokens
específicos à posição de linha), uma regra de layout mais rica, ainda não-semântica. A linha
estatística está, portanto, **exaurida**: a incerteza restante é de proveniência/material.

---

## 2. O modelo estrutural

**Nível do TOKEN (R43–55) — 100% funcional/lexical:**

```
[qo-] + OPERADOR(ok/ot) + NÚCLEO(ch/sh) + VOGAL(a/o) + CONSOANTE(r/l)
```

| Camada | Preditor | Segue | Força |
|--------|----------|-------|-------|
| Registro `qo-` | locus P vs L | discurso/prosa | forte |
| Operador `ok/ot` | locus_subtype | registro (fluxo vs rótulo) | fraco (V=0.13) |
| Núcleo `ch/sh` | a própria palavra | **léxico fixo** (R55) | — |
| Vogal `a/o` | Currier A/B | **escriba/dialeto** | forte (V=0.45, p≪1e-6) |
| Consoante `r/l` | posição na linha | sintaxe posicional (-l fecha) | moderado |

**Nível da PALAVRA (R56–57):** sinal topical fraco-mas-robusto (within-Currier-B, só-prosa,
nulo por bloco-de-fólio: I_norm=0.046, z≈5.6), de **registro de prosa**, NÃO nomeação de
objeto; texto e imagem **desacoplados**.

**Nível da LÍNGUA (R58–61):** morfologicamente rico (I(d) de caractere cai de 1.72 bits ao
piso em d≈15 = escala do token), sintaticamente fino (sem dependência de médio-alcance;
comprime como seu próprio saco-de-palavras); SEM estrutura escondida re-segmentável (R61).

---

## 3. Ledger de falsificação

| # | Hipótese testada | Rota | Teste decisivo | Veredito |
|---|------------------|------|----------------|----------|
| 1 | Operador e borda são camadas independentes | R43–44 | colocação; Currier×prefixo/sufixo | **confirmado** |
| 2 | a/o = atributo do objeto desenhado (M5) | R46–47 | within-section, A vs B | **refutado** |
| 3 | a/o = escriba/dialeto (M3) | R45–48 | Currier; within-mão; universalidade | **confirmado** (V=0.45) |
| 4 | ok/ot = complementaridade/grafotaxia | R49 | pares mínimos; contexto | **nulo** (variação livre) |
| 5 | ok/ot = registro (fluxo vs rótulo) | R50 | locus_subtype fino | preferência suave (V=0.13) |
| 6 | núcleo ch/sh = camada de conteúdo | R52–55 | seção vs Currier; **par mínimo** | **refutado** → `lexically_fixed` |
| 7 | conteúdo no nível da PALAVRA | R56 | I(seção;palavra) corrigido + controles | **fraco mas real** (`topical_vocabulary`) |
| 8 | palavra = nome de objeto (nomenclator) | R57 | label vs prosa; cross-modal IIIF | **refutado** (`prose_register`) |
| 9 | prosa de língua natural | R58 | h2 / LAAFU / repetição vs baselines | **refutado** (h2=2.15≪natural) |
| 10 | gerador de Markov local simples | R59 | decaimento de I(d) + embaralhamento-de-linha | **desfavorecido** (morfo-rico) |
| 11 | cifra verbosa (sintaxe sub-token) | R60–61 | saco-de-palavras; **BPE re-segmentação (lzma+bz2)** | **sem apoio** (`lzma_artifact`) |
| 12 | gerador local sem conteúdo é suficiente? | R62 | adequação de modelo: gerador reproduz a bateria? | **quase** (13/14; só LAAFU resiste) → sentido não é necessário |

Note como o fio do conteúdo (linhas 6–8) ilustra o ciclo: um sinal promissor (ch/sh segue
seção, V=0.14) sobreviveu a um controle (Currier B), foi **temperado** por outro (R54: é
prosa, acopla ao operador) e **fechado** pelo teste decisivo (R55: par mínimo → léxico-fixo).

---

## 4. Contexto físico do manuscrito (Beinecke MS 408)

**O que está documentado sobre o objeto.** A datação por radiocarbono do velino (amostras analisadas na Universidade do Arizona) situa a *preparação da pele* no início do século XV, num intervalo de cerca de 1404–1438. Isso é evidência física forte sobre o suporte, mas constrange apenas um *terminus post quem* frouxo para a escrita: prova que o pergaminho não é uma fabricação moderna, não que o texto foi inscrito imediatamente — embora a ausência de palimpsesto e a consistência das tintas tornem a hipótese de escrita muito posterior pouco econômica. Codicologicamente, MS 408 é um códice real e encadernado, organizado em cadernos (fascículos) com dobras grandes e desdobráveis, exibindo evidência de mais de uma mão. O programa de imagens é coerente e planejado, com seções convencionalmente rotuladas como herbal, astronômica/zodiacal, balneológica, cosmológica, farmacêutica e de "receitas". A distinção **Currier A/B** é, para nós, um fenômeno estatístico *documentado*: medimos V(Currier×vogal a/o)=0,45, regimes inequivocamente distintos. O que permanece *debatido* é a sua natureza — mão, dialeto ou modo gerativo —; lemos como escriba/dialeto/modo, **não** como duas línguas naturais.

**Como o objeto restringe o espaço de hipóteses.** Um códice em velino caro, com trabalho escribal sustentado e consistente e um programa de imagens coerente, argumenta *contra* rabisco casual ou nonsense ocioso — mas, por si só, **não** estabelece significado linguístico. O artefato é compatível com (a) língua real pesadamente codificada, (b) língua construída, (c) notação não-linguística com sentido, ou (d) construção deliberada elaborada. Cada uma exige evidência distinta: (a), uma chave ou assinatura estatística recuperável (que não encontramos); (b)/(c), regularidade interna sem texto-fonte — exatamente o que observamos; (d), motivação e meios, não excluídos pelo objeto.

**A leitura paleográfica dos efeitos de linha (LAAFU).** Convenções escribais documentadas explicam *mecanicamente* a ligação glifo↔posição que medimos — gallows iniciais `p` (6,25×) e `t` (3,48×) como *littera notabilior* decorativa de parágrafo e linha, e glifos finais (`g` 6,23×, `m` 5,86×) como hábito de compressão/justificação de fim de linha. Isso *deflaciona* honestamente o efeito: posição de linha pode ser caligrafia, não conteúdo. O que a convenção **não** explica é a repetição adjacente do mesmo token (0,875%, ~2,77× o esperado i.i.d.; `daiin daiin daiin`) — esta resiste à leitura puramente decorativa.

**O desacoplamento texto↔imagem (R57) em termos físicos.** A maioria dos fólios emparelha desenhos com *texto corrido em parágrafo*, não com rótulos de um token sobre os objetos. Rótulos-de-objeto verdadeiros concentram-se nas seções farmacêutica e astronômica (f99r ~84% rótulo), que **não** são onde vive o sinal topical fraco da R56 (prosa de herbal/balneológico, f1r 100% prosa). O layout físico, portanto, é consistente com o nosso achado: o sinal é de *registro de prosa*, não de nomeação.

**Fechamento sóbrio.** Como artefato, o manuscrito sustenta com mais parcimônia um *sistema deliberado e regular* — construído, codificado ou notacional — produzido com intenção, mas sem evidência física de referência semântica. O que faltaria para avançar **não** é mais estatística na escala do token, e sim evidência de proveniência: uma chave, um texto-irmão, marca d'água/oficina identificável ou documentação de cadeia de posse que ancore o objeto a uma prática de escrita concreta.

---

## 5. Espaço de hipóteses e veredito criptanalítico

Fechado o arco R43–61, o espaço de hipóteses sobreviventes é estreito e os priores abaixo são **subjetivos e falsificáveis** — calibrações de um analista, não probabilidades objetivas.

**Gerador / sistema de baixo-conteúdo (~55%).** É o mais parcimonioso com o conjunto. A morfologia rígida (operadores templáticos `qo-/ok-/ot-` + bordas de matriz `ar/al/or/ol`, R43–50) e o núcleo `ch/sh` léxico-fixo (R55, veredito `lexically_fixed`, I residual de seção = 0,124 bits com p de permutação = 1,0, puro viés) produzem mecanicamente o `h2`=2,15 e o comprimento de correlação de ~15 caracteres — exatamente a escala de um token (R59). Sem dependência de médio-alcance, a "sintaxe" colapsa ao piso na fronteira do token. A cauda de longo alcance é cross-linha e morre sob embaralhamento de linha: é deriva de vocabulário por tópico, não ordem sequencial.

**Língua construída (~30%).** O códice é sério (velino 1404–1438, mãos consistentes, programa de imagens coerente), o Zipf (−1,079) e o Heaps (β=0,786, vocabulário muito produtivo) são plausíveis, e há um sinal topical fraco-mas-robusto na palavra (R56, I_norm=0,046, z≈5,6). Um sistema desenhado, morfologicamente rico e sintaticamente fino, encaixa sem exigir sentido proposicional recuperável.

**Cifra / codificada, incluindo verbosa (~15%).** Rebaixada, não eliminada. A R61 era o último instrumento que poderia ressuscitá-la: a re-segmentação BPE reviveu ganho de ordem no `lzma` (diferencial 0,035), **mas colapsou no `bz2` (0,005)** — o mesmo `lzma_artifact` da R60 (ganho de ordem-de-palavra de ~1–3% vs 12–25% em prosa natural). A cifra verbosa **com sintaxe sub-token estatisticamente recuperável** não ganhou apoio.

**Decisivamente excluídos como modelo de codificação:** substituição mono-alfabética/simples (`h2` longe do natural de 2,5–3,6 + a morfologia em camadas, incompatível com mapeamento letra-a-letra); prosa de língua natural escrita diretamente (fineza sintática, R58–60); ruído puro/glossolalia (a morfologia rígida + Zipf/Heaps + o sinal topical fraco a refutam); nomenclator/diagrama-rotulado (R57, `prose_register`: palavras diagnósticas com label_frac 2,6% ≈ 2,7% do corpus, texto↔imagem desacoplados); e cifra verbosa com sintaxe recuperável (R61).

**O resíduo honesto.** Uma cifra ou língua que **não deixe assinatura estatística na escala observável** permanece formalmente possível, porém **sem apoio positivo**. Esta é a fronteira epistêmica: a estatística na escala do token mede forma e redundância, não referência — não pode decidir sentido proposicional. "É prosa natural?" foi respondido (não); "tem sentido?" é, em princípio, indecidível por corpus.

**Plausibilidade histórica (~1415), sem afirmar nada.** Cifras de expansão/verbosas, línguas filosóficas/construídas e sistemas de abreviação e taquigrafia (tradição de siglas latinas, notas tironianas) eram conhecidos ou proto-conhecidos no período — suficiente para manter a janela aberta, insuficiente para preferir qualquer um deles.

**O que ainda moveria o ponteiro:** apenas evidência **externa** — uma crib/chave documentada ou proveniência que vincule o manuscrito a um sistema conhecido. A incerteza remanescente é sobre **chave/proveniência, não sobre estatística**; os dados de corpus deram tudo o que podiam.

---

## 6. Metodologia — por que confiar neste veredito

Cada rota seguiu um protocolo de **pré-registro cego**: o `corpus-statistician` executava a
análise (script + CSV + testes) enquanto o `cryptanalyst`, **sem ver os números**,
pré-registrava predições e limiares. Esse desenho adversarial pegou erros que um passe único
de confirmação teria escondido:

- **R54:** temperou o "achado de conteúdo" da R53 (o sinal ch/sh era prosa, não rótulo; acopla ao operador).
- **R56:** os controles flagueados (Currier + locus-tipo + nulo por bloco-de-fólio) cortaram um sinal de conteúdo inflado para **1/3** do tamanho bruto.
- **R59:** o controle de embaralhamento-de-linha revelou que a única cauda de longo alcance é tópico/documento, **não** sintaxe.
- **R61 (capstone):** o `corpus-statistician` retornou `hidden_structure` por um diferencial `lzma` de 0,035; o `cryptanalyst` havia pré-registrado CEGO que isso exigia confirmação em **dois** compressores ("a R60 me queimou"). O cross-check de `bz2` (0,005) **virou um falso positivo de sentido escondido**.

**Regra operacional validada:** SEMPRE rodar os controles que o cryptanalyst flagueia —
Currier, locus-tipo, nulo por bloco-de-fólio, e um **segundo compressor**. A correção de
viés de amostra finita (nulos de permutação) é obrigatória para informação mútua.

---

## 7. A fronteira honesta

A estatística de corpus mede **forma, redundância e correlação** — não **referência**. Por
isso este relatório responde *"que tipo de objeto formal é o Voynichês"* mas se recusa a
responder *"o que ele diz"*. As duas perguntas são separáveis, e só a primeira é acessível
aos métodos aqui. Nenhuma das 19 rotas afirmou uma tradução; toda saída foi marcada com um
guardrail explícito. Esta disciplina é o que dá peso ao que **foi** excluído.

---

## 8. Trabalho futuro

A linha "o que é o Voynichês" está **fechada à resolução que os dados de corpus permitem**.
A incerteza remanescente é de **proveniência/chave**, não estatística. Frentes possíveis, em
ordem decrescente de retorno esperado:

- **Externo (alto valor, fora do corpus):** evidência de proveniência, uma crib/chave, ou um
  texto-irmão. É o único caminho que poderia decidir "tem sentido?".
- **Gerador-mínimo — FEITO (R62):** um gerador local sem conteúdo reproduziu 13/14
  assinaturas (só LAAFU resiste) → sentido não é necessário para explicar as estatísticas; a
  linha estatística está exaurida. Ver `docs/research/rota_62_generator.md`.
- **Retorno decrescente / degenerado:** chunking por Currier A/B; HMM glifo-a-glifo. Re-sondam
  o orçamento de ordem abaixo-do-token que R59/R60/R61 mostraram quase vazio; e (R62) qualquer
  teste na escala do token não separa "sem conteúdo" de "conteúdo invisível a estes testes".
- **Pivô de domínio (não-estatístico):** frente VISUAL (R32+, anotação IIIF) ou evidência de
  PROVENIÊNCIA/material — o único caminho que poderia mover a pergunta "tem sentido?".

---

## 9. Índice — rotas, scripts e saídas

| Rota | Doc | Script |
|------|-----|--------|
| R43–44 | docs/research/ | analyze_form_collocations.py, analyze_section_distribution.py |
| R45–50 | docs/research/rota_47, rota_50… | analyze_section_scribe.py |
| R52–53 | rota_52_nucleo_ch_sh.md, rota_53_nucleo_controle_currier.md | analyze_nucleus.py |
| R54 | rota_54_nucleo_contexto.md | analyze_nucleus_context.py |
| R55 | (resumo §72) | analyze_nucleus_minpair.py |
| R56 | rota_56_word_content.md | analyze_word_content.py |
| R57 | rota_57_grounding.md | analyze_word_grounding.py |
| R58 | rota_58_language_signature.md | analyze_language_signature.py |
| R59 | rota_59_long_range.md | analyze_long_range.py |
| R60 | rota_60_compressibility.md | analyze_compressibility.py |
| R61 | rota_61_resegment.md | analyze_resegment.py |

Resumo cronológico completo (seções 43–80): `../../resumo_voynich_codex.md`.
Estado do harness e regras: `../../CLAUDE.md`.
