#!/usr/bin/env python3
"""Rota 71: position the CONSTRUCTED-LANGUAGE ("lingua ignota") hypothesis.

THIS ROUTE MEASURES NOTHING NEW. The corpus-statistical line is EXHAUSTED (R62:
a local content-free generator reproduces 13/14 signatures; R67 closes the 14th as
layout) and the visual front is CLOSED (R63-65). It is a SYNTHESIS / POSITIONING
route: it encodes the verdicts ALREADY established by prior routes -- each criterion
cites its source rota -- into a falsifiable SCORECARD, and derives a verdict that is
a PURE FUNCTION of the scorecard tallies. No new statistic is computed; the only
file it reads is the OPTIONAL R68 codicology summary, used purely as a live anchor.

Why a route at all? The user asked whether the manuscript could be a *lingua ignota*.
The honest answer is not a yes/no: it splits across the frozen prior. This route makes
that split EXPLICIT and CHECKABLE rather than rhetorical.

TWO target hypotheses are scored SEPARATELY (they are not the same claim):

  H_broad      -- "constructed system / notation": an artificial sign system
                  deliberately designed by someone. This is the prior's ~22%
                  "construida" branch AND the family the ~70% content-free
                  generator itself belongs to (a generator is a constructed system).

  H_hildegard  -- the SPECIFIC Hildegard von Bingen *Lingua Ignota* model: a glossed,
                  referential invented vocabulary -- nomenclator-like, noun-dominated,
                  readable PRECISELY BECAUSE it carries parallel Latin/German glosses.

For each criterion we record: source route, the established finding (string), and its
effect (supports / weakens / neutral) on EACH hypothesis. ONE criterion -- the
R62/R67 content-free generator reproducing every statistical signature -- carries
`caps_confirmation=True`: it does NOT refute a constructed SYSTEM (the generator is
one), but it makes any CONTENT-BEARING reading UNCONFIRMABLE by corpus statistics.

VERDICT (a pure function of the tallies):
  family_alive          = NO criterion refutes H_broad           (n_weakens_broad == 0)
  hildegard_weakened    = weakens(H_hildegard) > supports(H_hildegard)
  confirmable_by_stats  = NO criterion caps confirmation          (i.e. not the generator)
  -> classify_verdict(...) in
       constructed_family_refuted                         (counterfactual: H_broad refuted)
       constructed_confirmable_by_statistics              (counterfactual: stats could decide)
       constructed_family_alive_hildegard_excluded_frozen (the actual state)
       constructed_family_alive_hildegard_open_frozen

GOLDEN RULE: this positions a HYPOTHESIS against the closed ledger; it assigns NO
meaning to any Voynichese token. Confirming content needs evidence EXTERNAL to corpus
statistics: a documented key/crib (#1) or a decode that predicts held-out folios (#6).
Absent those, the prior stays frozen at generator ~70% / constructed ~22% / cipher ~8%.
Guardrail in every output.
"""
from __future__ import annotations

import argparse
import collections
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GUARDRAIL = "rota71_constructed_language_not_decipherment"
DEFAULT_CODICOLOGY = ROOT / "data" / "derived" / "codicology_summary_zl3b.csv"

PRIOR_FROZEN = "generator ~70% / constructed ~22% / cipher ~8%"
CONFIRM_REQUIRES = (
    "#1 documented key/crib (a key => cipher; a grammar+lexicon => constructed language)",
    "#6 reproducible decode that predicts held-out (unseen) folios",
)
EFFECT_PT = {"supports": "sustenta", "weakens": "enfraquece", "neutral": "neutro"}

# --------------------------------------------------------------------------- #
# The scorecard: established prior-route findings, NOT new measurements.       #
# Each row's `broad`/`hildegard` is the effect on that hypothesis; `caps` marks #
# the one finding that bounds CONFIRMABILITY rather than the hypothesis itself. #
# --------------------------------------------------------------------------- #
CRITERIA: list[dict[str, object]] = [
    {
        "id": "designed_combinatorial_morphology",
        "axis": "morphology",
        "source": "R43-R55",
        "finding": "token is 100% functional: qo-/ok-/ot- operators + ar/al/or/ol matrix",
        "broad": "supports",
        "hildegard": "neutral",
        "caps": False,
        "note": "a designed operator system; Hildegard's words are not productively combinatorial",
    },
    {
        "id": "syntax_thin_bag_of_words",
        "axis": "syntax",
        "source": "R60",
        "finding": "compresses like its own bag-of-words; order info ~1-3% vs natural 12-25%",
        "broad": "supports",
        "hildegard": "supports",
        "caps": False,
        "note": "order-poor; both a designed system and a glossary lack rich word order",
    },
    {
        "id": "not_natural_prose",
        "axis": "entropy",
        "source": "R58",
        "finding": "h2=2.15, far below natural prose; not random noise either",
        "broad": "supports",
        "hildegard": "supports",
        "caps": False,
        "note": "constructed, not naturally written language",
    },
    {
        "id": "morph_rich_syntax_fine",
        "axis": "long_range",
        "source": "R59",
        "finding": "I(d) drops to floor at d~15 (token scale); no mid-range syntax",
        "broad": "supports",
        "hildegard": "neutral",
        "caps": False,
        "note": "rich morphology, thin syntax: a generated/designed surface",
    },
    {
        "id": "nomenclator_excluded",
        "axis": "semantics",
        "source": "R57",
        "finding": "nomenclator (label-is-a-name) hypothesis discarded",
        "broad": "neutral",
        "hildegard": "weakens",
        "caps": False,
        "note": "Hildegard's Lingua Ignota IS essentially a glossed nomenclator",
    },
    {
        "id": "label_object_decoupled",
        "axis": "cross_modal",
        "source": "R63-R65",
        "finding": "label<->object decoupled_refined (powered, no confirmation bias)",
        "broad": "neutral",
        "hildegard": "weakens",
        "caps": False,
        "note": "Hildegard's invented words label real objects; here they do not",
    },
    {
        "id": "no_gloss_no_parallel_key",
        "axis": "external",
        "source": "R68",
        "finding": "no gloss / no parallel text; documented key/crib (#1) not known",
        "broad": "neutral",
        "hildegard": "weakens",
        "caps": False,
        "note": "Hildegard is readable BECAUSE glossed; the Voynich has no such crib",
    },
    {
        "id": "lexicon_scale_morphology",
        "axis": "lexicon",
        "source": "R59",
        "finding": "thousands of word types, morphology-rich (not a ~1000-item noun list)",
        "broad": "neutral",
        "hildegard": "weakens",
        "caps": False,
        "note": "scale and morphology mismatch Hildegard's small noun-dominated glossary",
    },
    {
        "id": "serious_deliberate_production",
        "axis": "codicology",
        "source": "R68",
        "finding": "blocked p=0.001, 5 hands, V(hand x Currier)=0.98, interleaved_production",
        "broad": "supports",
        "hildegard": "supports",
        "caps": False,
        "note": "deliberate constructor + a system shared/taught across scribes",
    },
    {
        "id": "contentfree_generator_reproduces_signatures",
        "axis": "generative",
        "source": "R62/R67",
        "finding": "a local content-free generator reproduces 14/14 statistical signatures",
        "broad": "neutral",
        "hildegard": "neutral",
        "caps": True,
        "note": "does not refute a constructed SYSTEM; caps any content reading as "
        "unconfirmable by corpus statistics",
    },
]


# --------------------------------------------------------------------------- #
# Tally + verdict (pure functions)                                             #
# --------------------------------------------------------------------------- #
def tally(criteria: list[dict[str, object]], key: str) -> "collections.Counter[str]":
    """Count supports/weakens/neutral effects of the criteria on one hypothesis."""
    c: collections.Counter[str] = collections.Counter()
    for row in criteria:
        c[str(row[key])] += 1
    return c


def classify_verdict(
    family_alive: bool, hildegard_weakened: bool, confirmable_by_stats: bool
) -> str:
    """Pure-function verdict from the three scorecard booleans.

    The actual closed state yields constructed_family_alive_hildegard_excluded_frozen:
    the broad constructed-system family is unrefuted (family_alive), the specific
    Hildegard model is outweighed by weakening evidence (hildegard_weakened), and the
    content-free generator makes the question unconfirmable by statistics
    (not confirmable_by_stats). The other branches are kept reachable so the logic is
    testable, not asserted.
    """
    if not family_alive:
        return "constructed_family_refuted"
    if confirmable_by_stats:
        return "constructed_confirmable_by_statistics"
    if hildegard_weakened:
        return "constructed_family_alive_hildegard_excluded_frozen"
    return "constructed_family_alive_hildegard_open_frozen"


# --------------------------------------------------------------------------- #
# Optional live anchor: the R68 codicology summary                             #
# --------------------------------------------------------------------------- #
def load_codicology_anchor(path: Path) -> dict[str, str]:
    """Read the R68 codicology summary if present; return the few anchor metrics.

    This is the ONLY data the route reads. It grounds the serious-production
    criterion in a live prior output rather than a hard-coded constant. If the file
    is absent the route still runs (the criterion keeps its documented finding).
    """
    if not path.exists():
        return {}
    rows = {
        r["metric"]: r["value"]
        for r in csv.DictReader(path.open(encoding="utf-8"))
        if "metric" in r
    }
    keep = ("verdict", "V_hand_currier", "currier_runs_p_vs_null", "n_hands")
    return {k: rows[k] for k in keep if k in rows}


def apply_anchor(criteria: list[dict[str, object]], anchor: dict[str, str]) -> None:
    """Rewrite the serious-production finding from the live codicology anchor."""
    if not anchor:
        return
    for row in criteria:
        if row["id"] == "serious_deliberate_production":
            row["finding"] = (
                f"blocked p={anchor.get('currier_runs_p_vs_null', '?')}, "
                f"{anchor.get('n_hands', '?')} hands, "
                f"V(hand x Currier)={anchor.get('V_hand_currier', '?')}, "
                f"verdict={anchor.get('verdict', '?')}"
            )


# --------------------------------------------------------------------------- #
# IO                                                                           #
# --------------------------------------------------------------------------- #
def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def scorecard_rows(criteria: list[dict[str, object]]) -> list[dict]:
    """One CSV row per criterion, each carrying the guardrail."""
    out = []
    for row in criteria:
        out.append(
            {
                "criterion": row["id"],
                "axis": row["axis"],
                "source_route": row["source"],
                "established_finding": row["finding"],
                "effect_on_broad": row["broad"],
                "effect_on_hildegard": row["hildegard"],
                "caps_confirmation": str(row["caps"]),
                "note": row["note"],
                "semantic_guardrail": GUARDRAIL,
            }
        )
    return out


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("codicology", nargs="?", default=str(DEFAULT_CODICOLOGY))
    d = ROOT / "data" / "derived"
    p.add_argument(
        "--out-scorecard",
        default=str(d / "constructed_language_scorecard_zl3b.csv"),
    )
    p.add_argument(
        "--out-summary", default=str(d / "constructed_language_summary_zl3b.csv")
    )
    p.add_argument(
        "--md", default=str(ROOT / "docs" / "research" / "rota_71_lingua_construida.md")
    )
    return p.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    # the criteria are a synthesis of prior verdicts; copy so we can anchor in place
    criteria = [dict(c) for c in CRITERIA]
    anchor = load_codicology_anchor(Path(args.codicology))
    apply_anchor(criteria, anchor)

    t_broad = tally(criteria, "broad")
    t_hild = tally(criteria, "hildegard")
    caps = any(bool(c["caps"]) for c in criteria)

    family_alive = t_broad["weakens"] == 0
    hildegard_weakened = t_hild["weakens"] > t_hild["supports"]
    confirmable_by_stats = not caps
    verdict = classify_verdict(family_alive, hildegard_weakened, confirmable_by_stats)

    # --- scorecard CSV ---
    write_csv(
        Path(args.out_scorecard),
        scorecard_rows(criteria),
        [
            "criterion",
            "axis",
            "source_route",
            "established_finding",
            "effect_on_broad",
            "effect_on_hildegard",
            "caps_confirmation",
            "note",
            "semantic_guardrail",
        ],
    )

    # --- summary CSV (metric,value) ---
    caveat = (
        "positions the constructed-language hypothesis against the closed ledger; "
        "encodes prior-route verdicts; computes NO new corpus statistic; assigns NO "
        "meaning to any token"
    )
    summary_rows = [
        {"metric": "route_type", "value": "synthesis_positioning_not_new_measurement"},
        {"metric": "n_criteria", "value": str(len(criteria))},
        {"metric": "broad_supports", "value": str(t_broad["supports"])},
        {"metric": "broad_weakens", "value": str(t_broad["weakens"])},
        {"metric": "broad_neutral", "value": str(t_broad["neutral"])},
        {"metric": "hildegard_supports", "value": str(t_hild["supports"])},
        {"metric": "hildegard_weakens", "value": str(t_hild["weakens"])},
        {"metric": "hildegard_neutral", "value": str(t_hild["neutral"])},
        {"metric": "family_alive", "value": str(family_alive)},
        {"metric": "hildegard_weakened", "value": str(hildegard_weakened)},
        {"metric": "confirmable_by_corpus_statistics", "value": str(confirmable_by_stats)},
        {"metric": "verdict", "value": verdict},
        {"metric": "confirmation_requires", "value": " | ".join(CONFIRM_REQUIRES)},
        {"metric": "prior_frozen", "value": PRIOR_FROZEN},
        {
            "metric": "codicology_anchor_verdict",
            "value": anchor.get("verdict", "na"),
        },
        {"metric": "caveat", "value": caveat},
        {"metric": "guardrail", "value": GUARDRAIL},
    ]
    write_csv(Path(args.out_summary), summary_rows, ["metric", "value"])

    # --- markdown report ---
    write_report(
        Path(args.md),
        criteria=criteria,
        t_broad=t_broad,
        t_hild=t_hild,
        family_alive=family_alive,
        hildegard_weakened=hildegard_weakened,
        confirmable_by_stats=confirmable_by_stats,
        verdict=verdict,
        anchor=anchor,
        caveat=caveat,
    )

    # --- console report ---
    print(f"route_type=synthesis_positioning_not_new_measurement n_criteria={len(criteria)}")
    print(
        f"H_broad:     supports={t_broad['supports']} weakens={t_broad['weakens']} "
        f"neutral={t_broad['neutral']}  -> family_alive={family_alive}"
    )
    print(
        f"H_hildegard: supports={t_hild['supports']} weakens={t_hild['weakens']} "
        f"neutral={t_hild['neutral']}  -> weakened={hildegard_weakened}"
    )
    print(f"confirmable_by_corpus_statistics={confirmable_by_stats}")
    print(f"VERDICT={verdict}")
    print(f"prior_frozen={PRIOR_FROZEN}")
    print(f"codicology_anchor_verdict={anchor.get('verdict', 'na')}")
    print(f"scorecard_csv={args.out_scorecard}")
    print(f"summary_csv={args.out_summary}")
    print(f"md={args.md}")
    return 0


def write_report(
    path: Path,
    *,
    criteria: list[dict[str, object]],
    t_broad: "collections.Counter[str]",
    t_hild: "collections.Counter[str]",
    family_alive: bool,
    hildegard_weakened: bool,
    confirmable_by_stats: bool,
    verdict: str,
    anchor: dict[str, str],
    caveat: str,
) -> None:
    table = [
        "| Critério | Fonte | Achado estabelecido | H_amplo | H_Hildegard |",
        "|---|---|---|---|---|",
    ]
    for c in criteria:
        cap = " *(limita confirmação)*" if c["caps"] else ""
        table.append(
            f"| `{c['id']}`{cap} | {c['source']} | {c['finding']} | "
            f"**{EFFECT_PT[str(c['broad'])]}** | **{EFFECT_PT[str(c['hildegard'])]}** |"
        )
    anchor_line = (
        f"verdito codicológico (R68, lido ao vivo): **{anchor['verdict']}**"
        if anchor.get("verdict")
        else "âncora codicológica (R68) ausente — critério usa o achado documentado"
    )
    lines = [
        "# Rota 71 — A hipótese de língua construída (*lingua ignota*): posicionamento",
        "",
        f"Guardrail: `{GUARDRAIL}`.",
        "Guardrail global: esta rota posiciona uma **HIPÓTESE** contra o ledger fechado",
        "(R43–R70). Ela **não mede nada novo** no corpus (a linha estatística está exaurida",
        "desde a R62) e **não atribui sentido** a nenhum token Voynichês. É uma função-síntese",
        "dos vereditos já estabelecidos.",
        "",
        "## Sumário executivo",
        "",
        "O usuário perguntou se o manuscrito poderia ser uma *lingua ignota*. A resposta",
        "honesta não é sim/não: ela se **reparte** dentro do prior congelado. O termo tem",
        "dois sentidos, e eles caem em ramos diferentes do estado fechado:",
        "",
        "1. **Sentido amplo — sistema/notação construída** (`H_amplo`): um sistema de signos",
        "   artificial, desenhado por alguém. É o ramo **`construída ~22%`** do prior — e",
        "   também a família a que o **gerador content-free ~70%** pertence (um gerador É um",
        "   sistema construído).",
        "2. **Sentido estrito — o modelo de Hildegard von Bingen** (`H_Hildegard`): a *Lingua",
        "   Ignota* do séc. XII, um vocabulário inventado **glosado** (lista de substantivos",
        "   legível PORQUE traz glosas latim/alemão).",
        "",
        f"**Veredito** (função pura das contagens): **`{verdict}`**.",
        "",
        f"- **`H_amplo` está VIVO** — sustentado por {t_broad['supports']} critérios, "
        f"enfraquecido por {t_broad['weakens']}. Nada no ledger o refuta; é o segundo ramo",
        "  sobrevivente do prior.",
        f"- **`H_Hildegard` está ENFRAQUECIDO** — enfraquecido por {t_hild['weakens']} "
        f"critérios contra {t_hild['supports']} que o sustentam. O modelo glosado/nomenclator",
        "  é justamente o que as rotas R57/R63–65/R68 já tiraram de cima da mesa.",
        f"- **Nenhum dos dois é confirmável por estatística** (`confirmable_by_corpus_"
        f"statistics={confirmable_by_stats}`): o gerador da R62/R67 reproduz 14/14 assinaturas,",
        "  então um sistema construído COM conteúdo é indistinguível de um SEM conteúdo na",
        "  escala do token.",
        "",
        "## As duas hipóteses, lado a lado",
        "",
        "| | `H_amplo` (sistema construído) | `H_Hildegard` (Lingua Ignota glosada) |",
        "|---|---|---|",
        "| Unidade | operadores + matriz (combinatória) | substantivos inventados (lista) |",
        "| Glosa/chave | não exigida | **central** (é o que a torna legível) |",
        "| Nomeia objetos? | não precisa | **sim** (palavra↔coisa) |",
        "| Escala | milhares de *types* | ~1000 itens, dominados por nomes |",
        "| Status no ledger | **vivo (~22%)** | **enfraquecido/excluído** |",
        "",
        "## Scorecard (síntese dos vereditos anteriores)",
        "",
        f"{anchor_line}.",
        "",
        *table,
        "",
        "Contagens: "
        f"`H_amplo` sustenta={t_broad['supports']} / enfraquece={t_broad['weakens']} / "
        f"neutro={t_broad['neutral']}; "
        f"`H_Hildegard` sustenta={t_hild['supports']} / enfraquece={t_hild['weakens']} / "
        f"neutro={t_hild['neutral']}.",
        "",
        "## Veredito como função pura dos booleanos",
        "",
        f"- `family_alive = (broad_weakens == 0)` → **{family_alive}**",
        f"- `hildegard_weakened = (hildegard_weakens > hildegard_supports)` → "
        f"**{hildegard_weakened}**",
        f"- `confirmable_by_corpus_statistics = (nenhum critério limita confirmação)` → "
        f"**{confirmable_by_stats}**",
        f"- `classify_verdict(...)` → **`{verdict}`**",
        "",
        "## O que confirmaria — e o que já enfraquece",
        "",
        "**Só duas evidências movem isto, e nenhuma é estatística** (tabela de decisão da R68):",
        "",
        f"- **{CONFIRM_REQUIRES[0]}** — é a *única* que também separa **construída de cifra**.",
        f"- **{CONFIRM_REQUIRES[1]}**.",
        "",
        "**Já pesou contra o modelo de Hildegard** (e não vai mudar sem evidência externa):",
        "nomenclator excluído (R57), rótulo↔objeto desacoplado (R63–65), ausência de glosa/chave",
        "(R68) e escala/morfologia incompatíveis com uma lista de substantivos (R59).",
        "",
        "## Regra de ouro",
        "",
        f"{caveat}.",
        "",
        f"Prior **CONGELADO**: {PRIOR_FROZEN}. Esta rota **não move o ponteiro** — apenas",
        "torna explícito e checável como a pergunta da *lingua ignota* se reparte sobre ele.",
        "Não é uma decifração.",
        "",
        f"Guardrail: `{GUARDRAIL}`.",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
