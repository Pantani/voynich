# Rota 47: seção vs escriba como preditor do bit a/o

Esta rota testa se o bit a/o (vogal do sufixo) é determinado pelo ESCRIBA (Currier) ou pela SEÇÃO.
Guardrail: `rota47_section_scribe_ao_predictor_not_decipherment`.

## Resultado principal

- V(seção × ao) = **0.2547**
- V(Currier × ao) = **0.4409**

**Currier prevê ao melhor que seção** — sinal é de escriba, não de conteúdo.

## V(Currier × ao) DENTRO de cada seção

Teste decisivo: se V permanece alto dentro da mesma seção → escriba modula ao → M3.

| seção | n | A | B | V(Currier × ao) | veredito |
|-------|---|---|---|-----------------|---------|
| astronomical | 239 | 16 | 223 | 0.0461 | convergem (M5) |
| herbal | 178 | 109 | 69 | 0.5068 | M3 (escriba) |
| balneological | 104 | 0 | 104 | 0.0000 | convergem (M5) |
| pharmaceutical | 78 | 56 | 22 | 0.5627 | M3 (escriba) |
| cosmological | 54 | 1 | 53 | 0.2716 | M3 (escriba) |
| other | 24 | 0 | 24 | 0.0000 | convergem (M5) |
| recipes | 19 | 4 | 15 | 0.4085 | M3 (escriba) |

## Proporção a/o por seção

| seção | n | %a | %o | Currier mix |
|-------|---|----|----|-------------|
| astronomical | 305 | 80% | 20% | A:16 B:223 unknown:66 |
| herbal | 182 | 60% | 39% | A:109 B:69 unknown:4 |
| balneological | 124 | 79% | 20% | B:104 unknown:20 |
| pharmaceutical | 78 | 46% | 53% | A:56 B:22 |
| cosmological | 54 | 79% | 20% | A:1 B:53 |
| other | 24 | 70% | 29% | B:24 |
| recipes | 19 | 63% | 36% | A:4 B:15 |

## Interpretação: modelo de três camadas

Com base nas Rotas 43–47, o sufixo codifica três camadas distintas:

| Camada | Bit | Preditor | Efeito |
|--------|-----|----------|--------|
| **a/o** (vogal) | dialeto/escriba | Currier (V≈0.45) | A=vogal-o; B=vogal-a |
| **r/l** (consoante) | posição sintática | linha/locus | -l=fechamento; -r=continuação |
| prefixo **qo-** | registro | locus_kind | qo-=prosa exclusivo; bare=rótulo+prosa |

A borda não é um rótulo semântico do objeto — é uma composição de três sinalizadores
ortogonais: quem escreve (a/o), onde está na frase (r/l), e em que registro (qo-).

Guardrail: `rota47_section_scribe_ao_predictor_not_decipherment`.