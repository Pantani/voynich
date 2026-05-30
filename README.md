# Voynich Codex Project

A reproducible, conservative research toolkit and technical journal for studying
the Voynich Manuscript (Beinecke MS 408).

This repository does **not** present a final decipherment. Its goal is to
organize structural hypotheses, research routes, analysis scripts, and
human-in-the-loop visual-review tools so that ideas can be tested without turning
inference into "translation."

## Current state

The main research line — *"what is Voynichese?"* (routes R43–R71) — is now
**closed**:

- **Working model.** Voynichese behaves as a **morphologically rich,
  syntactically thin** token system: a restricted generative process (templatic
  operators `qo-/ok-/ot-` plus matrix borders) over a weak prose-topic layer,
  with the text statistically **decoupled from the images**.
- **Capstone (R62 / R67).** A *local, content-free* generator reproduces 13 of
  14 statistical signatures of the corpus — effectively 14/14 once the last
  residue (LAAFU) is shown to be page **layout**, not content. **Meaning is
  therefore not *necessary* to explain the statistics** — which is not the same
  as proving the text is meaningless. The statistical line is exhausted.
- **Remaining uncertainty is provenance/material, not statistics.** Current
  priors: content-free generator ≈ 70% · constructed system/notation ≈ 22% ·
  recoverable cipher ≈ 8%. Only an external key or a held-out decode could move
  the meaning question.
- **No decipherment or translation is claimed** anywhere in this arc; every
  result ships with an explicit guardrail.

Long-form summary: [`resumo_voynich_codex.md`](resumo_voynich_codex.md).
Consolidated closure report:
[`docs/summaries/relatorio_R43_R61_natureza_do_voyniches.md`](voynich-codex-project/docs/summaries/relatorio_R43_R61_natureza_do_voyniches.md).

## Working hypothesis

Each visible token is modeled as a layered form rather than a single substituted
symbol:

```
[visible token] = mode operator + nucleus/template + border value
```

| Component   | Examples                        | Status                    |
|-------------|---------------------------------|---------------------------|
| Operators   | `ok-`, `ot-`, `qo-`, `yk-`, `yt-` | Strong evidence         |
| Nuclei      | `ch`, `sh`, `d`                 | Plausible (lexically fixed) |
| Borders     | `-ar`, `-al`, `-or`, `-ol`, `-dy` | Strong evidence         |
| 2×2 matrix  | `ar / al / or / ol`             | Statistically confirmed   |

The `a/o` axis carries most of the textual structure; the `r/l` axis is weaker
and may be visual/diagrammatic.

### Selected statistical results

| Test                     | Metric      | Value              |
|--------------------------|-------------|--------------------|
| `prefix × suffix`        | Cramér's V  | 0.1682 (p ≤ 0.002) |
| `a/o axis (prefix)`      | Cramér's V  | 0.2607             |
| `r/l axis (prefix)`      | Cramér's V  | 0.1179             |
| `line_position × suffix` | Cramér's V  | 0.0978 (p ≤ 0.002) |
| `locus × suffix`         | Cramér's V  | 0.0780 (p ≤ 0.002) |
| `-ar` forms → standalone | χ² (1 df)   | 10.54 (p ≈ 0.001)  |

## Quick start

```bash
git clone git@github.com:Pantani/voynich.git
cd voynich
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r voynich-codex-project/requirements.txt

cd voynich-codex-project
PYTHONPATH=. python -m pytest -q   # 650+ tests
```

Python ≥ 3.10 is required. Core dependencies: `requests`, `pandas`,
`matplotlib`, `pytest`.

Download the public text corpus used by the experiments:

```bash
python scripts/download_sources.py   # fetches ZL3b-n.txt from voynich.nu
```

Download public folio images from the manifests:

```bash
python scripts/download_images.py
```

Run a single route script:

```bash
PYTHONPATH=. python scripts/analyze_form_collocations.py
```

## Repository map

```
voynich/
├── README.md                   ← you are here
├── resumo_voynich_codex.md     ← long-form executive summary
├── CONTRIBUTING.md · NOTICE.md · CITATION.cff · LICENSE
└── voynich-codex-project/      ← all research code, data, and docs
    ├── scripts/        ← 80+ route scripts (one per step; flat — do not move)
    ├── src/voynichkit/ ← Python package: clean API (corpus, types, constants)
    ├── data/
    │   ├── raw/            ← ZL3b-n.txt (main EVA corpus)
    │   ├── annotations/    ← human-fill sheets (pipeline gates)
    │   ├── derived/        ← computed CSVs (never edit by hand)
    │   ├── transcriptions/ ← small manual EVA seeds
    │   └── manifests/      ← image manifests & source lists
    ├── docs/
    │   ├── research/    ← one report per route (rota_1 … rota_71)
    │   ├── foundations/ ← hypotheses, glossary, sources, attack log
    │   ├── summaries/   ← executive summary, route map, closure report
    │   └── tools/       ← static HTML review/calibration tools
    ├── images/         ← downloaded folios (raw/, git-ignored) + derived crops
    ├── tests/          ← 650+ pytest tests
    └── project_state.json ← machine-readable snapshot of all route outputs
```

The internal project keeps its own operational guide:
[`voynich-codex-project/README.md`](voynich-codex-project/README.md).

### Key documents

| Document                | Location                                                                 |
|-------------------------|--------------------------------------------------------------------------|
| Route map (all routes)  | [`docs/summaries/rotas_de_pesquisa.md`](voynich-codex-project/docs/summaries/rotas_de_pesquisa.md) |
| R43–R61 closure report  | [`docs/summaries/relatorio_R43_R61_natureza_do_voyniches.md`](voynich-codex-project/docs/summaries/relatorio_R43_R61_natureza_do_voyniches.md) |
| Hypotheses and models   | [`docs/foundations/hipoteses_e_modelos.md`](voynich-codex-project/docs/foundations/hipoteses_e_modelos.md) |
| EVA/IVTFF glossary      | [`docs/foundations/glossario_voynich.md`](voynich-codex-project/docs/foundations/glossario_voynich.md) |
| Attack log              | [`docs/foundations/log_dos_ataques.md`](voynich-codex-project/docs/foundations/log_dos_ataques.md) |
| Sources and citations   | [`docs/foundations/fontes_e_citacoes.md`](voynich-codex-project/docs/foundations/fontes_e_citacoes.md) |
| Script index            | [`scripts/README.md`](voynich-codex-project/scripts/README.md) |

## Using the voynichkit package

```python
from voynichkit import read_border_matrix, read_exact_forms, FORMS, BORDER

rows = read_border_matrix()                 # full corpus (5,385 loci, 41,005 tokens)
exact = [r for r in rows if r["token"] in FORMS]

print(FORMS)   # ['okal', 'okar', 'okol', ...]
print(BORDER)  # frozenset({'ar', 'al', 'or', 'ol'})
```

The package exposes the readers `read_border_matrix`, `read_exact_forms`,
`read_zl3b_raw`; the constants `FORMS`, `BORDER`, `OPERATORS`, `CLOSURES`; and the
types `Token`, `Locus`, `MatrixCandidate`.

## Research contract

This repository keeps a strict separation between **evidence, inference, and
hypothesis**:

- Do not claim decipherment, translation, or semantic value without independent
  falsification and source-backed evidence.
- Keep routes, outputs, and next steps documented in
  [`docs/summaries/rotas_de_pesquisa.md`](voynich-codex-project/docs/summaries/rotas_de_pesquisa.md).
- Update
  [`project_state.json`](voynich-codex-project/project_state.json)
  whenever a route changes the real state of the investigation.
- Treat visual tooling as support for human review, never as automatic
  confirmation — never auto-fill human annotation fields from OCR-like inference.

See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the full contribution guidelines.

## Data, images, and license

Original code and documentation in this repository are released under the **MIT
License** (see [`LICENSE`](LICENSE)). Third-party texts, transcriptions, images,
and datasets remain subject to the terms of their original sources — see
[`NOTICE.md`](NOTICE.md) and
[`docs/foundations/fontes_e_citacoes.md`](voynich-codex-project/docs/foundations/fontes_e_citacoes.md).

Images downloaded into `voynich-codex-project/images/raw/` are git-ignored by
default; recreate them locally with the download scripts.
