# Rota 6: conferencia fina dos glifos

Esta rota pega somente os grupos locais que ja tem anotacao visual direta. Ela nao afirma posicao exata de glifo quando a anotacao anterior so localizou a camada/folio.

Fonte dos grupos: `voynich-codex-project/data/derived/same_context_matrix_pairs_zl3b.csv`.
Fonte visual: `voynich-codex-project/data/annotations/visual_annotations_seed_zl3b.csv`.
CSV de revisao: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/glyph_review_queue_zl3b.csv`.

## Resultado curto

- grupos na fila: 11;
- status dominante: needs_exact_glyph_isolation;
- nenhuma atribuicao semantica nova foi feita nesta rota.

### Status de isolamento

|item|n|
|---|---:|
|needs_exact_glyph_isolation|11|

### Folios na fila

|item|n|
|---|---:|
|f67r1|5|
|f70v2|3|
|f84r|2|
|f68r3|1|

### Arquivos de imagem

|item|n|
|---|---:|
|images/raw/commons_f67r1_r2.jpg|5|
|images/raw/commons_f70v2.jpg|3|
|images/raw/commons_f84r.jpg|2|
|images/raw/commons_f68r1_r2_r3.jpg|1|

## Fila de revisao

|id|score|folio|locus|familia|sufixos|eixo|tokens anotados|faltam|status|acao|
|---|---:|---|---|---|---|---|---|---|---|---|
|R6-001|59|f67r1|f67r1.6,+Cc|d|al ar ol|ao+rl|dal dar|dol|needs_exact_glyph_isolation|locate missing group tokens in image, then crop/zoom all matched tokens|
|R6-002|56|f67r1|f67r1.5,@Cc|standalone|ar ol|ao+rl|ar ol||needs_exact_glyph_isolation|crop/zoom image and isolate exact glyph positions|
|R6-003|56|f84r|f84r.14,+P0|standalone|ol or|rl|ol or||needs_exact_glyph_isolation|crop/zoom image and isolate exact glyph positions|
|R6-004|52|f67r1|f67r1.6,+Cc|standalone|al ar|rl|al ar||needs_exact_glyph_isolation|crop/zoom image and isolate exact glyph positions|
|R6-005|49|f67r1|f67r1.6,+Cc|ch|ar ol or|ao+rl|chol|chedar cheol cheor|needs_exact_glyph_isolation|locate missing group tokens in image, then crop/zoom all matched tokens|
|R6-006|49|f68r3|f68r3.1,@Cc|ch|al ol or|ao+rl|chol|cheor chodal chokol|needs_exact_glyph_isolation|locate missing group tokens in image, then crop/zoom all matched tokens|
|R6-007|49|f70v2|f70v2.1,@Cc|ch|al ar ol|ao+rl|chol|chokear cholkal|needs_exact_glyph_isolation|locate missing group tokens in image, then crop/zoom all matched tokens|
|R6-008|49|f70v2|f70v2.32,@Cc|standalone|al ar|rl|ar|al|needs_exact_glyph_isolation|locate missing group tokens in image, then crop/zoom all matched tokens|
|R6-009|35|f67r1|f67r1.5,@Cc|ot|ar or|ao|otor|otardar|needs_exact_glyph_isolation|locate missing group tokens in image, then crop/zoom all matched tokens|
|R6-010|35|f70v2|f70v2.21,@Cc|ot|ar or|ao|otar|oteedar oteeeor|needs_exact_glyph_isolation|locate missing group tokens in image, then crop/zoom all matched tokens|
|R6-011|35|f84r|f84r.23,+P0|standalone|ol or|rl|or|ol|needs_exact_glyph_isolation|locate missing group tokens in image, then crop/zoom all matched tokens|

## Leitura provisoria

- A Rota 5 achou pares locais; a Rota 6 mostra que a evidencia visual ainda esta em nivel de camada, nao de glifo.
- Todos os itens desta fila devem ser tratados como tarefas de zoom/crop antes de qualquer leitura de eixo.
- Os melhores alvos iniciais sao `f67r1`, `f70v2`, `f68r3` e `f84r`, porque ja possuem imagem local e anotacao media.
- A proxima etapa deve produzir recortes ou coordenadas aproximadas, preservando o status `not isolated` quando a palavra exata nao puder ser localizada.
