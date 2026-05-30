# Rota 64: com 3× mais dados, os rótulos seguem sendo desacoplados do objeto

Guardrail: `rota64_cross_modal_not_decipherment`.

A R63 foi um piloto subpotente (6 fólios, n=59) que sugeriu rótulos DESACOPLADOS do tipo de
objeto. A R64 **ampliou a cobertura de imagem** para dar potência: baixei 12 novos fólios IIIF
de alta-res da Beinecke (manifesto cached → `collections.library.yale.edu/iiif/2/{id}`) e
re-rodei o mesmo teste controlado-por-fólio. Combinado: **n=171 across 12 fólios** (~3×).

## Cobertura (correção honesta)

Dos 12 novos fólios, só **7 carregam loci de rótulo** em ZL3b. As páginas f93r–f96v, que eu
supus "farmacêuticas", são na verdade **herbais com texto de parágrafo apenas — zero `@L`**.
O visual-annotator codificou todo fólio com rótulos: **+112 elementos** (f100r 17, f73r 29,
f88r 15, f89v 23, f71r 15, f100v 13). Classes coarse combinadas: organ 81, figure 48 (nymph
44 + roundel 4), whole_plant 17, vessel 15, sky 9. **59% incertos** (anéis de zodíaco lotados;
pareamento rótulo↔parte-de-planta médio) → testes rodados em todas as linhas E no subconjunto
não-incerto (n=70).

## Headline — feature × tipo-de-objeto, controlado por fólio

| subconjunto | melhor feature | V | p_global | **p_within_folio** |
|-------------|----------------|---|----------|--------------------|
| todas (n=171) | gallows_present | 0.354 | 0.0003 | **0.054** (quase) |
| não-incerto (n=70) | length_bucket | 0.420 | — | 0.020 |

**Nenhuma feature é <0.05 nos DOIS subconjuntos.** Os V globais grandes (gallows p_global=
0.0003) **colapsam sob o controle de fólio** — confirmando, agora com potência, que eram
artefatos de vocabulário de seção/fólio (o confundidor que a R63 pré-registrou). **O
desacoplamento HOLDS com mais dados.**

## Sub-teste A — farmacêutico: jarro vs órgão (n=74)

Um sinal real e modesto SOBREVIVE ao controle de fólio: `length_bucket` V=0.345,
**p_within_folio=0.0063** (sobrevive Bonferroni de 7 features). **Rótulos de jarro nunca são
curtos** (skew longo/médio); rótulos de órgão-de-planta cobrem todos os comprimentos. É uma
assimetria estrutural genuína de **comprimento** — NÃO uma nomeação nem tradução; rótulos de
recipiente simplesmente tendem a palavras mais longas.

## Sub-teste B — ninfas: o rótulo é FÓLIO-LOCAL, não nome do objeto

Os 2 fólios de zodíaco dão ~44 rótulos sobre um tipo quase-constante (ninfa-com-estrela) — o
teste perfeito de "o mesmo objeto recebe um nome consistente?". Resultado:
- Ninfas SÃO estruturadas (is_nymph prevê `prefix4`, V=0.31, p=0.0067).
- MAS o perfil de rótulo **DIVERGE entre os fólios** (f71r = ot-/t-gallows/longo; f73r =
  ok-/k-gallows): divergência=0.265, **p=0.0113** (98.9º percentil do nulo de embaralhamento).

**Um nome verdadeiro casaria entre fólios; não casa.** O rótulo da ninfa é governado pelo
FÓLIO/escriba, não pelo objeto desenhado. Isto é evidência positiva limpa para o modelo
escriba/gerador: até os rótulos são condicionados ao escriba, não ao referente.

## Veredito

**`decoupled` (agora com potência, n=171).** A estrutura do rótulo NÃO corresponde ao tipo de
objeto além do confundidor de fólio; o mesmo objeto (ninfa) recebe rótulos fólio-locais
diferentes. Estende e CONFIRMA o desacoplamento texto↔imagem (R57) ao regime de rótulo. O
único correlato cross-modal real é uma assimetria de COMPRIMENTO jarro-vs-órgão (estrutura,
não sentido). Firma o prior geral (texto não descreve as imagens; sistema escriba/gerador,
gerador ~70%).

**Ressalva:** 59% das anotações são incertas; mas a convergência (headline nulo nos dois
subconjuntos + ninfa fólio-local) torna o desacoplamento a leitura robusta, não mais um piloto.

## Onde isto deixa a frente visual

A questão cross-modal "os rótulos nomeiam o que está desenhado?" está **respondida: não** — no
nível da palavra (R57) e do rótulo (R63→R64, com potência). A imagem e o texto são sistemas
desacoplados. Avançar a pergunta "o texto tem sentido?" exige evidência de
**proveniência/material**, não mais correlação corpus↔imagem.

Guardrail: `rota64_cross_modal_not_decipherment`.
Script/testes: `scripts/analyze_cross_modal.py` / `tests/test_cross_modal.py` (suíte **524**).
Imagens: `images/raw/yale_iiif_r64/` (12 fólios). Anotação: `data/derived/rota64_cross_modal_labels_zl3b.csv`
(112 elementos). Saídas: `data/derived/cross_modal_{test,summary}_combined_zl3b.csv`.
