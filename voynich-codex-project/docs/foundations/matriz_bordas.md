# Matriz de bordas: `ar/al/or/ol` e `dy/y/aiin`

## Matriz principal

```text
        r       l

a      ar      al

o      or      ol
```

A matriz deve ser tratada como hipótese operacional: talvez dois eixos independentes codifiquem classe, posição, direção, polaridade ou tabela de cifra.

## Exemplos de famílias

```text
okar / okal / okor / okol
otar / otal / otor / otol
chor / chol
shor / shol
dar / dal
qokol / okol
```

## Bordas fortes

```text
-dy
-y
-aiin
-iin
-dar
-dal
```

`dar/dal` podem ser extensões pesadas de `ar/al`.

## Testes recomendados

1. Contar todas as ocorrências dos finais `ar/al/or/ol` por seção.
2. Separar por locus: `P`, `L`, `C`, `R`, rubrica.
3. Medir posição na linha: início, meio, fim.
4. Medir vizinhança: tokens antes/depois.
5. Para diagramas, anotar posição visual: norte, sul, leste, oeste, setor, anel, raio.
6. Testar se a distribuição melhora quando tokens são lidos funcionalmente da direita para a esquerda.

## Continuação executada

Script novo:

```bash
python scripts/build_matrix_context_table.py data/transcriptions/f67r2_excerpt.eva data/transcriptions/f68r3_excerpt.eva
```

Saídas:

- `data/derived/border_matrix_context.csv`;
- `docs/estudo_matriz_bordas_contexto.md`.

Primeiro resultado:

|métrica|valor|
|---|---:|
|linhas/loci analisados|46|
|candidatos `ar/al/or/ol`|30|
|`ar`|11|
|`al`|6|
|`or`|2|
|`ol`|11|

Sinais novos:

- `okal ar ol` em `f67r2.P.red` mostra `ar` e `ol` como tokens autônomos imediatamente depois de `okal`;
- rubrica/vermelho em `f67r2` concentra `ar/or`;
- radial/circular em `f68r3` concentra `ol`;
- `qokol` aparece em duas linhas radiais de `f68r3`, uma vez no início e outra no meio da linha.

Predição falsificável para a próxima rodada: se `ar/al/or/ol` são valores de slot, uma transcrição maior deve mostrar distribuição desigual por locus/camada, não apenas variação homogênea por sufixo fonético.

## Rota 1 em corpus ampliado

A predicao acima foi testada em `data/raw/ZL3b-n.txt`.

Resumo:

|métrica|valor|
|---|---:|
|loci preservados|5.385|
|tokens analisados pelo contador simples|41.005|
|candidatos contextuais|8.398|
|`ar`|2.220|
|`al`|1.719|
|`or`|1.666|
|`ol`|2.793|
|standalone `ar/al/or/ol`|1.639|

Resultado importante: a distribuicao nao ficou homogenea por locus. Em texto de paragrafo (`P`), `ol` domina; em texto circular (`C`), `ar` domina. Isso fortalece a leitura de matriz funcional por locus, mas ainda nao identifica o significado dos eixos.
