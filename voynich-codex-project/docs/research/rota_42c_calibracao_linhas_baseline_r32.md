# Rota 42C: calibracao manual de linhas/baselines R32 high-res

Esta rota cria uma ferramenta local para calibrar baselines visuais das linhas alvo da R42B. Ela transforma zonas grandes em linhas manuais mais precisas, mas nao traduz, nao decide anotacao visual e nao preenche a R32.

Fonte R42B: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_annotation_highres_human_fill_html_zl3b.csv`.
Planilha de calibracao: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/annotations/ready_visual_line_calibration_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/ready_visual_line_calibration_summary_zl3b.csv`.
HTML: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/docs/rota_42c_calibrador_linhas_baseline_r32.html`.

## Resultado curto

- linhas/loci alvo para calibrar: 19;
- interacao: selecionar locus, seguir `Guia rapido`, rastrear a mira com coordenadas percentuais, clicar no comeco e no fim da linha real, usar `Ajuste fino` para mover a linha inteira ou uma ponta em passos pequenos, marcar calibrada/incerta/nao calibravel;
- usabilidade infantil: o HTML mostra progresso, passo atual, contagem de pontos, mira/ultimo clique, lupa de recorte real da linha e mensagens simples do que fazer agora;
- zoom/scroll: o painel da imagem tem respiro proprio para zoom alto, nao prende o gesto de scroll no topo, e tem botao `Topo da imagem` para voltar ao canto superior;
- exportacao: o HTML mostra rascunho CSV e oferece copiar/baixar CSV para aplicar na planilha de calibracao;
- navegacao: o HTML tem atalhos para R42B, R42D, R42E e R42F;
- apoio OpenCV: quando a R42D gerar sugestao inicial, o script preenche `baseline_points` como rascunho pendente, registra `Acao OpenCV: prefill_pending_baseline`, e o HTML mostra `Computador ja ajudou` com o proximo passo humano antes de marcar como calibrada;
- maturidade do scan: o overlay SVG fica preso ao canvas real da imagem, cada item recebe uma assinatura deterministica do scan, e o botao `Resetar scan local` limpa rascunhos antigos do navegador;
- persistencia: o HTML usa rascunho local e gera CSV; o script preserva baseline manual existente se rodar novamente;
- resiliencia: status `calibrated` sem pelo menos dois pontos validos volta para `pending_calibration`, inclusive quando vem de CSV ou de rascunho local antigo;
- guarda: `line_calibration_tool_not_visual_evidence`.

### Folios

|item|n|
|---|---:|
|f99v|5|
|f1r|2|
|f67r2|2|
|f67v1|2|
|f84r|2|
|f88v|2|
|f89r2|2|
|f99r|2|

### Status de calibracao

|item|n|
|---|---:|
|pending_calibration|19|

### Pontos de baseline

|item|n|
|---|---:|
|missing_baseline_points|17|
|with_baseline_points|2|

## Itens

|rota42C|rota32|folio|locus|status|
|---|---|---|---|---|
|R42C-001|R32-005|f84r|f84r.24,+P0|pending_calibration|
|R42C-002|R32-005|f84r|f84r.29,+P0|pending_calibration|
|R42C-003|R32-008|f99r|f99r.2,@Lf|pending_calibration|
|R42C-004|R32-008|f99r|f99r.8,@Lf|pending_calibration|
|R42C-005|R32-001|f99v|f99v.12,+P0|pending_calibration|
|R42C-006|R32-001|f99v|f99v.13,+P0|pending_calibration|
|R42C-007|R32-001|f99v|f99v.21,@P0|pending_calibration|
|R42C-008|R32-001|f99v|f99v.24,+P0|pending_calibration|
|R42C-009|R32-001|f99v|f99v.33,+P0|pending_calibration|
|R42C-010|R32-003|f67r2|f67r2.35,@Pb|pending_calibration|
|R42C-011|R32-003|f67r2|f67r2.73,+P0|pending_calibration|
|R42C-012|R32-004|f67v1|f67v1.3,&L0|pending_calibration|
|R42C-013|R32-004|f67v1|f67v1.5,&L0|pending_calibration|
|R42C-014|R32-002|f1r|f1r.21,=Pt|pending_calibration|
|R42C-015|R32-002|f1r|f1r.24,+P0|pending_calibration|
|R42C-016|R32-006|f88v|f88v.17,+P0|pending_calibration|
|R42C-017|R32-006|f88v|f88v.18,+P0|pending_calibration|
|R42C-018|R32-007|f89r2|f89r2.12,@P0|pending_calibration|
|R42C-019|R32-007|f89r2|f89r2.28,+P0|pending_calibration|
