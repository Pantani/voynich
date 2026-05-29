# Rota 2: controles estatisticos da matriz

Este relatorio testa se a distribuicao de `ar/al/or/ol` permanece estruturada quando observada por locus, prefixo e posicao de linha. Ele nao atribui significado aos eixos; apenas mede se o padrao parece aleatorio sob controles simples.

Fonte: `voynich-codex-project/data/derived/border_matrix_context_zl3b.csv`.

Candidatos analisados: 8398.

## Resultados-chave

|controle|resultado|interpretacao|
|---|---|---|
|locus_vs_suffix|chi2=153.340, df=9, cramers_v=0.0780, shuffle_p<=0.0020|Testa se P/L/C/R tem distribuicoes diferentes de ar/al/or/ol.|
|prefix_vs_suffix|chi2=712.684, df=36, cramers_v=0.1682, shuffle_p<=0.0020|Testa se familias de prefixo preferem bordas diferentes.|
|line_position_vs_suffix|chi2=240.746, df=9, cramers_v=0.0978, shuffle_p<=0.0020|Testa se inicio/meio/fim de linha afeta a borda.|
|locus_vs_suffix_given_prefix|chi2=93.418, df=9, cramers_v=0.0609|Compara locus x sufixo depois de controlar a mistura de prefixos.|

### Sufixos

|item|n|
|---|---:|
|ol|2793|
|ar|2220|
|al|1719|
|or|1666|

### Locus x sufixo

|item|ar|al|or|ol|total|
|---|---:|---:|---:|---:|---:|
|C|232|160|75|127|594|
|L|93|70|39|49|251|
|P|1870|1469|1546|2604|7489|
|R|25|20|6|13|64|

### Prefixo x sufixo

|item|ar|al|or|ol|total|
|---|---:|---:|---:|---:|---:|
|(none)|420|267|388|564|1639|
|ch|327|230|395|673|1625|
|d|354|287|141|192|974|
|o|150|93|108|102|453|
|od|24|20|9|3|56|
|ok|192|204|93|188|677|
|ot|224|181|89|174|668|
|qo|125|93|103|277|598|
|qok|185|209|75|179|648|
|sh|102|86|161|339|688|
|y|28|14|47|36|125|
|yk|48|17|27|43|135|
|yt|41|18|30|23|112|

### Posicao x sufixo

|item|ar|al|or|ol|total|
|---|---:|---:|---:|---:|---:|
|end|162|196|87|138|583|
|middle|1822|1399|1276|2323|6820|
|single|58|55|29|41|183|
|start|178|69|274|291|812|

### Pares exatos

|familia|total|formas|
|---|---:|---|
|ok|394|okar=133, okal=152, okor=34, okol=75|
|ot|392|otar=147, otal=129, otor=37, otol=79|
|qok|468|qokar=152, qokal=191, qokor=29, qokol=96|
|ch|583|chor=199, chol=384|
|sh|262|shor=89, shol=173|
|d|541|dar=306, dal=235|
|od|42|odar=23, odal=19|

## Leitura provisoria

- A associacao entre locus e sufixo precisa sobreviver ao controle por prefixo para interessar como camada funcional.
- Se o controle por prefixo ainda mostrar desvio, a matriz nao e explicada apenas por familias como `ch`, `sh`, `ok`, `ot` e `qok`.
- O proximo passo e escolher alguns folios/loci onde o desvio e forte e passar para anotacao visual manual.
