# Rota 23: pacote HTML guiado para preencher R21

Esta rota gera uma superficie HTML para guiar o preenchimento manual da planilha R21. Ela nao grava decisoes e nao cria evidencia visual.

Planilha R21: `voynich-codex-project/data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv`.
Log R22: `voynich-codex-project/data/derived/visual_decision_entry_validation_log_zl3b.csv`.
Manifest: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/guided_visual_entry_html_manifest_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/guided_visual_entry_html_summary_zl3b.csv`.
HTML guiado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/docs/rota_23_pacote_html_preenchimento_r21.html`.

## Resultado curto

- cartoes HTML gerados: 6;
- P0: 2;
- P1: 4;
- decisoes seguem fora do HTML e devem ser preenchidas no CSV R21;
- guarda: `guided_html_not_visual_evidence`.

### Status do cartao

|item|n|
|---|---:|
|ready_for_guided_manual_entry|6|

### Status R22

|item|n|
|---|---:|
|pending_blank_manual_entry|6|

### Prioridade

|item|n|
|---|---:|
|P1|4|
|P0|2|

### Folios

|item|n|
|---|---:|
|f67r1|3|
|f70v2|2|
|f68r3|1|

## Itens

|rota23|rota22|rota21|rota19|checklist|prioridade|folio|alvo|imagem|SVG|
|---|---|---|---|---|---|---|---|---|---|
|R23-001|R22-001|R21-001|R19-001|R13-001|P0|f67r1|otardar|`images/raw/commons_f67r1_r2.jpg`|`images/derived/review_crops/R7-009_R6-009_f67r1.svg`|
|R23-002|R22-002|R21-002|R19-002|R13-006|P0|f70v2|oteedar oteeeor|`images/raw/commons_f70v2.jpg`|`images/derived/review_crops/R7-010_R6-010_f70v2.svg`|
|R23-003|R22-003|R21-003|R19-003|R13-002|P1|f67r1|chedar cheol cheor|`images/raw/commons_f67r1_r2.jpg`|`images/derived/review_crops/R7-005_R6-005_f67r1.svg`|
|R23-004|R22-004|R21-004|R19-004|R13-003|P1|f67r1|dol|`images/raw/commons_f67r1_r2.jpg`|`images/derived/review_crops/R7-001_R6-001_f67r1.svg`|
|R23-005|R22-005|R21-005|R19-005|R13-007|P1|f70v2|chokear cholkal|`images/raw/commons_f70v2.jpg`|`images/derived/review_crops/R7-007_R6-007_f70v2.svg`|
|R23-006|R22-006|R21-006|R19-006|R13-009|P1|f68r3|cheor chodal chokol|`images/raw/commons_f68r1_r2_r3.jpg`|`images/derived/review_crops/R7-006_R6-006_f68r3.svg`|

## R23-001 / R21-001 / R19-001

- checklist: `R13-001`;
- alvo: `otardar`;
- imagem fonte: `images/raw/commons_f67r1_r2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-009_R6-009_f67r1.svg`;
- campos no CSV R21: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- regra de saida: `fill_r21_csv_manually_then_rerun_route_22`;
- guarda: `guided_html_not_visual_evidence`;

## R23-002 / R21-002 / R19-002

- checklist: `R13-006`;
- alvo: `oteedar oteeeor`;
- imagem fonte: `images/raw/commons_f70v2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-010_R6-010_f70v2.svg`;
- campos no CSV R21: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- regra de saida: `fill_r21_csv_manually_then_rerun_route_22`;
- guarda: `guided_html_not_visual_evidence`;

## R23-003 / R21-003 / R19-003

- checklist: `R13-002`;
- alvo: `chedar cheol cheor`;
- imagem fonte: `images/raw/commons_f67r1_r2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-005_R6-005_f67r1.svg`;
- campos no CSV R21: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- regra de saida: `fill_r21_csv_manually_then_rerun_route_22`;
- guarda: `guided_html_not_visual_evidence`;

## R23-004 / R21-004 / R19-004

- checklist: `R13-003`;
- alvo: `dol`;
- imagem fonte: `images/raw/commons_f67r1_r2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-001_R6-001_f67r1.svg`;
- campos no CSV R21: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- regra de saida: `fill_r21_csv_manually_then_rerun_route_22`;
- guarda: `guided_html_not_visual_evidence`;

## R23-005 / R21-005 / R19-005

- checklist: `R13-007`;
- alvo: `chokear cholkal`;
- imagem fonte: `images/raw/commons_f70v2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-007_R6-007_f70v2.svg`;
- campos no CSV R21: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- regra de saida: `fill_r21_csv_manually_then_rerun_route_22`;
- guarda: `guided_html_not_visual_evidence`;

## R23-006 / R21-006 / R19-006

- checklist: `R13-009`;
- alvo: `cheor chodal chokol`;
- imagem fonte: `images/raw/commons_f68r1_r2_r3.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-006_R6-006_f68r3.svg`;
- campos no CSV R21: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- regra de saida: `fill_r21_csv_manually_then_rerun_route_22`;
- guarda: `guided_html_not_visual_evidence`;
