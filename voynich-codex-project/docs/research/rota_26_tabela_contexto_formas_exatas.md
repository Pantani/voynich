# Rota 26: tabela ampliada das formas exatas ok/ot

Esta rota isola `okar/okal/okor/okol/otar/otal/otor/otol` e junta contexto textual com anotacao visual quando existe chave exata folio/locus/token.

Contexto textual: `voynich-codex-project/data/derived/border_matrix_context_zl3b.csv`.
Anotacao visual: `voynich-codex-project/data/annotations/visual_annotations_seed_zl3b.csv`.
Tabela ampliada: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/exact_form_context_table_zl3b.csv`.
Resumo derivado: `/Users/pantani/Desktop/go/src/github.com/Pantani/voynich/voynich-codex-project/data/derived/exact_form_context_summary_zl3b.csv`.

## Resultado curto

- ocorrencias exatas: 786;
- `ok*`: 394;
- `ot*`: 392;
- com anotacao visual exata: 23;
- sem anotacao visual exata: 763;
- guarda: `exact_form_context_not_decipherment`.

### Formas

|item|n|
|---|---:|
|okal|152|
|otar|147|
|okar|133|
|otal|129|
|otol|79|
|okol|75|
|otor|37|
|okor|34|

### Prefixos

|item|n|
|---|---:|
|ok|394|
|ot|392|

### Sufixos

|item|n|
|---|---:|
|al|281|
|ar|280|
|ol|154|
|or|71|

### Locus

|item|n|
|---|---:|
|P|664|
|C|69|
|L|45|
|R|8|

### Posicao na linha

|item|n|
|---|---:|
|middle|666|
|start|52|
|end|42|
|single|26|

### Match visual

|item|n|
|---|---:|
|no_visual_annotation|763|
|matched_visual_annotation|23|

## Primeiras ocorrencias

|rota26|token|folio|locus|locus_kind|posicao|visual_zone|objeto proximo|match|
|---|---|---|---|---|---|---|---|---|
|R26-0001|otol|f1r|f1r.21,=Pt|P|start|||no_visual_annotation|
|R26-0002|okol|f1r|f1r.24,+P0|P|middle|||no_visual_annotation|
|R26-0003|okol|f1v|f1v.9,+P0|P|middle|||no_visual_annotation|
|R26-0004|okol|f2r|f2r.12,+P0|P|start|||no_visual_annotation|
|R26-0005|okol|f3r|f3r.20,+P0|P|middle|||no_visual_annotation|
|R26-0006|okor|f3v|f3v.2,+P0|P|middle|||no_visual_annotation|
|R26-0007|okal|f3v|f3v.4,+P0|P|middle|||no_visual_annotation|
|R26-0008|otor|f4v|f4v.8,+P0|P|middle|||no_visual_annotation|
|R26-0009|otol|f5r|f5r.2,+P0|P|end|||no_visual_annotation|
|R26-0010|otol|f5v|f5v.4,+P0|P|middle|||no_visual_annotation|
|R26-0011|otol|f5v|f5v.6,+P0|P|start|||no_visual_annotation|
|R26-0012|okor|f6v|f6v.5,+P0|P|middle|||no_visual_annotation|
|R26-0013|okol|f6v|f6v.20,+P0|P|middle|||no_visual_annotation|
|R26-0014|okar|f8r|f8r.18,+P0|P|start|||no_visual_annotation|
|R26-0015|otol|f8v|f8v.1,@P0|P|middle|||no_visual_annotation|
|R26-0016|okol|f8v|f8v.14,+P0|P|middle|||no_visual_annotation|
|R26-0017|okor|f9r|f9r.3,+P0|P|middle|||no_visual_annotation|
|R26-0018|otar|f9r|f9r.4,+P0|P|middle|||no_visual_annotation|
|R26-0019|otol|f9v|f9v.4,+P0|P|middle|||no_visual_annotation|
|R26-0020|otol|f10r|f10r.8,+P0|P|middle|||no_visual_annotation|
|R26-0021|otor|f10r|f10r.10,+P0|P|middle|||no_visual_annotation|
|R26-0022|otol|f11r|f11r.6,+P0|P|middle|||no_visual_annotation|
|R26-0023|otol|f13v|f13v.1,@P0|P|middle|||no_visual_annotation|
|R26-0024|okal|f13v|f13v.7,+P0|P|middle|||no_visual_annotation|
|R26-0025|otal|f13v|f13v.9,+P0|P|middle|||no_visual_annotation|
|R26-0026|okol|f14r|f14r.2,+P0|P|end|||no_visual_annotation|
|R26-0027|okor|f14r|f14r.6,+P0|P|middle|||no_visual_annotation|
|R26-0028|otol|f16r|f16r.8,+P0|P|middle|||no_visual_annotation|
|R26-0029|okal|f16r|f16r.10,+P0|P|end|||no_visual_annotation|
|R26-0030|otor|f16v|f16v.12,+P0|P|middle|||no_visual_annotation|

## Leitura

A tabela melhora a rastreabilidade das oito formas exatas, mas nao atribui significado aos eixos `ok/ot` ou `ar/al/or/ol`. Linhas sem anotacao visual permanecem como lacuna, nao como evidencia negativa.
