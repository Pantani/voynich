# Rota 1: corpus textual ampliado

## Objetivo

Testar a matriz `ar/al/or/ol` em uma transcricao IVTFF/EVA maior, para sair da amostra pequena formada por `f67r2` e `f68r3`.

## Fonte usada

Arquivo bruto:

- `data/raw/ZL3b-n.txt`

Origem:

- `https://www.voynich.nu/data/ZL3b-n.txt`

Descricao:

- Zandbergen-Landini, IVTFF 2.0/EVA;
- versao 3b de 13/05/2025;
- baixado de Voynich.nu em 2026-05-15;
- arquivo com 8.510 linhas locais.

## Comandos

```bash
python scripts/build_matrix_context_table.py data/raw/ZL3b-n.txt \
  --csv data/derived/border_matrix_context_zl3b.csv \
  --md docs/estudo_matriz_bordas_contexto_zl3b.md \
  --md-max-rows 250
```

```bash
python scripts/analyze_border_matrix.py data/raw/ZL3b-n.txt
```

## Saidas

- `data/derived/border_matrix_context_zl3b.csv`;
- `docs/estudo_matriz_bordas_contexto_zl3b.md`.

## Resultado principal

|metrica|valor|
|---|---:|
|loci preservados|5.385|
|tokens analisados pelo contador simples|41.005|
|tipos analisados pelo contador simples|8.307|
|candidatos contextuais `ar/al/or/ol`|8.398|
|candidatos exatos|2.682|
|candidatos amplos|4.077|
|valores standalone|1.639|

## Distribuicao dos sufixos

|sufixo|n|
|---|---:|
|`ol`|2.793|
|`ar`|2.220|
|`al`|1.719|
|`or`|1.666|

## Locus x sufixo

|locus|`ar`|`al`|`or`|`ol`|total|
|---|---:|---:|---:|---:|---:|
|`P`|1.870|1.469|1.546|2.604|7.489|
|`C`|232|160|75|127|594|
|`L`|93|70|39|49|251|
|`R`|25|20|6|13|64|

## Pares minimos e formas exatas

|token|n|
|---|---:|
|`chol`|384|
|`dar`|306|
|`dal`|235|
|`chor`|199|
|`qokal`|191|
|`shol`|173|
|`okal`|152|
|`qokar`|152|
|`otar`|147|
|`okar`|133|
|`otal`|129|
|`qokol`|96|
|`shor`|89|
|`otol`|79|
|`okol`|75|
|`otor`|37|
|`okor`|34|
|`qokor`|29|
|`odar`|23|
|`odal`|19|

## Leituras provisórias

1. A matriz nao morreu quando saiu da amostra pequena. Ao contrario: `ar/al/or/ol` aparece em escala grande, com 8.398 candidatos contextuais.
2. `ol` e a borda mais comum no corpus ampliado, mas `ar` tambem e forte. `or` e o menor eixo.
3. O comportamento nao e homogeneo por locus. Em `C`, `ar` passa `ol`; em `P`, `ol` domina. Isso e compativel com uma matriz funcional por locus, embora ainda nao prove o valor semantico dos eixos.
4. As formas exatas de maior peso nao sao apenas `ok-`/`ot-`: `chol/chor`, `dar/dal` e `shol/shor` aparecem em massa. Isso sugere que o teste deve separar nucleo (`ch/sh/d/ok/ot/qok`) antes de propor qualquer leitura.
5. Os valores standalone `ar/al/or/ol` aparecem 1.639 vezes. Isso reforca a ideia de "valor de slot" ou unidade funcional independente, nao apenas final fonetico.

## Consequencia para o estudo

A Rota 1 fortalece a hipotese operacional:

```text
token visivel = operador/modo + nucleo/template + valor de borda
```

Mas tambem aumenta a cautela: a matriz e real como padrao formal, mas ainda nao sabemos se os eixos `a/o` e `r/l` significam direcao, classe, estado, polaridade, tabela de cifra ou outra coisa.

## Proxima acao recomendada

Seguir para a Rota 2 com controles:

- comparar distribuicao real contra tokens embaralhados;
- medir desvio por prefixo e por locus;
- testar se `P/C/L/R` continuam separaveis quando controlamos pelo prefixo;
- comparar exatamente `okar/okal/okor/okol`, `otar/otal/otor/otol`, `qokar/qokal/qokor/qokol`, `chor/chol`, `shor/shol`, `dar/dal`.
