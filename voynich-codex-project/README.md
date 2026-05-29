# Voynich Codex Project

Estudo sistemático do Manuscrito Voynich (Beinecke MS 408) com análise
estatística de corpus EVA, anotação visual IIIF e teoria de cifra.

**Não há decifração final.** O objetivo é testar hipóteses falsificáveis.

---

## Início Rápido

```bash
# 1. Ativar o venv
source /Users/pantani/Desktop/go/src/github.com/Pantani/voynich/.venv/bin/activate

# 2. Baixar transcrição e imagens (uma vez)
python scripts/download_sources.py
python scripts/download_images.py

# 3. Rodar análise principal
python scripts/analyze_form_collocations.py   # Rota 43: collocações ok/ot

# 4. Rodar todos os testes
python -m pytest tests/ -q   # deve mostrar 297+ passed
```

---

## Estrutura do Projeto

```
voynich-codex-project/
│
├── scripts/             ← 60+ scripts CLI Python (ver scripts/README.md)
├── src/voynichkit/      ← Pacote Python com API limpa (corpus, types, constants)
│
├── data/
│   ├── raw/             ← ZL3b-n.txt (corpus EVA principal), voy.b.paged.wds
│   ├── annotations/     ← Planilhas de anotação humana (R32, visual seeds, etc.)
│   ├── derived/         ← CSVs computados (border_matrix, exact_forms, etc.)
│   ├── transcriptions/  ← Trechos EVA manuais (f67r2, f68r3)
│   └── manifests/       ← image_manifest.json, commons_image_sources.csv
│
├── docs/
│   ├── research/        ← Relatórios individuais de cada Rota (rota_1.md … rota_43.md)
│   ├── foundations/     ← Hipóteses, glossário, fontes, log de ataques
│   ├── summaries/       ← Resumo executivo, mapa de rotas de pesquisa
│   └── tools/           ← Ferramentas HTML ativas (R42B, R42C, R42G, etc.)
│
├── images/
│   ├── raw/yale_iiif_r32/ ← 8 JPEGs Yale IIIF high-res (f1r, f67r2, f84r, f99v…)
│   └── derived/           ← Recortes SVG e derivados
│
├── tests/               ← 297+ testes pytest
├── notebooks/           ← Jupyter notebooks (em branco)
│
├── CLAUDE.md            ← Harness + regras do projeto para Claude
├── CODEX_PROMPT.md      ← Prompt de continuação para o Codex local
└── project_state.json   ← Estado completo do projeto (gerado automaticamente)
```

---

## Hipótese Principal

O Voynichese é provavelmente um **sistema formal em camadas**:

```
[token visível] = operador_de_modo + núcleo/template + valor_de_borda
```

| Componente | Exemplos | Status |
|-----------|----------|--------|
| Operadores | `ok-`, `ot-`, `qo-`, `yk-`, `yt-` | Forte evidência |
| Núcleos | `ch`, `sh`, `d` | Plausível |
| Bordas | `-ar`, `-al`, `-or`, `-ol`, `-dy` | Forte evidência |
| Matriz 2×2 | `ar/al/or/ol` | Estatisticamente confirmada |

**Achado mais recente (Rota 43):** formas `-ar` encerram loci com standalone `ar` a **15.4%** vs **6.8%** para `-al/-ol` — chi²=10.54, p≈0.001.

---

## Resultados Estatísticos Consolidados

| Teste | Métrica | Valor |
|-------|---------|-------|
| `locus × suffix` | Cramer's V | 0.0780 (p≤0.002) |
| `prefix × suffix` | Cramer's V | **0.1682** (p≤0.002) |
| `line_position × suffix` | Cramer's V | 0.0978 (p≤0.002) |
| `a/o axis (prefix)` | Cramer's V | **0.2607** |
| `r/l axis (prefix)` | Cramer's V | 0.1179 |
| `-ar forms → standalone` | chi²(1df) | **10.54** (p≈0.001) |

---

## Documentação

| Documento | Localização |
|-----------|-------------|
| Resumo executivo | `docs/summaries/resumo_executivo_pt.md` |
| Hipóteses e modelos | `docs/foundations/hipoteses_e_modelos.md` |
| Glossário EVA/IVTFF | `docs/foundations/glossario_voynich.md` |
| Mapa de todas as rotas | `docs/summaries/rotas_de_pesquisa.md` |
| Log completo de ataques | `docs/foundations/log_dos_ataques.md` |
| Ferramentas HTML ativas | `docs/tools/rota_42g_ferramentas_ativas_r32.html` |
| Índice de scripts | `scripts/README.md` |

---

## Usar o Pacote voynichkit

```python
from voynichkit import read_border_matrix, read_exact_forms, FORMS, BORDER

# Carregar corpus completo (5.385 loci, 41.005 tokens)
rows = read_border_matrix()

# Filtrar formas exatas
exact = [r for r in rows if r['token'] in FORMS]

# Ver as constantes
print(FORMS)     # ['okal', 'okar', 'okol', ...]
print(BORDER)    # frozenset({'ar', 'al', 'or', 'ol'})
```

---

## Manifestos de Imagem

- `data/commons_image_sources.csv` — usado por `download_images.py`
- `data/manifests/image_manifest.json` — manifesto detalhado com thumbnails

---

## Time de Especialistas (Harness)

O projeto tem um harness de agentes em `.claude/`:

| Agente | Papel |
|--------|-------|
| `linguistics-coordinator` | Líder, rigor científico, síntese |
| `corpus-statistician` | Scripts Python, chi², Cramer's V |
| `cryptanalyst` | Modelos de cifra, predições testáveis |
| `paleographer` | Contexto do manuscrito, seções, Currier A/B |
| `visual-annotator` | Imagens Yale IIIF, anotação R32 |
| `repo-architect` | Organização do repo, voynichkit, docs/ |

Trigger: skill `voynich-research` coordena o time para qualquer tarefa.
