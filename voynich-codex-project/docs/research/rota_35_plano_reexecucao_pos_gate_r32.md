# Rota 35: plano de reexecucao pos-gate R32

Esta rota decide se ha base manual para reexecutar R33 e R31 apos o gate R34. Ela nao chama os scripts de aplicacao/validacao quando o gate manual esta bloqueado.

Gate R34: `data/derived/ready_visual_annotation_manual_gate_zl3b.csv`.
Plano R35: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_post_gate_rerun_plan_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_post_gate_rerun_summary_zl3b.csv`.

## Resultado curto

- itens avaliados: 8;
- bloqueados pelo gate manual: 0;
- prontos para reexecucao controlada: 8;
- bloqueados por problema de gate: 0;
- reexecucoes R33/R31 planejadas agora: 8;
- guarda: `post_gate_rerun_not_visual_evidence`.

### Status R35

|item|n|
|---|---:|
|ready_for_controlled_rerun|8|

### Acao de reexecucao

|item|n|
|---|---:|
|rerun_r33_then_r31_for_explicit_entries|8|

### Proxima acao

|item|n|
|---|---:|
|run_r33_apply_entries_then_r31_validation|8|

### Status R34

|item|n|
|---|---:|
|ready_to_rerun_r33_r31|8|

## Itens

|rota35|rota34|rota32|rota28|status R34|status R35|acao|proxima acao|
|---|---|---|---|---|---|---|---|
|R35-001|R34-001|R32-001|R28-001|ready_to_rerun_r33_r31|ready_for_controlled_rerun|rerun_r33_then_r31_for_explicit_entries|run_r33_apply_entries_then_r31_validation|
|R35-002|R34-002|R32-002|R28-020|ready_to_rerun_r33_r31|ready_for_controlled_rerun|rerun_r33_then_r31_for_explicit_entries|run_r33_apply_entries_then_r31_validation|
|R35-003|R34-003|R32-003|R28-021|ready_to_rerun_r33_r31|ready_for_controlled_rerun|rerun_r33_then_r31_for_explicit_entries|run_r33_apply_entries_then_r31_validation|
|R35-004|R34-004|R32-004|R28-022|ready_to_rerun_r33_r31|ready_for_controlled_rerun|rerun_r33_then_r31_for_explicit_entries|run_r33_apply_entries_then_r31_validation|
|R35-005|R34-005|R32-005|R28-023|ready_to_rerun_r33_r31|ready_for_controlled_rerun|rerun_r33_then_r31_for_explicit_entries|run_r33_apply_entries_then_r31_validation|
|R35-006|R34-006|R32-006|R28-024|ready_to_rerun_r33_r31|ready_for_controlled_rerun|rerun_r33_then_r31_for_explicit_entries|run_r33_apply_entries_then_r31_validation|
|R35-007|R34-007|R32-007|R28-025|ready_to_rerun_r33_r31|ready_for_controlled_rerun|rerun_r33_then_r31_for_explicit_entries|run_r33_apply_entries_then_r31_validation|
|R35-008|R34-008|R32-008|R28-026|ready_to_rerun_r33_r31|ready_for_controlled_rerun|rerun_r33_then_r31_for_explicit_entries|run_r33_apply_entries_then_r31_validation|

## Leitura

A Rota 35 confirma que nao ha reexecucao responsavel de R33/R31 enquanto a planilha R32 estiver vazia. O proximo passo permanece manual: preencher a planilha R32 e reexecutar R34.
