# Resumo executivo dos estudos — Manuscrito Voynich

## 1. Situação geral

O Manuscrito Voynich, Beinecke MS 408, continua sem decifração comprovada. A própria Beinecke/Yale o descreve como um manuscrito misterioso e indecifrado, escrito em escrita desconhecida e com propósito incerto. O catálogo da Beinecke registra que várias decifrações foram alegadas, mas que, em geral, o texto permanece um quebra-cabeça sem solução.

Nosso estudo não chegou a uma tradução final. O avanço foi outro: identificar que tipo de problema provavelmente estamos enfrentando.

## 2. Hipótese mais forte

A hipótese que mais sobreviveu aos ataques é:

> O Voynichese provavelmente não é uma língua natural escrita diretamente, nem uma cifra simples de substituição. Ele parece uma escrita/cifra/notação em camadas, na qual a forma do token depende de seção, tipo de locus, posição na linha, rótulo, texto circular/radial, cor e função diagramática.

Modelo resumido:

```text
[token visível] = operador de modo + núcleo/template + valor de borda
```

Ou, se a estrutura funcional for parcialmente direita→esquerda:

```text
[token visível] = valor de borda + núcleo/template + operador de modo
```

## 3. Principais operadores candidatos

| Bloco | Interpretação provisória | Confiança |
|---|---|---:|
| `qo-` | operador típico de texto corrido | alta |
| `o-` | marcador genérico de entrada/formação | média |
| `ok-` / `ot-` | operadores de rótulo/diagrama/classe | alta |
| `yk-` / `yt-` | operadores diagramáticos/rubricais | média |
| `ch` / `sh` | núcleos ou classes de template | média |
| `-dy` / `-y` | borda, fechamento ou classe de token | alta |
| `-ar/-al/-or/-ol` | matriz de quatro estados | média-alta |
| `-aiin/-iin` | borda recorrente ou bloco funcional | média |

## 4. A fechadura principal: matriz `ar/al/or/ol`

A família abaixo parece central:

```text
        r       l

a      ar      al

o      or      ol
```

Pares mínimos suspeitos:

```text
okar / okal / okor / okol
otar / otal / otor / otol
chor / chol
shor / shol
dar / dal
```

A hipótese é que `a/o` e `r/l` codifiquem dois eixos independentes: classe, direção, posição, polaridade, estado, gênero/caso técnico, ou tabela de cifra. Ainda não sabemos o valor semântico desses eixos.

## 5. Ataques realizados e resultados

### Ataque 1 — Estatística geral

- O texto não parece ruído aleatório simples.
- Também não se comporta como uma língua europeia comum escrita diretamente.
- Distribuições tipo Zipf e vocabulários por seção indicam estrutura, mas não provam linguagem natural.

### Ataque 2 — Currier A/B

- Currier A e B parecem regimes estatísticos reais.
- Podem ser dialetos, mãos, seções, cifras ou templates diferentes.
- A/B talvez não sejam “línguas” distintas, mas modos de geração.

### Ataque 3 — Linha como unidade funcional

- Inícios e fins de linha têm comportamento diferente do meio.
- Isso é muito estranho para prosa comum.
- A linha física pode ser parte da chave ou uma unidade de registro/tabela.

### Ataque 4 — Rótulos

- Rótulos zodiacais e farmacêuticos têm alta unicidade.
- Começam muito mais por `ok-`/`ot-` do que o texto corrido.
- Quase não usam `qo-`, que é frequente em texto corrido.
- Conclusão: rótulos são uma camada própria, não palavras comuns copiadas dos parágrafos.

### Ataque 5 — Visual-semântico

- Candidatos como `otoldy`, `otaly`, `okolshy` reaparecem em contextos visuais diferentes.
- Isso enfraquece a ideia de “rótulo = nome direto do objeto”.
- Esses termos parecem mais operadores/template do que nomes simples.

### Ataque 6 — Astronômico

- f68r3, o diagrama frequentemente ligado às Plêiades, tem uma possível âncora `doaro/doary`.
- Contudo, `doaro = Plêiades` ainda é hipótese, não decifração.
- f67r2, “sete planetas”, tem estrutura rica, mas não entrega nomes planetários transparentes.

### Ataque 7 — Camada vermelha de f67r2

- O vermelho não parece tradução direta do texto marrom.
- Parece camada rubrical/técnica.
- O anel vermelho usa muito `yk-`, `ch`, `k` e quase nada de `q`/`aiin`.

### Ataque 8 — Família `okal/okar/ytokar`

- `okal` não deve ser assumido como “Sol”.
- A família `ok-/ot-/ytok-` aparece em Sol, Lua, estrelas, linhas radiais, rótulos e texto circular.
- Melhor leitura: operador de função diagramática.

### Ataque 9 — Matriz de bordas

- `-dy`, `-y`, `-aiin`, `-ar`, `-al`, `-or`, `-ol` parecem valores de slot.
- `ar` e `ol` aparecem também como tokens independentes em f67r2.
- A borda direita do token pode ser funcionalmente especial.

## 6. O que foi enfraquecido

Hipóteses fracas após os testes:

```text
Voynich = latim simples com alfabeto trocado
Voynich = italiano/hebraico/proto-romance direto
Voynich = substituição simples
Voynich = nomes de plantas codificados palavra por palavra
Voynich = puro nonsense aleatório
okal = Sol
otoldy = nome de uma planta específica
-dy = plural simples
```

## 7. O que ficou vivo

Hipóteses ainda plausíveis:

```text
cifra homofônica/verbosa
notação técnica artificial
texto natural muito transformado
sistema misto: cifra + abreviação + notação
texto gerado por regras com conteúdo estrutural
nomenclator com operadores
cifra dependente de linha/locus/seção
```

## 8. Próximo passo recomendado

O próximo estudo recomendado era construir uma tabela completa para pares mínimos:

```text
okar, okal, okor, okol
otar, otal, otor, otol
qokar, qokal, qokor, qokol
chor, chol, shor, shol
dar, dal, odar, odal
```

Esse passo agora começou em `voynich-codex-project/docs/estudo_matriz_bordas_contexto.md`, com uma primeira tabela contextual sobre os trechos `f67r2` e `f68r3`.

Resultado inicial:

- 46 linhas/loci de transcrição analisados;
- 30 candidatos `ar/al/or/ol`;
- distribuição de borda: `ar=11`, `ol=11`, `al=6`, `or=2`;
- tokens exatos mais relevantes: `okar=2`, `okal=2`, `qokol=2`, `dal=1`, `okol=1`, `dar=1`;
- rubrica/vermelho em `f67r2` concentrou `ar/or`;
- linhas radiais/circulares em `f68r3` concentraram `ol`;
- a sequência vermelha `okal ar ol` reforça que `ar`/`ol` podem aparecer como valores autônomos de slot, não só como terminações fonéticas.

Campos mínimos:

- folio;
- seção;
- tipo de locus (`P`, `L`, `C`, `R`, rubrica);
- posição na linha;
- posição visual no diagrama;
- cor/tinta;
- objeto gráfico próximo;
- Currier A/B;
- transcritor e variantes.

A meta é descobrir se `ar/al/or/ol` corresponde a direção, classe, polaridade, posição, ou estado.

Próxima etapa atualizada: rodar o mesmo gerador sobre uma transcrição IVTFF/EVA maior e acrescentar anotação visual manual para anel, setor, raio, cor/tinta e objeto gráfico próximo.

## 10. Continuação: Rota 1 executada

A Rota 1 ampliou o corpus textual usando `voynich-codex-project/data/raw/ZL3b-n.txt`, transcrição Zandbergen-Landini em IVTFF/EVA.

Saídas:

- `voynich-codex-project/data/derived/border_matrix_context_zl3b.csv`;
- `voynich-codex-project/docs/estudo_matriz_bordas_contexto_zl3b.md`;
- `voynich-codex-project/docs/rota_1_corpus_textual.md`.

Resultado:

- 5.385 loci preservados;
- 41.005 tokens no contador simples;
- 8.398 candidatos contextuais `ar/al/or/ol`;
- `ol=2.793`, `ar=2.220`, `al=1.719`, `or=1.666`;
- 2.682 candidatos exatos;
- 1.639 valores standalone.

Achado principal:

> A matriz não desaparece no corpus maior. Além disso, a distribuição varia por locus: `ol` domina em `P`, enquanto `ar` domina em `C`.

Conclusão provisória: a hipótese de matriz funcional ficou mais forte, mas ainda não há valor semântico para os eixos `a/o` e `r/l`. O próximo ataque deve ser estatístico/controle: embaralhar tokens/linhas, controlar por prefixo e medir se `P/C/L/R` continuam separáveis.

## 11. Continuação: Rotas 2 e 3

A Rota 2 executou controles estatísticos sobre `voynich-codex-project/data/derived/border_matrix_context_zl3b.csv`.

Saídas:

- `voynich-codex-project/docs/rota_2_controles_estatisticos.md`;
- `voynich-codex-project/data/derived/matrix_control_summary_zl3b.csv`;
- `voynich-codex-project/data/derived/matrix_exact_pairs_zl3b.csv`.

Resultado:

- locus x sufixo: chi2=153,340; Cramer's V=0,0780; embaralhamento p<=0,0020;
- prefixo x sufixo: chi2=712,684; Cramer's V=0,1682; embaralhamento p<=0,0020;
- posição x sufixo: chi2=240,746; Cramer's V=0,0978; embaralhamento p<=0,0020;
- locus x sufixo controlando prefixo: chi2=93,418; Cramer's V=0,0609.

Leitura: o prefixo explica uma parte importante da matriz, mas não explica tudo. O locus ainda deixa sinal mensurável depois do controle por prefixo.

A Rota 3 foi preparada em seguida para evitar que a etapa visual fosse preenchida por suposição.

Saídas:

- `voynich-codex-project/docs/rota_3_anotacao_visual.md`;
- `voynich-codex-project/data/annotations/visual_annotation_candidates_zl3b.csv`.

Resultado: 160 candidatos ranqueados para anotação manual. Os campos de imagem, cor, anel, setor, raio e objeto próximo ficaram vazios de propósito para evitar inferência automática.

## 12. Primeira anotação visual

A primeira rodada da Rota 3 conferiu imagens locais, expandiu a semente de anotação visual e gerou o primeiro cruzamento visual.

Saídas:

- `voynich-codex-project/docs/rota_3_primeira_anotacao_visual.md`;
- `voynich-codex-project/docs/rota_3_cruzamento_visual.md`;
- `voynich-codex-project/data/annotations/visual_annotations_seed_zl3b.csv`.
- `voynich-codex-project/data/derived/visual_annotation_summary_zl3b.csv`.

Resultado:

- 56 anotações preenchidas;
- 10 fólios cobertos: `f67r1`, `f67r2`, `f67v2`, `f68r1`, `f68r2`, `f68r3`, `f70v2`, `f84r`, `f88v`, `f99v`;
- zonas visuais: 23 circulares, 19 rótulos, 10 parágrafos/texto corrido, 4 radiais;
- confiança: 42 médias, 14 baixas.

Micro-cruzamento:

|zona|`ar`|`al`|`or`|`ol`|
|---|---:|---:|---:|---:|
|circular text|10|6|1|6|
|label|8|4|5|2|
|paragraph text|3|4|2|1|
|radial text|3|0|0|1|

Leitura: a anotação inicial é compatível com a hipótese de camada/locus, mas ainda não atribui significado a `a/o` ou `r/l`. O lote `f70v2` pesa muito em `ar/al`, então o cruzamento ainda é diagnóstico de pipeline, não conclusão.

## 13. Rota 4: eixos da matriz

A Rota 4 separou `ar/al/or/ol` em dois eixos binários:

```text
        r       l
a      ar      al
o      or      ol
```

Saídas:

- `voynich-codex-project/scripts/analyze_matrix_axes.py`;
- `voynich-codex-project/docs/rota_4_eixos_matriz.md`;
- `voynich-codex-project/data/derived/matrix_axis_summary_zl3b.csv`.

Resultado textual:

- `locus_kind x a/o`: Cramer's V=0,1336;
- `locus_kind x r/l`: Cramer's V=0,0385;
- `prefix x a/o`: Cramer's V=0,2607;
- `prefix x r/l`: Cramer's V=0,1179;
- `line_position x a/o`: Cramer's V=0,1356;
- `line_position x r/l`: Cramer's V=0,0635.

Leitura: no corpus textual, `a/o` carrega muito mais estrutura que `r/l`, especialmente por prefixo e posição de linha. Na semente visual, `r/l` aparece relativamente maior em `visual_zone`, mas a amostra ainda é pequena e enviesada por fólios. O próximo passo precisa comparar pares dentro do mesmo folio/locus/família, não páginas heterogêneas.

## 14. Rota 5: pares comparáveis locais

A Rota 5 comparou `ar/al/or/ol` apenas dentro do mesmo folio, locus e família de prefixo.

Saídas:

- `voynich-codex-project/scripts/analyze_same_context_pairs.py`;
- `voynich-codex-project/docs/rota_5_pares_comparaveis.md`;
- `voynich-codex-project/data/derived/same_context_matrix_pairs_zl3b.csv`.

Resultado:

- 725 grupos comparáveis;
- 11 grupos com anotação visual direta;
- cobertura de eixo: `rl=327`, `ao+rl=219`, `ao=179`;
- famílias mais frequentes: `standalone=217`, `ch=183`, `d=93`, `ok=50`, `ot=49`, `qok=32`.

Leitura: a matriz gera pares locais suficientes para teste, sem depender de comparação distante entre páginas. O gargalo agora é visual: isolar a posição exata dos glifos nos 11 grupos já anotados antes de propor significado para `a/o` ou `r/l`.

## 15. Rota 6: conferência fina dos glifos

A Rota 6 transformou os 11 grupos com anotação visual direta em uma fila de revisão conservadora.

Saídas:

- `voynich-codex-project/scripts/prepare_glyph_review_queue.py`;
- `voynich-codex-project/docs/rota_6_conferencia_glifos.md`;
- `voynich-codex-project/data/annotations/glyph_review_queue_zl3b.csv`.

Resultado:

- 11 grupos na fila;
- 11 ainda precisam de isolamento exato do glifo;
- fólios envolvidos: `f67r1=5`, `f70v2=3`, `f84r=2`, `f68r3=1`;
- nenhuma atribuição semântica nova foi feita.

Leitura: a evidência visual ainda está em nível de camada/folio. A próxima etapa precisa produzir recortes ou coordenadas aproximadas por `review_id`, mantendo `not isolated` quando a palavra exata não puder ser localizada.

## 16. Rota 7: recortes de revisão

A Rota 7 gerou recortes SVG aproximados para os 11 itens da fila R6.

Saídas:

- `voynich-codex-project/scripts/prepare_review_crops.py`;
- `voynich-codex-project/docs/rota_7_recortes_revisao.md`;
- `voynich-codex-project/data/annotations/review_crop_manifest_zl3b.csv`;
- `voynich-codex-project/images/derived/review_crops/*.svg`.

Resultado:

- 11 recortes SVG gerados;
- todos preservam `needs_exact_glyph_isolation`;
- todos têm escopo `rough_region_only`;
- nenhum JPG original foi modificado.

Leitura: agora a revisão visual é reproduzível por `crop_id`/`review_id`, mas as coordenadas continuam aproximadas. O próximo passo é abrir cada SVG e registrar coordenada melhorada ou manter `not isolated`.

## 17. Rota 8: revisão dos recortes

A Rota 8 validou os SVGs da Rota 7 e registrou a decisão conservadora por recorte.

Saídas:

- `voynich-codex-project/scripts/review_crop_decisions.py`;
- `voynich-codex-project/docs/rota_8_revisao_recortes.md`;
- `voynich-codex-project/data/annotations/crop_review_decisions_zl3b.csv`.

Resultado:

- 11 recortes avaliados;
- 11 SVGs válidos;
- 11 decisões `keep_not_isolated`;
- 8 decisões ainda têm tokens faltantes no grupo;
- nenhuma coordenada de glifo foi confirmada.

Leitura: os recortes são úteis como regiões revisáveis, mas ainda são amplos demais para provar palavra/glifo. A próxima etapa precisa ser revisão manual assistida, não inferência automática.

## 18. Rota 9: revisão manual assistida

A Rota 9 preparou uma folha de revisão manual para tentar coordenadas mais apertadas dentro dos SVGs, sem transformar campo vazio em confirmação.

Saídas:

- `voynich-codex-project/scripts/prepare_manual_svg_review.py`;
- `voynich-codex-project/docs/rota_9_revisao_manual.md`;
- `voynich-codex-project/docs/rota_9_revisao_manual.html`;
- `voynich-codex-project/data/annotations/manual_svg_review_zl3b.csv`.

Resultado:

- 11 itens na folha manual;
- 11 com status inicial `pending_manual_review`;
- famílias priorizadas: `ot`, depois `ch/d`, depois `standalone`;
- campos de coordenada deixados vazios de propósito;
- nenhuma coordenada de glifo foi confirmada.

Leitura: a trilha visual agora tem uma interface de revisão humana. O próximo passo só deve consolidar evidência depois que a folha for preenchida ou explicitamente marcada como `keep_not_isolated`.

## 19. Rota 10: consolidação da revisão manual

A Rota 10 consolidou a folha manual da Rota 9 e verificou se já havia alguma evidência pronta para teste visual fino dos eixos.

Saídas:

- `voynich-codex-project/scripts/consolidate_manual_svg_review.py`;
- `voynich-codex-project/docs/rota_10_consolidacao_manual.md`;
- `voynich-codex-project/data/derived/manual_svg_review_consolidated_zl3b.csv`;
- `voynich-codex-project/data/derived/manual_review_status_summary_zl3b.csv`.

Resultado:

- 11 itens consolidados;
- 11 ainda em `pending_manual_review`;
- 11 sem coordenadas manuais;
- 11 sem confirmação de glifo;
- 0 elegíveis para teste visual dos eixos.

Leitura: a consolidação impediu o salto indevido de “existe folha de revisão” para “existe evidência visual”. A próxima rota deve melhorar os recortes ou preencher manualmente a folha, não atribuir significado a `a/o` ou `r/l`.

## 20. Rota 11: segunda passada de recortes

A Rota 11 transformou os itens pendentes da consolidação em uma fila priorizada para revisão visual operacional.

Saídas:

- `voynich-codex-project/scripts/prepare_second_pass_crop_queue.py`;
- `voynich-codex-project/docs/rota_11_segunda_passada_recortes.md`;
- `voynich-codex-project/data/annotations/second_pass_crop_queue_zl3b.csv`;
- `voynich-codex-project/data/derived/second_pass_crop_queue_summary_zl3b.csv`.

Resultado:

- 11 itens na fila;
- 14 tokens faltantes a procurar;
- 8 itens com foco em localizar tokens faltantes;
- 3 itens para apertar região existente;
- prioridades: `P0=2`, `P1=4`, `P2=2`, `P3=3`.

Leitura: a fila é operacional. Ela diz o que revisar primeiro, não o que `a/o` ou `r/l` significam. Todos os itens preservam a guarda `no_axis_meaning_from_queue_position`.

## 21. Rota 12: pacotes por fólio

A Rota 12 agrupou a fila operacional da Rota 11 por fólio e imagem fonte, para facilitar uma revisão visual guiada por página.

Saídas:

- `voynich-codex-project/scripts/prepare_folio_review_packets.py`;
- `voynich-codex-project/docs/rota_12_pacotes_revisao_guiada.md`;
- `voynich-codex-project/data/annotations/folio_review_packets_zl3b.csv`;
- `voynich-codex-project/data/annotations/folio_review_packet_items_zl3b.csv`;
- `voynich-codex-project/data/derived/folio_review_packet_summary_zl3b.csv`.

Resultado:

- 4 pacotes por fólio/imagem;
- 11 itens preservados;
- 14 tokens faltantes agregados;
- 3 pacotes devem revisar a imagem fonte primeiro;
- 1 pacote deve procurar tokens e redesenhar recorte se houver localização visual.

Leitura: a revisão agora está organizada por página. Ainda assim, pacote não é evidência semântica: é só uma unidade de trabalho visual.

## 22. Rota 13: checklist por pacote

A Rota 13 transformou os itens dos pacotes em uma checklist preenchível para revisão visual item-a-item.

Saídas:

- `voynich-codex-project/scripts/prepare_packet_item_checklist.py`;
- `voynich-codex-project/docs/rota_13_checklist_pacotes.md`;
- `voynich-codex-project/data/annotations/packet_item_checklist_zl3b.csv`;
- `voynich-codex-project/data/derived/packet_item_checklist_summary_zl3b.csv`.

Resultado:

- 11 itens na checklist;
- 8 alvos são tokens faltantes;
- 3 alvos são tokens já anotados que precisam de região mais estreita;
- 11 itens ainda em `pending_visual_check`;
- campos manuais vazios até revisão real.

Leitura: agora há uma folha prática para revisão. Ela ainda não confirma glifo nem significado; só organiza o que deve ser observado.

## 23. Rota 14: consolidação da checklist

A Rota 14 consolidou a checklist preenchível da Rota 13. Como os campos manuais ainda estão vazios, o resultado é uma confirmação formal de pendência.

Saídas:

- `voynich-codex-project/scripts/consolidate_packet_item_checklist.py`;
- `voynich-codex-project/docs/rota_14_consolidacao_checklist.md`;
- `voynich-codex-project/data/derived/packet_item_checklist_consolidated_zl3b.csv`;
- `voynich-codex-project/data/derived/packet_item_checklist_consolidation_summary_zl3b.csv`.

Resultado:

- 11 itens consolidados;
- 11 ainda em `pending_visual_check`;
- 11 sem coordenadas novas;
- 11 sem evidência visual nova;
- 0 elegíveis após geração de recorte.

Leitura: a checklist ainda precisa ser preenchida por revisão visual real. A consolidação não adiciona prova nova; apenas impede que campos vazios sejam interpretados como confirmação ou negativa.

## 24. Rota 15: instruções humanas por pacote

A Rota 15 gerou instruções humanas por pacote/fólio para orientar o preenchimento da checklist sem alterar seus campos automaticamente.

Saídas:

- `voynich-codex-project/scripts/prepare_human_review_instructions.py`;
- `voynich-codex-project/docs/rota_15_instrucoes_revisao_humana.md`;
- `voynich-codex-project/data/annotations/human_review_instructions_zl3b.csv`;
- `voynich-codex-project/data/annotations/human_review_instruction_items_zl3b.csv`;
- `voynich-codex-project/data/derived/human_review_instruction_summary_zl3b.csv`.

Resultado:

- 4 pacotes instruídos;
- 11 itens preservados;
- 3 pacotes no modo `open_source_image_before_svg`;
- 1 pacote no modo `search_tokens_then_redraw_crop`;
- nenhum campo manual preenchido automaticamente;
- guarda semântica: `human_instruction_not_visual_evidence`.

Leitura: agora existe uma camada operacional clara para a revisão humana. Ela diz quais imagens abrir, quais SVGs usar como referência e quais campos preencher, mas não cria evidência visual nem autoriza leitura dos eixos.

## 25. Rota 16: consolidação da revisão humana

A Rota 16 cruzou os itens da Rota 15 com a checklist Rota 13 para transformar respostas humanas preenchidas em categorias operacionais de evidência.

Saídas:

- `voynich-codex-project/scripts/consolidate_human_review_evidence.py`;
- `voynich-codex-project/docs/rota_16_consolidacao_revisao_humana.md`;
- `voynich-codex-project/data/derived/human_review_evidence_consolidated_zl3b.csv`;
- `voynich-codex-project/data/derived/human_review_evidence_summary_zl3b.csv`.

Resultado:

- 11 itens consolidados;
- 11 ainda em `pending_human_review`;
- 11 sem coordenadas novas;
- 11 sem evidência visual humana;
- 0 prontos para novo recorte após revisão.

Leitura: a revisão humana ainda não aconteceu nos campos da checklist. A próxima etapa real é revisar visualmente os itens prioritários e preencher `manual_token_seen`, `manual_new_crop_needed`, `manual_image_insufficient` e coordenadas quando houver.

## 26. Rota 17: fila P0/P1 para revisão humana

A Rota 17 preparou o lote prioritário P0/P1 para revisão visual humana efetiva, sem preencher automaticamente a checklist.

Saídas:

- `voynich-codex-project/scripts/prepare_priority_human_review.py`;
- `voynich-codex-project/docs/rota_17_revisao_humana_p0_p1.md`;
- `voynich-codex-project/data/annotations/priority_human_review_p0_p1_zl3b.csv`;
- `voynich-codex-project/data/derived/priority_human_review_summary_zl3b.csv`.

Resultado:

- 6 itens na fila prioritária;
- `P0=2`;
- `P1=4`;
- fólios: `f67r1=3`, `f70v2=2`, `f68r3=1`;
- todos são alvos `missing_group_tokens`;
- guarda semântica: `priority_review_not_visual_evidence`.

Leitura: agora há uma fila curta e executável para revisão visual. Ela organiza o trabalho, mas não confirma nenhum token. A decisão ainda deve ser preenchida na checklist.

## 27. Rota 18: ingestão das decisões P0/P1

A Rota 18 ingeriu a fila P0/P1 contra a checklist para classificar somente decisões humanas já preenchidas.

Saídas:

- `voynich-codex-project/scripts/ingest_priority_human_decisions.py`;
- `voynich-codex-project/docs/rota_18_ingestao_decisoes_p0_p1.md`;
- `voynich-codex-project/data/derived/priority_human_decisions_p0_p1_zl3b.csv`;
- `voynich-codex-project/data/derived/priority_human_decisions_summary_zl3b.csv`.

Resultado:

- 6 itens P0/P1 ingeridos;
- 6 seguem como `pending_manual_decision`;
- 0 candidatos a novo recorte;
- 6 com `not_ready` para teste de eixo;
- guarda semântica: `priority_decision_not_axis_meaning`.

Leitura: a ingestão confirmou que a decisão visual ainda não foi preenchida. A próxima etapa deve facilitar o preenchimento desses 6 itens, não inferir evidência a partir da fila.

## 28. Rota 19: pacote visual direto P0/P1

A Rota 19 criou um pacote visual direto para reduzir a fricção da revisão dos 6 itens P0/P1 pendentes.

Saídas:

- `voynich-codex-project/scripts/prepare_direct_visual_decision_package.py`;
- `voynich-codex-project/docs/rota_19_pacote_visual_direto_p0_p1.md`;
- `voynich-codex-project/docs/rota_19_pacote_visual_direto_p0_p1.html`;
- `voynich-codex-project/data/annotations/direct_visual_decision_package_p0_p1_zl3b.csv`;
- `voynich-codex-project/data/derived/direct_visual_decision_package_summary_zl3b.csv`.

Resultado:

- 6 itens no pacote visual;
- `P0=2`;
- `P1=4`;
- fólios: `f67r1=3`, `f70v2=2`, `f68r3=1`;
- campos manuais permanecem em branco;
- guarda semântica: `direct_visual_package_not_evidence`.

Leitura: o HTML coloca imagem fonte e SVG lado a lado para apoiar a decisão humana. O pacote é superfície de trabalho, não evidência.

## 29. Rota 20: aplicação do pacote visual na checklist

A Rota 20 tentou aplicar os valores manuais do pacote visual Rota 19 a uma checklist derivada, preservando a checklist original.

Saídas:

- `voynich-codex-project/scripts/apply_direct_visual_decisions.py`;
- `voynich-codex-project/docs/rota_20_aplicacao_decisoes_pacote_visual.md`;
- `voynich-codex-project/data/derived/packet_item_checklist_after_direct_visual_p0_p1_zl3b.csv`;
- `voynich-codex-project/data/derived/direct_visual_decision_application_log_zl3b.csv`;
- `voynich-codex-project/data/derived/direct_visual_decision_application_summary_zl3b.csv`.

Resultado:

- 6 linhas processadas;
- 0 valores manuais aplicados;
- 6 linhas ignoradas por campos vazios;
- nenhum campo vazio apagou valor existente;
- guarda semântica: `applied_values_are_manual_not_axis_meaning`.

Leitura: o pacote visual ainda não foi preenchido. A rota gerou uma checklist derivada sem evidência nova e um log explícito de pendência.

## 30. Rota 21: planilha de preenchimento visual P0/P1

A Rota 21 criou uma planilha enxuta para preencher os 6 itens P0/P1 ainda pendentes com valores controlados.

Saídas:

- `voynich-codex-project/scripts/prepare_visual_decision_entry_sheet.py`;
- `voynich-codex-project/docs/rota_21_planilha_preenchimento_visual_p0_p1.md`;
- `voynich-codex-project/data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv`;
- `voynich-codex-project/data/derived/visual_decision_entry_sheet_summary_zl3b.csv`.

Resultado:

- 6 linhas aguardam entrada manual;
- `P0=2`;
- `P1=4`;
- fólios: `f67r1=3`, `f70v2=2`, `f68r3=1`;
- status: `awaiting_manual_entry=6`;
- guarda semântica: `entry_sheet_not_visual_evidence`.

Leitura: a planilha R21 reduz a superfície de decisão para `manual_token_seen=yes/no/uncertain`, `manual_new_crop_needed=yes/no` e `manual_image_insufficient=yes/no`. Ela continua em branco e não cria evidência visual.

## 31. Rota 22: validação da planilha visual R21

A Rota 22 validou a planilha R21 e preparou um pacote visual derivado que só receberá valores manuais explícitos.

Saídas:

- `voynich-codex-project/scripts/validate_visual_decision_entry_sheet.py`;
- `voynich-codex-project/docs/rota_22_validacao_planilha_visual.md`;
- `voynich-codex-project/data/derived/direct_visual_package_after_entry_sheet_p0_p1_zl3b.csv`;
- `voynich-codex-project/data/derived/visual_decision_entry_validation_log_zl3b.csv`;
- `voynich-codex-project/data/derived/visual_decision_entry_validation_summary_zl3b.csv`.

Resultado:

- 6 linhas validadas;
- 0 entradas válidas;
- 6 entradas pendentes;
- 0 entradas inválidas;
- status de aplicação: `skipped_blank_manual_entry=6`;
- guarda semântica: `validated_values_are_manual_not_axis_meaning`.

Leitura: a validação está pronta, mas a planilha R21 ainda não contém decisão humana. Nenhum campo vazio virou evidência.

## 32. Rota 23: pacote HTML guiado para preencher R21

A Rota 23 criou um HTML guiado para preencher manualmente a planilha R21 com imagem fonte, SVG de referência, valores permitidos e linha alvo.

Saídas:

- `voynich-codex-project/scripts/prepare_guided_visual_entry_html.py`;
- `voynich-codex-project/docs/rota_23_pacote_html_preenchimento_r21.md`;
- `voynich-codex-project/docs/rota_23_pacote_html_preenchimento_r21.html`;
- `voynich-codex-project/data/derived/guided_visual_entry_html_manifest_zl3b.csv`;
- `voynich-codex-project/data/derived/guided_visual_entry_html_summary_zl3b.csv`.

Resultado:

- 6 cartões HTML gerados;
- `P0=2`;
- `P1=4`;
- fólios: `f67r1=3`, `f70v2=2`, `f68r3=1`;
- status: `ready_for_guided_manual_entry=6`;
- guarda semântica: `guided_html_not_visual_evidence`.

Leitura: o HTML reduz a fricção visual, mas não grava decisão. O próximo passo real é preencher a R21 manualmente e reexecutar a Rota 22.

## 33. Rota 24: prontidão para preenchimento visual R21

A Rota 24 verificou se o pacote HTML R23 e seus assets estão prontos para o preenchimento manual da planilha R21.

Saídas:

- `voynich-codex-project/scripts/verify_guided_visual_entry_readiness.py`;
- `voynich-codex-project/docs/rota_24_prontidao_preenchimento_visual.md`;
- `voynich-codex-project/data/derived/guided_visual_entry_readiness_zl3b.csv`;
- `voynich-codex-project/data/derived/guided_visual_entry_readiness_summary_zl3b.csv`.

Resultado:

- 6 itens verificados;
- 6 prontos para preenchimento manual;
- 0 já preenchidos;
- 0 bloqueados por asset;
- 0 bloqueados por HTML;
- guarda semântica: `readiness_check_not_visual_evidence`.

Leitura: a revisão visual está pronta para entrada humana. A planilha R21 segue vazia e nenhum valor foi inferido.

## 34. Rota 25: gate manual de preenchimento R21

A Rota 25 permanece pendente porque exigiria decisão visual humana na planilha R21.

Resultado:

- a R21 segue vazia;
- nenhum `manual_token_seen` foi preenchido por inferência;
- nenhum novo recorte foi inventado;
- o HTML R23 continua sendo o guia operacional.

Leitura: esta rota é um gate humano. A investigação automatizada continuou por uma frente textual/visual independente.

## 35. Rota 26: tabela ampliada das formas exatas ok/ot

A Rota 26 criou uma tabela ampliada das formas `okar/okal/okor/okol/otar/otal/otor/otol`, cruzando contexto textual e anotação visual quando há chave exata.

Saídas:

- `voynich-codex-project/scripts/build_exact_form_context_table.py`;
- `voynich-codex-project/docs/rota_26_tabela_contexto_formas_exatas.md`;
- `voynich-codex-project/data/derived/exact_form_context_table_zl3b.csv`;
- `voynich-codex-project/data/derived/exact_form_context_summary_zl3b.csv`.

Resultado:

- 786 ocorrências exatas;
- `ok* = 394`;
- `ot* = 392`;
- formas mais comuns: `okal=152`, `otar=147`, `okar=133`, `otal=129`;
- 23 com anotação visual exata;
- 763 sem anotação visual exata;
- guarda semântica: `exact_form_context_not_decipherment`.

Leitura: o recorte exato mostra equilíbrio forte entre `ok*` e `ot*`, mas a cobertura visual ainda é pequena. Ausência de anotação visual continua sendo lacuna, não evidência negativa.

## 36. Rota 27: fila de lacunas visuais das formas exatas

A Rota 27 transformou as 763 ocorrências exatas sem anotação visual em uma fila operacional por fólio e tipo de locus.

Saídas:

- `voynich-codex-project/scripts/prepare_exact_form_visual_gap_queue.py`;
- `voynich-codex-project/docs/rota_27_fila_lacunas_visuais_formas_exatas.md`;
- `voynich-codex-project/data/derived/exact_form_visual_gap_queue_zl3b.csv`;
- `voynich-codex-project/data/derived/exact_form_visual_gap_summary_zl3b.csv`.

Resultado:

- 195 grupos de lacuna visual;
- `P0=1`;
- `P1=25`;
- `P2=7`;
- `P3=162`;
- 15 grupos com imagem no manifesto;
- 180 grupos ainda sem imagem no manifesto;
- guarda semântica: `visual_gap_priority_not_evidence`.

Leitura: a fila indica onde revisar primeiro. Ela não transforma ausência de anotação em evidência nem atribui significado a `ok/ot`, `a/o` ou `r/l`.

## 37. Rota 28: pacote de anotação visual P0/P1 das formas exatas

A Rota 28 criou um pacote operacional para os grupos `P0/P1` da fila R27, separando itens com imagem pronta dos que exigem fonte antes de revisão.

Saídas:

- `voynich-codex-project/scripts/prepare_exact_form_visual_annotation_package.py`;
- `voynich-codex-project/docs/rota_28_pacote_anotacao_visual_formas_exatas.md`;
- `voynich-codex-project/docs/rota_28_pacote_anotacao_visual_formas_exatas.html`;
- `voynich-codex-project/data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`;
- `voynich-codex-project/data/derived/exact_form_visual_annotation_package_summary_zl3b.csv`.

Resultado:

- 26 itens empacotados;
- `P0=1`;
- `P1=25`;
- 8 prontos para anotação visual manual;
- 18 bloqueados por falta de imagem fonte;
- guarda semântica: `visual_annotation_package_not_evidence`.

Leitura: esta rota ainda não anota nada. Ela só transforma prioridade em trabalho revisável e mantém os campos manuais vazios.

## 38. Rota 29: fila de fontes de imagem ausentes

A Rota 29 criou uma fila específica para os 18 itens da Rota 28 bloqueados por ausência de imagem fonte.

Saídas:

- `voynich-codex-project/scripts/prepare_missing_source_image_queue.py`;
- `voynich-codex-project/docs/rota_29_fila_fontes_imagem_formas_exatas.md`;
- `voynich-codex-project/docs/rota_29_fila_fontes_imagem_formas_exatas.html`;
- `voynich-codex-project/data/annotations/exact_form_missing_source_queue_p0_p1_zl3b.csv`;
- `voynich-codex-project/data/derived/exact_form_missing_source_summary_zl3b.csv`.

Resultado:

- 18 fontes pendentes;
- `P1=18`;
- `P=17`;
- `C=1`;
- status: `pending_public_source_verification`;
- campos candidatos ainda vazios;
- guarda semântica: `missing_source_queue_not_visual_evidence`.

Leitura: a fila cria consultas e campos de preenchimento. Ela não confirma fonte, não atualiza manifesto e não acrescenta anotação visual.

## 39. Rota 30: validação de fontes candidatas

A Rota 30 validou a fila R29 contra regras estruturais de fonte pública e escreveu uma cópia derivada do manifesto.

Saídas:

- `voynich-codex-project/scripts/validate_missing_source_candidates.py`;
- `voynich-codex-project/docs/rota_30_validacao_fontes_candidatas.md`;
- `voynich-codex-project/data/derived/missing_source_candidate_validation_zl3b.csv`;
- `voynich-codex-project/data/derived/missing_source_candidate_validation_summary_zl3b.csv`;
- `voynich-codex-project/data/derived/commons_image_sources_after_source_validation_zl3b.csv`.

Resultado:

- 18 candidatos avaliados;
- 18 pendentes vazios;
- 0 válidos estruturalmente;
- 0 inválidos;
- 0 anexados ao manifesto derivado;
- guarda semântica: `source_validation_not_visual_evidence`.

Leitura: o caminho de aplicação está pronto, mas ainda não há URL candidata preenchida. A cópia derivada do manifesto continua equivalente ao manifesto original.

## 40. Rota 31: validação de anotações visuais prontas

A Rota 31 validou os 8 itens da Rota 28 que já tinham imagem no manifesto e estavam prontos para anotação manual.

Saídas:

- `voynich-codex-project/scripts/validate_ready_visual_annotations.py`;
- `voynich-codex-project/docs/rota_31_validacao_anotacoes_visuais_prontas.md`;
- `voynich-codex-project/data/derived/ready_visual_annotation_validation_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_manual_visual_annotations_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_annotation_validation_summary_zl3b.csv`.

Resultado:

- 8 itens prontos avaliados;
- 8 pendentes vazios;
- 0 válidos;
- 0 inválidos;
- 0 anotações derivadas gravadas;
- guarda semântica: `manual_visual_annotation_not_axis_meaning`.

Leitura: a validação está pronta, mas ainda não há anotação manual preenchida. Campo vazio continua pendente.

## 41. Rota 32: pacote HTML focado para anotações visuais prontas

A Rota 32 gerou uma superfície pequena para anotar manualmente os 8 itens da Rota 28 que já tinham imagem no manifesto e continuam pendentes na Rota 31.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_annotation_html.py`;
- `voynich-codex-project/docs/rota_32_pacote_html_anotacao_visual_prontos.md`;
- `voynich-codex-project/docs/rota_32_pacote_html_anotacao_visual_prontos.html`;
- `voynich-codex-project/data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_annotation_html_summary_zl3b.csv`.

Resultado:

- 8 cartões HTML gerados;
- 8 pendentes R31;
- `P0=1`;
- `P1=7`;
- `P=6`;
- `L=2`;
- campos manuais ainda vazios;
- guarda semântica: `focused_visual_annotation_html_not_evidence`.

Leitura: a rota facilita a revisão humana, mas não cria anotação visual. A próxima etapa deve aplicar somente valores preenchidos explicitamente e reexecutar a Rota 31.

## 42. Rota 33: aplicação das entradas visuais R32

A Rota 33 aplicou a planilha R32 atual a uma cópia derivada do pacote R28, aceitando somente valores manuais explícitos.

Saídas:

- `voynich-codex-project/scripts/apply_ready_visual_annotation_entries.py`;
- `voynich-codex-project/docs/rota_33_aplicacao_entradas_visuais_r32.md`;
- `voynich-codex-project/data/derived/exact_form_visual_annotation_package_after_ready_entries_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_annotation_entry_application_log_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_annotation_entry_application_summary_zl3b.csv`.

Resultado:

- 8 entradas avaliadas;
- 8 pendentes vazias;
- 0 válidas;
- 0 inválidas;
- 0 linhas atualizadas no pacote derivado;
- pacote R28 original preservado;
- guarda semântica: `ready_visual_entry_application_not_visual_evidence`.

Leitura: a infraestrutura de aplicação está pronta, mas ainda depende de anotação humana na Rota 32.

## 43. Rota 34: gate manual de anotação visual R32

A Rota 34 verificou se a planilha R32 já tem anotação humana suficiente para reexecutar R33 e R31.

Saídas:

- `voynich-codex-project/scripts/verify_ready_visual_annotation_manual_gate.py`;
- `voynich-codex-project/docs/rota_34_gate_manual_anotacao_visual_r32.md`;
- `voynich-codex-project/data/derived/ready_visual_annotation_manual_gate_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_annotation_manual_gate_summary_zl3b.csv`.

Resultado:

- 8 itens verificados;
- 8 bloqueados por anotação manual pendente;
- 0 prontos para reexecutar R33/R31;
- 8 cartões HTML presentes;
- 8 itens com valores permitidos presentes no HTML;
- guarda semântica: `manual_visual_gate_not_evidence`.

Leitura: o pipeline chegou ao gate correto. A próxima evidência visual depende de preenchimento humano explícito na planilha R32.

## 44. Rota 35: plano de reexecução pós-gate R32

A Rota 35 verificou se já havia base manual para reexecutar R33 e R31 depois do gate R34.

Saídas:

- `voynich-codex-project/scripts/plan_ready_visual_annotation_post_gate_rerun.py`;
- `voynich-codex-project/docs/rota_35_plano_reexecucao_pos_gate_r32.md`;
- `voynich-codex-project/data/derived/ready_visual_annotation_post_gate_rerun_plan_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_annotation_post_gate_rerun_summary_zl3b.csv`.

Resultado:

- 8 itens avaliados;
- 8 bloqueados pelo gate manual;
- 0 prontos para reexecução controlada;
- 0 reexecuções R33/R31 planejadas;
- guarda semântica: `post_gate_rerun_not_visual_evidence`.

Leitura: a próxima ação continua sendo humana: preencher a planilha R32 antes de qualquer nova validação visual.

## 45. Rota 36: protocolo de preenchimento humano R32

A Rota 36 preparou um protocolo de preenchimento humano para a planilha R32, sem gravar decisões automaticamente.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_annotation_manual_fill_protocol.py`;
- `voynich-codex-project/docs/rota_36_protocolo_preenchimento_humano_r32.md`;
- `voynich-codex-project/data/derived/ready_visual_annotation_manual_fill_protocol_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_annotation_manual_fill_protocol_summary_zl3b.csv`.

Resultado:

- 8 itens no protocolo;
- 8 aguardando anotação humana;
- 0 prontos para reexecutar gate;
- 0 inválidos;
- planilha R32 original preservada;
- guarda semântica: `manual_fill_protocol_not_visual_evidence`.

Leitura: a próxima mudança de evidência precisa vir de revisão humana explícita no HTML/CSV R32.

## 46. Rota 37: plano de revalidação R34/R35/R33/R31

A Rota 37 definiu a cadeia de revalidação pós-preenchimento da R32, mas não a executou porque ainda não há entrada humana.

Saídas:

- `voynich-codex-project/scripts/plan_ready_visual_annotation_revalidation_chain.py`;
- `voynich-codex-project/docs/rota_37_plano_revalidacao_r34_r35_r33_r31.md`;
- `voynich-codex-project/data/derived/ready_visual_annotation_revalidation_chain_plan_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_annotation_revalidation_chain_summary_zl3b.csv`.

Resultado:

- 8 itens avaliados;
- 8 bloqueados sem entrada humana;
- 0 prontos para cadeia de revalidação;
- 0 execuções planejadas;
- guarda semântica: `revalidation_chain_not_visual_evidence`.

Leitura: a ordem `R34>R35>R33>R31` está pronta, mas só deve rodar depois de preenchimento humano explícito da R32.

## 47. Rota 38: ordem de trabalho para preencher R32

A Rota 38 criou uma ordem de trabalho para preencher manualmente a planilha R32 e reabrir a cadeia de revalidação.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_annotation_manual_reopen_work_order.py`;
- `voynich-codex-project/docs/rota_38_ordem_trabalho_preencher_r32_reabrir_cadeia.md`;
- `voynich-codex-project/data/derived/ready_visual_annotation_manual_reopen_work_order_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_annotation_manual_reopen_work_order_summary_zl3b.csv`.

Resultado:

- 8 itens na ordem de trabalho;
- 8 exigem preenchimento manual;
- 0 prontos para reabrir cadeia;
- 0 inválidos;
- planilha R32 original preservada;
- guarda semântica: `manual_reopen_work_order_not_visual_evidence`.

Leitura: o estudo chegou a uma tarefa humana bem delimitada. Sem preenchimento visual explícito, a cadeia continua fechada.

## 48. Rota 39: auditoria da execução do preenchimento humano R32

A Rota 39 auditou se a ordem R38 foi efetivamente preenchida na planilha R32.

Saídas:

- `voynich-codex-project/scripts/audit_ready_visual_annotation_manual_fill_execution.py`;
- `voynich-codex-project/docs/rota_39_auditoria_execucao_preenchimento_humano_r32.md`;
- `voynich-codex-project/data/derived/ready_visual_annotation_manual_fill_execution_audit_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_annotation_manual_fill_execution_audit_summary_zl3b.csv`.

Resultado:

- 8 itens auditados;
- 8 sem preenchimento humano executado;
- 0 prontos para reabrir a cadeia;
- 0 inválidos ou parciais;
- planilha R32 original preservada;
- guarda semântica: `manual_fill_execution_audit_not_visual_evidence`.

Leitura: a auditoria não criou evidência visual nova. Ela confirmou formalmente que o próximo avanço depende de preenchimento humano explícito na R32.

## 49. Rota 40: plano condicional de reabertura da cadeia

A Rota 40 converteu a auditoria R39 em um plano operacional para decidir se a cadeia `R34>R35>R33>R31` pode ser reaberta.

Saídas:

- `voynich-codex-project/scripts/plan_ready_visual_annotation_conditional_chain_reopen.py`;
- `voynich-codex-project/docs/rota_40_plano_condicional_reabertura_cadeia_r39.md`;
- `voynich-codex-project/data/derived/ready_visual_annotation_conditional_chain_reopen_plan_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_annotation_conditional_chain_reopen_summary_zl3b.csv`.

Resultado:

- 8 itens planejados;
- 8 bloqueados aguardando entrada humana;
- 0 prontos para rodar a cadeia;
- 0 inválidos;
- ação planejada: `do_not_run_revalidation_chain`;
- guarda semântica: `conditional_chain_reopen_plan_not_visual_evidence`.

Leitura: a cadeia continua fechada. A regra agora está explícita: só executar `R34>R35>R33>R31` se a R39 liberar `ready_to_reopen_chain`.

## 50. Rota 41: pacote de entrada humana externa na R32

A Rota 41 preparou um pacote operacional para que um revisor humano externo preencha a R32.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_annotation_external_human_entry_packet.py`;
- `voynich-codex-project/docs/rota_41_pacote_entrada_humana_externa_r32.md`;
- `voynich-codex-project/data/derived/ready_visual_annotation_external_human_entry_packet_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_annotation_external_human_entry_summary_zl3b.csv`.

Resultado:

- 8 itens no pacote;
- 8 exigem entrada humana externa;
- 0 entradas humanas presentes;
- 0 inválidas ou parciais;
- planilha R32 original preservada;
- guarda semântica: `external_human_entry_packet_not_visual_evidence`.

Leitura: o próximo avanço depende de revisão visual humana real. A R41 não criou evidência nova; apenas organizou o trabalho humano exigido.

## 51. Rota 42: fontes Yale IIIF high-res para R32

A Rota 42 baixou fontes oficiais Yale/Beinecke em alta resolução para melhorar a revisão humana da R32.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_annotation_highres_source_packet.py`;
- `voynich-codex-project/docs/rota_42_fontes_yale_iiif_highres_r32.md`;
- `voynich-codex-project/docs/rota_42_pacote_html_yale_iiif_highres_r32.html`;
- `voynich-codex-project/data/derived/yale_iiif_manifest_2002046.json`;
- `voynich-codex-project/data/derived/ready_visual_annotation_highres_sources_zl3b.csv`;
- `voynich-codex-project/images/raw/yale_iiif_r32/*.jpg`.

Resultado:

- 8 itens da R32 mapeados no manifesto Yale;
- 8 JPEGs IIIF baixados localmente;
- 0 fontes sem match;
- dimensões entre `2702x3765` e `9078x3777`;
- guarda semântica: `highres_source_download_not_visual_evidence`.

Leitura: há agora um HTML de revisão visual mais nítido. A rota melhora a fonte de imagem, mas não preenche anotação manual nem reabre a cadeia.

## 52. Rota 42A: análise assistida das fontes Yale high-res para R32

A Rota 42A analisou as novas imagens oficiais em alta resolução para orientar o preenchimento humano da R32, sem converter a leitura da IA em evidência.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_annotation_highres_ai_assist.py`;
- `voynich-codex-project/tests/test_ready_visual_annotation_highres_ai_assist.py`;
- `voynich-codex-project/docs/rota_42a_analise_assistida_highres_r32.md`;
- `voynich-codex-project/data/derived/ready_visual_annotation_highres_ai_assist_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_annotation_highres_ai_assist_summary_zl3b.csv`.

Resultado:

- 8 itens avaliados;
- 2 regiões claramente localizáveis para recorte;
- 4 regiões parcialmente localizáveis;
- 2 páginas compostas exigem desambiguação e recorte;
- 0 decisões exatas de token tomadas pela IA;
- cadeia ainda bloqueada nos 8 itens;
- guarda semântica: `ai_highres_visual_assist_not_human_evidence`.

Leitura: as fontes novas ajudam, especialmente em `f84r` e `f99r`, mas ainda falta revisão humana explícita na R32 para transformar isso em evidência operacional.

## 53. Rota 42B: ferramenta guiada de preenchimento humano R32 high-res

A Rota 42B criou uma ferramenta HTML guiada para preenchimento manual da R32 usando as fontes high-res e a orientação R42A.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_annotation_highres_human_fill_html.py`;
- `voynich-codex-project/tests/test_ready_visual_annotation_highres_human_fill_html.py`;
- `voynich-codex-project/docs/rota_42b_preenchimento_humano_highres_r32.md`;
- `voynich-codex-project/docs/rota_42b_pacote_html_preenchimento_humano_r32.html`;
- `voynich-codex-project/data/derived/ready_visual_annotation_highres_human_fill_html_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_annotation_highres_human_fill_html_summary_zl3b.csv`.

Resultado:

- 8 itens de revisão guiada;
- ordem de revisão começando por `f84r` e `f99r`;
- pergunta `Você achou essas palavrinhas na imagem?`;
- cartões visuais EVA para comparar o desenho da palavra com a imagem;
- total de entradas/loci ZL3b por fólio, lista auditável dessas entradas e prévia textual das linhas alvo;
- botões simples `Achei`/`Não achei`/`Não sei`, mapeados para `annotated/not_visible/uncertain`;
- fila lateral, item ativo, próximo pendente, zoom, contraste, rotação, mostrar/esconder zonas, subir/descer zonas, reset de vista e atalho `Calibrar linhas` para a R42C;
- baselines calibradas da R42C quando existirem, com fallback para zonas visuais prováveis de bloco quando a linha ainda estiver pendente;
- chips de tokens/linhas e detalhes técnicos recolhidos;
- guia rápido, nota automática e rascunho CSV recolhido para uso no final;
- R32 original preservada;
- guarda semântica: `highres_human_fill_html_not_visual_evidence`.

Leitura: a fricção de preenchimento caiu e a revisão ficou mais intuitiva. Ainda assim, as baselines R42C são apoio operacional de localização, não evidência automática. Quando uma baseline ainda não existe, as zonas visuais seguem ajustáveis e aproximadas por bloco, não linhas exatas; a ferramenta não calcula posição visual por proporção da numeração ZL3b. O total por fólio segue entradas/loci ZL3b e não é uma contagem visual direta da imagem. Os deslocamentos de zona agora são temporários, então recarregar a página volta ao mapa calibrado. A página é apoio operacional, não evidência.

## 54. Rota 42C: calibração manual de linhas/baselines R32 high-res

A Rota 42C criou uma ferramenta HTML local para calibrar as linhas reais dos loci alvo da R42B com baselines manuais.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_line_calibration_tool.py`;
- `voynich-codex-project/tests/test_ready_visual_line_calibration_tool.py`;
- `voynich-codex-project/data/annotations/ready_visual_line_calibration_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_line_calibration_summary_zl3b.csv`;
- `voynich-codex-project/docs/rota_42c_calibracao_linhas_baseline_r32.md`;
- `voynich-codex-project/docs/rota_42c_calibrador_linhas_baseline_r32.html`.

Resultado:

- 19 linhas/loci alvo para calibrar;
- todos continuam como `pending_calibration`;
- 2 alvos (`f84r.24,+P0` e `f84r.29,+P0`) agora têm `baseline_points` em rascunho OpenCV agrupado, ainda pendentes;
- o usuário seleciona um locus, segue um `Guia rápido`, vê progresso, mira, coordenadas percentuais e último clique, e clica no começo e no fim da linha real;
- a seção `Ajuste fino` permite mover a linha inteira ou só o ponto esquerdo/direito em passos pequenos, sem criar novas colunas no CSV;
- o painel da imagem ganhou respiro de scroll para zoom alto, scroll natural para cima quando o painel chega no topo, e botão `Topo da imagem` para voltar ao canto superior;
- a ferramenta gera CSV de calibração separado, com botões `Copiar CSV` e `Baixar CSV`;
- a página tem atalhos `Abrir R42B`, `Abrir sugestões OpenCV` e `Abrir mapa OpenCV`;
- quando a R42D gera sugestão OpenCV, o script mescla esses pontos no CSV como rascunho pendente, registra a linha visual OpenCV candidata e `Acao OpenCV: prefill_pending_baseline`, e a página mostra `Computador ja ajudou` com o próximo passo humano antes de marcar como calibrada;
- o overlay do scan fica preso ao canvas real da imagem, para não atravessar o fundo/painel fora da página;
- cada item do HTML recebe uma assinatura determinística do scan; se a sugestão/geração mudar, rascunho local antigo é rejeitado, preservando calibração manual real;
- o HTML invalida rascunhos locais antigos por versão e tem botão `Resetar scan local` para limpar sobras do navegador;
- o script preserva baselines manuais existentes se for executado novamente;
- status `calibrated` sem pelo menos dois pontos válidos volta para `pending_calibration`, tanto no CSV quanto no rascunho local antigo;
- R32 original preservada;
- guarda semântica: `line_calibration_tool_not_visual_evidence`.

Leitura: esta rota resolve a ambiguidade das zonas grandes sem fingir leitura automática. A baseline calibrada é referência operacional de localização, não evidência visual nem tradução.

## 55. Rota 42D: sugestões OpenCV para calibração inicial

A Rota 42D usa OpenCV como assistente de pré-calibração, detectando faixas de tinta/texto nas imagens high-res e gerando sugestões iniciais para a R42C.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_line_opencv_suggestions.py`;
- `voynich-codex-project/tests/test_ready_visual_line_opencv_suggestions.py`;
- `voynich-codex-project/data/derived/ready_visual_line_opencv_suggestions_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_line_opencv_suggestions_summary_zl3b.csv`;
- `voynich-codex-project/docs/rota_42d_sugestoes_opencv_linhas_r32.md`;
- `voynich-codex-project/docs/rota_42d_sugestoes_opencv_linhas_r32.html`.

Resultado:

- 19 alvos analisados;
- 2 sugestões OpenCV para `f84r.24` e `f84r.29`, ligadas às linhas visuais agrupadas 6 e 14, classificadas como `prefill_pending_baseline` com confiança operacional `media`;
- 13 alvos com faixas detectadas, mas ainda exigindo zona/bloco manual (`needs_manual_zone`);
- 4 alvos sem faixa confiável detectada (`needs_better_scan_or_manual_line`);
- a R42C consome as sugestões como `baseline_points` em rascunho pendente para `f84r.24,+P0` e `f84r.29,+P0`;
- nenhuma sugestão vira `calibrated` sem confirmação humana;
- guarda semântica: `opencv_initial_line_suggestion_not_visual_evidence`.

Leitura: OpenCV resolve sozinho a parte mecânica segura: detectar faixas, numerar linhas visuais e pré-preencher rascunhos de baseline quando já existe zona manual. Ele ainda não resolve sozinho o vínculo final entre locus ZL3b e posição visual; o humano confirma.

## 56. Rota 42E: mapa OpenCV de linhas visuais

A Rota 42E cria uma página separada para contar e numerar linhas visuais detectadas por OpenCV nas imagens high-res.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_line_opencv_map.py`;
- `voynich-codex-project/tests/test_ready_visual_line_opencv_map.py`;
- `voynich-codex-project/data/derived/ready_visual_line_opencv_map_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_line_opencv_map_images_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_line_opencv_map_summary_zl3b.csv`;
- `voynich-codex-project/docs/rota_42e_mapa_opencv_linhas_visuais_r32.md`;
- `voynich-codex-project/docs/rota_42e_mapa_opencv_linhas_visuais_r32.html`.

Resultado:

- 8 imagens mapeadas;
- 52 linhas visuais agrupadas por OpenCV no mapa bruto;
- f84r tem 23 linhas visuais agrupadas no mapa bruto, não 47 entradas/loci ZL3b;
- R42D usa esse agrupamento filtrado para sugerir `f84r.24,+P0` como linha visual 6 e `f84r.29,+P0` como linha visual 14;
- a página abre em modo focado nas zonas R32 conhecidas, desenha réguas finas em vez de caixas grandes e ainda oferece `Mapa bruto` para auditoria;
- a página tem navegação para R42B, R42C e R42D;
- guarda semântica: `opencv_visual_line_map_not_word_evidence`.

Leitura: a R42E resolve a confusão entre “número de linha da transcrição” e “linha visual detectada na imagem”. Ela conta linhas visuais, mas não confirma palavras nem tradução.

## 57. Rota 42F: escolha simples de linhas visuais sem zona

A Rota 42F criou uma ferramenta local para os 13 casos em que o OpenCV detectou linhas na imagem, mas ainda precisa saber qual linha visual combina com o locus ZL3b.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_line_zone_choice_tool.py`;
- `voynich-codex-project/tests/test_ready_visual_line_zone_choice_tool.py`;
- `voynich-codex-project/data/annotations/ready_visual_line_zone_choice_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_line_zone_choice_summary_zl3b.csv`;
- `voynich-codex-project/docs/rota_42f_escolha_linhas_visuais_sem_zona_r32.md`;
- `voynich-codex-project/docs/rota_42f_escolha_linhas_visuais_sem_zona_r32.html`.

Resultado:

- 13 alvos pendentes de escolha (`pending_zone_choice`);
- a página mostra linhas visuais reais da R42E e permite clicar em `Essa e a linha`;
- a escolha gera `selected_zone_box_pct`, que a R42D pode consumir para criar novas sugestões `prefill_pending_baseline`;
- guarda semântica: `line_zone_choice_not_visual_evidence`.

Leitura: esta rota separa bem máquina e humano. OpenCV mostra as linhas possíveis; o humano escolhe a correspondente; só depois a R42D transforma isso em baseline pendente.

## 58. Rota 42G: painel único de ferramentas ativas R32

A Rota 42G removeu as páginas HTML antigas do caminho e criou uma entrada única para o fluxo atual.

Saídas:

- `voynich-codex-project/scripts/prepare_active_tool_dashboard.py`;
- `voynich-codex-project/tests/test_active_tool_dashboard.py`;
- `voynich-codex-project/docs/rota_42g_ferramentas_ativas_r32.md`;
- `voynich-codex-project/docs/rota_42g_ferramentas_ativas_r32.html`.

Resultado:

- 10 ferramentas HTML ativas: R42G, R42K, R42L, R42M, R42F, R42D, R42J, R42C, R42B e R42E;
- 8 ferramentas HTML antigas removidas da pasta `docs`;
- as páginas ativas ganharam link para `Ferramentas ativas`;
- a limpeza é idempotente e pode ser reexecutada sem recriar páginas antigas;
- guarda operacional: esta rota não altera evidência, tradução ou planilhas de anotação.

Leitura: agora existe uma porta de entrada limpa para continuar o preenchimento sem tropeçar nas ferramentas antigas.

## 59. Rota 42H: renderização visual EVA nas ferramentas ativas

A Rota 42H criou um renderizador SVG compartilhado para mostrar palavras EVA como desenho nas ferramentas humanas ativas.

Saídas:

- `voynich-codex-project/scripts/eva_visual.py`;
- `voynich-codex-project/tests/test_eva_visual.py`;
- R42B, R42C e R42F atualizadas para usar `eva-visual-line` e `eva-word`.

Resultado:

- textos de referência deixam de aparecer principalmente como strings cruas tipo `okar,y`;
- cada palavra vira um cartão visual SVG;
- tokens alvo ficam destacados;
- R42C e R42F mostram `Texto de referencia visual`;
- CSVs e dados técnicos ainda preservam o texto cru para auditoria.

Leitura: isso melhora a comparação humana com a imagem. Não é tradução, evidência visual nova nem decifração.

## 60. Rota 42I: recortes reais e lupas nas ferramentas ativas

A Rota 42I reduziu mais uma camada de dificuldade humana: em vez de depender só de texto EVA ou de desenho SVG de referência, as ferramentas agora mostram recortes reais da própria imagem do manuscrito quando existe zona, linha OpenCV ou baseline.

Saídas:

- `voynich-codex-project/scripts/visual_crop.py`;
- `voynich-codex-project/tests/test_visual_crop.py`;
- R42B com `Recortes reais da pagina`;
- R42C com `Lupa da linha`;
- R42D com recorte real da sugestão OpenCV;
- R42E com recortes das linhas detectadas;
- R42F com botões clicáveis que mostram o recorte real de cada linha candidata.

Resultado:

- a comparação principal passa a ser imagem contra imagem;
- R42F deixa de pedir que a pessoa escolha por número de linha e passa a oferecer recortes clicáveis;
- R42C mostra a lupa derivada dos pontos atuais ou da sugestão OpenCV;
- R42B mostra primeiro o recorte real da região alvo, usando baseline calibrada quando existir ou zona conhecida quando ainda não houver baseline;
- o painel R42G orienta o uso pelo novo modo de recortes;
- os recortes são renderizados no navegador a partir da imagem original e de caixas percentuais, preservando idempotência dos geradores.

Leitura: isto melhora usabilidade e reduz erro humano. Não é tradução, OCR, evidência automática nem confirmação de palavra.

## 61. Rota 42J: análise fina OpenCV de fragmentos visuais

A Rota 42J criou uma análise mais fina por computer vision: dentro das linhas visuais da R42E, o OpenCV separa pedaços de tinta em fragmentos visuais parecidos com palavras.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_word_opencv_map.py`;
- `voynich-codex-project/tests/test_ready_visual_word_opencv_map.py`;
- `voynich-codex-project/data/derived/ready_visual_word_opencv_map_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_word_opencv_map_summary_zl3b.csv`;
- `voynich-codex-project/docs/rota_42j_fragmentos_visuais_opencv_r32.md`;
- `voynich-codex-project/docs/rota_42j_fragmentos_visuais_opencv_r32.html`.

Resultado:

- 52 linhas visuais de entrada vindas da R42E;
- 77 fragmentos visuais detectados;
- R42J entrou no painel de ferramentas ativas;
- R42B, R42C, R42D, R42E e R42F ganharam atalhos para a rota quando útil;
- cada fragmento aparece como recorte real da imagem, agrupado por linha visual.

Leitura: isto é uma lupa operacional. Não é OCR, tradução, leitura de EVA, confirmação automática de palavra nem preenchimento da R32.

## 62. Rota 42K: fila priorizada de revisão visual

A Rota 42K criou o próximo passo operacional: uma fila que cruza as 13 pendências da R42F com os fragmentos visuais da R42J e ordena o que deve ser revisado primeiro.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_review_priority_queue.py`;
- `voynich-codex-project/tests/test_ready_visual_review_priority_queue.py`;
- `voynich-codex-project/data/derived/ready_visual_review_priority_queue_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_review_priority_queue_summary_zl3b.csv`;
- `voynich-codex-project/docs/rota_42k_fila_priorizada_revisao_visual_r32.md`;
- `voynich-codex-project/docs/rota_42k_fila_priorizada_revisao_visual_r32.html`.

Resultado:

- 13 pendências priorizadas;
- 4 itens em `revisar_primeiro`;
- 4 itens em `revisar_depois`;
- 5 itens em `revisao_dificil`;
- R42K entrou no painel de ferramentas ativas;
- R42F e R42J ganharam atalhos diretos para a fila;
- R42K aponta para a R42L como etapa de confirmação antes de aplicar qualquer linha.

Leitura: isto não decide a linha correta sozinho. A R42K só diz por onde começar para reduzir atrito humano, mantendo a decisão final na R42L/R42F/R42C.

## 63. Rota 42L: confirmação de linhas sugeridas

A Rota 42L criou a ponte natural entre a fila priorizada R42K e a escolha manual R42F: uma tela para confirmar ou trocar a linha visual sugerida antes de qualquer aplicação.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_line_choice_confirmation.py`;
- `voynich-codex-project/tests/test_ready_visual_line_choice_confirmation.py`;
- `voynich-codex-project/data/annotations/ready_visual_line_choice_confirmation_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_line_choice_confirmation_summary_zl3b.csv`;
- `voynich-codex-project/docs/rota_42l_confirmacao_linhas_sugeridas_r32.md`;
- `voynich-codex-project/docs/rota_42l_confirmacao_linhas_sugeridas_r32.html`.

Resultado:

- 13 itens pendentes de confirmação humana;
- 4 itens vieram de `revisar_primeiro`;
- 4 itens vieram de `revisar_depois`;
- 5 itens vieram de `revisao_dificil`;
- R42L entrou no painel de ferramentas ativas;
- o CSV de confirmação preserva a linha sugerida, mas deixa `selected_visual_line_number` e `selected_zone_box_pct` vazios;
- R42L aponta para a R42M como lupa de captura fina antes de aplicar a escolha.

Leitura: a R42L não aplica a sugestão automaticamente. Ela transforma o palpite operacional da R42K em uma decisão humana explícita, auditável e reversível.

## 64. Rota 42M: captura fina de linhas

A Rota 42M criou um alinhamento de captura mais preciso que a zona grande inicial: ela cruza a linha sugerida da R42L com os fragmentos visuais da R42J e produz um recorte mais estreito para conferência.

Saídas:

- `voynich-codex-project/scripts/prepare_ready_visual_fine_line_capture.py`;
- `voynich-codex-project/tests/test_ready_visual_fine_line_capture.py`;
- `voynich-codex-project/data/derived/ready_visual_fine_line_capture_zl3b.csv`;
- `voynich-codex-project/data/derived/ready_visual_fine_line_capture_summary_zl3b.csv`;
- `voynich-codex-project/docs/rota_42m_captura_fina_linhas_r32.md`;
- `voynich-codex-project/docs/rota_42m_captura_fina_linhas_r32.html`.

Resultado:

- 13 capturas finas geradas;
- 13 continuam exigindo confirmação humana;
- confiança operacional: 11 `media`, 2 `baixa`;
- R42M entrou no painel de ferramentas ativas;
- `selected_visual_line_number` e `selected_zone_box_pct` continuam vazios.

Leitura: a R42M melhora o alinhamento da captura, não a interpretação. Ela é uma lupa operacional, não OCR, tradução, confirmação de palavra ou evidência visual final.

## 65. Rota 43: collocações e padrões terminais das 8 formas exatas

A Rota 43 analisou a vizinhança imediata, trigramas e bigrams para as 8 formas `okal/okar/okol/okor/otal/otar/otol/otor`.

Saídas:

- `voynich-codex-project/scripts/analyze_form_collocations.py`;
- `voynich-codex-project/docs/rota_43_collocacoes_formas_exatas.md`;
- `voynich-codex-project/data/derived/form_standalone_collocations_zl3b.csv`;
- `voynich-codex-project/data/derived/form_collocation_trigrams_zl3b.csv`;
- `voynich-codex-project/data/derived/form_collocation_summary_zl3b.csv`.

Resultado principal:

- formas `-ar` (okar+otar): 15.4% seguidas por standalone `ar/al/or/ol`;
- formas `-al/-ol` (okal+otal+okol+otol): 6.8%;
- chi²(1 df) = 10.54 (p ≈ 0.001) — assimetria **estatisticamente significativa**;
- trigrama mais frequente: `okar ar _END_` (n=8) — forma `-ar` fecha o locus com standalone `ar`;
- bigrama forma×forma mais frequente: `okar → okar` (n=5); `okar → otar` (n=5);
- sequência dupla de bordas confirmada: `otar ar al` (n=3), `otar or ol` (n=2).

Leitura:

> As formas terminadas em `-ar` (okar, otar) encerram loci com standalone `ar` a uma taxa significativamente maior do que formas `-al/-ol`. Isso reforça a hipótese de que `-ar` tem um papel de **fechamento forte ou slot-final** no sistema. A sequência `otar ar al` sugere que o standalone pode codificar um **segundo valor de slot** — não só repetição do sufixo da forma longa.

## 66. Conclusão atualizada

A melhor leitura atual é:

> O Voynich não deve ser atacado como texto contínuo comum. Deve ser atacado como sistema formal com camadas. A unidade real talvez não seja a “palavra”, mas o template dentro de uma linha/locus.

A chave parcial provavelmente não será uma tradução lexical, mas uma tabela funcional.

Novo dado (Rota 43): as formas `-ar` têm padrão de fechamento de locus estatisticamente distinto das formas `-al/-ol`. O standalone `ar` parece funcionar como marcador terminal específico da família `-ar`. A sequência `FORM-ar + ar + al` (e variantes) pode codificar pares de valores no mesmo slot.

## 67. Rota 44: distribuição por seção e Currier A/B — novo achado paradigmático

A Rota 44 analisou as 8 formas exatas por seção do manuscrito e pelos regimes Currier A/B, com análise visual complementar das 8 imagens Yale IIIF (visual-annotator).

Saídas:

- `voynich-codex-project/scripts/analyze_section_distribution.py`;
- `voynich-codex-project/docs/research/rota_44_distribuicao_secoes_currier.md`;
- `voynich-codex-project/data/derived/section_currier_suffix_zl3b.csv`;
- `voynich-codex-project/data/derived/section_form_distribution_zl3b.csv`;
- `voynich-codex-project/data/derived/section_locus_suffix_zl3b.csv`;
- `voynich-codex-project/data/derived/section_distribution_summary_zl3b.csv`.

### Achado principal — operador e borda são camadas independentes

| Métrica | Cramer's V |
|---------|-----------|
| Currier × sufixo (`-ar/-al/-or/-ol`) | **0.1595** |
| Currier × prefixo (`ok-/ot-`) | **0.0113** |
| Secção × forma | 0.1480 |
| Locus × sufixo | 0.0699 |

A borda é **14× mais sensível ao dialeto do que o operador.** O prefixo `ok-/ot-` mantém proporção ~50/50 nos dois Currier, enquanto o sufixo varia fortemente:

- **Currier A**: bordas `-ol/-or` dominantes (76%), `-ar` raro (6%)
- **Currier B**: bordas `-ar/-al` dominantes (73%), `-ar` é a borda modal (42%)

### Achados visuais (visual-annotator, Rota 44)

Análise direta das 8 imagens IIIF revelou três achados visuais:

1. **`okar + okor` adjacentes em f99r** (topo de catálogo farmacêutico): par mínimo `-ar/-or` confirmado em locus visual idêntico.
2. **`okal + okol` adjacentes em f67v1** (diagrama cosmológico): par mínimo `-al/-ol` confirmado no mesmo diagrama radial.
3. **`okol` aparece em TODOS os regimes visuais** (diagrama, catálogo, prosa): é "agnóstico ao gênero da página" — assinatura de elemento gramatical, não de rótulo de conteúdo.

### Achado da seção astronômica

Na seção de estrelas (23% de todas as 786 ocorrências):
- Estrelas "Light star, 7 points, tail" → `okal` domina
- Estrelas "dotted, 7 points, tail" → `otar/otal` domina

A forma exata varia com um **atributo pictórico discreto da estrela adjacente** — evidência mais forte até agora de função "índice/atributo", não "nome de objeto".

### Interpretação consolidada

> O operador (`ok-/ot-`) é compartilhado por ambos os dialetos — codifica algo universal ao sistema (talvez o tipo de entrada ou operação). A borda (`-ar/-al/-or/-ol`) varia sistematicamente entre dialetos — codifica algo que mudou entre mãos/épocas/locais (talvez um estado, classe ou contexto). Os pares mínimos confirmados in situ (f67v1 e f99r) provam que `-al/-ol` e `-ar/-or` marcam distinções reais dentro do mesmo contexto visual, não variação aleatória.

Isso é consistente com a hipótese de **nomenclator ou tabela de lookup** onde diferentes escribas usaram diferentes valores de borda para o mesmo referente, mas mantiveram os operadores constantes.

## 68. Rota 45: correção do Currier — eixo a/o é o marcador de dialeto

A Rota 44 usava regex de texto livre para detectar Currier, cobrindo apenas 97/786 loci (12%). A Rota 45 corrigiu usando o código IVTFF `$L=A/B` dos headers do ZL3b, cobrindo 696/786 loci (88.5%).

Saídas:
- `voynich-codex-project/data/derived/exact_form_context_table_currier_zl3b.csv` (com coluna `currier`);
- `voynich-codex-project/docs/research/rota_45_currier_eixo_ao.md`.

### Números corrigidos

| | Currier A (n=186) | Currier B (n=510) |
|---|---|---|
| `-ol` | 78 (42%) | 50 (10%) |
| `-al` | 51 (27%) | 204 (40%) |
| `-or` | 34 (18%) | 30 (6%) |
| `-ar` | 23 (12%) | 226 (44%) |

Chi²=144.07, **V=0.4550**, p_permutação=0.0000.

### Decomposição em dois bits

| Eixo | V | Currier A | Currier B |
|------|---|-----------|-----------|
| **a/o** (vogal) | **0.4409** | 60% `o` (ol,or) | 84% `a` (ar,al) |
| **r/l** (consoante) | 0.1739 | 69% `l` | 50% `l` / 50% `r` |

**O efeito Currier concentra-se no EIXO a/o (V=0.44), não no r/l (V=0.17).**

- **Currier A = dialeto-o**: prefere vogal `o` nos sufixos
- **Currier B = dialeto-a**: prefere vogal `a` nos sufixos
- O eixo r/l é secundário e mais equilibrado

### Correção importante: dotted/plain star era ruído

O sinal "estrela dotted → otar, plain → okal" da Rota 44 NÃO sobreviveu controle de permutação: chi²=3.27, p=0.374. Era artefato de amostragem. O sinal Currier×sufixo, por outro lado, é robusto (p=0.0000).

### Achado visual confirmado (visual-annotator)

Em f67v1, okal e okol habitam a **mesma banda concêntrica** do diagrama solar (anel de estrelas), diferindo apenas em posição angular (~2 setores). Em f99r, okar e okor são entradas sequenciais na mesma fila de rótulos. Ambos os pares são Currier A e provam distinção **intra-dialectal** — não inter-dialectal.

### Interpretação consolidada

> O eixo a/o é o marcador de escriba/dialeto: A usa vogal-o, B usa vogal-a.
> O eixo r/l marca contexto/posição dentro de cada dialeto.
> A borda pode ser bidimensional: bit_ao = convenção de escriba; bit_rl = slot de posição.

### Rota 46 — design do teste decisivo

A Rota 46 testará se o bit a/o ancora no **objeto visual** (M5 — atributo) ou no **escriba** (M3 — dialeto) via estratificação:

- Calcular V(Currier × bit_ao) dentro de cada tipo de objeto pictórico (estrelas dotted/plain, etc.)
- Se V cai para ~0 com objeto fixo → objeto determina a borda (M5 vence)
- Se V permanece ~0.44 → escriba determina a borda (M3 vence)
- Alvo: seção astronômica f67–f73 (única mista A+B); fólio f69r (49 rótulos, B puro) como controle

Design completo: `voynich-codex-project/docs/research/rota_46_design_ancoragem_borda.md`.

## 69. Rotas 46–47: M5 refutado — bit a/o é assinatura de escriba

A Rota 46 (estratificação por tipo de estrela) revelou colinearidade objeto↔Currier: todos os tipos finos de estrela são 100% Currier B. No único estrato misto, A e B convergem na proporção a/o (p=0.44, NS). A Rota 47 fez o teste decisivo usando seções com mistura real A/B.

Saídas:
- `voynich-codex-project/scripts/analyze_section_scribe.py`;
- `voynich-codex-project/docs/research/rota_47_seccao_vs_escriba_ao.md`;
- `voynich-codex-project/data/derived/section_scribe_ao_zl3b.csv`;
- `voynich-codex-project/data/derived/section_scribe_intra_ao_zl3b.csv`.

### Teste decisivo: mesma seção, escribas diferentes

| Seção | n | Currier A | Currier B | V(Currier×ao) |
|-------|---|-----------|-----------|---------------|
| Herbal | 178 | 40% a / 60% o | 91% a / 9% o | **0.5068** (p=2.7e-12) |
| Pharmaceutical | 78 | 29% a / 71% o | 91% a / 9% o | **0.5627** (p=5e-7) |
| Astronomical | 239 | A≈0 | B=dominante | 0.0461 (sem contraste) |

**Dentro das mesmas seções (herbal, pharmaceutical), A e B divergem maximamente no bit a/o.** O sinal Currier×ao (V=0.45) NÃO é artefato de seção — é assinatura de escriba. M5 (atributo-do-objeto) está refutado para o bit a/o. M3 (dialeto/escriba) confirmado.

### Achado textual complementar (análise de 102 linhas EVA)

- **-l (al/ol) precede `<END>` e `daiin` 5× cada; -r (ar/or) nunca fecha linha** → Rota 43 confirmada no nível da linha individual
- **qo- é exclusivo de prosa** — nunca aparece em rótulos (Lc/Lf/Ln/Ls)
- **ok/ot tem papel dual**: standalone/inicial em rótulos (nominal), interno em prosa (morfológico)
- **f99r.30**: cadeia de 6 formas ok/ot consecutivas alternando qo-/bare — paradigma morfológico, não lista de objetos

## 70. Modelo estrutural emergente (síntese das Rotas 43–47)

O sufixo das formas `ok/ot` codifica três camadas **ortogonais**:

```
[qo-] + operador(ok/ot) + VOGAL(a/o) + CONSOANTE(r/l) [+ sufixo_de_fechamento(-y/-dy/-aiin)]
```

| Camada | Elemento | Preditor | Função |
|--------|----------|----------|--------|
| Registro | `qo-` prefixo | locus_kind (P/L) | qo-=prosa; ausente=rótulo ou prosa curta |
| Clase | `ok-` vs `ot-` | locus+Currier (V≈0.11) | distinção de tipo de entrada (~50/50 nos dois dialetos) |
| **Dialeto** | **vogal a/o** | **Currier (V=0.45)** | **A=vogal-o; B=vogal-a (p≪1e-6)** |
| **Sintaxe** | **consoante r/l** | **posição na linha** | **-l=fechamento/terminal; -r=continuação** |

**Interpretação consolidada:**

> O Voynichese usa um sistema de notação em camadas onde o operador (ok/ot) marca a CLASSE do item e o sufixo composto (vogal+consoante) combina um **parâmetro de escriba** (quem escreve) com um **parâmetro posicional** (onde está na frase). O prefixo qo- marca o registro discursivo. Nenhum dos quatro elementos é uma tradução semântica direta — são marcadores funcionais de um sistema formal.

### Rota 48 — próximo ataque

Testar se o bit a/o é uma regra **ortográfica do sistema** (o mesmo escriba usa sempre a mesma vogal) ou um hábito **motor individual** (variação intra-mão):

- 48-A: V(mão × ao) dentro de Currier B (mãos H1–H5 se disponíveis)
- 48-B: stationariedade do bit a/o ao longo de um fólio (teste de runs)
- 48-C: generalização além de ok/ot — o padrão vale para outras famílias?

## 71. Rotas 48–50: ok/ot confirmado; modelo de 4 camadas completo

**Rota 48**: bit a/o é regra ortográfica do SISTEMA (V entre mãos B = 0.13), estacionário dentro de fólios (todos p>0.22), e generaliza para TODAS as 11 famílias testadas (ch, d, sh, qok, yk, yt…). ok vs ot: V(Currier×ok/ot)=0.11, V(locus×ok/ot)=0.06.

**Rota 49**: ok/ot é nulo limpo em grafotaxia (V(ok/ot × r/l)=0.05, p=0.20), contexto anterior (cosine p=0.50), e 20 pares mínimos co-ocorrem livremente → NOT complementaridade.

**Rota 50** usou subtipos finos de locus (Ls, Lf, L0, Pb, Lt) e encontrou o maior V para ok/ot: **V=0.1290**. Padrão consistente:

| Subtipo | ok% | ot% | ot/ok |
|---------|-----|-----|-------|
| Pb (blocked) | 77% | 22% | **0.29** |
| L0 (ring flow) | 64% | 35% | 0.55 |
| P0 (paragraph) | 51% | 48% | 0.93 |
| Lf (label) | 38% | 61% | 1.62 |
| Ls (symbol label) | 38% | 61% | 1.60 |
| Lt | 14% | 85% | **6.0** |

**Hipótese visual confirmada em f67r2**: ot- (otar, ytokar, otolor) estão TODOS nos labels de luas (Ls); ok- estão TODOS em texto-fluxo (L0, Pb, P0). Separação perfeita no fólio mais estruturado.

> ok = modo de texto/discurso (fluxo); ot = modo de rótulo/nomeação (figura isolada)

É **preferência suave**, não regra categórica — P0 está 50/50. Mas o sinal direcional é consistente em todos os subtipos.

### Modelo estrutural final (Rotas 43–50)

```
[qo-] + OPERADOR(ok=fluxo/ot=label) + VOGAL(a=B/o=A) + CONSOANTE(l=fecha/r=continua) [+-y/-dy/-aiin]
```

| Camada | Elemento | Preditor | Efeito | Força |
|--------|----------|----------|--------|-------|
| Registro | qo- | locus P vs L | qo-=prosa; ausente=rótulo/prosa curta | forte |
| **Operador** | ok vs ot | locus_subtype | ok=fluxo; ot=label (preferência suave) | fraco (V=0.13) |
| **Dialeto** | vogal a/o | Currier | A=vogal-o; B=vogal-a | forte (V=0.45) |
| **Sintaxe** | consoante r/l | posição na linha | -l=fechamento; -r=continuação | moderado (Rota 43) |

Todos os 4 elementos identificados. Nenhum é semântica direta.

Saídas: `docs/research/rota_50_ok_ot_registro.md`.

### Rota 51 — próxima frente

- R51-A: Bootstrap dos subtipos Ls e Lf para IC 95% do efeito ok/ot
- R51-B: Markov serial k/t dentro de linhas (runs test de k→k vs k→t)
- R51-C: yt- como variante de ot- (mesmo perfil de subtipos?)

## 72. Rotas 52–53: o NÚCLEO ch/sh segue CONTEÚDO — primeiro candidato lexical

A Rota 51 (mais bootstrap de ok/ot) foi **despriorizada**: o operador já estava
mapeado como o elemento mais fraco do modelo (V≤0.13), e atacar o NÚCLEO abriu uma
frente muito mais promissora. Toda a CASCA do token (qo- + ok/ot + a/o + r/l) provou
ser marcação funcional não-lexical. Faltava o miolo: o banco **ch vs sh**.

**Pergunta falsificável:** a escolha ch/sh é prevista pelo ESCRIBA (Currier) ou pelo
CONTEÚDO (seção)? Teste-de-tornassol prescrito pelo cryptanalyst:
- Currier > seção → convenção de mão → conteúdo não está no núcleo
- seção > Currier → **primeiro candidato a carga lexical**

**Rota 52** (descoberta, subconjunto de 786 formas exatas): V(seção)=0.1294 >
V(Currier)=0.0861. Sinal aponta para conteúdo. Doc: `docs/research/rota_52_nucleo_ch_sh.md`.

**Rota 53** (confirmação em TODO o corpus + controle de confundidor): novo script
`scripts/analyze_nucleus.py` lê o ZL3b cru, mapeia Currier por `$L=` e seção por
fólio, e classifica cada token com ch XOR sh (14 594 tokens). Resultado **mais forte**:

| Preditor de ch/sh | V de Cramér | n |
|-------------------|-------------|---|
| **Seção (conteúdo)** | **0.1415** | 14 594 |
| Currier (escriba) | 0.0619 | 13 574 |
| **Seção \| Currier=B** | **0.1571** | 8 738 |
| Seção \| Currier=A | 0.0480 | 4 836 |

Permutação (500 embaralhamentos): **p ≈ 0.002**. O sinal de seção **sobrevive ao
controle** dentro de um único escriba (B): não é artefato da correlação seção↔Currier.

**ch/sh por seção (corpus completo):**

| seção | n | %ch | %sh |
|-------|---|-----|-----|
| herbal | 4 874 | 74% | 25% |
| recipes | 4 184 | 74% | 25% |
| **balneológico** | **2 520** | **57%** | **42%** |
| pharmaceutical | 1 333 | 70% | 29% |
| astronômico | 987 | 76% | 23% |
| cosmológico | 696 | 66% | 33% |

**Achados:**
1. O **balneológico** (ninfas/água/corpo) é a seção mais carregada de **sh** (42% vs
   ~25% de base); herbal/astronômico (plantas/estrelas) pendem para **ch**. (Nota: o
   perfil de "receitas" do subconjunto-786 da Rota 52 NÃO se confirma no corpus pleno —
   era artefato do subconjunto ok/ot; o sinal robusto é o balneológico.)
2. **Assimetria A/B decisiva**: o sinal de seção vive em B (V=0.157) e some em A
   (V=0.048). A é quase só herbal — sem variância de conteúdo para mostrar. Se ch/sh
   fosse hábito motor do escriba, A e B teriam o mesmo perfil dentro de cada seção;
   o efeito é de **conteúdo**, não de mão.

> **O núcleo ch/sh é o PRIMEIRO elemento do token que responde ao conteúdo do
> manuscrito, não ao escriba.** É o primeiro candidato a carga lexical do projeto.

**Ressalvas:** V≈0.14 é efeito moderado — é estrutura de conteúdo, não um lexema
isolado. "Segue conteúdo" ≠ "tem semântica conhecida": continua sendo estrutura, não
tradução. Banco-gallows (cth/ckh/cph/cfh) ficam fora do teste binário por construção.

Guardrails: `rota52_core_glyph_signal_not_decipherment`,
`rota53_nucleus_content_signal_not_decipherment`.
Saídas: `scripts/analyze_nucleus.py`, `tests/test_nucleus.py` (8 testes),
`data/derived/nucleus_chsh_{context,by_section,summary}_zl3b.csv`,
`docs/research/rota_53_nucleo_controle_currier.md`.

### Modelo estrutural atualizado (Rotas 43–53)

```
[qo-] + OPERADOR(ok/ot) + [ NÚCLEO(ch/sh ← CONTEÚDO) ] + VOGAL(a/o ← escriba) + CONSOANTE(r/l ← posição)
```

| Camada | Elemento | Preditor | Segue | Força |
|--------|----------|----------|-------|-------|
| Registro | qo- | locus P vs L | discurso | forte |
| Operador | ok/ot | locus_subtype | registro (fluxo/label) | fraco (V=0.13) |
| **Núcleo** | **ch/sh** | **seção** | **CONTEÚDO** | **moderado (V=0.14, p≈0.002)** |
| Dialeto | vogal a/o | Currier | escriba | forte (V=0.45) |
| Sintaxe | consoante r/l | posição na linha | posição | moderado |

**Primeira separação clara CONTEÚDO vs FORMA no token.** Quatro camadas são marcação
funcional (quem/onde/registro); o núcleo é a única que varia com o ASSUNTO.

## 73. Rota 54: estresse do sinal ch/sh — refina e TEMPERA a Rota 53

Três ataques falsificáveis ao sinal de conteúdo, com o **cryptanalyst pré-registrando
predições CEGO aos números** (antes de o statistician rodar). Script:
`scripts/analyze_nucleus_context.py`; testes: `tests/test_nucleus_context.py`
(suíte total 343). Reproduz o total da Rota 53 (n=14 594).

| Sub-ataque | Predição (cega) | Resultado | Veredito |
|------------|-----------------|-----------|----------|
| **A** rótulo vs texto | sh nos rótulos (ninfas) | sh%(L)=33%, n=24 < sh%(P)=42.5%; V=0.018, p=0.42 | **refutado/nulo** |
| **B** núcleo ⟂ operador | independência (V≈0) | V=0.1145, p=0.002; em B V=0.099 | **refuta parcial** |
| **C** ambiente ch vs sh | mesmo conjunto sucessor | top-3 igual (e,o,y), ΔH=0.38 bits | **misto** |

**R54-A:** o excesso de sh do balneológico vive na PROSA (texto P, 42.5% sh), não nos
rótulos de ninfa (L, n=24, 33% sh). Refuta "ch/sh nomeia referente"; rebaixa o sinal de
conteúdo de nível-rótulo para **frequência topical no texto corrido**.

**R54-B:** ok/ot-tokens preferem fortemente ch (sh: ok=18%, ot=14%), tokens SEM operador
são 31% sh. V(operador×ch/sh)=0.11, p=0.002, **sobrevive em Currier B** (V=0.099). O
modelo previa ortogonalidade; há **acoplamento fraco mas real** — o vocabulário sh é
majoritariamente o vocabulário sem operador. As camadas núcleo e operador **interagem**.

**R54-C:** H(próximo|ch)=2.32 bits, H(próximo|sh)=1.94 bits. O **inventário de sucessores
é idêntico** (e,o,y,d,a,c — mesma ordem), mas sh é mais concentrado em `-e` (ΔH=0.38).
Não são variantes livres: **ch e sh são dois valores de um único slot**, sobre gramática
compartilhada.

**Síntese — modelo refinado:** ch/sh segue sendo o melhor sinal de conteúdo, mas a
história de "camada lexical ortogonal" da Rota 53 não se sustenta limpa:
1. a correlação com seção é frequência topical na PROSA, não nomeação;
2. o núcleo **interage** com o operador (não ortogonal);
3. ch/sh são dois valores de um slot (gramática comum), não variantes livres.

> Descrição corrente: ch/sh é uma distinção **sublexical** (1 slot, 2 valores) cuja
> frequência é condicionada por DUAS forças — operador (ok/ot→ch) e tópico (prosa
> balneológica→sh). Estrutura integrada e enviesada por tópico, **não** marcador
> semântico isolado. O harness (pré-registro cego) foi decisivo: produziu números que
> COMPLICAM o achado em vez de confirmá-lo — mais confiável que um passe único.

Guardrail: `rota54_nucleus_context_not_decipherment`. Doc: `docs/research/rota_54_nucleo_contexto.md`.
Saídas: `data/derived/nucleus_{context_balneo,operator,next_glyph,context_summary}_zl3b.csv`.

## 74. Rota 55: teste de par mínimo — ch/sh é LÉXICO, não conteúdo (fecha o fio R52–R53)

**Teste decisivo.** Esqueleto = token com o banco trocado por `#` (`chol`/`shol`→`#ol`).
Par mínimo = esqueleto que ocorre com ch E sh. Dentro de um esqueleto fixo todo vizinho
in-token é constante; só SEÇÃO, TOKEN ANTERIOR e POSIÇÃO podem variar. Mede-se
`I(banco ; X | esqueleto)` (informação mútua condicional, bits).

**ADEQUADAMENTE DIMENSIONADO:** 570 esqueletos de par mínimo, 10 855 tokens (74% de todos
os 14 594 ch/sh). Pares mínimos são abundantes.

| X (dado o esqueleto) | I (bits) | p perm |
|----------------------|----------|--------|
| Seção | 0.124 | **1.0** |
| Char anterior | 0.141 | **1.0** |
| Posição na linha | 0.054 | — |

**Veredito: `lexically_fixed`.** p=1.0 não é bug: seção é colinear com esqueleto, então
condicionar na palavra já absorve a info de seção; o resíduo é puro viés de amostra finita
(o shuffle atinge I≥observado em 100%). Teste sintético confirma que a métrica discrimina
(quando seção determina o banco, I=H(banco|esq) e p<0.05).

**Evidência descritiva independente:** nos pares mínimos do topo, forma-ch e forma-sh do
MESMO esqueleto vivem na MESMA seção (~74%): `#ol` chol/shol ambos herbal; `#edy` ambos
balneológico; `#or` ambos herbal. **O banco não move a seção.**

> **ch/sh é propriedade da PALAVRA (léxico), não marcador de conteúdo produtivo nem
> alografia.** A correlação de seção da Rota 53 é **frequência de vocabulário topical**
> (seções usam palavras diferentes, cada palavra com sua tendência ch/sh) — efeito
> ENTRE-palavras, não DENTRO-da-palavra. Reconcilia R53 (segue seção, mas por vocabulário),
> R54 (prosa não rótulo; acopla operador — ambos lexicais) e R55 (nada externo governa o banco).

**Implicação estratégica:** o fio "ch/sh = primeira camada de conteúdo" das R52–53 **NÃO
sobrevive ao teste decisivo**. Todo o token (casca + núcleo) é marcação funcional/lexical;
**nenhuma camada de conteúdo produtivo foi identificada DENTRO do token.** A pergunta vira:
onde está o conteúdo, se está? — no nível da PALAVRA INTEIRA, não do token. Resultado
negativo valioso (pré-registro cego do harness bateu com o prior do cryptanalyst).

Guardrail: `rota55_minpair_not_decipherment`. Doc: `docs/research/rota_55_minpair.md`.
Script: `scripts/analyze_nucleus_minpair.py`; testes: `tests/test_nucleus_minpair.py`
(suíte total **356**). Saídas: `data/derived/nucleus_minpair_{skeletons,summary}_zl3b.csv`.

## 75. Rota 56: o conteúdo topical vive na PALAVRA INTEIRA — 1º sinal positivo (fraco)

**Virada.** R43–55 provaram que o TOKEN é todo funcional/lexical (nenhuma camada de
conteúdo dentro dele). Então o conteúdo, se existe, tem de estar no nível da PALAVRA.
Mede-se `I(seção ; palavra)` em bits, corrigido por viés contra nulo de permutação.
Cryptanalyst pré-registrou cego (prior em (b) escriba 50%, (c) sem-sinal 30%, (a) topical 20%).

| Teste (within Currier B) | I_norm |
|--------------------------|--------|
| (i) bruto, perm por token | 0.096 |
| (ii) só prosa (locus P) | 0.095 |
| (iii) nulo por bloco de fólio | 0.069 |
| **(iv) ESTRITO: prosa + bloco de fólio** | **0.046 (z≈5.6)** |

- Agrupado: H(seção)=2.335 bits; I_obs=0.896 vs nulo 0.588, p=0.002, I_norm=0.132.
- **Sobrevive a TODOS os controles** (Currier B, locus-tipo, autocorrelação de fólio) mas
  **atENUA à metade**: o nulo por bloco de fólio fica ~4× mais largo e absorve ~metade do
  efeito. Resíduo estrito I_norm=0.046, z≈5.6 — pequeno mas robusto.
- Locus-tipo NÃO infla (só-prosa ≈ bruto); ~metade do efeito bruto era autocorrelação de
  fólio; o grosso da associação agrupada é dialeto A/B.
- Marcadores qo-/ok-/ot- mais planos (0.208) que não-marcadores (0.230) — direção funcional.
- Vocabulário diagnóstico estável sob restrição a prosa (mesma composição): herbal→kchy,
  tchy, cthor, dchor, cthy; balneológico→olkedy, olkain, qol, olshedy, olchedy.

**Veredito controlado: `topical_vocabulary`.** PRIMEIRO sinal positivo de conteúdo do
projeto: a escolha da palavra é fracamente condicionada pelo tópico além do escriba, da
estrutura de locus e da autocorrelação. Vive onde a dissecção do token previu (R43–55).

**Ressalvas:** efeito PEQUENO (4.6% de H(seção), estrito) — não prova semântica conhecida,
só que a escolha de palavra é fracamente topical. Compatível tanto com língua real de
léxico fraco quanto com baixo-conteúdo levemente enviesado. A Rota 57 decide.

> O prior (b)/(c) do cryptanalyst estava parcialmente certo: muito do efeito bruto era
> escriba/confundidor. O harness (pré-registro + controles flagueados cego) evitou
> proclamar um "achado de conteúdo" inflado — o sinal real é 1/3 do título bruto.

Guardrail: `rota56_word_content_not_decipherment`. Doc: `docs/research/rota_56_word_content.md`.
Script: `scripts/analyze_word_content.py`; testes: `tests/test_word_content.py` (suíte **377**).
Saídas: `data/derived/word_section_{diagnostic,summary}_zl3b.csv`.

## 76. Rota 57: a topicalidade da palavra é PROSA, não nome — texto e imagem desacoplados

A R56 achou sinal topical fraco na palavra, vivendo em loci de PROSA. A R57 decide o que é:
as palavras diagnósticas NOMEIAM objetos desenhados (referencial) ou são vocabulário de
prosa que varia por tópico (registro)? Três legs do harness — convergem. Pré-registro cego
do cryptanalyst: PROSE_REGISTER 0.72, REFERENTIAL 0.08 (já declarado "clinicamente morto").

**Leg 1 (estatística, corpus inteiro):** 75 palavras diagnósticas vs 205 baseline.
- label_frac diagnóstico = 0.0264 ≈ baseline do corpus 0.0273 (NÃO elevado, razão 0.97×).
- **0 palavras dominadas-por-rótulo; 0 concentradas-em-fólio.** folio_entropy 0.96 (espalhadas).
- Veredito: **`prose_register`**. (Ressalva: marginalmente mais rotuladoras que palavras
  ultra-comuns, perm p=0.026, mas 97% não-rótulo — referencial fraco quase-morto.)

**Leg 2 (visual-annotator, imagens IIIF):** onde o sinal R56 vive (prosa de herbal/balneo),
o layout é PROSA (f1r=100% prosa). Rótulo-em-objeto existe em farmacêutico (f99r 84% rótulo)
e astronômico — seções que NÃO são onde o sinal está. Das diagnósticas, só `kchy` aparece em
rótulo, e num rótulo ASTRONÔMICO, não numa planta. Cobertura honesta: só 1 fólio herbal + 1
balneológico no set IIIF (cadeia R32 astro) → leg 2 é sugestivo; o leg 1 é a evidência forte.

**Conclusão — texto e imagem desacoplados no nível da palavra:** a topicalidade fraca da R56
é **variação de registro de prosa**, NÃO nomenclatura que aponta para os desenhos. As
palavras que distinguem o herbal não nomeiam as plantas. **Descarta o modelo de
nomenclator/diagrama-rotulado** para o grosso do texto. Resta o dilema afiado: língua de
prosa real (sobre tópicos) vs sistema de baixo-conteúdo com deriva topical — a R58 decide.

Guardrail: `rota57_word_grounding_not_decipherment`. Doc: `docs/research/rota_57_grounding.md`.
Script: `scripts/analyze_word_grounding.py`; testes: `tests/test_word_grounding.py` (suíte **393**).
Saídas: `data/derived/word_grounding_{,summary_}zl3b.csv`.

## 77. Rota 58: Voynichês NÃO é prosa de língua natural — mas não é "sem sentido"

A rota decisiva. 3 legs do harness (statistician + cryptanalyst pré-registro cego +
paleographer contra-interpretação). Mede 3 assinaturas estruturais clássicas vs baselines
de língua natural (literatura).

| Assinatura | Voynich | Âncora natural | Anômalo |
|------------|---------|----------------|---------|
| **h2 caractere** | **2.15 bits** | inglês 3.1–3.6; latim 2.5–3.0 | **SIM (decisivo)** |
| h2 palavra | 4.36 (H1=10.44) | gap grande = templático | leans templático |
| LAAFU I(palavra;posição) | 0.471, p=0.003 (1.94× nulo) | ≈0 | borderline |
| Repetição adjacente | 0.875% (2.77× i.i.d.) | <0.25% prosa | ~3.5× prosa |

Validação interna: h2 embaralhado = 3.87 = h1 (cálculo correto). Borda de linha por GLIFO,
inequívoca: inicial `p` 6.25×, `t` 3.48×; final `g` 6.23×, `m` 5.86× — os gallows iniciais
são a convenção decorativa documentada do manuscrito. Repetições: `chol`×21, `qokeedy`×18.

**Veredito mecânico `mixed` (1/3); leitura honesta:** as TRÊS assinaturas apontam para longe
da prosa natural (h2 decisivamente baixo, repetição ~3.5× prosa, borda-de-linha dramática),
mas os efeitos de LAAFU/repetição são moderados — não grita "ruído aleatório". **Voynichês
NÃO é prosa de língua natural.**

**CAVEAT crítico (cryptanalyst):** h2-baixo + LAAFU + repetição são produzidos TAMBÉM por
codificações reais (cifra verbosa, latim abreviado, notação tabular/numérica). Baixo-conteúdo
≠ sem sentido. A COMBINAÇÃO afasta de cifra-de-substituição-de-prosa-limpa e estreita para
codificação-acoplada-a-layout OU gerador. **Deflação paleográfica:** borda-de-linha é
convenção escribal (não significado); abreviação explica h2 baixo mas NÃO `daiin daiin daiin`;
o códice físico sério argumenta contra fraude casual.

**Veredito integrado:** Voynichês é **altamente estruturado mas decisivamente ≠ prosa
natural**. Constrange sem decidir: descarta prosa natural simples E ruído puro; sobrevivem
(a) língua real pesadamente codificada, (b) língua construída, (c) gerador baixo-conteúdo.
Prior cryptanalyst: real-codificada 0.30 / baixo-conteúdo 0.30 / **híbrido 0.40** (camada
gerativa de layout + camada fina de conteúdo real — casa com o sinal topical fraco da R56).
Paleographer: mais parcimonioso = sistema construído OU notação não-linguística com sentido.

Guardrail: `rota58_language_signature_not_decipherment`. Doc: `docs/research/rota_58_language_signature.md`.
Script/testes: `analyze_language_signature.py` / `test_language_signature.py` (suíte **410**).
Saídas: `data/derived/language_signature_{summary,lineedge,repeats}_zl3b.csv`.

## 78. Rota 59: morfologicamente RICO, sintaticamente FINO — correlação de longo alcance

O separador único. 2 legs (statistician + cryptanalyst cego). MI de caractere I(d), d=1…150,
nulo por embaralhamento (piso ínfimo 0.0018 bits) + controle de embaralhamento-de-LINHA.

| d | excess I(d) |
|---|-------------|
| 1 | **1.717** |
| 10 | 0.019 |
| **15** | 0.0055 (≈piso → **compr. de correlação = 15**) |
| 50 | 0.0019 |
| 100 | 0.0007 |

**Dois regimes:** (1) queda local íngreme d=1→15 (lei de potência γ=1.16 R²=0.76 vence exp
R²=0.35, mas pela dominância de d=1; compr. de correlação curto=15 → veredito mecânico
`ambiguous`); (2) cauda fraquíssima. **Controle de embaralhamento-de-linha (decisivo):** o
regime local (d<10) é INTRA-linha (real≈embaralhado = morfologia da palavra); a cauda longa
(d>15, ratio_d50=17.85) é CROSS-linha e MORRE sob embaralhamento → é tópico/documento (=
vocabulário R56), NÃO sintaxe. Zipf −1.079 (tipo-língua); Heaps β=0.786 (alto = vocabulário
muito produtivo, bate com morfologia rígida).

**Leitura integrada — o achado mais coerente do projeto:**
> Voynichês é **morfologicamente RICO** (dependência intra-token forte, I=1.72 em d=1, decai
> a ~15 caracteres = escala do token = a gramática qo-+ok/ot+ch/sh+vogal+cons das R43–55, a
> fonte do h2 baixo) e **sintaticamente FINO** (sem dependência de médio alcance d≈20–100 que
> a prosa natural possui; só uma cauda de tópico fraca e cross-linha).

**Descarta:** prosa de língua natural rica (compr. correlação curto demais; nuance vs
Lin&Tegmark — o embaralhamento-de-linha revela que a cauda longa é documento/tópico, não
sequencial). **Desfavorece** Markov local simples (fraco — a cauda de tópico existe). **Mais
consistente com:** formação rígida de palavra + deriva fraca de vocabulário por tópico, SEM
sintaxe de sentença → construído/codificado/gerador templático com camada fina de conteúdo
(hipótese híbrida).

Guardrail: `rota59_long_range_not_decipherment`. Doc: `docs/research/rota_59_long_range.md`.
Script/testes: `analyze_long_range.py` / `test_long_range.py` (suíte **430**).
Saídas: `data/derived/long_range_{mi,summary}_zl3b.csv`.

## 79. Rota 60: Voynichês comprime como seu PRÓPRIO saco-de-palavras — textura, não sintaxe

Teste final. 2 legs (statistician + cryptanalyst cego). Escada de compressão (lzma/bz2):

| stream | lzma bpc | preserva |
|--------|----------|----------|
| markov2_char | 2.45 | trigrama de char |
| **word_unigram (saco-de-palavras)** | **2.39** | identidade de palavra, ORDEM destruída |
| **real** | **2.31** | tudo |

- gain_over_markov2 = 0.055 (estrutura além de trigramas).
- **gain_over_wordunigram = 0.034 (lzma) / 0.008 (bz2)** — ordem-de-palavra. Faca de gume:
  compressores discordam. Decomposição: IDENTIDADE-de-palavra (0.061 bpc) ~4× a ORDEM (0.015).
- Âncora natural (cryptanalyst): prosa real perde 12–25% ao embaralhar palavras; Voynich ~1–3%,
  ~10× mais fraco. Predição cega (~2%, dominado por identidade) acertou.

**Veredito integrado: Voynichês comprime essencialmente como seu próprio saco-de-palavras.**
A ordem das palavras carrega no máximo um traço — confirma "sintaticamente fino" (R59) por
método independente. A compressibilidade vem da MORFOLOGIA, não de sintaxe. (Veredito mecânico
`word_order_informative` é artefato de limiar — lzma mal cruzou 0.03, bz2 não.)

**Caveat:** "fino na escala do token" ≠ sem sentido. Sobrevive **cifra verbosa** (1 palavra→n
tokens; sintaxe abaixo do token, invisível ao embaralhamento). A escada não separa
cifra-verbosa-com-sentido de gerador.

---

### SÍNTESE CUMULATIVA — linha R43–60 (essencialmente fechada)

> **Voynichês é um sistema de tokens morfologicamente RICO e sintaticamente FINO:** processo
> gerativo restrito (operadores templáticos qo-/ok-/ot- + bordas de matriz) com camada fraca
> de tópico de prosa, TEXTO desacoplado das IMAGENS.

**Robustamente EXCLUÍDO:** substituição simples; prosa de língua natural direta; ruído puro;
nomenclator. **NÃO distinguido:** cifra-verbosa-com-sentido vs gerador-de-baixo-conteúdo
(ambos finos na escala do token). "É prosa de língua natural?" → **NÃO.** "Tem sentido?" →
não resolvível por estatística na escala do token. Prior: construído/gerador ~45–50%,
real-codificada(cifra-verbosa) ~30–35%, baixo-conteúdo-puro ~20%. **Nenhuma tradução afirmada
em nenhum ponto — guardrails em todas as 18 rotas.**

Guardrail: `rota60_compressibility_not_decipherment`. Doc: `docs/research/rota_60_compressibility.md`.
Script/testes: `analyze_compressibility.py` / `test_compressibility.py` (suíte **442**).

## 80. Rota 61: re-segmentação NÃO revela sintaxe escondida — linha R43–61 FECHADA

A última falsificação. A única hipótese "com sentido" sobrevivente era a cifra verbosa
(1 palavra→n tokens, sintaxe abaixo do token). Teste: BPE re-segmenta o fluxo de char, mede
ganho de ordem nas novas unidades, **diferencialmente** vs substitutos (Markov-2, saco-de-
palavras). 2 legs (statistician + cryptanalyst cego).

| compressor | revival_voy | saco-de-palavras | diferencial | ratio |
|------------|-------------|------------------|-------------|-------|
| lzma | 0.083 | 0.049 | **0.035** | 1.72× |
| **bz2** | 0.074 | 0.069 | **0.005** | **1.07×** |

O ganho lzma (0.035) PARECIA estrutura escondida — mas **colapsa no bz2 (0.005)**, exatamente
o padrão da R60 (lzma 0.034→bz2 0.008): **artefato de compressor**. Veredito robusto (ambos
compressores): **`lzma_artifact` → `no_hidden_structure`**. A re-segmentação não recupera
ordem além do que a morfologia produz mecanicamente; a grade de tokens é a unidade natural; a
fineza sintática é fundamental. (cross_boundary_merge_frac=0.49 é descritivo, não evidência —
morfologia rígida; os substitutos fazem os mesmos merges cruzados.)

**O método foi o herói:** o statistician retornou `hidden_structure` pelo critério lzma-only;
o cryptanalyst pré-registrou CEGO o oposto ("a R60 me queimou; exigir bz2 também") e o
cross-check de bz2 **virou um falso positivo de sentido escondido.** Capstone da disciplina
"sempre rodar os controles flagueados".

Guardrail: `rota61_resegment_not_decipherment`. Doc: `docs/research/rota_61_resegment.md`.
Script/testes: `analyze_resegment.py` / `test_resegment.py` (suíte **466**).

---

### 🏁 VEREDITO FINAL — linha "o que é o Voynichês" (R43–61) FECHADA

> **O Voynichês é um sistema de tokens morfologicamente RICO e sintaticamente FINO, sem
> estrutura de ordem re-segmentável escondida:** processo gerativo restrito (operadores
> templáticos qo-/ok-/ot- + bordas de matriz `ar/al/or/ol`) + camada fraca de tópico de prosa,
> texto desacoplado das imagens.

- **EXCLUÍDO (robusto):** substituição simples · prosa de língua natural direta · ruído puro ·
  nomenclator · cifra verbosa com sintaxe sub-token recuperável.
- **Sobrevive sem apoio positivo (minoritário):** cifra/língua construída que não deixa
  assinatura estatística na escala observável.
- *"É prosa de língua natural?"* → **NÃO** (decisivo). *"Tem sentido proposicional?"* → **não
  resolvível por estatística** (a R61 era o último instrumento). Prior: ~55% gerador, ~30%
  construída, ~15% cifra. **Nenhuma tradução afirmada em 19 rotas — guardrail em tudo.**

### Próximo passo recomendado — CONSOLIDAR

Ambos especialistas endossam: a linha está fechada à resolução dos dados; mais falsificação na
escala do token rende pouco. Próximo de maior valor: **consolidar R43–61 num relatório
coerente** (a incerteza restante é proveniência/chave, não estatística).

## 81. Relatório consolidado (R43–61) — ENTREGUE

A linha investigativa foi consolidada num relatório único e coerente, montado pelo time
(coordenador escreve a espinha; cryptanalyst e paleographer redigem suas seções de domínio):
**`docs/summaries/relatorio_R43_R61_natureza_do_voyniches.md`**. Seções: (1) sumário
executivo, (2) modelo estrutural em 3 níveis, (3) ledger de falsificação de 11 hipóteses,
(4) contexto físico do manuscrito [paleographer], (5) espaço de hipóteses + priores finais
[cryptanalyst], (6) metodologia (pré-registro cego + os falsos positivos pegos), (7) a
fronteira "estatística não decide sentido", (8) trabalho futuro, (9) índice de rotas. É o
artefato de fechamento da pergunta "o que é o Voynichês".

## 82. Rota 62 (capstone): gerador local sem conteúdo reproduz QUASE tudo

Teste de adequação de modelo (item nº 1 do trabalho futuro). Um gerador LOCAL e SEM CONTEÚDO
(bag-of-real-words + tabela de vocabulário por seção + auto-citação p_rep=0.0046 + viés de
borda-de-linha) foi medido contra a bateria completa:

| métrica | real | gerador | casa? |
|---------|------|---------|-------|
| h2 caractere | 2.153 | 2.227 | ✅ |
| repetição adjacente | 0.875% | 0.873% | ✅ |
| **LAAFU I(palavra;posição)** | **0.471** | **0.303** | **❌** |
| compr. correlação I(d) | 15 | 12 | ✅ |
| Zipf / Heaps | −1.08 / 0.79 | −0.99 / 0.74 | ✅ |
| gain_over_wordunigram | 0.034 | 0.008 | ✅ |

**13/14 casam (6/7 principais); só o LAAFU resiste** (o corpus liga tokens ESPECÍFICOS à
posição de linha mais que um viés de glifo — uma regra de layout mais rica, ainda
não-semântica). Veredito `generator_insufficient`, mas por uma só assinatura.

**Leitura:** **sentido NÃO é NECESSÁRIO para explicar as estatísticas** (prova de existência,
não de unicidade; ≠ texto sem sentido). Priores: gerador ~55%→**~70%**, construída ~22%,
cifra ~8%. **A linha estatística está EXAURIDA** — qualquer teste na escala do token é
degenerado (não separa "sem conteúdo" de "conteúdo invisível a estes testes"). A incerteza
restante é proveniência/material. Ambos especialistas: PARAR a linha estatística aqui.

Guardrail: `rota62_generator_not_decipherment`. Doc: `docs/research/rota_62_generator.md`.
Script/testes: `analyze_generator.py` / `test_generator.py` (suíte **479**). Relatório
consolidado atualizado com o capstone R62.

## 83. Rota 63 (FRENTE VISUAL): os rótulos também são desacoplados da imagem (piloto)

Pivô de domínio para as imagens. A R57 mostrou desacoplamento texto↔imagem no nível da
PALAVRA; a R63 testa o regime de RÓTULO (tokens curtos sobre objetos desenhados, onde a
nomeação seria mais provável). Pipeline do harness: visual-annotator leu 6 fólios IIIF
(farmacêuticos f88v/f89r2/f99r/f99v + astro f67r2/f67v1) e codificou **59 elementos** (tipo
visual do objeto, independente do token, + token-rótulo da transcrição; 46% incertos);
cryptanalyst pré-registrou cego (prior 65% B); statistician testou V(feature×objeto) com nulo.

**Confundidor crítico (pré-registrado):** tipo-de-objeto ≈ determinado pelo fólio → V global
re-mede vocabulário de seção. Sinal real precisa sobreviver ao embaralhamento **DENTRO do
fólio** (análogo ao controle de Currier).

**Resultado:** nenhuma feature (prefix4, first_glyph, gallows, length, nucleus) bate o nulo
dentro-do-fólio (nem nas 59 linhas, nem nas 32 não-incertas). Contraste mais limpo (jarro vs
órgão dentro do farmacêutico, n=39): gallows V=0.42 mas **p_within_folio=0.10** — não
sobrevive. Sinais globais modestos = confundidores de fólio, como pré-registrado. **Veredito
`decoupled_pilot`:** rótulos também desacoplados do tipo de objeto, estendendo a R57 ao regime
de rótulo. **Ressalva: PILOTO subpotente** (n=59, 46% incerto) — nulo não prova B, só falha em
achar A. Firma levemente o prior geral (texto não descreve as imagens; gerador ~70%).

**Próximo passo:** baixar mais fólios IIIF rotulados (farmacêuticos/herbais) para sair do
nível-piloto e repetir com n adequado + controle dentro-do-fólio.

Guardrail: `rota63_cross_modal_not_decipherment`. Doc: `docs/research/rota_63_cross_modal.md`.
Script/testes: `analyze_cross_modal.py` / `test_cross_modal.py` (suíte **506**). Anotação:
`data/derived/rota63_cross_modal_labels_zl3b.csv` (59 elementos cross-modais).

## 84. Rota 64: cobertura ampliada (n=171) — desacoplamento HOLDS com potência

Ampliei a cobertura: baixei **12 novos fólios IIIF** de alta-res da Beinecke (rede OK; manifesto
cached `yale_iiif_manifest_2002046.json`) → `images/raw/yale_iiif_r64/`. Correção honesta: só 7
carregam rótulos (f93–96 são herbais de parágrafo). visual-annotator codificou +112 elementos
→ **combinado n=171 across 12 fólios** (~3× o piloto; 59% incertos). Re-rodei o teste
controlado-por-fólio.

- **Headline:** nenhuma feature (gallows, prefix4, length, nucleus…) sobrevive ao controle
  dentro-do-fólio nos DOIS subconjuntos (melhor gallows p_within=0.054, quase). Os V globais
  grandes (gallows p_global=0.0003) **colapsam sob o controle** → confirmados como artefatos de
  vocabulário de seção/fólio, agora com potência.
- **Sub-teste A (jarro vs órgão no farmacêutico, n=74):** `length_bucket` p_within=**0.0063**
  sobrevive — rótulos de jarro nunca são curtos (assimetria de COMPRIMENTO, estrutura não nome).
- **Sub-teste B (ninfas, 2 fólios de zodíaco, n=44):** ninfas são estruturadas (is_nymph→prefix4,
  p=0.0067) MAS o perfil de rótulo **DIVERGE entre fólios** (f71r=ot/t/longo; f73r=ok/k;
  divergência p=0.0113) → **rótulo é FÓLIO-LOCAL, não nome do objeto.** Mesmo objeto, rótulos
  diferentes por fólio → o rótulo segue o escriba, não o referente.

**Veredito `decoupled` (com potência):** os rótulos NÃO nomeiam os objetos; a imagem e o texto
são sistemas desacoplados — confirmado no nível da palavra (R57) E do rótulo (R63→R64). O único
correlato cross-modal real é a assimetria de comprimento jarro-vs-órgão. Evidência positiva
limpa para o modelo escriba/gerador (até os rótulos são condicionados ao escriba). Firma
gerador ~70%. A pergunta "o texto tem sentido?" agora exige proveniência/material, não mais
correlação corpus↔imagem.

Guardrail: `rota64_cross_modal_not_decipherment`. Doc: `docs/research/rota_64_cross_modal_powered.md`.
Script/testes: `analyze_cross_modal.py` / `test_cross_modal.py` (suíte **524**). 12 fólios em
`images/raw/yale_iiif_r64/`; anotação `data/derived/rota64_cross_modal_labels_zl3b.csv` (112
elementos); saídas `data/derived/cross_modal_{test,summary}_combined_zl3b.csv`.

## 85. Rota 65: radial≠parágrafo (Perna A) + refino fortalece desacoplamento (Perna B) — frente visual FECHADA

Duas pernas em paralelo no harness; pré-registro cego do cryptanalyst para ambas.

**Perna A — texto radial/circular vs parágrafo (corpus inteiro, `locus_kind` da IVTFF).**
n_paragraph=34 259, n_radial=2 383, n_label=1 029. Distribuição de prefixo virada decisiva:
- `qo-`: paragraph **15.1%** → radial 2.3% → label 0.9% (colapsa fora da prosa)
- `ot-`: paragraph 5.2% → radial **16.0%** → label **17.2%** (triplica)
- Headline within-folio (10 fólios cosmológicos com ambas as classes): prefix V=**0.217**,
  p=**0.0005**; nucleus V=0.134, p=0.0005; length nulo. Per-fólio: prefix p<0.05 em 6/10.
- **f67r2 confirma R50:** label-vs-paragraph V=0.26, p_within=0.027 — o padrão "ot- nos
  rótulos da lua" reproduz-se em escala de corpus sob controle rigoroso.
- Veredito: **`radial_paragraph_differ`** — `locus_kind` atua como SELETOR DE REGISTRO sobre
  o mesmo inventário de operadores. Não é nova camada; firma a casca externa do modelo (R47/R50).

**Perna B — refino dos rótulos uncertain + re-teste cross-modal.** visual-annotator
re-examinou 101 linhas uncertain de R63/R64; 38 elevadas a medium, 15 medium→high, 0 uncertain
→high (honestidade). Uncertain caiu 59%→**37%**; n_não-incerto 70→**108** (+54%). Bias check
do cryptanalyst: mediana de comprimento idêntica entre elevados/mantidos → SEM viés-de-
confirmação. Sem mudanças de object_type. Limites estruturais irredutíveis documentados
(ninfas em anel; rótulos chevron f67r2; painel f89v2 ausente da imagem; multi-token).

Re-teste com controle dentro-do-fólio (3000 perms, ambos subconjuntos):
- gallows (all rows): p_within **0.0560** (R64=0.054, afasta-se de 0.05)
- gallows (não-incerto n=108): 0.0150 (mas all-rows não corrobora → regra dos dois subconjuntos bloqueia)
- pharma vessel-vs-organ (comprimento): **0.0073** (R64=0.006, sobrevive <0.01)
- nymph cross-folio divergence (f71r vs f73r): **0.0130** (R64=0.011, essencialmente igual; fólio-local)

Veredito Perna B: **`decoupled_refined`** — refino FORTALECEU o desacoplamento (cryptanalyst
pré-registrou ~55% deste cenário).

**Síntese — frente visual ENCERRADA.** Per cryptanalyst: "if Leg B (a) lands → declare visual
front CLOSED". (a) `decoupled_refined` aterrissou. Os rótulos NÃO nomeiam objetos (com potência
+ dados refinados); o texto radial usa um REGISTRO de prefixo diferente do parágrafo (não
semântica, layout-licenciado). Priores efetivamente inalterados: gerador ~70% / construída
~22% / cifra ~8%. **A pergunta "tem sentido?" agora exige proveniência/material — nem corpus,
nem imagem, nem mais cross-modal vão decidir.**

Guardrails: `rota65a_radial_paragraph_not_decipherment`, `rota65b_cross_modal_refined_not_decipherment`.
Doc: `docs/research/rota_65_radial_and_refinement.md`. Suíte: **549 testes** (524+11 Perna A +14
Perna B Round 2). Saídas: `data/derived/radial_paragraph_{distribution,test,summary}_zl3b.csv`,
`rota65b_cross_modal_refined_zl3b.csv`, `cross_modal_{test,summary}_refined_zl3b.csv`. 4 fólios
cosmológicos baixados em `images/raw/yale_iiif_r65/`.

## 86. Rota 66: matriz de ataque às teses externas — 1/13 fura o gerador

Primeira rota que vira a arma para FORA: em vez de mais um ataque interno ao corpus, o time
de harness (linguistics-coordinator + cryptanalyst + corpus-statistician + paleographer +
visual-annotator) auditou 13 teses modernas do Voynich contra o ESTADO FECHADO do repo (R43–65).

**Método — não-circular e pré-registrado.** Cada especialista emitiu, às cegas, o veredito
que sua tese mereceria ANTES de ver o resultado dos outros. O script não julga por opinião:
ele valida cada veredito contra a SAÍDA do próprio gerador R62 (o gerador local e sem conteúdo
vira o árbitro). Uma tese só "sobrevive" se prevê um sinal que o gerador content-free NÃO produz.

**Manchete — 1/13 bate o gerador.** Só **Parisel** (texto como artefato de layout/scribal)
prevê um sinal além do gerador, ancorado no único resíduo conhecido: o **LAAFU** (`laafu_I`
observado **0.471 > 0.303** do gerador). Os outros 12 são mortos ou degenerados pelo estado fechado.

**Placar (13 teses):** refutadas=6 `{1,2,3,5,10,13}` (cada uma derrubada por um instrumento
nomeado do repo); unsupported=2 `{4,6}`; survives_weakly=3 `{7,8,12}`; actionable=1 `{9}`;
external_only=1 `{11}`.

**Os 5 baldes, compactos:**
- **mortas** — 6 refutadas + as degeneradas: 12/13 não sobrevivem ao gerador.
- **degeneradas** — survives_weakly/unsupported: vivas só por ausência de instrumento, não por sinal.
- **actionable** → **Rota 67** proposta: discriminador *laafu content-vs-layout*, **pré-registrada
  como degenerada-provável** (o LAAFU deve ceder a layout, não a conteúdo).
- **external_only=11 + resíduos** — só decidível por evidência de fora do texto.
- **próximo ataque = EXTERNO**: proveniência/material; corpus, imagem e cross-modal já se esgotaram.

**Priores inalterados:** gerador ~70% / construída ~22% / cifra ~8%. O ataque externo CONFIRMA
a casca — não move a agulha de "tem sentido?"; isso agora depende de proveniência/material.

Guardrail: `rota66_external_thesis_attack_not_decipherment`. Script:
`scripts/analyze_external_thesis_attack_matrix.py`; teste:
`tests/test_external_thesis_attack_matrix.py` (11). Saídas:
`data/derived/external_thesis_attack_matrix_{,summary_}zl3b.csv` (matriz de 13 linhas). Doc:
`docs/research/rota_66_estado_da_arte_attack_matrix.md`. Suíte: **560 testes**.

## 87. Rota 67: o resíduo LAAFU é LAYOUT, não conteúdo — gerador efetivamente 14/14

Primeiro teste do único lead acionável do R66 (Parisel / tese 9): o LAAFU — o único resíduo
que o gerador content-free R62 não reproduzia (`laafu_I` observado **0.471 > 0.303**) — carrega
conteúdo ou é artefato de layout/escriba? Harness cega de 2 pernas (statistician + paleographer),
pré-registrada como **degenerada-provável** (o LAAFU deve ceder a LAYOUT, não a conteúdo).

**Controle decisivo — subtração da cabeça paleográfica.** Colapsar as identidades caligráficas
de CABEÇA (gallows littera-notabilior de início de linha `p`/`t` + justificação de fim de linha
`-m`/`-g`/`-dy`) derruba `laafu_I` de **0.471 → 0.307 ≈ baseline R62 0.303**, explicando **97.6%**
do gap. Miller–Madow debiased = **0.4395** (o sinal NÃO é inflação de amostra finita). Dentro de
Currier o efeito é real por modo: A=**0.589**, B=**0.487**.

**Veredito mecânico vs leitura.** O script classifica `laafu_mixed` (fecho difuso k70=2116;
seção borderline p=0.018 = provável confundidor de vocabulário-de-seção) — mas a LEITURA é
**LAYOUT**: o gerador R62, com um viés de aresta consciente da identidade-de-cabeça, alcança
efetivamente **14/14** assinaturas. O lead de Parisel **dobra no gerador** (o pré-registro
degenerada-provável acertou).

**Priores cutucam, não movem:** gerador ~70% / construída ~22% / cifra ~8%. Guardrail:
`rota67_laafu_layout_not_decipherment`. Script: `scripts/analyze_laafu_layout.py`; teste:
`tests/test_laafu_layout.py` (15). Saídas:
`data/derived/laafu_layout_{closure,section,summary}_zl3b.csv`. Doc:
`docs/research/rota_67_laafu_layout.md`. Suíte: **593 testes**.

## 88. Rota 68: frente externa — proveniência/material + codicologia de produção

Com a linha de corpus exaurida (R62), a visual fechada (R63–65) e o R66 congelando os priores,
só **proveniência/material** pode mover "tem sentido?". Três peças.

**(A) Dossiê de proveniência/material.** Velino ¹⁴C **1404–1438** (terminus post quem só da
PELE); tinta ferrogálica (McCrone 2009, genérica). Sólido: **assinatura erodida de Sinapius em
f1r** + carta **Marci–Kircher 1665**. Contestado: os 600 ducados de Rudolf II. A cadeia
documentada começa **~170–200 anos APÓS** o velino = vazio probatório entre fabricação e registro.

**(B) Tabela de decisão externa.** Só **#1 chave/crib** OU **#6 um decode que prevê fólios NÃO
VISTOS (held-out)** podem confirmar sentido (necessário E suficiente); na ausência deles os priores
ficam **CONGELADOS em 70/22/8**. Prioridade: **#7 mapa de cadernos/mãos (feito aqui)** > #4 estudo
de campanha de tinta > #2 monitorar texto-irmão.

**(C) Codicologia da metadata IVTFF.** Currier fortemente **BLOCADO** (26 runs vs null ~96,
**p=0.001**), V(mão×Currier)=**0.98** (quase determinístico; **5 mãos**), **12 regimes** — mas só
**5/23 trocas de Currier em costuras de caderno** → veredito **`interleaved_production`** (blocado
no geral, intercalado localmente no herbal). Ressalva honesta: produção séria é consistente com
texto COM sentido E com gerador content-free → reforça "artefato construído sério" SEM mover o
sentido.

Guardrail: `rota68_codicology_not_decipherment`. Script: `scripts/analyze_codicology.py`; teste:
`tests/test_codicology.py` (18). Saídas:
`data/derived/codicology_{currier_runs,alignment,summary}_zl3b.csv`. Doc:
`docs/research/rota_68_codicologia.md`. Suíte: **593 testes**.

## 89. Rota 69: hipóteses "estilo Leonardo" — direção/espelhamento DEGENERAM

Pergunta da internet: o Voynich seria de Leonardo da Vinci (escrita espelhada, "palavras de trás
pra frente", leitura direita→esquerda, páginas espelhadas)? **Autoria refutada pela materialidade**
(velino ¹⁴C 1404–1438; Leonardo nasceu em 1452). Mas as TÉCNICAS são testáveis independentemente de
quem segurou a pena, e a R69 as arbitrou contra o gerador R62.

**Veredito `leonardo_operations_degenerate`.** Teorema confirmado no corpus: a entropia condicional
de uma fonte estacionária é invariante por reversão → `h2_fwd − h2_bwd = −0,00002` (h2=2,153 idêntico
nas duas direções; h3=1,899 idêntico). **A direção de leitura é invisível no nível da sequência** — a
famosa h2 NÃO pode favorecer R→L (mata o argumento central do paper de direcionalidade de 2025). O
único conteúdo direcional de 2ª ordem = `dir_edge = H(1ª letra) − H(última) = +0,676` = morfologia de
sufixo (fins de palavra mais rígidos que inícios), reproduzida pelo gerador (+0,686, Δ=0,010) e que só
TROCA DE SINAL ao inverter os tokens (−0,676). Nenhum reverso aproxima h2 da banda natural [2,5–3,6]
(preso ~2,15). Páginas NÃO espelhadas (facing reverso 0,0045 < direto 0,0059, effect=−0,0014, p=0,40;
palíndromo p=0,91) — um falso positivo do nulo ingênuo (p=0,0066) foi PEGO pela pré-registração cega.
Priores inalterados 70/22/8.

Guardrail: `rota69_directionality_mirror_not_decipherment`. Script: `scripts/analyze_directionality_mirror.py`;
teste: `tests/test_directionality_mirror.py`. Saídas: `data/derived/directionality_{summary,corpora}_zl3b.csv`.
Doc: `docs/research/rota_69_direcionalidade_espelhamento.md`. Suíte: **605 testes**.

## 90. Rota 70: a tese hebraica (Kondrak & Hauer 2018) — alfagrama REFUTADO

Pergunta trazida de fora: "o Voynich é hebraico?" A afirmação tem DUAS formas e o repo só atacara
uma. As decifrações pontuais (Cheshire/Bax/Gibbs) são a **Tese 13 da R66**, mortas por `char_h2=2.15`.
A versão ALGORÍTMICA — **Kondrak & Hauer 2018** (identificação automática de língua → hebraico em 1º;
modelo: cada palavra = palavra hebraica abjad SEM VOGAIS + letras REORDENADAS em ordem alfabética, um
*alfagrama*) — nunca fora isolada. Seu mecanismo é falsificável SEM chave: um alfagrama impõe uma
**ordem TOTAL** dos glifos.

**Três medidas, duas independentes da ordem escolhida:**
- `alphagram_fraction` (tokens não-decrescentes sob a melhor ordem): real **0,273** vs teto (alfagrama
  verdadeiro) **1,0** e piso (embaralhado) **0,063** → só **22,5%** do caminho do acaso ao alfagrama.
- `pair_decidedness` (pares de glifos com ordem estrita ≥95%): **0,347** (alfagrama exige ~1,0);
  **124/190 pares são ambíguos** (e/o maioria 0,66; h/o 0,65; k/o 0,74 — coexistem nas duas ordens).
- `majority_cycles` (3-ciclos `a<b<c<a`): **15** → PROVA que nenhuma ordem total existe → o texto não
  pode ser um anagrama alfabético.

**Arbitragem R62:** o lift de ordem é reproduzido pelo gerador content-free (real 0,273 ≈ gen 0,277,
Δ=0,004) = **morfologia templática** (R49: `qo-/ok-/ot-`…`-dy/-y`), não reordenação alfabética.
**Glifo-EVA** (ch/sh como unidades) refuta igual (0,34; 19 ciclos). **Abjad** (remover `a/o/e/y`) não
resgata (decididos 0,42; ainda há ciclos). **Frequência** não-discrimina: hebraico 1,00 empata inglês
0,997 (Zipf).

**Veredito `hebrew_alphagram_refuted`** — fecha o gap da Tese 13: a forma algorítmica morre pelo PRÓPRIO
mecanismo declarado. A direção R→L (hebraico é direita→esquerda) é escopo da Rota 69 (direcionalidade,
mantida separada). Priores congelados 70/22/8.

Guardrail: `rota70_hebrew_alphagram_not_decipherment`. Script: `scripts/analyze_hebrew_alphagram.py`;
teste: `tests/test_hebrew_alphagram.py` (17). Saídas:
`data/derived/hebrew_alphagram_{summary,corpora,pairs}_zl3b.csv`. Doc:
`docs/research/rota_70_hebrew_alphagram.md`. Suíte: **622 testes**.

## 91. Rota 71: hipótese de língua construída (*lingua ignota*) — família VIVA, Hildegard ENFRAQUECIDA

Pergunta do usuário: o manuscrito poderia ser uma "lingua ignota" (língua construída)? Rota de
**SÍNTESE** — posiciona a hipótese contra o ledger fechado R43–R70, **sem medir corpus novo**
(scorecard de 10 critérios). Distingue dois sentidos:

- **H_amplo (sistema de signos construído deliberadamente):** VIVA — sustenta 5 / enfraquece 0.
  Morfologia combinatória desenhada (R43–55), saco-de-palavras sintaxe-fina (R60), prosa não-natural
  h2=2,15 (R58), morfo-rico/sintaxe-fino (R59) e produção séria multi-escriba (R68: blocado p=0,001,
  5 mãos, V(mão×Currier)=0,98) todos a sustentam. É o ramo ~22% e a família a que o gerador ~70% pertence.
- **H_Hildegard (o modelo específico: nomenclator glosado, vocabulário inventado referencial):**
  ENFRAQUECIDA — enfraquece 4 > sustenta 3. Nomenclator excluído (R57), rótulo↔objeto desacoplado
  (R63–65), sem glosa/chave paralela (R68), escala/morfologia do léxico ≠ lista de ~1000 substantivos (R59).

Nenhum dos dois é confirmável por estatística: o gerador content-free R62/R67 reproduz 14/14
assinaturas, logo um sistema construído COM conteúdo é indistinguível de um SEM na escala do token.
Só chave/crib #1 (que também separa construída de cifra) ou decode held-out #6 move o ponteiro.
Veredito `constructed_family_alive_hildegard_excluded_frozen`. Priores congelados 70/22/8.

Guardrail: `rota71_constructed_language_not_decipherment`. Script: `scripts/assess_constructed_language.py`;
teste: `tests/test_constructed_language.py`. Saídas: `data/derived/constructed_language_{scorecard,summary}_zl3b.csv`.
Doc: `docs/research/rota_71_lingua_construida.md`. Suíte: **636 testes**.
