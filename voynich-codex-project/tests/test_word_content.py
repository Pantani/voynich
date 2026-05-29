"""Tests for Rota 56 word-level topical content (scripts/analyze_word_content.py).

Covers: a SYNTHETIC known-answer case (words that perfectly determine section ->
I_norm~1; words independent of section -> observed ~ null, I_norm~0); MI/entropy
correctness; lift computation; that the permutation null discriminates real signal
(low p) from independence (high p); and integration on the real ZL3b corpus
(I_section_word_obs finite, ~37671 token coverage) with both CSVs + guardrail.

Also covers the two PRE-REGISTERED confound controls added on top of Rota 56:
  CONTROL 1 — paragraph-only restriction (locus_kind == 'P') changes/reduces the
    token set used for I(section;word).
  CONTROL 2 — a folio-block permutation null (each folio keeps its whole bag of
    tokens; only the per-folio section labels are shuffled across folios). On
    autocorrelated data its p must be >= the token-level p, and on a folio-block
    confound (folio-specific words, no real topic) it must ABSORB the inflated
    token-level MI (null mean ~ observed, p large) while the token-level null
    false-positives.
"""
from __future__ import annotations

import collections
import csv
from pathlib import Path

from scripts.analyze_word_content import (
    GUARDRAIL,
    build_records,
    build_records_with_kind,
    decide_verdict,
    diagnostic_rows,
    entropy,
    flattest_words,
    folio_block_null,
    i_norm,
    main,
    marker_vs_nonmarker,
    mutual_information,
    permutation_null,
    top_lift_by_section,
)
from scripts.analyze_nucleus import parse_corpus
from scripts.analyze_nucleus_context import parse_corpus_with_kind

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"


# --------------------------------------------------------------------------
# Entropy / MI correctness
# --------------------------------------------------------------------------
def test_entropy_known_values():
    # uniform over 4 outcomes -> 2 bits; degenerate -> 0; empty -> 0
    assert abs(entropy([1, 1, 1, 1]) - 2.0) < 1e-9
    assert entropy([10]) == 0.0
    assert entropy([]) == 0.0
    # fair coin = 1 bit
    assert abs(entropy([5, 5]) - 1.0) < 1e-9


def test_mutual_information_perfect_and_independent():
    # word perfectly determines section -> I == H(section)
    perfect = [("wa", "herbal")] * 50 + [("wb", "recipes")] * 50
    h = entropy(collections.Counter(s for _, s in perfect).values())  # 1 bit
    mi = mutual_information(perfect)
    assert abs(mi - h) < 1e-9
    assert abs(mi - 1.0) < 1e-9
    # word carries NO information about section (every word evenly split) -> I == 0
    indep = [("wa", "herbal"), ("wa", "recipes"), ("wb", "herbal"), ("wb", "recipes")] * 25
    assert mutual_information(indep) < 1e-9
    assert mutual_information([]) == 0.0


# --------------------------------------------------------------------------
# SYNTHETIC known-answer: I_norm ~ 1 for perfect, ~ 0 for independent
# --------------------------------------------------------------------------
def test_synthetic_perfect_determination_inorm_near_one():
    pairs = [("wa", "herbal")] * 60 + [("wb", "recipes")] * 60
    h = entropy(collections.Counter(s for _, s in pairs).values())
    obs, null_mean, null_std, p = permutation_null(pairs, n_perm=200, seed=1)
    norm = i_norm(obs, null_mean, h)
    # signal massively exceeds its shuffle-bias floor and explains ~all of H(section)
    assert obs > null_mean
    assert norm > 0.95
    assert p < 0.05


def test_synthetic_independent_inorm_near_zero_and_high_p():
    # Each word is split evenly across sections -> no real signal; any observed MI
    # is pure finite-sample bias, so observed should sit at/under the null mean and
    # the permutation p must be large (not significant).
    pairs = (
        [("wa", "herbal"), ("wa", "recipes"), ("wb", "herbal"), ("wb", "recipes")] * 60
    )
    h = entropy(collections.Counter(s for _, s in pairs).values())
    obs, null_mean, null_std, p = permutation_null(pairs, n_perm=200, seed=2)
    norm = i_norm(obs, null_mean, h)
    assert norm < 0.05  # essentially nothing beyond bias
    assert p > 0.2  # permutation does NOT flag a real signal


# --------------------------------------------------------------------------
# Permutation null DISCRIMINATES: real -> low p, null -> high p
# --------------------------------------------------------------------------
def test_permutation_discriminates_real_vs_null():
    real = [("wa", "herbal")] * 40 + [("wb", "recipes")] * 40
    _, _, _, p_real = permutation_null(real, n_perm=200, seed=3)
    null = [("wa", "herbal"), ("wa", "recipes"), ("wb", "herbal"), ("wb", "recipes")] * 20
    _, _, _, p_null = permutation_null(null, n_perm=200, seed=3)
    assert p_real < 0.05 < p_null


def test_permutation_null_reports_positive_bias_floor():
    # With many singleton word types, MI is positively biased: the null mean must
    # be > 0 even though there is no real word->section structure. This is the
    # Rota-55 lesson encoded as a regression guard.
    pairs = [(f"w{i}", "herbal" if i % 2 else "recipes") for i in range(200)]
    obs, null_mean, null_std, p = permutation_null(pairs, n_perm=150, seed=4)
    assert null_mean > 0.0  # finite-sample bias floor is non-zero


# --------------------------------------------------------------------------
# Lift computation
# --------------------------------------------------------------------------
def test_lift_computation_matches_definition():
    # Corpus: 100 tokens, section split 50/50. Word 'wa' (freq 40) appears 30x in
    # herbal, 10x in recipes => P(herbal|wa)=0.75, P(herbal)=0.5 => lift=1.5.
    pairs = (
        [("wa", "herbal")] * 30
        + [("wa", "recipes")] * 10
        + [("filler", "herbal")] * 20
        + [("filler", "recipes")] * 40
    )
    word_cur: dict = collections.defaultdict(collections.Counter)
    rows = diagnostic_rows(pairs, word_cur, min_freq=20, guardrail="g")
    wa = next(r for r in rows if r["word"] == "wa")
    assert wa["top_section"] == "herbal"
    assert abs(wa["lift_top"] - 1.5) < 1e-6
    # top_lift_by_section recomputes lift per target section and agrees
    tops = top_lift_by_section(rows, pairs, ["herbal"], top_n=5)
    assert ("wa", 40, 1.5) in tops["herbal"]


def test_diagnostic_rows_respects_min_freq_and_currier_skew():
    pairs = [("rare", "herbal")] * 5 + [("common", "recipes")] * 30 + [("common", "herbal")] * 10
    word_cur: dict = collections.defaultdict(collections.Counter)
    word_cur["common"].update({"B": 35, "A": 5})  # skewed to B
    rows = diagnostic_rows(pairs, word_cur, min_freq=20, guardrail="g")
    words = {r["word"] for r in rows}
    assert "common" in words and "rare" not in words  # freq gate at 20
    common = next(r for r in rows if r["word"] == "common")
    assert abs(common["currier_skew"] - (30 / 40)) < 1e-6  # |35-5|/40


# --------------------------------------------------------------------------
# Marker vs non-marker + verdict logic
# --------------------------------------------------------------------------
def test_marker_vs_nonmarker_split():
    rows = [
        {"word": "qokeedy", "freq": 50, "section_entropy_norm": 0.9},  # marker, flat
        {"word": "okaiin", "freq": 50, "section_entropy_norm": 0.8},   # marker
        {"word": "daiin", "freq": 50, "section_entropy_norm": 0.4},    # non-marker, peaky
    ]
    mk, nm, n_mk, n_nm = marker_vs_nonmarker(rows)
    assert n_mk == 2 and n_nm == 1
    # marker mean diagnosticity (1-Hn) lower than non-marker -> markers flatter
    assert mk < nm


def test_decide_verdict_branches():
    # pooled real AND survives B -> topical_vocabulary
    assert decide_verdict(0.9, 0.6, 0.003, 0.10, 0.004) == "topical_vocabulary"
    # pooled real but collapses within B (norm ~0 / high p) -> scribe_vocabulary
    assert decide_verdict(0.9, 0.6, 0.003, 0.001, 0.6) == "scribe_vocabulary"
    # pooled NOT significant -> no_topical_signal
    assert decide_verdict(0.6, 0.59, 0.40, 0.10, 0.004) == "no_topical_signal"


def test_flattest_words_are_high_entropy():
    rows = [
        {"word": "flat", "freq": 100, "section_entropy_norm": 0.99},
        {"word": "peaky", "freq": 100, "section_entropy_norm": 0.20},
    ]
    flat = flattest_words(rows, top_n=1)
    assert flat[0][0] == "flat"


# --------------------------------------------------------------------------
# Integration on the real corpus
# --------------------------------------------------------------------------
def test_build_records_real_corpus_shapes():
    from scripts.analyze_nucleus import parse_corpus

    fc, toks = parse_corpus(CORPUS)
    rec = build_records(fc, toks)
    # B spans multiple sections (the decisive control needs >1 section in B)
    secs_B = {s for _, s in rec["pairs_B"]}
    assert len(secs_B) >= 3
    # every pair is (word, section) with a non-'other' section
    assert all(s != "other" for _, s in rec["pairs_all"])
    assert len(rec["pairs_all"]) > 30000


def test_integration_real_signal_and_token_count():
    """I(section;word) is finite, exceeds its null, and coverage ~ full corpus."""
    from scripts.analyze_nucleus import parse_corpus

    fc, toks = parse_corpus(CORPUS)
    rec = build_records(fc, toks)
    pairs = rec["pairs_all"]
    h = entropy(collections.Counter(s for _, s in pairs).values())
    obs, null_mean, null_std, p = permutation_null(pairs, n_perm=80, seed=0)
    assert 0.0 < obs < h  # finite, bounded by H(section)
    assert obs > null_mean  # real signal beats the finite-sample bias floor
    assert p < 0.05
    # actual token count used by this route (clean tokens with a real section)
    assert len(pairs) == 37671


def test_main_writes_both_csvs_with_guardrail(tmp_path):
    diag = tmp_path / "diag.csv"
    summ = tmp_path / "summary.csv"
    rc = main(
        [
            str(CORPUS),
            "--n-perm",
            "30",
            "--out-diagnostic",
            str(diag),
            "--out-summary",
            str(summ),
        ]
    )
    assert rc == 0
    for p in (diag, summ):
        assert p.exists() and p.stat().st_size > 0
        assert GUARDRAIL in p.read_text(encoding="utf-8")
    # summary has the required metrics
    rows = list(csv.DictReader(summ.open(encoding="utf-8")))
    metrics = {r["metric"] for r in rows}
    for required in (
        "H_section_bits",
        "I_section_word_obs",
        "I_null_mean",
        "I_perm_p",
        "I_norm",
        "I_within_B_obs",
        "I_within_B_null_mean",
        "I_within_B_norm",
        "I_within_A_norm",
        "marker_mean_diag",
        "nonmarker_mean_diag",
        "n_types_freq20",
        "token_coverage",
        "verdict",
    ):
        assert required in metrics
    # verdict is one of the three encoded outcomes
    verdict = next(r["value"] for r in rows if r["metric"] == "verdict")
    assert verdict in {"topical_vocabulary", "scribe_vocabulary", "no_topical_signal"}
    # diagnostic CSV has the required columns
    drows = list(csv.DictReader(diag.open(encoding="utf-8")))
    assert drows  # non-empty
    assert set(drows[0].keys()) == {
        "word",
        "freq",
        "top_section",
        "lift_top",
        "section_entropy_norm",
        "currier_skew",
        "semantic_guardrail",
    }


# ==========================================================================
# CONTROL 1 — paragraph-only restriction (locus_kind == 'P')
# ==========================================================================
def test_paragraph_restriction_reduces_and_changes_the_set():
    """Restricting to prose (kind=='P') must DROP non-prose tokens (labels/
    circular/radial) and so SHRINK the token set, while keeping it a proper
    SUBSET of the unrestricted pairs. On ZL3b this removes ~3000+ tokens."""
    fc, _ = parse_corpus(CORPUS)
    rk = build_records_with_kind(fc, parse_corpus_with_kind(CORPUS))
    n_all = len(rk["pairs_all"])
    n_P = len(rk["pairs_P"])
    n_BP = len(rk["pairs_BP"])
    n_B = len(rk["pairs_B"])
    # strictly fewer prose tokens than all tokens (real non-prose loci exist)
    assert 0 < n_P < n_all
    assert n_all - n_P > 1000  # labels+circular+radial are a sizeable chunk
    # within-B prose is a strict subset of within-B
    assert 0 < n_BP < n_B
    # the prose pairs are a multiset-subset of all pairs (restriction, not relabel)
    c_all = collections.Counter(rk["pairs_all"])
    c_P = collections.Counter(rk["pairs_P"])
    assert all(c_P[k] <= c_all[k] for k in c_P)
    # and the DIAGNOSTIC set can change: some words drop below MIN_FREQ once the
    # label/circular occurrences are removed (set is not identical).
    diag_all = {r["word"] for r in diagnostic_rows(rk["pairs_all"], rk["word_cur"], 20, "g")}
    diag_P = {r["word"] for r in diagnostic_rows(rk["pairs_P"], rk["word_cur"], 20, "g")}
    assert diag_P != diag_all
    assert diag_P  # still non-empty


def test_build_records_with_kind_matches_unrestricted_totals():
    """The kind-aware builder must reproduce the canonical build_records totals
    on 'pairs_all' (same tokenization / same (folio,token) stream), so the only
    thing the new path adds is the kind split — not a different corpus."""
    fc, toks = parse_corpus(CORPUS)
    base = build_records(fc, toks)
    rk = build_records_with_kind(fc, parse_corpus_with_kind(CORPUS))
    assert collections.Counter(rk["pairs_all"]) == collections.Counter(base["pairs_all"])
    assert collections.Counter(rk["pairs_B"]) == collections.Counter(base["pairs_B"])
    # triples carry the folio and reduce to the same (word,section) pairs
    assert [(w, s) for _, w, s in rk["triples_all"]] == rk["pairs_all"]


# ==========================================================================
# CONTROL 2 — folio-block permutation null
# ==========================================================================
def test_folio_block_null_preserves_per_folio_section_marginal():
    """Mechanics: the folio-block null shuffles the LIST of per-folio section
    labels, so the COUNT of folios per section is invariant under the null
    (only WHICH folio gets WHICH label changes). We verify the observed MI is
    computed correctly and the null mean is finite/non-negative."""
    triples = []
    for i in range(5):  # 5 herbal folios, 5 recipes folios
        triples += [(f"h{i}", f"w{i}", "herbal")] * 20
    for i in range(5):
        triples += [(f"r{i}", f"v{i}", "recipes")] * 20
    obs, null_mean, null_std, p = folio_block_null(triples, n_perm=200, seed=7)
    # observed equals the direct MI of the (word,section) pairs
    direct = mutual_information([(w, s) for _, w, s in triples])
    assert abs(obs - direct) < 1e-12
    assert null_mean >= 0.0 and null_std >= 0.0
    assert 1.0 / 201 <= p <= 1.0


def test_folio_block_p_ge_token_p_on_autocorrelated_data():
    """On autocorrelated data (each folio repeats its OWN word many times), the
    token-level null is too tight and reports a tiny p; the conservative folio-
    block null must report a p that is >= the token-level p. This is the core
    LAAFU guard the cryptanalyst pre-registered."""
    triples = []
    for i in range(6):
        triples += [(f"h{i}", f"word_h{i}", "herbal")] * 50
    for i in range(6):
        triples += [(f"r{i}", f"word_r{i}", "recipes")] * 50
    pairs = [(w, s) for _, w, s in triples]
    _, _, _, p_token = permutation_null(pairs, n_perm=300, seed=8)
    _, _, _, p_fb = folio_block_null(triples, n_perm=300, seed=8)
    assert p_fb >= p_token


def test_folio_block_null_absorbs_a_folio_block_confound():
    """Decisive synthetic: a folio-block CONFOUND inflates token-level MI but is
    NOT real topic. Each folio carries a unique word repeated 50x; section is a
    deterministic function of the folio and many folios share each section.

    - Token-perm breaks the folio bag -> observed MI looks hugely significant
      (false positive): obs >> null, p small.
    - Folio-block keeps each folio's bag intact and only relabels folios; because
      the word identifies the folio (not the topic), shuffling labels reproduces
      the SAME MI -> null mean ~ observed, p large. The confound is absorbed."""
    triples = []
    for i in range(6):
        triples += [(f"h{i}", f"only_h{i}", "herbal")] * 50
    for i in range(6):
        triples += [(f"r{i}", f"only_r{i}", "recipes")] * 50
    pairs = [(w, s) for _, w, s in triples]

    obs_t, null_t, _, p_t = permutation_null(pairs, n_perm=300, seed=9)
    obs_f, null_f, _, p_f = folio_block_null(triples, n_perm=300, seed=9)

    # token-level FALSE POSITIVE: high observed, near-zero null, tiny p
    assert obs_t > 0.9
    assert null_t < 0.2
    assert p_t < 0.05
    # folio-block ABSORBS it: null mean ~ observed, p not significant
    assert abs(obs_f - null_f) < 0.05
    assert p_f > 0.20

    # CONTRAST — a REAL topic word (shared within a section across folios) still
    # survives the folio-block null (label shuffle scrambles the association).
    triples_real = []
    for i in range(6):
        triples_real += [(f"h{i}", "TOPIC_HERB", "herbal")] * 50
    for i in range(6):
        triples_real += [(f"r{i}", "TOPIC_REC", "recipes")] * 50
    obs_r, null_r, _, p_r = folio_block_null(triples_real, n_perm=300, seed=9)
    assert obs_r - null_r > 0.5  # signal stands well above the conservative null
    assert p_r < 0.05


def test_folio_block_null_is_more_conservative_on_real_within_B():
    """On the REAL ZL3b within-Currier-B data, the folio-block null mean must sit
    ABOVE the token-perm null mean (it absorbs within-folio autocorrelation), so
    the bias-corrected signal shrinks. The signal still survives here, but the
    point of this guard is the ORDERING null_fb > null_token (conservativeness)."""
    fc, _ = parse_corpus(CORPUS)
    rk = build_records_with_kind(fc, parse_corpus_with_kind(CORPUS))
    pairs_B = rk["pairs_B"]
    _, null_token, _, _ = permutation_null(pairs_B, n_perm=120, seed=10)
    obs_fb, null_fb, _, p_fb = folio_block_null(rk["triples_B"], n_perm=120, seed=10)
    assert null_fb > null_token  # folio-block null is the conservative (looser) one
    assert obs_fb > null_fb  # but observed still beats even the conservative null


# ==========================================================================
# Controlled summary metrics land in the CSV + controlled verdict is valid
# ==========================================================================
def test_main_writes_controlled_metrics(tmp_path):
    diag = tmp_path / "diag.csv"
    summ = tmp_path / "summary.csv"
    rc = main(
        [
            str(CORPUS),
            "--n-perm",
            "30",
            "--out-diagnostic",
            str(diag),
            "--out-summary",
            str(summ),
        ]
    )
    assert rc == 0
    rows = list(csv.DictReader(summ.open(encoding="utf-8")))
    metrics = {r["metric"]: r["value"] for r in rows}
    # the new pre-registered control metrics must be present
    for required in (
        "I_paragraph_only_norm",
        "I_paragraph_only_p",
        "I_within_B_paragraph_norm",
        "I_within_B_paragraph_p",
        "I_within_B_folioblock_p",
        "I_within_B_paragraph_folioblock_p",
        "verdict_controlled",
        "token_coverage_paragraph",
        "token_coverage_within_B_paragraph",
    ):
        assert required in metrics
    # the OLD metrics must still be present (nothing removed)
    for kept in ("I_norm", "I_within_B_norm", "verdict", "token_coverage"):
        assert kept in metrics
    # controlled verdict is one of the three encoded outcomes
    assert metrics["verdict_controlled"] in {
        "topical_vocabulary",
        "scribe_vocabulary",
        "no_topical_signal",
    }
    # paragraph coverage is strictly less than full coverage
    assert int(metrics["token_coverage_paragraph"]) < int(metrics["token_coverage"])
