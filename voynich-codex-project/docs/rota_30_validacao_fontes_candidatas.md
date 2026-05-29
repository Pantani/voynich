# Rota 30: validacao de fontes candidatas

Esta rota valida candidatos da Rota 29 e aplica somente fontes estruturalmente validas a uma copia derivada do manifesto. Ela nao confirma conteudo visual nem atualiza o manifesto original.

Fila R29: `voynich-codex-project/data/annotations/exact_form_missing_source_queue_p0_p1_zl3b.csv`.
Manifesto original: `voynich-codex-project/data/commons_image_sources.csv`.
Log de validacao: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/missing_source_candidate_validation_zl3b.csv`.
Manifesto derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/commons_image_sources_after_source_validation_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/missing_source_candidate_validation_summary_zl3b.csv`.

## Resultado curto

- candidatos avaliados: 18;
- pendentes vazios: 18;
- validos estruturalmente: 0;
- invalidos: 0;
- linhas anexadas ao manifesto derivado: 0;
- guarda: `source_validation_not_visual_evidence`.

### Status de validacao

|item|n|
|---|---:|
|pending_blank_source_candidate|18|

### Aplicacao

|item|n|
|---|---:|
|skipped_blank_source_candidate|18|

### Validade do candidato

|item|n|
|---|---:|
|no|18|

## Itens

|rota30|rota29|folio|status|aplicacao|motivo|
|---|---|---|---|---|---|
|R30-001|R29-001|f113v|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-002|R29-002|f58v|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-003|R29-003|f86v6|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-004|R29-004|fRos|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-005|R29-005|f107v|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-006|R29-006|f104r|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-007|R29-007|f107r|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-008|R29-008|f86v5|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-009|R29-009|f108r|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-010|R29-010|f116r|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-011|R29-011|f58r|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-012|R29-012|f75r|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-013|R29-013|f85r1|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-014|R29-014|f105v|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-015|R29-015|f106v|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-016|R29-016|f112r|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-017|R29-017|f114r|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|
|R30-018|R29-018|f84v|pending_blank_source_candidate|skipped_blank_source_candidate|candidate_fields_blank|

## Leitura

Campos vazios continuam pendentes. URLs com formato correto ainda sao apenas fontes candidatas estruturalmente validas; a anotacao visual continua exigindo revisao separada.
