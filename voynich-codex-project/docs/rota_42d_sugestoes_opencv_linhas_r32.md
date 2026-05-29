# Rota 42D: sugestoes OpenCV para calibracao inicial de linhas

Esta rota usa OpenCV para detectar faixas de tinta/texto nas imagens high-res e gerar sugestoes iniciais de baseline para a R42C.

As sugestoes nao sao evidencia visual, nao traduzem, nao preenchem a R32 e nao mudam a R42C para `calibrated`.
Quando a R42C e reexecutada depois da R42D, sugestoes validas podem ser mescladas como `baseline_points` pendentes para revisao humana.
Quando a R42F tiver escolhas de linha visual, a R42D tambem consome essas zonas pequenas para gerar novas sugestoes pendentes.
A pagina HTML mostra recorte real da linha sugerida quando a sugestao tem caixa visual, para diminuir a dependencia de codigo textual.

CSV: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_line_opencv_suggestions_zl3b.csv`.
Resumo: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_line_opencv_suggestions_summary_zl3b.csv`.
HTML: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/docs/rota_42d_sugestoes_opencv_linhas_r32.html`.

## Status

|status|n|
|---|---:|
|opencv_candidates_detected_needs_manual_zone|13|
|no_text_band_detected|4|
|opencv_suggested_needs_human_confirmation|2|

## O que o OpenCV resolveu sozinho

|acao automatica|n|
|---|---:|
|needs_manual_zone|13|
|needs_better_scan_or_manual_line|4|
|prefill_pending_baseline|2|

## Sugestoes prontas para conferir na R42C

|alvo ZL3b|linha visual OpenCV|baseline sugerida|confianca|acao OpenCV|proximo passo humano|
|---|---:|---|---:|---|---|
|f84r.24,+P0|6|`17.00,34.46 80.07,34.46`|0.41|prefill_pending_baseline|conferir se a linha acompanha o texto e marcar calibrada se estiver certa|
|f84r.29,+P0|14|`14.60,62.84 43.00,62.84`|0.45|prefill_pending_baseline|conferir se a linha acompanha o texto e marcar calibrada se estiver certa|

Guarda: `opencv_initial_line_suggestion_not_visual_evidence`.
