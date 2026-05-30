# Rota 59: morfologicamente rico, sintaticamente fino — correlação de longo alcance

Guardrail: `rota59_long_range_not_decipherment`.

O separador único. A Rota 58 mostrou que toda estatística LOCAL (h2, LAAFU, repetição) é
reproduzível por todo candidato. Só a **correlação de longo alcance** separa língua real
codificada (decai como lei de potência, persiste) de gerador local (colapso exponencial).
2 legs: statistician (mede I(d), ajusta, controla por embaralhamento-de-linha + Zipf/Heaps)
e cryptanalyst (pré-registra limiares cego + flagueia a armadilha de interpretação).

## A curva de informação mútua de caractere I(d)

Piso de viés (nulo) = 0.00179 bits (caractere é bem amostrado → viés ínfimo, como previsto).

| d | excess I(d) | nota |
|---|-------------|------|
| 1 | **1.717** | dependência intra-token enorme |
| 2 | 0.827 | |
| 5 | 0.127 | |
| 10 | 0.019 | |
| **15** | **0.0055** | ≈ piso — **comprimento de correlação = 15** |
| 50 | 0.0019 | cauda fina |
| 100 | 0.0007 | quase no piso |

**Curva de DOIS regimes:** (1) queda local íngreme de d=1 a ~15 (cai a ~floor), depois
(2) uma cauda persistente fraquíssima. Ajuste: lei de potência γ=1.16, R²=0.76 **vence** o
exponencial (ξ=58, R²=0.35) — mas vence sobretudo pela dominância de d=1; o comprimento de
correlação real é curto (**15**, abaixo do limiar de 50 pré-registrado) → veredito mecânico
**`ambiguous`**.

## O controle de embaralhamento-de-linha (decisivo)

Embaralhar a ORDEM das linhas (preservando cada linha por dentro):
- d=1–10: real ≈ embaralhado → o regime local íngreme é **INTRA-linha** (morfologia da
  palavra, intacta sob embaralhamento).
- d=50–150: real (0.0037) > embaralhado (≈piso 0.0019), ratio_d50 = **17.85** → a cauda
  fraca de longo alcance é **CROSS-linha** e MORRE quando a ordem das linhas é destruída →
  é estrutura de **tópico/documento** (= o vocabulário de prosa por seção da R56), **não**
  dependência sequencial/sintática.

Zipf slope = **−1.079** (≈ língua natural); Heaps β = **0.786** (ALTO, acima da faixa
natural 0.4–0.6 → vocabulário muito produtivo, gerando muitas formas — bate com a morfologia
rígida que multiplica tokens).

## Leitura integrada — o achado mais coerente do projeto

> **Voynichês é morfologicamente RICO e sintaticamente FINO.**
>
> - **Estrutura local forte (d<15):** a dependência intra-token (I=1.72 bits em d=1, decai a
>   ~15 caracteres ≈ a escala de um token) é exatamente a gramática rígida de formação de
>   palavra mapeada nas R43–55 (qo-+ok/ot+ch/sh+vogal+consoante). É a fonte do h2 baixo.
> - **Cauda de tópico fraca e CROSS-linha (d>15):** a única estrutura de longo alcance é o
>   agrupamento de vocabulário por seção (R56) — fraquíssima (mal acima do piso) e morre sob
>   embaralhamento de linha. Não é sintaxe.
> - **Sem dependência de médio alcance (d≈20–100):** o regime que a prosa de língua natural
>   POSSUI (dependências de frase/sentença) está **ausente** no Voynichês.

**O que isto descarta e o que sobra:**
- **Descarta prosa de língua natural rica:** comprimento de correlação ~15 é curto demais;
  prosa natural mantém MI forte até d≫50. (Nuance vs Lin&Tegmark 2017, que reportaram
  lei-de-potência tipo-língua: nosso controle de embaralhamento-de-linha revela que a cauda
  longa é estrutura de documento/tópico, não sequencial — qualifica a afirmação "tipo-língua".)
- **Desfavorece gerador de Markov local SIMPLES** fracamente: a cauda de tópico existe (um
  Markov estacionário puro não a teria) — mas um gerador POR-SEÇÃO a produziria.
- **Mais consistente com:** um sistema dominado por **formação rígida de palavra + deriva
  fraca de vocabulário por tópico, sem sintaxe de sentença** — i.e. **construído / codificado
  / gerador templático com uma camada fina de conteúdo topical** (a hipótese híbrida).

**Prior atualizado (cryptanalyst):** o resultado (lei-de-potência ganha o ajuste, MAS cauda
longa é cross-linha/tópico e curta) puxa para longe tanto de "prosa natural rica" quanto de
"Markov simples", e mantém o leque {real-codificada / construída / gerador} com peso híbrido.

## Rota 60 — teste decisivo (ramo lei-de-potência): COMPRESSIBILIDADE condicional

A estrutura de longo alcance que existe é INFORMAÇÃO ou só TEXTURA? Comprimir o corpus e
comparar bits/token contra:
1. um **resample de Markov ordem-2 do próprio Voynich** (mesma estatística local, sem longo alcance),
2. língua natural casada em tamanho/Zipf,
3. uma expansão de cifra-verbosa/homofônica de texto real.

**Discriminador:** se o Voynich comprime ≈ como seu gêmeo-Markov (sem ganho residual do
longo alcance) → a estrutura de longo alcance é **textura, não informação** →
construído/gerador. Se comprime MELHOR que o gêmeo-Markov (longo alcance remove redundância
real, como em língua/cifra-verbosa) → **língua real codificada** segue viva. Pergunta direta:
o longo alcance carrega sinal decodificável?

Guardrail: `rota59_long_range_not_decipherment`.
Script: `scripts/analyze_long_range.py`; testes: `tests/test_long_range.py` (suíte **430**).
Saídas: `data/derived/long_range_{mi,summary}_zl3b.csv`.
