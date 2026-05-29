# Rota 37: plano de revalidacao R34/R35/R33/R31

Esta rota verifica se o protocolo R36 ja permite reexecutar a cadeia R34/R35/R33/R31. Ela nao roda a cadeia quando nao ha entrada humana pronta.

Protocolo R36: `data/derived/ready_visual_annotation_manual_fill_protocol_zl3b.csv`.
Plano R37: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_revalidation_chain_plan_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_revalidation_chain_summary_zl3b.csv`.

## Resultado curto

- itens avaliados: 8;
- bloqueados sem entrada humana: 0;
- prontos para cadeia de revalidacao: 8;
- bloqueados por entradas invalidas: 0;
- execucoes da cadeia planejadas agora: 8;
- ordem de cadeia: `R34>R35>R33>R31`;
- guarda: `revalidation_chain_not_visual_evidence`.

### Status R37

|item|n|
|---|---:|
|ready_for_revalidation_chain|8|

### Acao da cadeia

|item|n|
|---|---:|
|run_r34_r35_r33_r31_in_order|8|

### Proxima acao

|item|n|
|---|---:|
|rerun_chain_and_review_r31_valid_annotations|8|

### Status R36

|item|n|
|---|---:|
|human_entry_present_ready_for_gate_rerun|8|

## Itens

|rota37|rota36|rota32|rota28|status R36|status R37|acao|proxima acao|
|---|---|---|---|---|---|---|---|
|R37-001|R36-001|R32-001|R28-001|human_entry_present_ready_for_gate_rerun|ready_for_revalidation_chain|run_r34_r35_r33_r31_in_order|rerun_chain_and_review_r31_valid_annotations|
|R37-002|R36-002|R32-002|R28-020|human_entry_present_ready_for_gate_rerun|ready_for_revalidation_chain|run_r34_r35_r33_r31_in_order|rerun_chain_and_review_r31_valid_annotations|
|R37-003|R36-003|R32-003|R28-021|human_entry_present_ready_for_gate_rerun|ready_for_revalidation_chain|run_r34_r35_r33_r31_in_order|rerun_chain_and_review_r31_valid_annotations|
|R37-004|R36-004|R32-004|R28-022|human_entry_present_ready_for_gate_rerun|ready_for_revalidation_chain|run_r34_r35_r33_r31_in_order|rerun_chain_and_review_r31_valid_annotations|
|R37-005|R36-005|R32-005|R28-023|human_entry_present_ready_for_gate_rerun|ready_for_revalidation_chain|run_r34_r35_r33_r31_in_order|rerun_chain_and_review_r31_valid_annotations|
|R37-006|R36-006|R32-006|R28-024|human_entry_present_ready_for_gate_rerun|ready_for_revalidation_chain|run_r34_r35_r33_r31_in_order|rerun_chain_and_review_r31_valid_annotations|
|R37-007|R36-007|R32-007|R28-025|human_entry_present_ready_for_gate_rerun|ready_for_revalidation_chain|run_r34_r35_r33_r31_in_order|rerun_chain_and_review_r31_valid_annotations|
|R37-008|R36-008|R32-008|R28-026|human_entry_present_ready_for_gate_rerun|ready_for_revalidation_chain|run_r34_r35_r33_r31_in_order|rerun_chain_and_review_r31_valid_annotations|

## Leitura

A cadeia de revalidacao esta descrita, mas deve permanecer parada enquanto R36 indicar `awaiting_human_visual_entry`. O proximo passo continua sendo preencher a planilha R32 a partir do HTML R32.
