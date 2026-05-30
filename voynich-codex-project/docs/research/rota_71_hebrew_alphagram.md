# Rota 71: a tese hebraica (Kondrak & Hauer 2018) — ataque ao alfagrama + abjad

Guardrail: `rota71_hebrew_alphagram_not_decipherment`.

**Guardrail global:** este relatório mede ESTRUTURA (ordem dos glifos dentro da
palavra) e o que a hipótese hebraica algorítmica PREDIZ — não tradução. Nenhuma
afirmação de sentido é feita. O veredito foi validado mecanicamente contra o
gerador sem-conteúdo da Rota 62, não por inferência.

---

## 1. Sumário executivo

A afirmação "o Voynich é hebraico" tem **duas formas distintas**, e o repositório
só havia atacado uma:

- **Decifrações pontuais** (Cheshire, Bax, Gibbs — traduções de frase) já são a
  **Tese 13 da R66**, refutadas por `char_h2=2.15` e pela ausência de uma gramática
  que reproduza o corpus inteiro. Decodificam um punhado de tokens a dedo.
- A versão **algorítmica** — **Kondrak & Hauer (2018)**, *"Decoding Anagrammed
  Texts..."* (TACL) — é diferente e **nunca foi isolada aqui**. Eles rodaram
  identificação automática de língua sobre ~380 idiomas (o hebraico pontuou em
  primeiro) e propuseram um **modelo gerador específico** para a cifra:

  > cada palavra Voynich = uma palavra hebraica que foi **(a)** despida das vogais
  > [abjad] e **(b)** teve as letras restantes **reordenadas em ordem alfabética**
  > (um *alfagrama* / anagrama alfabético).

  O "decode" da primeira linha deles depende de des-alfagramar + repor vogais +
  Google Tradutor.

A Rota 71 isola e ataca o **pilar falsificável** da versão algorítmica: a
**hipótese do alfagrama**. Se cada palavra é um anagrama alfabético, então existe
**uma ordem total dos glifos** sob a qual *quase todo* token é não-decrescente —
de forma equivalente, a ordem majoritária par-a-par dos glifos é uma ordem total
**estrita** (transitiva, **acíclica**) e quase todo token a obedece.

> **Manchete: o alfagrama é REFUTADO no corpus inteiro.** Sob a melhor ordem total
> possível, só **27,3%** dos tokens estão ordenados (teto de um alfagrama real =
> 100%; piso de embaralhamento = 6,3%) — apenas **22,5% do caminho** do acaso ao
> alfagrama. Só **35%** dos pares de glifos têm ordem estrita (alfagrama exige
> ~100%), e a relação de ordem majoritária contém **15 ciclos de 3** (`a<b<c<a`):
> isso **prova** que **nenhuma** ordem total de glifos consegue ordenar todas as
> palavras. O modesto viés de ordem que existe é **reproduzido pelo gerador
> sem-conteúdo da R62** (real 0,273 ≈ gerador 0,277, Δ=0,004): é a **morfologia
> templática** já mapeada (R49: `qo-/ok-/ot-` no início, `-dy/-y/-aiin` no fim),
> **não** uma reordenação alfabética de uma língua subjacente.

Isso **refina a Tese 13 da R66**: a forma de "decifração pontual" do hebraico já
estava morta por `char_h2`; agora a forma **algorítmica e estrutural** (K-H) está
morta pelo seu **próprio mecanismo declarado** — o texto não é um alfagrama. Os
priores permanecem **gerador ~70% / construída ~22% / cifra ~8%**.

---

## 2. O pilar falsificável e por que ele é decisivo

K-H não fazem uma alegação vaga de "parece hebraico"; eles afirmam uma **operação
mecânica** (abjad + reordenação alfabética). Essa operação tem uma consequência
matemática inescapável:

> Um alfagrama impõe uma **ordem total** dos símbolos. Logo, para QUALQUER par de
> glifos `(x, y)`, ou `x` sempre precede `y` dentro das palavras, ou `y` sempre
> precede `x` — nunca os dois. E a relação resultante é **acíclica**.

Testar isso não exige conhecer a chave, o mapeamento de glifos, nem o hebraico.
Basta medir a **consistência de ordem intra-palavra** do corpus e compará-la com o
que um alfagrama de verdade produz. Três medidas, duas delas **independentes da
ordem específica** escolhida (portanto à prova da objeção "você escolheu a ordem
errada"):

| Medida | O que mede | Valor num alfagrama real |
|---|---|---|
| `alphagram_fraction` | fração de tokens não-decrescentes sob a melhor ordem | ~1,0 |
| `pair_decidedness` (order-free) | fração de pares de glifos com ordem estrita (≥95%) | ~1,0 |
| `majority_cycles` (order-free) | nº de 3-ciclos `a<b<c<a` na ordem majoritária | **0** |

`majority_cycles > 0` é uma **prova de impossibilidade**: se há um ciclo, nenhuma
ordem total existe, e o texto **não pode** ser um alfabeto reordenado — sem
threshold, sem ambiguidade.

---

## 3. Metodologia

Mesmo protocolo adversarial das rotas R58–R69, agora apontado para o mecanismo de K-H:

1. **Piso e teto internos.** Cada métrica é ancorada entre o **piso**
   (embaralhar as letras dentro de cada palavra → destrói a ordem) e o **teto**
   (ordenar de fato as letras de cada palavra → um alfagrama verdadeiro, por
   construção). Isso calibra "quão alfagrama" o texto real é.
2. **Arbitragem contra o gerador R62.** O gerador sem-conteúdo redesenha
   **palavras inteiras reais** em ordem i.i.d.; sua morfologia **intra-palavra é
   idêntica** ao corpus. Logo, qualquer sinal de ordem **dentro da palavra** que o
   gerador reproduz é **morfologia templática**, não evidência de reordenação
   alfabética → degenera (mesma lógica da R66/R69).
3. **Robustez de tokenização (glifo-EVA).** O EVA escreve alguns glifos únicos como
   dígrafos (`ch`, `sh`, `cth`, `ckh`, `cph`, `cfh`). Todo o teste é repetido
   tratando-os como unidades, para o veredito não ser artefato do split ASCII.
4. **Camada abjad.** As vogais-candidatas do EVA (`a`, `o`, `e`, `y`) são removidas
   e o teste recomputado: remover vogais **resgata** uma ordem total? Também o
   comprimento médio de palavra vs a âncora abjad (esqueletos consonantais
   hebraicos ~3–4).
5. **Frequência de letras (fraca, não-discriminante).** Perfil de frequência
   ordenado dos glifos Voynich vs âncoras de hebraico E inglês (literatura, nunca
   recomputadas). Zipf faz os perfis ordenados de duas línguas quaisquer
   correlacionarem ~1,0 → um "casamento" com o hebraico é não-informativo.

A direção da escrita (hebraico é direita→esquerda) é escopo da **Rota 69**
(direcionalidade / espelhamento), mantida separada; esta rota é o pilar
alfagrama + abjad.

---

## 4. Resultados

Reproduzido de `data/derived/hebrew_alphagram_corpora_zl3b.csv` (37 671 tokens):

| corpus | `alphagram_fraction` | pares decididos | maioria pond. | ciclos | unid./palavra |
|---|---:|---:|---:|---:|---:|
| **real** | **0,2733** | **0,3474** | 0,845 | **15** | 5,06 |
| piso (embaralhado) | 0,0626 | 0,0042 | 0,507 | 191 | 5,06 |
| **teto (alfagrama real)** | **1,0000** | **1,0000** | 1,000 | **0** | 5,06 |
| gerador R62 (base) | 0,2769 | 0,3866 | 0,845 | 12 | 5,05 |
| gerador R62 (full) | 0,2676 | 0,3550 | 0,836 | 18 | 5,04 |
| glifo-EVA (real) | 0,3333 | 0,3402 | 0,859 | 19 | 4,54 |
| abjad (sem vogais) | 0,4729 | 0,4159 | 0,842 | 3 | 3,05 |

Leitura linha a linha:

- **real vs teto:** 0,273 contra 1,0. O texto está a **22,5%** do caminho entre o
  acaso e um alfagrama. Um texto genuinamente alfagramado fica colado no teto.
- **real vs gerador:** 0,273 ≈ 0,277 (Δ=0,004). O viés de ordem que existe é
  **inteiramente reproduzido** pela morfologia da forma do token — não precisa de
  hebraico nem de reordenação alfabética.
- **15 ciclos de maioria (real):** prova que **nenhuma** ordem total ordena todas
  as palavras. O alfagrama exige 0.
- **glifo-EVA:** mesma conclusão (decididos 0,34; 19 ciclos) — o veredito **não** é
  artefato do split em caracteres ASCII.

---

## 5. Por que não é alfagrama — a evidência dos pares

De `data/derived/hebrew_alphagram_pairs_zl3b.csv`: **124 dos 190** pares de glifos
co-ocorrentes são **ambíguos** (não atingem maioria de 95%). Num alfagrama esse
número seria ~0. Exemplos em que ambas as ordens coexistem fortemente:

| par | x→y | y→x | maioria |
|---|---:|---:|---:|
| `e` / `o` | 4 755 | 9 423 | 0,66 |
| `h` / `o` | 6 744 | 3 642 | 0,65 |
| `k` / `o` | 2 492 | 7 180 | 0,74 |

Para `e`/`o` há quase 5 000 palavras com `e` antes de `o` **e** mais de 9 000 com
`o` antes de `e`. Sob a hipótese de K-H, `e` e `o` teriam uma posição alfabética
fixa, uma sempre antes da outra. A coexistência maciça das duas ordens é
incompatível com qualquer reordenação alfabética.

Os pares que **são** decididos (ex.: `e`→`y` 0,90; `h`→`y` 0,92) refletem
**posição de borda** — `y` é um glifo terminal típico, então quase tudo vem antes
dele. Isso é exatamente a **morfologia de sufixo/borda** que as rotas R43–R55 já
mapearam, não uma ordem alfabética: o que parece "ordenação" é o template
prefixo–meio–borda, e ele falha o teste assim que se olham os pares do **miolo**.

---

## 6. Abjad e frequência (camadas secundárias)

- **Abjad não resgata.** Remover as vogais-candidatas (`a/o/e/y`) encurta as
  palavras (5,06 → 3,05 unidades, compatível com esqueletos consonantais) e reduz
  os ciclos de 15 para 3 — mas a fração de pares decididos sobe só para **0,42**
  (≪ 0,90) e **ainda há ciclos**. Tirar vogais não cria a ordem total que o
  alfagrama exige; só há menos glifos para formar ciclos.
- **Frequência é não-discriminante.** A correlação de rank do perfil de frequência
  ordenado do Voynich é **1,00 com o hebraico** e **0,997 com o inglês** — um
  empate. Como toda língua segue Zipf, "as frequências batem com o hebraico" não
  distingue o hebraico de qualquer outra língua. Sinal nulo, como pré-registrado.

---

## 7. Veredito

**`hebrew_alphagram_refuted`.** O mecanismo declarado de Kondrak & Hauer — abjad +
reordenação alfabética — produziria um texto colado no teto do alfagrama (tokens
~100% ordenados, pares ~100% decididos, 0 ciclos). O Voynich entrega 0,27 / 0,35 /
**15 ciclos**, e o pouco de ordem que tem é **reproduzido pelo gerador
sem-conteúdo** (morfologia templática). O abjad não resgata e a frequência não
discrimina.

Posição na matriz da R66: isto **fecha a lacuna** da Tese 13. A forma de
"decifração pontual" do hebraico já morria por `char_h2`; a forma **algorítmica e
estrutural** (a única que fazia uma predição mecânica testável) morre agora pelo
**próprio mecanismo**. Nenhuma das duas formas sobrevive.

**Priores inalterados:** gerador ~70% / construída ~22% / cifra ~8%. Como nas
demais rotas, a estrutura medida aqui é **morfologia**, não sentido; o avanço da
pergunta "tem sentido?" continua exigindo proveniência/material (R68), não mais
estatística de corpus.

### Ressalvas honestas (pré-registradas)

- A ordem total é **inferida** por posição média; mas as duas conclusões centrais
  — `pair_decidedness` e `majority_cycles` — são **independentes da ordem**. Mesmo
  a ordem ótima não pode bater os ciclos: eles provam que nenhuma ordem total
  existe.
- Testou-se o alfagrama **direto**. Um defensor de K-H poderia postular um
  alfabeto/transcrição diferente; mas o teste é robusto à tokenização (glifo-EVA
  falha igual), e os ciclos persistem.
- Isto **não** testa "é hebraico?" em geral — testa o **mecanismo declarado por
  K-H** (alfagrama). Um hebraico que NÃO fosse alfagramado seria uma língua-natural
  direta, já excluída por `char_h2`/MI de médio-alcance (R58/R59).

---

## 8. Ponteiros de arquivo

- **Script:** `scripts/analyze_hebrew_alphagram.py` (alfagrama + decidedness +
  ciclos, arbitrado contra o gerador R62; passes glifo-EVA, abjad e frequência).
- **Teste:** `tests/test_hebrew_alphagram.py` (17 testes; primitivas order-free
  fixadas em corpora construídos com resposta conhecida + asserts no corpus real).
- **CSVs:** `data/derived/hebrew_alphagram_summary_zl3b.csv` (métricas + veredito),
  `data/derived/hebrew_alphagram_corpora_zl3b.csv` (bateria por corpus),
  `data/derived/hebrew_alphagram_pairs_zl3b.csv` (pares de glifos — evidência da
  não-ordem-total).
- **Insumos de grounding:** `docs/research/rota_62_generator.md` (o gerador árbitro),
  `docs/research/rota_66_estado_da_arte_attack_matrix.md` (Tese 13, que esta rota
  refina), `docs/research/rota_58_language_signature.md` (`char_h2`=2,15).
- **Guardrail:** `rota71_hebrew_alphagram_not_decipherment`.

---

## REGRA DE OURO (reafirmada)

A saída da R71 **enfraquece a hipótese hebraica; NÃO converte estrutura em sentido
e NÃO produz tradução.** A consistência de ordem medida é morfologia templática
(reproduzida pelo gerador R62), não reordenação alfabética. Os priores permanecem
**gerador ~70% / construída ~22% / cifra ~8%**.

Guardrail: `rota71_hebrew_alphagram_not_decipherment`.
