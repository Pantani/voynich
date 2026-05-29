# Imagens

Este diretório recebe as imagens baixadas.

Para baixar as quatro imagens principais em domínio público do Wikimedia Commons:

```bash
python scripts/download_images.py
```

Para baixar também imagens de pré-visualização do VIB/Yale listadas em `data/image_sources.csv`:

```bash
python scripts/download_images.py --include-supplemental
```

As imagens binárias não foram embutidas neste pacote; os manifests contêm URLs diretas e páginas de origem.
