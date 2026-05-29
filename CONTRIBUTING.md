# Contributing

This is a route-based research repository. Contributions should make the next
research step more reproducible, not more speculative.

## Principles

- Keep claims conservative: distinguish observation, inference, and hypothesis.
- Do not describe any result as a decipherment or translation unless it has
  independent falsification and source-backed evidence.
- Prefer small, reviewable changes to route docs, scripts, tests, or derived
  tables.
- Keep visual tooling image-first and human-reviewed. Do not auto-fill human
  confirmation fields from OCR-like inference.
- Do not commit local environment folders, editor state, downloaded raw images,
  caches, or personal agent configuration.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r voynich-codex-project/requirements.txt
cd voynich-codex-project
python -m pytest -q
```

When a route changes the project state, update these together:

- `voynich-codex-project/docs/rotas_de_pesquisa.md`
- the route-specific document under `voynich-codex-project/docs/`
- `voynich-codex-project/project_state.json`
- tests for any script behavior that changed

## Data and images

Use manifests and download scripts for third-party data. Keep source URLs and
attribution notes close to any derived output that depends on them.
