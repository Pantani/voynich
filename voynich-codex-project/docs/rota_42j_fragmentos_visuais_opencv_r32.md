# Rota 42J: fragmentos visuais OpenCV dentro das linhas

Esta rota faz uma analise mais fina por computer vision: dentro das linhas visuais da R42E, ela separa pedacos de tinta em fragmentos visuais parecidos com palavras.

Ela nao e OCR, nao le EVA, nao traduz, nao confirma palavra e nao preenche a R32.

Entrada: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_line_opencv_map_zl3b.csv`.
CSV de fragmentos: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_word_opencv_map_zl3b.csv`.
Resumo: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_word_opencv_map_summary_zl3b.csv`.
HTML: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/docs/rota_42j_fragmentos_visuais_opencv_r32.html`.

## Resultado curto

- OpenCV disponivel: sim;
- fragmentos visuais detectados: 77;
- uso correto: abrir R42J para comparar recortes de fragmentos dentro de uma linha visual, depois voltar para R42F/R42C;
- guarda: `opencv_visual_fragment_map_not_ocr_or_word_evidence`.

### Fragmentos por folio

|item|n|
|---|---:|
|f84r|42|
|f67r2|16|
|f99v|8|
|f99r|7|
|f1r|3|
|f67v1|1|

### Fragmentos por linha visual

|item|n|
|---|---:|
|f67r2 linha 2|9|
|f67r2 linha 3|7|
|f84r linha 23|5|
|f84r linha 4|5|
|f84r linha 12|4|
|f99r linha 4|3|
|f1r linha 2|2|
|f84r linha 10|2|
|f84r linha 11|2|
|f84r linha 14|2|
|f84r linha 17|2|
|f84r linha 2|2|
|f84r linha 22|2|
|f84r linha 5|2|
|f84r linha 6|2|
|f99v linha 11|2|
|f1r linha 4|1|
|f67v1 linha 1|1|
|f84r linha 1|1|
|f84r linha 13|1|
|f84r linha 15|1|
|f84r linha 16|1|
|f84r linha 18|1|
|f84r linha 19|1|
|f84r linha 20|1|
|f84r linha 21|1|
|f84r linha 3|1|
|f84r linha 7|1|
|f84r linha 8|1|
|f84r linha 9|1|
|f99r linha 1|1|
|f99r linha 2|1|
|f99r linha 5|1|
|f99r linha 6|1|
|f99v linha 12|1|
|f99v linha 13|1|
|f99v linha 15|1|
|f99v linha 2|1|
|f99v linha 3|1|
|f99v linha 9|1|
