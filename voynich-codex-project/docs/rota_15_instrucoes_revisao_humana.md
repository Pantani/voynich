# Rota 15: instrucoes humanas por pacote

Esta rota gera instrucoes de revisao humana para preencher a checklist Rota 13. As instrucoes nao alteram a checklist e nao criam evidencia visual por si mesmas.

Pacotes de entrada: `voynich-codex-project/data/annotations/folio_review_packets_zl3b.csv`.
Checklist de entrada: `voynich-codex-project/data/annotations/packet_item_checklist_zl3b.csv`.
Instrucoes por pacote: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/human_review_instructions_zl3b.csv`.
Instrucoes item-a-item: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/human_review_instruction_items_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/human_review_instruction_summary_zl3b.csv`.

## Resultado curto

- pacotes instruidos: 4;
- itens instruidos: 11;
- nenhum campo manual foi preenchido automaticamente;
- nenhuma instrucao autoriza leitura semantica dos eixos.

### Modo de instrucao

|item|n|
|---|---:|
|open_source_image_before_svg|3|
|search_tokens_then_redraw_crop|1|

### Folios

|item|n|
|---|---:|
|f67r1|1|
|f68r3|1|
|f70v2|1|
|f84r|1|

## R15-001 / R12-001 / f67r1

- imagem fonte: `images/raw/commons_f67r1_r2.jpg`;
- modo: `open_source_image_before_svg`;
- campos a preencher: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- guarda: `human_instruction_not_visual_evidence`;

|checklist|prioridade|alvo|tipo|SVG|
|---|---|---|---|---|
|R13-001|P0_operator_missing_tokens|otardar|missing_group_tokens|`images/derived/review_crops/R7-009_R6-009_f67r1.svg`|
|R13-002|P1_core_missing_tokens|chedar cheol cheor|missing_group_tokens|`images/derived/review_crops/R7-005_R6-005_f67r1.svg`|
|R13-003|P1_core_missing_tokens|dol|missing_group_tokens|`images/derived/review_crops/R7-001_R6-001_f67r1.svg`|
|R13-004|P3_tighten_existing_region|ar ol|matched_group_tokens|`images/derived/review_crops/R7-002_R6-002_f67r1.svg`|
|R13-005|P3_tighten_existing_region|al ar|matched_group_tokens|`images/derived/review_crops/R7-004_R6-004_f67r1.svg`|

Preenchimento:

- Abra primeiro a imagem fonte quando o modo pedir `open_source_image_before_svg`.
- Use o SVG apenas como referencia de regiao, nao como confirmacao automatica.
- Marque `manual_token_seen=yes/no/uncertain` depois da revisao visual.
- Preencha coordenadas novas somente quando `manual_new_crop_needed=yes`.
- Nao atribua significado a `a/o` ou `r/l` nesta etapa.

## R15-002 / R12-002 / f70v2

- imagem fonte: `images/raw/commons_f70v2.jpg`;
- modo: `open_source_image_before_svg`;
- campos a preencher: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- guarda: `human_instruction_not_visual_evidence`;

|checklist|prioridade|alvo|tipo|SVG|
|---|---|---|---|---|
|R13-006|P0_operator_missing_tokens|oteedar oteeeor|missing_group_tokens|`images/derived/review_crops/R7-010_R6-010_f70v2.svg`|
|R13-007|P1_core_missing_tokens|chokear cholkal|missing_group_tokens|`images/derived/review_crops/R7-007_R6-007_f70v2.svg`|
|R13-008|P2_other_missing_tokens|al|missing_group_tokens|`images/derived/review_crops/R7-008_R6-008_f70v2.svg`|

Preenchimento:

- Abra primeiro a imagem fonte quando o modo pedir `open_source_image_before_svg`.
- Use o SVG apenas como referencia de regiao, nao como confirmacao automatica.
- Marque `manual_token_seen=yes/no/uncertain` depois da revisao visual.
- Preencha coordenadas novas somente quando `manual_new_crop_needed=yes`.
- Nao atribua significado a `a/o` ou `r/l` nesta etapa.

## R15-003 / R12-003 / f68r3

- imagem fonte: `images/raw/commons_f68r1_r2_r3.jpg`;
- modo: `open_source_image_before_svg`;
- campos a preencher: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- guarda: `human_instruction_not_visual_evidence`;

|checklist|prioridade|alvo|tipo|SVG|
|---|---|---|---|---|
|R13-009|P1_core_missing_tokens|cheor chodal chokol|missing_group_tokens|`images/derived/review_crops/R7-006_R6-006_f68r3.svg`|

Preenchimento:

- Abra primeiro a imagem fonte quando o modo pedir `open_source_image_before_svg`.
- Use o SVG apenas como referencia de regiao, nao como confirmacao automatica.
- Marque `manual_token_seen=yes/no/uncertain` depois da revisao visual.
- Preencha coordenadas novas somente quando `manual_new_crop_needed=yes`.
- Nao atribua significado a `a/o` ou `r/l` nesta etapa.

## R15-004 / R12-004 / f84r

- imagem fonte: `images/raw/commons_f84r.jpg`;
- modo: `search_tokens_then_redraw_crop`;
- campos a preencher: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- guarda: `human_instruction_not_visual_evidence`;

|checklist|prioridade|alvo|tipo|SVG|
|---|---|---|---|---|
|R13-010|P2_other_missing_tokens|ol|missing_group_tokens|`images/derived/review_crops/R7-011_R6-011_f84r.svg`|
|R13-011|P3_tighten_existing_region|ol or|matched_group_tokens|`images/derived/review_crops/R7-003_R6-003_f84r.svg`|

Preenchimento:

- Abra primeiro a imagem fonte quando o modo pedir `open_source_image_before_svg`.
- Use o SVG apenas como referencia de regiao, nao como confirmacao automatica.
- Marque `manual_token_seen=yes/no/uncertain` depois da revisao visual.
- Preencha coordenadas novas somente quando `manual_new_crop_needed=yes`.
- Nao atribua significado a `a/o` ou `r/l` nesta etapa.
