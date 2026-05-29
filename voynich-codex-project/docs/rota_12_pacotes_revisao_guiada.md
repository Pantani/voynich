# Rota 12: pacotes por folio para revisao guiada

Esta rota agrupa a fila Rota 11 por folio e imagem fonte. Os pacotes sao unidades operacionais de revisao visual, nao evidencias semanticas.

Fila de entrada: `voynich-codex-project/data/annotations/second_pass_crop_queue_zl3b.csv`.
Manifesto de recortes: `voynich-codex-project/data/annotations/review_crop_manifest_zl3b.csv`.
Pacotes: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/folio_review_packets_zl3b.csv`.
Itens por pacote: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/folio_review_packet_items_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/folio_review_packet_summary_zl3b.csv`.

## Resultado curto

- pacotes por folio/imagem: 4;
- itens preservados nos pacotes: 11;
- tokens faltantes agregados: 14;
- nenhum pacote autoriza leitura dos eixos `a/o` ou `r/l`.

### Objetivo do pacote

|item|n|
|---|---:|
|review_source_image_first|3|
|search_tokens_then_redraw_crop|1|

### Folios

|item|n|
|---|---:|
|f67r1|1|
|f68r3|1|
|f70v2|1|
|f84r|1|

## Pacotes

|pacote|folio|imagem|itens|faltam|objetivo|rotas R11|
|---|---|---|---:|---:|---|---|
|R12-001|f67r1|`images/raw/commons_f67r1_r2.jpg`|5|5|review_source_image_first|R11-002 R11-003 R11-006 R11-009 R11-010|
|R12-002|f70v2|`images/raw/commons_f70v2.jpg`|3|5|review_source_image_first|R11-001 R11-005 R11-007|
|R12-003|f68r3|`images/raw/commons_f68r1_r2_r3.jpg`|1|3|review_source_image_first|R11-004|
|R12-004|f84r|`images/raw/commons_f84r.jpg`|2|1|search_tokens_then_redraw_crop|R11-008 R11-011|

## Leitura provisoria

- Pacotes com `review_source_image_first` devem abrir a imagem fonte antes de redesenhar recortes.
- Pacotes com `tighten_current_svg_regions` ainda nao confirmam glifo; apenas indicam onde tentar reduzir a regiao.
- O campo `folio_packet_is_operational_not_semantic` impede usar o agrupamento como prova de significado.
