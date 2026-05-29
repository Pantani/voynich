# Rota 36: protocolo de preenchimento humano R32

Esta rota prepara o preenchimento humano efetivo da planilha R32. Ela nao escreve decisoes na planilha original e nao interpreta imagens automaticamente.

Planilha R32: `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`.
Plano R35: `data/derived/ready_visual_annotation_post_gate_rerun_plan_zl3b.csv`.
HTML de apoio: `docs/rota_32_pacote_html_anotacao_visual_prontos.html`.
Protocolo R36: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_manual_fill_protocol_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_manual_fill_protocol_summary_zl3b.csv`.

## Resultado curto

- itens no protocolo: 8;
- aguardando anotacao humana: 0;
- entradas prontas para reexecutar gate: 8;
- entradas invalidas: 0;
- planilha R32 original preservada;
- guarda: `manual_fill_protocol_not_visual_evidence`.

### Status de preenchimento

|item|n|
|---|---:|
|human_entry_present_ready_for_gate_rerun|8|

### Motivo

|item|n|
|---|---:|
|manual_entry_present|8|

### Proxima acao

|item|n|
|---|---:|
|rerun_r34_then_r35|8|

### Status R35

|item|n|
|---|---:|
|ready_for_controlled_rerun|8|

## Itens

|rota36|rota35|rota32|rota28|folio|status|motivo|proxima acao|
|---|---|---|---|---|---|---|---|
|R36-001|R35-001|R32-001|R28-001|f99v|human_entry_present_ready_for_gate_rerun|manual_entry_present|rerun_r34_then_r35|
|R36-002|R35-002|R32-002|R28-020|f1r|human_entry_present_ready_for_gate_rerun|manual_entry_present|rerun_r34_then_r35|
|R36-003|R35-003|R32-003|R28-021|f67r2|human_entry_present_ready_for_gate_rerun|manual_entry_present|rerun_r34_then_r35|
|R36-004|R35-004|R32-004|R28-022|f67v1|human_entry_present_ready_for_gate_rerun|manual_entry_present|rerun_r34_then_r35|
|R36-005|R35-005|R32-005|R28-023|f84r|human_entry_present_ready_for_gate_rerun|manual_entry_present|rerun_r34_then_r35|
|R36-006|R35-006|R32-006|R28-024|f88v|human_entry_present_ready_for_gate_rerun|manual_entry_present|rerun_r34_then_r35|
|R36-007|R35-007|R32-007|R28-025|f89r2|human_entry_present_ready_for_gate_rerun|manual_entry_present|rerun_r34_then_r35|
|R36-008|R35-008|R32-008|R28-026|f99r|human_entry_present_ready_for_gate_rerun|manual_entry_present|rerun_r34_then_r35|

## Instrucao manual

Abrir o HTML R32, revisar visualmente uma linha por vez e preencher na planilha R32 somente valores humanos explicitos. `manual_annotation_status` aceita `annotated`, `not_visible` ou `uncertain`; `manual_visual_notes` e obrigatorio para qualquer status preenchido.
