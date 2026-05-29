# Rota 32: pacote HTML focado para anotacoes visuais prontas

Esta rota cria uma superficie pequena para preencher manualmente os 8 itens da Rota 28 que ja tinham imagem no manifesto e continuam pendentes na Rota 31. O HTML/CSV nao cria evidencia visual por inferencia.

Pacote R28: `data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`.
Validacao R31: `data/derived/ready_visual_annotation_validation_zl3b.csv`.
Planilha manual R32: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_html_summary_zl3b.csv`.
Pacote HTML: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/docs/rota_32_pacote_html_anotacao_visual_prontos.html`.

## Resultado curto

- cartoes HTML: 8;
- pendentes R31: 8;
- `P0`: 1;
- `P1`: 7;
- locus `P`: 6;
- locus `L`: 2;
- campos manuais permanecem em branco;
- valores permitidos: `annotated/not_visible/uncertain`;
- guarda: `focused_visual_annotation_html_not_evidence`.

### Status do cartao

|item|n|
|---|---:|
|ready_for_focused_manual_visual_annotation|8|

### Status R31

|item|n|
|---|---:|
|pending_blank_manual_annotation|8|

### Prioridade

|item|n|
|---|---:|
|P1|7|
|P0|1|

### Tipo de locus

|item|n|
|---|---:|
|P|6|
|L|2|

## Itens

|rota32|rota31|rota28|folio|prioridade|locus|tokens|status R31|
|---|---|---|---|---|---|---|---|
|R32-001|R31-001|R28-001|f99v|P0|P|okol=4<br>okal=2<br>okor=1<br>otol=1|pending_blank_manual_annotation|
|R32-002|R31-002|R28-020|f1r|P1|P|okol=1<br>otol=1|pending_blank_manual_annotation|
|R32-003|R31-003|R28-021|f67r2|P1|P|okol=2|pending_blank_manual_annotation|
|R32-004|R31-004|R28-022|f67v1|P1|L|okal=1<br>okol=1|pending_blank_manual_annotation|
|R32-005|R31-005|R28-023|f84r|P1|P|okal=1<br>otar=1|pending_blank_manual_annotation|
|R32-006|R31-006|R28-024|f88v|P1|P|okol=1<br>otol=1|pending_blank_manual_annotation|
|R32-007|R31-007|R28-025|f89r2|P1|P|okar=1<br>otol=1|pending_blank_manual_annotation|
|R32-008|R31-008|R28-026|f99r|P1|L|okar=1<br>okor=1|pending_blank_manual_annotation|

## Cartoes

### R32-001: f99v / R28-001

- R31: `R31-001`;
- prioridade: `P0`;
- locus: `P`;
- tokens: `okol=4|okal=2|okor=1|otol=1`;
- valores permitidos: `annotated/not_visible/uncertain`;
- campos a preencher: `manual_annotation_status manual_visual_notes`;
- regra de saida: `copy_completed_fields_back_to_route28_package_then_rerun_route31`;
- guarda: `focused_visual_annotation_html_not_evidence`.

### R32-002: f1r / R28-020

- R31: `R31-002`;
- prioridade: `P1`;
- locus: `P`;
- tokens: `okol=1|otol=1`;
- valores permitidos: `annotated/not_visible/uncertain`;
- campos a preencher: `manual_annotation_status manual_visual_notes`;
- regra de saida: `copy_completed_fields_back_to_route28_package_then_rerun_route31`;
- guarda: `focused_visual_annotation_html_not_evidence`.

### R32-003: f67r2 / R28-021

- R31: `R31-003`;
- prioridade: `P1`;
- locus: `P`;
- tokens: `okol=2`;
- valores permitidos: `annotated/not_visible/uncertain`;
- campos a preencher: `manual_annotation_status manual_visual_notes`;
- regra de saida: `copy_completed_fields_back_to_route28_package_then_rerun_route31`;
- guarda: `focused_visual_annotation_html_not_evidence`.

### R32-004: f67v1 / R28-022

- R31: `R31-004`;
- prioridade: `P1`;
- locus: `L`;
- tokens: `okal=1|okol=1`;
- valores permitidos: `annotated/not_visible/uncertain`;
- campos a preencher: `manual_annotation_status manual_visual_notes`;
- regra de saida: `copy_completed_fields_back_to_route28_package_then_rerun_route31`;
- guarda: `focused_visual_annotation_html_not_evidence`.

### R32-005: f84r / R28-023

- R31: `R31-005`;
- prioridade: `P1`;
- locus: `P`;
- tokens: `okal=1|otar=1`;
- valores permitidos: `annotated/not_visible/uncertain`;
- campos a preencher: `manual_annotation_status manual_visual_notes`;
- regra de saida: `copy_completed_fields_back_to_route28_package_then_rerun_route31`;
- guarda: `focused_visual_annotation_html_not_evidence`.

### R32-006: f88v / R28-024

- R31: `R31-006`;
- prioridade: `P1`;
- locus: `P`;
- tokens: `okol=1|otol=1`;
- valores permitidos: `annotated/not_visible/uncertain`;
- campos a preencher: `manual_annotation_status manual_visual_notes`;
- regra de saida: `copy_completed_fields_back_to_route28_package_then_rerun_route31`;
- guarda: `focused_visual_annotation_html_not_evidence`.

### R32-007: f89r2 / R28-025

- R31: `R31-007`;
- prioridade: `P1`;
- locus: `P`;
- tokens: `okar=1|otol=1`;
- valores permitidos: `annotated/not_visible/uncertain`;
- campos a preencher: `manual_annotation_status manual_visual_notes`;
- regra de saida: `copy_completed_fields_back_to_route28_package_then_rerun_route31`;
- guarda: `focused_visual_annotation_html_not_evidence`.

### R32-008: f99r / R28-026

- R31: `R31-008`;
- prioridade: `P1`;
- locus: `L`;
- tokens: `okar=1|okor=1`;
- valores permitidos: `annotated/not_visible/uncertain`;
- campos a preencher: `manual_annotation_status manual_visual_notes`;
- regra de saida: `copy_completed_fields_back_to_route28_package_then_rerun_route31`;
- guarda: `focused_visual_annotation_html_not_evidence`.

## Leitura

A rota reduz a friccao para uma revisao humana focada. Para transformar essas entradas em anotacoes derivadas, copie valores preenchidos de volta para o pacote R28 e reexecute a Rota 31.
