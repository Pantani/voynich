# Voynich Codex Project

Ferramentas, dados de trabalho e diario tecnico para estudar o Manuscrito Voynich
(Beinecke MS 408) de forma reprodutivel e conservadora.

Este repositorio nao apresenta uma decifracao final. O objetivo e organizar
hipoteses estruturais, rotas de pesquisa, scripts de analise e ferramentas de
revisao visual humana para testar ideias sem transformar inferencias em
"traducao".

## Estado atual

- Hipotese de trabalho: o Voynichese se comporta mais como uma notacao/cifra em
  camadas do que como uma lingua natural escrita diretamente.
- Padrao mais forte em estudo: a matriz `ar/al/or/ol`, especialmente quando
  controlada por locus, prefixo e posicao de linha.
- Rota ativa mais recente: R42M, que refina capturas visuais de linhas para
  revisao humana. Ela nao faz OCR, nao traduz e nao confirma glifos sozinha.

## Comeco rapido

```bash
git clone git@github.com:Pantani/voynich.git
cd voynich
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r voynich-codex-project/requirements.txt
cd voynich-codex-project
python -m pytest -q
```

Para baixar dados textuais publicos usados nos experimentos:

```bash
python scripts/download_sources.py
```

Para baixar imagens publicas a partir dos manifests:

```bash
python scripts/download_images.py
```

## Mapa do repositorio

- `resumo_voynich_codex.md`: resumo executivo longo da linha de pesquisa.
- `voynich-codex-project/README.md`: guia operacional do projeto interno.
- `voynich-codex-project/docs/`: rotas de pesquisa, relatorios e ferramentas
  HTML estaticas.
- `voynich-codex-project/scripts/`: analisadores, geradores de pacotes e
  verificadores.
- `voynich-codex-project/data/`: manifests, anotacoes e tabelas derivadas.
- `voynich-codex-project/images/`: espaco local para imagens baixadas e recortes
  gerados.
- `voynich-codex-project/project_state.json`: estado resumido para retomada.

## Contrato de pesquisa

Este repo deve preservar uma separacao clara entre evidencia, inferencia e
hipotese:

- nao afirmar decifracao, traducao ou valor semantico sem teste independente;
- manter rotas, saidas e proximos passos documentados em
  `voynich-codex-project/docs/rotas_de_pesquisa.md`;
- atualizar `voynich-codex-project/project_state.json` quando uma rota muda o
  estado real da investigacao;
- tratar ferramentas visuais como suporte para revisao humana, nao como
  confirmacao automatica.

## Dados, imagens e licenca

O codigo e a documentacao originais deste repositorio estao sob a licenca MIT.
Textos, transcricoes, imagens e datasets de terceiros continuam sujeitos aos
termos das fontes originais. Veja `NOTICE.md` e
`voynich-codex-project/docs/fontes_e_citacoes.md`.

As imagens baixadas em `voynich-codex-project/images/raw/` sao ignoradas pelo Git
por padrao. Recrie-as localmente com os scripts de download.
