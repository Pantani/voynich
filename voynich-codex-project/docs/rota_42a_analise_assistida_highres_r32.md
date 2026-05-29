# Rota 42A: analise assistida das fontes Yale high-res para R32

Esta camada registra uma leitura visual assistida das imagens Yale/Beinecke baixadas na R42. Ela serve para orientar recorte, zoom e revisao humana. Ela nao preenche a R32, nao decide `annotated/not_visible/uncertain` e nao reabre a cadeia.

Fonte R42: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_highres_sources_zl3b.csv`.
CSV R42A: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_highres_ai_assist_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_highres_ai_assist_summary_zl3b.csv`.

## Resultado curto

- itens avaliados: 8;
- regioes claramente localizaveis: 2;
- regioes parcialmente localizaveis: 4;
- paginas compostas que exigem recorte/lado: 2;
- decisoes exatas de token tomadas pela IA: 0;
- cadeia ainda bloqueada: 8;
- guarda: `ai_highres_visual_assist_not_human_evidence`.

## Leitura

As fontes novas melhoram o trabalho de revisao. `f84r` e `f99r` ficaram com regioes de interesse prontas para recorte local; `f99v`, `f67r2` e `f67v1` tambem ficaram uteis, mas precisam de alinhamento fino de linhas, setores ou circulos. `f1r` continua relativamente apagado. `f88v` e `f89r2` exigem cuidado extra porque usam a mesma imagem composta Yale `88v and 89r`.

Nenhum item abaixo e uma anotacao manual. O proximo passo correto ainda e uma pessoa preencher `manual_annotation_status` e `manual_visual_notes` na R32 usando as fontes high-res.

### Qualidade visual assistida

|item|n|
|---|---:|
|high|5|
|medium_composite|2|
|medium_faint|1|

### Localizacao assistida da regiao

|item|n|
|---|---:|
|partial|4|
|partial_composite_page|2|
|yes_region|2|

### Acoes manuais sugeridas

|item|n|
|---|---:|
|crop_composite_foldout_plant_rows|1|
|crop_composite_foldout_recipe_rows|1|
|crop_label_rows_and_match_petersen_lines|1|
|crop_top_label_row|1|
|crop_upper_pool_text_lines|1|
|increase_contrast_crop_paragraph_starts|1|
|rotate_crop_circle_labels|1|
|rotate_crop_sector_and_red_line|1|

## Itens

|rota42A|rota32|folio|qualidade|regiao|decisao exata|acao manual sugerida|
|---|---|---|---|---|---|---|
|R42A-001|R32-001|f99v|high|partial|not_determined_requires_human_zoom|crop_label_rows_and_match_petersen_lines|
|R42A-002|R32-002|f1r|medium_faint|partial|not_determined_requires_human_zoom|increase_contrast_crop_paragraph_starts|
|R42A-003|R32-003|f67r2|high|partial|not_determined_requires_human_zoom|rotate_crop_sector_and_red_line|
|R42A-004|R32-004|f67v1|high|partial|not_determined_requires_human_zoom|rotate_crop_circle_labels|
|R42A-005|R32-005|f84r|high|yes_region|not_determined_requires_human_zoom|crop_upper_pool_text_lines|
|R42A-006|R32-006|f88v|medium_composite|partial_composite_page|not_determined_requires_human_zoom|crop_composite_foldout_recipe_rows|
|R42A-007|R32-007|f89r2|medium_composite|partial_composite_page|not_determined_requires_human_zoom|crop_composite_foldout_plant_rows|
|R42A-008|R32-008|f99r|high|yes_region|not_determined_requires_human_zoom|crop_top_label_row|
