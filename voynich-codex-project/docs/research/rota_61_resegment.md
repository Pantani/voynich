# Rota 61: re-segmentação NÃO revela sintaxe escondida — a cifra verbosa não ganha apoio

Guardrail: `rota61_resegment_not_decipherment`.

A última falsificação decisiva da linha "o que é o Voynichês". A única hipótese
"com sentido" sobrevivente após a R60 era a **cifra verbosa**: 1 palavra de texto-claro →
muitos tokens Voynich, escondendo a sintaxe ABAIXO da grade de tokens. Teste: re-segmentar
(BPE) o fluxo de caracteres e ver se a estrutura de ORDEM revive — **diferencialmente** vs
substitutos casados em estrutura (Markov-2 de char, saco-de-palavras), porque BPE fabrica
estrutura aparente em QUALQUER texto. 2 legs: statistician (BPE + diferencial) + cryptanalyst
(pré-registro cego).

## O resultado — e por que o bz2 foi decisivo

| compressor | revival_voy (BPE) | markov2 | saco-de-palavras | **diferencial** | ratio voy/bow |
|------------|-------------------|---------|------------------|-----------------|---------------|
| lzma | 0.083 | 0.034 | 0.049 | **0.035** | 1.72× |
| **bz2** | 0.074 | 0.057 | 0.069 | **0.005** | **1.07×** |

A re-segmentação revive ganho de ordem no Voynich (0.083 lzma) acima dos substitutos — MAS
**só no lzma.** No bz2 o diferencial **colapsa de 0.035 para 0.005** e o Voynich revive
praticamente o mesmo que seu próprio saco-de-palavras (1.07×). **É exatamente o padrão da
R60** (lzma 0.034 → bz2 0.008): um ganho lzma perto do limiar que o bz2 mata = **artefato de
compressor**, não estrutura.

**Veredito robusto (ambos compressores): `lzma_artifact` → `no_hidden_structure`.** A
re-segmentação NÃO recupera estrutura de ordem além do que a morfologia rígida produz
mecanicamente (os substitutos revivem quase tanto). A grade de tokens é, para efeitos
estatísticos, a unidade natural; a fineza sintática é **fundamental**, não artefato de
tokenização.

**`cross_boundary_merge_frac` = 0.49** (metade dos units re-segmentados engole um antigo
espaço) é DESCRITIVO mas NÃO evidência: a morfologia rígida (palavras começam qo-/ok-,
terminam -y/-dy/-aiin) torna as fronteiras entre tokens previsíveis, então o Markov-2 produz
os MESMOS merges cruzados — eles cancelam no diferencial. Só EXCESSO de ordem contaria, e não há.

## O método foi o herói (capstone)

O statistician retornou `hidden_structure` pelo critério mecânico lzma-only (0.035 > 0.03).
O cryptanalyst, **cego aos números**, havia pré-registrado o resultado oposto — "aceitar
estrutura escondida só se o diferencial sobreviver em lzma E bz2; a R60 me queimou com um
0.034 lzma que o bz2 matou em 0.008 — não serei enganado duas vezes" — e previu
`no_hidden_structure`. O **cross-check de bz2 confirmou a predição cega e VIROU um falso
positivo de "sentido escondido".** Sem a disciplina "sempre rodar os controles que o
cryptanalyst flagueia", o projeto teria proclamado a cifra verbosa viva por um artefato de
um único compressor.

## Veredito final — linha R43–61 FECHADA

> **O Voynichês é um sistema de tokens morfologicamente RICO e sintaticamente FINO, sem
> estrutura de ordem re-segmentável escondida.** Um processo gerativo restrito (operadores
> templáticos qo-/ok-/ot- + bordas de matriz) com uma camada fraca de tópico de prosa, e o
> texto desacoplado das imagens.

- **Robustamente EXCLUÍDO:** substituição simples · prosa de língua natural direta · ruído
  puro · nomenclator · **cifra verbosa com sintaxe sub-token recuperável** (R61).
- **Hipótese "com sentido" sobrevivente:** apenas formas que NÃO deixam assinatura estatística
  na escala observável (uma cifra verbosa cuja chave nenhum teste estatístico revelaria, ou
  uma língua construída) — formalmente possíveis, **sem apoio positivo**, minoritárias.
- "É prosa de língua natural?" → **NÃO** (decisivo). "Tem sentido proposicional?" → **não
  resolvível por estatística** — e a R61 era o último instrumento que poderia mover isso.
- **Prior final (cryptanalyst):** ~55% gerador/baixo-conteúdo, ~30% construída, ~15%
  cifra/codificada. **Nenhuma tradução afirmada em 19 rotas — guardrail em cada saída.**

## Próximo passo — CONSOLIDAR

Ambos os especialistas endossam: a linha está fechada à resolução que os dados permitem; mais
falsificação na escala do token tem retorno decrescente. O passo de maior valor agora é
**consolidar as Rotas 43–61 num relatório coerente** (a incerteza restante é de
proveniência/chave-de-cifra, não de estatística).

Guardrail: `rota61_resegment_not_decipherment`.
Script: `scripts/analyze_resegment.py`; testes: `tests/test_resegment.py` (suíte **466**).
Saídas: `data/derived/resegment_{,summary_}zl3b.csv`.
