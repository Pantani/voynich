"""Tests for Rota 55 minimal-pair nucleus analysis (analyze_nucleus_minpair.py).

The decisive design: within a fixed skeleton (token with its bench -> '#'), every
in-token neighbor is constant, so only EXTERNAL context (section / prev_char /
line_pos) can vary and "explain" the ch/sh choice. We measure conditional mutual
information I(B;X|skeleton) and ask which external variable, if any, governs the
bench. Tests include a synthetic case with a known answer plus the reproduction
of the Rota 53 ch-XOR-sh universe (14594 single-bench tokens).
"""
from __future__ import annotations

import collections
import csv
from pathlib import Path

from scripts.analyze_nucleus import nucleus, parse_corpus
from scripts.analyze_nucleus_minpair import (
    GUARDRAIL,
    build,
    collect,
    conditional_entropy_b_given,
    conditional_mi,
    line_position,
    main,
    minimal_pair_skeletons,
    parse_loci,
    permutation_p,
    skeleton,
    verdict,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"


# ---------------------------------------------------------------------------
# skeleton() + minimal-pair detection
# ---------------------------------------------------------------------------
def test_skeleton_marks_bench_and_is_bench_agnostic():
    # ch and sh forms of the same word collapse to one skeleton
    assert skeleton("chol", "ch") == "#ol"
    assert skeleton("shol", "sh") == "#ol"
    assert skeleton("chol", "ch") == skeleton("shol", "sh")
    # every occurrence of the (single) bench is replaced
    assert skeleton("chedchy", "ch") == "#ed#y"
    # non-bench letters untouched; only the marked bench changes
    assert skeleton("qokeedy", "ch") == "qokeedy"  # no ch -> unchanged


def test_minimal_pair_detection_requires_both_benches():
    recs = [
        {"skeleton": "#ol", "bench": "ch"},
        {"skeleton": "#ol", "bench": "sh"},   # #ol has both -> minimal pair
        {"skeleton": "#edy", "bench": "ch"},  # only ch -> not a minimal pair
        {"skeleton": "#ar", "bench": "sh"},   # only sh -> not a minimal pair
    ]
    mp = minimal_pair_skeletons(recs)
    assert mp == {"#ol"}


def test_line_position_initial_medial_final():
    assert line_position(0, 5) == "initial"
    assert line_position(4, 5) == "final"
    assert line_position(2, 5) == "medial"
    # length-1 locus: the single token is initial
    assert line_position(0, 1) == "initial"


# ---------------------------------------------------------------------------
# conditional-MI correctness + non-negativity
# ---------------------------------------------------------------------------
def test_conditional_entropy_b_given_basic():
    # one context, 4 ch / 4 sh -> H(B|S) = 1 bit
    pairs = [("S0", "ch")] * 4 + [("S0", "sh")] * 4
    assert abs(conditional_entropy_b_given(pairs) - 1.0) < 1e-9
    # deterministic context -> 0 bits
    assert conditional_entropy_b_given([("S0", "ch")] * 6) == 0.0
    assert conditional_entropy_b_given([]) == 0.0


def test_synthetic_section_determines_bench_neighbor_does_not():
    """Known-answer synthetic: within ONE skeleton, section perfectly determines
    the bench and a balanced neighbor is independent of it.

    Construction: skeleton S0; section A -> always ch, section B -> always sh
    (4 each). The neighbor cycles n0,n1 in a pattern orthogonal to the bench:
    each neighbor value sees 2 ch and 2 sh. Expect I_section == H(B|S) == 1 bit
    and I_neighbor == 0.
    """
    skel = ["S0"] * 8
    bench = ["ch", "ch", "ch", "ch", "sh", "sh", "sh", "sh"]
    section = ["A", "A", "A", "A", "B", "B", "B", "B"]
    # neighbor: n0 over (ch,ch,sh,sh), n1 over (ch,ch,sh,sh) -> independent of bench
    neighbor = ["n0", "n0", "n1", "n1", "n0", "n0", "n1", "n1"]

    h_b_given_s = conditional_entropy_b_given(list(zip(skel, bench)))
    i_section = conditional_mi(skel, bench, section)
    i_neighbor = conditional_mi(skel, bench, neighbor)

    assert abs(h_b_given_s - 1.0) < 1e-9
    assert abs(i_section - h_b_given_s) < 1e-9  # section fully explains bench
    assert abs(i_section - 1.0) < 1e-9
    assert abs(i_neighbor - 0.0) < 1e-9         # neighbor explains nothing


def test_conditional_mi_is_non_negative_on_random_data():
    import random

    rng = random.Random(7)
    skel = [f"S{rng.randint(0, 4)}" for _ in range(400)]
    bench = [rng.choice(["ch", "sh"]) for _ in range(400)]
    x = [rng.choice(["a", "b", "c", "d"]) for _ in range(400)]
    for _ in range(20):
        rng.shuffle(x)
        assert conditional_mi(skel, bench, x) >= 0.0


def test_permutation_p_small_when_signal_real_large_when_absent():
    # Real signal: section determines bench within S0 -> low p.
    skel = ["S0"] * 8
    bench = ["ch", "ch", "ch", "ch", "sh", "sh", "sh", "sh"]
    section = ["A", "A", "A", "A", "B", "B", "B", "B"]
    i_sec = conditional_mi(skel, bench, section)
    p_sig = permutation_p(skel, bench, section, i_sec, 200, seed=0)
    assert p_sig < 0.10

    # No signal: a constant X carries zero info -> observed I == 0, and every
    # shuffle also yields 0 >= 0, so p == 1.0 (correctly "not significant").
    x_const = ["z"] * 8
    i0 = conditional_mi(skel, bench, x_const)
    assert i0 == 0.0
    p_null = permutation_p(skel, bench, x_const, i0, 200, seed=0)
    assert p_null == 1.0


def test_verdict_logic_all_three_branches():
    # content/semantic: section dominant AND significant
    assert verdict(0.5, 0.1, 0.05, p_section=0.001, p_neighbor=0.9) == "content/semantic"
    # allography/positional: a neighbor dominant AND significant
    assert verdict(0.05, 0.6, 0.1, p_section=0.9, p_neighbor=0.001) == "allography/positional"
    # lexically_fixed: nothing significant (both p high)
    assert verdict(0.12, 0.14, 0.05, p_section=1.0, p_neighbor=1.0) == "lexically_fixed"
    # section larger but NOT significant -> not content; neighbor not sig either
    assert verdict(0.2, 0.1, 0.05, p_section=0.4, p_neighbor=0.4) == "lexically_fixed"


# ---------------------------------------------------------------------------
# corpus parsing reproduces Rota 53
# ---------------------------------------------------------------------------
def test_parse_loci_flatten_matches_parse_corpus_order():
    folio_currier, loci = parse_loci(CORPUS)
    flat = [(f, t) for f, toks in loci for t in toks]
    ref_currier, ref_tokens = parse_corpus(CORPUS)
    assert flat == ref_tokens            # same tokens, same order
    assert folio_currier == ref_currier  # same Currier map


def test_collect_reproduces_rota53_single_bench_total():
    """Sanity gate: the single-bench (ch XOR sh) universe is the Rota 53 14594."""
    folio_currier, loci = parse_loci(CORPUS)
    records = collect(folio_currier, loci)
    assert len(records) == 14594
    # every record is a single bench type, matching nucleus()
    assert all(r["bench"] in ("ch", "sh") for r in records)
    assert all(nucleus(r["token"]) == r["bench"] for r in records)


def test_collect_prev_char_resets_at_locus_start():
    folio_currier, loci = parse_loci(CORPUS)
    records = collect(folio_currier, loci)
    # locus-initial ch/sh tokens must carry the '^' sentinel as prev_char
    assert any(r["prev_char"] == "^" for r in records)
    # prev_char is always a single char (a letter or the '^' sentinel)
    assert all(len(r["prev_char"]) == 1 for r in records)


def test_build_minimal_pair_subset_is_well_defined():
    folio_currier, loci = parse_loci(CORPUS)
    records = collect(folio_currier, loci)
    b = build(records)
    # minimal-pair tokens are a strict subset of all single-bench tokens
    assert 0 < b["n_minpair_tokens"] <= b["n_chsh_total"] == 14594
    assert b["n_minpair_skeletons"] > 0
    # frac is the token ratio
    assert abs(b["frac_in_minpairs"] - b["n_minpair_tokens"] / 14594) < 1e-9
    # every minimal-pair skeleton genuinely has both benches present
    for sk, d in b["per_skeleton"].items():
        assert d["n_ch"] >= 1 and d["n_sh"] >= 1
    # parallel context lists are aligned and the right length
    assert (
        len(b["skel"])
        == len(b["bench"])
        == len(b["section"])
        == len(b["prev_char"])
        == len(b["line_pos"])
        == b["n_minpair_tokens"]
    )


# ---------------------------------------------------------------------------
# main() writes the two CSVs with the guardrail
# ---------------------------------------------------------------------------
def test_main_writes_outputs_with_guardrail(tmp_path):
    skeletons = tmp_path / "skel.csv"
    summary = tmp_path / "summary.csv"
    rc = main(
        [
            str(CORPUS),
            "--n-perm",
            "30",
            "--out-skeletons",
            str(skeletons),
            "--out-summary",
            str(summary),
        ]
    )
    assert rc == 0
    for p in (skeletons, summary):
        assert p.exists() and p.stat().st_size > 0
        assert GUARDRAIL in p.read_text(encoding="utf-8")

    # summary carries the required metrics
    text = summary.read_text(encoding="utf-8")
    for metric in (
        "n_minpair_skeletons",
        "n_minpair_tokens",
        "frac_of_chsh_in_minpairs",
        "I_section_bits",
        "I_prevchar_bits",
        "I_linepos_bits",
        "perm_p_section",
        "perm_p_neighbor",
        "verdict",
    ):
        assert metric in text

    # skeletons CSV: every row has both benches and is sorted by total desc
    with skeletons.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert rows
    totals = []
    for r in rows:
        n_ch, n_sh = int(r["n_ch"]), int(r["n_sh"])
        assert n_ch >= 1 and n_sh >= 1
        totals.append(n_ch + n_sh)
    assert totals == sorted(totals, reverse=True)

    # verdict is one of the three encoded outcomes
    with summary.open(encoding="utf-8") as f:
        sm = {row["metric"]: row["value"] for row in csv.DictReader(f)}
    assert sm["verdict"] in {"content/semantic", "allography/positional", "lexically_fixed"}
