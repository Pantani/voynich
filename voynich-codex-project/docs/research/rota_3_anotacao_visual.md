# Rota 3: preparacao da anotacao visual

Este arquivo prepara a anotacao visual manual sem preencher campos por suposicao. A lista abaixo foi ranqueada a partir da tabela contextual e dos controles da Rota 2.

Fonte: `voynich-codex-project/data/derived/border_matrix_context_zl3b.csv`.
Candidatos selecionados: 160.
Folios cobertos: f101v, f102v2, f57v, f66r, f67r1, f67r2, f67v1, f67v2, f68r1, f68r2, f68r3, f68v1, f68v3, f69r, f69v, f70r1, f70r2, f70v1, f70v2, f71r, f71v, f72r1, f72r2, f72r3, f72v1, f72v2, f72v3, f73r, f73v, f75v, f77r, f77v, f80r, f82r, f82v, f84r, f85r2, f86v4, f88r, f88v, f89r2, f99r, f99v, fRos.

CSV de trabalho:

- `data/annotations/visual_annotation_candidates_zl3b.csv`

## Como anotar

Preencher manualmente, olhando a imagem do folio:

- `image_checked`: `yes` quando a imagem foi conferida;
- `image_file_or_url`: arquivo local ou URL usada;
- `ink_color`: marrom, vermelho, azul, verde etc.;
- `visual_zone`: anel, setor, raio, margem, rótulo, corpo do paragrafo;
- `ring`, `sector`, `radius`: quando aplicavel;
- `object_nearby`: estrela, lua, planta, recipiente, figura, linha radial etc.;
- `visual_notes`: observacao curta sem interpretar como traducao;
- `annotation_confidence`: baixa, media ou alta.

## Primeiros candidatos

|score|folio|locus|kind|token|suffix|status|line_position|
|---:|---|---|---|---|---|---|---|
|16|f67r1|f67r1.6,+Cc|C|otar|ar|exact|middle|
|16|f70v2|f70v2.21,@Cc|C|otar|ar|exact|middle|
|15|f67r1|f67r1.5,@Cc|C|ar|ar|standalone|middle|
|15|f67r1|f67r1.6,+Cc|C|ar|ar|standalone|middle|
|15|f70r2|f70r2.16,+Cc|C|otar|ar|exact|start|
|15|f70v2|f70v2.21,@Cc|C|ar|ar|standalone|middle|
|15|f70v2|f70v2.32,@Cc|C|ar|ar|standalone|middle|
|15|f70v2|f70v2.32,@Cc|C|otal|al|exact|start|
|15|f72r1|f72r1.12,@Cc|C|qokar|ar|exact|end|
|15|f72v1|f72v1.22,@Cc|C|otar|ar|exact|start|
|15|f67r2|f67r2.10,&L0|L|okar|ar|exact|end|
|15|f67r2|f67r2.22,+L0|L|okal|al|exact|single|
|15|f67r2|f67r2.3,&L0|L|okar|ar|exact|end|
|15|f67r2|f67r2.57,&Ls|L|otar|ar|exact|start|
|15|f68r1|f68r1.25,@Ls|L|otol|ol|exact|single|
|15|f68r1|f68r1.26,@Ls|L|otor|or|exact|single|
|15|f70v2|f70v2.16,&Lz|L|otal|al|exact|start|
|15|f70v2|f70v2.22,@Lz|L|otar|ar|exact|start|
|15|f70v2|f70v2.23,&Lz|L|otar|ar|exact|start|
|15|f70v2|f70v2.4,&Lz|L|otar|ar|exact|single|
|15|f88v|f88v.12,@Lf|L|otor|or|exact|start|
|15|f88v|f88v.4,@Lf|L|otar|ar|exact|start|
|15|f99r|f99r.2,@Lf|L|okar|ar|exact|start|
|15|f99r|f99r.8,@Lf|L|okor|or|exact|single|
|15|f99v|f99v.27,@Lf|L|otal|al|exact|single|
|15|f67v2|f67v2.16,@Ri|R|okar|ar|exact|start|
|15|f68r3|f68r3.5,@Ri|R|qokol|ol|exact|start|
|14|f57v|f57v.2,@Cc|C|qokar|ar|exact|middle|
|14|f67r1|f67r1.5,@Cc|C|otor|or|exact|middle|
|14|f68r2|f68r2.31,@Cc|C|okol|ol|exact|middle|
|14|f68r3|f68r3.22,@Cc|C|okol|ol|exact|middle|
|14|f69v|f69v.1,@Cc|C|okar|ar|exact|middle|
|14|f70r1|f70r1.13,@Cc|C|otar|ar|exact|middle|
|14|f70r2|f70r2.15,@Cc|C|okar|ar|exact|middle|
|14|f71v|f71v.1,@Cc|C|otar|ar|exact|middle|
|14|f72r1|f72r1.12,@Cc|C|otar|ar|exact|middle|
|14|f72r2|f72r2.6,@Cc|C|otar|ar|exact|middle|
|14|f72r3|f72r3.1,@Cc|C|okar|ar|exact|middle|
|14|f72v1|f72v1.1,@Cc|C|otar|ar|exact|middle|
|14|f72v2|f72v2.20,@Cc|C|ar|ar|standalone|end|

## Criterio de selecao

- priorizar `C`, `R`, `L` e rubricas;
- priorizar tokens exatos e valores standalone;
- priorizar familias `ok/ot/qok` e valores `ar/al/or/ol`;
- dar leve bonus a folios que ja estao nos manifests de imagem;
- nao preencher nenhum campo visual automaticamente.

## Primeira anotacao executada

Arquivo preenchido:

- `data/annotations/visual_annotations_seed_zl3b.csv`

Relatorio:

- `docs/rota_3_primeira_anotacao_visual.md`
- `docs/rota_3_cruzamento_visual.md`

Resumo:

- 56 anotacoes preenchidas;
- folios: `f67r1`, `f67r2`, `f67v2`, `f68r1`, `f68r2`, `f68r3`, `f70v2`, `f84r`, `f88v`, `f99v`;
- zonas: 23 circulares, 19 rotulos, 10 paragrafos/texto corrido, 4 radiais;
- confianca: 42 medias, 14 baixas.

Observacao: os campos foram preenchidos apenas para imagens conferidas localmente. Alguns folios entram por preview suplementar, com baixa confianca quando a palavra exata nao foi isolada.

Etapa seguinte executada:

- `docs/rota_4_eixos_matriz.md`;
- `data/derived/matrix_axis_summary_zl3b.csv`.
