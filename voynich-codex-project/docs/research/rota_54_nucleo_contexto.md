# Rota 54: estresse do sinal ch/sh — refina (e tempera) a Rota 53

Guardrail: `rota54_nucleus_context_not_decipherment`.

A Rota 53 estabeleceu que o núcleo ch/sh segue CONTEÚDO (seção), não escriba. A Rota 54
submete esse achado a três ataques falsificáveis. O **cryptanalyst pré-registrou as
predições CEGO aos números** (antes de o corpus-statistician rodar) — método que evita
racionalização pós-hoc e dá limiares limpos para julgar cada resultado.

Script: `scripts/analyze_nucleus_context.py`. Testes: `tests/test_nucleus_context.py`
(8 testes; suíte total **343 passando**). Sanidade: reproduz o total da Rota 53
(n_chsh = 14 594).

## Pré-registro × resultado

| Sub-ataque | Predição do modelo (cryptanalyst, cego) | Limiar | Resultado | Veredito |
|------------|-----------------------------------------|--------|-----------|----------|
| **A** rótulo vs texto | sh marca referente → excesso nos RÓTULOS (ninfas) | sh%(L) − sh%(P) ≥ 10pp, p<0.01 | sh%(L)=33% (n=24) < sh%(P)=42.5%; V=0.018, p=0.42 | **refutado / nulo** |
| **B** núcleo ⟂ operador | camadas ortogonais → independência | V<0.05 confirma; V>0.15 refuta | V=0.1145, p=0.002; dentro de B V=0.099 | **refuta parcial (acoplamento fraco)** |
| **C** ambiente ch vs sh | conteúdo → mesmo conjunto de sucessores | ΔH<0.15 confirma; ΔH>0.3 = alografia | mesmo top-3 (e,o,y) MAS ΔH=0.38 bits | **misto** |

## R54-A — o excesso de sh é do TEXTO, não dos rótulos

Dentro do balneológico (fólios 75–84), separando loci de RÓTULO (kind L) de TEXTO
corrido (kind P):

| kind | n | %ch | %sh |
|------|---|-----|-----|
| Texto (P) | 2496 | 57.5% | **42.5%** |
| Rótulo (L) | 24 | 66.7% | 33.3% |

sh é até *menor* nos rótulos (e n=24 é minúsculo); V=0.018, p=0.42. **O excesso de sh do
balneológico vive na PROSA, não na nomeação de ninfas.** Isso refuta "ch/sh nomeia o
referente" e rebaixa o sinal de conteúdo de *nível-palavra/rótulo* para *frequência
topical no texto corrido*.

## R54-B — o núcleo NÃO é ortogonal ao operador

| operador | n_ch | n_sh | %sh |
|----------|------|------|-----|
| ok | 920 | 206 | 18.3% |
| ot | 774 | 124 | 13.8% |
| nenhum | 8653 | 3917 | **31.2%** |

V(operador × ch/sh)=0.1145, p=0.002, **sobrevive dentro de Currier B** (V=0.099). O
modelo de 5 camadas previa independência (V≈0); em vez disso, **tokens com ok/ot
preferem fortemente ch**, e o vocabulário sh é majoritariamente o vocabulário SEM
operador. O acoplamento é fraco (V≈0.11, não colapsa o modelo) mas é real e significativo:
as camadas núcleo e operador **interagem**.

## R54-C — ch e sh: mesma gramática, valores distintos

| | H(próximo) | top-3 sucessores |
|--|-----------|------------------|
| ch | 2.32 bits | e=0.46, o=0.24, y=0.09 |
| sh | 1.94 bits | e=0.58, o=0.22, y=0.06 |

O **inventário de sucessores é IDÊNTICO** (e, o, y, d, a, c — mesma ordem nos dois) — ou
seja, ch e sh montam na MESMA gramática descendente. Mas sh é mais concentrado em `-e`
(ΔH=0.38 bits): **não são variantes livres**. Leitura adjudicada: ch e sh são **dois
valores de um único slot**, sobre uma gramática comum — nem alógrafos livres, nem
fonologias separadas. (O limiar binário ΔH>0.3 do cryptanalyst sugeriria alografia, mas
ele mesmo pré-registrou que *mesmo conjunto de sucessores* = gramática compartilhada;
os dois critérios apontam para "um slot, dois valores".)

## Síntese — o modelo refinado

A Rota 54 **tempera** a Rota 53. ch/sh continua sendo o melhor sinal correlacionado a
conteúdo do projeto, mas a história limpa de "primeira camada lexical ortogonal" não se
sustenta:

1. (A) a correlação com seção é **frequência topical na prosa**, não nomeação de referente;
2. (B) o núcleo **interage** com o operador (ok/ot→ch), logo as camadas não são ortogonais;
3. (C) ch/sh são **dois valores de um slot** com gramática compartilhada, não variantes livres.

> **Descrição corrente mais defensável:** ch/sh é uma distinção **sublexical** (um slot,
> dois valores, gramática comum) cuja frequência é condicionada por DUAS forças — a camada
> de operador (ok/ot→ch) e o tópico/seção (prosa balneológica→sh). É estrutura
> integrada e topicamente enviesada, **não** um marcador semântico de classe isolado.

### Modelo (Rotas 43–54)

```
[qo-] + OPERADOR(ok/ot) ──┐ (acoplam, V=0.11)
                          ├─ NÚCLEO(ch/sh: 1 slot, 2 valores; enviesado por tópico)
       VOGAL(a/o←escriba) + CONSOANTE(r/l←posição)
```

As 4 camadas da casca permanecem; o núcleo é o sinal correlacionado a conteúdo, mas
**acoplado ao operador**, não independente.

## Rota 55 — teste decisivo (proposto pelo cryptanalyst)

**Troca de par mínimo entre seções.** Fixar operador+vogal+borda e comparar o MESMO
radical com ch vs sh entre seções:
- se ch/sh = marcador de classe semântica → as formas-ch e formas-sh do mesmo radical
  ocupam seções **complementares** (perfis de seção quase disjuntos por radical);
- se ch/sh = alternância fonológica/posicional → as duas variantes co-ocorrem nos mesmos
  loci, governadas pelo vizinho (posição na linha, caractere anterior), independente de seção.

Quantificar: V(seção | radical, ch/sh) vs V(vizinho | radical, ch/sh). Isso resolve se a
correlação de conteúdo da Rota 53 é **semântica** ou apenas **fonotática com viés topical**.

Guardrail: `rota54_nucleus_context_not_decipherment`.
