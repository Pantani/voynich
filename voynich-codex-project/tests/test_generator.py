"""Tests for Rota 62 generator-sufficiency analysis (analyze_generator.py).

The capstone of the "what is Voynichese" arc: can ONE simple LOCAL CONTENTLESS
process (bag-of-real-words + section-vocabulary table + self-citation + line-edge
habit) reproduce the WHOLE measured statistical battery at once? Tests pin the
generator's mechanics and the reporting contract:

  - base (bag-of-real-words) with NO self-citation has an adjacent-repeat rate at
    the i.i.d. collision floor sum_w p(w)^2 (drawing fresh whole words i.i.d.).
  - raising p_rep raises the adjacent-repeat rate MONOTONICALLY (self-citation is
    exactly what lifts repetition above i.i.d.), and calibration hits the target.
  - section_cond reproduces the per-section TOP words (it is a topic-vocabulary
    table: each synthetic line samples from its real section's word distribution).
  - line geometry matches the real corpus: same line COUNT, and the synthetic
    line-length distribution tracks the real one (same mean within tolerance).
  - the imported battery functions all run on a synthetic corpus and return
    finite numbers.
  - the ablation ladder has exactly one row per cumulative mechanism set, in
    order, ending at "full".
  - main() writes all THREE CSVs, each carrying the guardrail, with the required
    columns/metrics and a well-formed verdict.

Everything is seeded; generation is reproducible byte-for-byte. No decipherment
claims are made anywhere (guardrail in every output CSV).
"""
from __future__ import annotations

import collections
import csv
import math
from pathlib import Path

from scripts.analyze_generator import (
    ABLATION_LADDER,
    GUARDRAIL,
    KEY_METRICS,
    MECHANISMS,
    GeneratorProfile,
    build_match_rows,
    calibrate_p_rep,
    classify_verdict,
    generate,
    main,
    measure_battery,
    parse_loci_with_section,
    real_line_initial_gallows_fraction,
)
from scripts.analyze_language_signature import adjacent_repeats, parse_loci

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"


# --------------------------------------------------------------------------- #
# Fixtures / helpers                                                          #
# --------------------------------------------------------------------------- #
def _profile():
    lines, sections = parse_loci_with_section(CORPUS)
    return GeneratorProfile(lines, sections), lines, sections


def _iid_collision(lines) -> float:
    """sum_w p(w)^2 over the real token-unigram (the i.i.d. adjacent-match rate)."""
    uni = collections.Counter(t for line in lines for t in line)
    n = sum(uni.values())
    return sum((c / n) ** 2 for c in uni.values())


# --------------------------------------------------------------------------- #
# Parser parity with the rest of the pipeline                                 #
# --------------------------------------------------------------------------- #
def test_parse_loci_with_section_matches_parse_loci():
    """The section-aware parser must yield EXACTLY the same line set (and token
    order) as analyze_language_signature.parse_loci, so the generator measures the
    identical token universe used by R58/R59/R60 (37671 tokens, 5216 lines)."""
    lines, sections = parse_loci_with_section(CORPUS)
    base = parse_loci(CORPUS)
    assert len(lines) == len(base) == len(sections) == 5216
    assert lines == base
    assert sum(len(l) for l in lines) == 37671
    # every line gets a section label; the herbal section is the largest
    assert all(s for s in sections)
    counts = collections.Counter(sections)
    assert counts["herbal"] > 0 and counts["balneological"] > 0


# --------------------------------------------------------------------------- #
# base = bag-of-real-words sits at the i.i.d. repeat floor                     #
# --------------------------------------------------------------------------- #
def test_base_adjacent_repeat_near_iid_collision():
    """With self_citation OFF (base / bag-of-real-words), the generator draws
    fresh whole words i.i.d., so its adjacent-repeat rate sits at the unigram
    collision floor sum_w p(w)^2 -- NOT elevated. This is the null the real
    corpus's 0.875% must be lifted above (by self-citation)."""
    prof, lines, _ = _profile()
    iid = _iid_collision(lines)
    base = generate(
        prof,
        section_cond=False,
        self_citation=False,
        line_edge_bias=False,
        p_rep=0.0,
        rep_window=1,
        p_initial_gallows=0.0,
        seed=100,
    )
    obs = adjacent_repeats(base)["observed"]
    # within sampling noise of the i.i.d. collision rate (no self-citation lift)
    assert abs(obs - iid) < 0.0015, (obs, iid)
    # and far below the real 0.875% (the whole point: base under-repeats)
    assert obs < 0.005


def test_self_citation_p_rep_zero_equals_iid():
    """self_citation ON but p_rep=0 never copies -> identical behaviour to base:
    the adjacent-repeat rate is still the i.i.d. collision floor. This isolates
    self-citation as THE mechanism that raises repetition."""
    prof, lines, _ = _profile()
    iid = _iid_collision(lines)
    g = generate(
        prof,
        section_cond=False,
        self_citation=True,
        line_edge_bias=False,
        p_rep=0.0,
        rep_window=1,
        p_initial_gallows=0.0,
        seed=100,
    )
    obs = adjacent_repeats(g)["observed"]
    assert abs(obs - iid) < 0.0015, (obs, iid)


# --------------------------------------------------------------------------- #
# self_citation raises repetition monotonically + calibration hits target      #
# --------------------------------------------------------------------------- #
def test_raising_p_rep_raises_repetition_monotonically():
    """Adjacent-repeat rate is monotone increasing in p_rep: more self-citation ->
    more adjacent matches. Checked across a ladder of probabilities at a fixed
    seed (base config so only self-citation drives the change)."""
    prof, _lines, _ = _profile()
    rates = []
    for p in (0.0, 0.02, 0.05, 0.10, 0.20):
        g = generate(
            prof,
            section_cond=False,
            self_citation=True,
            line_edge_bias=False,
            p_rep=p,
            rep_window=1,
            p_initial_gallows=0.0,
            seed=100,
        )
        rates.append(adjacent_repeats(g)["observed"])
    # strictly non-decreasing, and the top probability clearly exceeds p_rep=0
    assert all(b >= a - 1e-9 for a, b in zip(rates, rates[1:])), rates
    assert rates[-1] > rates[0] + 0.05


def test_calibrate_p_rep_hits_target_repeat():
    """Bisection calibration of p_rep reproduces a chosen adjacent-repeat target
    (here the real 0.875%) within a small tolerance, in the full configuration."""
    prof, lines, _ = _profile()
    target = adjacent_repeats(lines)["observed"]  # the real 0.00875
    lig = real_line_initial_gallows_fraction(lines)
    p = calibrate_p_rep(
        prof,
        target,
        section_cond=True,
        line_edge_bias=True,
        rep_window=1,
        p_initial_gallows=lig,
        seed=200,
        n_iter=16,
    )
    assert 0.0 < p < 1.0
    g = generate(
        prof,
        section_cond=True,
        self_citation=True,
        line_edge_bias=True,
        p_rep=p,
        rep_window=1,
        p_initial_gallows=lig,
        seed=200,
    )
    obs = adjacent_repeats(g)["observed"]
    assert abs(obs - target) < 0.0008, (obs, target)


# --------------------------------------------------------------------------- #
# section_cond reproduces per-section top words                                #
# --------------------------------------------------------------------------- #
def test_section_cond_reproduces_per_section_top_words():
    """With section_cond ON, tokens on a synthetic line are drawn from that line's
    REAL section word-distribution, so the synthetic per-section top words match
    the real per-section top words. Verified on the two largest sections."""
    prof, lines, sections = _profile()
    lig = real_line_initial_gallows_fraction(lines)
    g = generate(
        prof,
        section_cond=True,
        self_citation=False,
        line_edge_bias=False,
        p_rep=0.0,
        rep_window=1,
        p_initial_gallows=lig,
        seed=100,
    )
    # real per-section top words
    real_by_sec: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for line, sec in zip(lines, sections):
        for t in line:
            real_by_sec[sec][t] += 1
    # synthetic per-section top words (synthetic line i has real section[i])
    gen_by_sec: dict[str, collections.Counter] = collections.defaultdict(collections.Counter)
    for line, sec in zip(g, sections):
        for t in line:
            gen_by_sec[sec][t] += 1

    largest = [s for s, _ in collections.Counter(sections).most_common(2)]
    for sec in largest:
        real_top = {w for w, _ in real_by_sec[sec].most_common(5)}
        gen_top = {w for w, _ in gen_by_sec[sec].most_common(5)}
        # at least 4 of the top-5 section words coincide (sampling noise on ties)
        assert len(real_top & gen_top) >= 4, (sec, real_top, gen_top)


# --------------------------------------------------------------------------- #
# Line geometry matches the real corpus                                        #
# --------------------------------------------------------------------------- #
def test_line_geometry_matches_real():
    """The generator emits one synthetic line per real line (exact line COUNT),
    and draws each length from the real line-length distribution, so the mean
    line length and total token count track the real corpus within tolerance."""
    prof, lines, _ = _profile()
    g = generate(
        prof,
        section_cond=True,
        self_citation=True,
        line_edge_bias=True,
        p_rep=0.05,
        rep_window=1,
        p_initial_gallows=0.15,
        seed=100,
    )
    assert len(g) == len(lines)  # exact line count
    real_mean = sum(len(l) for l in lines) / len(lines)
    gen_mean = sum(len(l) for l in g) / len(g)
    assert abs(real_mean - gen_mean) < 0.3, (real_mean, gen_mean)
    real_tok = sum(len(l) for l in lines)
    gen_tok = sum(len(l) for l in g)
    # total tokens within 3% (length is sampled, not copied)
    assert abs(real_tok - gen_tok) / real_tok < 0.03


def test_generate_deterministic_under_seed():
    """A fixed seed makes the synthetic corpus reproducible token-for-token."""
    prof, _lines, _ = _profile()
    kw = dict(
        section_cond=True,
        self_citation=True,
        line_edge_bias=True,
        p_rep=0.05,
        rep_window=1,
        p_initial_gallows=0.15,
    )
    a = generate(prof, seed=7, **kw)
    b = generate(prof, seed=7, **kw)
    assert a == b


# --------------------------------------------------------------------------- #
# Battery runs on synthetic                                                   #
# --------------------------------------------------------------------------- #
def test_battery_runs_on_synthetic_and_returns_finite():
    """The full imported battery (h2, adjacent_repeat, LAAFU, char-MI checkpoints,
    correlation length, Zipf, Heaps, gain_over_wordunigram) computes on a
    synthetic corpus and returns finite values. Small max_d/n_null keep it fast;
    correctness of each estimator is covered by the R58/R59/R60 suites."""
    prof, _lines, _ = _profile()
    g = generate(
        prof,
        section_cond=True,
        self_citation=True,
        line_edge_bias=True,
        p_rep=0.05,
        rep_window=1,
        p_initial_gallows=0.15,
        seed=100,
    )
    bat = measure_battery(g, seed=0, max_d=8, n_null=1)
    for key in (
        "h2",
        "adjacent_repeat",
        "laafu_I",
        "corr_length",
        "mi_d1",
        "mi_d5",
        "zipf_slope",
        "heaps_beta",
        "gain_over_wordunigram",
    ):
        assert key in bat
        assert math.isfinite(bat[key]), (key, bat[key])
    # h2 of a bag of REAL words ~ the real h2 by construction (within-token chars)
    assert 1.5 < bat["h2"] < 3.0


# --------------------------------------------------------------------------- #
# Match table + verdict logic                                                 #
# --------------------------------------------------------------------------- #
def test_build_match_rows_and_verdict_logic():
    """build_match_rows produces one row per tolerance-tracked metric with the
    within_tol flag, and classify_verdict returns 'generator_sufficient' iff every
    KEY metric is within tolerance, else names the resisting key metrics."""
    real = {
        "h2": 2.15, "adjacent_repeat": 0.00875, "laafu_I": 0.47,
        "line_initial_gallows": 0.15, "mi_d1": 1.72, "mi_d2": 0.83,
        "mi_d5": 0.13, "mi_d10": 0.02, "mi_d50": 0.0037, "mi_d100": 0.0025,
        "corr_length": 15.0, "zipf_slope": -1.08, "heaps_beta": 0.79,
        "gain_over_wordunigram": 0.034,
    }
    # identical generator -> all within tolerance -> sufficient
    gen_same = dict(real)
    rows = build_match_rows(real, gen_same)
    assert len(rows) == 14
    assert all(r["within_tol"] for r in rows)
    verdict, n_matched, n_key, resisting = classify_verdict(rows)
    assert verdict == "generator_sufficient"
    assert n_matched == n_key == len(KEY_METRICS)
    assert resisting == []
    # blow out ONE key metric (corr_length) beyond its tolerance -> insufficient
    gen_bad = dict(real)
    gen_bad["corr_length"] = 80.0  # |15-80| = 65 >> tol 5
    rows_bad = build_match_rows(real, gen_bad)
    verdict_b, n_matched_b, _n_key_b, resisting_b = classify_verdict(rows_bad)
    assert verdict_b == "generator_insufficient"
    assert "corr_length" in resisting_b
    assert n_matched_b == len(KEY_METRICS) - 1


# --------------------------------------------------------------------------- #
# Ablation ladder shape                                                       #
# --------------------------------------------------------------------------- #
def test_ablation_ladder_is_cumulative_and_ordered():
    """The ablation ladder has one entry per cumulative mechanism set, in order,
    starting at base (all toggles off) and ending at full (all on)."""
    labels = [lbl for lbl, _ in ABLATION_LADDER]
    assert labels == [
        "base",
        "base+section_cond",
        "base+section_cond+self_citation",
        "full",
    ]
    # base: all three toggles off; full: all three on; monotone turn-on
    base_toggles = ABLATION_LADDER[0][1]
    assert not any(base_toggles.values())
    full_toggles = ABLATION_LADDER[-1][1]
    assert all(full_toggles.values())
    assert MECHANISMS == ("base", "section_cond", "self_citation", "line_edge_bias")


# --------------------------------------------------------------------------- #
# main() writes all three CSVs with guardrail                                 #
# --------------------------------------------------------------------------- #
def test_main_writes_three_csvs_with_guardrail(tmp_path):
    """main() writes generator_match, generator_ablation, and generator_summary,
    each carrying the guardrail. Uses fixed p_rep / p_initial_gallows (skipping
    calibration) and small max_d / n_null to stay fast; the statistical content is
    validated by the dedicated battery tests."""
    match = tmp_path / "match.csv"
    ablation = tmp_path / "ablation.csv"
    summary = tmp_path / "summary.csv"
    rc = main(
        [
            str(CORPUS),
            "--max-d", "8",
            "--n-null", "1",
            "--p-rep", "0.0052",
            "--p-initial-gallows", "0.15",
            "--out-match", str(match),
            "--out-ablation", str(ablation),
            "--out-summary", str(summary),
        ]
    )
    assert rc == 0
    for p in (match, ablation, summary):
        assert p.exists() and p.stat().st_size > 0
        assert GUARDRAIL in p.read_text(encoding="utf-8")

    # match CSV: required columns; one row per tolerance metric; key metrics flagged
    with match.open(encoding="utf-8") as f:
        mrows = list(csv.DictReader(f))
    assert len(mrows) == 14
    for r in mrows:
        assert {
            "metric", "real", "generator", "abs_delta",
            "tolerance", "within_tol", "key_metric", "semantic_guardrail",
        } <= set(r)
        assert r["semantic_guardrail"] == GUARDRAIL
        assert r["within_tol"] in {"True", "False"}
    assert {r["metric"] for r in mrows if r["key_metric"] == "True"} == set(KEY_METRICS)

    # ablation CSV: exactly one row per cumulative mechanism set, in order
    with ablation.open(encoding="utf-8") as f:
        arows = list(csv.DictReader(f))
    assert [r["mechanism_set"] for r in arows] == [
        "base",
        "base+section_cond",
        "base+section_cond+self_citation",
        "full",
    ]
    for r in arows:
        assert {
            "mechanism_set", "h2", "adjacent_repeat", "laafu_I",
            "line_initial_gallows", "corr_length", "zipf_slope",
            "heaps_beta", "gain_over_wordunigram", "semantic_guardrail",
        } <= set(r)
        assert r["semantic_guardrail"] == GUARDRAIL

    # summary CSV: required metrics present and well-formed
    with summary.open(encoding="utf-8") as f:
        s = {r["metric"]: r["value"] for r in csv.DictReader(f)}
    for metric in (
        "mechanisms_in_full",
        "n_metrics",
        "n_matched",
        "p_rep_used",
        "verdict",
        "guardrail",
    ):
        assert metric in s, metric
    assert s["guardrail"] == GUARDRAIL
    assert s["verdict"] in {"generator_sufficient", "generator_insufficient"}
    assert s["mechanisms_in_full"] == "base+section_cond+self_citation+line_edge_bias"
    assert int(s["n_metrics"]) == 14
    # the calibrated/forced p_rep is echoed
    assert abs(float(s["p_rep_used"]) - 0.0052) < 1e-9


def test_main_self_citation_lifts_repeat_in_ablation(tmp_path):
    """In the ablation table, turning on self_citation must lift the adjacent-
    repeat rate above the base / section_cond rows (which sit at the i.i.d. floor).
    This is the ablation's headline: self_citation is NECESSARY for repetition."""
    match = tmp_path / "m.csv"
    ablation = tmp_path / "a.csv"
    summary = tmp_path / "s.csv"
    main(
        [
            str(CORPUS),
            "--max-d", "8",
            "--n-null", "1",
            "--p-rep", "0.05",
            "--p-initial-gallows", "0.15",
            "--out-match", str(match),
            "--out-ablation", str(ablation),
            "--out-summary", str(summary),
        ]
    )
    with ablation.open(encoding="utf-8") as f:
        arows = {r["mechanism_set"]: r for r in csv.DictReader(f)}
    base_rep = float(arows["base"]["adjacent_repeat"])
    seccond_rep = float(arows["base+section_cond"]["adjacent_repeat"])
    selfcite_rep = float(arows["base+section_cond+self_citation"]["adjacent_repeat"])
    # base and section_cond are at the i.i.d. floor (no copying)
    assert base_rep < 0.005
    assert seccond_rep < 0.006
    # self_citation clearly lifts repetition above those
    assert selfcite_rep > seccond_rep + 0.02
