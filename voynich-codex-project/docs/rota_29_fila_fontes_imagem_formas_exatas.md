# Rota 29: fila de fontes de imagem ausentes

Esta rota transforma os itens bloqueados da Rota 28 em uma fila de busca de fonte publica. Ela nao adiciona URLs candidatas por inferencia e nao cria evidencia visual.

Fonte R28: `voynich-codex-project/data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`.
Fila CSV: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/exact_form_missing_source_queue_p0_p1_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/exact_form_missing_source_summary_zl3b.csv`.
Pacote HTML: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/docs/rota_29_fila_fontes_imagem_formas_exatas.html`.

## Resultado curto

- fontes pendentes: 18;
- status: `pending_public_source_verification`;
- acao de manifesto: `do_not_update_manifest_until_url_verified`;
- campos candidatos permanecem em branco;
- guarda: `missing_source_queue_not_visual_evidence`.

### Prioridade

|item|n|
|---|---:|
|P1|18|

### Tipo de locus

|item|n|
|---|---:|
|P|17|
|C|1|

### Folios

|item|n|
|---|---:|
|f104r|1|
|f105v|1|
|f106v|1|
|f107r|1|
|f107v|1|
|f108r|1|
|f112r|1|
|f113v|1|
|f114r|1|
|f116r|1|
|f58r|1|
|f58v|1|
|f75r|1|
|f84v|1|
|f85r1|1|
|f86v5|1|
|f86v6|1|
|fRos|1|

## Itens

|rota29|rota28|prioridade|folio|locus|lacunas|consulta|campos|
|---|---|---|---|---|---:|---|---|
|R29-001|R28-002|P1|f113v|P|26|Voynich Manuscript f113v|candidate_commons_page candidate_image_url source_notes|
|R29-002|R28-003|P1|f58v|P|23|Voynich Manuscript f58v|candidate_commons_page candidate_image_url source_notes|
|R29-003|R28-004|P1|f86v6|P|20|Voynich Manuscript f86v6|candidate_commons_page candidate_image_url source_notes|
|R29-004|R28-005|P1|fRos|C|20|Voynich Manuscript fRos|candidate_commons_page candidate_image_url source_notes|
|R29-005|R28-006|P1|f107v|P|18|Voynich Manuscript f107v|candidate_commons_page candidate_image_url source_notes|
|R29-006|R28-007|P1|f104r|P|16|Voynich Manuscript f104r|candidate_commons_page candidate_image_url source_notes|
|R29-007|R28-008|P1|f107r|P|16|Voynich Manuscript f107r|candidate_commons_page candidate_image_url source_notes|
|R29-008|R28-009|P1|f86v5|P|16|Voynich Manuscript f86v5|candidate_commons_page candidate_image_url source_notes|
|R29-009|R28-010|P1|f108r|P|15|Voynich Manuscript f108r|candidate_commons_page candidate_image_url source_notes|
|R29-010|R28-011|P1|f116r|P|12|Voynich Manuscript f116r|candidate_commons_page candidate_image_url source_notes|
|R29-011|R28-012|P1|f58r|P|12|Voynich Manuscript f58r|candidate_commons_page candidate_image_url source_notes|
|R29-012|R28-013|P1|f75r|P|12|Voynich Manuscript f75r|candidate_commons_page candidate_image_url source_notes|
|R29-013|R28-014|P1|f85r1|P|11|Voynich Manuscript f85r1|candidate_commons_page candidate_image_url source_notes|
|R29-014|R28-015|P1|f105v|P|10|Voynich Manuscript f105v|candidate_commons_page candidate_image_url source_notes|
|R29-015|R28-016|P1|f106v|P|10|Voynich Manuscript f106v|candidate_commons_page candidate_image_url source_notes|
|R29-016|R28-017|P1|f112r|P|10|Voynich Manuscript f112r|candidate_commons_page candidate_image_url source_notes|
|R29-017|R28-018|P1|f114r|P|10|Voynich Manuscript f114r|candidate_commons_page candidate_image_url source_notes|
|R29-018|R28-019|P1|f84v|P|10|Voynich Manuscript f84v|candidate_commons_page candidate_image_url source_notes|

## Leitura

A fila separa busca de fonte de anotacao visual. O manifesto so deve ser atualizado depois que `candidate_commons_page` e `candidate_image_url` forem verificados manualmente como fonte publica adequada.
