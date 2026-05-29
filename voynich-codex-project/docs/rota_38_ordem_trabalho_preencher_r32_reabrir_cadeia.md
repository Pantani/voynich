# Rota 38: ordem de trabalho para preencher R32 e reabrir cadeia

Esta rota organiza o preenchimento humano da planilha R32 para reabrir a cadeia R34/R35/R33/R31. Ela nao grava decisoes nem interpreta imagem automaticamente.

Planilha R32: `voynich-codex-project/data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`.
Protocolo R36: `voynich-codex-project/data/derived/ready_visual_annotation_manual_fill_protocol_zl3b.csv`.
Plano R37: `voynich-codex-project/data/derived/ready_visual_annotation_revalidation_chain_plan_zl3b.csv`.
HTML de apoio: `voynich-codex-project/docs/rota_32_pacote_html_anotacao_visual_prontos.html`.
Ordem de trabalho R38: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_manual_reopen_work_order_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_manual_reopen_work_order_summary_zl3b.csv`.

## Resultado curto

- itens na ordem de trabalho: 8;
- exigem preenchimento manual: 8;
- prontos para reabrir cadeia: 0;
- bloqueados por entrada invalida: 0;
- planilha R32 original preservada;
- guarda: `manual_reopen_work_order_not_visual_evidence`.

### Status da ordem

|item|n|
|---|---:|
|manual_fill_required|8|

### Acao de reabertura

|item|n|
|---|---:|
|do_not_reopen_chain_until_r32_filled|8|

### Proxima acao

|item|n|
|---|---:|
|fill_manual_annotation_status_and_notes_in_r32|8|

### Status R36

|item|n|
|---|---:|
|awaiting_human_visual_entry|8|

### Status R37

|item|n|
|---|---:|
|blocked_no_human_entries|8|

## Itens

|rota38|rota37|rota36|rota32|folio|campos|status|proxima acao|
|---|---|---|---|---|---|---|---|
|R38-001|R37-001|R36-001|R32-001|f99v|manual_annotation_status manual_visual_notes|manual_fill_required|fill_manual_annotation_status_and_notes_in_r32|
|R38-002|R37-002|R36-002|R32-002|f1r|manual_annotation_status manual_visual_notes|manual_fill_required|fill_manual_annotation_status_and_notes_in_r32|
|R38-003|R37-003|R36-003|R32-003|f67r2|manual_annotation_status manual_visual_notes|manual_fill_required|fill_manual_annotation_status_and_notes_in_r32|
|R38-004|R37-004|R36-004|R32-004|f67v1|manual_annotation_status manual_visual_notes|manual_fill_required|fill_manual_annotation_status_and_notes_in_r32|
|R38-005|R37-005|R36-005|R32-005|f84r|manual_annotation_status manual_visual_notes|manual_fill_required|fill_manual_annotation_status_and_notes_in_r32|
|R38-006|R37-006|R36-006|R32-006|f88v|manual_annotation_status manual_visual_notes|manual_fill_required|fill_manual_annotation_status_and_notes_in_r32|
|R38-007|R37-007|R36-007|R32-007|f89r2|manual_annotation_status manual_visual_notes|manual_fill_required|fill_manual_annotation_status_and_notes_in_r32|
|R38-008|R37-008|R36-008|R32-008|f99r|manual_annotation_status manual_visual_notes|manual_fill_required|fill_manual_annotation_status_and_notes_in_r32|

## Instrucao manual

Para cada linha, abrir o HTML R32, verificar a imagem fonte e preencher na planilha R32 somente `manual_annotation_status` e `manual_visual_notes`. Valores permitidos: `annotated`, `not_visible`, `uncertain`. Depois, reexecutar R36 e R37 antes de reabrir R34/R35/R33/R31.
