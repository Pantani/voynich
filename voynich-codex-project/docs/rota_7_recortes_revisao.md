# Rota 7: recortes de revisao

Esta rota gera recortes aproximados para revisao visual. Os SVGs apenas enquadram regioes provaveis; eles nao confirmam a palavra exata.

Fonte: `voynich-codex-project/data/annotations/glyph_review_queue_zl3b.csv`.
Manifesto: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/review_crop_manifest_zl3b.csv`.

## Resultado curto

- recortes SVG gerados: 11;
- escopo dos recortes: `rough_region_only`;
- nenhuma coordenada foi tratada como glifo confirmado.

### Status preservado

|item|n|
|---|---:|
|needs_exact_glyph_isolation|11|

### Folios

|item|n|
|---|---:|
|f67r1|5|
|f70v2|3|
|f84r|2|
|f68r3|1|

## Recortes

|crop|review|folio|locus|tokens|faltam|status|arquivo|
|---|---|---|---|---|---|---|---|
|R7-001|R6-001|f67r1|f67r1.6,+Cc|dal dar dol|dol|needs_exact_glyph_isolation|`images/derived/review_crops/R7-001_R6-001_f67r1.svg`|
|R7-002|R6-002|f67r1|f67r1.5,@Cc|ar ol||needs_exact_glyph_isolation|`images/derived/review_crops/R7-002_R6-002_f67r1.svg`|
|R7-003|R6-003|f84r|f84r.14,+P0|ol or||needs_exact_glyph_isolation|`images/derived/review_crops/R7-003_R6-003_f84r.svg`|
|R7-004|R6-004|f67r1|f67r1.6,+Cc|al ar||needs_exact_glyph_isolation|`images/derived/review_crops/R7-004_R6-004_f67r1.svg`|
|R7-005|R6-005|f67r1|f67r1.6,+Cc|chedar cheol cheor chol|chedar cheol cheor|needs_exact_glyph_isolation|`images/derived/review_crops/R7-005_R6-005_f67r1.svg`|
|R7-006|R6-006|f68r3|f68r3.1,@Cc|cheor chodal chokol chol|cheor chodal chokol|needs_exact_glyph_isolation|`images/derived/review_crops/R7-006_R6-006_f68r3.svg`|
|R7-007|R6-007|f70v2|f70v2.1,@Cc|chokear chol cholkal|chokear cholkal|needs_exact_glyph_isolation|`images/derived/review_crops/R7-007_R6-007_f70v2.svg`|
|R7-008|R6-008|f70v2|f70v2.32,@Cc|al ar|al|needs_exact_glyph_isolation|`images/derived/review_crops/R7-008_R6-008_f70v2.svg`|
|R7-009|R6-009|f67r1|f67r1.5,@Cc|otardar otor|otardar|needs_exact_glyph_isolation|`images/derived/review_crops/R7-009_R6-009_f67r1.svg`|
|R7-010|R6-010|f70v2|f70v2.21,@Cc|otar oteedar oteeeor|oteedar oteeeor|needs_exact_glyph_isolation|`images/derived/review_crops/R7-010_R6-010_f70v2.svg`|
|R7-011|R6-011|f84r|f84r.23,+P0|ol or|ol|needs_exact_glyph_isolation|`images/derived/review_crops/R7-011_R6-011_f84r.svg`|

## Leitura provisoria

- Os recortes agora tornam a revisao visual reproduzivel por `review_id`/`crop_id`.
- O status `needs_exact_glyph_isolation` foi preservado em todos os itens.
- A proxima etapa deve abrir os SVGs, tentar localizar a palavra exata e registrar coordenadas melhores ou manter `not isolated`.
