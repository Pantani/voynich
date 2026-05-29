# Rota 42: fontes IIIF de alta resolucao para R32

Esta rota troca o apoio visual da R32 para fontes oficiais Yale/Beinecke em IIIF. Ela nao preenche anotacoes manuais e nao cria evidencia semantica.

Planilha R32: `voynich-codex-project/data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`.
Manifesto Yale IIIF usado: `voynich-codex-project/data/derived/yale_iiif_manifest_2002046.json`.
Fonte oficial: `https://collections.library.yale.edu/manifests/2002046`.
Pagina catalogo: `https://collections.library.yale.edu/catalog/2002046`.
CSV R42: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_highres_sources_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_highres_sources_summary_zl3b.csv`.
HTML high-res: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/docs/rota_42_pacote_html_yale_iiif_highres_r32.html`.

## Resultado curto

- itens avaliados: 8;
- matches exatos: 4;
- matches por folio colapsado: 2;
- matches por pagina composta: 2;
- sem match: 0;
- guarda: `highres_source_download_not_visual_evidence`.

### Status de match

|item|n|
|---|---:|
|matched_exact_manifest_label|4|
|matched_collapsed_folio|2|
|matched_composite_manifest_label|2|

### Status de download planejado

|item|n|
|---|---:|
|downloaded|8|

### Labels Yale

|item|n|
|---|---:|
|88v and 89r|2|
|1r|1|
|67r|1|
|67v|1|
|84r|1|
|99r|1|
|99v|1|

## Itens

|rota42|rota32|folio|label Yale|imagem Yale|dimensoes|local|
|---|---|---|---|---|---|---|
|R42-001|R32-001|f99v|99v|1006247|2802x3697|`images/raw/yale_iiif_r32/f99v_1006247.jpg`|
|R42-002|R32-002|f1r|1r|1006076|2972x3766|`images/raw/yale_iiif_r32/f1r_1006076.jpg`|
|R42-003|R32-003|f67r2|67r|1006194|4972x3738|`images/raw/yale_iiif_r32/f67r2_1006194.jpg`|
|R42-004|R32-004|f67v1|67v|1006195|5059x3753|`images/raw/yale_iiif_r32/f67v1_1006195.jpg`|
|R42-005|R32-005|f84r|84r|1006226|2753x3745|`images/raw/yale_iiif_r32/f84r_1006226.jpg`|
|R42-006|R32-006|f88v|88v and 89r|1006233|9078x3777|`images/raw/yale_iiif_r32/f88v_1006233.jpg`|
|R42-007|R32-007|f89r2|88v and 89r|1006233|9078x3777|`images/raw/yale_iiif_r32/f89r2_1006233.jpg`|
|R42-008|R32-008|f99r|99r|1006246|2702x3765|`images/raw/yale_iiif_r32/f99r_1006246.jpg`|
