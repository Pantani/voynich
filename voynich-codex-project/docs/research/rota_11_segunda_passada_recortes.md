# Rota 11: segunda passada de recortes melhores

Esta rota transforma os itens pendentes da Rota 10 em uma fila objetiva para nova revisao visual. Ela nao interpreta os eixos da matriz.

Fonte: `voynich-codex-project/data/derived/manual_svg_review_consolidated_zl3b.csv`.
Fila de trabalho: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/second_pass_crop_queue_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/second_pass_crop_queue_summary_zl3b.csv`.

## Resultado curto

- itens na fila: 11;
- tokens faltantes a procurar: 14;
- itens com foco em tokens faltantes: 8;
- itens para apertar regiao existente: 3;
- nenhuma linha fica elegivel para semantica por estar nesta fila.

### Prioridade

|item|n|
|---|---:|
|P1_core_missing_tokens|4|
|P3_tighten_existing_region|3|
|P0_operator_missing_tokens|2|
|P2_other_missing_tokens|2|

### Foco da segunda passada

|item|n|
|---|---:|
|locate_missing_group_tokens|8|
|tighten_existing_matched_tokens|3|

### Estrategia de recorte

|item|n|
|---|---:|
|rescan_source_image_before_new_crop|4|
|search_single_missing_token_then_redraw_crop|4|
|tighten_current_svg_region|3|

### Familias

|item|n|
|---|---:|
|standalone|5|
|ch|3|
|ot|2|
|d|1|

## Fila

|rota11|rota10|manual|crop|familia|folio|locus|faltam|prioridade|foco|estrategia|
|---|---|---|---|---|---|---|---:|---|---|---|
|R11-001|R10-002|R9-002|R7-010|ot|f70v2|f70v2.21,@Cc|2|P0_operator_missing_tokens|locate_missing_group_tokens|rescan_source_image_before_new_crop|
|R11-002|R10-001|R9-001|R7-009|ot|f67r1|f67r1.5,@Cc|1|P0_operator_missing_tokens|locate_missing_group_tokens|search_single_missing_token_then_redraw_crop|
|R11-003|R10-004|R9-004|R7-005|ch|f67r1|f67r1.6,+Cc|3|P1_core_missing_tokens|locate_missing_group_tokens|rescan_source_image_before_new_crop|
|R11-004|R10-005|R9-005|R7-006|ch|f68r3|f68r3.1,@Cc|3|P1_core_missing_tokens|locate_missing_group_tokens|rescan_source_image_before_new_crop|
|R11-005|R10-006|R9-006|R7-007|ch|f70v2|f70v2.1,@Cc|2|P1_core_missing_tokens|locate_missing_group_tokens|rescan_source_image_before_new_crop|
|R11-006|R10-003|R9-003|R7-001|d|f67r1|f67r1.6,+Cc|1|P1_core_missing_tokens|locate_missing_group_tokens|search_single_missing_token_then_redraw_crop|
|R11-007|R10-007|R9-007|R7-008|standalone|f70v2|f70v2.32,@Cc|1|P2_other_missing_tokens|locate_missing_group_tokens|search_single_missing_token_then_redraw_crop|
|R11-008|R10-008|R9-008|R7-011|standalone|f84r|f84r.23,+P0|1|P2_other_missing_tokens|locate_missing_group_tokens|search_single_missing_token_then_redraw_crop|
|R11-009|R10-009|R9-009|R7-002|standalone|f67r1|f67r1.5,@Cc|0|P3_tighten_existing_region|tighten_existing_matched_tokens|tighten_current_svg_region|
|R11-010|R10-010|R9-010|R7-004|standalone|f67r1|f67r1.6,+Cc|0|P3_tighten_existing_region|tighten_existing_matched_tokens|tighten_current_svg_region|
|R11-011|R10-011|R9-011|R7-003|standalone|f84r|f84r.14,+P0|0|P3_tighten_existing_region|tighten_existing_matched_tokens|tighten_current_svg_region|

## Leitura provisoria

- A fila prioriza revisao operacional, nao importancia semantica.
- Itens `P0` indicam operadores com tokens faltantes e devem ser conferidos primeiro.
- Itens `P3` ja tinham tokens anotados, mas ainda precisam de uma regiao menor antes de qualquer teste fino.
- A proxima rota pode gerar instrucoes por folio ou recortes alternativos, preservando a guarda `no_axis_meaning_from_queue_position`.
