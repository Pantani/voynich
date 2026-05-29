# Rota 3: primeira anotacao visual

## Objetivo

Comecar a preencher a camada visual sem transformar observacao de pagina inteira em leitura lexical. Esta primeira rodada usa somente imagens ja conferidas localmente e marca baixa/media confianca quando a palavra exata nao foi isolada no nivel de glifo.

## Imagens conferidas

|arquivo|conteudo visual usado|
|---|---|
|`images/raw/commons_f67r1_r2.jpg`|abertura com `f67r1` e `f67r2`; diagramas circulares astronomicos/cosmologicos|
|`images/raw/commons_f67v2_v1.jpg`|abertura com `f67v2`; diagramas radiais/cosmologicos|
|`images/raw/commons_f68r1_r2_r3.jpg`|foldout com `f68r1`, `f68r2` e `f68r3`; estrelas, faces, texto radial/circular|
|`images/raw/commons_f70v2.jpg`|zodiaco com figuras/ninfas, estrelas, texto circular e rotulos|
|`images/raw/supplemental_f84r.jpg`|preview biologico/balneologico|
|`images/raw/supplemental_f89r1.jpg`|preview farmaceutico, abertura com f88v/f89r|
|`images/raw/supplemental_f99v.jpg`|preview farmaceutico|

Baixa parcial:

- `f1r`, `f67r1_r2`, `f67v2_v1`, `f68r1_r2_r3` e `f70v2` foram baixados do Commons;
- previews suplementares foram baixados para `f67r2`, `f68r1`, `f68r2`, `f68r3`, `f70v2`, `f84r`, `f89r1`, `f99v`, `f67v2`, `f1r` e imagem Yale;
- arquivos grandes do Commons para `f84r`, `f88v/f89r`, `f99r`, `f99v` e `f116v` ainda bateram em HTTP 429.

## Saida

Arquivo de anotacao preenchido:

- `data/annotations/visual_annotations_seed_zl3b.csv`

Resumo:

|metrica|valor|
|---|---:|
|anotacoes preenchidas|56|
|folios cobertos|10|
|camadas circulares|23|
|rotulos|19|
|paragrafos/texto corrido|10|
|camadas radiais|4|
|confianca media|42|
|confianca baixa|14|

Folios cobertos:

- `f67r1`;
- `f67r2`;
- `f67v2`;
- `f68r1`;
- `f68r2`;
- `f68r3`.
- `f70v2`;
- `f84r`;
- `f88v`;
- `f99v`.

## Observacoes conservadoras

1. Os candidatos `f67r1` estao em texto circular marrom ao redor de um diagrama com face central, raios vermelhos/azuis e estrelas. Isso apoia tratar esses tokens como camada circular/diagramatica, nao como texto corrido comum.
2. Os candidatos de `f67r2` foram anotados como rotulos dentro do diagrama circular da pagina direita, perto de pequenos discos lunares/planetarios e divisores de setor. A confianca e baixa porque a palavra exata nao foi isolada visualmente.
3. Os candidatos de `f67v2` pertencem a uma camada radial/cosmologica visivel na pagina esquerda da abertura. A confianca e media para camada, baixa para posicao exata.
4. Os candidatos de `f68r3` pertencem ao painel direito do foldout estelar, com texto radial/circular ao redor de uma face central e grupos de estrelas. A confianca e media para camada.
5. O lote `f70v2` acrescenta uma camada zodiacal com figuras/ninfas, estrelas, anel circular e rotulos curtos. Nessa semente, ele pesa muito em `ar/al`, entao ainda deve ser tratado como possivel vies de amostragem.
6. As paginas biologicas/farmaceuticas entraram apenas por preview; portanto a confianca permanece baixa.
7. Nenhuma anotacao afirma que `okar`, `otar`, `qokol`, `ar`, `ol` etc. sejam nomes de objetos. O ganho aqui e apenas locus visual.

## Consequencia

A primeira anotacao visual e compatível com a leitura da Rota 2:

```text
locus/camada visual influencia a distribuicao de ar/al/or/ol
```

Mas ainda nao basta para atribuir os eixos:

```text
a/o = ?
r/l = ?
```

## Micro-cruzamento da semente

Amostra pequena demais para conclusao, mas util como checagem de direcao:

|visual_zone|`ar`|`al`|`or`|`ol`|total|
|---|---:|---:|---:|---:|---:|
|circular text|10|6|1|6|23|
|label|8|4|5|2|19|
|paragraph text|3|4|2|1|10|
|radial text|3|0|0|1|4|

Relatorio derivado:

- `docs/rota_3_cruzamento_visual.md`;
- `data/derived/visual_annotation_summary_zl3b.csv`.

Leitura: a semente ainda e pequena e enviesada por `f70v2`, `f67r1` e `f84r`, mas ja permite testar o pipeline visual e alimentar a Rota 4. O proximo ganho real vira de aumentar as anotacoes para 75-100 linhas e reduzir os casos de baixa confianca.

## Proximo passo

1. Tentar baixar novamente os folios que falharam por HTTP 429: `f84r`, `f88v/f89r`, `f99r`, `f99v`, `f116v`.
2. Preencher mais 20-40 anotacoes visuais, priorizando `C`, `R`, `L`, tokens exatos e valores standalone.
3. Testar comparacoes dentro do mesmo folio/locus para evitar que diferencas entre paginas virem falso sinal.
4. So depois testar hipoteses de eixo como direcao, classe, anel, setor ou polaridade.
