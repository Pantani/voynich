# Rota 9: revisao manual assistida

Esta rota prepara uma folha de revisao para coordenadas mais apertadas. Ela nao confirma glifos automaticamente.

Fonte: `voynich-codex-project/data/annotations/crop_review_decisions_zl3b.csv`.
CSV de trabalho: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/manual_svg_review_zl3b.csv`.
HTML de revisao: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/docs/rota_9_revisao_manual.html`.

## Resultado curto

- itens para revisar: 11;
- campos de coordenada foram deixados vazios de proposito;
- status inicial: `pending_manual_review` para todos os itens;
- prioridade: `ot`, depois `ch/d`, depois `standalone`.

### Familias na fila

|item|n|
|---|---:|
|standalone|5|
|ch|3|
|ot|2|
|d|1|

### Status inicial

|item|n|
|---|---:|
|pending_manual_review|11|

## Ordem de revisao

|manual|decisao|crop|familia|folio|locus|tokens|faltam|
|---|---|---|---|---|---|---|---|
|R9-001|R8-009|R7-009|ot|f67r1|f67r1.5,@Cc|otardar otor|otardar|
|R9-002|R8-010|R7-010|ot|f70v2|f70v2.21,@Cc|otar oteedar oteeeor|oteedar oteeeor|
|R9-003|R8-001|R7-001|d|f67r1|f67r1.6,+Cc|dal dar dol|dol|
|R9-004|R8-005|R7-005|ch|f67r1|f67r1.6,+Cc|chedar cheol cheor chol|chedar cheol cheor|
|R9-005|R8-006|R7-006|ch|f68r3|f68r3.1,@Cc|cheor chodal chokol chol|cheor chodal chokol|
|R9-006|R8-007|R7-007|ch|f70v2|f70v2.1,@Cc|chokear chol cholkal|chokear cholkal|
|R9-007|R8-008|R7-008|standalone|f70v2|f70v2.32,@Cc|al ar|al|
|R9-008|R8-011|R7-011|standalone|f84r|f84r.23,+P0|ol or|ol|
|R9-009|R8-002|R7-002|standalone|f67r1|f67r1.5,@Cc|ar ol||
|R9-010|R8-004|R7-004|standalone|f67r1|f67r1.6,+Cc|al ar||
|R9-011|R8-003|R7-003|standalone|f84r|f84r.14,+P0|ol or||

## Como preencher

- Use `manual_tighter_x/y/width/height` apenas quando uma regiao menor for realmente visivel.
- Use `manual_final_status=confirmed_tighter_region` somente para regiao melhorada, nao para significado.
- Use `manual_final_status=keep_not_isolated` se a palavra exata nao puder ser isolada.
- Nao transformar coordenada visual em traducao.
