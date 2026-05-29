# Rota 14: consolidacao da checklist preenchida

Esta rota consolida os campos manuais da checklist Rota 13. Com a checklist ainda vazia, ela registra pendencia e impede leitura semantica prematura.

Fonte: `voynich-codex-project/data/annotations/packet_item_checklist_zl3b.csv`.
Consolidado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/packet_item_checklist_consolidated_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/packet_item_checklist_consolidation_summary_zl3b.csv`.

## Resultado curto

- itens consolidados: 11;
- itens elegiveis apos geracao de recorte: 0;
- pendentes: 11;
- nenhuma evidencia visual nova foi criada por inferencia.

### Resultado de consolidacao

|item|n|
|---|---:|
|pending_visual_check|11|

### Status de coordenadas

|item|n|
|---|---:|
|no_new_crop_coordinates|11|

### Evidencia visual

|item|n|
|---|---:|
|no_new_visual_evidence|11|

### Elegibilidade

|item|n|
|---|---:|
|not_eligible|11|

### Tipo de alvo

|item|n|
|---|---:|
|missing_group_tokens|8|
|matched_group_tokens|3|

## Linhas consolidadas

|rota14|checklist|pacote|folio|alvo|resultado|evidencia|elegivel|
|---|---|---|---|---|---|---|---|
|R14-001|R13-001|R12-001|f67r1|otardar|pending_visual_check|no_new_visual_evidence|not_eligible|
|R14-002|R13-002|R12-001|f67r1|chedar cheol cheor|pending_visual_check|no_new_visual_evidence|not_eligible|
|R14-003|R13-003|R12-001|f67r1|dol|pending_visual_check|no_new_visual_evidence|not_eligible|
|R14-004|R13-004|R12-001|f67r1|ar ol|pending_visual_check|no_new_visual_evidence|not_eligible|
|R14-005|R13-005|R12-001|f67r1|al ar|pending_visual_check|no_new_visual_evidence|not_eligible|
|R14-006|R13-006|R12-002|f70v2|oteedar oteeeor|pending_visual_check|no_new_visual_evidence|not_eligible|
|R14-007|R13-007|R12-002|f70v2|chokear cholkal|pending_visual_check|no_new_visual_evidence|not_eligible|
|R14-008|R13-008|R12-002|f70v2|al|pending_visual_check|no_new_visual_evidence|not_eligible|
|R14-009|R13-009|R12-003|f68r3|cheor chodal chokol|pending_visual_check|no_new_visual_evidence|not_eligible|
|R14-010|R13-010|R12-004|f84r|ol|pending_visual_check|no_new_visual_evidence|not_eligible|
|R14-011|R13-011|R12-004|f84r|ol or|pending_visual_check|no_new_visual_evidence|not_eligible|

## Leitura provisoria

- Campos manuais vazios continuam sendo pendencia, nao negativa nem confirmacao.
- Coordenadas novas so podem ser usadas quando `manual_new_crop_needed=yes` e todos os campos numericos estiverem completos.
- A guarda `checklist_consolidation_not_axis_evidence` impede usar esta consolidacao como significado de `a/o` ou `r/l`.
