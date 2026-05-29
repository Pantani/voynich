# Rota 4: teste dos eixos da matriz

Este relatorio separa `ar/al/or/ol` em dois eixos binarios. Ele mede associacao, nao significado.

Corpus textual: `voynich-codex-project/data/derived/border_matrix_context_zl3b.csv` (8398 candidatos).
Semente visual: `voynich-codex-project/data/annotations/visual_annotations_seed_zl3b.csv` (56 anotacoes).

## Resultados no corpus textual

|dimensao|eixo a/o|eixo r/l|
|---|---|---|
|locus_kind|chi2=149.949, df=3, Cramer's V=0.1336|chi2=12.453, df=3, Cramer's V=0.0385|
|prefix|chi2=570.909, df=12, Cramer's V=0.2607|chi2=116.682, df=12, Cramer's V=0.1179|
|line_position|chi2=154.326, df=3, Cramer's V=0.1356|chi2=33.878, df=3, Cramer's V=0.0635|

## Resultados na semente visual

|dimensao|eixo a/o|eixo r/l|
|---|---|---|
|visual_zone|chi2=0.338, df=3, Cramer's V=0.0777|chi2=2.531, df=3, Cramer's V=0.2126|
|object_nearby|chi2=22.270, df=13, Cramer's V=0.6306|chi2=10.353, df=13, Cramer's V=0.4300|
|annotation_confidence|chi2=5.349, df=1, Cramer's V=0.3091|chi2=0.389, df=1, Cramer's V=0.0833|
|folio|chi2=19.983, df=9, Cramer's V=0.5974|chi2=7.335, df=9, Cramer's V=0.3619|

### Corpus: locus_kind x eixo a/o

|item|a|o|total|a_share|o_share|
|---|---:|---:|---:|---:|---:|
|C|392|202|594|0.660|0.340|
|L|163|88|251|0.649|0.351|
|P|3339|4150|7489|0.446|0.554|
|R|45|19|64|0.703|0.297|

### Corpus: locus_kind x eixo r/l

|item|r|l|total|r_share|l_share|
|---|---:|---:|---:|---:|---:|
|C|307|287|594|0.517|0.483|
|L|132|119|251|0.526|0.474|
|P|3416|4073|7489|0.456|0.544|
|R|31|33|64|0.484|0.516|

### Visual: visual_zone x eixo a/o

|item|a|o|total|a_share|o_share|
|---|---:|---:|---:|---:|---:|
|circular text|16|7|23|0.696|0.304|
|label|12|7|19|0.632|0.368|
|paragraph text|7|3|10|0.700|0.300|
|radial text|3|1|4|0.750|0.250|

### Visual: visual_zone x eixo r/l

|item|r|l|total|r_share|l_share|
|---|---:|---:|---:|---:|---:|
|circular text|11|12|23|0.478|0.522|
|label|13|6|19|0.684|0.316|
|paragraph text|5|5|10|0.500|0.500|
|radial text|3|1|4|0.750|0.250|

## Leitura provisoria

- No corpus grande, prefixo deve ser o principal fator a observar: se o eixo muda por prefixo, parte da matriz e morfologica/template.
- Locus e posicao de linha continuam importantes se seus eixos mantiverem efeito mesmo quando o prefixo for controlado.
- Na semente visual, o resultado ainda e exploratorio: a amostra e pequena e enviesada para `f70v2`, `f67r1` e `f84r`.
- O proximo passo deve testar os eixos em pares comparaveis dentro do mesmo folio/locus, nao entre paginas muito diferentes.
