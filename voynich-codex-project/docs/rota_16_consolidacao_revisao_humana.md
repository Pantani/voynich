# Rota 16: consolidacao da revisao humana

Esta rota cruza os itens de instrucao humana da Rota 15 com os campos manuais da checklist. Campos vazios continuam como pendencia e nao viram evidencia visual.

Instrucoes item-a-item: `voynich-codex-project/data/annotations/human_review_instruction_items_zl3b.csv`.
Checklist com campos manuais: `voynich-codex-project/data/annotations/packet_item_checklist_zl3b.csv`.
Consolidado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/human_review_evidence_consolidated_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/human_review_evidence_summary_zl3b.csv`.

## Resultado curto

- itens consolidados: 11;
- pendentes de revisao humana: 11;
- prontos para novo recorte apos revisao: 0;
- nenhum campo vazio foi interpretado como confirmacao ou rejeicao;
- nenhuma linha autoriza significado para `a/o` ou `r/l`.
- guarda: `human_review_evidence_not_axis_meaning`.

### Estado da revisao humana

|item|n|
|---|---:|
|pending_human_review|11|

### Categoria de evidencia

|item|n|
|---|---:|
|no_human_visual_evidence|11|

### Status de coordenadas

|item|n|
|---|---:|
|no_new_crop_coordinates|11|

### Acao de recorte

|item|n|
|---|---:|
|no_crop_generation|11|

### Prontidao para eixo

|item|n|
|---|---:|
|not_ready|11|

## Linhas consolidadas

|rota16|instrucao|checklist|pacote|folio|alvo|estado|evidencia|acao|
|---|---|---|---|---|---|---|---|---|
|R16-001|R15I-001|R13-001|R12-001|f67r1|otardar|pending_human_review|no_human_visual_evidence|no_crop_generation|
|R16-002|R15I-002|R13-002|R12-001|f67r1|chedar cheol cheor|pending_human_review|no_human_visual_evidence|no_crop_generation|
|R16-003|R15I-003|R13-003|R12-001|f67r1|dol|pending_human_review|no_human_visual_evidence|no_crop_generation|
|R16-004|R15I-004|R13-004|R12-001|f67r1|ar ol|pending_human_review|no_human_visual_evidence|no_crop_generation|
|R16-005|R15I-005|R13-005|R12-001|f67r1|al ar|pending_human_review|no_human_visual_evidence|no_crop_generation|
|R16-006|R15I-006|R13-006|R12-002|f70v2|oteedar oteeeor|pending_human_review|no_human_visual_evidence|no_crop_generation|
|R16-007|R15I-007|R13-007|R12-002|f70v2|chokear cholkal|pending_human_review|no_human_visual_evidence|no_crop_generation|
|R16-008|R15I-008|R13-008|R12-002|f70v2|al|pending_human_review|no_human_visual_evidence|no_crop_generation|
|R16-009|R15I-009|R13-009|R12-003|f68r3|cheor chodal chokol|pending_human_review|no_human_visual_evidence|no_crop_generation|
|R16-010|R15I-010|R13-010|R12-004|f84r|ol|pending_human_review|no_human_visual_evidence|no_crop_generation|
|R16-011|R15I-011|R13-011|R12-004|f84r|ol or|pending_human_review|no_human_visual_evidence|no_crop_generation|

## Leitura provisoria

- A Rota 16 e uma consolidacao operacional das respostas humanas, nao uma etapa semantica.
- Somente linhas com token visto e coordenadas completas podem seguir para geracao/revisao de novo recorte.
- Mesmo um novo recorte revisado ainda precisara de teste separado antes de qualquer leitura dos eixos.
