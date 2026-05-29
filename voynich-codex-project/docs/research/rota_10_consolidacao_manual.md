# Rota 10: consolidacao da revisao manual

Esta rota consolida a folha manual da Rota 9. Ela valida status e coordenadas, mas nao cria confirmacao visual por inferencia.

Fonte: `voynich-codex-project/data/annotations/manual_svg_review_zl3b.csv`.
CSV consolidado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/manual_svg_review_consolidated_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/manual_review_status_summary_zl3b.csv`.

## Resultado curto

- itens consolidados: 11;
- itens ainda pendentes: 11;
- itens elegiveis para teste visual dos eixos: 0;
- nenhuma leitura semantica foi atribuida.

### Resultado de consolidacao

|item|n|
|---|---:|
|pending_manual_review|11|

### Status de coordenada

|item|n|
|---|---:|
|no_manual_coordinates|11|

### Evidencia visual

|item|n|
|---|---:|
|no_glyph_confirmation|11|

### Elegibilidade para teste dos eixos

|item|n|
|---|---:|
|not_eligible|11|

## Linhas consolidadas

|rota10|manual|crop|familia|folio|locus|status manual|resultado|coordenada|elegivel|
|---|---|---|---|---|---|---|---|---|---|
|R10-001|R9-001|R7-009|ot|f67r1|f67r1.5,@Cc|pending_manual_review|pending_manual_review|no_manual_coordinates|not_eligible|
|R10-002|R9-002|R7-010|ot|f70v2|f70v2.21,@Cc|pending_manual_review|pending_manual_review|no_manual_coordinates|not_eligible|
|R10-003|R9-003|R7-001|d|f67r1|f67r1.6,+Cc|pending_manual_review|pending_manual_review|no_manual_coordinates|not_eligible|
|R10-004|R9-004|R7-005|ch|f67r1|f67r1.6,+Cc|pending_manual_review|pending_manual_review|no_manual_coordinates|not_eligible|
|R10-005|R9-005|R7-006|ch|f68r3|f68r3.1,@Cc|pending_manual_review|pending_manual_review|no_manual_coordinates|not_eligible|
|R10-006|R9-006|R7-007|ch|f70v2|f70v2.1,@Cc|pending_manual_review|pending_manual_review|no_manual_coordinates|not_eligible|
|R10-007|R9-007|R7-008|standalone|f70v2|f70v2.32,@Cc|pending_manual_review|pending_manual_review|no_manual_coordinates|not_eligible|
|R10-008|R9-008|R7-011|standalone|f84r|f84r.23,+P0|pending_manual_review|pending_manual_review|no_manual_coordinates|not_eligible|
|R10-009|R9-009|R7-002|standalone|f67r1|f67r1.5,@Cc|pending_manual_review|pending_manual_review|no_manual_coordinates|not_eligible|
|R10-010|R9-010|R7-004|standalone|f67r1|f67r1.6,+Cc|pending_manual_review|pending_manual_review|no_manual_coordinates|not_eligible|
|R10-011|R9-011|R7-003|standalone|f84r|f84r.14,+P0|pending_manual_review|pending_manual_review|no_manual_coordinates|not_eligible|

## Leitura provisoria

- A Rota 10 confirma apenas o estado da revisao, nao o glifo.
- Com todos os itens ainda pendentes, nenhum par deve entrar em teste visual fino dos eixos `a/o` ou `r/l`.
- A proxima etapa pode preencher a folha manual ou ampliar a busca por recortes melhores nos mesmos folios.
