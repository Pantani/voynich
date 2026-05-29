# Scripts — Índice Categorizado

Todos os 60+ scripts Python do projeto. O diretório é **flat** (sem subpastas) para manter compatibilidade com os imports dos testes.

Execute sempre com o venv do projeto:
```bash
/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/.venv/bin/python scripts/<nome>.py
```

---

## Análise Estatística (analyze_*, build_*)

| Script | Rota | Descrição |
|--------|------|-----------|
| `analyze_border_matrix.py` | — | Análise inicial da matriz ar/al/or/ol nos trechos EVA |
| `analyze_tokens.py` | — | Análise básica de tokens |
| `analyze_matrix_controls.py` | 2 | Controles estatísticos: chi², embaralhamento, Cramer's V |
| `analyze_matrix_axes.py` | 4 | Decompõe matriz em eixos a/o e r/l |
| `analyze_same_context_pairs.py` | 5 | Pares comparáveis dentro do mesmo folio/locus/família |
| `analyze_visual_annotations.py` | 3 | Cruza corpus textual com anotações visuais |
| `analyze_form_collocations.py` | 43 | **Novo**: collocações, trigramas e assimetria ar vs al (chi²=10.54) |
| `build_matrix_context_table.py` | 1 | Tabela contextual da matriz ZL3b |
| `build_exact_form_context_table.py` | 26 | Tabela ampliada das 8 formas exatas ok/ot |

---

## Download e Setup

| Script | Descrição |
|--------|-----------|
| `download_images.py` | Baixa imagens do manuscrito (Wikimedia Commons) |
| `download_sources.py` | Baixa transcrição ZL3b-n.txt e dados Reddy & Knight |

---

## Anotação Visual — Preparação (prepare_visual_*, prepare_exact_*)

| Script | Rota | Descrição |
|--------|------|-----------|
| `prepare_visual_annotation_candidates.py` | 3 | Lista candidatos para anotação visual |
| `prepare_review_crops.py` | 7 | Gera recortes SVG aproximados |
| `prepare_glyph_review_queue.py` | 6 | Fila de conferência fina de glifos |
| `prepare_exact_form_visual_gap_queue.py` | 27 | Fila de lacunas visuais das formas exatas |
| `prepare_exact_form_visual_annotation_package.py` | 28 | Pacote P0/P1 para anotação visual |
| `prepare_missing_source_image_queue.py` | 29 | Fila de fontes de imagem ausentes |

---

## Anotação Visual — Pipeline R32 (prepare_ready_visual_*)

Pipeline de desbloqueio da anotação visual das 8 formas exatas prioritárias.

| Script | Rota | Descrição |
|--------|------|-----------|
| `prepare_ready_visual_annotation_html.py` | 32 | Gera HTML + entry sheet ⚠️ sobrescreve CSV |
| `prepare_ready_visual_annotation_highres_source_packet.py` | 42 | Baixa fontes Yale IIIF high-res |
| `prepare_ready_visual_annotation_highres_ai_assist.py` | 42A | Análise assistida das fontes high-res |
| `prepare_ready_visual_annotation_highres_human_fill_html.py` | 42B | Ferramenta HTML principal de revisão (70KB) |
| `prepare_ready_visual_line_calibration_tool.py` | 42C | Calibrador de baselines (54KB) |
| `prepare_ready_visual_line_opencv_suggestions.py` | 42D | Sugestões OpenCV de pré-calibração |
| `prepare_ready_visual_line_opencv_map.py` | 42E | Mapa de linhas visuais OpenCV |
| `prepare_ready_visual_line_zone_choice_tool.py` | 42F | Escolha simples de linhas sem zona |
| `prepare_active_tool_dashboard.py` | 42G | Painel unificado das ferramentas ativas |
| `prepare_ready_visual_word_opencv_map.py` | 42J | Fragmentos visuais OpenCV |
| `prepare_ready_visual_review_priority_queue.py` | 42K | Fila priorizada de revisão visual |
| `prepare_ready_visual_line_choice_confirmation.py` | 42L | Confirmação de linhas sugeridas |
| `prepare_ready_visual_fine_line_capture.py` | 42M | Captura fina de linhas |
| `prepare_ready_visual_annotation_manual_fill_protocol.py` | 36 | Protocolo de preenchimento humano |
| `prepare_ready_visual_annotation_manual_reopen_work_order.py` | 38 | Ordem de trabalho para reabrir cadeia |
| `prepare_ready_visual_annotation_external_human_entry_packet.py` | 41 | Pacote para revisor externo |

---

## Pipeline de Revisão — Checklists e Pacotes

| Script | Rota | Descrição |
|--------|------|-----------|
| `prepare_second_pass_crop_queue.py` | 11 | Segunda passada de recortes |
| `prepare_folio_review_packets.py` | 12 | Pacotes por fólio para revisão guiada |
| `prepare_packet_item_checklist.py` | 13 | Checklist item-a-item |
| `prepare_manual_svg_review.py` | 9 | Folha de revisão manual assistida |
| `prepare_human_review_instructions.py` | 15 | Instruções humanas por pacote |
| `prepare_priority_human_review.py` | 17 | Fila P0/P1 para revisão humana |
| `prepare_direct_visual_decision_package.py` | 19 | Pacote visual direto P0/P1 |
| `prepare_visual_decision_entry_sheet.py` | 21 | Planilha de preenchimento visual |
| `prepare_guided_visual_entry_html.py` | 23 | HTML guiado para preencher R21 |

---

## Validação, Consolidação e Auditoria

| Script | Rota | Descrição |
|--------|------|-----------|
| `validate_ready_visual_annotations.py` | 31 | Valida anotações manuais prontas |
| `validate_visual_decision_entry_sheet.py` | 22 | Valida planilha visual R21 |
| `validate_missing_source_candidates.py` | 30 | Valida fontes candidatas |
| `verify_guided_visual_entry_readiness.py` | 24 | Verifica prontidão do pacote HTML R23 |
| `verify_ready_visual_annotation_manual_gate.py` | 34 | Gate manual de anotação R32 |
| `consolidate_manual_svg_review.py` | 10 | Consolida revisão manual |
| `consolidate_packet_item_checklist.py` | 14 | Consolida checklist |
| `consolidate_human_review_evidence.py` | 16 | Consolida revisão humana preenchida |
| `review_crop_decisions.py` | 8 | Registra decisões de recorte |
| `audit_ready_visual_annotation_manual_fill_execution.py` | 39 | Audita execução do preenchimento |

---

## Aplicação e Ingestão

| Script | Rota | Descrição |
|--------|------|-----------|
| `apply_direct_visual_decisions.py` | 20 | Aplica valores manuais do pacote visual |
| `apply_ready_visual_annotation_entries.py` | 33 | Aplica entradas R32 no pacote derivado |
| `ingest_priority_human_decisions.py` | 18 | Ingere decisões P0/P1 |

---

## Planejamento e Revalidação

| Script | Rota | Descrição |
|--------|------|-----------|
| `plan_ready_visual_annotation_post_gate_rerun.py` | 35 | Plano pós-gate |
| `plan_ready_visual_annotation_revalidation_chain.py` | 37 | Plano de revalidação R34→R33→R31 |
| `plan_ready_visual_annotation_conditional_chain_reopen.py` | 40 | Reabertura condicional da cadeia |

---

## Utilitários Compartilhados

| Script | Descrição |
|--------|-----------|
| `eva_visual.py` | Renderizador SVG de tokens EVA (usado por R42B/C/F) |
| `visual_crop.py` | Recortes reais de imagem (usado por R42B/C/D/E/F) |
| `parse_eva_text.py` | Parser básico de texto EVA |
