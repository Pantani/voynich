# Rota 69: hipóteses "estilo Leonardo" — espelhamento, reverso, leitura direita→esquerda

Guardrail: `rota69_directionality_mirror_not_decipherment`.
Guardrail global: esta rota decide **ESTRUTURA** (existe assimetria de direção/espelho além
da morfologia?), **nunca tradução**. Nenhuma palavra Voynichesa recebe sentido aqui.

## Sumário executivo

O usuário pediu para varrer as hipóteses populares na internet — em especial a de que o
manuscrito seria de **Leonardo da Vinci** (escrita espelhada, "palavras de trás pra frente",
criptografia visual, páginas espelhadas) — compará-las com o estado fechado do repo e
**testar** as que forem testáveis.

Dois resultados, um materializado e um estatístico:

1. **A autoria de Leonardo está refutada pela materialidade.** O velino é datado por C14 em
   **1404–1438**; Leonardo nasceu em **1452**. O pergaminho foi fabricado de 14 a 48 anos
   *antes* do nascimento dele, e a tinta ferrogálica + pigmentos batem com o início do séc. XV.
   Usar 50 anos de velino virgem guardado E casar os materiais ao período torna a hipótese
   essencialmente impossível. (Leonardo entra na longa lista de "autores" refutados: Bacon,
   Dee/Kelley, Fontana, Averlino…)

2. **As TÉCNICAS de Leonardo, porém, são testáveis independentemente de quem segurou a pena** —
   e a Rota 69 as testou. Veredito: **`leonardo_operations_degenerate`**. Espelhar tokens, ler
   de trás pra frente, leitura direita→esquerda e páginas espelhadas **não produzem nenhum sinal
   além do que o gerador content-free da R62 já reproduz**.

O achado de fundo é um **teorema**, confirmado empiricamente: a entropia condicional de um
processo **estacionário é invariante por reversão** —

```
H(c_i | c_{i-1}) − H(c_{i-1} | c_i) = H(c_i) − H(c_{i-1}) → 0
```

Medido no corpus real: `h2_fwd − h2_bwd = −0,00002` (h2 = 2,153 idêntico nas duas direções;
h3 = 1,899 idêntico). **A direção de leitura é invisível no nível da sequência.** Logo a famosa
entropia h2 (o argumento central do paper de direcionalidade de 2025) **não pode** distinguir
esquerda→direita de direita→esquerda. O único conteúdo direcional de 2ª ordem reduz-se a **um
número** — `dir_edge = H(1ª letra) − H(última letra) = +0,676` — que é **morfologia de sufixo**
(fins de palavra mais rígidos que inícios), reproduzida pelo gerador (`+0,686`, Δ=0,010) e que
simplesmente **troca de sinal** quando todo token é invertido (`−0,676`). Pura casca templática.

A pré-registração cega do cryptanalyst (prior de 7% para QUALQUER sinal novo) acertou cada sinal
e cada confound — inclusive um **falso positivo** que o método pegou (ver §5).

## 1. As hipóteses da internet vs o estado do repo

Varredura da literatura (Wikipédia, ciphermysteries, arXiv, edithsherwood, Yale News, etc.).
Cada hipótese externa foi mapeada contra nosso ledger de falsificação R43–R68.

| # | Hipótese (internet) | Proponente / fonte | Status externo | Nosso veredito (rota) |
|---|---|---|---|---|
| 1 | Substituição simples (letra-a-letra) | Friedman/NSA (1950s) | rejeitada (freq. de letras) | **EXCLUÍDA** (R43–55) — concordamos |
| 2 | Cifra polialfabética | vários | descartada (entropia) | **EXCLUÍDA** (h2 baixo, R58) |
| 3 | **Cifra verbosa** | Pelling; **Naibbe 2025** | "prova de conceito" plausível | **EXCLUÍDA na forma recuperável** (R61 `lzma_artifact`); cifra-sem-assinatura sobrevive ~8% |
| 4 | Língua natural (europeia desconhecida) | vários | "compatível com stats" | **EXCLUÍDA como prosa direta** (R58, h2=2,15≪3,1) |
| 5 | **Leitura direita→esquerda / Pahlavi** | arXiv 2509.10573 (2025); Pahlavi | "stats favorecem R→L *se* for língua" | **R69: artefato de morfologia** — h2 é invariante por reversão |
| 6 | **Leonardo: espelho / reverso / páginas espelhadas** | Edith Sherwood | sem prova; "letra parecida" | **R69: `degenerate`**; autoria refutada por C14 |
| 7 | Nahuatl / asteca | Tucker & Talbert (2014) | criticada; contradiz C14 | incompatível com nossa estrutura templática |
| 8 | Khojki / scripts indianos | deep-learning (2023) | "semelhança de glifo" | sobre forma de glifo, não estrutura textual — ortogonal |
| 9 | Língua construída / filosófica | Friedman; Wilkins-like | especulativa | **SOBREVIVE** — prior ~22% |
| 10 | **Hoax por grade de Cardan** | Rugg (2003); Schinner | reproduz stats superficiais | nosso gerador R62 é um primo disto → "sentido não é necessário" |
| 11 | **Auto-citação / processo gerativo** | **Timm & Schinner (2019)** | simulação reproduz stats | **ALINHAMENTO FORTE** — nosso gerador R62 usa auto-citação; 13/14 assinaturas |
| 12 | Texto significativo (rede semântica) | Montemurro (2013); Yale tf-idf | "clusters = tópicos" | parcial: R56 acha topicalidade **fraca** mas real (prosa, não nome) |
| 13 | Glossolalia / fluxo de consciência | Kennedy & Churchill | "impossível provar" | nem ruído nem prosa (R58); não decidível por stats |
| 14 | Autores (Bacon, Dee, Fontana, Averlino) | vários | sem evidência | fora do nosso escopo (natureza, não autor); vários refutados por data |

**Convergências importantes.** A literatura mainstream (Bowern & Lindemann; Wikipedia cita
`h2≈2`, "mais previsível que línguas naturais 3–4", estrutura prefixo-raiz-sufixo) **coincide
exatamente** com nossos R58/R43. O processo de auto-citação de **Timm & Schinner** é, na prática,
a mesma família do nosso gerador R62. Nosso projeto está na fronteira do que a literatura sabe —
e em alguns eixos (o ledger de falsificação, o gerador como árbitro, R69) à frente dela.

**Tensão produtiva — Naibbe (2025).** O paper Naibbe mostra que uma **cifra verbosa executável à
mão** no séc. XV reproduz muitas stats do VM. Isso NÃO contradiz nosso R61: o R61 exclui cifras
verbosas que deixam **ordem escondida recuperável** (o ganho lzma colapsa no bz2). Naibbe é
apresentada pelos próprios autores como *benchmark*, não solução — e cai precisamente no nosso
fatia residual "cifra/construída sem assinatura estatística" (~8–22%). Coerente com nossos priores.

## 2. A pergunta testável da Rota 69

Tirando a autoria (refutada), as ideias "estilo Leonardo" viram operações concretas no corpus:

- **Reverso de palavra** ("trás pra frente"): inverter os caracteres de cada token.
- **Leitura direita→esquerda**: ler o fluxo ao contrário (= entropia condicional backward).
- **Páginas espelhadas**: fólios vizinhos seriam o espelho um do outro.
- **Cripto visual**: nível de forma de glifo — fora do escopo de um teste só-texto (e a frente
  visual R63–65 já fechou: texto↔imagem desacoplados).

Método (idêntico a R62/R66/R67): medir cada operação no corpus real e **arbitrar contra o
gerador content-free da R62**, que sorteia **palavras reais inteiras** em ordem i.i.d. — logo tem
morfologia intra-palavra **idêntica** ao real, mas ordem de palavra destruída. Um sinal só conta
como NOVO se **vence o gerador** (a mesma régua que o resíduo LAAFU um dia cruzou).

## 3. Resultado A — invariância por reversão (o golpe decisivo)

| corpus | h1 | h2_fwd | h2_bwd | h3_fwd | h3_bwd | H(1ª) | H(últ) | dir_edge |
|---|---|---|---|---|---|---|---|---|
| **real** | 3,872 | **2,153** | **2,153** | 1,899 | 1,899 | 3,206 | 2,530 | **+0,676** |
| real_reversed_tokens | 3,872 | 2,153 | 2,153 | 1,924 | 1,924 | 2,530 | 3,206 | **−0,676** |
| word_shuffle | 3,872 | 2,153 | 2,153 | 1,926 | 1,926 | 3,206 | 2,530 | +0,676 |
| generator_base | 3,869 | 2,149 | 2,149 | 1,918 | 1,918 | 3,208 | 2,522 | +0,686 |
| generator_full | 3,881 | 2,217 | 2,217 | 1,988 | 1,988 | 3,244 | 2,587 | +0,657 |

`real h2_fwd − h2_bwd = −0,00002`. **Idêntico nas duas direções**, em h2 E h3. Isto é forçado:
para uma fonte estacionária a entropia condicional é a mesma para frente e para trás (a entropia
conjunta do bigrama é simétrica sob troca do par; as duas marginais diferem só pelo 1º/último
caractere de todo o fluxo). **Conclusão: nenhuma medida de entropia condicional — em qualquer
ordem — pode favorecer R→L sobre L→R.** O paper de direcionalidade de 2025, lido à luz disto,
não está detectando uma direção de leitura escondida: está re-descrevendo a assimetria de
**borda de palavra**.

## 4. Resultado B — o único conteúdo direcional é morfologia de sufixo

Toda a assimetria direcional de 2ª ordem colapsa em **um número**: `dir_edge = H(1ª letra) −
H(última letra) = +0,676 bits`. Inícios de palavra são mais variados (q/o/ch/sh/d/y/gallows);
finais são dominados por `y`/`n`/`-aiin`/`-dy` → mais previsíveis. É o fato clássico "fins de
palavra são rígidos". Três provas de que isto é **casca**, não direção de leitura:

- **O gerador reproduz**: `dir_edge` gerador `+0,686` vs real `+0,676`, Δ=0,010 (< limiar 0,05).
- **Inverter tokens troca o sinal e preserva a magnitude**: `+0,676 → −0,676` (exato). O "sinal"
  só rastreia **de que lado fica o sufixo** — `morphology_artifact_confirmed = True`.
- **Embaralhar a ordem das palavras não muda nada** (`+0,676` idêntico) → a assimetria é 100%
  intra-palavra, não há componente de ordem/sintaxe.

**Nenhum reverso aproxima h2 da banda de língua natural [2,5; 3,6]**: h2 fica preso em ~2,15 em
todas as variantes. Reversão é uma involução sobre estatística local — não consegue fabricar a
sintaxe de longo alcance que falta (o déficit é sintaxe ausente, não um eixo trocado).

## 5. Resultado D — páginas NÃO são espelhadas (e o falso positivo que o método pegou)

A 1ª implementação do teste de página usou um nulo ingênuo (par aleatório global) e **acusou
`mirror_page_signal`** (p=0,0066). Mas o cryptanalyst tinha **pré-registrado exatamente este
confound**: fólios vizinhos compartilham seção, mão e vocabulário, então se sobrepõem mais que
páginas distantes em **qualquer** alinhamento — não por espelhamento. Implementada a adjudicação
pré-registrada (efeito espelho-específico = sobreposição-reversa − sobreposição-direta, p<0,01):

- facing: **reversa=0,00450 < direta=0,00590** → `mirror_effect = −0,00140`, p=0,402. A
  sobreposição direta é até **maior** que a reversa — não há espelhamento; é coincidência de
  vocabulário de mesma seção (~0,5%, nível de ruído).
- palindromo de página: obs=0,00585 < nulo=0,00686, p=0,914 → páginas não são palíndromos.

O falso positivo evaporou. Mesmo padrão do capstone R61 (o cross-check pego pela pré-registração
cega). Este é o método funcionando.

## 6. Veredito e priores

**`leonardo_operations_degenerate`.** Espelho, reverso, R→L e páginas-espelhadas são
reparametrizações de duas coisas que já entendemos: (a) morfologia de sufixo intra-palavra
(reproduzida pelo gerador, troca de sinal sob reversão) e (b) layout não-estacionário (LAAFU =
o resíduo conhecido, já mostrado ser layout na R67). Nenhuma toca um eixo novo.

**Priores INALTERADOS: gerador ~70% / construída ~22% / cifra ~8%.** A varredura externa (R66)
e agora a varredura "estilo Leonardo" (R69) só **confirmam a casca**. A direção de leitura é,
por teorema, estatisticamente invisível — então nem pode mover os priores.

**Para o paper de 2025 (Directionality):** nossa leitura é que o "sinal R→L" deles é a assimetria
de borda de palavra (sufixos rígidos à direita ⇒ bordas detectáveis pela direita), que é
**idêntica** ao que um gerador templático L→R de slots produz, com **zero** bits de direção de
leitura transmitidos. O controle que adjudica é o reverso-por-token: ele troca o sinal e preserva
a magnitude — diagnóstico de artefato.

## 7. O que sobra (e não muda)

A incerteza restante é a mesma de R68: **proveniência / material / chave**, não estatística.
Só duas coisas moveriam o eixo "tem sentido?": uma **chave histórica** documentada, ou um
**decode held-out** que prediga texto não visto. Nenhuma operação direcional/visual fornece isso.

## Artefatos

- `scripts/analyze_directionality_mirror.py` — análise (medidas A–D + árbitro gerador).
- `tests/test_directionality_mirror.py` — 12 testes (primitivas + invariância por reversão +
  flip de `dir_edge` + veredito degenerado).
- `data/derived/directionality_summary_zl3b.csv` — sumário métrica→valor.
- `data/derived/directionality_corpora_zl3b.csv` — tabela por corpus (real/reverso/shuffle/gerador).

Guardrail em todas as saídas: `rota69_directionality_mirror_not_decipherment`.
```
[token visível] = casca templática (prefixo→núcleo→sufixo), morfologicamente assimétrica;
a assimetria é de CONSTRUÇÃO (de que lado fica o sufixo), não de DIREÇÃO DE LEITURA.
```
```
