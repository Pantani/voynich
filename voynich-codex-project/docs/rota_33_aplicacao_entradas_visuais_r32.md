# Rota 33: aplicacao das entradas visuais R32

Esta rota aplica somente valores manuais explicitos da planilha R32 a uma copia derivada do pacote R28. Campos vazios, invalidos ou itens fora do alvo nao alteram o pacote.

Planilha R32: `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`.
Pacote R28 original: `data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`.
Pacote R28 derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/exact_form_visual_annotation_package_after_ready_entries_zl3b.csv`.
Log de aplicacao: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_entry_application_log_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_entry_application_summary_zl3b.csv`.

## Resultado curto

- entradas R32 avaliadas: 8;
- pendentes vazias: 0;
- validas: 8;
- invalidas: 0;
- linhas atualizadas no pacote derivado: 8;
- pacote R28 original nao foi alterado;
- guarda: `ready_visual_entry_application_not_visual_evidence`.

### Status de validacao

|item|n|
|---|---:|
|valid_manual_annotation|8|

### Aplicacao

|item|n|
|---|---:|
|applied_manual_annotation_to_derived_package|8|

### Acao no pacote

|item|n|
|---|---:|
|updated_derived_package_row|8|

## Itens

|rota33|rota32|rota28|status|aplicacao|acao|motivo|
|---|---|---|---|---|---|---|
|R33-001|R32-001|R28-001|valid_manual_annotation|applied_manual_annotation_to_derived_package|updated_derived_package_row|manual_annotation_fields_valid|
|R33-002|R32-002|R28-020|valid_manual_annotation|applied_manual_annotation_to_derived_package|updated_derived_package_row|manual_annotation_fields_valid|
|R33-003|R32-003|R28-021|valid_manual_annotation|applied_manual_annotation_to_derived_package|updated_derived_package_row|manual_annotation_fields_valid|
|R33-004|R32-004|R28-022|valid_manual_annotation|applied_manual_annotation_to_derived_package|updated_derived_package_row|manual_annotation_fields_valid|
|R33-005|R32-005|R28-023|valid_manual_annotation|applied_manual_annotation_to_derived_package|updated_derived_package_row|manual_annotation_fields_valid|
|R33-006|R32-006|R28-024|valid_manual_annotation|applied_manual_annotation_to_derived_package|updated_derived_package_row|manual_annotation_fields_valid|
|R33-007|R32-007|R28-025|valid_manual_annotation|applied_manual_annotation_to_derived_package|updated_derived_package_row|manual_annotation_fields_valid|
|R33-008|R32-008|R28-026|valid_manual_annotation|applied_manual_annotation_to_derived_package|updated_derived_package_row|manual_annotation_fields_valid|

## Leitura

A infraestrutura de aplicacao esta pronta. Como a planilha R32 ainda esta vazia, o pacote derivado preserva os campos manuais em branco e a Rota 31 continuara sem anotacoes derivadas ate existir preenchimento humano.
