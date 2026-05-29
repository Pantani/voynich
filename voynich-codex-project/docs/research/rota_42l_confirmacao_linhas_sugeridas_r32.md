# Rota 42L: confirmacao de linhas sugeridas

Esta rota transforma a fila R42K em uma tela de confirmacao humana para selecionar a linha visual antes de qualquer aplicacao.

Ela nao aplica automaticamente, nao e OCR, nao le EVA, nao traduz e nao cria evidencia visual.

Entrada R42K: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_review_priority_queue_zl3b.csv`.
Entrada R42F: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/ready_visual_line_zone_choice_zl3b.csv`.
CSV de confirmacao: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/ready_visual_line_choice_confirmation_zl3b.csv`.
Resumo: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_line_choice_confirmation_summary_zl3b.csv`.
HTML: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/docs/rota_42l_confirmacao_linhas_sugeridas_r32.html`.

## Resultado curto

- itens pendentes de confirmacao: 13;
- guarda: `line_choice_confirmation_not_evidence_or_ocr`.

### Buckets de origem

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
