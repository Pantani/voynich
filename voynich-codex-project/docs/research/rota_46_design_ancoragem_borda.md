# Rota 46 — Design: Teste de Ancoragem da Borda (objeto vs escriba)

Guardrail: `rota46_border_anchor_object_vs_scribe_not_decipherment`.

## Objetivo

Discriminar entre dois modelos sobreviventes:

| Modelo | Predição |
|--------|----------|
| **M5 — Atributo-do-objeto** | bit a/o determinado pelo objeto visual; V(a/o\|objeto) ≈ 0 |
| **M3 — Morfema de dialeto** | bit a/o determinado pelo escriba; V(a/o\|objeto) ≈ 0.44 |

## Desenho em três camadas

### Camada 1 — Estratificação central (teste Currier × a/o por tipo de objeto)

Fonte: seção astronômica f67–f73, que é a única com A e B misturados.
Usar as anotações de estrela do corpus (`section_note`: dotted/plain/8-pointed/7-pointed/tail).

```
Para cada tipo de estrela com n ≥ 10:
  calcular V(Currier × bit_ao)
```

- Se V cai para < 0.10 dentro dos estratos → objeto determina a borda (M5)
- Se V permanece ≥ 0.30 dentro dos estratos → escriba determina a borda (M3)
- Threshold falsificação M5: V ≥ 0.12 com n ≥ 30

### Camada 2 — Objeto repetido entre dialetos

Identificar o mesmo tipo de objeto pictórico em fólios A e fólios B:
- Mesmo tipo de estrela em f69r (Currier B, 49 rótulos) vs herbal A (f1r–f66)
- Mesmo rótulo farmacêutico em f99r (A) vs f103r–f116v (B, receitas)

Se o mesmo objeto recebe sufixo-a em B e sufixo-o em A → dialeto (M3)
Se recebe sufixo similar independente do Currier → atributo (M5)

### Camada 3 — Entropia condicional

Calcular H(bit_ao | objeto) vs H(bit_ao | Currier):
- H menor condicional ao objeto → objeto é melhor preditor → M5
- H menor condicional ao Currier → escriba é melhor preditor → M3

## Fólios alvo

| Fólio | Tipo | Currier | n rótulos estrela | Prioridade |
|-------|------|---------|------------------|-----------|
| f69r | círculo de estrelas rotuladas | B (puro) | 49 | **P0** |
| f68r1 | estrelas com labels | misto | 37 | P0 |
| f73r/f73v | zodíaco final | misto | 33/33 | P1 |
| f99r | farmacêutico labels | A | ~14 (top row) | P1 |

## Dados necessários

- `data/derived/exact_form_context_table_currier_zl3b.csv` (já gerado, tem coluna `currier`)
- Anotação de tipo de objeto por locus (existente em `section_note` para estrelas)

## Script a criar

`scripts/analyze_border_anchor.py` — Rota 46

Saídas:
- `data/derived/border_anchor_stratified_zl3b.csv`
- `data/derived/border_anchor_summary_zl3b.csv`
- `docs/research/rota_46_ancoragem_borda.md`

## Predição refinada do cryptanalyst

O resultado mais informativo possível seria:
- **bit a/o** ancora no **objeto** (V cai) → componente de atributo
- **bit r/l** ancora no **escriba** (V permanece) → componente de convenção

Isso unificaria M5 e M3: borda bidimensional com um bit de atributo + um bit de convenção.
