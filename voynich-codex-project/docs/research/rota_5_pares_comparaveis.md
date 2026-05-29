# Rota 5: pares comparaveis no mesmo contexto

Esta rota reduz falso sinal comparando valores da matriz apenas dentro do mesmo folio, locus e familia de prefixo.

Corpus textual: `voynich-codex-project/data/derived/border_matrix_context_zl3b.csv`.
Semente visual: `voynich-codex-project/data/annotations/visual_annotations_seed_zl3b.csv`.
CSV gerado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/same_context_matrix_pairs_zl3b.csv`.

## Resultado curto

- grupos comparaveis encontrados: 725;
- grupos com anotacao visual direta: 11;
- eixo/cobertura mais comum: rl.

### Cobertura de eixo

|item|n|
|---|---:|
|rl|327|
|ao+rl|219|
|ao|179|

### Familias de prefixo

|item|n|
|---|---:|
|standalone|217|
|ch|183|
|d|93|
|ok|50|
|ot|49|
|sh|46|
|qok|32|
|qo|29|
|o|19|
|yk|3|
|yt|3|
|y|1|

## Grupos com anotacao visual direta

|score|folio|locus|kind|familia|sufixos|eixo|tokens|visual|objeto|
|---:|---|---|---|---|---|---|---|---|---|
|59|f67r1|f67r1.6,+Cc|C|d|al ar ol|ao+rl|dal dar dol|circular text|central face with red/blue rays and surrounding stars|
|56|f67r1|f67r1.5,@Cc|C|standalone|ar ol|ao+rl|ar ol|circular text|central face with red/blue rays and surrounding stars|
|56|f84r|f84r.14,+P0|P|standalone|ol or|rl|ol or|paragraph text|green pool with nymph figures and dense text|
|52|f67r1|f67r1.6,+Cc|C|standalone|al ar|rl|al ar|circular text|central face with red/blue rays and surrounding stars|
|49|f67r1|f67r1.6,+Cc|C|ch|ar ol or|ao+rl|chedar cheol cheor chol|circular text|central face with red/blue rays and surrounding stars|
|49|f68r3|f68r3.1,@Cc|C|ch|al ol or|ao+rl|cheor chodal chokol chol|circular text|central face medallion and dense star groups|
|49|f70v2|f70v2.1,@Cc|C|ch|al ar ol|ao+rl|chokear chol cholkal|circular text|zodiac nymph figures and stars|
|49|f70v2|f70v2.32,@Cc|C|standalone|al ar|rl|al ar|circular text|zodiac nymph figures and stars|
|35|f67r1|f67r1.5,@Cc|C|ot|ar or|ao|otardar otor|circular text|central face with red/blue rays and surrounding stars|
|35|f70v2|f70v2.21,@Cc|C|ot|ar or|ao|otar oteedar oteeeor|circular text|zodiac nymph figures and stars|
|35|f84r|f84r.23,+P0|P|standalone|ol or|rl|ol or|paragraph text|green pool with nymph figures and dense text|

## Grupos prioritarios

|score|folio|locus|kind|familia|sufixos|eixo|tokens|visual|
|---:|---|---|---|---|---|---|---|---|
|79|fRos|fRos.20,@Cc|C|standalone|al ar ol or|ao+rl|al ar ol or|circular text|
|70|fRos|fRos.122,@Cc|C|standalone|al ar ol or|ao+rl|al ar ol or|circular text|
|67|fRos|fRos.94,@Cc|C|standalone|al ar ol or|ao+rl|al ar ol or|circular text|
|64|fRos|fRos.2,@Cc|C|standalone|al ar ol or|ao+rl|al ar ol or|circular text|
|59|f67r1|f67r1.6,+Cc|C|d|al ar ol|ao+rl|dal dar dol|circular text|
|56|f34r|f34r.14,+P0|P|standalone|al ar ol or|ao+rl|al ar ol or|paragraph/text line|
|56|f55r|f55r.2,+P0|P|standalone|al ar ol or|ao+rl|al ar ol or|paragraph/text line|
|56|f67r1|f67r1.5,@Cc|C|standalone|ar ol|ao+rl|ar ol|circular text|
|56|f84r|f84r.14,+P0|P|standalone|ol or|rl|ol or|paragraph text|
|55|f68v3|f68v3.5,@Cc|C|d|al ar ol|ao+rl|dal dar dchol|circular text|
|52|f67r1|f67r1.6,+Cc|C|standalone|al ar|rl|al ar|circular text|
|51|f70r1|f70r1.13,@Cc|C|standalone|al ar ol|ao+rl|al ar ol|circular text|
|51|f71r|f71r.1,@Cc|C|standalone|al ar or|ao+rl|al ar or|circular text|
|51|f71v|f71v.1,@Cc|C|standalone|al ar or|ao+rl|al ar or|circular text|
|51|fRos|fRos.2,@Cc|C|ok|al ol or|ao+rl|okal okalol okor|circular text|
|51|fRos|fRos.62,@Cc|C|standalone|ar ol or|ao+rl|ar ol or|circular text|
|49|f67r1|f67r1.6,+Cc|C|ch|ar ol or|ao+rl|chedar cheol cheor chol|circular text|
|49|f68r3|f68r3.1,@Cc|C|ch|al ol or|ao+rl|cheor chodal chokol chol|circular text|
|49|f70v2|f70v2.1,@Cc|C|ch|al ar ol|ao+rl|chokear chol cholkal|circular text|
|49|f70v2|f70v2.32,@Cc|C|standalone|al ar|rl|al ar|circular text|
|49|f86v4|f86v4.6,+P0|P|standalone|al ol or|ao+rl|al ol or|paragraph/text line|
|49|f86v6|f86v6.7,+P0|P|standalone|ar ol or|ao+rl|ar ol or|paragraph/text line|
|48|f86v4|f86v4.4,@Cc|C|standalone|ar ol or|ao+rl|ar ol or|circular text|
|47|f69v|f69v.2,@Cc|C|ch|al ar ol|ao+rl|cheal chear chol|circular text|
|47|f70r2|f70r2.16,+Cc|C|ch|al ar ol|ao+rl|chedal choar chol|circular text|
|47|f72r3|f72r3.1,@Cc|C|ok|ar ol or|ao+rl|okar okarar okeeol okor|circular text|
|46|f104v|f104v.33,+P0|P|standalone|ar ol or|ao+rl|ar ol or|paragraph/text line|
|46|f112r|f112r.32,+P0|P|standalone|al ar ol|ao+rl|al ar ol|paragraph/text line|
|46|f115r|f115r.24,+P0|P|standalone|ar ol or|ao+rl|ar ol or|paragraph/text line|
|46|f40r|f40r.5,+P0|P|standalone|ar ol or|ao+rl|ar ol or|paragraph/text line|
|46|f58v|f58v.26,+P0|P|standalone|al ar ol|ao+rl|al ar ol|paragraph/text line|
|46|f86v5|f86v5.15,+P0|P|standalone|ar ol or|ao+rl|ar ol or|paragraph/text line|
|46|f86v6|f86v6.34,+P0|P|standalone|ar ol or|ao+rl|ar ol or|paragraph/text line|
|46|f89v2|f89v2.8,+P0|P|ok|ar ol or|ao+rl|okar okol okor|paragraph/text line|
|43|f101r|f101r.8,+P0|P|standalone|al ol or|ao+rl|al ol or|paragraph/text line|
|43|f111v|f111v.50,+P0|P|standalone|ar ol or|ao+rl|ar ol or|paragraph/text line|
|43|f113r|f113r.43,+P0|P|standalone|al ar ol|ao+rl|al ar ol|paragraph/text line|
|43|f113v|f113v.30,+P0|P|standalone|ar ol or|ao+rl|ar ol or|paragraph/text line|
|43|f55r|f55r.10,+P0|P|standalone|ar ol or|ao+rl|ar ol or|paragraph/text line|
|43|f55v|f55v.3,+P0|P|standalone|al ar ol|ao+rl|al ar ol|paragraph/text line|

## Leitura provisoria

- Grupos `standalone` ajudam a separar valores da matriz de tokens com nucleo.
- Grupos `ok`, `ot` e `qok` sao melhores candidatos para pares minimos porque preservam uma familia de prefixo.
- `ao+rl` e o caso mais informativo: a comparacao cruza os dois eixos dentro do mesmo contexto.
- Grupos sem anotacao visual continuam uteis textualmente, mas nao devem ser usados para inferir direcao, anel, setor ou objeto.
- O proximo passo deve escolher poucos grupos de alta prioridade e conferir a posicao exata dos glifos na imagem.
