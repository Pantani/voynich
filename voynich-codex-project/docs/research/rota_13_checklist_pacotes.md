# Rota 13: checklist item-a-item por pacote

Esta rota gera uma folha preenchivel para revisar cada item dos pacotes Rota 12. Ela preserva rastreabilidade e deixa campos manuais vazios por desenho.

Fonte: `voynich-codex-project/data/annotations/folio_review_packet_items_zl3b.csv`.
Checklist: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/packet_item_checklist_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/packet_item_checklist_summary_zl3b.csv`.

## Resultado curto

- itens na checklist: 11;
- itens para procurar tokens faltantes: 8;
- itens para apertar tokens ja anotados: 3;
- todos os campos manuais ficam vazios ate revisao visual real;
- nenhuma linha autoriza leitura semantica dos eixos.

### Itens por pacote

|item|n|
|---|---:|
|R12-001|5|
|R12-002|3|
|R12-004|2|
|R12-003|1|

### Tipo de alvo

|item|n|
|---|---:|
|missing_group_tokens|8|
|matched_group_tokens|3|

### Status inicial

|item|n|
|---|---:|
|pending_visual_check|11|

### Prioridade

|item|n|
|---|---:|
|P1_core_missing_tokens|4|
|P3_tighten_existing_region|3|
|P0_operator_missing_tokens|2|
|P2_other_missing_tokens|2|

## Checklist

|checklist|pacote|rota11|folio|locus|alvo|tipo|status|
|---|---|---|---|---|---|---|---|
|R13-001|R12-001|R11-002|f67r1|f67r1.5,@Cc|otardar|missing_group_tokens|pending_visual_check|
|R13-002|R12-001|R11-003|f67r1|f67r1.6,+Cc|chedar cheol cheor|missing_group_tokens|pending_visual_check|
|R13-003|R12-001|R11-006|f67r1|f67r1.6,+Cc|dol|missing_group_tokens|pending_visual_check|
|R13-004|R12-001|R11-009|f67r1|f67r1.5,@Cc|ar ol|matched_group_tokens|pending_visual_check|
|R13-005|R12-001|R11-010|f67r1|f67r1.6,+Cc|al ar|matched_group_tokens|pending_visual_check|
|R13-006|R12-002|R11-001|f70v2|f70v2.21,@Cc|oteedar oteeeor|missing_group_tokens|pending_visual_check|
|R13-007|R12-002|R11-005|f70v2|f70v2.1,@Cc|chokear cholkal|missing_group_tokens|pending_visual_check|
|R13-008|R12-002|R11-007|f70v2|f70v2.32,@Cc|al|missing_group_tokens|pending_visual_check|
|R13-009|R12-003|R11-004|f68r3|f68r3.1,@Cc|cheor chodal chokol|missing_group_tokens|pending_visual_check|
|R13-010|R12-004|R11-008|f84r|f84r.23,+P0|ol|missing_group_tokens|pending_visual_check|
|R13-011|R12-004|R11-011|f84r|f84r.14,+P0|ol or|matched_group_tokens|pending_visual_check|

## Como preencher

- `manual_token_seen`: use `yes`, `no` ou `uncertain` depois de olhar a imagem.
- `manual_new_crop_needed`: use `yes` somente se houver base visual para novo recorte.
- `manual_image_insufficient`: use `yes` quando a imagem atual nao permitir decisao.
- Coordenadas novas devem ser preenchidas apenas quando um recorte menor for realmente visivel.
- `checklist_item_not_axis_evidence` significa que a linha ainda nao prova nada sobre `a/o` ou `r/l`.
