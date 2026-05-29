# Rota 43: collocações e padrões terminais das 8 formas ok/ot exatas

Esta rota analisa vizinhança, trigramas e assimetria de fechamento de locus para
as 8 formas exatas `okal/okar/okol/okor/otal/otar/otol/otor`.
Nenhuma collocação é tradução ou decifração.

- guardrail: `form_collocation_analysis_not_decipherment`.

## Distribuição prefix+suffix

|prefix|suffix|n|
|---|---|---:|
|ok|al|152|
|ot|ar|147|
|ok|ar|133|
|ot|al|129|
|ot|ol|79|
|ok|ol|75|
|ot|or|37|
|ok|or|34|

## Standalone border após cada forma

Percentual de ocorrências onde o token seguinte é `ar/al/or/ol` isolado.

|forma|n|standalone_after|%|ar|al|or|ol|
|---|---:|---:|---:|---:|---:|---:|---:|
|okal|152|10|6.6%|2|1|4|3|
|okar|133|21|15.8%|11|3|1|6|
|okol|75|5|6.7%|1|0|2|2|
|okor|34|5|14.7%|1|0|2|2|
|otal|129|9|7.0%|1|2|2|4|
|otar|147|22|15.0%|12|5|2|3|
|otol|79|5|6.3%|1|2|0|2|
|otor|37|1|2.7%|1|0|0|0|

### Assimetria ar-group vs al-group (chi²)

- ar_group (okar+otar): hits=43 / 280 = 15.4%;
- al_group (okal+otal): hits=19 / 281 = 6.8%;
- chi²(1 df) = 10.54 (p<0.001 se >10.83);
- guardrail: `form_collocation_analysis_not_decipherment`.

## Top-20 trigramas forma→border→?

|forma|border|próximo|n|
|---|---|---|---:|
|okar|ar|_END_|8|
|otal|ol|_END_|6|
|otar|ar|_END_|5|
|okol|or|_END_|4|
|okar|ol|_END_|4|
|okal|or|_END_|3|
|otar|ar|al|3|
|otar|al|_END_|3|
|otol|ol|_END_|3|
|otar|or|ol|2|
|otar|or|_END_|2|
|otol|ol|dar|2|
|otar|ol|_END_|2|
|okal|ol|_END_|2|
|otal|ar|_END_|2|
|otal|al|_END_|2|
|otol|ol|qotchar|1|
|okor|ar|chdal|1|
|otar|ar|or|1|
|okal|ar|_END_|1|

## Bigrams forma→forma

|forma1|forma2|n|
|---|---|---:|
|okar|okar|5|
|okar|otar|5|
|otar|otal|5|
|okar|okal|5|
|otal|otar|5|
|otal|otal|5|
|okal|okal|4|
|okal|okar|3|
|okal|otar|3|
|okol|okal|2|
|okar|okol|2|
|okal|otal|2|
|otor|otar|2|
|otar|okol|2|
|otal|okar|1|

## Compostos: forma + border + forma

|forma1|border|forma2|n|
|---|---|---|---:|
|okar|ar|otol|1|
|otor|ar|otal|1|
|otal|al|okol|1|
|otar|ar|otol|1|
|okal|ol|otar|1|
|okal|or|okar|1|
|otar|ol|okar|1|
|otal|or|otar|1|
|okar|or|okal|1|
|okor|ol|okar|1|
|otar|al|okal|1|
|otar|ar|okol|1|
|otar|ar|otar|1|
|otal|al|otar|1|

## Leitura

**Padrão 1 — fechamento concordante**: formas `-ar` (okar, otar) encerram locus com
standalone `ar` a ~15%, enquanto formas `-al/-ol` fazem isso a ~7%.
A assimetria é estatisticamente mensurável (ver chi² acima).

**Padrão 2 — bigrama dominante**: `okar → otar` (n=5) é o bigrama forma×forma mais
frequente, sugerindo que estas duas formas aparecem em par sequencial.

**Padrão 3 — tripla de bordas**: `otar ar al` (n=3) e `otar or ol` (n=2) mostram
que após `otar` podem aparecer DOIS valores de borda consecutivos (ar+al, or+ol),
consistente com a hipótese de que o standalone codifica um segundo slot.

**Não é tradução**: estas collocações descrevem distribuição textual, não semântica.