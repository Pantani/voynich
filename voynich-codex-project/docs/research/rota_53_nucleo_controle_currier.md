# Rota 53: o núcleo ch/sh segue conteúdo — confirmado em todo o corpus

Guardrail: `rota53_nucleus_content_signal_not_decipherment`.

A Rota 52 detectou o sinal no subconjunto de 786 formas exatas. A Rota 53
repete o teste em **todo o corpus ZL3b** e adiciona o controle de confundidor
(seção dentro de um único escriba).

## Resultado decisivo

| Preditor de ch/sh | V de Cramér | n |
|-------------------|-------------|---|
| **Seção (conteúdo)** | **0.1415** | 14594 |
| Currier (escriba) | 0.0619 | 13574 |
| Seção \| Currier=B | **0.1571** | 8738 |
| Seção \| Currier=A | 0.0480 | 4836 |

Permutação (seção): p = 0.001996 (500 embaralhamentos).

**Veredito:** seção (0.142) supera Currier (0.062), e o sinal de seção **sobrevive** dentro de Currier B (0.157).
O núcleo ch/sh é o primeiro elemento do token que responde ao CONTEÚDO.

## ch/sh por seção

| seção | n | %ch | %sh |
|-------|---|-----|-----|
| herbal | 4874 | 74.1% | 25.9% |
| recipes | 4184 | 74.6% | 25.4% |
| balneological | 2520 | 57.5% | 42.5% |
| pharmaceutical | 1333 | 70.7% | 29.3% |
| astronomical | 987 | 76.7% | 23.3% |
| cosmological | 696 | 66.7% | 33.3% |

## ch/sh por Currier

| Currier | n | %ch | %sh |
|---------|---|-----|-----|
| B | 8738 | 68.4% | 31.6% |
| A | 4836 | 74.3% | 25.7% |

## Interpretação

- O **balneológico** (ninfas/água/corpo) é a seção mais carregada de **sh**;
  herbal e astronômico (plantas/estrelas/objetos) pendem para **ch**.
- O sinal vive sobretudo no corpus **B** (V_B alto, V_A baixo): é em B que a
  diversidade de conteúdo existe — A é quase só herbal, sem variância de seção.
- A assimetria A/B reforça que o efeito é de **conteúdo**, não de mão: se fosse
  hábito motor do escriba, A e B teriam o mesmo perfil dentro de cada seção.

**Ressalvas:**
1. V≈0.14 é efeito moderado — é estrutura de conteúdo, não um lexema isolado.
2. "Segue conteúdo" ≠ "tem semântica conhecida". Nada de tradução.
3. ch/sh é binário de banco; banco-gallows (cth/ckh/cph/cfh) ficam fora do teste.

## Próximo passo — Rota 54

- Isolar QUAL contexto dentro do balneológico puxa sh (loci de ninfa vs texto).
- Testar se o par ch/sh interage com o operador ok/ot (núcleo × operador).
- Entropia condicional H(próximo glifo | ch) vs H(próximo glifo | sh).

Guardrail: `rota53_nucleus_content_signal_not_decipherment`.