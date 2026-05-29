# Rota 41: pacote de entrada humana externa na R32

Esta rota prepara o pacote para revisao visual humana externa. Ela nao preenche a R32, nao interpreta imagem e nao altera arquivos derivados.

Planilha alvo R32: `voynich-codex-project/data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`.
Ordem R38: `voynich-codex-project/data/derived/ready_visual_annotation_manual_reopen_work_order_zl3b.csv`.
Plano R40: `voynich-codex-project/data/derived/ready_visual_annotation_conditional_chain_reopen_plan_zl3b.csv`.
Pacote R41: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_external_human_entry_packet_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_external_human_entry_summary_zl3b.csv`.

## Resultado curto

- itens no pacote: 8;
- exigem entrada humana externa: 8;
- entradas humanas presentes: 0;
- entradas invalidas ou parciais: 0;
- planilha R32 original preservada;
- guarda: `external_human_entry_packet_not_visual_evidence`.

### Status de entrada externa

|item|n|
|---|---:|
|external_human_entry_required|8|

### Acao do revisor

|item|n|
|---|---:|
|fill_r32_manual_annotation_status_and_notes|8|

### Acao pos-entrada

|item|n|
|---|---:|
|do_not_modify_derived_outputs|8|

### Status R40

|item|n|
|---|---:|
|blocked_waiting_human_entry|8|

## Itens

|rota41|rota40|rota38|rota32|folio|alvo|status|acao do revisor|
|---|---|---|---|---|---|---|---|
|R41-001|R40-001|R38-001|R32-001|f99v|manual_annotation_status manual_visual_notes|external_human_entry_required|fill_r32_manual_annotation_status_and_notes|
|R41-002|R40-002|R38-002|R32-002|f1r|manual_annotation_status manual_visual_notes|external_human_entry_required|fill_r32_manual_annotation_status_and_notes|
|R41-003|R40-003|R38-003|R32-003|f67r2|manual_annotation_status manual_visual_notes|external_human_entry_required|fill_r32_manual_annotation_status_and_notes|
|R41-004|R40-004|R38-004|R32-004|f67v1|manual_annotation_status manual_visual_notes|external_human_entry_required|fill_r32_manual_annotation_status_and_notes|
|R41-005|R40-005|R38-005|R32-005|f84r|manual_annotation_status manual_visual_notes|external_human_entry_required|fill_r32_manual_annotation_status_and_notes|
|R41-006|R40-006|R38-006|R32-006|f88v|manual_annotation_status manual_visual_notes|external_human_entry_required|fill_r32_manual_annotation_status_and_notes|
|R41-007|R40-007|R38-007|R32-007|f89r2|manual_annotation_status manual_visual_notes|external_human_entry_required|fill_r32_manual_annotation_status_and_notes|
|R41-008|R40-008|R38-008|R32-008|f99r|manual_annotation_status manual_visual_notes|external_human_entry_required|fill_r32_manual_annotation_status_and_notes|

## Instrucao manual

Para cada item, abrir o HTML R32 e a imagem fonte, revisar visualmente e preencher na planilha R32 somente `manual_annotation_status` e `manual_visual_notes`. Valores permitidos: `annotated`, `not_visible`, `uncertain`. Depois reexecutar R36, R37, R39 e R40 antes de qualquer reabertura da cadeia.
