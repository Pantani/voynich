# Rota 42F: escolha simples de linhas visuais sem zona

Esta rota cria uma ferramenta local para resolver os casos em que o OpenCV encontrou linhas na imagem, mas ainda nao sabe qual linha corresponde ao locus ZL3b.

A escolha gera zonas pequenas para a R42D consumir depois. Ela nao preenche a R32, nao traduz e nao confirma evidencia visual sozinha.

CSV: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/ready_visual_line_zone_choice_zl3b.csv`.
Resumo: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_line_zone_choice_summary_zl3b.csv`.
HTML: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/docs/rota_42f_escolha_linhas_visuais_sem_zona_r32.html`.

## Resultado curto

- alvos que precisam escolher linha visual: 13;
- fluxo: abrir a pagina, comparar recortes reais das linhas com o desenho de referencia, clicar no recorte `Essa e a linha`, copiar/baixar o CSV e reexecutar a R42D;
- guarda: `line_zone_choice_not_visual_evidence`.

### Status

|item|n|
|---|---:|
|pending_zone_choice|13|

### Folios

|item|n|
|---|---:|
|f99v|5|
|f1r|2|
|f67r2|2|
|f67v1|2|
|f99r|2|
