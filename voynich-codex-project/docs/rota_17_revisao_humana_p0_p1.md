# Rota 17: revisao humana P0/P1

Esta rota prepara o lote P0/P1 pendente para revisao visual humana efetiva. Ela nao preenche campos manuais e nao cria evidencia visual por inferencia.

Fonte: `voynich-codex-project/data/derived/human_review_evidence_consolidated_zl3b.csv`.
Fila P0/P1: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/priority_human_review_p0_p1_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/priority_human_review_summary_zl3b.csv`.

## Resultado curto

- itens P0/P1 na fila: 6;
- P0: 2;
- P1: 4;
- campos manuais permanecem vazios ate revisao visual real;
- guarda: `priority_review_not_visual_evidence`.

### Prioridade

|item|n|
|---|---:|
|P1|4|
|P0|2|

### Pacotes

|item|n|
|---|---:|
|R12-001|3|
|R12-002|2|
|R12-003|1|

### Folios

|item|n|
|---|---:|
|f67r1|3|
|f70v2|2|
|f68r3|1|

### Foco de revisao

|item|n|
|---|---:|
|core_missing_tokens_second|4|
|operator_missing_tokens_first|2|

## Fila resumida

|rota17|checklist|prioridade|folio|alvo|imagem|SVG|
|---|---|---|---|---|---|---|
|R17-001|R13-001|P0|f67r1|otardar|`images/raw/commons_f67r1_r2.jpg`|`images/derived/review_crops/R7-009_R6-009_f67r1.svg`|
|R17-002|R13-006|P0|f70v2|oteedar oteeeor|`images/raw/commons_f70v2.jpg`|`images/derived/review_crops/R7-010_R6-010_f70v2.svg`|
|R17-003|R13-002|P1|f67r1|chedar cheol cheor|`images/raw/commons_f67r1_r2.jpg`|`images/derived/review_crops/R7-005_R6-005_f67r1.svg`|
|R17-004|R13-003|P1|f67r1|dol|`images/raw/commons_f67r1_r2.jpg`|`images/derived/review_crops/R7-001_R6-001_f67r1.svg`|
|R17-005|R13-007|P1|f70v2|chokear cholkal|`images/raw/commons_f70v2.jpg`|`images/derived/review_crops/R7-007_R6-007_f70v2.svg`|
|R17-006|R13-009|P1|f68r3|cheor chodal chokol|`images/raw/commons_f68r1_r2_r3.jpg`|`images/derived/review_crops/R7-006_R6-006_f68r3.svg`|

## R17-001 / R13-001 / f67r1

- alvo: `otardar`;
- imagem fonte: `images/raw/commons_f67r1_r2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-009_R6-009_f67r1.svg`;
- regiao atual: `x=31 y=158 w=768 h=913`;
- campos a preencher: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- guarda: `priority_review_not_visual_evidence`;

Procedimento:

- Abra a imagem fonte antes de decidir qualquer campo manual.
- Use o SVG apenas para localizar a regiao aproximada.
- Preencha a checklist, nao este consolidado.
- Se a palavra nao estiver clara, use `manual_token_seen=uncertain` ou marque imagem insuficiente.
- Nao atribua significado a `a/o` ou `r/l` nesta etapa.

## R17-002 / R13-006 / f70v2

- alvo: `oteedar oteeeor`;
- imagem fonte: `images/raw/commons_f70v2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-010_R6-010_f70v2.svg`;
- regiao atual: `x=138 y=106 w=1198 h=1298`;
- campos a preencher: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- guarda: `priority_review_not_visual_evidence`;

Procedimento:

- Abra a imagem fonte antes de decidir qualquer campo manual.
- Use o SVG apenas para localizar a regiao aproximada.
- Preencha a checklist, nao este consolidado.
- Se a palavra nao estiver clara, use `manual_token_seen=uncertain` ou marque imagem insuficiente.
- Nao atribua significado a `a/o` ou `r/l` nesta etapa.

## R17-003 / R13-002 / f67r1

- alvo: `chedar cheol cheor`;
- imagem fonte: `images/raw/commons_f67r1_r2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-005_R6-005_f67r1.svg`;
- regiao atual: `x=31 y=158 w=768 h=913`;
- campos a preencher: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- guarda: `priority_review_not_visual_evidence`;

Procedimento:

- Abra a imagem fonte antes de decidir qualquer campo manual.
- Use o SVG apenas para localizar a regiao aproximada.
- Preencha a checklist, nao este consolidado.
- Se a palavra nao estiver clara, use `manual_token_seen=uncertain` ou marque imagem insuficiente.
- Nao atribua significado a `a/o` ou `r/l` nesta etapa.

## R17-004 / R13-003 / f67r1

- alvo: `dol`;
- imagem fonte: `images/raw/commons_f67r1_r2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-001_R6-001_f67r1.svg`;
- regiao atual: `x=31 y=158 w=768 h=913`;
- campos a preencher: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- guarda: `priority_review_not_visual_evidence`;

Procedimento:

- Abra a imagem fonte antes de decidir qualquer campo manual.
- Use o SVG apenas para localizar a regiao aproximada.
- Preencha a checklist, nao este consolidado.
- Se a palavra nao estiver clara, use `manual_token_seen=uncertain` ou marque imagem insuficiente.
- Nao atribua significado a `a/o` ou `r/l` nesta etapa.

## R17-005 / R13-007 / f70v2

- alvo: `chokear cholkal`;
- imagem fonte: `images/raw/commons_f70v2.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-007_R6-007_f70v2.svg`;
- regiao atual: `x=138 y=106 w=1198 h=1298`;
- campos a preencher: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- guarda: `priority_review_not_visual_evidence`;

Procedimento:

- Abra a imagem fonte antes de decidir qualquer campo manual.
- Use o SVG apenas para localizar a regiao aproximada.
- Preencha a checklist, nao este consolidado.
- Se a palavra nao estiver clara, use `manual_token_seen=uncertain` ou marque imagem insuficiente.
- Nao atribua significado a `a/o` ou `r/l` nesta etapa.

## R17-006 / R13-009 / f68r3

- alvo: `cheor chodal chokol`;
- imagem fonte: `images/raw/commons_f68r1_r2_r3.jpg`;
- SVG de referencia: `images/derived/review_crops/R7-006_R6-006_f68r3.svg`;
- regiao atual: `x=891 y=53 w=568 h=570`;
- campos a preencher: `manual_token_seen manual_new_crop_needed manual_image_insufficient manual_new_crop_x manual_new_crop_y manual_new_crop_width manual_new_crop_height manual_notes`;
- guarda: `priority_review_not_visual_evidence`;

Procedimento:

- Abra a imagem fonte antes de decidir qualquer campo manual.
- Use o SVG apenas para localizar a regiao aproximada.
- Preencha a checklist, nao este consolidado.
- Se a palavra nao estiver clara, use `manual_token_seen=uncertain` ou marque imagem insuficiente.
- Nao atribua significado a `a/o` ou `r/l` nesta etapa.
