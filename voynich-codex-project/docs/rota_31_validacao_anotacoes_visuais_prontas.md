# Rota 31: validacao de anotacoes visuais manuais prontas

Esta rota valida somente os itens da Rota 28 que ja tinham imagem no manifesto. Campos manuais vazios continuam pendentes e nenhuma anotacao visual e criada por inferencia.

Pacote R28: `data/derived/exact_form_visual_annotation_package_after_ready_entries_zl3b.csv`.
Log de validacao: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_validation_zl3b.csv`.
Anotacoes validas derivadas: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_manual_visual_annotations_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_validation_summary_zl3b.csv`.

## Resultado curto

- itens prontos avaliados: 8;
- pendentes vazios: 0;
- validos: 8;
- invalidos: 0;
- anotacoes derivadas gravadas: 8;
- guarda: `manual_visual_annotation_not_axis_meaning`.

### Status de validacao

|item|n|
|---|---:|
|valid_manual_annotation|8|

### Aplicacao

|item|n|
|---|---:|
|manual_annotation_recorded|8|

### Validade manual

|item|n|
|---|---:|
|yes|8|

## Itens

|rota31|rota28|folio|status|aplicacao|motivo|
|---|---|---|---|---|---|
|R31-001|R28-001|f99v|valid_manual_annotation|manual_annotation_recorded|manual_annotation_fields_valid|
|R31-002|R28-020|f1r|valid_manual_annotation|manual_annotation_recorded|manual_annotation_fields_valid|
|R31-003|R28-021|f67r2|valid_manual_annotation|manual_annotation_recorded|manual_annotation_fields_valid|
|R31-004|R28-022|f67v1|valid_manual_annotation|manual_annotation_recorded|manual_annotation_fields_valid|
|R31-005|R28-023|f84r|valid_manual_annotation|manual_annotation_recorded|manual_annotation_fields_valid|
|R31-006|R28-024|f88v|valid_manual_annotation|manual_annotation_recorded|manual_annotation_fields_valid|
|R31-007|R28-025|f89r2|valid_manual_annotation|manual_annotation_recorded|manual_annotation_fields_valid|
|R31-008|R28-026|f99r|valid_manual_annotation|manual_annotation_recorded|manual_annotation_fields_valid|

## Leitura

A rota deixa pronta a validacao das anotacoes dos 8 itens com imagem. Enquanto os campos manuais estiverem vazios, nada entra na tabela derivada de anotacoes.
