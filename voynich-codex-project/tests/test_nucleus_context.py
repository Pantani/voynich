"""Tests for Rota 54 nucleus-context analysis (scripts/analyze_nucleus_context.py).

Covers the three falsifiable sub-attacks and verifies the parse reproduces the
Rota 53 ch-XOR-sh total (14594) so the kind-aware parser stays consistent with
scripts.analyze_nucleus.
"""
from __future__ import annotations

import collections
import csv
from pathlib import Path

from scripts.analyze_nucleus import parse_corpus
from scripts.analyze_nucleus_context import (
    GUARDRAIL,
    build,
    folio_num,
    main,
    operator_of,
    parse_corpus_with_kind,
    shannon_entropy,
)

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "data" / "raw" / "ZL3b-n.txt"


def test_operator_of_precedence_ok_over_ot_over_none():
    assert operator_of("qokeedy") == "ok"
    assert operator_of("qotedy") == "ot"
    assert operator_of("shedy") == "none"
    # ok dominates even when ot also present
    assert operator_of("okotaiin") == "ok"
    assert folio_num("f75r") == 75
    assert folio_num("f103v") == 103


def test_shannon_entropy_bounds():
    # uniform over 2 outcomes -> 1 bit
    assert abs(shannon_entropy(collections.Counter({"a": 5, "b": 5})) - 1.0) < 1e-9
    # deterministic -> 0 bits
    assert shannon_entropy(collections.Counter({"a": 10})) == 0.0
    # empty -> 0
    assert shannon_entropy(collections.Counter()) == 0.0
    # 4 equiprobable outcomes -> 2 bits
    assert abs(shannon_entropy(collections.Counter({c: 3 for c in "abcd"})) - 2.0) < 1e-9


def test_parse_corpus_with_kind_captures_kinds_and_reproduces_totals():
    records = parse_corpus_with_kind(CORPUS)
    kinds = {k for _, k, _ in records}
    # KIND letters seen in ZL3b are P (text), L (label), C (circular), R (other)
    assert {"P", "L"} <= kinds
    assert kinds <= {"P", "L", "C", "R", "?"}
    # token enumeration must match analyze_nucleus.parse_corpus exactly
    _, ref_tokens = parse_corpus(CORPUS)
    assert len(records) == len(ref_tokens)
    assert [(f, t) for f, _, t in records] == ref_tokens


def test_build_reproduces_rota53_chsh_total():
    """Sanity gate: the binary ch-XOR-sh universe is the Rota 53 14594 tokens."""
    records = parse_corpus_with_kind(CORPUS)
    b = build(records)
    assert b["n_chsh"] == 14594


def test_r54a_balneo_table_only_L_and_P_in_75_84():
    records = parse_corpus_with_kind(CORPUS)
    b = build(records)
    bal = b["balneo"]
    # only L and P kinds enter the 2x2; the cell counts are integers > 0 for P
    assert set(bal.keys()) <= {"L", "P"}
    assert sum(bal["P"].values()) > 0
    # falsifiable H1 (sh higher in labels) is NOT supported: sh% in P >= sh% in L
    n_sh_L = bal.get("L", collections.Counter()).get("sh", 0)
    n_L = sum(bal.get("L", collections.Counter()).values())
    n_sh_P = bal.get("P", collections.Counter()).get("sh", 0)
    n_P = sum(bal["P"].values())
    sh_pct_L = 100 * n_sh_L / n_L if n_L else 0.0
    sh_pct_P = 100 * n_sh_P / n_P if n_P else 0.0
    assert sh_pct_P >= sh_pct_L  # H1 refuted on the real corpus


def test_r54b_operator_table_partitions_all_chsh_tokens():
    records = parse_corpus_with_kind(CORPUS)
    b = build(records)
    op = b["operator"]
    assert set(op.keys()) == {"ok", "ot", "none"}
    total = sum(sum(c.values()) for c in op.values())
    assert total == b["n_chsh"]  # operator labels partition the universe


def test_r54c_next_char_uses_all_occurrences_and_marks_end():
    # 'chedy': ch->e ; 'sh' absent. 'qoshey': sh->e ; 'ch' absent.
    # 'och': ch ends token -> $END. 'chch': overlap counts twice (c then $END).
    recs = [
        ("f75r", "P", "chedy"),
        ("f75r", "P", "qoshey"),
        ("f75r", "P", "och"),
        ("f75r", "P", "chch"),
    ]
    b = build(recs)
    nxt = b["next"]
    assert nxt["ch"]["e"] == 1  # from chedy
    assert nxt["ch"]["$END"] == 2  # 'och' end + second ch of 'chch' end
    assert nxt["ch"]["c"] == 1  # first ch of 'chch' followed by c
    assert nxt["sh"]["e"] == 1  # from qoshey
    assert nxt["sh"].get("$END", 0) == 0


def test_main_writes_four_csvs_with_guardrail(tmp_path):
    balneo = tmp_path / "balneo.csv"
    operator = tmp_path / "operator.csv"
    nxt = tmp_path / "next.csv"
    summary = tmp_path / "summary.csv"
    rc = main(
        [
            str(CORPUS),
            "--n-perm",
            "30",
            "--out-balneo",
            str(balneo),
            "--out-operator",
            str(operator),
            "--out-next",
            str(nxt),
            "--out-summary",
            str(summary),
        ]
    )
    assert rc == 0
    for p in (balneo, operator, nxt, summary):
        assert p.exists() and p.stat().st_size > 0
        assert GUARDRAIL in p.read_text(encoding="utf-8")
    # summary must carry V & p for A and B, both entropies, and the predictors
    text = summary.read_text(encoding="utf-8")
    for metric in (
        "A_cramerV_kind_balneo",
        "A_perm_p_kind_balneo",
        "B_cramerV_operator_nucleus",
        "B_cramerV_operator_within_B",
        "C_entropy_next_ch_bits",
        "C_entropy_next_sh_bits",
        "A_predictor",
        "B_orthogonal",
        "C_free_variants",
    ):
        assert metric in text
    # next-glyph CSV has both benches and probabilities in [0,1]
    with nxt.open(encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert {r["bench"] for r in rows} == {"ch", "sh"}
    assert all(0.0 <= float(r["prob"]) <= 1.0 for r in rows)
