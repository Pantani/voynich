# Rotas de pesquisa

Este arquivo organiza as proximas frentes do estudo sem transformar o projeto em uma tentativa de "decifrar" por intuicao. Cada rota precisa gerar evidencia que possa confirmar, enfraquecer ou matar uma hipotese.

## Rota 1: ampliar corpus textual

Objetivo: testar a matriz `ar/al/or/ol` em uma transcricao IVTFF/EVA maior, nao apenas nos trechos manuais de `f67r2` e `f68r3`.

Fonte principal:

- Zandbergen-Landini, `ZL3b-n.txt`, IVTFF 2.0/EVA, versao 3b de 13/05/2025.

Perguntas:

- `ar/al/or/ol` continua desigual por locus (`P`, `L`, `C`, `R`) quando o corpus aumenta?
- `ok-`, `ot-`, `qok-`, `yk-` e `yt-` preferem bordas diferentes?
- os valores independentes `ar`, `al`, `or`, `ol` aparecem em posicoes especificas de linha?
- a diferenca vista nos trechos astronomicos sobrevive em secoes herbais, biologicas, zodiacais e estrelas?

Saidas esperadas:

- arquivo bruto em `data/raw/`;
- CSV contextual em `data/derived/`;
- relatorio Markdown em `docs/`;
- resumo comparando trechos pequenos versus corpus maior.

Status: primeira rodada concluida em `docs/rota_1_corpus_textual.md`.

Resultado curto:

- fonte: `data/raw/ZL3b-n.txt`;
- loci preservados: 5.385;
- candidatos contextuais: 8.398;
- maior borda: `ol=2.793`;
- valores standalone: 1.639.

## Rota 2: testes falsificaveis e controles

Objetivo: verificar se a matriz e os operadores sobrevivem a controles estatisticos simples.

Testes propostos:

- comparar distribuicao real contra tokens embaralhados;
- comparar linhas reais contra linhas embaralhadas dentro do mesmo folio;
- medir inicio/meio/fim de linha;
- separar tokens exatos de candidatos amplos;
- comparar por prefixo e por tipo de locus.

Predicao forte:

- se `ar/al/or/ol` sao valores de slot, a distribuicao real deve ser mais estruturada por locus/posicao/prefixo do que uma distribuicao embaralhada.

Status: primeira rodada concluida em `docs/rota_2_controles_estatisticos.md`.

Resultado curto:

- `locus_vs_suffix`: chi2=153,340; Cramer's V=0,0780; embaralhamento p<=0,0020;
- `prefix_vs_suffix`: chi2=712,684; Cramer's V=0,1682; embaralhamento p<=0,0020;
- `line_position_vs_suffix`: chi2=240,746; Cramer's V=0,0978; embaralhamento p<=0,0020;
- `locus_vs_suffix_given_prefix`: chi2=93,418; Cramer's V=0,0609.

Leitura: o padrao por locus nao e explicado apenas pela mistura de prefixos, embora o efeito seja pequeno/moderado e ainda precise de anotacao visual.

## Rota 3: anotacao visual manual

Objetivo: acrescentar contexto visual nos folios mais informativos.

Folios candidatos:

- `f67r2`;
- `f68r3`;
- `f70v2`;
- `f89r1`;
- paginas de estrelas no final do manuscrito.

Campos manuais:

- anel, setor ou raio;
- posicao aproximada;
- cor/tinta;
- objeto grafico proximo;
- relacao com rótulo, texto circular, radial ou paragrafo.

Predicao forte:

- se os finais da matriz codificam estado, direcao, classe ou posicao, a anotacao visual deve revelar agrupamentos nao triviais.

Status: lista inicial preparada em `docs/rota_3_anotacao_visual.md`.

Resultado curto:

- CSV de trabalho: `data/annotations/visual_annotation_candidates_zl3b.csv`;
- candidatos selecionados: 160;
- campos visuais foram deixados vazios de proposito para evitar preenchimento por suposicao.

Primeira anotacao visual:

- relatorio: `docs/rota_3_primeira_anotacao_visual.md`;
- cruzamento: `docs/rota_3_cruzamento_visual.md`;
- CSV preenchido: `data/annotations/visual_annotations_seed_zl3b.csv`;
- resumo derivado: `data/derived/visual_annotation_summary_zl3b.csv`;
- 56 anotacoes em imagens conferidas localmente;
- folios cobertos: `f67r1`, `f67r2`, `f67v2`, `f68r1`, `f68r2`, `f68r3`, `f70v2`, `f84r`, `f88v`, `f99v`;
- zonas visuais: 23 circulares, 19 rotulos, 10 paragrafos/texto corrido, 4 radiais;
- alguns arquivos grandes do Commons seguem pendentes por HTTP 429.

## Rota 4: separar os eixos da matriz

Objetivo: testar se `ar/al/or/ol` se comporta melhor como quatro sufixos independentes ou como dois eixos binarios:

```text
        r       l
a      ar      al
o      or      ol
```

Perguntas:

- o eixo `a/o` aparece mais forte que o eixo `r/l` no corpus textual?
- prefixo, locus e posicao de linha afetam os dois eixos da mesma maneira?
- a semente visual sugere diferencas entre texto circular, rotulos, radial e paragrafo?

Status: primeira rodada concluida em `docs/rota_4_eixos_matriz.md`.

Saidas:

- `scripts/analyze_matrix_axes.py`;
- `data/derived/matrix_axis_summary_zl3b.csv`;
- `docs/rota_4_eixos_matriz.md`.

Resultado curto:

- corpus textual: `locus_kind x a/o` tem Cramer's V=0,1336, enquanto `locus_kind x r/l` tem V=0,0385;
- corpus textual: `prefix x a/o` tem V=0,2607, enquanto `prefix x r/l` tem V=0,1179;
- corpus textual: `line_position x a/o` tem V=0,1356, enquanto `line_position x r/l` tem V=0,0635;
- semente visual: `visual_zone x a/o` e fraco nesta amostra (V=0,0777), mas `visual_zone x r/l` aparece maior (V=0,2126), ainda com n pequeno.

Leitura: o eixo `a/o` parece carregar a maior parte da estrutura textual, especialmente por prefixo e posicao de linha. O eixo `r/l` ainda pode ser visual/diagramatico, mas precisa ser testado em pares comparaveis dentro do mesmo folio ou locus.

## Rota 5: pares comparaveis dentro do mesmo folio/locus

Objetivo: evitar comparar paginas muito diferentes entre si.

Status: primeira rodada concluida em `docs/rota_5_pares_comparaveis.md`.

Saidas:

- `scripts/analyze_same_context_pairs.py`;
- `data/derived/same_context_matrix_pairs_zl3b.csv`;
- `docs/rota_5_pares_comparaveis.md`.

Resultado curto:

- grupos comparaveis encontrados: 725;
- grupos com anotacao visual direta: 11;
- cobertura de eixo: `rl=327`, `ao+rl=219`, `ao=179`;
- familias mais frequentes: `standalone=217`, `ch=183`, `d=93`, `ok=50`, `ot=49`, `sh=46`, `qok=32`.

Leitura: a matriz continua gerando pares locais suficientes para teste. Mas a parte visual ainda e o gargalo: so 11 grupos comparaveis ja estao ligados a anotacao visual direta.

## Rota 6: conferencia fina dos grupos anotados

Objetivo: sair de "folio/locus identificado" para "palavra exata isolada no glifo/imagem" nos grupos mais informativos.

Status: primeira rodada concluida em `docs/rota_6_conferencia_glifos.md`.

Saidas:

- `scripts/prepare_glyph_review_queue.py`;
- `data/annotations/glyph_review_queue_zl3b.csv`;
- `docs/rota_6_conferencia_glifos.md`.

Resultado curto:

- grupos na fila: 11;
- status de isolamento: `needs_exact_glyph_isolation=11`;
- folios envolvidos: `f67r1=5`, `f70v2=3`, `f84r=2`, `f68r3=1`;
- imagens envolvidas: `commons_f67r1_r2.jpg`, `commons_f70v2.jpg`, `commons_f84r.jpg`, `commons_f68r1_r2_r3.jpg`.

Leitura: a evidencia visual ainda esta em nivel de camada/folio, nao de palavra isolada. Nenhum eixo recebeu significado novo.

## Rota 7: recortes e coordenadas aproximadas

Objetivo: criar evidencia visual revisavel para os 11 itens da Rota 6.

Status: primeira rodada concluida em `docs/rota_7_recortes_revisao.md`.

Saidas:

- `scripts/prepare_review_crops.py`;
- `data/annotations/review_crop_manifest_zl3b.csv`;
- `docs/rota_7_recortes_revisao.md`;
- `images/derived/review_crops/*.svg`.

Resultado curto:

- recortes SVG gerados: 11;
- escopo preservado: `rough_region_only=11`;
- status preservado: `needs_exact_glyph_isolation=11`;
- nenhum JPG original foi alterado.

Leitura: a revisao visual agora tem artefatos reproduziveis por `review_id`/`crop_id`, mas os recortes continuam aproximados.

## Rota 8: revisar recortes e melhorar coordenadas

Objetivo: transformar recorte aproximado em coordenada mais fina ou confirmar que a palavra exata segue nao isolada.

Status: primeira rodada concluida em `docs/rota_8_revisao_recortes.md`.

Saidas:

- `scripts/review_crop_decisions.py`;
- `data/annotations/crop_review_decisions_zl3b.csv`;
- `docs/rota_8_revisao_recortes.md`.

Resultado curto:

- recortes avaliados: 11;
- SVGs validos: 11;
- decisoes `keep_not_isolated`: 11;
- decisoes com tokens faltantes: 8;
- nenhum glifo recebeu coordenada confirmada.

Leitura: os recortes sao bons como regioes revisaveis, mas ainda nao bastam como prova de palavra exata.

## Rota 9: revisao manual assistida dos SVGs

Objetivo: tentar coordenadas mais apertadas dentro dos recortes, mas registrar falha explicitamente quando a palavra exata nao aparecer.

Status: primeira rodada concluida em `docs/rota_9_revisao_manual.md`.

Saidas:

- `scripts/prepare_manual_svg_review.py`;
- `data/annotations/manual_svg_review_zl3b.csv`;
- `docs/rota_9_revisao_manual.md`;
- `docs/rota_9_revisao_manual.html`.

Resultado curto:

- itens para revisar: 11;
- status inicial: `pending_manual_review=11`;
- familias na fila: `standalone=5`, `ch=3`, `ot=2`, `d=1`;
- campos de coordenada foram deixados vazios de proposito;
- prioridade: `ot`, depois `ch/d`, depois `standalone`.

Leitura: a etapa esta pronta para intervencao visual manual; nenhum campo vazio deve ser interpretado como confirmacao.

## Rota 10: consolidar revisoes manuais preenchidas

Objetivo: quando a folha Rota 9 for preenchida, consolidar `confirmed_tighter_region`, `keep_not_isolated` e `unusable_crop`.

Status: primeira rodada concluida em `docs/rota_10_consolidacao_manual.md`.

Saidas:

- `scripts/consolidate_manual_svg_review.py`;
- `data/derived/manual_svg_review_consolidated_zl3b.csv`;
- `data/derived/manual_review_status_summary_zl3b.csv`;
- `docs/rota_10_consolidacao_manual.md`.

Resultado curto:

- itens consolidados: 11;
- status consolidado: `pending_manual_review=11`;
- status de coordenada: `no_manual_coordinates=11`;
- evidencia visual: `no_glyph_confirmation=11`;
- elegiveis para teste visual dos eixos: 0.

Leitura: a folha manual ainda nao gerou evidencia de coordenada/glifo. Nenhum item deve entrar em teste fino de `a/o` ou `r/l`.

## Rota 11: segunda passada de recortes melhores

Objetivo: produzir uma fila mais objetiva para novos recortes ou revisao visual guiada, priorizando itens sem coordenada e com tokens faltantes.

Status: primeira rodada concluida em `docs/rota_11_segunda_passada_recortes.md`.

Saidas:

- `scripts/prepare_second_pass_crop_queue.py`;
- `data/annotations/second_pass_crop_queue_zl3b.csv`;
- `data/derived/second_pass_crop_queue_summary_zl3b.csv`;
- `docs/rota_11_segunda_passada_recortes.md`.

Resultado curto:

- itens na fila: 11;
- tokens faltantes a procurar: 14;
- foco em tokens faltantes: 8;
- foco em apertar regiao existente: 3;
- prioridades: `P0=2`, `P1=4`, `P2=2`, `P3=3`.

Leitura: a fila prioriza operacao de revisao, nao importancia semantica. A guarda `no_axis_meaning_from_queue_position` foi aplicada a todos os itens.

## Rota 12: pacotes por folio para revisao guiada

Objetivo: agrupar a fila Rota 11 por folio/imagem e gerar instrucoes de revisao visual por pagina.

Status: primeira rodada concluida em `docs/rota_12_pacotes_revisao_guiada.md`.

Saidas:

- `scripts/prepare_folio_review_packets.py`;
- `data/annotations/folio_review_packets_zl3b.csv`;
- `data/annotations/folio_review_packet_items_zl3b.csv`;
- `data/derived/folio_review_packet_summary_zl3b.csv`;
- `docs/rota_12_pacotes_revisao_guiada.md`.

Resultado curto:

- pacotes por folio/imagem: 4;
- itens preservados nos pacotes: 11;
- tokens faltantes agregados: 14;
- objetivos: `review_source_image_first=3`, `search_tokens_then_redraw_crop=1`;
- folios: `f67r1`, `f68r3`, `f70v2`, `f84r`.

Leitura: os pacotes tornam a revisao operacional por pagina, mas continuam sem valor semantico para os eixos.

## Rota 13: checklist item-a-item por pacote

Objetivo: transformar cada pacote Rota 12 em uma folha de acao item-a-item, com campos para registrar se o token foi visto, se precisa de novo recorte ou se deve ser suspenso.

Status: primeira rodada concluida em `docs/rota_13_checklist_pacotes.md`.

Saidas:

- `scripts/prepare_packet_item_checklist.py`;
- `data/annotations/packet_item_checklist_zl3b.csv`;
- `data/derived/packet_item_checklist_summary_zl3b.csv`;
- `docs/rota_13_checklist_pacotes.md`.

Resultado curto:

- itens na checklist: 11;
- alvo `missing_group_tokens`: 8;
- alvo `matched_group_tokens`: 3;
- status inicial: `pending_visual_check=11`;
- todos os campos manuais ficam vazios ate revisao visual real.

Leitura: a checklist e uma folha de acao. Ela ainda nao confirma token, recorte novo, glifo ou significado de eixo.

## Rota 14: consolidar checklist preenchida

Objetivo: depois de preencher a checklist Rota 13, consolidar `token_seen`, `new_crop_needed`, `image_insufficient` e coordenadas novas sem transformar decisao operacional em semantica.

Status: primeira rodada concluida em `docs/rota_14_consolidacao_checklist.md`.

Saidas:

- `scripts/consolidate_packet_item_checklist.py`;
- `data/derived/packet_item_checklist_consolidated_zl3b.csv`;
- `data/derived/packet_item_checklist_consolidation_summary_zl3b.csv`;
- `docs/rota_14_consolidacao_checklist.md`.

Resultado curto:

- itens consolidados: 11;
- status: `pending_visual_check=11`;
- coordenadas novas: `no_new_crop_coordinates=11`;
- evidencia visual: `no_new_visual_evidence=11`;
- elegiveis apos geracao de recorte: 0.

Leitura: a checklist ainda esta vazia. Nenhuma linha confirma token, novo recorte ou significado de eixo.

## Rota 15: instrucoes humanas por pacote

Objetivo: gerar instrucoes legiveis por pacote/folio para orientar a revisao manual das imagens, sem alterar a checklist automaticamente.

Status: primeira rodada concluida em `docs/rota_15_instrucoes_revisao_humana.md`.

Saidas:

- `scripts/prepare_human_review_instructions.py`;
- `data/annotations/human_review_instructions_zl3b.csv`;
- `data/annotations/human_review_instruction_items_zl3b.csv`;
- `data/derived/human_review_instruction_summary_zl3b.csv`;
- `docs/rota_15_instrucoes_revisao_humana.md`.

Resultado curto:

- pacotes instruidos: 4;
- itens instruidos: 11;
- modos: `open_source_image_before_svg=3`, `search_tokens_then_redraw_crop=1`;
- campos manuais nao foram preenchidos automaticamente;
- guarda: `human_instruction_not_visual_evidence`.

Leitura: as instrucoes guiam a revisao humana por imagem/pacote. Elas nao confirmam token, nao criam recorte novo e nao atribuem significado aos eixos `a/o` ou `r/l`.

## Rota 16: consolidar revisao humana preenchida

Objetivo: depois de preencher a checklist/instrucoes, consolidar `manual_token_seen`, `manual_new_crop_needed`, `manual_image_insufficient` e coordenadas novas em categorias de evidencia visual.

Status: primeira rodada concluida em `docs/rota_16_consolidacao_revisao_humana.md`.

Saidas:

- `scripts/consolidate_human_review_evidence.py`;
- `data/derived/human_review_evidence_consolidated_zl3b.csv`;
- `data/derived/human_review_evidence_summary_zl3b.csv`;
- `docs/rota_16_consolidacao_revisao_humana.md`.

Resultado curto:

- itens consolidados: 11;
- pendentes de revisao humana: 11;
- prontos para novo recorte apos revisao: 0;
- evidencia visual nova: 0;
- guarda: `human_review_evidence_not_axis_meaning`.

Leitura: a consolidacao cruzou Rota 15 com a checklist Rota 13 e confirmou que ainda nao ha resposta humana preenchida. Nenhum item pode seguir para teste fino dos eixos.

## Rota 17: revisao humana efetiva dos P0/P1

Objetivo: executar a revisao visual real dos itens pendentes, comecando por P0 e P1, e preencher os campos manuais da checklist.

Status: lote P0/P1 preparado em `docs/rota_17_revisao_humana_p0_p1.md`.

Saidas:

- `scripts/prepare_priority_human_review.py`;
- `data/annotations/priority_human_review_p0_p1_zl3b.csv`;
- `data/derived/priority_human_review_summary_zl3b.csv`;
- `docs/rota_17_revisao_humana_p0_p1.md`.

Resultado curto:

- itens P0/P1 na fila: 6;
- P0: 2;
- P1: 4;
- folios: `f67r1=3`, `f70v2=2`, `f68r3=1`;
- campos manuais permanecem vazios ate revisao visual real;
- guarda: `priority_review_not_visual_evidence`.

Leitura: a Rota 17 criou a fila executavel de revisao prioritária. Ela nao preenche `manual_token_seen` nem cria evidencia; o preenchimento deve acontecer na checklist.

## Rota 18: ingerir decisoes P0/P1 preenchidas

Objetivo: depois da revisao visual dos 6 itens P0/P1, ingerir os campos preenchidos e separar itens com token visto, nao visto, incerto, imagem insuficiente e coordenadas prontas para novo recorte.

Status: primeira rodada concluida em `docs/rota_18_ingestao_decisoes_p0_p1.md`.

Saidas:

- `scripts/ingest_priority_human_decisions.py`;
- `data/derived/priority_human_decisions_p0_p1_zl3b.csv`;
- `data/derived/priority_human_decisions_summary_zl3b.csv`;
- `docs/rota_18_ingestao_decisoes_p0_p1.md`.

Resultado curto:

- itens P0/P1 ingeridos: 6;
- pendentes: 6;
- candidatos a novo recorte: 0;
- prontidao para eixo: `not_ready=6`;
- guarda: `priority_decision_not_axis_meaning`.

Leitura: a ingestao confirmou que as decisoes P0/P1 ainda nao foram preenchidas na checklist. Nenhum item passou para geracao de recorte ou teste dos eixos.

## Rota 19: preencher decisoes P0/P1 ou criar pacote visual direto

Objetivo: produzir a menor superficie possivel para preencher os 6 itens P0/P1 na checklist, com foco em imagem fonte, SVG de referencia, alvo e campos manuais.

Status: pacote visual direto gerado em `docs/rota_19_pacote_visual_direto_p0_p1.md` e `docs/rota_19_pacote_visual_direto_p0_p1.html`.

Saidas:

- `scripts/prepare_direct_visual_decision_package.py`;
- `data/annotations/direct_visual_decision_package_p0_p1_zl3b.csv`;
- `data/derived/direct_visual_decision_package_summary_zl3b.csv`;
- `docs/rota_19_pacote_visual_direto_p0_p1.md`;
- `docs/rota_19_pacote_visual_direto_p0_p1.html`.

Resultado curto:

- itens no pacote visual: 6;
- P0: 2;
- P1: 4;
- folios: `f67r1=3`, `f70v2=2`, `f68r3=1`;
- campos manuais permanecem em branco;
- guarda: `direct_visual_package_not_evidence`.

Leitura: a Rota 19 reduziu a friccao visual com um pacote HTML lado a lado. O pacote continua sendo superficie de trabalho, nao evidencia.

## Rota 20: aplicar decisoes preenchidas do pacote visual

Objetivo: quando o CSV/HTML da Rota 19 for usado para revisar os itens, copiar as decisoes preenchidas para a checklist e reexecutar a ingestao P0/P1.

Status: primeira rodada concluida em `docs/rota_20_aplicacao_decisoes_pacote_visual.md`.

Saidas:

- `scripts/apply_direct_visual_decisions.py`;
- `data/derived/packet_item_checklist_after_direct_visual_p0_p1_zl3b.csv`;
- `data/derived/direct_visual_decision_application_log_zl3b.csv`;
- `data/derived/direct_visual_decision_application_summary_zl3b.csv`;
- `docs/rota_20_aplicacao_decisoes_pacote_visual.md`.

Resultado curto:

- linhas no pacote: 6;
- valores aplicados: 0;
- ignoradas por campos vazios: 6;
- checklist original nao foi sobrescrita;
- guarda: `applied_values_are_manual_not_axis_meaning`.

Leitura: o pacote visual ainda nao foi preenchido. A aplicacao produziu uma checklist derivada sem mudancas manuais e registrou a pendencia.

## Rota 21: planilha de preenchimento visual P0/P1

Objetivo: transformar os 6 itens P0/P1 ainda vazios em uma planilha pequena, com valores permitidos explícitos, sem preencher nada por inferência.

Status: primeira rodada concluida em `docs/rota_21_planilha_preenchimento_visual_p0_p1.md`.

Saidas:

- `scripts/prepare_visual_decision_entry_sheet.py`;
- `data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv`;
- `data/derived/visual_decision_entry_sheet_summary_zl3b.csv`;
- `docs/rota_21_planilha_preenchimento_visual_p0_p1.md`.

Resultado curto:

- linhas para preencher: 6;
- P0: 2;
- P1: 4;
- folios: `f67r1=3`, `f70v2=2`, `f68r3=1`;
- status: `awaiting_manual_entry=6`;
- guarda: `entry_sheet_not_visual_evidence`.

Leitura: a planilha R21 e a menor superficie de entrada manual. Ela especifica `yes/no/uncertain` para `manual_token_seen`, `yes/no` para os campos de novo recorte e imagem insuficiente, mas nao cria evidencia visual.

## Rota 22: validar e aplicar a planilha R21 preenchida

Objetivo: depois do preenchimento humano, validar os valores da planilha R21 e aplicar somente entradas explícitas ao pacote visual/checklist derivada.

Status: primeira rodada concluida em `docs/rota_22_validacao_planilha_visual.md`.

Saidas:

- `scripts/validate_visual_decision_entry_sheet.py`;
- `data/derived/direct_visual_package_after_entry_sheet_p0_p1_zl3b.csv`;
- `data/derived/visual_decision_entry_validation_log_zl3b.csv`;
- `data/derived/visual_decision_entry_validation_summary_zl3b.csv`;
- `docs/rota_22_validacao_planilha_visual.md`.

Resultado curto:

- linhas validadas: 6;
- entradas validas: 0;
- entradas pendentes: 6;
- entradas invalidas: 0;
- status de aplicacao: `skipped_blank_manual_entry=6`;
- guarda: `validated_values_are_manual_not_axis_meaning`.

Leitura: a planilha R21 segue sem preenchimento humano. A Rota 22 deixou a validacao pronta e gerou um pacote visual derivado sem aplicar valores inventados.

## Rota 23: pacote HTML guiado para preencher R21

Objetivo: reduzir a friccao humana restante com uma superficie HTML que mostre imagem, SVG, campos permitidos e linha CSV alvo para cada uma das 6 pendencias.

Status: primeira rodada concluida em `docs/rota_23_pacote_html_preenchimento_r21.md` e `docs/rota_23_pacote_html_preenchimento_r21.html`.

Saidas:

- `scripts/prepare_guided_visual_entry_html.py`;
- `data/derived/guided_visual_entry_html_manifest_zl3b.csv`;
- `data/derived/guided_visual_entry_html_summary_zl3b.csv`;
- `docs/rota_23_pacote_html_preenchimento_r21.md`;
- `docs/rota_23_pacote_html_preenchimento_r21.html`.

Resultado curto:

- cartoes HTML gerados: 6;
- P0: 2;
- P1: 4;
- status: `ready_for_guided_manual_entry=6`;
- guarda: `guided_html_not_visual_evidence`.

Leitura: o HTML R23 deixa a revisao visual pronta, mas nao grava decisoes. O preenchimento verdadeiro continua sendo manual no CSV R21.

## Rota 24: prontidao para preenchimento visual R21

Objetivo: verificar se os assets e o HTML guiado da Rota 23 estao prontos para preencher explicitamente a planilha R21.

Status: primeira rodada concluida em `docs/rota_24_prontidao_preenchimento_visual.md`.

Saidas:

- `scripts/verify_guided_visual_entry_readiness.py`;
- `data/derived/guided_visual_entry_readiness_zl3b.csv`;
- `data/derived/guided_visual_entry_readiness_summary_zl3b.csv`;
- `docs/rota_24_prontidao_preenchimento_visual.md`.

Resultado curto:

- itens verificados: 6;
- prontos para preenchimento manual: 6;
- ja preenchidos: 0;
- bloqueados por asset: 0;
- bloqueados por HTML: 0;
- guarda: `readiness_check_not_visual_evidence`.

Leitura: o pacote visual esta operacionalmente pronto. A planilha R21 segue vazia; nenhuma decisao visual foi tomada.

## Rota 25: preencher R21 usando o HTML guiado

Objetivo: usar o pacote HTML R23 para preencher explicitamente a planilha R21 e entao reexecutar a validacao da Rota 22.

Status: gate manual pendente. A Rota 24 confirmou que o material esta pronto, mas a planilha R21 segue sem decisao humana.

- preservar cada `route21_id`, `route19_id`, `checklist_id`, `manual_review_id` e `crop_id`;
- preencher somente `manual_token_seen`, `manual_new_crop_needed`, `manual_image_insufficient`, coordenadas de novo recorte e notas;
- usar `yes/no/uncertain` e `yes/no` exatamente como definidos;
- manter campo vazio quando nao houver decisao visual;
- reexecutar `scripts/validate_visual_decision_entry_sheet.py` depois do preenchimento.

Leitura: esta rota nao deve ser automatizada por inferencia. Enquanto a R21 nao for preenchida manualmente, o caminho automatizavel segue por tabelas textuais/visuais independentes.

## Rota 26: tabela ampliada das formas exatas ok/ot

Objetivo: cruzar cada forma `okar/okal/okor/okol/otar/otal/otor/otol` com folio, secao/nota, tipo de locus, posicao na linha, vizinhos textuais e objeto visual proximo quando houver anotacao.

Status: primeira rodada concluida em `docs/rota_26_tabela_contexto_formas_exatas.md`.

Saidas:

- `scripts/build_exact_form_context_table.py`;
- `data/derived/exact_form_context_table_zl3b.csv`;
- `data/derived/exact_form_context_summary_zl3b.csv`;
- `docs/rota_26_tabela_contexto_formas_exatas.md`.

Resultado curto:

- ocorrencias exatas: 786;
- `ok*`: 394;
- `ot*`: 392;
- formas mais comuns: `okal=152`, `otar=147`, `okar=133`, `otal=129`;
- com anotacao visual exata: 23;
- sem anotacao visual exata: 763;
- guarda: `exact_form_context_not_decipherment`.

Leitura: `ok*` e `ot*` estao quase equilibrados nas oito formas exatas. A cobertura visual ainda e pequena, entao as lacunas nao devem ser lidas como evidencia negativa.

## Rota 27: priorizar lacunas visuais das formas exatas

Objetivo: a partir da Rota 26, criar uma fila pequena de folios/loci onde as formas exatas ainda nao tem anotacao visual, priorizando concentracoes por folio e tipo de locus.

Status: primeira rodada concluida em `docs/rota_27_fila_lacunas_visuais_formas_exatas.md`.

Saidas:

- `scripts/prepare_exact_form_visual_gap_queue.py`;
- `data/derived/exact_form_visual_gap_queue_zl3b.csv`;
- `data/derived/exact_form_visual_gap_summary_zl3b.csv`;
- `docs/rota_27_fila_lacunas_visuais_formas_exatas.md`.

Resultado curto:

- grupos de lacuna visual: 195;
- `P0=1`;
- `P1=25`;
- `P2=7`;
- `P3=162`;
- com imagem no manifesto: 15;
- sem imagem no manifesto: 180;
- guarda: `visual_gap_priority_not_evidence`.

Leitura: a fila ordena trabalho visual, nao evidencia. O primeiro item acionavel com imagem pronta e `f99v/P`; varios P1 densos ainda exigem localizar ou baixar imagem antes da anotacao.

## Rota 28: pacote de anotacao visual para lacunas P0/P1 da Rota 27

Objetivo: transformar a fila R27 em um pacote revisavel, separando folios com imagem pronta dos folios que primeiro exigem fonte de imagem, sem preencher evidencia visual por inferencia.

Status: primeira rodada concluida em `docs/rota_28_pacote_anotacao_visual_formas_exatas.md`.

Saidas:

- `scripts/prepare_exact_form_visual_annotation_package.py`;
- `data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`;
- `data/derived/exact_form_visual_annotation_package_summary_zl3b.csv`;
- `docs/rota_28_pacote_anotacao_visual_formas_exatas.md`;
- `docs/rota_28_pacote_anotacao_visual_formas_exatas.html`.

Resultado curto:

- itens no pacote: 26;
- `P0=1`;
- `P1=25`;
- prontos para anotacao manual: 8;
- bloqueados por falta de imagem: 18;
- guarda: `visual_annotation_package_not_evidence`.

Leitura: a Rota 28 e um pacote operacional. Os 8 itens prontos ainda exigem anotacao humana; os 18 bloqueados precisam de fonte de imagem antes de qualquer revisao visual.

## Rota 29: resolver fontes de imagem ausentes da Rota 28

Objetivo: criar uma fila de busca/download para os 18 itens `blocked_pending_source_image`, atualizar o manifesto de imagens quando houver fonte publica adequada e reexecutar a Rota 28 sem inferir anotacoes visuais.

Status: primeira rodada concluida em `docs/rota_29_fila_fontes_imagem_formas_exatas.md`.

Saidas:

- `scripts/prepare_missing_source_image_queue.py`;
- `data/annotations/exact_form_missing_source_queue_p0_p1_zl3b.csv`;
- `data/derived/exact_form_missing_source_summary_zl3b.csv`;
- `docs/rota_29_fila_fontes_imagem_formas_exatas.md`;
- `docs/rota_29_fila_fontes_imagem_formas_exatas.html`.

Resultado curto:

- fontes pendentes: 18;
- `P1=18`;
- locus `P=17`;
- locus `C=1`;
- status: `pending_public_source_verification`;
- acao de manifesto: `do_not_update_manifest_until_url_verified`;
- guarda: `missing_source_queue_not_visual_evidence`.

Leitura: a fila so cria consultas e campos candidatos. `candidate_commons_page` e `candidate_image_url` continuam vazios ate verificacao humana ou checagem explicita de fonte publica.

## Rota 30: validar fontes candidatas e aplicar ao manifesto

Objetivo: depois que a Rota 29 receber URLs candidatas verificadas, validar formato/fonte publica, atualizar `data/commons_image_sources.csv` em uma copia controlada e reexecutar Rota 27/28 sem criar anotacao visual automaticamente.

Status: primeira rodada concluida em `docs/rota_30_validacao_fontes_candidatas.md`.

Saidas:

- `scripts/validate_missing_source_candidates.py`;
- `data/derived/missing_source_candidate_validation_zl3b.csv`;
- `data/derived/missing_source_candidate_validation_summary_zl3b.csv`;
- `data/derived/commons_image_sources_after_source_validation_zl3b.csv`;
- `docs/rota_30_validacao_fontes_candidatas.md`.

Resultado curto:

- candidatos avaliados: 18;
- pendentes vazios: 18;
- validos estruturalmente: 0;
- invalidos: 0;
- linhas anexadas ao manifesto derivado: 0;
- manifesto original nao recebeu novas fontes;
- guarda: `source_validation_not_visual_evidence`.

Leitura: a validacao esta pronta, mas a Rota 29 ainda nao contem URLs candidatas. A copia derivada do manifesto permanece com as mesmas 10 linhas do manifesto original.

## Rota 31: validar anotacoes visuais manuais do pacote R28

Objetivo: depois que os 8 itens `ready_for_manual_visual_annotation` da Rota 28 receberem anotacao humana, validar somente valores preenchidos e gerar uma tabela derivada sem alterar a semente visual original por inferencia.

Status: primeira rodada concluida em `docs/rota_31_validacao_anotacoes_visuais_prontas.md`.

Saidas:

- `scripts/validate_ready_visual_annotations.py`;
- `data/derived/ready_visual_annotation_validation_zl3b.csv`;
- `data/derived/ready_manual_visual_annotations_zl3b.csv`;
- `data/derived/ready_visual_annotation_validation_summary_zl3b.csv`;
- `docs/rota_31_validacao_anotacoes_visuais_prontas.md`.

Resultado curto:

- itens prontos avaliados: 8;
- pendentes vazios: 8;
- validos: 0;
- invalidos: 0;
- anotacoes derivadas gravadas: 0;
- guarda: `manual_visual_annotation_not_axis_meaning`.

Leitura: a validacao esta pronta, mas o pacote R28 ainda nao contem anotacoes manuais. Campos vazios continuam pendentes, nao rejeicao.

## Rota 32: pacote HTML focado para anotar os 8 itens prontos

Objetivo: gerar uma superficie HTML/CSV pequena para preencher explicitamente `manual_annotation_status` e `manual_visual_notes` nos 8 itens `ready_for_manual_visual_annotation` da Rota 28, sem alterar a validacao R31 por inferencia.

Status: primeira rodada concluida em `docs/rota_32_pacote_html_anotacao_visual_prontos.md`.

Saidas:

- `scripts/prepare_ready_visual_annotation_html.py`;
- `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`;
- `data/derived/ready_visual_annotation_html_summary_zl3b.csv`;
- `docs/rota_32_pacote_html_anotacao_visual_prontos.md`;
- `docs/rota_32_pacote_html_anotacao_visual_prontos.html`.

Resultado curto:

- cartoes HTML: 8;
- pendentes R31: 8;
- `P0=1`;
- `P1=7`;
- locus `P=6`;
- locus `L=2`;
- campos manuais permanecem em branco;
- valores permitidos: `annotated/not_visible/uncertain`;
- guarda: `focused_visual_annotation_html_not_evidence`.

Leitura: a rota reduz a friccao da anotacao humana sem criar evidencia. O HTML mostra imagens do manifesto e campos permitidos; a planilha R32 ainda precisa de preenchimento manual e depois deve ser copiada de volta ao pacote R28 para reexecutar R31.

## Rota 33: aplicar entradas manuais R32 ao pacote R28

Objetivo: depois que `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv` receber preenchimento humano, aplicar somente campos explicitos ao pacote R28 derivado e reexecutar a validacao R31, mantendo campos vazios como pendentes.

Status: primeira rodada concluida em `docs/rota_33_aplicacao_entradas_visuais_r32.md`.

Saidas:

- `scripts/apply_ready_visual_annotation_entries.py`;
- `data/derived/exact_form_visual_annotation_package_after_ready_entries_zl3b.csv`;
- `data/derived/ready_visual_annotation_entry_application_log_zl3b.csv`;
- `data/derived/ready_visual_annotation_entry_application_summary_zl3b.csv`;
- `docs/rota_33_aplicacao_entradas_visuais_r32.md`.

Resultado curto:

- entradas R32 avaliadas: 8;
- pendentes vazias: 8;
- validas: 0;
- invalidas: 0;
- linhas atualizadas no pacote derivado: 0;
- pacote R28 original nao foi alterado;
- guarda: `ready_visual_entry_application_not_visual_evidence`.

Leitura: a infraestrutura de aplicacao esta pronta. Como a planilha R32 ainda nao recebeu anotacao humana, o pacote derivado preserva os campos manuais em branco.

## Rota 34: gate manual de anotacao visual R32

Objetivo: preencher manualmente `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv` usando `docs/rota_32_pacote_html_anotacao_visual_prontos.html`, com valores permitidos e notas explicitas, antes de reexecutar R33 e R31.

Status: primeira rodada concluida em `docs/rota_34_gate_manual_anotacao_visual_r32.md`.

Saidas:

- `scripts/verify_ready_visual_annotation_manual_gate.py`;
- `data/derived/ready_visual_annotation_manual_gate_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_gate_summary_zl3b.csv`;
- `docs/rota_34_gate_manual_anotacao_visual_r32.md`.

Resultado curto:

- itens verificados: 8;
- bloqueados por anotacao manual pendente: 8;
- prontos para reexecutar R33/R31: 0;
- cartoes HTML presentes: 8;
- valores permitidos presentes no HTML: 8;
- guarda: `manual_visual_gate_not_evidence`.

Leitura: o material operacional esta pronto, mas a planilha R32 ainda nao tem anotacao humana. O estudo nao deve seguir para nova evidencia visual ate que `manual_annotation_status` e `manual_visual_notes` sejam preenchidos.

## Rota 35: reexecutar R33 e R31 apos preenchimento humano R32

Objetivo: quando a Rota 34 apontar itens `ready_to_rerun_r33_r31`, reexecutar a aplicacao R33 sobre o pacote derivado e validar as anotacoes com R31, registrando somente entradas manuais validas.

Status: primeira rodada concluida como plano pos-gate em `docs/rota_35_plano_reexecucao_pos_gate_r32.md`.

Saidas:

- `scripts/plan_ready_visual_annotation_post_gate_rerun.py`;
- `data/derived/ready_visual_annotation_post_gate_rerun_plan_zl3b.csv`;
- `data/derived/ready_visual_annotation_post_gate_rerun_summary_zl3b.csv`;
- `docs/rota_35_plano_reexecucao_pos_gate_r32.md`.

Resultado curto:

- itens avaliados: 8;
- bloqueados pelo gate manual: 8;
- prontos para reexecucao controlada: 0;
- reexecucoes R33/R31 planejadas agora: 0;
- guarda: `post_gate_rerun_not_visual_evidence`.

Leitura: a rota confirma que nao ha reexecucao responsavel de R33/R31 enquanto a planilha R32 estiver vazia. O proximo passo permanece preencher R32 manualmente e reexecutar R34.

## Rota 36: preenchimento humano efetivo da planilha R32

Objetivo: inserir decisoes humanas explicitas em `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv`, uma linha por vez, com `manual_annotation_status=annotated/not_visible/uncertain` e `manual_visual_notes` obrigatorio, usando o HTML R32 como apoio.

Status: primeira rodada concluida como protocolo de preenchimento em `docs/rota_36_protocolo_preenchimento_humano_r32.md`.

Saidas:

- `scripts/prepare_ready_visual_annotation_manual_fill_protocol.py`;
- `data/derived/ready_visual_annotation_manual_fill_protocol_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_fill_protocol_summary_zl3b.csv`;
- `docs/rota_36_protocolo_preenchimento_humano_r32.md`.

Resultado curto:

- itens no protocolo: 8;
- aguardando anotacao humana: 8;
- entradas prontas para reexecutar gate: 0;
- entradas invalidas: 0;
- planilha R32 original preservada;
- guarda: `manual_fill_protocol_not_visual_evidence`.

Leitura: a rota prepara o preenchimento humano efetivo sem escrever decisoes automaticamente. A proxima mudanca de evidencia exige revisar o HTML R32 e preencher manualmente a planilha R32.

## Rota 37: revalidar R34/R35/R33/R31 apos preenchimento R32

Objetivo: depois que a planilha R32 receber entradas humanas, reexecutar R34, R35, R33 e R31 nessa ordem, aplicando somente valores validos e mantendo qualquer linha vazia como pendente.

Status: primeira rodada concluida como plano de revalidacao em `docs/rota_37_plano_revalidacao_r34_r35_r33_r31.md`.

Saidas:

- `scripts/plan_ready_visual_annotation_revalidation_chain.py`;
- `data/derived/ready_visual_annotation_revalidation_chain_plan_zl3b.csv`;
- `data/derived/ready_visual_annotation_revalidation_chain_summary_zl3b.csv`;
- `docs/rota_37_plano_revalidacao_r34_r35_r33_r31.md`.

Resultado curto:

- itens avaliados: 8;
- bloqueados sem entrada humana: 8;
- prontos para cadeia de revalidacao: 0;
- execucoes da cadeia planejadas agora: 0;
- ordem: `R34>R35>R33>R31`;
- guarda: `revalidation_chain_not_visual_evidence`.

Leitura: a cadeia de revalidacao esta definida, mas permanece parada enquanto R36 indicar `awaiting_human_visual_entry`.

## Rota 38: preencher R32 e reabrir a cadeia de revalidacao

Objetivo: realizar o preenchimento humano efetivo da planilha R32, usando o HTML R32 e o protocolo R36, para que R37 possa liberar a cadeia `R34>R35>R33>R31`.

Status: primeira rodada concluida como ordem de trabalho em `docs/rota_38_ordem_trabalho_preencher_r32_reabrir_cadeia.md`.

Saidas:

- `scripts/prepare_ready_visual_annotation_manual_reopen_work_order.py`;
- `data/derived/ready_visual_annotation_manual_reopen_work_order_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_reopen_work_order_summary_zl3b.csv`;
- `docs/rota_38_ordem_trabalho_preencher_r32_reabrir_cadeia.md`.

Resultado curto:

- itens na ordem de trabalho: 8;
- exigem preenchimento manual: 8;
- prontos para reabrir cadeia: 0;
- bloqueados por entrada invalida: 0;
- planilha R32 original preservada;
- guarda: `manual_reopen_work_order_not_visual_evidence`.

Leitura: a ordem de trabalho deixa o preenchimento humano operacional e rastreavel, mas nao substitui a revisao visual. A cadeia segue fechada ate que R32 receba valores humanos explicitos.

## Rota 39: auditar execucao do preenchimento humano R32

Objetivo: verificar se o preenchimento humano da ordem R38 foi executado na planilha R32, sem escrever decisoes, sem interpretar imagens e sem reabrir a cadeia por inferencia.

Status: primeira rodada concluida como auditoria em `docs/rota_39_auditoria_execucao_preenchimento_humano_r32.md`.

Saidas:

- `scripts/audit_ready_visual_annotation_manual_fill_execution.py`;
- `data/derived/ready_visual_annotation_manual_fill_execution_audit_zl3b.csv`;
- `data/derived/ready_visual_annotation_manual_fill_execution_audit_summary_zl3b.csv`;
- `docs/rota_39_auditoria_execucao_preenchimento_humano_r32.md`.

Resultado curto:

- itens auditados: 8;
- preenchimento humano nao executado: 8;
- prontos para reabrir cadeia: 0;
- entradas invalidas ou parciais: 0;
- planilha R32 original preservada;
- guarda: `manual_fill_execution_audit_not_visual_evidence`.

Leitura: a R39 confirma que a R32 ainda nao recebeu entradas humanas. A cadeia `R34>R35>R33>R31` segue fechada.

## Rota 40: preencher R32 com entrada humana e revalidar cadeia

Objetivo: depois que houver decisao visual humana explicita na R32, reexecutar R36, R37 e R39; somente se R39 liberar, rodar R34/R35/R33/R31.

Status: primeira rodada concluida como plano condicional em `docs/rota_40_plano_condicional_reabertura_cadeia_r39.md`.

Saidas:

- `scripts/plan_ready_visual_annotation_conditional_chain_reopen.py`;
- `data/derived/ready_visual_annotation_conditional_chain_reopen_plan_zl3b.csv`;
- `data/derived/ready_visual_annotation_conditional_chain_reopen_summary_zl3b.csv`;
- `docs/rota_40_plano_condicional_reabertura_cadeia_r39.md`.

Resultado curto:

- itens planejados: 8;
- bloqueados aguardando entrada humana: 8;
- prontos para rodar cadeia: 0;
- entradas invalidas: 0;
- acao planejada: `do_not_run_revalidation_chain`;
- guarda: `conditional_chain_reopen_plan_not_visual_evidence`.

Leitura: a cadeia continua fechada. A R40 apenas formaliza a regra de liberacao: rodar `R34>R35>R33>R31` somente quando R39 produzir `ready_to_reopen_chain`.

## Rota 41: executar entrada humana externa na R32

Objetivo: preencher manualmente `manual_annotation_status` e `manual_visual_notes` na R32 a partir do HTML R32 e da ordem R38. Esta rota exige revisao visual humana; o pipeline nao deve gerar esses valores.

Status: primeira rodada concluida como pacote de entrada humana externa em `docs/rota_41_pacote_entrada_humana_externa_r32.md`.

Saidas:

- `scripts/prepare_ready_visual_annotation_external_human_entry_packet.py`;
- `data/derived/ready_visual_annotation_external_human_entry_packet_zl3b.csv`;
- `data/derived/ready_visual_annotation_external_human_entry_summary_zl3b.csv`;
- `docs/rota_41_pacote_entrada_humana_externa_r32.md`.

Resultado curto:

- itens no pacote: 8;
- exigem entrada humana externa: 8;
- entradas humanas presentes: 0;
- entradas invalidas ou parciais: 0;
- planilha R32 original preservada;
- guarda: `external_human_entry_packet_not_visual_evidence`.

Leitura: a R41 transformou a pendencia em uma fila operacional para revisao humana externa. Ela nao substitui a revisao visual e nao libera a cadeia.

## Rota 42: baixar fontes Yale IIIF high-res para R32

Objetivo: substituir o apoio visual da R32 por imagens oficiais Yale/Beinecke em alta resolucao, sem preencher anotacoes e sem alterar decisoes manuais.

Status: primeira rodada concluida em `docs/rota_42_fontes_yale_iiif_highres_r32.md` e `docs/rota_42_pacote_html_yale_iiif_highres_r32.html`.

Saidas:

- `scripts/prepare_ready_visual_annotation_highres_source_packet.py`;
- `data/derived/yale_iiif_manifest_2002046.json`;
- `data/derived/ready_visual_annotation_highres_sources_zl3b.csv`;
- `data/derived/ready_visual_annotation_highres_sources_summary_zl3b.csv`;
- `docs/rota_42_fontes_yale_iiif_highres_r32.md`;
- `docs/rota_42_pacote_html_yale_iiif_highres_r32.html`;
- `images/raw/yale_iiif_r32/*.jpg`.

Resultado curto:

- itens avaliados: 8;
- matches no manifesto Yale: 8;
- downloads locais: 8;
- sem match: 0;
- dimensoes entre `2702x3765` e `9078x3777`;
- guarda: `highres_source_download_not_visual_evidence`.

Leitura: agora ha um HTML alternativo mais nitido para a revisao humana da R32. A rota nao muda evidencias nem libera a cadeia.

## Rota 42A: analise assistida das fontes Yale high-res

Objetivo: registrar uma leitura assistida das imagens Yale/Beinecke baixadas na R42 para orientar recorte, zoom e revisao humana, sem preencher a R32 e sem decidir `annotated/not_visible/uncertain`.

Status: concluida em `docs/rota_42a_analise_assistida_highres_r32.md`.

Saidas:

- `scripts/prepare_ready_visual_annotation_highres_ai_assist.py`;
- `data/derived/ready_visual_annotation_highres_ai_assist_zl3b.csv`;
- `data/derived/ready_visual_annotation_highres_ai_assist_summary_zl3b.csv`;
- `docs/rota_42a_analise_assistida_highres_r32.md`.

Resultado curto:

- itens avaliados: 8;
- regioes claramente localizaveis para recorte: 2;
- regioes parcialmente localizaveis: 4;
- paginas compostas que exigem recorte/lado: 2;
- decisoes exatas de token tomadas pela IA: 0;
- cadeia ainda bloqueada: 8;
- guarda: `ai_highres_visual_assist_not_human_evidence`.

Leitura: as fontes novas melhoram a revisao. `f84r` e `f99r` estao prontos para recortes locais mais objetivos; `f99v`, `f67r2` e `f67v1` precisam de alinhamento fino; `f1r` segue apagado; `f88v` e `f89r2` precisam de desambiguacao na pagina composta `88v and 89r`.

## Rota 42B: ferramenta guiada de preenchimento humano R32 high-res

Objetivo: criar uma pagina HTML de preenchimento manual com as imagens high-res, os campos `manual_annotation_status`/`manual_visual_notes`, ordenacao por facilidade, fila de revisao, controles de imagem, guia rapido, pergunta principal em linguagem simples, cartoes visuais EVA para as palavras-alvo, botoes `Achei`/`Nao achei`/`Nao sei`, nota automatica e rascunho CSV recolhido ate o fim, sem gravar a R32 automaticamente.

Status: concluida em `docs/rota_42b_preenchimento_humano_highres_r32.md` e `docs/rota_42b_pacote_html_preenchimento_humano_r32.html`.

Saidas:

- `scripts/prepare_ready_visual_annotation_highres_human_fill_html.py`;
- `tests/test_ready_visual_annotation_highres_human_fill_html.py`;
- `data/derived/ready_visual_annotation_highres_human_fill_html_zl3b.csv`;
- `data/derived/ready_visual_annotation_highres_human_fill_html_summary_zl3b.csv`;
- `docs/rota_42b_preenchimento_humano_highres_r32.md`;
- `docs/rota_42b_pacote_html_preenchimento_humano_r32.html`.

Resultado curto:

- itens de revisao guiada: 8;
- primeiro bloco claro: 2 (`f84r`, `f99r`);
- bloco intermediario parcial: 3;
- fonte apagada: 1;
- paginas compostas finais: 2;
- controles: item ativo, fila lateral, proximo pendente, zoom, contraste, rotacao, mostrar/esconder zonas, subir/descer zonas e reset de vista;
- modo ultrassimples: guia rapido, pergunta `Voce achou essas palavrinhas?`, cartoes visuais EVA, total de entradas/loci ZL3b por folio, lista auditavel dessas entradas, texto de referencia das linhas alvo, baselines calibradas quando R42C estiver preenchida, zonas visuais provaveis quando a linha ainda estiver pendente, botoes `Achei`/`Nao achei`/`Nao sei`, nota automatica e detalhes tecnicos recolhidos;
- observacao: as baselines R42C substituem a zona grande apenas como apoio operacional de localizacao; se uma baseline ainda nao existe, as zonas numeradas continuam aproximadas por bloco, nao linha exata, coordenada exata nem evidencia automatica; a ferramenta nao calcula posicao visual por proporcao da numeracao ZL3b; o total por folio segue entradas/loci ZL3b e nao e uma contagem visual direta da imagem; deslocamentos de zona sao temporarios para que recarregar a pagina volte ao mapa calibrado;
- guarda: `highres_human_fill_html_not_visual_evidence`.

Leitura: agora o usuario tem uma superficie mais parecida com uma ficha de preenchimento. O HTML gera um rascunho CSV, mas a aplicacao na R32 continua manual e auditavel. Depois da R42C, a R42B consome baselines calibradas e cai de volta para zonas provaveis quando a linha ainda esta pendente.

## Rota 42C: calibracao manual de linhas/baselines R32 high-res

Objetivo: criar uma ferramenta local para calibrar as linhas reais dos loci alvo da R42B, usando baselines manuais em vez de zonas grandes. A rota melhora a precisao visual de onde procurar, mas nao traduz, nao decide anotacao visual e nao preenche a R32.

Status: concluida em `docs/rota_42c_calibracao_linhas_baseline_r32.md` e `docs/rota_42c_calibrador_linhas_baseline_r32.html`.

Saidas:

- `scripts/prepare_ready_visual_line_calibration_tool.py`;
- `tests/test_ready_visual_line_calibration_tool.py`;
- `data/annotations/ready_visual_line_calibration_zl3b.csv`;
- `data/derived/ready_visual_line_calibration_summary_zl3b.csv`;
- `docs/rota_42c_calibracao_linhas_baseline_r32.md`;
- `docs/rota_42c_calibrador_linhas_baseline_r32.html`.

Resultado curto:

- linhas/loci alvo para calibrar: 19;
- status atual: 19 `pending_calibration`;
- rascunhos OpenCV ja mesclados: 2 `baseline_points` pendentes (`f84r.24,+P0` na linha visual 6, `f84r.29,+P0` na linha visual 14);
- interacao: selecionar locus, seguir `Guia rapido`, ver progresso/mira/coordenadas/ultimo clique, usar scroll natural para subir mesmo em zoom alto, usar `Topo da imagem` quando o zoom deslocar a visualizacao, clicar no comeco e no fim da linha real, usar `Ajuste fino` para mover a linha inteira ou uma ponta em passos pequenos, marcar `calibrated`/`uncertain`/`not_calibratable`;
- exportacao: botoes `Copiar CSV` e `Baixar CSV` para transferir o rascunho para a planilha de calibracao;
- navegacao: atalhos `Abrir R42B`, `Abrir sugestoes OpenCV` e `Abrir mapa OpenCV`;
- apoio OpenCV: quando a R42D gera sugestao inicial, a R42C mescla a baseline como rascunho pendente, registra o numero de linha visual candidata e `Acao OpenCV: prefill_pending_baseline`, mostra `Computador ja ajudou` com proximo passo humano e ainda exige confirmacao humana;
- maturidade do scan: o overlay SVG fica preso ao canvas real da imagem, cada item recebe assinatura deterministica do scan para rejeitar rascunho local defasado, e o botao `Resetar scan local` limpa rascunhos antigos do navegador;
- resiliencia: se `data/annotations/ready_visual_line_calibration_zl3b.csv` ja tiver baselines manuais, o script preserva os campos manuais ao rodar novamente; status `calibrated` sem pelo menos dois pontos validos volta para `pending_calibration`, inclusive se vier de CSV ou rascunho local antigo;
- guarda: `line_calibration_tool_not_visual_evidence`.

Leitura: a R42C cria um passo intermediario honesto entre zonas provaveis e linhas precisas. O proximo refinamento visual deve usar as baselines calibradas para substituir ou reduzir as zonas da R42B, sem transformar calibracao em evidencia sem preenchimento humano.

## Rota 42D: sugestoes OpenCV para calibracao inicial de linhas

Objetivo: usar OpenCV para detectar faixas de tinta/texto nas imagens high-res e gerar sugestoes iniciais de baseline para a R42C, sem decidir anotacao visual e sem marcar nada como calibrado automaticamente.

Status: concluida em `docs/rota_42d_sugestoes_opencv_linhas_r32.md` e `docs/rota_42d_sugestoes_opencv_linhas_r32.html`.

Saidas:

- `scripts/prepare_ready_visual_line_opencv_suggestions.py`;
- `tests/test_ready_visual_line_opencv_suggestions.py`;
- `data/derived/ready_visual_line_opencv_suggestions_zl3b.csv`;
- `data/derived/ready_visual_line_opencv_suggestions_summary_zl3b.csv`;
- `docs/rota_42d_sugestoes_opencv_linhas_r32.md`;
- `docs/rota_42d_sugestoes_opencv_linhas_r32.html`.

Resultado curto:

- alvos analisados: 19;
- sugestoes OpenCV prontas para confirmar: 2 (`f84r.24` como linha visual 6, `f84r.29` como linha visual 14), ambas como `prefill_pending_baseline` e confianca operacional `media`;
- faixas detectadas, mas ainda exigindo zona/bloco manual: 13 (`needs_manual_zone`);
- sem faixa confiavel detectada: 4 (`needs_better_scan_or_manual_line`);
- a R42C ja mescla as duas sugestoes confiaveis como `baseline_points` pendentes, sem promover para `calibrated`;
- guarda: `opencv_initial_line_suggestion_not_visual_evidence`.

Leitura: OpenCV agora resolve sozinho a parte mecanica segura: detectar faixas, numerar linhas visuais e pre-preencher rascunhos de baseline quando ja existe zona manual de bloco. Para os demais alvos, ele ainda precisa de uma zona humana antes de sugerir baseline especifica. A tela R42D deixa claro o que foi resolvido pela maquina e o que ainda depende de confirmacao humana.

## Rota 42E: mapa OpenCV de linhas visuais

Objetivo: contar e numerar linhas visuais detectadas por OpenCV nas imagens high-res, separando a numeracao visual da numeracao ZL3b.

Status: concluida em `docs/rota_42e_mapa_opencv_linhas_visuais_r32.md` e `docs/rota_42e_mapa_opencv_linhas_visuais_r32.html`.

Saidas:

- `scripts/prepare_ready_visual_line_opencv_map.py`;
- `tests/test_ready_visual_line_opencv_map.py`;
- `data/derived/ready_visual_line_opencv_map_zl3b.csv`;
- `data/derived/ready_visual_line_opencv_map_images_zl3b.csv`;
- `data/derived/ready_visual_line_opencv_map_summary_zl3b.csv`;
- `docs/rota_42e_mapa_opencv_linhas_visuais_r32.md`;
- `docs/rota_42e_mapa_opencv_linhas_visuais_r32.html`.

Resultado curto:

- imagens mapeadas: 8;
- linhas visuais agrupadas no mapa bruto: 52;
- f84r: 23 linhas visuais agrupadas no mapa bruto, contra 47 entradas/loci ZL3b de transcricao;
- exibicao: a R42E abre em modo focado nas zonas R32 conhecidas, desenha reguas finas em vez de caixas grandes e mantem o botao `Mapa bruto` para auditoria;
- navegacao: R42E aponta para R42B, R42C e R42D; R42B e R42C tambem apontam de volta para o mapa;
- guarda: `opencv_visual_line_map_not_word_evidence`.

Leitura: a R42E e o mapa visual de apoio. Ela ajuda a escolher a linha certa na R42C, mas nao confirma palavra, objeto, traducao ou evidencia visual.

## Rota 42F: escolha simples de linhas visuais sem zona

Objetivo: resolver os casos em que o OpenCV detectou linhas na imagem, mas ainda nao sabe qual linha visual corresponde ao locus ZL3b. A rota cria uma tela simples para escolher `Essa e a linha`, gerando zonas pequenas que a R42D pode consumir depois.

Status: concluida em `docs/rota_42f_escolha_linhas_visuais_sem_zona_r32.md` e `docs/rota_42f_escolha_linhas_visuais_sem_zona_r32.html`.

Saidas:

- `scripts/prepare_ready_visual_line_zone_choice_tool.py`;
- `tests/test_ready_visual_line_zone_choice_tool.py`;
- `data/annotations/ready_visual_line_zone_choice_zl3b.csv`;
- `data/derived/ready_visual_line_zone_choice_summary_zl3b.csv`;
- `docs/rota_42f_escolha_linhas_visuais_sem_zona_r32.md`;
- `docs/rota_42f_escolha_linhas_visuais_sem_zona_r32.html`.

Resultado curto:

- alvos que precisam escolher linha visual: 13;
- status atual: 13 `pending_zone_choice`;
- a pagina mostra as linhas visuais reais vindas da R42E, com caixas/zones percentuais derivadas do OpenCV, nao espacamento artificial;
- depois que uma linha visual for escolhida, a R42D consome `selected_zone_box_pct` como zona pequena e pode gerar uma baseline pendente para a R42C;
- guarda: `line_zone_choice_not_visual_evidence`.

Leitura: a R42F e o elo honesto entre o que o OpenCV consegue ver e o que ainda precisa de escolha humana. Ela nao traduz, nao preenche a R32 e nao transforma escolha de linha em evidencia final.

## Rota 42G: painel unico de ferramentas ativas R32

Objetivo: remover do caminho as ferramentas HTML antigas e deixar uma entrada unica para o fluxo atual R42B-L.

Status: concluida em `docs/rota_42g_ferramentas_ativas_r32.md` e `docs/rota_42g_ferramentas_ativas_r32.html`.

Saidas:

- `scripts/prepare_active_tool_dashboard.py`;
- `tests/test_active_tool_dashboard.py`;
- `docs/rota_42g_ferramentas_ativas_r32.md`;
- `docs/rota_42g_ferramentas_ativas_r32.html`.

Resultado curto:

- ferramentas HTML ativas: 10;
- ferramentas HTML antigas removidas: 8;
- o painel lista apenas R42G, R42K, R42L, R42M, R42F, R42D, R42J, R42C, R42B e R42E;
- as paginas ativas agora apontam para `Ferramentas ativas`;
- a limpeza e idempotente: reexecutar o script nao recria nem falha por arquivos antigos ja removidos.

Leitura: a R42G nao altera evidencia, traducao ou planilhas de anotacao. Ela reduz a superficie humana para o fluxo atual e evita voltar por acidente para ferramentas antigas.

## Rota 42H: renderizacao visual EVA nas ferramentas ativas

Objetivo: trocar a referencia textual EVA crua por desenhos SVG das palavras nas paginas humanas ativas, para que o usuario compare o formato visual com a imagem do manuscrito sem depender de strings como `okar,y`.

Status: concluida nos HTMLs ativos R42B, R42C e R42F, com helper compartilhado em `scripts/eva_visual.py`.

Saidas:

- `scripts/eva_visual.py`;
- `tests/test_eva_visual.py`;
- atualizacao de `scripts/prepare_ready_visual_annotation_highres_human_fill_html.py`;
- atualizacao de `scripts/prepare_ready_visual_line_calibration_tool.py`;
- atualizacao de `scripts/prepare_ready_visual_line_zone_choice_tool.py`;
- HTMLs regenerados de R42B, R42C, R42D, R42E, R42F e R42G.

Resultado curto:

- textos de referencia nas ferramentas humanas agora usam `eva-visual-line` e `eva-word`;
- tokens alvo ficam destacados como `is-target`;
- a R42B tambem renderiza a lista de entradas ZL3b como desenhos quando aberta;
- a R42C e a R42F mostram `Texto de referencia visual`;
- o texto cru permanece nos CSVs/dados tecnicos para auditoria, mas deixa de ser a forma principal de leitura na interface.

Leitura: a R42H melhora usabilidade, nao evidencia. O desenho SVG e guia de comparacao visual, nao transcricao nova, traducao ou confirmacao automatica.

## Rota 42I: recortes reais e lupas nas ferramentas ativas

Objetivo: diminuir a dificuldade de comparar texto/desenho EVA com o manuscrito, mostrando recortes reais da imagem original sempre que a ferramenta tiver uma zona, linha OpenCV ou baseline para usar.

Status: concluida nos HTMLs ativos R42B, R42C, R42D, R42E, R42F e no painel R42G, com helper compartilhado em `scripts/visual_crop.py`.

Saidas:

- `scripts/visual_crop.py`;
- `tests/test_visual_crop.py`;
- atualizacao de `scripts/prepare_ready_visual_annotation_highres_human_fill_html.py`;
- atualizacao de `scripts/prepare_ready_visual_line_calibration_tool.py`;
- atualizacao de `scripts/prepare_ready_visual_line_opencv_suggestions.py`;
- atualizacao de `scripts/prepare_ready_visual_line_opencv_map.py`;
- atualizacao de `scripts/prepare_ready_visual_line_zone_choice_tool.py`;
- atualizacao de `scripts/prepare_active_tool_dashboard.py`.

Resultado curto:

- R42B mostra `Recortes reais da pagina` antes da decisão final;
- R42C mostra `Lupa da linha`, derivada dos pontos atuais ou da sugestão OpenCV;
- R42D mostra recorte real da linha sugerida quando existe `suggested_band_box_pct`;
- R42E lista recortes reais das linhas detectadas;
- R42F transforma cada linha candidata em um botão com recorte real clicável;
- R42G orienta o fluxo pelo novo modo de recortes;
- os recortes são desenhados no navegador por canvas a partir da imagem original e de caixas percentuais, sem criar nova evidência nem mutar CSVs originais.

Leitura: a R42I torna o fluxo mais fácil e mais idempotente, porque a mesma caixa percentual sempre recria o mesmo recorte ao regenerar a página. Ainda é apoio visual humano, não OCR, tradução ou confirmação automática.

## Rota 42J: fragmentos visuais OpenCV dentro das linhas

Objetivo: fazer uma análise mais fina por computer vision, separando pedaços de tinta dentro das linhas visuais da R42E em fragmentos visuais parecidos com palavras.

Status: concluída em `docs/rota_42j_fragmentos_visuais_opencv_r32.md` e `docs/rota_42j_fragmentos_visuais_opencv_r32.html`.

Saídas:

- `scripts/prepare_ready_visual_word_opencv_map.py`;
- `tests/test_ready_visual_word_opencv_map.py`;
- `data/derived/ready_visual_word_opencv_map_zl3b.csv`;
- `data/derived/ready_visual_word_opencv_map_summary_zl3b.csv`;
- `docs/rota_42j_fragmentos_visuais_opencv_r32.md`;
- `docs/rota_42j_fragmentos_visuais_opencv_r32.html`.

Resultado curto:

- linhas visuais de entrada: 52;
- fragmentos visuais detectados: 77;
- R42J entrou no painel R42G como ferramenta ativa;
- o HTML agrupa fragmentos por linha visual e mostra cada um como recorte real da imagem;
- a rota é acessível a partir de R42B, R42C, R42D, R42E e R42F.

Leitura: a R42J é uma lupa operacional para quando a linha ainda estiver difícil. Ela não é OCR, não lê EVA, não traduz, não confirma palavra e não preenche R32.

## Rota 42K: fila priorizada de revisão visual

Objetivo: transformar os fragmentos da R42J em uma fila prática para atacar as 13 escolhas pendentes da R42F na ordem de menor atrito.

Status: concluída em `docs/rota_42k_fila_priorizada_revisao_visual_r32.md` e `docs/rota_42k_fila_priorizada_revisao_visual_r32.html`.

Saídas:

- `scripts/prepare_ready_visual_review_priority_queue.py`;
- `tests/test_ready_visual_review_priority_queue.py`;
- `data/derived/ready_visual_review_priority_queue_zl3b.csv`;
- `data/derived/ready_visual_review_priority_queue_summary_zl3b.csv`;
- `docs/rota_42k_fila_priorizada_revisao_visual_r32.md`;
- `docs/rota_42k_fila_priorizada_revisao_visual_r32.html`.

Resultado curto:

- pendências priorizadas: 13;
- revisar primeiro: 4;
- revisar depois: 4;
- revisão difícil: 5;
- R42K entrou no painel R42G como ferramenta ativa;
- R42F e R42J apontam para a fila;
- R42K aponta para a R42L como etapa de confirmação antes de aplicar qualquer linha.

Leitura: a R42K é uma fila de trabalho, não uma leitura automática. Ela recomenda por onde começar, mas não confirma linha, palavra, tradução ou evidência visual.

## Rota 42L: confirmação de linhas sugeridas

Objetivo: transformar a sugestão operacional da R42K em uma confirmação humana explícita antes de preencher qualquer zona escolhida.

Status: concluída em `docs/rota_42l_confirmacao_linhas_sugeridas_r32.md` e `docs/rota_42l_confirmacao_linhas_sugeridas_r32.html`.

Saídas:

- `scripts/prepare_ready_visual_line_choice_confirmation.py`;
- `tests/test_ready_visual_line_choice_confirmation.py`;
- `data/annotations/ready_visual_line_choice_confirmation_zl3b.csv`;
- `data/derived/ready_visual_line_choice_confirmation_summary_zl3b.csv`;
- `docs/rota_42l_confirmacao_linhas_sugeridas_r32.md`;
- `docs/rota_42l_confirmacao_linhas_sugeridas_r32.html`.

Resultado curto:

- itens pendentes de confirmação humana: 13;
- revisar primeiro: 4;
- revisar depois: 4;
- revisão difícil: 5;
- R42L entrou no painel R42G como ferramenta ativa;
- a sugestão de linha fica visível, mas `selected_visual_line_number` e `selected_zone_box_pct` continuam vazios até ação humana;
- R42L aponta para a R42M para conferir a captura fina antes de aplicar a escolha.

Leitura: a R42L é o próximo filtro de resiliência. Ela deixa o OpenCV sugerir, mas obriga confirmação humana antes de alimentar R42F/R42D/R42C. Não é OCR, não traduz e não cria evidência visual.

## Rota 42M: captura fina de linhas

Objetivo: reduzir a zona grande de uma linha sugerida para um recorte mais alinhado, usando a união dos fragmentos visuais já detectados pela R42J dentro da zona sugerida pela R42L.

Status: concluída em `docs/rota_42m_captura_fina_linhas_r32.md` e `docs/rota_42m_captura_fina_linhas_r32.html`.

Saídas:

- `scripts/prepare_ready_visual_fine_line_capture.py`;
- `tests/test_ready_visual_fine_line_capture.py`;
- `data/derived/ready_visual_fine_line_capture_zl3b.csv`;
- `data/derived/ready_visual_fine_line_capture_summary_zl3b.csv`;
- `docs/rota_42m_captura_fina_linhas_r32.md`;
- `docs/rota_42m_captura_fina_linhas_r32.html`.

Resultado curto:

- capturas finas: 13;
- status: 13 `fine_capture_ready_needs_human_confirmation`;
- confiança: 11 `media`, 2 `baixa`;
- R42M entrou no painel R42G como ferramenta ativa;
- nenhum campo de escolha humana foi preenchido automaticamente.

Leitura: a R42M é uma melhoria de alinhamento de captura. Ela não substitui a confirmação humana, não lê EVA, não traduz e não cria evidência visual.

## Rota 43: aplicar entrada humana externa e reexecutar gates

Objetivo: depois que a R32 for preenchida por humano usando o HTML high-res R42/R42B, reexecutar R36, R37, R39, R40 e somente entao avaliar se R34/R35/R33/R31 podem rodar.
