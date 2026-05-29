# Rota 21: planilha de preenchimento visual P0/P1

Esta rota cria uma planilha enxuta para preencher manualmente os 6 itens P0/P1 que a Rota 20 manteve em branco. Ela nao decide campos visuais e nao converte ausencia de anotacao em evidencia.

Log de aplicacao fonte: `voynich-codex-project/data/derived/direct_visual_decision_application_log_zl3b.csv`.
Pacote visual fonte: `voynich-codex-project/data/annotations/direct_visual_decision_package_p0_p1_zl3b.csv`.
Planilha de entrada: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/visual_decision_entry_sheet_summary_zl3b.csv`.

## Valores permitidos

- `manual_token_seen`: `yes/no/uncertain`;
- `manual_new_crop_needed`: `yes/no`;
- `manual_image_insufficient`: `yes/no`;
- coordenadas de novo recorte devem ficar vazias quando `manual_new_crop_needed=no`.

## Resultado curto

- linhas para preencher: 6;
- P0: 2;
- P1: 4;
- campos manuais permanecem em branco;
- guarda: `entry_sheet_not_visual_evidence`.

### Status de entrada

|item|n|
|---|---:|
|awaiting_manual_entry|6|

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

|rota21|rota20|rota19|checklist|prioridade|folio|alvo|imagem|SVG|
|---|---|---|---|---|---|---|---|---|
|R21-001|R20-001|R19-001|R13-001|P0|f67r1|otardar|`images/raw/commons_f67r1_r2.jpg`|`images/derived/review_crops/R7-009_R6-009_f67r1.svg`|
|R21-002|R20-002|R19-002|R13-006|P0|f70v2|oteedar oteeeor|`images/raw/commons_f70v2.jpg`|`images/derived/review_crops/R7-010_R6-010_f70v2.svg`|
|R21-003|R20-003|R19-003|R13-002|P1|f67r1|chedar cheol cheor|`images/raw/commons_f67r1_r2.jpg`|`images/derived/review_crops/R7-005_R6-005_f67r1.svg`|
|R21-004|R20-004|R19-004|R13-003|P1|f67r1|dol|`images/raw/commons_f67r1_r2.jpg`|`images/derived/review_crops/R7-001_R6-001_f67r1.svg`|
|R21-005|R20-005|R19-005|R13-007|P1|f70v2|chokear cholkal|`images/raw/commons_f70v2.jpg`|`images/derived/review_crops/R7-007_R6-007_f70v2.svg`|
|R21-006|R20-006|R19-006|R13-009|P1|f68r3|cheor chodal chokol|`images/raw/commons_f68r1_r2_r3.jpg`|`images/derived/review_crops/R7-006_R6-006_f68r3.svg`|

## R21-001 / R20-001 / R13-001

- alvo: `otardar`;
- folio: `f67r1`;
- imagem fonte: `images/raw/commons_f67r1_r2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-009_R6-009_f67r1.svg`;
- regiao atual: `x=31 y=158 w=768 h=913`;
- valores permitidos para `manual_token_seen`: `yes/no/uncertain`;
- valores permitidos para `manual_new_crop_needed`: `yes/no`;
- valores permitidos para `manual_image_insufficient`: `yes/no`;
- regra de saida: `copy_completed_entry_values_to_direct_visual_package`;
- guarda: `entry_sheet_not_visual_evidence`;

## R21-002 / R20-002 / R13-006

- alvo: `oteedar oteeeor`;
- folio: `f70v2`;
- imagem fonte: `images/raw/commons_f70v2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-010_R6-010_f70v2.svg`;
- regiao atual: `x=138 y=106 w=1198 h=1298`;
- valores permitidos para `manual_token_seen`: `yes/no/uncertain`;
- valores permitidos para `manual_new_crop_needed`: `yes/no`;
- valores permitidos para `manual_image_insufficient`: `yes/no`;
- regra de saida: `copy_completed_entry_values_to_direct_visual_package`;
- guarda: `entry_sheet_not_visual_evidence`;

## R21-003 / R20-003 / R13-002

- alvo: `chedar cheol cheor`;
- folio: `f67r1`;
- imagem fonte: `images/raw/commons_f67r1_r2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-005_R6-005_f67r1.svg`;
- regiao atual: `x=31 y=158 w=768 h=913`;
- valores permitidos para `manual_token_seen`: `yes/no/uncertain`;
- valores permitidos para `manual_new_crop_needed`: `yes/no`;
- valores permitidos para `manual_image_insufficient`: `yes/no`;
- regra de saida: `copy_completed_entry_values_to_direct_visual_package`;
- guarda: `entry_sheet_not_visual_evidence`;

## R21-004 / R20-004 / R13-003

- alvo: `dol`;
- folio: `f67r1`;
- imagem fonte: `images/raw/commons_f67r1_r2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-001_R6-001_f67r1.svg`;
- regiao atual: `x=31 y=158 w=768 h=913`;
- valores permitidos para `manual_token_seen`: `yes/no/uncertain`;
- valores permitidos para `manual_new_crop_needed`: `yes/no`;
- valores permitidos para `manual_image_insufficient`: `yes/no`;
- regra de saida: `copy_completed_entry_values_to_direct_visual_package`;
- guarda: `entry_sheet_not_visual_evidence`;

## R21-005 / R20-005 / R13-007

- alvo: `chokear cholkal`;
- folio: `f70v2`;
- imagem fonte: `images/raw/commons_f70v2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-007_R6-007_f70v2.svg`;
- regiao atual: `x=138 y=106 w=1198 h=1298`;
- valores permitidos para `manual_token_seen`: `yes/no/uncertain`;
- valores permitidos para `manual_new_crop_needed`: `yes/no`;
- valores permitidos para `manual_image_insufficient`: `yes/no`;
- regra de saida: `copy_completed_entry_values_to_direct_visual_package`;
- guarda: `entry_sheet_not_visual_evidence`;

## R21-006 / R20-006 / R13-009

- alvo: `cheor chodal chokol`;
- folio: `f68r3`;
- imagem fonte: `images/raw/commons_f68r1_r2_r3.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-006_R6-006_f68r3.svg`;
- regiao atual: `x=891 y=53 w=568 h=570`;
- valores permitidos para `manual_token_seen`: `yes/no/uncertain`;
- valores permitidos para `manual_new_crop_needed`: `yes/no`;
- valores permitidos para `manual_image_insufficient`: `yes/no`;
- regra de saida: `copy_completed_entry_values_to_direct_visual_package`;
- guarda: `entry_sheet_not_visual_evidence`;
