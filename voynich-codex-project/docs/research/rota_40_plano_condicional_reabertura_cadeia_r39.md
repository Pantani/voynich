# Rota 40: plano condicional de reabertura da cadeia R34/R35/R33/R31

Esta rota decide se a cadeia de revalidacao pode ser reaberta a partir da auditoria R39. Ela nao preenche a R32, nao interpreta imagens e nao executa a cadeia quando a R39 permanece bloqueada.

Auditoria R39: `data/derived/ready_visual_annotation_manual_fill_execution_audit_zl3b.csv`.
Plano R40: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_conditional_chain_reopen_plan_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_conditional_chain_reopen_summary_zl3b.csv`.
Ordem da cadeia: `R34>R35>R33>R31`.

## Resultado curto

- itens planejados: 8;
- bloqueados aguardando entrada humana: 0;
- bloqueados aguardando refresh R36/R37/R39: 0;
- prontos para rodar cadeia: 8;
- entradas invalidas: 0;
- guarda: `conditional_chain_reopen_plan_not_visual_evidence`.

### Status do plano

|item|n|
|---|---:|
|ready_to_run_revalidation_chain|8|

### Acao de cadeia planejada

|item|n|
|---|---:|
|run_R34_R35_R33_R31|8|

### Proxima acao

|item|n|
|---|---:|
|execute_chain_and_validate_outputs|8|

### Status de execucao R39

|item|n|
|---|---:|
|ready_for_revalidation_chain_reopen|8|

### Liberacao R39

|item|n|
|---|---:|
|ready_to_reopen_chain|8|

## Itens

|rota40|rota39|rota32|folio|status do plano|acao da cadeia|proxima acao|
|---|---|---|---|---|---|---|
|R40-001|R39-001|R32-001|f99v|ready_to_run_revalidation_chain|run_R34_R35_R33_R31|execute_chain_and_validate_outputs|
|R40-002|R39-002|R32-002|f1r|ready_to_run_revalidation_chain|run_R34_R35_R33_R31|execute_chain_and_validate_outputs|
|R40-003|R39-003|R32-003|f67r2|ready_to_run_revalidation_chain|run_R34_R35_R33_R31|execute_chain_and_validate_outputs|
|R40-004|R39-004|R32-004|f67v1|ready_to_run_revalidation_chain|run_R34_R35_R33_R31|execute_chain_and_validate_outputs|
|R40-005|R39-005|R32-005|f84r|ready_to_run_revalidation_chain|run_R34_R35_R33_R31|execute_chain_and_validate_outputs|
|R40-006|R39-006|R32-006|f88v|ready_to_run_revalidation_chain|run_R34_R35_R33_R31|execute_chain_and_validate_outputs|
|R40-007|R39-007|R32-007|f89r2|ready_to_run_revalidation_chain|run_R34_R35_R33_R31|execute_chain_and_validate_outputs|
|R40-008|R39-008|R32-008|f99r|ready_to_run_revalidation_chain|run_R34_R35_R33_R31|execute_chain_and_validate_outputs|

## Regra de liberacao

Executar `R34>R35>R33>R31` somente quando `reopen_plan_status=ready_to_run_revalidation_chain`. Qualquer outro status preserva o bloqueio manual.
