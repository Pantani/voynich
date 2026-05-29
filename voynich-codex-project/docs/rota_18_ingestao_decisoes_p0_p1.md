# Rota 18: ingestao das decisoes P0/P1

Esta rota ingere a fila P0/P1 da Rota 17 contra a checklist. Ela classifica somente campos ja preenchidos e mantem campos vazios como pendencia.

Fila P0/P1: `voynich-codex-project/data/annotations/priority_human_review_p0_p1_zl3b.csv`.
Checklist: `voynich-codex-project/data/annotations/packet_item_checklist_zl3b.csv`.
Consolidado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/priority_human_decisions_p0_p1_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/priority_human_decisions_summary_zl3b.csv`.

## Resultado curto

- itens ingeridos: 6;
- pendentes: 6;
- candidatos a novo recorte: 0;
- campos vazios nao foram convertidos em evidencia;
- guarda: `priority_decision_not_axis_meaning`.

### Decisoes

|item|n|
|---|---:|
|pending_manual_decision|6|

### Estado humano

|item|n|
|---|---:|
|pending_human_review|6|

### Prioridade

|item|n|
|---|---:|
|P1|4|
|P0|2|

### Acao de recorte

|item|n|
|---|---:|
|no_crop_generation|6|

### Prontidao para eixo

|item|n|
|---|---:|
|not_ready|6|

## Linhas ingeridas

|rota18|rota17|checklist|prioridade|folio|alvo|decisao|acao|
|---|---|---|---|---|---|---|---|
|R18-001|R17-001|R13-001|P0|f67r1|otardar|pending_manual_decision|no_crop_generation|
|R18-002|R17-002|R13-006|P0|f70v2|oteedar oteeeor|pending_manual_decision|no_crop_generation|
|R18-003|R17-003|R13-002|P1|f67r1|chedar cheol cheor|pending_manual_decision|no_crop_generation|
|R18-004|R17-004|R13-003|P1|f67r1|dol|pending_manual_decision|no_crop_generation|
|R18-005|R17-005|R13-007|P1|f70v2|chokear cholkal|pending_manual_decision|no_crop_generation|
|R18-006|R17-006|R13-009|P1|f68r3|cheor chodal chokol|pending_manual_decision|no_crop_generation|

## R18-001 / R17-001 / R13-001

- folio: `f67r1`;
- alvo: `otardar`;
- manual_token_seen: ``;
- manual_new_crop_needed: ``;
- manual_image_insufficient: ``;
- decisao: `pending_manual_decision`;
- proxima acao: `fill human review fields from source image inspection`;
- guarda: `priority_decision_not_axis_meaning`;

## R18-002 / R17-002 / R13-006

- folio: `f70v2`;
- alvo: `oteedar oteeeor`;
- manual_token_seen: ``;
- manual_new_crop_needed: ``;
- manual_image_insufficient: ``;
- decisao: `pending_manual_decision`;
- proxima acao: `fill human review fields from source image inspection`;
- guarda: `priority_decision_not_axis_meaning`;

## R18-003 / R17-003 / R13-002

- folio: `f67r1`;
- alvo: `chedar cheol cheor`;
- manual_token_seen: ``;
- manual_new_crop_needed: ``;
- manual_image_insufficient: ``;
- decisao: `pending_manual_decision`;
- proxima acao: `fill human review fields from source image inspection`;
- guarda: `priority_decision_not_axis_meaning`;

## R18-004 / R17-004 / R13-003

- folio: `f67r1`;
- alvo: `dol`;
- manual_token_seen: ``;
- manual_new_crop_needed: ``;
- manual_image_insufficient: ``;
- decisao: `pending_manual_decision`;
- proxima acao: `fill human review fields from source image inspection`;
- guarda: `priority_decision_not_axis_meaning`;

## R18-005 / R17-005 / R13-007

- folio: `f70v2`;
- alvo: `chokear cholkal`;
- manual_token_seen: ``;
- manual_new_crop_needed: ``;
- manual_image_insufficient: ``;
- decisao: `pending_manual_decision`;
- proxima acao: `fill human review fields from source image inspection`;
- guarda: `priority_decision_not_axis_meaning`;

## R18-006 / R17-006 / R13-009

- folio: `f68r3`;
- alvo: `cheor chodal chokol`;
- manual_token_seen: ``;
- manual_new_crop_needed: ``;
- manual_image_insufficient: ``;
- decisao: `pending_manual_decision`;
- proxima acao: `fill human review fields from source image inspection`;
- guarda: `priority_decision_not_axis_meaning`;
