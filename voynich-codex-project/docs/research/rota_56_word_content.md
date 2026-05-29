# Rota 56: o conteúdo topical vive na PALAVRA INTEIRA — primeiro sinal positivo (fraco)

Guardrail: `rota56_word_content_not_decipherment`.

**Virada estratégica.** As Rotas 43–55 dissecaram o TOKEN e mostraram que cada peça é
marcação funcional/lexical — culminando na Rota 55, onde o teste de par mínimo provou que
até o núcleo ch/sh é léxico-fixo, NÃO conteúdo. Não há camada de conteúdo DENTRO do token.
Logo: se Voynichês tem conteúdo topical, ele tem de estar no nível da PALAVRA INTEIRA.
Esta rota testa exatamente isso — e, pela primeira vez, encontra sinal positivo.

## Pergunta e controles

**Falsificável:** a identidade da PALAVRA carrega conteúdo de seção ALÉM do que o escriba
(Currier) explica? Métrica: `I(seção ; palavra)` em bits, corrigida por viés contra um
nulo de permutação (MI é positivamente enviesado com muitos tipos — lição da Rota 55).

O cryptanalyst pré-registrou CEGO, com prior em (b) vocabulário-de-escriba (50%), (c)
sem-sinal (30%), (a) vocabulário-topical (20%) — e flagueou DOIS confundidores a controlar.

## Resultado — sobrevive a TODOS os controles, mas atenua à metade

| Teste (within Currier B) | I_norm | nota |
|--------------------------|--------|------|
| (i) bruto, perm por token | 0.096 | p=0.002 |
| (ii) só prosa (locus P), perm por token | 0.095 | locus-tipo NÃO infla |
| (iii) nulo por BLOCO de fólio | 0.069 | nulo ~4× mais largo (corrige LAAFU) |
| **(iv) ESTRITO: prosa + bloco de fólio** | **0.046** | **z≈5.6 sobre o próprio nulo** |

- **Agrupado:** H(seção)=2.335 bits; I_obs=0.896 vs nulo=0.588 (p=0.002); I_norm=0.132.
- **Controle de Currier (within B, multi-seção numa só mão):** I_norm=0.096 — sobrevive.
- **Controle de locus-tipo (só prosa):** I_norm=0.095 — quase idêntico → **não é artefato
  de rótulo vs prosa**.
- **Controle de autocorrelação (nulo por bloco de fólio, preserva repetição intra-fólio):**
  o nulo fica ~4× mais largo e absorve ~metade do efeito → I_norm cai para 0.069, e
  combinado com prosa, **0.046**. Ainda **z≈5.6** acima do nulo conservador (altamente
  significativo; o p=0.002 é só o piso de resolução de 500 permutações).

**Veredito (controlado): `topical_vocabulary`.** O sinal palavra→seção é REAL e robusto,
mas FRACO: ~4.6% da incerteza de seção, dentro de um único escriba, só prosa, sob o nulo
mais conservador. **Metade do efeito bruto era autocorrelação de fólio; o grosso da
associação agrupada é dialeto (A vs B).** O resíduo topical genuíno é pequeno — mas existe.

## Vocabulário diagnóstico (estável sob restrição a prosa)

Top-5 por lift (P(seção|palavra)/P(seção)), só-prosa vs irrestrito — **mesma composição**:

| Seção | palavras diagnósticas (lift) |
|-------|------------------------------|
| Herbal | kchy(3.1) tchy(2.9) cthor(2.9) dchor(2.9) cthy(2.9) |
| Balneológico | olkedy(3.9) olkain(3.9) qol(3.9) olshedy(3.4) olchedy(3.3) |

A vizinhança membro não muda da lista irrestrita para a só-prosa (só encolhe o lift) →
**o vocabulário diagnóstico é propriedade da PROSA, não artefato de rótulos.**

**Marcador vs não-marcador:** palavras qo-/ok-/ot- (n=85) têm diagnosticidade média 0.208
< não-marcadores (n=195) 0.230 — marcadores são mais PLANOS, como a teoria funcional prevê
(fraco, mas na direção certa).

## Interpretação — honesta

> **Primeiro sinal positivo de conteúdo do projeto.** A escolha da PALAVRA é fracamente
> condicionada pelo tópico (seção) além do escriba, da estrutura de locus e da
> autocorrelação de fólio. O conteúdo, se existe, vive onde a dissecção do token (R43–55)
> previu que teria de viver: na identidade da palavra inteira, não nas suas peças.

**Ressalvas (cruciais, não enfeite):**
1. O efeito é PEQUENO (I_norm 0.046 no controle estrito). Não prova "língua com semântica
   conhecida" — prova que a escolha de palavra é fracamente topical.
2. ~Metade do efeito aparente era autocorrelação de fólio; o prior (b)/(c) do cryptanalyst
   estava parcialmente certo (muito do bruto era escriba/confundidor).
3. Compatível tanto com uma língua real de léxico topical fraco QUANTO com um sistema de
   baixo-conteúdo com leve viés topical. Não decide entre os dois — a Rota 57 decide.

## Rota 57 — teste decisivo (cross-modal, proposto pelo cryptanalyst)

Se a palavra carrega conteúdo, as palavras diagnósticas de herbal devem **concentrar-se
nos fólios cujas IMAGENS mostram o conteúdo correspondente** (plantas). Usar o
visual-annotator + crops IIIF: pegar as top palavras herbal-diagnósticas e checar se caem
em fólios com desenho botânico acima do acaso. Aterrissar no conteúdo visual certo →
conteúdo confirmado de forma cross-modal (enorme). Não aterrissar → o sinal é estatístico
mas não-referencial (empurra para baixo-conteúdo). Discriminador limpo.

Guardrail: `rota56_word_content_not_decipherment`.
Script: `scripts/analyze_word_content.py`; testes: `tests/test_word_content.py` (suíte 377).
Saídas: `data/derived/word_section_{diagnostic,summary}_zl3b.csv`.
