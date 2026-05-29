# Rota 28: pacote de anotacao visual das formas exatas P0/P1

Esta rota transforma a fila P0/P1 da Rota 27 em um pacote de anotacao. Ela separa itens com imagem pronta dos itens que exigem fonte de imagem e nao preenche evidencia visual por inferencia.

Fonte R27: `voynich-codex-project/data/derived/exact_form_visual_gap_queue_zl3b.csv`.
Pacote CSV: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/exact_form_visual_annotation_package_summary_zl3b.csv`.
Pacote HTML: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/docs/rota_28_pacote_anotacao_visual_formas_exatas.html`.

## Resultado curto

- itens no pacote: 26;
- P0: 1;
- P1: 25;
- prontos para anotacao manual: 8;
- bloqueados por falta de imagem: 18;
- campos manuais permanecem em branco;
- guarda: `visual_annotation_package_not_evidence`.

### Prioridade

|item|n|
|---|---:|
|P1|25|
|P0|1|

### Status do pacote

|item|n|
|---|---:|
|blocked_pending_source_image|18|
|ready_for_manual_visual_annotation|8|

### Fluxo de trabalho

|item|n|
|---|---:|
|source_image_required|18|
|annotate_from_manifest_image|8|

### Tipo de locus

|item|n|
|---|---:|
|P|23|
|L|2|
|C|1|

## Itens

|rota28|rota27|prioridade|folio|locus|lacunas|tokens|status|
|---|---|---|---|---|---:|---|---|
|R28-001|R27-001|P0|f99v|P|8|okol=4<br>okal=2<br>okor=1<br>otol=1|ready_for_manual_visual_annotation|
|R28-002|R27-002|P1|f113v|P|26|otar=8<br>okar=7<br>okal=5<br>otal=2<br>otor=2<br>okol=1<br>otol=1|blocked_pending_source_image|
|R28-003|R27-003|P1|f58v|P|23|okal=12<br>okar=4<br>otal=4<br>okor=2<br>otol=1|blocked_pending_source_image|
|R28-004|R27-004|P1|f86v6|P|20|otar=6<br>okar=5<br>otal=5<br>otol=2<br>okal=1<br>otor=1|blocked_pending_source_image|
|R28-005|R27-005|P1|fRos|C|20|okal=7<br>otar=5<br>okar=3<br>okor=2<br>otal=1<br>otol=1<br>otor=1|blocked_pending_source_image|
|R28-006|R27-006|P1|f107v|P|18|otal=7<br>okal=5<br>otar=3<br>okar=1<br>okol=1<br>otol=1|blocked_pending_source_image|
|R28-007|R27-007|P1|f104r|P|16|okar=9<br>okal=3<br>otar=2<br>otal=1<br>otor=1|blocked_pending_source_image|
|R28-008|R27-008|P1|f107r|P|16|otal=6<br>okal=5<br>otar=3<br>okar=1<br>otor=1|blocked_pending_source_image|
|R28-009|R27-009|P1|f86v5|P|16|otal=7<br>otar=3<br>okar=2<br>otol=2<br>okal=1<br>okol=1|blocked_pending_source_image|
|R28-010|R27-010|P1|f108r|P|15|otal=5<br>okar=4<br>okal=3<br>okol=1<br>okor=1<br>otol=1|blocked_pending_source_image|
|R28-011|R27-011|P1|f116r|P|12|otal=5<br>otar=4<br>okal=1<br>okar=1<br>otor=1|blocked_pending_source_image|
|R28-012|R27-012|P1|f58r|P|12|otal=4<br>otar=4<br>okal=3<br>okar=1|blocked_pending_source_image|
|R28-013|R27-013|P1|f75r|P|12|otar=6<br>okar=4<br>okal=1<br>otol=1|blocked_pending_source_image|
|R28-014|R27-014|P1|f85r1|P|11|otar=4<br>okar=3<br>okal=1<br>otal=1<br>otol=1<br>otor=1|blocked_pending_source_image|
|R28-015|R27-015|P1|f105v|P|10|otar=5<br>otal=2<br>okal=1<br>okol=1<br>otor=1|blocked_pending_source_image|
|R28-016|R27-016|P1|f106v|P|10|okal=4<br>otal=2<br>otar=2<br>otol=1<br>otor=1|blocked_pending_source_image|
|R28-017|R27-017|P1|f112r|P|10|okal=3<br>otar=3<br>okar=2<br>otal=2|blocked_pending_source_image|
|R28-018|R27-018|P1|f114r|P|10|okar=3<br>otar=3<br>otal=2<br>okol=1<br>otol=1|blocked_pending_source_image|
|R28-019|R27-019|P1|f84v|P|10|otal=3<br>okal=2<br>okar=2<br>otol=2<br>okol=1|blocked_pending_source_image|
|R28-020|R27-020|P1|f1r|P|2|okol=1<br>otol=1|ready_for_manual_visual_annotation|
|R28-021|R27-021|P1|f67r2|P|2|okol=2|ready_for_manual_visual_annotation|
|R28-022|R27-022|P1|f67v1|L|2|okal=1<br>okol=1|ready_for_manual_visual_annotation|
|R28-023|R27-023|P1|f84r|P|2|okal=1<br>otar=1|ready_for_manual_visual_annotation|
|R28-024|R27-024|P1|f88v|P|2|okol=1<br>otol=1|ready_for_manual_visual_annotation|
|R28-025|R27-025|P1|f89r2|P|2|okar=1<br>otol=1|ready_for_manual_visual_annotation|
|R28-026|R27-026|P1|f99r|L|2|okar=1<br>okor=1|ready_for_manual_visual_annotation|

## Leitura

O pacote define trabalho revisavel. Itens bloqueados precisam primeiro de imagem fonte; itens prontos ainda dependem de anotacao manual explicita.
