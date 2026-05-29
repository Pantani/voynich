# Rota 34: gate manual de anotacao visual R32

Esta rota verifica se a planilha R32 ja recebeu anotacao humana suficiente para reexecutar R33 e R31. Ela nao interpreta imagens nem cria evidencia visual.

Planilha R32: `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`.
HTML R32: `docs/rota_32_pacote_html_anotacao_visual_prontos.html`.
Log R33: `data/derived/ready_visual_annotation_entry_application_log_zl3b.csv`.
Gate CSV: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_manual_gate_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_manual_gate_summary_zl3b.csv`.

## Resultado curto

- itens verificados: 8;
- bloqueados por anotacao manual pendente: 0;
- prontos para reexecutar R33/R31: 8;
- bloqueados por valores invalidos: 0;
- cartoes HTML presentes: 8;
- valores permitidos presentes no HTML: 8;
- guarda: `manual_visual_gate_not_evidence`.

### Status do gate

|item|n|
|---|---:|
|ready_to_rerun_r33_r31|8|

### Proxima acao

|item|n|
|---|---:|
|rerun_r33_then_r31_validation|8|

### Status manual

|item|n|
|---|---:|
|manual_annotation_filled|8|

### HTML

|item|n|
|---|---:|
|present|8|

## Itens

|rota34|rota32|rota33|rota28|folio|status manual|gate|proxima acao|
|---|---|---|---|---|---|---|---|
|R34-001|R32-001|R33-001|R28-001|f99v|manual_annotation_filled|ready_to_rerun_r33_r31|rerun_r33_then_r31_validation|
|R34-002|R32-002|R33-002|R28-020|f1r|manual_annotation_filled|ready_to_rerun_r33_r31|rerun_r33_then_r31_validation|
|R34-003|R32-003|R33-003|R28-021|f67r2|manual_annotation_filled|ready_to_rerun_r33_r31|rerun_r33_then_r31_validation|
|R34-004|R32-004|R33-004|R28-022|f67v1|manual_annotation_filled|ready_to_rerun_r33_r31|rerun_r33_then_r31_validation|
|R34-005|R32-005|R33-005|R28-023|f84r|manual_annotation_filled|ready_to_rerun_r33_r31|rerun_r33_then_r31_validation|
|R34-006|R32-006|R33-006|R28-024|f88v|manual_annotation_filled|ready_to_rerun_r33_r31|rerun_r33_then_r31_validation|
|R34-007|R32-007|R33-007|R28-025|f89r2|manual_annotation_filled|ready_to_rerun_r33_r31|rerun_r33_then_r31_validation|
|R34-008|R32-008|R33-008|R28-026|f99r|manual_annotation_filled|ready_to_rerun_r33_r31|rerun_r33_then_r31_validation|

## Leitura

O material operacional esta pronto, mas o gate permanece bloqueado por falta de anotacao visual humana. O proximo passo nao e inferir: e preencher `manual_annotation_status` e `manual_visual_notes` na planilha R32 usando o HTML R32.
