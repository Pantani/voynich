"""Tests for analyze_hand_campaign (Rota 72, hand-campaign token signature).

Covers the core logic deterministically on synthetic inputs (no corpus needed):
tokenisation, prefix/length/a-o classifiers, Miller-Madow entropy + bias floor,
repeat rate, the folio-block permutation null, the pure-function verdict, and the
campaign-boundary contrast. One extra test pins the hand-attribution source to
R68 (the $H tag) so it can never silently diverge.
"""
import pytest

from scripts.analyze_hand_campaign import (
    GUARDRAIL,
    ao_nucleus_count,
    campaign_boundary_contrast,
    char_h2,
    classify_verdict,
    clean_token,
    folio_block_v,
    group_signature,
    length_bin,
    parse_folio_tokens,
    prefix_bucket,
    repeat_rate,
)


# --------------------------------------------------------------------------- #
# Tokenisation                                                                 #
# --------------------------------------------------------------------------- #
def test_clean_token_strips_markup_and_resolves_alternates():
    assert clean_token("fachys") == "fachys"
    assert clean_token("[cth:oto]y") == "cthy"  # alternate -> first option
    assert clean_token("ok<$>ar") == "okar"  # inline markup removed
    assert clean_token("da200") == "da"  # digits dropped
    assert clean_token("<->") == ""  # pure markup -> empty
    assert clean_token("{plant}qoy") == "qoy"  # comment removed


def test_parse_folio_tokens_only_reads_locus_lines(tmp_path):
    corpus = tmp_path / "mini.txt"
    corpus.write_text(
        "#=IVTFF Eva- 2.0\n"
        "<f1r>      <! $L=A $H=1 $I=H>\n"
        "<f1r.1,@P0>\tqokar.otal.daiin\n"
        "<f1r.2,@P0>\tchol.qoy\n"
        "<f2v>      <! $L=B $H=2 $I=B>\n"
        "<f2v.1,@P0>\totar.otar.ar\n",
        encoding="utf-8",
    )
    by_folio = parse_folio_tokens(corpus)
    assert by_folio["f1r"] == ["qokar", "otal", "daiin", "chol", "qoy"]
    assert by_folio["f2v"] == ["otar", "otar", "ar"]
    # header lines contribute no tokens
    assert "f1r" in by_folio and len(by_folio) == 2


# --------------------------------------------------------------------------- #
# Per-token classifiers                                                        #
# --------------------------------------------------------------------------- #
def test_prefix_bucket_covers_operators_and_other():
    assert prefix_bucket("qokeey") == "qo"
    assert prefix_bucket("okar") == "ok"
    assert prefix_bucket("otal") == "ot"
    assert prefix_bucket("ykal") == "yk"
    assert prefix_bucket("ytar") == "yt"
    assert prefix_bucket("daiin") == "other"
    assert prefix_bucket("chol") == "other"


def test_length_bin_boundaries():
    assert length_bin("ar") == "1-2"
    assert length_bin("okar") == "3-4"
    assert length_bin("qokar") == "5-6"
    assert length_bin("qokeedy") == "7+"


def test_ao_nucleus_count_matches_matrix_axis():
    # 'ar' -> one a-nucleus; 'or' -> one o-nucleus; 'okal' -> a before l
    assert ao_nucleus_count("ar") == (1, 0)
    assert ao_nucleus_count("or") == (0, 1)
    assert ao_nucleus_count("okal") == (1, 0)
    assert ao_nucleus_count("okol") == (0, 1)
    assert ao_nucleus_count("daiin") == (0, 0)  # no r/l after a/o
    assert ao_nucleus_count("oror") == (0, 2)


# --------------------------------------------------------------------------- #
# Entropy + repeat rate                                                        #
# --------------------------------------------------------------------------- #
def test_char_h2_low_for_single_repeated_token():
    # a stream of one repeated token has near-zero PLUGIN char uncertainty (only
    # the boundary symbol breaks it up); the MM bias floor is reported explicitly.
    h2_plug, h2_mm, floor = char_h2(["aaaa", "aaaa"])
    assert 0.0 <= h2_plug < 1.0  # very low conditional char entropy
    # bias floor is exactly the MM correction magnitude (plugin - MM)
    assert floor == pytest.approx(h2_plug - h2_mm, abs=1e-12)


def test_char_h2_positive_and_mm_corrects_upward():
    toks = ["qokar", "otal", "chol", "daiin", "qokeedy", "shol"]
    h2_plug, h2_mm, floor = char_h2(toks)
    assert h2_plug > 0.0
    # Miller-Madow adds a positive small-sample correction to conditional entropy
    assert h2_mm >= h2_plug - 1e-9
    assert floor == pytest.approx(h2_plug - h2_mm, abs=1e-9)


def test_repeat_rate_counts_adjacent_identical():
    assert repeat_rate(["otar", "otar", "ar"]) == pytest.approx(0.5)  # 1 of 2 pairs
    assert repeat_rate(["a", "b", "c"]) == 0.0
    assert repeat_rate(["x"]) == 0.0
    assert repeat_rate(["q", "q", "q"]) == pytest.approx(1.0)


def test_group_signature_shapes_and_fractions():
    toks = ["qokar", "okal", "otar", "daiin"]
    sig = group_signature(toks)
    assert sig["n_tokens"] == 4.0
    assert sig["frac_qo"] == pytest.approx(0.25)
    assert sig["frac_ok"] == pytest.approx(0.25)
    assert sig["frac_ot"] == pytest.approx(0.25)
    assert sig["frac_other"] == pytest.approx(0.25)
    # fractions over the prefix buckets sum to 1
    total = sum(sig[f"frac_{b}"] for b in ("qo", "ok", "ot", "yk", "yt", "other"))
    assert total == pytest.approx(1.0)


# --------------------------------------------------------------------------- #
# Folio-block permutation null (decisive machinery)                           #
# --------------------------------------------------------------------------- #
def test_folio_block_v_detects_perfect_hand_separation():
    # Two hands, each on several folios, with a perfectly hand-specific prefix
    # (hand 1 -> qo only, hand 2 -> ot only). The observed V is maximal and
    # strictly exceeds the folio-block null mean: the real signal is detected and
    # sits above the finite-sample bias floor. (p is checked on the larger,
    # well-powered corpus run, not this tiny synthetic where n_folios is small.)
    folio_hand = {f"f{i}": ("1" if i < 4 else "2") for i in range(8)}
    folio_tokens = {
        f"f{i}": (["qoa", "qob"] if i < 4 else ["ota", "otb"]) for i in range(8)
    }
    folios = [f"f{i}" for i in range(8)]
    v_obs, v_null, p, n_hands = folio_block_v(
        folio_hand, folio_tokens, folios, prefix_bucket, n_perm=500, seed=1
    )
    assert n_hands == 2
    assert v_obs == pytest.approx(1.0, abs=1e-9)  # perfect association
    assert v_obs > v_null  # real signal beats its folio-block bias floor
    assert v_null < 1.0  # the null is genuinely broken by shuffling (not degenerate)
    assert 0.0 < p <= 1.0  # a valid one-sided p (power is corpus-scale, see summary)


def test_folio_block_v_null_kills_spurious_collinear_signal():
    # Only ONE folio per hand: hand is fully confounded with the folio block, so
    # every permutation reproduces a perfect table and the observed V is NOT
    # extreme vs the null -> p == 1.0 (the null correctly refuses to crown it).
    folio_hand = {"f1": "1", "f2": "2"}
    folio_tokens = {"f1": ["qoa", "qob"], "f2": ["ota", "otb"]}
    v_obs, v_null, p, n_hands = folio_block_v(
        folio_hand, folio_tokens, ["f1", "f2"], prefix_bucket, n_perm=200, seed=2
    )
    assert p == pytest.approx(1.0)


def test_folio_block_v_determinism_under_seed():
    folio_hand = {f"f{i}": str(i % 2 + 1) for i in range(6)}
    folio_tokens = {
        f"f{i}": (["qoa"] if i % 2 == 0 else ["ota"]) * 5 + ["daiin"]
        for i in range(6)
    }
    folios = [f"f{i}" for i in range(6)]
    a = folio_block_v(folio_hand, folio_tokens, folios, prefix_bucket, 100, 42)
    b = folio_block_v(folio_hand, folio_tokens, folios, prefix_bucket, 100, 42)
    assert a == b  # same seed -> identical (v_obs, v_null, p, n_hands)


# --------------------------------------------------------------------------- #
# Verdict (pure function)                                                      #
# --------------------------------------------------------------------------- #
def test_classify_verdict_truth_table():
    # double control (within Currier x section) survives -> signature beyond Currier
    assert (
        classify_verdict(True, True, 0.5)
        == "hand_campaign_signature_beyond_currier"
    )
    # near-perfect collinearity and nothing survives the double control -> collinear
    assert classify_verdict(True, False, 0.98) == "hand_collinear_with_currier"
    assert classify_verdict(False, False, 0.98) == "hand_collinear_with_currier"
    # not collinear, nothing survives -> unconfirmed
    assert classify_verdict(True, False, 0.3) == "hand_signature_unconfirmed"
    # tested, not survived, below the collinearity threshold -> unconfirmed
    assert classify_verdict(True, False, 0.84) == "hand_signature_unconfirmed"


# --------------------------------------------------------------------------- #
# Campaign-boundary contrast                                                   #
# --------------------------------------------------------------------------- #
def test_campaign_boundary_contrast_finds_within_quire_seam():
    folio_rows = [
        {"folio": "f1", "quire": "A", "hand": "1"},
        {"folio": "f2", "quire": "A", "hand": "1"},  # f1->f2 same-hand pair
        {"folio": "f3", "quire": "A", "hand": "2"},  # f2->f3 hand change in quire = seam
        {"folio": "f4", "quire": "B", "hand": "2"},  # f3->f4 same hand (also quire break)
    ]
    folio_tokens = {
        "f1": ["qoa", "qob"],
        "f2": ["qoc", "qod"],
        "f3": ["ota", "otb"],
        "f4": ["otc", "otd"],
    }
    out = campaign_boundary_contrast(folio_rows, folio_tokens)
    assert out["n_campaign_seams"] == 1.0  # only f2->f3 (same quire, hand change)
    # both f1->f2 and f3->f4 are same-hand adjacent pairs (within-hand baseline)
    assert out["n_same_hand_pairs"] == 2.0
    assert out["mean_tv_at_seam"] == pytest.approx(1.0)  # qo-only vs ot-only = max TV
    assert out["mean_tv_same_hand"] == pytest.approx(0.0)  # qo|qo and ot|ot = 0


# --------------------------------------------------------------------------- #
# Hand-attribution source pinned to R68 ($H tag)                               #
# --------------------------------------------------------------------------- #
def test_hand_source_is_r68_dollar_H_tag():
    # The hand attribution MUST be R68's $H tag, parsed by analyze_codicology.
    from scripts.analyze_codicology import hand_label

    assert hand_label({"H": "3"}) == "3"
    assert hand_label({"H": "?"}) == "unknown"
    assert hand_label({}) == "unknown"


def test_guardrail_present():
    assert GUARDRAIL == "rota72_hand_campaign_not_decipherment"
