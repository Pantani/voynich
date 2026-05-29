# Rota 55: o teste de par mínimo — ch/sh é LÉXICO, não conteúdo nem alografia

Guardrail: `rota55_minpair_not_decipherment`.

As Rotas 52–53 levantaram a hipótese mais promissora do projeto: o banco ch/sh seria o
primeiro elemento "de conteúdo" do token (segue a SEÇÃO, V=0.14, p≈0.002). A Rota 54 já
temperou isso. A Rota 55 aplica o **teste decisivo** e fecha a questão.

## Desenho — par mínimo por troca de banco

Um **esqueleto** = um token com o banco substituído por `#` (`chol`→`#ol`, `shol`→`#ol`).
Um esqueleto é **par mínimo** se ocorre TANTO com forma-ch QUANTO com forma-sh.

A sacada: dentro de um esqueleto fixo, **todo vizinho IN-TOKEN é constante por
construção** — só o banco muda. Logo, a única coisa que pode variar entre ocorrências e
"explicar" a escolha do banco é EXTERNA: a SEÇÃO, o TOKEN ANTERIOR ou a POSIÇÃO na linha.
Mede-se a informação mútua condicional `I(banco ; X | esqueleto)` em bits — quanto X
informa sobre o banco, *já sabendo a palavra*.

O cryptanalyst pré-registrou os três veredictos CEGO aos números, com prior em
**(c) léxico-fixo** (porque a R54 já feria a história de conteúdo limpo).

## Resultado — ADEQUADAMENTE DIMENSIONADO

- Esqueletos de par mínimo: **570**
- Tokens de par mínimo: **10 855** (= **74%** de todos os 14 594 tokens ch/sh)

Pares mínimos são ABUNDANTES — o mesmo esqueleto toma os dois bancos o tempo todo. O
teste tem poder de sobra (limiar pré-registrado de inconclusividade: <300 tokens).

| X (condicionado ao esqueleto) | I (bits) | p de permutação |
|-------------------------------|----------|-----------------|
| Seção | 0.1239 | **1.0** |
| Char anterior | 0.1411 | **1.0** |
| Posição na linha | 0.0537 | — |

**Veredito: `lexically_fixed`.** Nenhuma das forças externas informa sobre o banco uma
vez que a palavra (esqueleto) é conhecida.

### Por que p=1.0 é o achado (não um bug)

A informação mútua condicional é **enviesada para cima** quando o condicionante (esqueleto)
tem muitos valores: cada cela (esqueleto, X) tem poucas amostras, gerando associação
espúria. A permutação mede exatamente esse piso de viés — embaralhar X produz I ≥ observado
em 100% das vezes. Como seção é quase **colinear** com esqueleto (palavras se agrupam por
tópico), condicionar no esqueleto já absorve a informação de seção; o resíduo (0.124 bits)
é puro viés. O teste sintético confirma que a métrica discrimina: quando a seção *de fato*
determina o banco dentro de um esqueleto, I_seção = H(banco|esqueleto) e p<0.05.

## Evidência descritiva independente (não depende do argumento de viés)

Para os pares mínimos do topo, a forma-ch e a forma-sh do MESMO esqueleto vivem na MESMA
seção dominante (~74% dos esqueletos):

| esqueleto | n_ch | n_sh | seção-ch | seção-sh |
|-----------|------|------|----------|----------|
| `#edy` | 501 | 432 | balneológico | balneológico |
| `#ol` | 382 | 174 | herbal | herbal |
| `#or` | 199 | 90 | herbal | herbal |
| `#y` | 170 | 97 | herbal | herbal |
| `#ckhy` | 131 | 56 | balneológico | balneológico |
| `qot#y` | 61 | 5 | herbal | herbal |

O banco **não move a seção**. `chol` e `shol` são ambos do herbal; `chedy` e `shedy`
ambos do balneológico. Onde diferem (`#ey`, `#eor`), é entre seções vizinhas do corpus B,
nunca o split limpo ch=herbal / sh=balneológico que "conteúdo" exigiria.

## Síntese — o que isto resolve (Rotas 52–55)

> **ch/sh é essencialmente uma propriedade da PALAVRA (léxico), não um marcador de
> conteúdo produtivo nem uma alternância fonológica/posicional.** A correlação de seção da
> Rota 53 é **frequência de vocabulário topical**: seções diferentes usam palavras
> diferentes, e essas palavras carregam suas próprias tendências ch/sh. É um efeito
> ENTRE-palavras (qual palavra aparece onde), não DENTRO-da-palavra (uma regra geradora).

Isto reconcilia toda a série:
- R53: ch/sh segue seção — **sim, mas por vocabulário**, não por regra ch↔sh.
- R54: sinal na prosa, não em rótulos; acopla ao operador — ambos são propriedades lexicais.
- R55: dentro do esqueleto fixo, nada externo governa o banco → léxico-fixo.

**Implicação honesta:** o fio "ch/sh = primeira camada lexical/de conteúdo" das Rotas
52–53 **não sobrevive ao teste decisivo**. ch/sh não é um pé-de-apoio para decifração — é
ortografia embutida nas palavras. Resultado negativo valioso: redireciona o esforço.

> **Atenção ao modelo:** todo o token (casca qo-/ok-ot/a-o/r-l + núcleo ch/sh) é agora
> marcação funcional/lexical SEM camada de conteúdo produtivo identificada. A questão
> estratégica passa a ser: **onde está o conteúdo, se está em algum lugar?** — no nível da
> PALAVRA INTEIRA (quais tokens são diagnósticos de seção), não dentro do token.

O método do harness (pré-registro cego) foi decisivo: o prior (c) do cryptanalyst bateu
com os dados, e a fan-out de 2 agentes pegou o que um passe único de confirmação esconderia.

## Rota 56 — próxima frente

1. **Estabilidade do banco por esqueleto** (proposto pelo cryptanalyst): regredir a razão
   ch/sh por esqueleto sobre MÃO/quire vs seção. Estável entre mãos + seção mediada só por
   frequência de esqueleto → grafia fixa por palavra. Deriva por mão → distinção
   escriba-idiossincrática (decorativa).
2. **Virar para o nível de PALAVRA**: quais tokens inteiros são diagnósticos de seção
   (V por token), há um "vocabulário de tópico"? É aí que o conteúdo estaria, se existe.

Guardrail: `rota55_minpair_not_decipherment`.
