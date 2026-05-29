# Rota 39: auditoria de execucao do preenchimento humano R32

Esta rota verifica se o preenchimento humano da planilha R32 foi executado. Ela nao grava decisoes, nao interpreta imagens e nao reabre a cadeia por inferencia.

Planilha R32: `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`.
Ordem R38: `data/derived/ready_visual_annotation_manual_reopen_work_order_zl3b.csv`.
Protocolo R36: `data/derived/ready_visual_annotation_manual_fill_protocol_zl3b.csv`.
Plano R37: `data/derived/ready_visual_annotation_revalidation_chain_plan_zl3b.csv`.
Auditoria R39: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_manual_fill_execution_audit_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_manual_fill_execution_audit_summary_zl3b.csv`.

## Resultado curto

- itens auditados: 8;
- preenchimento humano nao executado: 0;
- entradas manuais presentes exigindo refresh R36/R37: 0;
- prontos para reabrir cadeia: 8;
- entradas invalidas ou parciais: 0;
- planilha R32 original preservada;
- guarda: `manual_fill_execution_audit_not_visual_evidence`.

### Status de execucao

|item|n|
|---|---:|
|ready_for_revalidation_chain_reopen|8|

### Status de liberacao da cadeia

|item|n|
|---|---:|
|ready_to_reopen_chain|8|

### Proxima acao

|item|n|
|---|---:|
|rerun_r34_r35_r33_r31|8|

### Status R36

|item|n|
|---|---:|
|human_entry_present_ready_for_gate_rerun|8|

### Status R37

|item|n|
|---|---:|
|ready_for_revalidation_chain|8|

## Itens

|rota39|rota38|rota32|folio|execucao|liberacao|proxima acao|
|---|---|---|---|---|---|---|
|R39-001|R38-001|R32-001|f99v|ready_for_revalidation_chain_reopen|ready_to_reopen_chain|rerun_r34_r35_r33_r31|
|R39-002|R38-002|R32-002|f1r|ready_for_revalidation_chain_reopen|ready_to_reopen_chain|rerun_r34_r35_r33_r31|
|R39-003|R38-003|R32-003|f67r2|ready_for_revalidation_chain_reopen|ready_to_reopen_chain|rerun_r34_r35_r33_r31|
|R39-004|R38-004|R32-004|f67v1|ready_for_revalidation_chain_reopen|ready_to_reopen_chain|rerun_r34_r35_r33_r31|
|R39-005|R38-005|R32-005|f84r|ready_for_revalidation_chain_reopen|ready_to_reopen_chain|rerun_r34_r35_r33_r31|
|R39-006|R38-006|R32-006|f88v|ready_for_revalidation_chain_reopen|ready_to_reopen_chain|rerun_r34_r35_r33_r31|
|R39-007|R38-007|R32-007|f89r2|ready_for_revalidation_chain_reopen|ready_to_reopen_chain|rerun_r34_r35_r33_r31|
|R39-008|R38-008|R32-008|f99r|ready_for_revalidation_chain_reopen|ready_to_reopen_chain|rerun_r34_r35_r33_r31|

## Instrucao manual

Enquanto `fill_execution_status=manual_fill_not_executed`, preencher manualmente na R32 somente `manual_annotation_status` e `manual_visual_notes` usando a ordem R38 e o HTML R32. Depois reexecutar R36, R37 e esta auditoria antes de rodar R34/R35/R33/R31.
