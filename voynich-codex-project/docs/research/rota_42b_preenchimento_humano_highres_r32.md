# Rota 42B: ferramenta guiada de preenchimento humano R32 high-res

Esta rota cria um HTML estatico e guiado para preencher manualmente a R32 usando as imagens Yale/Beinecke high-res da R42, a orientacao assistida da R42A e, quando disponiveis, as baselines calibradas da R42C. A ferramenta mostra um item por vez e reduz a decisao para `Achei`, `Nao achei` ou `Nao sei`. Ela oferece zoom, contraste, rotacao, fila de revisao, guia rapido, alvo simplificado por tokens/linhas, total de entradas/loci ZL3b por folio, lista auditavel das entradas que originam esse total, texto de referencia das linhas alvo, cartoes visuais EVA para comparar o desenho da palavra com a imagem, recortes reais da pagina para olhar primeiro, baselines calibradas ou zonas visuais provaveis dos blocos alvo, nota automatica acionada pelo clique do revisor, detalhes tecnicos recolhidos e rascunho CSV escondido ate o final. O HTML nao grava a planilha R32 e nao cria evidencia visual sozinho; ajustes visuais de zona sao temporarios e voltam ao mapa calibrado ao recarregar.

Fontes R42: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_highres_sources_zl3b.csv`.
Orientacao R42A: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_highres_ai_assist_zl3b.csv`.
Alvo humano: `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`.
CSV R42B: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_highres_human_fill_html_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_highres_human_fill_html_summary_zl3b.csv`.
HTML: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/docs/rota_42b_pacote_html_preenchimento_humano_r32.html`.

## Resultado curto

- itens de revisao guiada: 8;
- primeiro bloco claro: 2;
- bloco intermediario parcial: 3;
- fonte apagada: 1;
- paginas compostas finais: 2;
- controles: fila lateral, item ativo, proximo pendente, zoom, contraste, rotacao, mostrar/esconder zonas, subir/descer zonas, reset de vista e atalho para calibrar linhas na R42C;
- modo ultrassimples: guia rapido, pergunta `Voce achou essas palavrinhas?`, cartoes visuais EVA, recortes reais da pagina, total de entradas/loci ZL3b por folio, lista auditavel das entradas que originam o total, texto de referencia das linhas alvo, baselines calibradas quando R42C estiver preenchida, zonas provaveis quando a linha ainda estiver pendente, botoes `Achei`/`Nao achei`/`Nao sei`, nota automatica e detalhes tecnicos recolhidos;
- observacao: as baselines R42C sao apoio operacional de localizacao, nao evidencia automatica; quando uma baseline ainda nao existe, as zonas visuais continuam sendo orientacao aproximada de bloco, nao linha exata ou coordenada exata; a ferramenta nao calcula posicao visual por proporcao da numeracao ZL3b; o total por folio segue entradas/loci ZL3b e nao e uma contagem visual direta da imagem; deslocamentos de zona nao sao gravados no rascunho local para manter recarga idempotente;
- campos gerados: `manual_annotation_status` e `manual_visual_notes`;
- guarda: `highres_human_fill_html_not_visual_evidence`.

### Grupos de revisao

|item|n|
|---|---:|
|middle_partial_regions|3|
|first_clear_regions|2|
|last_composite_pages|2|
|faint_source|1|

### Qualidade assistida

|item|n|
|---|---:|
|high|5|
|medium_composite|2|
|medium_faint|1|

### Regiao assistida

|item|n|
|---|---:|
|partial|4|
|partial_composite_page|2|
|yes_region|2|

## Itens

|rota42B|rota32|folio|grupo|qualidade|acao sugerida|
|---|---|---|---|---|---|
|R42B-001|R32-005|f84r|first_clear_regions|high|crop_upper_pool_text_lines|
|R42B-002|R32-008|f99r|first_clear_regions|high|crop_top_label_row|
|R42B-003|R32-001|f99v|middle_partial_regions|high|crop_label_rows_and_match_petersen_lines|
|R42B-004|R32-003|f67r2|middle_partial_regions|high|rotate_crop_sector_and_red_line|
|R42B-005|R32-004|f67v1|middle_partial_regions|high|rotate_crop_circle_labels|
|R42B-006|R32-002|f1r|faint_source|medium_faint|increase_contrast_crop_paragraph_starts|
|R42B-007|R32-006|f88v|last_composite_pages|medium_composite|crop_composite_foldout_recipe_rows|
|R42B-008|R32-007|f89r2|last_composite_pages|medium_composite|crop_composite_foldout_plant_rows|
