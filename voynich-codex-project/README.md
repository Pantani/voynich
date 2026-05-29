# Projeto local — Estudos sobre o Manuscrito Voynich

Criado em: 2026-05-15

Este pacote reúne o resumo dos estudos feitos nesta conversa, uma hipótese de trabalho, dados-semente e scripts para continuar a investigação no Codex local.

## Comece por aqui

1. Leia `docs/resumo_executivo_pt.md`.
2. Veja a matriz de hipóteses em `docs/hipoteses_e_modelos.md`.
3. Baixe as imagens com:

```bash
python scripts/download_images.py
```

4. Rode uma análise básica nos trechos EVA incluídos:

```bash
python scripts/analyze_border_matrix.py data/transcriptions/*.eva
```

5. Gere a tabela contextual da matriz `ar/al/or/ol`:

```bash
python scripts/build_matrix_context_table.py data/transcriptions/*.eva
```

Esse comando grava:

- `data/derived/border_matrix_context.csv`;
- `docs/estudo_matriz_bordas_contexto.md`.

## Observação sobre imagens

As imagens binárias não foram embutidas neste pacote. Em vez disso, o projeto inclui `data/image_sources.csv` e o script `scripts/download_images.py`, que baixam páginas-chave do manuscrito a partir de URLs públicas no seu ambiente local. Isso evita redistribuir cópias de terceiros e deixa o projeto leve.

As páginas configuradas nos manifests incluem os folios mais usados nos ataques: `f67r2`, `f68r3`, `f70v2`, `f89r1`, `f99v`, `f84r`, `f68r1`, `f68r2`, `f67v2` e `f1r`.

## Estrutura

```text
voynich-codex-project/
├── README.md
├── CODEX_PROMPT.md
├── requirements.txt
├── pyproject.toml
├── docs/
├── data/
│   ├── image_sources.csv
│   ├── patterns_seed.tsv
│   ├── attack_matrix_seed.csv
│   └── transcriptions/
├── images/
├── scripts/
├── notebooks/
└── tests/
```

## Estado da investigação

Não há decifração final. A hipótese de trabalho mais forte é que o Voynichese funciona como um sistema formal em camadas: operadores de locus/seção, bordas de token e núcleos variáveis, talvez com leitura funcional parcialmente direita→esquerda.

A “fechadura” mais promissora é a matriz:

```text
        r       l
a      ar      al
o      or      ol
```

com operadores como `ok-`, `ot-`, `qo-`, `yk-`, `yt-` e bordas como `-dy`, `-y`, `-aiin`.

## Baixar dados textuais públicos iniciais

```bash
python scripts/download_sources.py
```

Esse comando baixa a transcrição IVTFF/EVA `ZL3b-n.txt` de Voynich.nu e alguns dados do repositório público de Reddy & Knight para experimentos estatísticos.

Rota de pesquisa atual:

- `docs/rotas_de_pesquisa.md`;
- Rota 1: ampliar corpus textual com `data/raw/ZL3b-n.txt`;
- relatório contextual: `docs/estudo_matriz_bordas_contexto_zl3b.md`.
- Rota 2: controles estatísticos em `docs/rota_2_controles_estatisticos.md`;
- Rota 3: anotação visual em `data/annotations/visual_annotations_seed_zl3b.csv` e `docs/rota_3_cruzamento_visual.md`;
- Rota 4: decomposição dos eixos `a/o` e `r/l` em `docs/rota_4_eixos_matriz.md`;
- Rota 5: pares comparáveis no mesmo folio/locus/família em `docs/rota_5_pares_comparaveis.md`;
- Rota 6: fila de conferência fina de glifos em `docs/rota_6_conferencia_glifos.md`;
- Rota 7: recortes SVG aproximados em `docs/rota_7_recortes_revisao.md`;
- Rota 8: decisões conservadoras de revisão dos recortes em `docs/rota_8_revisao_recortes.md`.
- Rota 9: folha de revisão manual assistida em `docs/rota_9_revisao_manual.md` e `docs/rota_9_revisao_manual.html`.
- Rota 10: consolidação da revisão manual em `docs/rota_10_consolidacao_manual.md`.
- Rota 11: fila de segunda passada de recortes em `docs/rota_11_segunda_passada_recortes.md`.
- Rota 12: pacotes por fólio para revisão guiada em `docs/rota_12_pacotes_revisao_guiada.md`.
- Rota 13: checklist item-a-item por pacote em `docs/rota_13_checklist_pacotes.md`.
- Rota 14: consolidação da checklist em `docs/rota_14_consolidacao_checklist.md`.
- Rota 15: instruções humanas por pacote em `docs/rota_15_instrucoes_revisao_humana.md`.
- Rota 16: consolidação da revisão humana em `docs/rota_16_consolidacao_revisao_humana.md`.
- Rota 17: fila P0/P1 para revisão humana em `docs/rota_17_revisao_humana_p0_p1.md`.
- Rota 18: ingestão das decisões P0/P1 em `docs/rota_18_ingestao_decisoes_p0_p1.md`.
- Rota 19: pacote visual direto P0/P1 em `docs/rota_19_pacote_visual_direto_p0_p1.md` e `docs/rota_19_pacote_visual_direto_p0_p1.html`.
- Rota 20: aplicação do pacote visual na checklist em `docs/rota_20_aplicacao_decisoes_pacote_visual.md`.
- Rota 21: planilha de preenchimento visual P0/P1 em `docs/rota_21_planilha_preenchimento_visual_p0_p1.md`.
- Rota 22: validação da planilha visual R21 em `docs/rota_22_validacao_planilha_visual.md`.
- Rota 23: pacote HTML guiado para preencher R21 em `docs/rota_23_pacote_html_preenchimento_r21.md` e `docs/rota_23_pacote_html_preenchimento_r21.html`.
- Rota 24: prontidão para preenchimento visual R21 em `docs/rota_24_prontidao_preenchimento_visual.md`.
- Rota 25: gate manual de preenchimento R21 permanece pendente.
- Rota 26: tabela ampliada das formas exatas `ok/ot` em `docs/rota_26_tabela_contexto_formas_exatas.md`.
- Rota 27: fila de lacunas visuais das formas exatas em `docs/rota_27_fila_lacunas_visuais_formas_exatas.md`.
- Rota 28: pacote de anotação visual P0/P1 das formas exatas em `docs/rota_28_pacote_anotacao_visual_formas_exatas.md` e `docs/rota_28_pacote_anotacao_visual_formas_exatas.html`.
- Rota 29: fila de fontes de imagem ausentes em `docs/rota_29_fila_fontes_imagem_formas_exatas.md` e `docs/rota_29_fila_fontes_imagem_formas_exatas.html`.
- Rota 30: validação de fontes candidatas em `docs/rota_30_validacao_fontes_candidatas.md`.
- Rota 31: validação de anotações visuais prontas em `docs/rota_31_validacao_anotacoes_visuais_prontas.md`.
- Rota 32: pacote HTML focado para anotações visuais prontas em `docs/rota_32_pacote_html_anotacao_visual_prontos.md` e `docs/rota_32_pacote_html_anotacao_visual_prontos.html`.
- Rota 33: aplicação controlada das entradas R32 em `docs/rota_33_aplicacao_entradas_visuais_r32.md`.
- Rota 34: gate manual de anotação visual R32 em `docs/rota_34_gate_manual_anotacao_visual_r32.md`.
- Rota 35: plano de reexecução pós-gate R32 em `docs/rota_35_plano_reexecucao_pos_gate_r32.md`.
- Rota 36: protocolo de preenchimento humano R32 em `docs/rota_36_protocolo_preenchimento_humano_r32.md`.
- Rota 37: plano de revalidação R34/R35/R33/R31 em `docs/rota_37_plano_revalidacao_r34_r35_r33_r31.md`.
- Rota 38: ordem de trabalho para preencher R32 em `docs/rota_38_ordem_trabalho_preencher_r32_reabrir_cadeia.md`.
- Rota 39: auditoria de execução do preenchimento humano R32 em `docs/rota_39_auditoria_execucao_preenchimento_humano_r32.md`.
- Rota 40: plano condicional de reabertura da cadeia R34/R35/R33/R31 em `docs/rota_40_plano_condicional_reabertura_cadeia_r39.md`.
- Rota 41: pacote de entrada humana externa na R32 em `docs/rota_41_pacote_entrada_humana_externa_r32.md`.
- Rota 42: fontes Yale IIIF high-res para R32 em `docs/rota_42_fontes_yale_iiif_highres_r32.md` e `docs/rota_42_pacote_html_yale_iiif_highres_r32.html`.
- Rota 42A: análise assistida das fontes Yale high-res em `docs/rota_42a_analise_assistida_highres_r32.md`.
- Rota 42B: ferramenta guiada de preenchimento humano high-res em `docs/rota_42b_pacote_html_preenchimento_humano_r32.html`.

## Manifestos de imagem

- `data/commons_image_sources.csv` — usado diretamente pelo script `download_images.py`.
- `data/manifests/image_manifest.json` — versão detalhada em JSON, com thumbnails, página de fonte e notas.
- `docs/imagens_preview.html` — prévia HTML das imagens externas.
