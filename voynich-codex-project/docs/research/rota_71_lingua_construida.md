# Rota 71 — A hipótese de língua construída (*lingua ignota*): posicionamento

Guardrail: `rota71_constructed_language_not_decipherment`.
Guardrail global: esta rota posiciona uma **HIPÓTESE** contra o ledger fechado
(R43–R70). Ela **não mede nada novo** no corpus (a linha estatística está exaurida
desde a R62) e **não atribui sentido** a nenhum token Voynichês. É uma função-síntese
dos vereditos já estabelecidos.

## Sumário executivo

O usuário perguntou se o manuscrito poderia ser uma *lingua ignota*. A resposta
honesta não é sim/não: ela se **reparte** dentro do prior congelado. O termo tem
dois sentidos, e eles caem em ramos diferentes do estado fechado:

1. **Sentido amplo — sistema/notação construída** (`H_amplo`): um sistema de signos
   artificial, desenhado por alguém. É o ramo **`construída ~22%`** do prior — e
   também a família a que o **gerador content-free ~70%** pertence (um gerador É um
   sistema construído).
2. **Sentido estrito — o modelo de Hildegard von Bingen** (`H_Hildegard`): a *Lingua
   Ignota* do séc. XII, um vocabulário inventado **glosado** (lista de substantivos
   legível PORQUE traz glosas latim/alemão).

**Veredito** (função pura das contagens): **`constructed_family_alive_hildegard_excluded_frozen`**.

- **`H_amplo` está VIVO** — sustentado por 5 critérios, enfraquecido por 0. Nada no ledger o refuta; é o segundo ramo
  sobrevivente do prior.
- **`H_Hildegard` está ENFRAQUECIDO** — enfraquecido por 4 critérios contra 3 que o sustentam. O modelo glosado/nomenclator
  é justamente o que as rotas R57/R63–65/R68 já tiraram de cima da mesa.
- **Nenhum dos dois é confirmável por estatística** (`confirmable_by_corpus_statistics=False`): o gerador da R62/R67 reproduz 14/14 assinaturas,
  então um sistema construído COM conteúdo é indistinguível de um SEM conteúdo na
  escala do token.

## As duas hipóteses, lado a lado

| | `H_amplo` (sistema construído) | `H_Hildegard` (Lingua Ignota glosada) |
|---|---|---|
| Unidade | operadores + matriz (combinatória) | substantivos inventados (lista) |
| Glosa/chave | não exigida | **central** (é o que a torna legível) |
| Nomeia objetos? | não precisa | **sim** (palavra↔coisa) |
| Escala | milhares de *types* | ~1000 itens, dominados por nomes |
| Status no ledger | **vivo (~22%)** | **enfraquecido/excluído** |

## Scorecard (síntese dos vereditos anteriores)

verdito codicológico (R68, lido ao vivo): **interleaved_production**.

| Critério | Fonte | Achado estabelecido | H_amplo | H_Hildegard |
|---|---|---|---|---|
| `designed_combinatorial_morphology` | R43-R55 | token is 100% functional: qo-/ok-/ot- operators + ar/al/or/ol matrix | **sustenta** | **neutro** |
| `syntax_thin_bag_of_words` | R60 | compresses like its own bag-of-words; order info ~1-3% vs natural 12-25% | **sustenta** | **sustenta** |
| `not_natural_prose` | R58 | h2=2.15, far below natural prose; not random noise either | **sustenta** | **sustenta** |
| `morph_rich_syntax_fine` | R59 | I(d) drops to floor at d~15 (token scale); no mid-range syntax | **sustenta** | **neutro** |
| `nomenclator_excluded` | R57 | nomenclator (label-is-a-name) hypothesis discarded | **neutro** | **enfraquece** |
| `label_object_decoupled` | R63-R65 | label<->object decoupled_refined (powered, no confirmation bias) | **neutro** | **enfraquece** |
| `no_gloss_no_parallel_key` | R68 | no gloss / no parallel text; documented key/crib (#1) not known | **neutro** | **enfraquece** |
| `lexicon_scale_morphology` | R59 | thousands of word types, morphology-rich (not a ~1000-item noun list) | **neutro** | **enfraquece** |
| `serious_deliberate_production` | R68 | blocked p=0.000999, 5 hands, V(hand x Currier)=0.9801, verdict=interleaved_production | **sustenta** | **sustenta** |
| `contentfree_generator_reproduces_signatures` *(limita confirmação)* | R62/R67 | a local content-free generator reproduces 14/14 statistical signatures | **neutro** | **neutro** |

Contagens: `H_amplo` sustenta=5 / enfraquece=0 / neutro=5; `H_Hildegard` sustenta=3 / enfraquece=4 / neutro=3.

## Veredito como função pura dos booleanos

- `family_alive = (broad_weakens == 0)` → **True**
- `hildegard_weakened = (hildegard_weakens > hildegard_supports)` → **True**
- `confirmable_by_corpus_statistics = (nenhum critério limita confirmação)` → **False**
- `classify_verdict(...)` → **`constructed_family_alive_hildegard_excluded_frozen`**

## O que confirmaria — e o que já enfraquece

**Só duas evidências movem isto, e nenhuma é estatística** (tabela de decisão da R68):

- **#1 documented key/crib (a key => cipher; a grammar+lexicon => constructed language)** — é a *única* que também separa **construída de cifra**.
- **#6 reproducible decode that predicts held-out (unseen) folios**.

**Já pesou contra o modelo de Hildegard** (e não vai mudar sem evidência externa):
nomenclator excluído (R57), rótulo↔objeto desacoplado (R63–65), ausência de glosa/chave
(R68) e escala/morfologia incompatíveis com uma lista de substantivos (R59).

## Regra de ouro

positions the constructed-language hypothesis against the closed ledger; encodes prior-route verdicts; computes NO new corpus statistic; assigns NO meaning to any token.

Prior **CONGELADO**: generator ~70% / constructed ~22% / cipher ~8%. Esta rota **não move o ponteiro** — apenas
torna explícito e checável como a pergunta da *lingua ignota* se reparte sobre ele.
Não é uma decifração.

Guardrail: `rota71_constructed_language_not_decipherment`.