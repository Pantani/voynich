# Rota 8: revisao dos recortes

Esta rota registra a decisao conservadora para cada recorte da Rota 7. Ela valida os SVGs e separa regiao revisavel de coordenada de glifo confirmada.

Fonte: `voynich-codex-project/data/annotations/review_crop_manifest_zl3b.csv`.
CSV de decisoes: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/crop_review_decisions_zl3b.csv`.

## Resultado curto

- recortes avaliados: 11;
- decisoes `keep_not_isolated`: 11;
- SVGs validos: 11;
- nenhuma coordenada de glifo foi confirmada.

### Decisoes

|item|n|
|---|---:|
|keep_not_isolated|11|

### Status dos SVGs

|item|n|
|---|---:|
|svg_ok|11|

### Tokens faltantes

|item|n|
|---|---:|
|missing_tokens_remain|8|
|no_missing_group_tokens|3|

## Decisoes por recorte

|decisao|crop|review|folio|locus|tokens|faltam|svg|resultado|
|---|---|---|---|---|---|---|---|---|
|R8-001|R7-001|R6-001|f67r1|f67r1.6,+Cc|dal dar dol|dol|svg_ok|keep_not_isolated|
|R8-002|R7-002|R6-002|f67r1|f67r1.5,@Cc|ar ol||svg_ok|keep_not_isolated|
|R8-003|R7-003|R6-003|f84r|f84r.14,+P0|ol or||svg_ok|keep_not_isolated|
|R8-004|R7-004|R6-004|f67r1|f67r1.6,+Cc|al ar||svg_ok|keep_not_isolated|
|R8-005|R7-005|R6-005|f67r1|f67r1.6,+Cc|chedar cheol cheor chol|chedar cheol cheor|svg_ok|keep_not_isolated|
|R8-006|R7-006|R6-006|f68r3|f68r3.1,@Cc|cheor chodal chokol chol|cheor chodal chokol|svg_ok|keep_not_isolated|
|R8-007|R7-007|R6-007|f70v2|f70v2.1,@Cc|chokear chol cholkal|chokear cholkal|svg_ok|keep_not_isolated|
|R8-008|R7-008|R6-008|f70v2|f70v2.32,@Cc|al ar|al|svg_ok|keep_not_isolated|
|R8-009|R7-009|R6-009|f67r1|f67r1.5,@Cc|otardar otor|otardar|svg_ok|keep_not_isolated|
|R8-010|R7-010|R6-010|f70v2|f70v2.21,@Cc|otar oteedar oteeeor|oteedar oteeeor|svg_ok|keep_not_isolated|
|R8-011|R7-011|R6-011|f84r|f84r.23,+P0|ol or|ol|svg_ok|keep_not_isolated|

## Leitura provisoria

- Os recortes sao validos como regioes revisaveis, mas continuam amplos demais para confirmar palavra/glifo.
- O status `not isolated` permanece para todos os itens.
- A proxima etapa deve ser uma revisao manual assistida: marcar coordenadas mais apertadas dentro dos SVGs ou registrar que o token nao pode ser isolado nessa imagem.
