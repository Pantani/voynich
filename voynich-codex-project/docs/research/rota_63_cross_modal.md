# Rota 63: os RÓTULOS também são desacoplados da imagem (piloto cross-modal)

Guardrail: `rota63_cross_modal_not_decipherment`.

**Primeira rota da FRENTE VISUAL** (pivô de domínio após a linha estatística fechar na R62).
A R57 mostrou que o texto e a imagem são desacoplados no nível da PALAVRA (prosa não nomeia
desenhos), mas não pôde testar o **regime de RÓTULO** — tokens curtos colocados SOBRE objetos
desenhados, que vivem nas seções farmacêutica e astronômica. Esta rota testa: **a ESTRUTURA
de um token-rótulo corresponde ao TIPO VISUAL do objeto que ele rotula?** (A) sim → primeiro
elo texto↔imagem / rótulo-como-nome; (B) não → rótulos também desacoplados.

## Método (pipeline do harness)

- **visual-annotator** leu 6 fólios IIIF de alta resolução (farmacêuticos f88v/f89r2/f99r/f99v,
  astronômicos f67r2/f67v1) e codificou **59 elementos** desenhados: tipo visual do objeto
  (codificado INDEPENDENTE do token, sem circularidade) + o token-rótulo da transcrição. 46%
  marcados `uncertain` (honesto: o pareamento rótulo↔parte-de-planta é médio; rótulos de jarro
  `Lc` são de alta confiança). Saída: `data/derived/rota63_cross_modal_labels_zl3b.csv`.
- **cryptanalyst** pré-registrou CEGO: prior 65% B / 35% A; exigiu que qualquer sinal
  sobrevivesse a um embaralhamento **DENTRO do fólio** (não só global).
- **corpus-statistician** testou V(feature × classe-de-objeto) com nulo de permutação.

**O confundidor crítico (pré-registrado):** o tipo de objeto é quase DETERMINADO pelo fólio
(farmacêutico=raízes/jarros, astro=estrelas), e fólios diferem em inventário E vocabulário de
rótulo. Logo um V global re-mede vocabulário de seção — sinal espúrio. **O sinal real precisa
sobreviver ao embaralhamento DENTRO do fólio** (análogo ao controle de Currier da linha textual).

## Resultado — desacoplado (piloto)

Classes coarse: organ {folha/raiz/caule/flor/spray}, whole_plant, vessel {jarro}, sky
{estrela/roundel}. Features: first_glyph, prefix4, gallows, length, nucleus, vogal.

| feature | V | p_global | **p_within_folio** |
|---------|---|----------|--------------------|
| prefix4 | 0.39 | 0.092 | **0.258** |
| first_glyph | 0.38 | 0.40 | 0.79 |
| length_bucket | 0.19 | 0.64 | 0.36 |
| nucleus ch/sh | 0.19 | 0.54 | 0.50 |

**Nenhuma feature bate o nulo dentro-do-fólio** (nem em todas as 59 linhas, nem no subconjunto
não-incerto de 32). Os sinais globais modestos (prefix4 p_global=0.092) são confundidores de
vocabulário de fólio/seção — exatamente como pré-registrado. O único p<0.05 (length_bucket
p_within=0.049) aparece SÓ no subconjunto não-incerto e NÃO em todas as linhas → ruído isolado
em n=32.

**Contraste mais limpo (controlado por fólio): jarro vs órgão dentro do farmacêutico**
(n=39, 6 jarros / 33 partes-de-planta): melhor feature gallows_class, **V=0.42 mas
p_within_folio=0.10** — a diferença estrutural aparente entre rótulos-de-jarro e
rótulos-de-planta NÃO sobrevive ao embaralhamento dentro dos mesmos fólios.

**Veredito: `decoupled_pilot`.** Removido o confundidor de fólio, a estrutura do rótulo NÃO
corresponde ao tipo de objeto. Os rótulos parecem desacoplados também — estendendo o
desacoplamento texto↔imagem da R57 ao regime de rótulo, o lugar mais provável para uma função
de nomeação.

## Ressalvas (honestas)

1. É um **PILOTO subpotente** (n=59, 46% incerto). Um nulo NÃO prova B — só falha em achar A.
2. O pareamento rótulo↔elemento para partes-de-planta é de confiança média; só os jarros
   (`Lc`) são de alta confiança.
3. O resultado é consistente com R57 e com o veredito geral (texto não descreve as imagens),
   e firma levemente o prior B; não o prova.

## Próximo passo

Para sair do nível de piloto, a frente visual precisa de **mais cobertura de imagem**: baixar
mais fólios IIIF rotulados (farmacêuticos e herbais com rótulos claros) e repetir o teste com n
adequado e o controle dentro-do-fólio. Alternativa: se aparecer qualquer sinal com mais dados,
testar se o MESMO tipo de objeto recebe rótulo consistente ENTRE fólios (nomeação verdadeira)
vs local-ao-fólio.

Guardrail: `rota63_cross_modal_not_decipherment`.
Script: `scripts/analyze_cross_modal.py`; testes: `tests/test_cross_modal.py` (suíte **506**).
Anotação: `data/derived/rota63_cross_modal_labels_zl3b.csv`.
Saídas: `data/derived/cross_modal_{test,summary}_zl3b.csv`.
