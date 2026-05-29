# Log dos ataques realizados

## Ataque geral: estatística do corpus

Observações:

- Tokens frequentes: `daiin`, `ol`, `chedy`, `aiin`, `shedy`, `chol`, `or`, `ar`, `chey`, `dar`, `qokeey`, `qokeedy`, `shey`, `qokain`, `qokedy`.
- Famílias recorrentes: `qok-`, `chedy/shedy`, `daiin/aiin`, `chol/chor`.
- Hipótese de substituição simples enfraquecida.

## Ataque Currier A/B

Currier A e B têm vocabulários e padrões diferentes.

- A: mais `daiin`, `chol`, `chor`, `sho`, `cth-`.
- B: mais `chedy`, `shedy`, `qokedy`, `qokeedy`, `qokain`.

Interpretação: regimes ou templates distintos, não necessariamente duas línguas.

## Ataque dos rótulos

Achado central: rótulos são uma subgramática.

- Muito mais `ok-`/`ot-`.
- Quase ausência de `qo-`.
- Alta taxa de hapax.
- Pouca repetição exata com o texto corrido da mesma página.

## Ataque visual-semântico

Candidatos:

- `otoldy`: aparece em farmacêutico, mas não como nome único de planta.
- `otaly/otoly`: atravessa zodíaco, farmacêutico e biológico.
- `okolshy`: aparece em contextos astronômicos e biológicos.
- `oran`: instável demais como âncora.

Conclusão: rótulos não parecem nomes diretos dos objetos.

## Ataque astronômico

Folios-chave:

- `f67r2`: “sete planetas”, 12 setores, luas, camada vermelha.
- `f68r3`: “Plêiades”, oito setores, grupo de sete estrelas.

Achado: estruturas visuais fortes, mas sem lista transparente de planetas/estrelas.

## Ataque da camada vermelha

Em `f67r2`:

- Anel vermelho externo: muita família `yk-`, `ch`, `k`; quase nenhum `q`.
- Linha vermelha inferior: `sshey syshees qeykeey ykchey ykchey qokeochy oaiin okal ar ol`.

Conclusão: vermelho é camada técnica/rubrical, não tradução direta.

## Ataque `okal/okar/ytokar`

`okal` apareceu como candidato a “Sol”, mas foi enfraquecido.

A família aparece em:

- luas;
- estrelas;
- anéis solares/lunares;
- texto circular;
- texto radial;
- anel vermelho;
- setores.

Conclusão: operador diagramático, não nome de astro.

## Ataque das bordas

Matriz mais promissora:

```text
        r       l

a      ar      al

o      or      ol
```

Hipótese: `a/o` e `r/l` são dois eixos independentes.

## Ataque contextual da matriz `ar/al/or/ol`

Novo artefato: `docs/estudo_matriz_bordas_contexto.md`.

Entradas iniciais:

- `data/transcriptions/f67r2_excerpt.eva`;
- `data/transcriptions/f68r3_excerpt.eva`.

Resultado:

- 46 linhas/loci preservados;
- 30 candidatos contextuais;
- `ar=11`, `ol=11`, `al=6`, `or=2`;
- `okar`, `okal` e `qokol` aparecem duas vezes cada;
- `ar` e `ol` aparecem como tokens autônomos na sequência vermelha `okal ar ol`.

Leitura provisória:

- a amostra é pequena e enviesada para diagramas astronômicos;
- a camada rubrical de `f67r2` favorece `ar/or`;
- linhas radiais/circulares de `f68r3` favorecem `ol`;
- isso fortalece a hipótese de borda como valor funcional de slot, mas ainda não identifica o eixo semântico de `a/o` ou `r/l`.

## Rota 1: corpus textual ampliado

Novo artefato: `docs/rota_1_corpus_textual.md`.

Fonte:

- `data/raw/ZL3b-n.txt`, Zandbergen-Landini IVTFF/EVA, versao 3b de 13/05/2025.

Resultado:

- 5.385 loci preservados;
- 41.005 tokens no contador simples;
- 8.398 candidatos contextuais `ar/al/or/ol`;
- `ol=2.793`, `ar=2.220`, `al=1.719`, `or=1.666`;
- candidatos exatos: 2.682;
- valores standalone: 1.639.

Locus x sufixo:

|locus|`ar`|`al`|`or`|`ol`|
|---|---:|---:|---:|---:|
|`P`|1.870|1.469|1.546|2.604|
|`C`|232|160|75|127|
|`L`|93|70|39|49|
|`R`|25|20|6|13|

Leitura provisoria:

- a matriz nao morreu no corpus maior;
- `ol` domina em `P`, mas `ar` domina em `C`;
- os valores standalone reforcam a leitura de slot;
- a proxima etapa deve ser controle estatistico, nao leitura semantica direta.

## Rota 2: controles estatisticos

Novo artefato: `docs/rota_2_controles_estatisticos.md`.

Entradas:

- `data/derived/border_matrix_context_zl3b.csv`.

Saidas:

- `data/derived/matrix_control_summary_zl3b.csv`;
- `data/derived/matrix_exact_pairs_zl3b.csv`.

Resultados-chave:

|controle|chi2|df|Cramer's V|embaralhamento|
|---|---:|---:|---:|---:|
|locus x sufixo|153,340|9|0,0780|p <= 0,0020|
|prefixo x sufixo|712,684|36|0,1682|p <= 0,0020|
|posicao x sufixo|240,746|9|0,0978|p <= 0,0020|
|locus x sufixo controlando prefixo|93,418|9|0,0609|n/a|

Leitura provisoria:

- prefixos explicam parte forte da matriz, como esperado;
- a posicao na linha tambem influencia a borda;
- mesmo depois de controlar por prefixo, locus ainda tem desvio mensuravel;
- isso favorece a hipotese de camada funcional, mas o efeito e pequeno/moderado e precisa de anotacao visual.

## Rota 3: preparacao da anotacao visual

Novo artefato: `docs/rota_3_anotacao_visual.md`.

Saida:

- `data/annotations/visual_annotation_candidates_zl3b.csv`.

Resultado:

- 160 candidatos ranqueados para anotacao manual;
- prioridade para `C`, `R`, `L`, rubricas, tokens exatos e valores standalone;
- campos visuais ficaram vazios de proposito.

Proxima acao:

- baixar/conferir imagens dos folios candidatos;
- preencher cor, zona visual, anel/setor/raio e objeto proximo;
- depois cruzar esses campos com `ar/al/or/ol`.

## Rota 3: primeira anotacao visual

Novo artefato: `docs/rota_3_primeira_anotacao_visual.md`.

Saida:

- `data/annotations/visual_annotations_seed_zl3b.csv`.
- `data/derived/visual_annotation_summary_zl3b.csv`.
- `docs/rota_3_cruzamento_visual.md`.

Imagens conferidas:

- `images/raw/commons_f67r1_r2.jpg`;
- `images/raw/commons_f67v2_v1.jpg`;
- `images/raw/commons_f68r1_r2_r3.jpg`.

Resultado:

- 56 anotacoes preenchidas;
- 10 folios cobertos;
- zonas: 23 circulares, 19 rotulos, 10 paragrafos/texto corrido, 4 radiais;
- confianca: 42 medias, 14 baixas.

Visual zone x sufixo:

|zona|`ar`|`al`|`or`|`ol`|
|---|---:|---:|---:|---:|
|circular text|10|6|1|6|
|label|8|4|5|2|
|paragraph text|3|4|2|1|
|radial text|3|0|0|1|

Leitura provisoria:

- a primeira anotacao visual e compativel com a leitura de camada/locus;
- ainda nao ha atribuicao semantica para `a/o` ou `r/l`;
- a confianca baixa marca casos em que o folio/camada foi identificado, mas a palavra exata ainda nao foi isolada em nivel de glifo;
- o lote `f70v2` pesa bastante em `ar/al`, entao o cruzamento visual ainda deve ser tratado como diagnostico de pipeline, nao como conclusao.

## Rota 4: eixos da matriz `ar/al/or/ol`

Novo artefato: `docs/rota_4_eixos_matriz.md`.

Entradas:

- `data/derived/border_matrix_context_zl3b.csv`;
- `data/annotations/visual_annotations_seed_zl3b.csv`.

Saidas:

- `data/derived/matrix_axis_summary_zl3b.csv`;
- `docs/rota_4_eixos_matriz.md`.

Resultados no corpus textual:

|controle|eixo `a/o`|eixo `r/l`|
|---|---:|---:|
|locus_kind|V=0,1336|V=0,0385|
|prefixo|V=0,2607|V=0,1179|
|posicao de linha|V=0,1356|V=0,0635|

Resultados na semente visual:

|controle|eixo `a/o`|eixo `r/l`|
|---|---:|---:|
|visual_zone|V=0,0777|V=0,2126|
|object_nearby|V=0,6306|V=0,4300|
|folio|V=0,5974|V=0,3619|

Leitura provisoria:

- no corpus textual, o eixo `a/o` carrega muito mais estrutura que `r/l`;
- prefixo e posicao de linha afetam principalmente o eixo `a/o`;
- na semente visual, os valores por objeto/folio sao fortes demais para conclusao sem controle, porque a amostra e pequena e enviesada por pagina;
- a proxima rota deve comparar pares dentro do mesmo folio/locus/familia, nao misturar paginas heterogeneas.

## Rota 5: pares comparaveis no mesmo contexto

Novo artefato: `docs/rota_5_pares_comparaveis.md`.

Entradas:

- `data/derived/border_matrix_context_zl3b.csv`;
- `data/annotations/visual_annotations_seed_zl3b.csv`.

Saidas:

- `scripts/analyze_same_context_pairs.py`;
- `data/derived/same_context_matrix_pairs_zl3b.csv`;
- `docs/rota_5_pares_comparaveis.md`.

Resultado:

- 725 grupos comparaveis no mesmo folio/locus/familia;
- 11 grupos com anotacao visual direta;
- cobertura de eixo: `rl=327`, `ao+rl=219`, `ao=179`;
- familias: `standalone=217`, `ch=183`, `d=93`, `ok=50`, `ot=49`, `sh=46`, `qok=32`, `qo=29`, `o=19`.

Grupos anotados mais uteis:

|folio/locus|familia|sufixos|eixo|tokens|visual|
|---|---|---|---|---|---|
|`f67r1.6,+Cc`|`d`|`al ar ol`|`ao+rl`|`dal dar dol`|texto circular|
|`f67r1.5,@Cc`|`standalone`|`ar ol`|`ao+rl`|`ar ol`|texto circular|
|`f84r.14,+P0`|`standalone`|`ol or`|`rl`|`ol or`|paragrafo biologico|
|`f67r1.6,+Cc`|`ch`|`ar ol or`|`ao+rl`|`chedar cheol cheor chol`|texto circular|
|`f68r3.1,@Cc`|`ch`|`al ol or`|`ao+rl`|`cheor chodal chokol chol`|texto circular|

Leitura provisoria:

- a matriz tem muitos pares locais, entao a hipotese nao depende mais de comparacoes distantes entre paginas;
- `standalone` e util para isolar valores puros da matriz, mas nao deve ser misturado com pares `ok/ot/qok` sem controle;
- a proxima etapa e visual: confirmar a posicao exata dos 11 grupos anotados antes de propor significado para `a/o` ou `r/l`.

## Rota 6: conferencia fina dos glifos

Novo artefato: `docs/rota_6_conferencia_glifos.md`.

Entradas:

- `data/derived/same_context_matrix_pairs_zl3b.csv`;
- `data/annotations/visual_annotations_seed_zl3b.csv`.

Saidas:

- `scripts/prepare_glyph_review_queue.py`;
- `data/annotations/glyph_review_queue_zl3b.csv`;
- `docs/rota_6_conferencia_glifos.md`.

Resultado:

- 11 grupos entraram na fila de revisao;
- todos os 11 ficaram com status `needs_exact_glyph_isolation`;
- folios: `f67r1=5`, `f70v2=3`, `f84r=2`, `f68r3=1`;
- imagens: `commons_f67r1_r2.jpg`, `commons_f70v2.jpg`, `commons_f84r.jpg`, `commons_f68r1_r2_r3.jpg`.

Fila principal:

|id|folio/locus|familia|sufixos|tokens anotados|faltam|
|---|---|---|---|---|---|
|`R6-001`|`f67r1.6,+Cc`|`d`|`al ar ol`|`dal dar`|`dol`|
|`R6-002`|`f67r1.5,@Cc`|`standalone`|`ar ol`|`ar ol`||
|`R6-003`|`f84r.14,+P0`|`standalone`|`ol or`|`ol or`||
|`R6-004`|`f67r1.6,+Cc`|`standalone`|`al ar`|`al ar`||
|`R6-005`|`f67r1.6,+Cc`|`ch`|`ar ol or`|`chol`|`chedar cheol cheor`|

Leitura provisoria:

- a evidencia visual ainda esta em nivel de camada, nao em coordenada/glifo;
- a rota impede o salto indevido de "texto circular identificado" para "palavra exata localizada";
- a proxima etapa deve criar recortes ou coordenadas aproximadas para cada `review_id`.

## Rota 7: recortes de revisao

Novo artefato: `docs/rota_7_recortes_revisao.md`.

Entradas:

- `data/annotations/glyph_review_queue_zl3b.csv`;
- imagens locais em `images/raw/`.

Saidas:

- `scripts/prepare_review_crops.py`;
- `data/annotations/review_crop_manifest_zl3b.csv`;
- `docs/rota_7_recortes_revisao.md`;
- `images/derived/review_crops/*.svg`.

Resultado:

- 11 recortes SVG gerados;
- todos preservam `isolation_status=needs_exact_glyph_isolation`;
- todos usam `crop_scope=rough_region_only`;
- folios: `f67r1=5`, `f70v2=3`, `f84r=2`, `f68r3=1`;
- nenhum JPG original foi modificado.

Leitura provisoria:

- agora ha artefatos visuais reproduziveis para a revisao;
- os SVGs sao wrappers nao destrutivos com `viewBox` sobre a imagem original;
- as coordenadas sao regioes aproximadas, nao localizacao de palavra;
- a proxima etapa deve abrir cada SVG e registrar coordenada melhorada ou manter `not isolated`.

## Rota 8: revisao dos recortes

Novo artefato: `docs/rota_8_revisao_recortes.md`.

Entradas:

- `data/annotations/review_crop_manifest_zl3b.csv`;
- `images/derived/review_crops/*.svg`.

Saidas:

- `scripts/review_crop_decisions.py`;
- `data/annotations/crop_review_decisions_zl3b.csv`;
- `docs/rota_8_revisao_recortes.md`.

Resultado:

- 11 recortes avaliados;
- 11 SVGs validos;
- 11 decisoes `keep_not_isolated`;
- 8 decisoes ainda tem tokens do grupo nao anotados diretamente;
- nenhuma coordenada de glifo foi confirmada.

Leitura provisoria:

- os SVGs sao artefatos validos para revisao, mas continuam amplos;
- a decisao correta por enquanto e manter `not isolated`;
- a proxima rota deve ser uma revisao manual assistida, nao uma inferencia automatica de significado.

## Rota 9: revisao manual assistida dos SVGs

Novo artefato: `docs/rota_9_revisao_manual.md`.

Entradas:

- `data/annotations/crop_review_decisions_zl3b.csv`;
- `images/derived/review_crops/*.svg`.

Saidas:

- `scripts/prepare_manual_svg_review.py`;
- `data/annotations/manual_svg_review_zl3b.csv`;
- `docs/rota_9_revisao_manual.md`;
- `docs/rota_9_revisao_manual.html`.

Resultado:

- 11 itens na folha manual;
- 11 com `pending_manual_review`;
- familias: `standalone=5`, `ch=3`, `ot=2`, `d=1`;
- campos de coordenada em branco por desenho;
- nenhuma coordenada/glifo confirmada.

Leitura provisoria: agora existe uma interface revisavel; a proxima etapa depende de preencher manualmente coordenadas ou manter `not isolated`.

## Rota 10: consolidacao da revisao manual

Novo artefato: `docs/rota_10_consolidacao_manual.md`.

Entradas:

- `data/annotations/manual_svg_review_zl3b.csv`.

Saidas:

- `scripts/consolidate_manual_svg_review.py`;
- `data/derived/manual_svg_review_consolidated_zl3b.csv`;
- `data/derived/manual_review_status_summary_zl3b.csv`;
- `docs/rota_10_consolidacao_manual.md`.

Resultado:

- 11 itens consolidados;
- 11 com `pending_manual_review`;
- 11 com `no_manual_coordinates`;
- 11 com `no_glyph_confirmation`;
- 0 elegiveis para teste visual dos eixos.

Leitura provisoria: a Rota 10 fechou a porta para interpretacao prematura. Enquanto a folha manual estiver vazia, o caminho correto e nova revisao visual ou recortes melhores, nao semantica.

## Rota 11: segunda passada de recortes melhores

Novo artefato: `docs/rota_11_segunda_passada_recortes.md`.

Entradas:

- `data/derived/manual_svg_review_consolidated_zl3b.csv`.

Saidas:

- `scripts/prepare_second_pass_crop_queue.py`;
- `data/annotations/second_pass_crop_queue_zl3b.csv`;
- `data/derived/second_pass_crop_queue_summary_zl3b.csv`;
- `docs/rota_11_segunda_passada_recortes.md`.

Resultado:

- 11 itens na fila;
- 14 tokens faltantes a procurar;
- 8 itens com foco em localizar tokens faltantes;
- 3 itens para apertar a regiao ja anotada;
- prioridades: `P0_operator_missing_tokens=2`, `P1_core_missing_tokens=4`, `P2_other_missing_tokens=2`, `P3_tighten_existing_region=3`.

Leitura provisoria: a fila organiza o trabalho manual sem transformar prioridade operacional em significado. Todos os itens preservam a guarda `no_axis_meaning_from_queue_position`.

## Rota 12: pacotes por folio para revisao guiada

Novo artefato: `docs/rota_12_pacotes_revisao_guiada.md`.

Entradas:

- `data/annotations/second_pass_crop_queue_zl3b.csv`;
- `data/annotations/review_crop_manifest_zl3b.csv`.

Saidas:

- `scripts/prepare_folio_review_packets.py`;
- `data/annotations/folio_review_packets_zl3b.csv`;
- `data/annotations/folio_review_packet_items_zl3b.csv`;
- `data/derived/folio_review_packet_summary_zl3b.csv`;
- `docs/rota_12_pacotes_revisao_guiada.md`.

Resultado:

- 4 pacotes por folio/imagem;
- 11 itens preservados;
- 14 tokens faltantes agregados;
- objetivos: `review_source_image_first=3`, `search_tokens_then_redraw_crop=1`;
- folios: `f67r1`, `f68r3`, `f70v2`, `f84r`.

Leitura provisoria: agora o trabalho visual esta organizado por pagina/imagem fonte. O pacote e uma unidade operacional de revisao, nao evidencia de significado.

## Rota 13: checklist item-a-item por pacote

Novo artefato: `docs/rota_13_checklist_pacotes.md`.

Entradas:

- `data/annotations/folio_review_packet_items_zl3b.csv`.

Saidas:

- `scripts/prepare_packet_item_checklist.py`;
- `data/annotations/packet_item_checklist_zl3b.csv`;
- `data/derived/packet_item_checklist_summary_zl3b.csv`;
- `docs/rota_13_checklist_pacotes.md`.

Resultado:

- 11 itens na checklist;
- 8 alvos `missing_group_tokens`;
- 3 alvos `matched_group_tokens`;
- 11 com `pending_visual_check`;
- campos manuais vazios por desenho.

Leitura provisoria: a checklist cria uma superficie de anotacao manual rastreavel, mas ainda nao adiciona evidencia visual nova.

## Rota 14: consolidacao da checklist preenchida

Novo artefato: `docs/rota_14_consolidacao_checklist.md`.

Entradas:

- `data/annotations/packet_item_checklist_zl3b.csv`.

Saidas:

- `scripts/consolidate_packet_item_checklist.py`;
- `data/derived/packet_item_checklist_consolidated_zl3b.csv`;
- `data/derived/packet_item_checklist_consolidation_summary_zl3b.csv`;
- `docs/rota_14_consolidacao_checklist.md`.

Resultado:

- 11 itens consolidados;
- 11 com `pending_visual_check`;
- 11 com `no_new_crop_coordinates`;
- 11 com `no_new_visual_evidence`;
- 0 elegiveis apos geracao de recorte.

Leitura provisoria: a consolidacao confirma que a checklist ainda nao adicionou observacao visual. Campos vazios continuam sendo pendencia, nao negativa nem confirmacao.

## Rota 15: instrucoes humanas por pacote

Novo artefato: `docs/rota_15_instrucoes_revisao_humana.md`.

Entradas:

- `data/annotations/folio_review_packets_zl3b.csv`;
- `data/annotations/packet_item_checklist_zl3b.csv`.

Saidas:

- `scripts/prepare_human_review_instructions.py`;
- `data/annotations/human_review_instructions_zl3b.csv`;
- `data/annotations/human_review_instruction_items_zl3b.csv`;
- `data/derived/human_review_instruction_summary_zl3b.csv`;
- `docs/rota_15_instrucoes_revisao_humana.md`.

Resultado:

- 4 pacotes receberam instrucoes humanas;
- 11 itens foram preservados item-a-item;
- modos: `open_source_image_before_svg=3`, `search_tokens_then_redraw_crop=1`;
- campos manuais continuam vazios por desenho;
- guarda aplicada: `human_instruction_not_visual_evidence`.

Leitura provisoria: as instrucoes tornam a revisao visual executavel por humano, mas ainda nao adicionam evidencia. A proxima rota deve consolidar apenas respostas preenchidas manualmente.

## Rota 16: consolidacao da revisao humana

Novo artefato: `docs/rota_16_consolidacao_revisao_humana.md`.

Entradas:

- `data/annotations/human_review_instruction_items_zl3b.csv`;
- `data/annotations/packet_item_checklist_zl3b.csv`.

Saidas:

- `scripts/consolidate_human_review_evidence.py`;
- `data/derived/human_review_evidence_consolidated_zl3b.csv`;
- `data/derived/human_review_evidence_summary_zl3b.csv`;
- `docs/rota_16_consolidacao_revisao_humana.md`.

Resultado:

- 11 itens consolidados;
- 11 continuam em `pending_human_review`;
- 11 sem coordenadas novas;
- 11 sem evidencia visual humana;
- 0 prontos para novo recorte apos revisao.

Leitura provisoria: a Rota 16 confirmou formalmente que a revisao humana ainda nao foi preenchida. A proxima acao real e revisar os itens P0/P1 nas imagens fonte e preencher a checklist, nao interpretar `a/o` ou `r/l`.

## Rota 17: fila P0/P1 para revisao humana

Novo artefato: `docs/rota_17_revisao_humana_p0_p1.md`.

Entrada:

- `data/derived/human_review_evidence_consolidated_zl3b.csv`.

Saidas:

- `scripts/prepare_priority_human_review.py`;
- `data/annotations/priority_human_review_p0_p1_zl3b.csv`;
- `data/derived/priority_human_review_summary_zl3b.csv`;
- `docs/rota_17_revisao_humana_p0_p1.md`.

Resultado:

- 6 itens P0/P1 entraram na fila;
- prioridades: `P0=2`, `P1=4`;
- folios: `f67r1=3`, `f70v2=2`, `f68r3=1`;
- todos os itens sao `missing_group_tokens`;
- os campos manuais continuam sem preenchimento automatico.

Leitura provisoria: a fila torna a revisao humana executavel sem fingir que ela ja aconteceu. A proxima rota deve ingerir somente decisoes preenchidas na checklist.

## Rota 18: ingestao das decisoes P0/P1

Novo artefato: `docs/rota_18_ingestao_decisoes_p0_p1.md`.

Entradas:

- `data/annotations/priority_human_review_p0_p1_zl3b.csv`;
- `data/annotations/packet_item_checklist_zl3b.csv`.

Saidas:

- `scripts/ingest_priority_human_decisions.py`;
- `data/derived/priority_human_decisions_p0_p1_zl3b.csv`;
- `data/derived/priority_human_decisions_summary_zl3b.csv`;
- `docs/rota_18_ingestao_decisoes_p0_p1.md`.

Resultado:

- 6 itens P0/P1 ingeridos;
- 6 seguem em `pending_manual_decision`;
- 0 candidatos a novo recorte;
- 6 com `not_ready` para teste de eixo;
- campos vazios nao foram convertidos em evidencia.

Leitura provisoria: a ingestao confirmou que a revisao P0/P1 ainda nao foi preenchida. A proxima etapa deve reduzir a friccao visual para preencher esses 6 itens, nao reinterpretar a matriz.

## Rota 19: pacote visual direto P0/P1

Novo artefato: `docs/rota_19_pacote_visual_direto_p0_p1.md`.

Entradas:

- `data/derived/priority_human_decisions_p0_p1_zl3b.csv`.

Saidas:

- `scripts/prepare_direct_visual_decision_package.py`;
- `data/annotations/direct_visual_decision_package_p0_p1_zl3b.csv`;
- `data/derived/direct_visual_decision_package_summary_zl3b.csv`;
- `docs/rota_19_pacote_visual_direto_p0_p1.md`;
- `docs/rota_19_pacote_visual_direto_p0_p1.html`.

Resultado:

- 6 itens entraram no pacote visual direto;
- prioridades: `P0=2`, `P1=4`;
- folios: `f67r1=3`, `f70v2=2`, `f68r3=1`;
- status do pacote: `ready_for_manual_visual_decision=6`;
- campos manuais seguem vazios.

Leitura provisoria: o pacote HTML coloca imagem fonte e SVG lado a lado para diminuir a friccao da revisao. Ele nao confirma tokens e nao deve ser usado como evidencia sem preenchimento humano.

## Rota 20: aplicacao do pacote visual na checklist

Novo artefato: `docs/rota_20_aplicacao_decisoes_pacote_visual.md`.

Entradas:

- `data/annotations/direct_visual_decision_package_p0_p1_zl3b.csv`;
- `data/annotations/packet_item_checklist_zl3b.csv`.

Saidas:

- `scripts/apply_direct_visual_decisions.py`;
- `data/derived/packet_item_checklist_after_direct_visual_p0_p1_zl3b.csv`;
- `data/derived/direct_visual_decision_application_log_zl3b.csv`;
- `data/derived/direct_visual_decision_application_summary_zl3b.csv`;
- `docs/rota_20_aplicacao_decisoes_pacote_visual.md`.

Resultado:

- 6 linhas do pacote foram processadas;
- 0 valores manuais foram aplicados;
- 6 linhas foram ignoradas por campos vazios;
- nenhum campo vazio apagou valor existente;
- a checklist original nao foi sobrescrita.

Leitura provisoria: a aplicacao confirma que ainda falta preencher o pacote visual. A proxima etapa deve ser revisao visual/preenchimento manual, nao nova interpretacao de eixo.

## Rota 21: planilha de preenchimento visual P0/P1

Novo artefato: `docs/rota_21_planilha_preenchimento_visual_p0_p1.md`.

Entradas:

- `data/derived/direct_visual_decision_application_log_zl3b.csv`;
- `data/annotations/direct_visual_decision_package_p0_p1_zl3b.csv`.

Saidas:

- `scripts/prepare_visual_decision_entry_sheet.py`;
- `data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv`;
- `data/derived/visual_decision_entry_sheet_summary_zl3b.csv`;
- `docs/rota_21_planilha_preenchimento_visual_p0_p1.md`.

Resultado:

- 6 linhas aguardam preenchimento manual;
- prioridades: `P0=2`, `P1=4`;
- folios: `f67r1=3`, `f70v2=2`, `f68r3=1`;
- status: `awaiting_manual_entry=6`;
- valores permitidos: `manual_token_seen=yes/no/uncertain`, `manual_new_crop_needed=yes/no`, `manual_image_insufficient=yes/no`;
- campos manuais seguem vazios.

Leitura provisoria: a Rota 21 nao e evidencia visual; e uma planilha controlada para reduzir erro humano no preenchimento. A proxima rota deve validar essa planilha preenchida e aplicar apenas valores explicitos.

## Rota 22: validacao da planilha visual R21

Novo artefato: `docs/rota_22_validacao_planilha_visual.md`.

Entradas:

- `data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv`;
- `data/annotations/direct_visual_decision_package_p0_p1_zl3b.csv`.

Saidas:

- `scripts/validate_visual_decision_entry_sheet.py`;
- `data/derived/direct_visual_package_after_entry_sheet_p0_p1_zl3b.csv`;
- `data/derived/visual_decision_entry_validation_log_zl3b.csv`;
- `data/derived/visual_decision_entry_validation_summary_zl3b.csv`;
- `docs/rota_22_validacao_planilha_visual.md`.

Resultado:

- 6 linhas da planilha R21 foram validadas;
- entradas validas: 0;
- entradas pendentes: 6;
- entradas invalidas: 0;
- status de aplicacao: `skipped_blank_manual_entry=6`;
- campos vazios nao apagaram nem criaram valores.

Leitura provisoria: a validacao esta pronta, mas a planilha R21 segue sem decisao humana. A proxima rota deve facilitar o preenchimento visual, nao reinterpretar os eixos.

## Rota 23: pacote HTML guiado para preencher R21

Novo artefato: `docs/rota_23_pacote_html_preenchimento_r21.md`.

Entradas:

- `data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv`;
- `data/derived/visual_decision_entry_validation_log_zl3b.csv`.

Saidas:

- `scripts/prepare_guided_visual_entry_html.py`;
- `data/derived/guided_visual_entry_html_manifest_zl3b.csv`;
- `data/derived/guided_visual_entry_html_summary_zl3b.csv`;
- `docs/rota_23_pacote_html_preenchimento_r21.md`;
- `docs/rota_23_pacote_html_preenchimento_r21.html`.

Resultado:

- 6 cartoes HTML foram gerados;
- prioridades: `P0=2`, `P1=4`;
- folios: `f67r1=3`, `f70v2=2`, `f68r3=1`;
- status: `ready_for_guided_manual_entry=6`;
- valores permitidos aparecem em cada cartao;
- nenhuma decisao foi gravada automaticamente.

Leitura provisoria: a friccao visual foi reduzida ao minimo restante. O proximo passo nao e estatistico: e preencher manualmente a R21 usando o HTML e reexecutar a Rota 22.

## Rota 24: prontidao para preenchimento visual R21

Novo artefato: `docs/rota_24_prontidao_preenchimento_visual.md`.

Entradas:

- `data/derived/guided_visual_entry_html_manifest_zl3b.csv`;
- `data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv`;
- `docs/rota_23_pacote_html_preenchimento_r21.html`.

Saidas:

- `scripts/verify_guided_visual_entry_readiness.py`;
- `data/derived/guided_visual_entry_readiness_zl3b.csv`;
- `data/derived/guided_visual_entry_readiness_summary_zl3b.csv`;
- `docs/rota_24_prontidao_preenchimento_visual.md`.

Resultado:

- 6 itens foram verificados;
- 6 estao prontos para preenchimento manual;
- 0 ja contem entrada manual;
- 0 estao bloqueados por asset ausente;
- 0 estao bloqueados por cartao HTML ausente;
- imagem fonte, SVG, cartao HTML e valores permitidos foram confirmados para todos os itens.

Leitura provisoria: a etapa operacional esta pronta. O proximo passo depende de decisao visual manual na R21; a Rota 24 nao acrescenta evidencia sobre os eixos.

## Rota 25: gate manual de preenchimento R21

Status: pendente de decisao visual manual.

Motivo:

- a R21 so deve receber valores vistos explicitamente no HTML R23;
- campos vazios continuam pendentes;
- preencher automaticamente `manual_token_seen` ou coordenadas criaria evidencia falsa;
- portanto a execucao automatizada segue para outra frente enquanto esse gate humano permanece aberto.

Leitura provisoria: nada mudou na evidencia P0/P1; a planilha R21 continua vazia.

## Rota 26: tabela ampliada das formas exatas ok/ot

Novo artefato: `docs/rota_26_tabela_contexto_formas_exatas.md`.

Entradas:

- `data/derived/border_matrix_context_zl3b.csv`;
- `data/annotations/visual_annotations_seed_zl3b.csv`.

Saidas:

- `scripts/build_exact_form_context_table.py`;
- `data/derived/exact_form_context_table_zl3b.csv`;
- `data/derived/exact_form_context_summary_zl3b.csv`;
- `docs/rota_26_tabela_contexto_formas_exatas.md`.

Resultado:

- 786 ocorrencias das oito formas exatas;
- `ok*`: 394;
- `ot*`: 392;
- formas mais comuns: `okal=152`, `otar=147`, `okar=133`, `otal=129`;
- com anotacao visual exata: 23;
- sem anotacao visual exata: 763;
- guarda: `exact_form_context_not_decipherment`.

Leitura provisoria: o eixo `ok/ot` esta praticamente equilibrado nesta selecao exata. A baixa cobertura visual vira uma fila de anotacao, nao uma conclusao sobre significado.

## Rota 27: fila de lacunas visuais das formas exatas

Novo artefato: `docs/rota_27_fila_lacunas_visuais_formas_exatas.md`.

Entradas:

- `data/derived/exact_form_context_table_zl3b.csv`;
- `data/commons_image_sources.csv`.

Saidas:

- `scripts/prepare_exact_form_visual_gap_queue.py`;
- `data/derived/exact_form_visual_gap_queue_zl3b.csv`;
- `data/derived/exact_form_visual_gap_summary_zl3b.csv`;
- `docs/rota_27_fila_lacunas_visuais_formas_exatas.md`.

Resultado:

- 195 grupos de lacuna visual foram criados;
- prioridades: `P0=1`, `P1=25`, `P2=7`, `P3=162`;
- 15 grupos ja tem imagem no manifesto;
- 180 grupos ainda exigem localizar ou baixar fonte de imagem;
- tipos de locus: `P=154`, `L=19`, `C=18`, `R=4`;
- primeiro item P0: `f99v/P`, com 8 lacunas e imagem disponivel.

Leitura provisoria: a fila R27 organiza trabalho de anotacao, nao interpreta `ok/ot` nem os sufixos. O proximo passo automatizavel e montar um pacote P0/P1, separando imagem pronta de busca de fonte.

## Rota 28: pacote de anotacao visual das formas exatas P0/P1

Novo artefato: `docs/rota_28_pacote_anotacao_visual_formas_exatas.md`.

Entradas:

- `data/derived/exact_form_visual_gap_queue_zl3b.csv`.

Saidas:

- `scripts/prepare_exact_form_visual_annotation_package.py`;
- `data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`;
- `data/derived/exact_form_visual_annotation_package_summary_zl3b.csv`;
- `docs/rota_28_pacote_anotacao_visual_formas_exatas.md`;
- `docs/rota_28_pacote_anotacao_visual_formas_exatas.html`.

Resultado:

- 26 itens P0/P1 foram empacotados;
- prioridades: `P0=1`, `P1=25`;
- 8 itens estao prontos para anotacao visual manual a partir do manifesto;
- 18 itens estao bloqueados por falta de imagem fonte;
- tipos de locus: `P=23`, `L=2`, `C=1`;
- campos manuais permanecem vazios.

Leitura provisoria: a Rota 28 cria uma superficie de trabalho. `ready_for_manual_visual_annotation` nao e evidencia; `blocked_pending_source_image` e somente uma fila para resolver fontes antes da revisao.

## Rota 29: fila de fontes de imagem ausentes

Novo artefato: `docs/rota_29_fila_fontes_imagem_formas_exatas.md`.

Entradas:

- `data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`.

Saidas:

- `scripts/prepare_missing_source_image_queue.py`;
- `data/annotations/exact_form_missing_source_queue_p0_p1_zl3b.csv`;
- `data/derived/exact_form_missing_source_summary_zl3b.csv`;
- `docs/rota_29_fila_fontes_imagem_formas_exatas.md`;
- `docs/rota_29_fila_fontes_imagem_formas_exatas.html`.

Resultado:

- 18 itens bloqueados da Rota 28 viraram fila de fonte ausente;
- todos estao em `pending_public_source_verification`;
- `P1=18`;
- tipos de locus: `P=17`, `C=1`;
- campos `candidate_commons_page`, `candidate_image_url` e `source_notes` seguem vazios;
- o manifesto nao deve ser atualizado ate a URL ser verificada.

Leitura provisoria: a Rota 29 separa busca de fonte de anotacao visual. Consultas de busca nao sao fontes confirmadas nem evidencia sobre os glifos.

## Rota 30: validacao de fontes candidatas

Novo artefato: `docs/rota_30_validacao_fontes_candidatas.md`.

Entradas:

- `data/annotations/exact_form_missing_source_queue_p0_p1_zl3b.csv`;
- `data/commons_image_sources.csv`.

Saidas:

- `scripts/validate_missing_source_candidates.py`;
- `data/derived/missing_source_candidate_validation_zl3b.csv`;
- `data/derived/missing_source_candidate_validation_summary_zl3b.csv`;
- `data/derived/commons_image_sources_after_source_validation_zl3b.csv`;
- `docs/rota_30_validacao_fontes_candidatas.md`.

Resultado:

- 18 candidatos foram avaliados;
- 18 continuam em `pending_blank_source_candidate`;
- 0 fontes candidatas validas estruturalmente;
- 0 fontes invalidas;
- 0 linhas anexadas ao manifesto derivado;
- o manifesto original nao recebeu novas fontes;
- a copia derivada manteve 10 linhas de manifesto.

Leitura provisoria: a infraestrutura de validacao/aplicacao esta pronta, mas a Rota 29 ainda nao tem URLs candidatas. Campo vazio continua pendente, nao rejeicao.

## Rota 31: validacao de anotacoes visuais manuais prontas

Novo artefato: `docs/rota_31_validacao_anotacoes_visuais_prontas.md`.

Entradas:

- `data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`.

Saidas:

- `scripts/validate_ready_visual_annotations.py`;
- `data/derived/ready_visual_annotation_validation_zl3b.csv`;
- `data/derived/ready_manual_visual_annotations_zl3b.csv`;
- `data/derived/ready_visual_annotation_validation_summary_zl3b.csv`;
- `docs/rota_31_validacao_anotacoes_visuais_prontas.md`.

Resultado:

- 8 itens com imagem no manifesto foram avaliados;
- 8 continuam em `pending_blank_manual_annotation`;
- 0 anotacoes manuais validas;
- 0 anotacoes manuais invalidas;
- 0 registros gravados na tabela derivada de anotacoes;
- campos manuais vazios continuam pendentes.

Leitura provisoria: a validacao das anotacoes manuais esta pronta, mas nenhuma evidencia visual nova foi adicionada. A proxima rota deve reduzir a friccao para preencher esses 8 itens.

## Rota 32: pacote HTML focado para anotacoes visuais prontas

Novo artefato: `docs/rota_32_pacote_html_anotacao_visual_prontos.md`.

Entradas:

- `data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`;
- `data/derived/ready_visual_annotation_validation_zl3b.csv`.

Saidas:

- `scripts/prepare_ready_visual_annotation_html.py`;
- `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`;
- `data/derived/ready_visual_annotation_html_summary_zl3b.csv`;
- `docs/rota_32_pacote_html_anotacao_visual_prontos.md`;
- `docs/rota_32_pacote_html_anotacao_visual_prontos.html`.

Resultado:

- 8 cartoes HTML foram gerados para itens pendentes da Rota 31;
- todos seguem em `pending_blank_manual_annotation`;
- prioridades: `P0=1`, `P1=7`;
- tipos de locus: `P=6`, `L=2`;
- campos `manual_annotation_status` e `manual_visual_notes` seguem vazios;
- valores permitidos: `annotated/not_visible/uncertain`.

Leitura provisoria: a Rota 32 e uma superficie de entrada manual, nao uma decisao visual. O proximo passo e aplicar somente valores humanos preenchidos de volta a um pacote R28 derivado e reexecutar R31.

## Rota 33: aplicacao das entradas visuais R32

Novo artefato: `docs/rota_33_aplicacao_entradas_visuais_r32.md`.

Entradas:

- `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`;
- `data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`.

Saidas:

- `scripts/apply_ready_visual_annotation_entries.py`;
- `data/derived/exact_form_visual_annotation_package_after_ready_entries_zl3b.csv`;
- `data/derived/ready_visual_annotation_entry_application_log_zl3b.csv`;
- `data/derived/ready_visual_annotation_entry_application_summary_zl3b.csv`;
- `docs/rota_33_aplicacao_entradas_visuais_r32.md`.

Resultado:

- 8 entradas R32 foram avaliadas;
- 8 continuam em `pending_blank_manual_annotation`;
- 0 entradas validas;
- 0 entradas invalidas;
- 0 linhas atualizadas no pacote derivado;
- o pacote R28 original nao foi alterado.

Leitura provisoria: a aplicacao controlada esta pronta, mas nao houve preenchimento humano. A proxima etapa real e manual: preencher R32 com `annotated/not_visible/uncertain` e notas explicitas.

## Rota 34: gate manual de anotacao visual R32

Novo artefato: `docs/rota_34_gate_manual_anotacao_visual_r32.md`.

Entradas:

- `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`;
- `docs/rota_32_pacote_html_anotacao_visual_prontos.html`;
- `data/derived/ready_visual_annotation_entry_application_log_zl3b.csv`.

Saidas:

- `scripts/verify_ready_visual_annotation_manual_gate.py`;
- `data/derived/ready_visual_annotation_manual_gate_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_gate_summary_zl3b.csv`;
- `docs/rota_34_gate_manual_anotacao_visual_r32.md`.

Resultado:

- 8 itens foram verificados;
- 8 estao bloqueados por `blocked_pending_manual_annotation`;
- 0 estao prontos para reexecutar R33/R31;
- 8 cartoes HTML foram encontrados;
- 8 itens preservam os valores permitidos no HTML.

Leitura provisoria: o pipeline chegou ao limite correto. A proxima acao exige anotacao visual humana na planilha R32; continuar por inferencia violaria a guarda do estudo.

## Rota 35: plano de reexecucao pos-gate R32

Novo artefato: `docs/rota_35_plano_reexecucao_pos_gate_r32.md`.

Entradas:

- `data/derived/ready_visual_annotation_manual_gate_zl3b.csv`.

Saidas:

- `scripts/plan_ready_visual_annotation_post_gate_rerun.py`;
- `data/derived/ready_visual_annotation_post_gate_rerun_plan_zl3b.csv`;
- `data/derived/ready_visual_annotation_post_gate_rerun_summary_zl3b.csv`;
- `docs/rota_35_plano_reexecucao_pos_gate_r32.md`.

Resultado:

- 8 itens foram avaliados contra o gate R34;
- 8 estao em `blocked_by_manual_gate`;
- 0 estao prontos para reexecucao controlada;
- 0 reexecucoes R33/R31 foram planejadas agora.

Leitura provisoria: o pipeline pos-gate esta armado, mas nao deve rodar R33/R31 enquanto nao houver entrada humana explicita na planilha R32.

## Rota 36: protocolo de preenchimento humano R32

Novo artefato: `docs/rota_36_protocolo_preenchimento_humano_r32.md`.

Entradas:

- `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`;
- `data/derived/ready_visual_annotation_post_gate_rerun_plan_zl3b.csv`;
- `docs/rota_32_pacote_html_anotacao_visual_prontos.html`.

Saidas:

- `scripts/prepare_ready_visual_annotation_manual_fill_protocol.py`;
- `data/derived/ready_visual_annotation_manual_fill_protocol_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_fill_protocol_summary_zl3b.csv`;
- `docs/rota_36_protocolo_preenchimento_humano_r32.md`.

Resultado:

- 8 itens entraram no protocolo de preenchimento;
- 8 aguardam `awaiting_human_visual_entry`;
- 0 entradas estao prontas para reexecutar o gate;
- 0 entradas estao invalidas;
- a planilha R32 original permanece sem preenchimento automatico.

Leitura provisoria: o proximo avanço depende de revisao visual humana. A rota documenta a acao exata, mas nao substitui a decisao humana.

## Rota 37: plano de revalidacao R34/R35/R33/R31

Novo artefato: `docs/rota_37_plano_revalidacao_r34_r35_r33_r31.md`.

Entradas:

- `data/derived/ready_visual_annotation_manual_fill_protocol_zl3b.csv`.

Saidas:

- `scripts/plan_ready_visual_annotation_revalidation_chain.py`;
- `data/derived/ready_visual_annotation_revalidation_chain_plan_zl3b.csv`;
- `data/derived/ready_visual_annotation_revalidation_chain_summary_zl3b.csv`;
- `docs/rota_37_plano_revalidacao_r34_r35_r33_r31.md`.

Resultado:

- 8 itens foram avaliados;
- 8 estao em `blocked_no_human_entries`;
- 0 estao prontos para a cadeia de revalidacao;
- 0 execucoes da cadeia `R34>R35>R33>R31` foram planejadas agora.

Leitura provisoria: a ordem de revalidacao esta documentada, mas a cadeia permanece bloqueada ate haver preenchimento humano na planilha R32.

## Rota 38: ordem de trabalho para preencher R32 e reabrir cadeia

Novo artefato: `docs/rota_38_ordem_trabalho_preencher_r32_reabrir_cadeia.md`.

Entradas:

- `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_fill_protocol_zl3b.csv`;
- `data/derived/ready_visual_annotation_revalidation_chain_plan_zl3b.csv`;
- `docs/rota_32_pacote_html_anotacao_visual_prontos.html`.

Saidas:

- `scripts/prepare_ready_visual_annotation_manual_reopen_work_order.py`;
- `data/derived/ready_visual_annotation_manual_reopen_work_order_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_reopen_work_order_summary_zl3b.csv`;
- `docs/rota_38_ordem_trabalho_preencher_r32_reabrir_cadeia.md`.

Resultado:

- 8 itens entraram na ordem de trabalho;
- 8 exigem preenchimento manual;
- 0 estao prontos para reabrir a cadeia;
- 0 estao bloqueados por entrada invalida;
- a planilha R32 original permanece preservada.

Leitura provisoria: a tarefa humana agora esta isolada em uma ordem de trabalho. Nao ha nova evidencia visual ate que a planilha R32 seja preenchida por revisao humana.

## Rota 39: auditoria de execucao do preenchimento humano R32

Novo artefato: `docs/rota_39_auditoria_execucao_preenchimento_humano_r32.md`.

Entradas:

- `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_reopen_work_order_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_fill_protocol_zl3b.csv`;
- `data/derived/ready_visual_annotation_revalidation_chain_plan_zl3b.csv`.

Saidas:

- `scripts/audit_ready_visual_annotation_manual_fill_execution.py`;
- `data/derived/ready_visual_annotation_manual_fill_execution_audit_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_fill_execution_audit_summary_zl3b.csv`;
- `docs/rota_39_auditoria_execucao_preenchimento_humano_r32.md`.

Resultado:

- 8 itens foram auditados;
- 8 estao em `manual_fill_not_executed`;
- 0 estao prontos para reabrir a cadeia;
- 0 estao bloqueados por entrada invalida ou parcial;
- a planilha R32 original permanece preservada.

Leitura provisoria: a auditoria confirma que a etapa humana ainda nao aconteceu. A cadeia R34/R35/R33/R31 continua bloqueada ate que a R32 receba entradas humanas explicitas e R36/R37/R39 sejam reexecutadas.

## Rota 40: plano condicional de reabertura da cadeia R34/R35/R33/R31

Novo artefato: `docs/rota_40_plano_condicional_reabertura_cadeia_r39.md`.

Entradas:

- `data/derived/ready_visual_annotation_manual_fill_execution_audit_zl3b.csv`.

Saidas:

- `scripts/plan_ready_visual_annotation_conditional_chain_reopen.py`;
- `data/derived/ready_visual_annotation_conditional_chain_reopen_plan_zl3b.csv`;
- `data/derived/ready_visual_annotation_conditional_chain_reopen_summary_zl3b.csv`;
- `docs/rota_40_plano_condicional_reabertura_cadeia_r39.md`.

Resultado:

- 8 itens foram planejados;
- 8 estao em `blocked_waiting_human_entry`;
- 0 estao prontos para rodar `R34>R35>R33>R31`;
- 0 estao bloqueados por entrada invalida;
- a acao planejada e `do_not_run_revalidation_chain`.

Leitura provisoria: a R40 transforma a auditoria R39 em uma regra operacional: a cadeia so reabre se R39 liberar explicitamente. No estado atual, a cadeia continua fechada por falta de entrada humana na R32.

## Rota 41: pacote de entrada humana externa na R32

Novo artefato: `docs/rota_41_pacote_entrada_humana_externa_r32.md`.

Entradas:

- `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_reopen_work_order_zl3b.csv`;
- `data/derived/ready_visual_annotation_conditional_chain_reopen_plan_zl3b.csv`.

Saidas:

- `scripts/prepare_ready_visual_annotation_external_human_entry_packet.py`;
- `data/derived/ready_visual_annotation_external_human_entry_packet_zl3b.csv`;
- `data/derived/ready_visual_annotation_external_human_entry_summary_zl3b.csv`;
- `docs/rota_41_pacote_entrada_humana_externa_r32.md`.

Resultado:

- 8 itens entraram no pacote;
- 8 exigem `external_human_entry_required`;
- 0 entradas humanas estao presentes;
- 0 entradas estao invalidas ou parciais;
- a planilha R32 original permanece preservada.

Leitura provisoria: a rota tornou a tarefa humana externa executavel e auditavel, mas ainda nao ha evidencia visual nova. A cadeia permanece fechada ate preenchimento humano explicito na R32 e reexecucao de R36/R37/R39/R40.

## Rota 42: fontes Yale IIIF high-res para R32

Novo artefato: `docs/rota_42_fontes_yale_iiif_highres_r32.md`.

Entradas:

- `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`;
- `data/derived/yale_iiif_manifest_2002046.json`;
- manifesto oficial Yale/Beinecke: `https://collections.library.yale.edu/manifests/2002046`.

Saidas:

- `scripts/prepare_ready_visual_annotation_highres_source_packet.py`;
- `data/derived/ready_visual_annotation_highres_sources_zl3b.csv`;
- `data/derived/ready_visual_annotation_highres_sources_summary_zl3b.csv`;
- `docs/rota_42_fontes_yale_iiif_highres_r32.md`;
- `docs/rota_42_pacote_html_yale_iiif_highres_r32.html`;
- `images/raw/yale_iiif_r32/*.jpg`.

Resultado:

- 8 itens da R32 foram mapeados para o manifesto Yale;
- 4 matches exatos, 2 por folio colapsado e 2 por pagina composta;
- 8 JPEGs IIIF foram baixados localmente;
- 0 fontes ficaram sem match;
- a R32 original permaneceu preservada.

Leitura provisoria: a revisao humana agora pode usar imagens oficiais mais nitidas da Yale/Beinecke. Isso melhora o insumo visual, mas nao cria anotacao nem decifracao.

## Rota 42A: analise assistida das fontes Yale high-res

Novo artefato: `docs/rota_42a_analise_assistida_highres_r32.md`.

Entradas:

- `data/derived/ready_visual_annotation_highres_sources_zl3b.csv`;
- imagens locais em `images/raw/yale_iiif_r32/*.jpg`.

Saidas:

- `scripts/prepare_ready_visual_annotation_highres_ai_assist.py`;
- `data/derived/ready_visual_annotation_highres_ai_assist_zl3b.csv`;
- `data/derived/ready_visual_annotation_highres_ai_assist_summary_zl3b.csv`;
- `docs/rota_42a_analise_assistida_highres_r32.md`.

Resultado:

- 8 itens avaliados;
- 5 imagens classificadas como `high`;
- 2 regioes ficaram claramente localizaveis para recorte (`f84r`, `f99r`);
- 4 regioes ficaram parcialmente localizaveis;
- 2 itens exigem cuidado de pagina composta (`f88v`, `f89r2`);
- 0 decisoes exatas de token foram tomadas pela IA;
- a cadeia continua bloqueada para os 8 itens.

Leitura provisoria: a analise assistida ajuda a direcionar o revisor humano, mas nao substitui a anotacao manual R32 e nao libera R34/R35/R33/R31.

## Rota 42B: ferramenta guiada de preenchimento humano R32 high-res

Novo artefato: `docs/rota_42b_pacote_html_preenchimento_humano_r32.html`.

Entradas:

- `data/derived/ready_visual_annotation_highres_sources_zl3b.csv`;
- `data/derived/ready_visual_annotation_highres_ai_assist_zl3b.csv`.

Saidas:

- `scripts/prepare_ready_visual_annotation_highres_human_fill_html.py`;
- `tests/test_ready_visual_annotation_highres_human_fill_html.py`;
- `data/derived/ready_visual_annotation_highres_human_fill_html_zl3b.csv`;
- `data/derived/ready_visual_annotation_highres_human_fill_html_summary_zl3b.csv`;
- `docs/rota_42b_preenchimento_humano_highres_r32.md`;
- `docs/rota_42b_pacote_html_preenchimento_humano_r32.html`.

Resultado:

- 8 itens de revisao guiada foram gerados;
- a ordem de revisao comeca por `f84r` e `f99r`;
- a pagina contem pergunta `Voce achou essas palavrinhas na imagem?`;
- a pagina mostra cartoes visuais EVA para comparar o desenho da palavra com a imagem;
- a pagina mostra total de entradas/loci ZL3b por folio, lista auditavel dessas entradas e texto de referencia das linhas alvo;
- a pagina contem botoes simples `Achei`/`Nao achei`/`Nao sei`, mapeados para `annotated/not_visible/uncertain`;
- a pagina contem fila lateral, item ativo, proximo pendente, zoom, contraste, rotacao, mostrar/esconder zonas, subir/descer zonas, reset de vista e atalho para calibrar linhas na R42C;
- a pagina mostra baselines calibradas da R42C quando existirem, ou zonas visuais provaveis de bloco quando a linha ainda estiver pendente;
- a pagina mostra chips de tokens/linhas e recolhe os detalhes tecnicos;
- a pagina contem guia rapido, nota automatica e rascunho CSV recolhido para uso no final;
- a R32 original permanece preservada.

Leitura provisoria: o preenchimento ficou mais intuitivo, mas continua humano. As baselines R42C sao apoio operacional de localizacao, nao evidencia automatica; quando uma baseline ainda nao existe, as zonas visuais continuam ajustaveis e aproximadas por bloco, nao linhas exatas. A ferramenta nao calcula posicao visual por proporcao da numeracao ZL3b. O total por folio segue entradas/loci ZL3b e nao e uma contagem visual direta da imagem. Os deslocamentos de zona sao temporarios para que recarregar a pagina volte ao mapa calibrado. A pagina nao altera a planilha alvo e nao cria evidencia por si so.

## Rota 42C: calibracao manual de linhas/baselines R32 high-res

Novo artefato: `docs/rota_42c_calibrador_linhas_baseline_r32.html`.

Entradas:

- `data/derived/ready_visual_annotation_highres_human_fill_html_zl3b.csv`;
- `data/raw/ZL3b-n.txt`.

Saidas:

- `scripts/prepare_ready_visual_line_calibration_tool.py`;
- `tests/test_ready_visual_line_calibration_tool.py`;
- `data/annotations/ready_visual_line_calibration_zl3b.csv`;
- `data/derived/ready_visual_line_calibration_summary_zl3b.csv`;
- `docs/rota_42c_calibracao_linhas_baseline_r32.md`;
- `docs/rota_42c_calibrador_linhas_baseline_r32.html`.

Resultado:

- 19 linhas/loci alvo foram extraidos da R42B;
- todos continuam como `pending_calibration`;
- 2 linhas (`f84r.24,+P0` e `f84r.29,+P0`) receberam `baseline_points` de rascunho OpenCV agrupado, ainda pendentes;
- a ferramenta agora mostra `Guia rapido`, progresso, mira, coordenadas percentuais e ultimo clique para deixar claro onde o usuario esta apontando;
- o painel da imagem ganhou respiro de scroll para zoom alto, scroll natural para cima quando chega no topo, e botao `Topo da imagem` para retornar ao canto superior;
- a ferramenta permite clicar no comeco e no fim da linha real para gerar `baseline_points`;
- a ferramenta agora permite `Ajuste fino` da linha inteira ou de cada ponta em passos pequenos, reaproveitando os mesmos `baseline_points`;
- a ferramenta gera um rascunho CSV separado da R32, com botoes `Copiar CSV` e `Baixar CSV`;
- a ferramenta tem atalhos `Abrir R42B`, `Abrir sugestoes OpenCV` e `Abrir mapa OpenCV`;
- quando a R42D gera sugestao OpenCV, a ferramenta mescla a baseline como rascunho pendente, registra o numero de linha visual candidata e `Acao OpenCV: prefill_pending_baseline`, mostra `Computador ja ajudou` com proximo passo humano e ainda nao marca como calibrada automaticamente;
- o overlay do scan foi preso ao canvas real da imagem; cada item recebeu assinatura deterministica do scan para rejeitar rascunho local defasado, e a UI manteve `Resetar scan local` para limpar sobras do navegador;
- o script preserva baselines manuais ja existentes em reruns;
- o status `calibrated` sem pelo menos dois pontos validos volta para `pending_calibration`, inclusive se vier de CSV ou rascunho local antigo;
- a R32 original permanece preservada.

Leitura provisoria: a R42C melhora a precisao operacional da busca visual sem criar evidencia automatica. A baseline calibrada e referencia de localizacao, nao traducao nem decisao visual.

## Rota 42D: sugestoes OpenCV para calibracao inicial de linhas

Novo artefato: `docs/rota_42d_sugestoes_opencv_linhas_r32.html`.

Entradas:

- `data/annotations/ready_visual_line_calibration_zl3b.csv`;
- imagens high-res em `images/raw/yale_iiif_r32/`.

Saidas:

- `scripts/prepare_ready_visual_line_opencv_suggestions.py`;
- `tests/test_ready_visual_line_opencv_suggestions.py`;
- `data/derived/ready_visual_line_opencv_suggestions_zl3b.csv`;
- `data/derived/ready_visual_line_opencv_suggestions_summary_zl3b.csv`;
- `docs/rota_42d_sugestoes_opencv_linhas_r32.md`;
- `docs/rota_42d_sugestoes_opencv_linhas_r32.html`.

Resultado:

- 19 alvos analisados;
- 2 sugestoes `opencv_suggested_needs_human_confirmation` para `f84r.24` e `f84r.29`, agora como linhas visuais 6 e 14 no mapa agrupado, classificadas como `prefill_pending_baseline`;
- 13 alvos com faixas detectadas, mas ainda sem zona manual para associar alvo e posicao (`needs_manual_zone`);
- 4 alvos sem faixa confiavel detectada (`needs_better_scan_or_manual_line`);
- a R42C consome as duas sugestoes confiaveis como `baseline_points` pendentes;
- nenhuma sugestao preenche R32 ou altera `calibrated` automaticamente.

Leitura provisoria: OpenCV agora resolve sozinho a parte mecanica segura: detecta faixas, numera linhas visuais e pre-preenche rascunhos de baseline quando ja existe zona manual. Ele continua sendo apoio operacional; nao prova que o locus ZL3b esta naquela faixa e nao aceita calibracao sozinho.

## Rota 42E: mapa OpenCV de linhas visuais

Novo artefato: `docs/rota_42e_mapa_opencv_linhas_visuais_r32.html`.

Entradas:

- `data/annotations/ready_visual_line_calibration_zl3b.csv`;
- imagens high-res em `images/raw/yale_iiif_r32/`.

Saidas:

- `scripts/prepare_ready_visual_line_opencv_map.py`;
- `tests/test_ready_visual_line_opencv_map.py`;
- `data/derived/ready_visual_line_opencv_map_zl3b.csv`;
- `data/derived/ready_visual_line_opencv_map_images_zl3b.csv`;
- `data/derived/ready_visual_line_opencv_map_summary_zl3b.csv`;
- `docs/rota_42e_mapa_opencv_linhas_visuais_r32.md`;
- `docs/rota_42e_mapa_opencv_linhas_visuais_r32.html`.

Resultado:

- 8 imagens mapeadas;
- 52 linhas visuais agrupadas detectadas no mapa bruto;
- f84r ficou com 23 linhas visuais agrupadas no mapa bruto;
- R42D passou a usar linhas agrupadas filtradas, sugerindo f84r.24 como linha visual 6 e f84r.29 como linha visual 14;
- a pagina abre em modo focado nas zonas R32 conhecidas, desenha reguas finas em vez de caixas grandes e mantem `Mapa bruto` para auditoria;
- a pagina tem navegacao para R42B, R42C e R42D.

Leitura provisoria: a R42E e uma ferramenta de orientacao visual. Ela conta/numera faixas de texto da imagem, mas nao confirma palavras, traducao ou preenchimento R32.

## Rota 42F: escolha simples de linhas visuais sem zona

Novo artefato: `docs/rota_42f_escolha_linhas_visuais_sem_zona_r32.html`.

Entradas:

- `data/annotations/ready_visual_line_calibration_zl3b.csv`;
- `data/derived/ready_visual_line_opencv_suggestions_zl3b.csv`;
- `data/derived/ready_visual_line_opencv_map_zl3b.csv`.

Saidas:

- `scripts/prepare_ready_visual_line_zone_choice_tool.py`;
- `tests/test_ready_visual_line_zone_choice_tool.py`;
- `data/annotations/ready_visual_line_zone_choice_zl3b.csv`;
- `data/derived/ready_visual_line_zone_choice_summary_zl3b.csv`;
- `docs/rota_42f_escolha_linhas_visuais_sem_zona_r32.md`;
- `docs/rota_42f_escolha_linhas_visuais_sem_zona_r32.html`.

Resultado:

- 13 alvos entraram na fila `pending_zone_choice`;
- a pagina mostra as linhas visuais reais da R42E, com zonas derivadas das caixas OpenCV;
- o usuario pode escolher `Essa e a linha`;
- a R42D agora esta preparada para consumir `selected_zone_box_pct` da R42F e transformar escolhas em novas baselines pendentes;
- nenhuma escolha preenche R32 ou marca R42C como calibrada automaticamente.

Leitura provisoria: a R42F nao aumenta a traducao, mas reduz a ambiguidade operacional. Ela transforma o problema “OpenCV achou linhas, mas nao sabe qual e o locus” em uma escolha humana simples e auditavel.

## Rota 42G: painel unico de ferramentas ativas R32

Novo artefato: `docs/rota_42g_ferramentas_ativas_r32.html`.

Saidas:

- `scripts/prepare_active_tool_dashboard.py`;
- `tests/test_active_tool_dashboard.py`;
- `docs/rota_42g_ferramentas_ativas_r32.md`;
- `docs/rota_42g_ferramentas_ativas_r32.html`.

Resultado:

- 10 ferramentas HTML ativas permanecem na pasta `docs`: R42G, R42K, R42L, R42M, R42F, R42D, R42J, R42C, R42B e R42E;
- 8 ferramentas HTML antigas foram removidas;
- as paginas ativas ganharam link `Ferramentas ativas`;
- a limpeza e idempotente e registrada em teste.

Leitura provisoria: a R42G nao altera evidencia, traducao ou planilhas. Ela reduz a superficie humana para evitar uso acidental de ferramentas antigas.

## Rota 42H: renderizacao visual EVA nas ferramentas ativas

Novo helper: `scripts/eva_visual.py`.

Saidas:

- `scripts/eva_visual.py`;
- `tests/test_eva_visual.py`;
- R42B, R42C e R42F regeneradas com texto de referencia visual;
- R42D, R42E e R42G regeneradas para manter o conjunto ativo consistente.

Resultado:

- tokens e linhas de referencia EVA agora aparecem como cartoes SVG;
- alvos ficam destacados com `is-target`;
- a interface humana deixa de depender de texto cru como `okar,y`;
- texto cru permanece nos CSVs e payloads tecnicos para auditoria/reexecucao.

Leitura provisoria: a R42H e melhoria de UX. Ela nao muda evidencia, transcricao, traducao ou planilhas.

## Rota 42I: recortes reais e lupas nas ferramentas ativas

Novo helper: `scripts/visual_crop.py`.

Saidas:

- `scripts/visual_crop.py`;
- `tests/test_visual_crop.py`;
- R42B, R42C, R42D, R42E, R42F e R42G regeneradas com apoio de recortes reais quando aplicavel.

Resultado:

- R42B mostra recortes reais da pagina antes da decisao final;
- R42C mostra lupa da linha pelos pontos atuais ou pela sugestao OpenCV;
- R42D mostra recorte real da sugestao quando ha caixa visual;
- R42E mostra recortes das linhas detectadas;
- R42F transforma linhas candidatas em botoes com recorte real clicavel;
- R42G direciona o fluxo para o modo de recortes.

Leitura provisoria: a R42I reduz friccao e erro humano ao trocar comparacao de codigo por comparacao imagem contra imagem. Ela nao e OCR, nao traduz, nao confirma palavra e nao altera planilhas originais.

## Rota 42J: fragmentos visuais OpenCV dentro das linhas

Novo artefato: `docs/rota_42j_fragmentos_visuais_opencv_r32.html`.

Entradas:

- `data/derived/ready_visual_line_opencv_map_zl3b.csv`;
- imagens high-res em `images/raw/yale_iiif_r32/`.

Saídas:

- `scripts/prepare_ready_visual_word_opencv_map.py`;
- `tests/test_ready_visual_word_opencv_map.py`;
- `data/derived/ready_visual_word_opencv_map_zl3b.csv`;
- `data/derived/ready_visual_word_opencv_map_summary_zl3b.csv`;
- `docs/rota_42j_fragmentos_visuais_opencv_r32.md`;
- `docs/rota_42j_fragmentos_visuais_opencv_r32.html`.

Resultado:

- 52 linhas visuais analisadas;
- 77 fragmentos visuais detectados por OpenCV;
- R42J adicionada ao painel ativo R42G;
- atalhos adicionados nas ferramentas relacionadas;
- cada fragmento aparece como recorte real da imagem.

Leitura provisoria: a R42J aprofunda a visão computacional sem fingir OCR. É uma lupa de fragmentos para orientar a revisão humana.

## Rota 42K: fila priorizada de revisão visual

Novo artefato: `docs/rota_42k_fila_priorizada_revisao_visual_r32.html`.

Entradas:

- `data/annotations/ready_visual_line_zone_choice_zl3b.csv`;
- `data/derived/ready_visual_word_opencv_map_zl3b.csv`;
- `data/derived/ready_visual_annotation_highres_human_fill_html_zl3b.csv`.

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
- R42K adicionada ao painel ativo R42G;
- atalhos adicionados em R42F e R42J;
- atalho adicionado para a R42L como tela de confirmação.

Leitura provisoria: a R42K reduz atrito humano ao indicar por onde começar. Ela nao e OCR, nao traduz e nao cria evidencia visual.

## Rota 42L: confirmacao de linhas sugeridas

Novo artefato: `docs/rota_42l_confirmacao_linhas_sugeridas_r32.html`.

Entradas:

- `data/derived/ready_visual_review_priority_queue_zl3b.csv`;
- `data/annotations/ready_visual_line_zone_choice_zl3b.csv`.

Saídas:

- `scripts/prepare_ready_visual_line_choice_confirmation.py`;
- `tests/test_ready_visual_line_choice_confirmation.py`;
- `data/annotations/ready_visual_line_choice_confirmation_zl3b.csv`;
- `data/derived/ready_visual_line_choice_confirmation_summary_zl3b.csv`;
- `docs/rota_42l_confirmacao_linhas_sugeridas_r32.md`;
- `docs/rota_42l_confirmacao_linhas_sugeridas_r32.html`.

Resultado:

- 13 itens pendentes de confirmacao humana;
- 4 itens em `revisar_primeiro`;
- 4 itens em `revisar_depois`;
- 5 itens em `revisao_dificil`;
- R42L adicionada ao painel ativo R42G;
- nenhuma linha sugerida foi aplicada automaticamente;
- a R42L agora aponta para a R42M como lupa de captura fina.

Leitura provisoria: a R42L torna a fila da R42K mais segura e idempotente. Ela preserva a sugestao, mostra alternativas e exige selecao humana antes de qualquer uso em R42F/R42D/R42C.

## Rota 42M: captura fina de linhas

Novo artefato: `docs/rota_42m_captura_fina_linhas_r32.html`.

Entradas:

- `data/annotations/ready_visual_line_choice_confirmation_zl3b.csv`;
- fragmentos/zonas propagados da R42K/R42L.

Saídas:

- `scripts/prepare_ready_visual_fine_line_capture.py`;
- `tests/test_ready_visual_fine_line_capture.py`;
- `data/derived/ready_visual_fine_line_capture_zl3b.csv`;
- `data/derived/ready_visual_fine_line_capture_summary_zl3b.csv`;
- `docs/rota_42m_captura_fina_linhas_r32.md`;
- `docs/rota_42m_captura_fina_linhas_r32.html`.

Resultado:

- 13 capturas finas;
- 13 exigem confirmacao humana;
- 11 com confiança operacional `media`;
- 2 com confiança operacional `baixa`;
- R42M adicionada ao painel ativo R42G;
- nenhum campo de decisão humana foi preenchido automaticamente.

Leitura provisoria: a R42M melhora a captura visual, não a prova. Ela gera `refined_capture_box_pct` e `refined_baseline_points` como ajuda operacional, sem OCR, sem tradução e sem evidência final.
