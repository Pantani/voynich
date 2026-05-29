# Rota 44: distribuicao das 8 formas por secao e Currier A/B

Esta rota analisa como as 8 formas exatas `okal/okar/okol/okor/otal/otar/otol/otor`
se distribuem por secao do manuscrito e pelos dois regimes de Currier (A/B).
Nenhuma distribuicao e traducao ou deciframento.

- guardrail: `rota44_section_currier_distribution_not_decipherment`.

## Achado principal: bordas diferem entre Currier A e B; operadores nao diferem

| | Currier A | Currier B |
|---|---|---|
| sufixo `-ar` | 2 (6%) | 27 (42%) |
| sufixo `-al` | 6 (18%) | 20 (31%) |
| sufixo `-or` | 8 (24%) | 7 (11%) |
| sufixo `-ol` | 17 (52%) | 10 (16%) |
| prefixo `ok-` | 17 (52%) | 31 (48%) |
| prefixo `ot-` | 16 (48%) | 33 (52%) |

- Cramer's V (Currier x sufixo): **0.1595**
- Cramer's V (Currier x prefixo): **0.0113**

Leitura: o eixo sufixo (-ar/-al/-or/-ol) discrimina Currier A/B
significativamente mais do que o eixo prefixo (ok-/ot-), que permanece ~50/50
em ambos os dialetos.

## Distribuicao por secao

| secao | n | top formas |
|-------|---|------------|
| astronomical | 255 | otar=63, otal=56, okal=48, okar=46 |
| other | 237 | otar=43, okal=41, okar=38, otal=35 |
| herbal | 180 | okal=44, okar=33, otol=23, okol=21 |
| balneological | 70 | otar=18, otal=13, okal=13, okar=9 |
| pharmaceutical | 44 | okol=11, okar=7, okal=6, otal=6 |

- Cramer's V (secao x forma): **0.1480**

## Distribuicao por locus_kind x sufixo

| locus | -ar | -al | -or | -ol | Cramer's V |
|-------|-----|-----|-----|-----|-----------|
| P | 237(36%) | 248(37%) | 57(9%) | 122(18%) | — |
| C | 25(36%) | 18(26%) | 8(12%) | 18(26%) | — |
| L | 13(29%) | 14(31%) | 6(13%) | 12(27%) | — |
| R | 5(62%) | 1(12%) | 0(0%) | 2(25%) | — |

- Cramer's V (locus x sufixo): **0.0699**

## Interpretacoes provisorias

1. **Operador (ok-/ot-) e borda (-ar/-al/-or/-ol) sao camadas independentes.**
   O prefixo nao muda entre A e B (~50/50 nos dois); o sufixo muda fortemente.
   Isso e evidencia direta de que as duas camadas codificam informacoes diferentes.

2. **A borda parece codificar algo que varia sistematicamente entre maos/dialectos.**
   Currier A prefere -ol/-or; Currier B prefere -ar/-al.
   Interpretacoes possiveis: (a) codigos diferentes para o mesmo referente
   (nomenclator com multiplos codes); (b) a borda codifica algo que realmente
   variou entre autores (contexto, epoca, local).

3. **Pares minimos confirmados in situ (visual-annotator, Rota 44):**
   - okal + okol no mesmo diagrama f67v1 (eixo -al vs -ol em contexto identico)
   - okar + okor no mesmo cabecalho f99r (eixo -ar vs -or em rotulos adjacentes)
   Isso e evidencia visual direta de que -al/-ol e -ar/-or marcam distincoes
   sistematicas dentro do mesmo contexto, nao apenas variacao aleatoria.

4. **A secao astronomica e o maior habitat das formas exatas (23% do total).**
   Dentro dela, o tipo de estrela distingue as formas: 'Light star, tail' puxam
   okal; 'dotted, tail' puxam otar/otal. Sugere que a forma rotula um ATRIBUTO
   do objeto, nao apenas o tipo de objeto.

## Nao e traducao

Todas as observacoes acima sao distribuicoes textuais.
Nenhuma forma foi traduzida. Guardrail: `rota44_section_currier_distribution_not_decipherment`.