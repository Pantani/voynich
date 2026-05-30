# Rota 62: um gerador local sem conteúdo reproduz QUASE tudo — capstone da linha

Guardrail: `rota62_generator_not_decipherment`.

O teste de adequação de modelo (item nº 1 do trabalho futuro do relatório consolidado).
Pergunta construtiva: existe um **processo gerativo LOCAL e SEM CONTEÚDO** que reproduza
SIMULTANEAMENTE todas as assinaturas estatísticas do Voynichês? Se sim, a parcimônia mostra
que **sentido não é NECESSÁRIO** para explicar as estatísticas. 2 legs: statistician
(constrói o gerador + ablação) + cryptanalyst (pré-registro cego).

## O gerador-mínimo

Processo local, mesma geometria (5.216 linhas, ~37,6k tokens), mecanismos ablatáveis:
1. **base** — amostra tokens REAIS i.i.d. da frequência-unigrama + distribuição real de
   tamanhos de linha. (Reproduz Zipf/Heaps/h2 por construção — match trivial, NÃO conta.)
2. **section_cond** — frequências de palavra CONDICIONADAS À SEÇÃO (tabela de vocabulário de
   tópico — para a cauda topical fraca da R56/R59). Não é sintaxe, é tabela.
3. **self_citation** — com prob `p_rep=0.0046`, repete um token recente (para a repetição adjacente).
4. **line_edge_bias** — enviesa tokens line-iniciais para gallows, line-finais para a distribuição real.

## Tabela de aderência (real vs gerador completo)

| métrica | real | gerador | casa? |
|---------|------|---------|-------|
| h2 (caractere) | 2.153 | 2.227 | ✅ |
| repetição adjacente | 0.875% | 0.873% | ✅ |
| **LAAFU I(palavra;posição)** | **0.471** | **0.303** | **❌ (Δ 0.17)** |
| comprimento de correlação I(d) | 15 | 12 | ✅ |
| Zipf slope | −1.079 | −0.994 | ✅ |
| Heaps β | 0.786 | 0.742 | ✅ |
| gain_over_wordunigram | 0.034 | 0.008 | ✅ |

**13/14 métricas casam (6/7 das principais).** Todos os 6 checkpoints de I(d) (d=1…100) casam.

**Ablação — cada mecanismo liga sua assinatura:** self_citation eleva a repetição do piso
i.i.d. (0.0028→0.0096); section_cond liga a cauda de compressibilidade (gain −0.012→0.014);
line_edge_bias liga o gallows-inicial (0.041→0.191) e empurra LAAFU (0.205→0.303).

## O único resíduo: LAAFU (ligação palavra↔posição)

**Veredito: `generator_insufficient` — mas por uma só assinatura.** O gerador produz LAAFU
(I=0.30, bem acima de zero) mas não alcança o real (0.47): o corpus liga **tokens inteiros
ESPECÍFICOS** à posição de linha mais fortemente do que um viés de glifo-de-borda consegue.
Para casar, o gerador precisaria de uma **tabela de posição-de-linha por token** — ainda um
mecanismo SEM CONTEÚDO, só com mais parâmetros (uma regra de layout mais rica, não sintaxe).

## Leitura integrada — o que isto licencia (e o que NÃO)

> Um gerador local sem conteúdo reproduz QUASE todo o perfil estatístico do Voynichês —
> **sentido NÃO é NECESSÁRIO para explicar as estatísticas.** A única assinatura que resiste
> (LAAFU) é uma regra POSICIONAL mais rica (palavras-tipo presas à borda de linha), ainda
> não-semântica — consistente com hábito escribal de layout, não com sintaxe.

**Ponto epistêmico (cryptanalyst):** isto é uma **prova de existência** de uma explicação
sem-sentido, NÃO uma prova de unicidade. Sentido-não-é-necessário **≠ texto é sem sentido**:
um texto com sentido PODE compartilhar estas estatísticas. Gerador vs "conteúdo engenheirado
para imitar um gerador" é **degenerado na escala do token** — indistinguível por estatística
de corpus. (Armadilha sinalizada: Zipf/Heaps/h2 casam trivialmente porque a base reamostra
palavras reais; o peso do veredito está nas assinaturas SEQUENCIAIS — repetição ✅, I(d) ✅,
gain ✅, LAAFU ❌.)

**Priores atualizados (cryptanalyst):** gerador/baixo-conteúdo ~55%→**~70%**, construída
~30%→~22%, cifra ~15%→~8%. NÃO 100%: gerador e construída/cifra são degenerados nesta
resolução; e um texto deliberadamente engenheirado passaria exatamente nesta bateria.

## META — a linha estatística está EXAURIDA

> O "o que é o Voynichês" está respondido **até onde a estatística de corpus pode responder.**
> Quase todo o perfil é gerável sem conteúdo; o resíduo de LAAFU é layout, não sentido. Mais
> trabalho na escala do token é **degenerado por construção** (não separa "sem conteúdo" de
> "conteúdo invisível a estes testes"). A incerteza remanescente é **proveniência/material
> (mão, tinta, caderno, datação, processo escribal)** — não estatística.

**Recomendação (ambos especialistas):** parar a linha estatística aqui; o relatório
consolidado (R43–61 + este capstone R62) é o artefato de fechamento. O que avançaria é
evidência física/proveniência, ou — se o usuário quiser — mudar de frente (anotação visual
IIIF, R32+).

Guardrail: `rota62_generator_not_decipherment`.
Script: `scripts/analyze_generator.py`; testes: `tests/test_generator.py` (suíte **479**).
Saídas: `data/derived/generator_{match,ablation,summary}_zl3b.csv`.
