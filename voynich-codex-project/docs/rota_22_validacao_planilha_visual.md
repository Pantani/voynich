# Rota 22: validacao da planilha visual R21

Esta rota valida os campos preenchidos na planilha R21 e copia somente valores manuais validos para um pacote visual derivado. Campos vazios continuam pendentes.

Planilha R21: `voynich-codex-project/data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv`.
Pacote visual fonte: `voynich-codex-project/data/annotations/direct_visual_decision_package_p0_p1_zl3b.csv`.
Pacote visual derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/direct_visual_package_after_entry_sheet_p0_p1_zl3b.csv`.
Log de validacao: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/visual_decision_entry_validation_log_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/visual_decision_entry_validation_summary_zl3b.csv`.

## Resultado curto

- linhas validadas: 6;
- entradas validas: 0;
- entradas pendentes: 6;
- entradas invalidas: 0;
- campos vazios nao apagam valores existentes;
- guarda: `validated_values_are_manual_not_axis_meaning`.

### Status de validacao

|item|n|
|---|---:|
|pending_blank_manual_entry|6|

### Status de aplicacao

|item|n|
|---|---:|
|skipped_blank_manual_entry|6|

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

## Log

|rota22|rota21|rota19|checklist|prioridade|folio|status|aplicacao|erros|
|---|---|---|---|---|---|---|---|---|
|R22-001|R21-001|R19-001|R13-001|P0|f67r1|pending_blank_manual_entry|skipped_blank_manual_entry||
|R22-002|R21-002|R19-002|R13-006|P0|f70v2|pending_blank_manual_entry|skipped_blank_manual_entry||
|R22-003|R21-003|R19-003|R13-002|P1|f67r1|pending_blank_manual_entry|skipped_blank_manual_entry||
|R22-004|R21-004|R19-004|R13-003|P1|f67r1|pending_blank_manual_entry|skipped_blank_manual_entry||
|R22-005|R21-005|R19-005|R13-007|P1|f70v2|pending_blank_manual_entry|skipped_blank_manual_entry||
|R22-006|R21-006|R19-006|R13-009|P1|f68r3|pending_blank_manual_entry|skipped_blank_manual_entry||

## R22-001 / R21-001 / R19-001

- checklist: `R13-001`;
- validacao: `pending_blank_manual_entry`;
- erros: ``;
- aplicacao: `skipped_blank_manual_entry`;
- proxima acao: `fill R21 entry sheet or keep item pending`;
- guarda: `validated_values_are_manual_not_axis_meaning`;

## R22-002 / R21-002 / R19-002

- checklist: `R13-006`;
- validacao: `pending_blank_manual_entry`;
- erros: ``;
- aplicacao: `skipped_blank_manual_entry`;
- proxima acao: `fill R21 entry sheet or keep item pending`;
- guarda: `validated_values_are_manual_not_axis_meaning`;

## R22-003 / R21-003 / R19-003

- checklist: `R13-002`;
- validacao: `pending_blank_manual_entry`;
- erros: ``;
- aplicacao: `skipped_blank_manual_entry`;
- proxima acao: `fill R21 entry sheet or keep item pending`;
- guarda: `validated_values_are_manual_not_axis_meaning`;

## R22-004 / R21-004 / R19-004

- checklist: `R13-003`;
- validacao: `pending_blank_manual_entry`;
- erros: ``;
- aplicacao: `skipped_blank_manual_entry`;
- proxima acao: `fill R21 entry sheet or keep item pending`;
- guarda: `validated_values_are_manual_not_axis_meaning`;

## R22-005 / R21-005 / R19-005

- checklist: `R13-007`;
- validacao: `pending_blank_manual_entry`;
- erros: ``;
- aplicacao: `skipped_blank_manual_entry`;
- proxima acao: `fill R21 entry sheet or keep item pending`;
- guarda: `validated_values_are_manual_not_axis_meaning`;

## R22-006 / R21-006 / R19-006

- checklist: `R13-009`;
- validacao: `pending_blank_manual_entry`;
- erros: ``;
- aplicacao: `skipped_blank_manual_entry`;
- proxima acao: `fill R21 entry sheet or keep item pending`;
- guarda: `validated_values_are_manual_not_axis_meaning`;
