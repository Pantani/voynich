# Rota 42K: fila priorizada para revisao visual

Esta rota cruza as pendencias da R42F com os fragmentos visuais da R42J para ordenar a proxima revisao humana.

Ela nao escolhe linha sozinha, nao e OCR, nao le EVA, nao traduz e nao cria evidencia de palavra.

Entrada R42F: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/ready_visual_line_zone_choice_zl3b.csv`.
Entrada R42J: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_word_opencv_map_zl3b.csv`.
CSV da fila: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_review_priority_queue_zl3b.csv`.
Resumo: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_review_priority_queue_summary_zl3b.csv`.
HTML: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/docs/rota_42k_fila_priorizada_revisao_visual_r32.html`.

## Resultado curto

- itens pendentes priorizados: 13;
- revisar primeiro: 4;
- revisar depois: 4;
- revisao dificil: 5;
- guarda: `visual_review_priority_not_evidence_or_ocr`.

### Buckets

|item|n|
|---|---:|
|revisao_dificil|5|
|revisar_depois|4|
|revisar_primeiro|4|

### Folios

|item|n|
|---|---:|
|f99v|5|
|f1r|2|
|f67r2|2|
|f67v1|2|
|f99r|2|

### Prioridade

|item|n|
|---|---:|
|P1|8|
|P0|5|
