# Rota 3: cruzamento visual

Este relatorio cruza a semente de anotacao visual com a matriz `ar/al/or/ol`. A amostra ainda e pequena; use como diagnostico de pipeline, nao como decifracao.

Fonte: `voynich-codex-project/data/annotations/visual_annotations_seed_zl3b.csv`.
Anotacoes analisadas: 56.

## Distribuicoes

|metrica|valor|
|---|---|
|folios|10|
|confianca baixa|14|
|confianca media|42|

### Sufixos na semente

|sufixo|n|
|---|---:|
|ar|24|
|al|14|
|or|8|
|ol|10|

### Visual zone x sufixo

|item|ar|al|or|ol|total|
|---|---:|---:|---:|---:|---:|
|circular text|10|6|1|6|23|
|label|8|4|5|2|19|
|paragraph text|3|4|2|1|10|
|radial text|3|0|0|1|4|

### Objeto proximo x sufixo

|item|ar|al|or|ol|total|
|---|---:|---:|---:|---:|---:|
|central face medallion and dense star groups|1|1|0|3|5|
|central face with red/blue rays and surrounding stars|6|2|1|2|11|
|green pool with nymph figures and dense text|3|4|2|1|10|
|plant/root drawings and container-like forms|0|1|1|0|2|
|plant/root drawings and vessels|1|0|1|0|2|
|pool/tube-like structures and dense paragraph text|0|0|1|0|1|
|small circular nodes and painted blue/green/red diagram areas|2|0|0|0|2|
|small moon/planet disks and lower text band|1|0|0|0|1|
|small moon/planet disks and red outer writing|1|0|0|0|1|
|small moon/planet disks and sector dividers|1|1|0|0|2|
|star field and small face medallions|0|0|0|1|1|
|stars and small moon/sun faces|0|0|2|2|4|
|zodiac nymph figure with star|4|2|0|0|6|
|zodiac nymph figures and stars|4|3|0|1|8|

## Leitura provisoria

- A semente confirma que o pipeline consegue cruzar texto, locus e imagem.
- `label` ainda esta dominado por `ar` nesta amostra, em parte por causa do lote `f70v2`.
- `circular text` esta mais balanceado entre `ar` e `ol`, mas a amostra ainda e pequena.
- A proxima rodada deve reduzir baixa confianca isolando melhor a posicao exata dos tokens nas imagens.
