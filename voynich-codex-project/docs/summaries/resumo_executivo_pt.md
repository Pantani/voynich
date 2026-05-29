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

Esse passo agora começou em `docs/estudo_matriz_bordas_contexto.md`, com uma primeira tabela contextual sobre os trechos `f67r2` e `f68r3`.

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

A Rota 1 ampliou o corpus textual usando `data/raw/ZL3b-n.txt`, transcrição Zandbergen-Landini em IVTFF/EVA.

Saídas:

- `data/derived/border_matrix_context_zl3b.csv`;
- `docs/estudo_matriz_bordas_contexto_zl3b.md`;
- `docs/rota_1_corpus_textual.md`.

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

A Rota 2 executou controles estatísticos sobre `data/derived/border_matrix_context_zl3b.csv`.

Saídas:

- `docs/rota_2_controles_estatisticos.md`;
- `data/derived/matrix_control_summary_zl3b.csv`;
- `data/derived/matrix_exact_pairs_zl3b.csv`.

Resultado:

- locus x sufixo: chi2=153,340; Cramer's V=0,0780; embaralhamento p<=0,0020;
- prefixo x sufixo: chi2=712,684; Cramer's V=0,1682; embaralhamento p<=0,0020;
- posição x sufixo: chi2=240,746; Cramer's V=0,0978; embaralhamento p<=0,0020;
- locus x sufixo controlando prefixo: chi2=93,418; Cramer's V=0,0609.

Leitura: o prefixo explica uma parte importante da matriz, mas não explica tudo. O locus ainda deixa sinal mensurável depois do controle por prefixo.

A Rota 3 foi preparada em seguida para evitar que a etapa visual fosse preenchida por suposição.

Saídas:

- `docs/rota_3_anotacao_visual.md`;
- `data/annotations/visual_annotation_candidates_zl3b.csv`.

Resultado: 160 candidatos ranqueados para anotação manual. Os campos de imagem, cor, anel, setor, raio e objeto próximo ficaram vazios de propósito para evitar inferência automática.

## 12. Primeira anotação visual

A primeira rodada da Rota 3 conferiu imagens locais, expandiu a semente de anotação visual e gerou o primeiro cruzamento visual.

Saídas:

- `docs/rota_3_primeira_anotacao_visual.md`;
- `docs/rota_3_cruzamento_visual.md`;
- `data/annotations/visual_annotations_seed_zl3b.csv`.
- `data/derived/visual_annotation_summary_zl3b.csv`.

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

- `scripts/analyze_matrix_axes.py`;
- `docs/rota_4_eixos_matriz.md`;
- `data/derived/matrix_axis_summary_zl3b.csv`.

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

- `scripts/analyze_same_context_pairs.py`;
- `docs/rota_5_pares_comparaveis.md`;
- `data/derived/same_context_matrix_pairs_zl3b.csv`.

Resultado:

- 725 grupos comparáveis;
- 11 grupos com anotação visual direta;
- cobertura de eixo: `rl=327`, `ao+rl=219`, `ao=179`;
- famílias mais frequentes: `standalone=217`, `ch=183`, `d=93`, `ok=50`, `ot=49`, `qok=32`.

Leitura: a matriz gera pares locais suficientes para teste, sem depender de comparação distante entre páginas. O gargalo agora é visual: isolar a posição exata dos glifos nos 11 grupos já anotados antes de propor significado para `a/o` ou `r/l`.

## 15. Rota 6: conferência fina dos glifos

A Rota 6 transformou os 11 grupos com anotação visual direta em uma fila de revisão conservadora.

Saídas:

- `scripts/prepare_glyph_review_queue.py`;
- `docs/rota_6_conferencia_glifos.md`;
- `data/annotations/glyph_review_queue_zl3b.csv`.

Resultado:

- 11 grupos na fila;
- 11 ainda precisam de isolamento exato do glifo;
- fólios envolvidos: `f67r1=5`, `f70v2=3`, `f84r=2`, `f68r3=1`;
- nenhuma atribuição semântica nova foi feita.

Leitura: a evidência visual ainda está em nível de camada/folio. A próxima etapa precisa produzir recortes ou coordenadas aproximadas por `review_id`, mantendo `not isolated` quando a palavra exata não puder ser localizada.

## 16. Rota 7: recortes de revisão

A Rota 7 gerou recortes SVG aproximados para os 11 itens da fila R6.

Saídas:

- `scripts/prepare_review_crops.py`;
- `docs/rota_7_recortes_revisao.md`;
- `data/annotations/review_crop_manifest_zl3b.csv`;
- `images/derived/review_crops/*.svg`.

Resultado:

- 11 recortes SVG gerados;
- todos preservam `needs_exact_glyph_isolation`;
- todos têm escopo `rough_region_only`;
- nenhum JPG original foi modificado.

Leitura: agora a revisão visual é reproduzível por `crop_id`/`review_id`, mas as coordenadas continuam aproximadas. O próximo passo é abrir cada SVG e registrar coordenada melhorada ou manter `not isolated`.

## 17. Rota 8: revisão dos recortes

A Rota 8 validou os SVGs da Rota 7 e registrou a decisão conservadora por recorte.

Saídas:

- `scripts/review_crop_decisions.py`;
- `docs/rota_8_revisao_recortes.md`;
- `data/annotations/crop_review_decisions_zl3b.csv`.

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

- `scripts/prepare_manual_svg_review.py`;
- `docs/rota_9_revisao_manual.md`;
- `docs/rota_9_revisao_manual.html`;
- `data/annotations/manual_svg_review_zl3b.csv`.

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

- `scripts/consolidate_manual_svg_review.py`;
- `docs/rota_10_consolidacao_manual.md`;
- `data/derived/manual_svg_review_consolidated_zl3b.csv`;
- `data/derived/manual_review_status_summary_zl3b.csv`.

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

- `scripts/prepare_second_pass_crop_queue.py`;
- `docs/rota_11_segunda_passada_recortes.md`;
- `data/annotations/second_pass_crop_queue_zl3b.csv`;
- `data/derived/second_pass_crop_queue_summary_zl3b.csv`.

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

- `scripts/prepare_folio_review_packets.py`;
- `docs/rota_12_pacotes_revisao_guiada.md`;
- `data/annotations/folio_review_packets_zl3b.csv`;
- `data/annotations/folio_review_packet_items_zl3b.csv`;
- `data/derived/folio_review_packet_summary_zl3b.csv`.

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

- `scripts/prepare_packet_item_checklist.py`;
- `docs/rota_13_checklist_pacotes.md`;
- `data/annotations/packet_item_checklist_zl3b.csv`;
- `data/derived/packet_item_checklist_summary_zl3b.csv`.

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

- `scripts/consolidate_packet_item_checklist.py`;
- `docs/rota_14_consolidacao_checklist.md`;
- `data/derived/packet_item_checklist_consolidated_zl3b.csv`;
- `data/derived/packet_item_checklist_consolidation_summary_zl3b.csv`.

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

- `scripts/prepare_human_review_instructions.py`;
- `docs/rota_15_instrucoes_revisao_humana.md`;
- `data/annotations/human_review_instructions_zl3b.csv`;
- `data/annotations/human_review_instruction_items_zl3b.csv`;
- `data/derived/human_review_instruction_summary_zl3b.csv`.

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

- `scripts/consolidate_human_review_evidence.py`;
- `docs/rota_16_consolidacao_revisao_humana.md`;
- `data/derived/human_review_evidence_consolidated_zl3b.csv`;
- `data/derived/human_review_evidence_summary_zl3b.csv`.

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

- `scripts/prepare_priority_human_review.py`;
- `docs/rota_17_revisao_humana_p0_p1.md`;
- `data/annotations/priority_human_review_p0_p1_zl3b.csv`;
- `data/derived/priority_human_review_summary_zl3b.csv`.

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

- `scripts/ingest_priority_human_decisions.py`;
- `docs/rota_18_ingestao_decisoes_p0_p1.md`;
- `data/derived/priority_human_decisions_p0_p1_zl3b.csv`;
- `data/derived/priority_human_decisions_summary_zl3b.csv`.

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

- `scripts/prepare_direct_visual_decision_package.py`;
- `docs/rota_19_pacote_visual_direto_p0_p1.md`;
- `docs/rota_19_pacote_visual_direto_p0_p1.html`;
- `data/annotations/direct_visual_decision_package_p0_p1_zl3b.csv`;
- `data/derived/direct_visual_decision_package_summary_zl3b.csv`.

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

- `scripts/apply_direct_visual_decisions.py`;
- `docs/rota_20_aplicacao_decisoes_pacote_visual.md`;
- `data/derived/packet_item_checklist_after_direct_visual_p0_p1_zl3b.csv`;
- `data/derived/direct_visual_decision_application_log_zl3b.csv`;
- `data/derived/direct_visual_decision_application_summary_zl3b.csv`.

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

- `scripts/prepare_visual_decision_entry_sheet.py`;
- `docs/rota_21_planilha_preenchimento_visual_p0_p1.md`;
- `data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv`;
- `data/derived/visual_decision_entry_sheet_summary_zl3b.csv`.

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

- `scripts/validate_visual_decision_entry_sheet.py`;
- `docs/rota_22_validacao_planilha_visual.md`;
- `data/derived/direct_visual_package_after_entry_sheet_p0_p1_zl3b.csv`;
- `data/derived/visual_decision_entry_validation_log_zl3b.csv`;
- `data/derived/visual_decision_entry_validation_summary_zl3b.csv`.

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

- `scripts/prepare_guided_visual_entry_html.py`;
- `docs/rota_23_pacote_html_preenchimento_r21.md`;
- `docs/rota_23_pacote_html_preenchimento_r21.html`;
- `data/derived/guided_visual_entry_html_manifest_zl3b.csv`;
- `data/derived/guided_visual_entry_html_summary_zl3b.csv`.

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

- `scripts/verify_guided_visual_entry_readiness.py`;
- `docs/rota_24_prontidao_preenchimento_visual.md`;
- `data/derived/guided_visual_entry_readiness_zl3b.csv`;
- `data/derived/guided_visual_entry_readiness_summary_zl3b.csv`.

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

- `scripts/build_exact_form_context_table.py`;
- `docs/rota_26_tabela_contexto_formas_exatas.md`;
- `data/derived/exact_form_context_table_zl3b.csv`;
- `data/derived/exact_form_context_summary_zl3b.csv`.

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

- `scripts/prepare_exact_form_visual_gap_queue.py`;
- `docs/rota_27_fila_lacunas_visuais_formas_exatas.md`;
- `data/derived/exact_form_visual_gap_queue_zl3b.csv`;
- `data/derived/exact_form_visual_gap_summary_zl3b.csv`.

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

- `scripts/prepare_exact_form_visual_annotation_package.py`;
- `docs/rota_28_pacote_anotacao_visual_formas_exatas.md`;
- `docs/rota_28_pacote_anotacao_visual_formas_exatas.html`;
- `data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`;
- `data/derived/exact_form_visual_annotation_package_summary_zl3b.csv`.

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

- `scripts/prepare_missing_source_image_queue.py`;
- `docs/rota_29_fila_fontes_imagem_formas_exatas.md`;
- `docs/rota_29_fila_fontes_imagem_formas_exatas.html`;
- `data/annotations/exact_form_missing_source_queue_p0_p1_zl3b.csv`;
- `data/derived/exact_form_missing_source_summary_zl3b.csv`.

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

- `scripts/validate_missing_source_candidates.py`;
- `docs/rota_30_validacao_fontes_candidatas.md`;
- `data/derived/missing_source_candidate_validation_zl3b.csv`;
- `data/derived/missing_source_candidate_validation_summary_zl3b.csv`;
- `data/derived/commons_image_sources_after_source_validation_zl3b.csv`.

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

- `scripts/validate_ready_visual_annotations.py`;
- `docs/rota_31_validacao_anotacoes_visuais_prontas.md`;
- `data/derived/ready_visual_annotation_validation_zl3b.csv`;
- `data/derived/ready_manual_visual_annotations_zl3b.csv`;
- `data/derived/ready_visual_annotation_validation_summary_zl3b.csv`.

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

- `scripts/prepare_ready_visual_annotation_html.py`;
- `docs/rota_32_pacote_html_anotacao_visual_prontos.md`;
- `docs/rota_32_pacote_html_anotacao_visual_prontos.html`;
- `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`;
- `data/derived/ready_visual_annotation_html_summary_zl3b.csv`.

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

- `scripts/apply_ready_visual_annotation_entries.py`;
- `docs/rota_33_aplicacao_entradas_visuais_r32.md`;
- `data/derived/exact_form_visual_annotation_package_after_ready_entries_zl3b.csv`;
- `data/derived/ready_visual_annotation_entry_application_log_zl3b.csv`;
- `data/derived/ready_visual_annotation_entry_application_summary_zl3b.csv`.

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

- `scripts/verify_ready_visual_annotation_manual_gate.py`;
- `docs/rota_34_gate_manual_anotacao_visual_r32.md`;
- `data/derived/ready_visual_annotation_manual_gate_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_gate_summary_zl3b.csv`.

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

- `scripts/plan_ready_visual_annotation_post_gate_rerun.py`;
- `docs/rota_35_plano_reexecucao_pos_gate_r32.md`;
- `data/derived/ready_visual_annotation_post_gate_rerun_plan_zl3b.csv`;
- `data/derived/ready_visual_annotation_post_gate_rerun_summary_zl3b.csv`.

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

- `scripts/prepare_ready_visual_annotation_manual_fill_protocol.py`;
- `docs/rota_36_protocolo_preenchimento_humano_r32.md`;
- `data/derived/ready_visual_annotation_manual_fill_protocol_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_fill_protocol_summary_zl3b.csv`.

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

- `scripts/plan_ready_visual_annotation_revalidation_chain.py`;
- `docs/rota_37_plano_revalidacao_r34_r35_r33_r31.md`;
- `data/derived/ready_visual_annotation_revalidation_chain_plan_zl3b.csv`;
- `data/derived/ready_visual_annotation_revalidation_chain_summary_zl3b.csv`.

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

- `scripts/prepare_ready_visual_annotation_manual_reopen_work_order.py`;
- `docs/rota_38_ordem_trabalho_preencher_r32_reabrir_cadeia.md`;
- `data/derived/ready_visual_annotation_manual_reopen_work_order_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_reopen_work_order_summary_zl3b.csv`.

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

- `scripts/visual_crop.py`;
- `tests/test_visual_crop.py`;
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

- `scripts/prepare_ready_visual_word_opencv_map.py`;
- `tests/test_ready_visual_word_opencv_map.py`;
- `data/derived/ready_visual_word_opencv_map_zl3b.csv`;
- `data/derived/ready_visual_word_opencv_map_summary_zl3b.csv`;
- `docs/rota_42j_fragmentos_visuais_opencv_r32.md`;
- `docs/rota_42j_fragmentos_visuais_opencv_r32.html`.

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

- `scripts/prepare_ready_visual_review_priority_queue.py`;
- `tests/test_ready_visual_review_priority_queue.py`;
- `data/derived/ready_visual_review_priority_queue_zl3b.csv`;
- `data/derived/ready_visual_review_priority_queue_summary_zl3b.csv`;
- `docs/rota_42k_fila_priorizada_revisao_visual_r32.md`;
- `docs/rota_42k_fila_priorizada_revisao_visual_r32.html`.

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

- `scripts/prepare_ready_visual_line_choice_confirmation.py`;
- `tests/test_ready_visual_line_choice_confirmation.py`;
- `data/annotations/ready_visual_line_choice_confirmation_zl3b.csv`;
- `data/derived/ready_visual_line_choice_confirmation_summary_zl3b.csv`;
- `docs/rota_42l_confirmacao_linhas_sugeridas_r32.md`;
- `docs/rota_42l_confirmacao_linhas_sugeridas_r32.html`.

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

- `scripts/prepare_ready_visual_fine_line_capture.py`;
- `tests/test_ready_visual_fine_line_capture.py`;
- `data/derived/ready_visual_fine_line_capture_zl3b.csv`;
- `data/derived/ready_visual_fine_line_capture_summary_zl3b.csv`;
- `docs/rota_42m_captura_fina_linhas_r32.md`;
- `docs/rota_42m_captura_fina_linhas_r32.html`.

Resultado:

- 13 capturas finas geradas;
- 13 continuam exigindo confirmação humana;
- confiança operacional: 11 `media`, 2 `baixa`;
- R42M entrou no painel de ferramentas ativas;
- `selected_visual_line_number` e `selected_zone_box_pct` continuam vazios.

Leitura: a R42M melhora o alinhamento da captura, não a interpretação. Ela é uma lupa operacional, não OCR, tradução, confirmação de palavra ou evidência visual final.

## 65. Conclusão

A melhor leitura atual é:

> O Voynich não deve ser atacado como texto contínuo comum. Deve ser atacado como sistema formal com camadas. A unidade real talvez não seja a “palavra”, mas o template dentro de uma linha/locus.

A chave parcial provavelmente não será uma tradução lexical, mas uma tabela funcional.
