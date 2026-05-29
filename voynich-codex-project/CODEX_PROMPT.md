# Prompt para continuar no Codex local

Você está continuando uma investigação sobre o Manuscrito Voynich.

Objetivo: testar hipóteses falsificáveis, não “forçar” uma tradução.

Leia, nesta ordem:

1. `docs/resumo_executivo_pt.md`
2. `docs/log_dos_ataques.md`
3. `docs/matriz_bordas.md`
4. `docs/hipoteses_e_modelos.md`
5. `data/patterns_seed.tsv`
6. `data/attack_matrix_seed.csv`

Hipótese atual:

- O Voynichese não parece uma substituição simples letra-por-letra.
- Rótulos, texto corrido, texto circular, texto radial e rubricas/vermelho devem ser tratados como camadas diferentes.
- `ok-`, `ot-`, `qo-`, `yk-`, `yt-` provavelmente são operadores de modo/locus/classe.
- `ar/al/or/ol` pode ser uma matriz de quatro estados.
- `dy/y/aiin` podem ser bordas de template, não sufixos linguísticos comuns.
- A linha física do manuscrito provavelmente participa do sistema.

Tarefas recomendadas:

1. Baixar imagens: `python scripts/download_images.py`.
2. Rodar `python scripts/analyze_border_matrix.py data/transcriptions/*.eva`.
3. Rodar `python scripts/build_matrix_context_table.py data/transcriptions/*.eva`.
4. Para o corpus ZL3b, rodar `python scripts/analyze_matrix_controls.py data/derived/border_matrix_context_zl3b.csv`.
5. Preparar a anotação visual com `python scripts/prepare_visual_annotation_candidates.py data/derived/border_matrix_context_zl3b.csv`.
6. Cruzar a semente visual com `python scripts/analyze_visual_annotations.py data/annotations/visual_annotations_seed_zl3b.csv`.
7. Testar os eixos com `python scripts/analyze_matrix_axes.py data/derived/border_matrix_context_zl3b.csv data/annotations/visual_annotations_seed_zl3b.csv`.
8. Encontrar pares locais com `python scripts/analyze_same_context_pairs.py data/derived/border_matrix_context_zl3b.csv data/annotations/visual_annotations_seed_zl3b.csv`.
9. Preparar a fila de conferência fina com `python scripts/prepare_glyph_review_queue.py data/derived/same_context_matrix_pairs_zl3b.csv data/annotations/visual_annotations_seed_zl3b.csv`.
10. Gerar recortes aproximados com `python scripts/prepare_review_crops.py data/annotations/glyph_review_queue_zl3b.csv`.
11. Registrar decisões conservadoras com `python scripts/review_crop_decisions.py data/annotations/review_crop_manifest_zl3b.csv`.
12. Preparar a revisão manual assistida com `python scripts/prepare_manual_svg_review.py data/annotations/crop_review_decisions_zl3b.csv`.
13. Consolidar a revisão manual com `python scripts/consolidate_manual_svg_review.py data/annotations/manual_svg_review_zl3b.csv`.
14. Preparar a fila de segunda passada com `python scripts/prepare_second_pass_crop_queue.py data/derived/manual_svg_review_consolidated_zl3b.csv`.
15. Agrupar pacotes por fólio com `python scripts/prepare_folio_review_packets.py data/annotations/second_pass_crop_queue_zl3b.csv data/annotations/review_crop_manifest_zl3b.csv`.
16. Gerar checklist por item com `python scripts/prepare_packet_item_checklist.py data/annotations/folio_review_packet_items_zl3b.csv`.
17. Consolidar a checklist com `python scripts/consolidate_packet_item_checklist.py data/annotations/packet_item_checklist_zl3b.csv`.
18. Gerar instruções humanas por pacote com `python scripts/prepare_human_review_instructions.py data/annotations/folio_review_packets_zl3b.csv data/annotations/packet_item_checklist_zl3b.csv`.
19. Consolidar a revisão humana preenchida com `python scripts/consolidate_human_review_evidence.py data/annotations/human_review_instruction_items_zl3b.csv data/annotations/packet_item_checklist_zl3b.csv`.
20. Preparar a fila P0/P1 com `python scripts/prepare_priority_human_review.py data/derived/human_review_evidence_consolidated_zl3b.csv`.
21. Revisar visualmente os itens P0/P1 pendentes e preencher `manual_token_seen`, `manual_new_crop_needed`, `manual_image_insufficient` e coordenadas novas quando houver.
22. Ingerir somente as decisões preenchidas na checklist com `python scripts/ingest_priority_human_decisions.py data/annotations/priority_human_review_p0_p1_zl3b.csv data/annotations/packet_item_checklist_zl3b.csv`; não preencher campos por inferência.
23. Preparar um pacote visual direto para reduzir fricção no preenchimento dos 6 itens P0/P1 com `python scripts/prepare_direct_visual_decision_package.py data/derived/priority_human_decisions_p0_p1_zl3b.csv`.
24. Aplicar somente valores manuais explícitos do pacote visual a uma checklist derivada com `python scripts/apply_direct_visual_decisions.py data/annotations/direct_visual_decision_package_p0_p1_zl3b.csv data/annotations/packet_item_checklist_zl3b.csv`; não sobrescrever a checklist original silenciosamente.
25. Gerar uma planilha pequena de entrada manual com `python scripts/prepare_visual_decision_entry_sheet.py data/derived/direct_visual_decision_application_log_zl3b.csv data/annotations/direct_visual_decision_package_p0_p1_zl3b.csv`.
26. Preencher manualmente `data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv`, respeitando `manual_token_seen=yes/no/uncertain`, `manual_new_crop_needed=yes/no` e `manual_image_insufficient=yes/no`.
27. Validar e aplicar somente valores explícitos da planilha R21 preenchida com `python scripts/validate_visual_decision_entry_sheet.py data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv data/annotations/direct_visual_decision_package_p0_p1_zl3b.csv`; campos vazios continuam pendentes e não apagam valores existentes.
28. Gerar um pacote HTML guiado para preencher R21 com `python scripts/prepare_guided_visual_entry_html.py data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv data/derived/visual_decision_entry_validation_log_zl3b.csv`, mostrando imagem fonte, SVG de referência, valores permitidos e linha alvo; não gravar decisões automaticamente.
29. Verificar prontidão do HTML/asset/CSV com `python scripts/verify_guided_visual_entry_readiness.py data/derived/guided_visual_entry_html_manifest_zl3b.csv data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv docs/rota_23_pacote_html_preenchimento_r21.html`; isso não interpreta glifos.
30. Preencher manualmente `data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv` usando `docs/rota_23_pacote_html_preenchimento_r21.html` como guia, sem preencher por inferência.
31. Depois de preencher/aplicar a planilha derivada, reexecutar as rotas 22, 18 e 14.
32. Ampliar a tabela que cruza cada forma `okar/okal/okor/okol/otar/otal/otor/otol` com `python scripts/build_exact_form_context_table.py data/derived/border_matrix_context_zl3b.csv data/annotations/visual_annotations_seed_zl3b.csv`:
   - folio;
   - seção;
   - tipo de locus;
   - posição visual;
   - início/meio/fim de linha;
   - objeto próximo na imagem.
33. Priorizar lacunas visuais das oito formas exatas com `python scripts/prepare_exact_form_visual_gap_queue.py data/derived/exact_form_context_table_zl3b.csv data/commons_image_sources.csv`; isso gera uma fila de trabalho, não evidência.
34. Montar o pacote de anotação visual P0/P1 com `python scripts/prepare_exact_form_visual_annotation_package.py data/derived/exact_form_visual_gap_queue_zl3b.csv`; isso separa imagem pronta de fonte ausente e mantém campos manuais vazios.
35. Criar a fila de fontes ausentes com `python scripts/prepare_missing_source_image_queue.py data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`; consultas de busca não são fontes confirmadas.
36. Validar e aplicar somente URLs candidatas verificadas da Rota 29 com `python scripts/validate_missing_source_candidates.py data/annotations/exact_form_missing_source_queue_p0_p1_zl3b.csv data/commons_image_sources.csv`; a saída deve ser uma cópia derivada do manifesto, não uma mutação silenciosa do original.
37. Validar anotações visuais manuais dos 8 itens prontos da Rota 28 com `python scripts/validate_ready_visual_annotations.py data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`; aceitar somente `manual_annotation_status=annotated/not_visible/uncertain` com notas explícitas, e manter campos vazios como pendentes.
38. Gerar um HTML focado para preencher os 8 itens prontos da Rota 28 com `python scripts/prepare_ready_visual_annotation_html.py data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv data/derived/ready_visual_annotation_validation_zl3b.csv`, mostrando a imagem do manifesto e os campos permitidos, sem gravar decisões automaticamente.
39. Aplicar somente entradas humanas explícitas da planilha R32 ao pacote R28 derivado com `python scripts/apply_ready_visual_annotation_entries.py data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv data/annotations/exact_form_visual_annotation_package_p0_p1_zl3b.csv`; campos vazios continuam pendentes e o pacote original não deve ser alterado.
40. Verificar o gate manual R32 com `python scripts/verify_ready_visual_annotation_manual_gate.py data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv docs/rota_32_pacote_html_anotacao_visual_prontos.html data/derived/ready_visual_annotation_entry_application_log_zl3b.csv`; isso só confirma prontidão/bloqueio, não interpreta imagem.
41. Planejar a reexecução pós-gate com `python scripts/plan_ready_visual_annotation_post_gate_rerun.py data/derived/ready_visual_annotation_manual_gate_zl3b.csv`; se não houver `ready_to_rerun_r33_r31`, não reexecutar R33/R31.
42. Preparar o protocolo de preenchimento humano com `python scripts/prepare_ready_visual_annotation_manual_fill_protocol.py data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv data/derived/ready_visual_annotation_post_gate_rerun_plan_zl3b.csv docs/rota_32_pacote_html_anotacao_visual_prontos.html`; isso nao preenche valores automaticamente.
43. Planejar a cadeia de revalidação com `python scripts/plan_ready_visual_annotation_revalidation_chain.py data/derived/ready_visual_annotation_manual_fill_protocol_zl3b.csv`; se não houver entrada humana pronta, não rodar R34/R35/R33/R31.
44. Gerar a ordem de trabalho para preenchimento com `python scripts/prepare_ready_visual_annotation_manual_reopen_work_order.py data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv data/derived/ready_visual_annotation_manual_fill_protocol_zl3b.csv data/derived/ready_visual_annotation_revalidation_chain_plan_zl3b.csv docs/rota_32_pacote_html_anotacao_visual_prontos.html`; isso nao grava decisoes.
45. Auditar a execução do preenchimento humano com `python scripts/audit_ready_visual_annotation_manual_fill_execution.py data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv data/derived/ready_visual_annotation_manual_reopen_work_order_zl3b.csv data/derived/ready_visual_annotation_manual_fill_protocol_zl3b.csv data/derived/ready_visual_annotation_revalidation_chain_plan_zl3b.csv`; isso só confirma bloqueio/liberação, não interpreta imagem.
46. Planejar a reabertura condicional da cadeia com `python scripts/plan_ready_visual_annotation_conditional_chain_reopen.py data/derived/ready_visual_annotation_manual_fill_execution_audit_zl3b.csv`; rodar R34/R35/R33/R31 somente se o plano emitir `ready_to_run_revalidation_chain`.
47. Preparar o pacote de entrada humana externa com `python scripts/prepare_ready_visual_annotation_external_human_entry_packet.py data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv data/derived/ready_visual_annotation_manual_reopen_work_order_zl3b.csv data/derived/ready_visual_annotation_conditional_chain_reopen_plan_zl3b.csv`; isso organiza o trabalho humano, mas nao preenche a R32.
48. Baixar/gerar fontes high-res oficiais com `curl -L https://collections.library.yale.edu/manifests/2002046 -o data/derived/yale_iiif_manifest_2002046.json` e `python scripts/prepare_ready_visual_annotation_highres_source_packet.py data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv data/derived/yale_iiif_manifest_2002046.json`; isso melhora a imagem de apoio, mas nao cria evidencia visual.
49. Registrar a leitura assistida das fontes high-res com `python scripts/prepare_ready_visual_annotation_highres_ai_assist.py`; isso orienta recorte/zoom, mas nao preenche `manual_annotation_status`, nao escreve notas manuais e nao reabre a cadeia.
50. Gerar a ferramenta guiada de preenchimento humano high-res com `python scripts/prepare_ready_visual_annotation_highres_human_fill_html.py`; isso cria uma pagina local com fila de revisao, guia rapido, pergunta `Voce achou essas palavrinhas na imagem?`, cartoes visuais EVA para os tokens, chips de linhas, total de entradas/loci ZL3b por folio com lista auditavel da origem desse total, texto de referencia das linhas alvo, baselines calibradas da R42C quando existirem ou zonas visuais provaveis de bloco quando a linha ainda estiver pendente, zoom/contraste/rotacao, botoes mostrar/esconder/subir/descer zonas, atalhos `Ferramentas ativas`, `Calibrar linhas` e `Mapa OpenCV`, botoes `Achei`/`Nao achei`/`Nao sei`, nota automatica e rascunho CSV recolhido. A pagina nao calcula posicao visual por proporcao da numeracao ZL3b; sem baseline R42C, no maximo mostra zona manual aproximada de bloco. Os deslocamentos de zona sao temporarios e nao entram no rascunho local; a pagina nao grava a R32 automaticamente.
51. Gerar o calibrador manual de linhas/baselines com `python scripts/prepare_ready_visual_line_calibration_tool.py`; isso cria `docs/rota_42c_calibrador_linhas_baseline_r32.html` e `data/annotations/ready_visual_line_calibration_zl3b.csv`, preservando baselines manuais em reruns, mesclando sugestoes OpenCV existentes como `baseline_points` pendentes, registrando `Acao OpenCV: prefill_pending_baseline`, mostrando `Computador ja ajudou` com o proximo passo humano, prendendo o overlay do scan ao canvas real da imagem, oferecendo `Guia rapido`, progresso, mira/ultimo clique, coordenadas percentuais, respiro de scroll para zoom alto, scroll natural para cima quando o painel chega no topo, botao `Topo da imagem` e `Ajuste fino` para mover linha inteira ou uma ponta em passos pequenos, criando assinatura deterministica por item para rejeitar rascunho local de scan defasado, invalidando rascunhos locais antigos por versao, oferecendo `Resetar scan local`, exigindo pelo menos dois pontos para manter `calibrated`, oferecendo `Copiar CSV`/`Baixar CSV` e atalhos `Ferramentas ativas`, `Abrir R42B`, `Abrir sugestoes OpenCV` e `Abrir mapa OpenCV`, mas nao cria evidencia visual nem preenche a R32.
52. Gerar mapa OpenCV de linhas visuais com `PYTHONPATH=/private/tmp/voynich-opencv python scripts/prepare_ready_visual_line_opencv_map.py`; isso cria a R42E, conta/numera linhas visuais agrupadas por imagem, abre por padrao em modo focado nas zonas R32 conhecidas, mostra reguas finas em vez de caixas grandes, preserva o modo `Mapa bruto`, aponta para `Ferramentas ativas` e deixa claro que isso nao e palavra encontrada nem evidencia.
53. Gerar sugestoes iniciais OpenCV com `PYTHONPATH=/private/tmp/voynich-opencv python scripts/prepare_ready_visual_line_opencv_suggestions.py` quando OpenCV/NumPy estiverem disponiveis; isso cria a R42D usando o agrupamento de linhas visuais e classifica `opencv_auto_action` como `prefill_pending_baseline`, `needs_manual_zone`, `needs_better_scan_or_manual_line` etc., mas apenas como rascunho operacional, sem preencher R32 e sem marcar R42C como `calibrated`.
54. Gerar a escolha simples de linhas sem zona com `python scripts/prepare_ready_visual_line_zone_choice_tool.py`; isso cria a R42F para os itens `needs_manual_zone`, mostra linhas reais vindas da R42E, deixa escolher `Essa e a linha`, gera `selected_zone_box_pct`, aponta para `Ferramentas ativas`, mas nao preenche R32 nem confirma evidencia.
55. Gerar o painel unico de ferramentas ativas com `python scripts/prepare_active_tool_dashboard.py`; isso cria a R42G, deixa apenas R42G/R42K/R42L/R42M/R42F/R42D/R42J/R42C/R42B/R42E como HTMLs ativos e remove os HTMLs antigos de forma idempotente.
56. Manter textos EVA visiveis como desenhos usando `scripts/eva_visual.py`; R42B, R42C e R42F devem mostrar `eva-visual-line`/`eva-word` como referencia humana principal, deixando texto cru apenas em CSVs/dados tecnicos para auditoria.
57. Manter recortes reais da imagem usando `scripts/visual_crop.py`; R42B deve mostrar `Recortes reais da pagina`, R42C deve mostrar `Lupa da linha`, R42D/R42E/R42F devem mostrar recortes reais das linhas quando houver caixa percentual, e R42G deve orientar o fluxo por esse modo. Isso e apoio visual humano, nao OCR nem evidencia automatica.
58. Gerar a analise fina de fragmentos visuais com `PYTHONPATH=/private/tmp/voynich-opencv python scripts/prepare_ready_visual_word_opencv_map.py`; isso cria a R42J, segmenta fragmentos visuais dentro das linhas R42E, mostra recortes reais por fragmento e adiciona a rota ao painel ativo. Isso nao e OCR, nao le EVA, nao traduz e nao confirma palavra.
59. Gerar a fila priorizada com `python scripts/prepare_ready_visual_review_priority_queue.py`; isso cria a R42K, cruza pendencias da R42F com fragmentos da R42J, ordena o que revisar primeiro e adiciona recortes reais para reduzir atrito humano. Isso nao e OCR, nao escolhe a linha sozinho e nao cria evidencia.
60. Gerar a confirmacao de linhas sugeridas com `python scripts/prepare_ready_visual_line_choice_confirmation.py`; isso cria a R42L, mostra a sugestao da R42K, alternativas vindas da R42F e recortes reais, mas mantem `selected_visual_line_number` e `selected_zone_box_pct` vazios ate confirmacao humana.
61. Gerar a captura fina de linhas com `python scripts/prepare_ready_visual_fine_line_capture.py`; isso cria a R42M, cruza a zona sugerida da R42L com a uniao dos fragmentos visuais, produz `refined_capture_box_pct` e `refined_baseline_points`, mas ainda nao escolhe linha, nao preenche R42F/R42C/R32, nao e OCR e nao cria evidencia.
62. Reexecutar `PYTHONPATH=/private/tmp/voynich-opencv python scripts/prepare_ready_visual_line_opencv_suggestions.py` depois da R42F para a R42D consumir as zonas escolhidas e transformar escolhas em novas sugestoes `prefill_pending_baseline` pendentes.
63. Reexecutar `python scripts/prepare_ready_visual_line_calibration_tool.py` depois da R42D para a R42C mesclar as sugestoes confiaveis como rascunho pendente, registrar a linha visual OpenCV candidata, mostrar linhas vermelhas tracejadas, exibir `Computador ja ajudou` e ainda exigir confirmacao humana antes de qualquer `calibrated`.
64. Preencher manualmente `data/annotations/ready_visual_line_calibration_zl3b.csv` pelo HTML R42C quando precisar substituir zonas grandes por baselines precisas; depois voltar pelo atalho `Abrir R42B` e usar essas baselines apenas como apoio operacional para revisar a R32.
65. Preencher manualmente `data/annotations/ready_visual_annotation_entry_sheet_zl3b.csv` usando a ordem R38, o pacote R41, o HTML high-res R42/R42B, a orientacao R42A e, quando disponivel, as baselines R42C; depois reexecutar a Rota 36, a Rota 37, a Rota 39, a Rota 40, a Rota 34, a Rota 35, a Rota 33 e validar o pacote derivado com a Rota 31.
66. Manter aberto o gate manual da R21: preencher `data/annotations/visual_decision_entry_sheet_p0_p1_zl3b.csv` usando o HTML guiado quando houver decisão visual humana.
67. Não assumir que `okal = Sol`, `doaro = Plêiades` ou `daiin = água`; trate como hipóteses fracas até que façam previsões.
