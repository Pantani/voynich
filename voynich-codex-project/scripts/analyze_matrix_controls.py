#!/usr/bin/env python3
"""Run statistical controls for the ar/al/or/ol matrix table.

Input is the contextual CSV produced by build_matrix_context_table.py. The
controls are deliberately dependency-free and conservative: they do not decode
anything, they only test whether suffix distributions stay structured across
locus, prefix, and line-position dimensions.
"""
from __future__ import annotations

import argparse
import csv
import random
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]
SUFFIXES = ("ar", "al", "or", "ol")
EXACT_FAMILIES = {
    "ok": ("okar", "okal", "okor", "okol"),
    "ot": ("otar", "otal", "otor", "otol"),
    "qok": ("qokar", "qokal", "qokor", "qokol"),
    "ch": ("chor", "chol"),
    "sh": ("shor", "shol"),
    "d": ("dar", "dal"),
    "od": ("odar", "odal"),
}


@dataclass(frozen=True)
class ChiSquareResult:
    statistic: float
    degrees_of_freedom: int
    cramers_v: float


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def contingency(
    rows: Iterable[dict[str, str]], row_key: str, col_key: str = "suffix"
) -> dict[str, Counter[str]]:
    table: dict[str, Counter[str]] = defaultdict(Counter)
    for row in rows:
        table[row[row_key] or "(none)"][row[col_key]] += 1
    return dict(table)


def totals(table: dict[str, Counter[str]]) -> tuple[Counter[str], Counter[str], int]:
    row_totals = Counter()
    col_totals = Counter()
    grand_total = 0
    for row_name, counts in table.items():
        row_total = sum(counts.values())
        row_totals[row_name] = row_total
        grand_total += row_total
        for col_name, value in counts.items():
            col_totals[col_name] += value
    return row_totals, col_totals, grand_total


def chi_square_independence(table: dict[str, Counter[str]]) -> ChiSquareResult:
    row_totals, col_totals, grand_total = totals(table)
    if grand_total == 0:
        return ChiSquareResult(0.0, 0, 0.0)
    rows = list(row_totals)
    cols = list(col_totals)
    statistic = 0.0
    for row_name in rows:
        for col_name in cols:
            expected = row_totals[row_name] * col_totals[col_name] / grand_total
            if expected:
                observed = table[row_name][col_name]
                statistic += (observed - expected) ** 2 / expected
    degrees = max(0, (len(rows) - 1) * (len(cols) - 1))
    min_dimension = min(len(rows) - 1, len(cols) - 1)
    cramers_v = (statistic / (grand_total * min_dimension)) ** 0.5 if min_dimension else 0.0
    return ChiSquareResult(statistic, degrees, cramers_v)


def shuffled_p_value(
    rows: list[dict[str, str]],
    row_key: str,
    actual_statistic: float,
    iterations: int,
    seed: int,
) -> float:
    if iterations <= 0:
        return 0.0
    rng = random.Random(seed)
    labels = [row["suffix"] for row in rows]
    row_values = [row[row_key] or "(none)" for row in rows]
    exceedances = 0
    for _ in range(iterations):
        shuffled = labels[:]
        rng.shuffle(shuffled)
        table: dict[str, Counter[str]] = defaultdict(Counter)
        for row_value, suffix in zip(row_values, shuffled):
            table[row_value][suffix] += 1
        if chi_square_independence(dict(table)).statistic >= actual_statistic:
            exceedances += 1
    return (exceedances + 1) / (iterations + 1)


def expected_suffix_by_locus_given_prefix(rows: list[dict[str, str]]) -> dict[str, Counter[str]]:
    """Expected suffix counts by locus if locus and suffix are independent within each prefix."""
    prefix_locus: dict[str, Counter[str]] = defaultdict(Counter)
    prefix_suffix: dict[str, Counter[str]] = defaultdict(Counter)
    prefix_total = Counter()
    expected: dict[str, Counter[str]] = defaultdict(Counter)

    for row in rows:
        prefix = row["prefix"] or "(none)"
        locus = row["locus_kind"] or "(none)"
        suffix = row["suffix"]
        prefix_locus[prefix][locus] += 1
        prefix_suffix[prefix][suffix] += 1
        prefix_total[prefix] += 1

    for prefix, total in prefix_total.items():
        if not total:
            continue
        for locus, locus_count in prefix_locus[prefix].items():
            for suffix, suffix_count in prefix_suffix[prefix].items():
                expected[locus][suffix] += locus_count * suffix_count / total
    return expected


def chi_square_against_expected(
    observed: dict[str, Counter[str]], expected: dict[str, Counter[str]]
) -> ChiSquareResult:
    row_names = sorted(set(observed) | set(expected))
    col_names = sorted({col for table in (observed, expected) for counts in table.values() for col in counts})
    grand_total = sum(sum(counts.values()) for counts in observed.values())
    statistic = 0.0
    for row_name in row_names:
        for col_name in col_names:
            exp = expected[row_name][col_name]
            if exp:
                obs = observed[row_name][col_name]
                statistic += (obs - exp) ** 2 / exp
    degrees = max(0, (len(row_names) - 1) * (len(col_names) - 1))
    min_dimension = min(len(row_names) - 1, len(col_names) - 1)
    cramers_v = (statistic / (grand_total * min_dimension)) ** 0.5 if grand_total and min_dimension else 0.0
    return ChiSquareResult(statistic, degrees, cramers_v)


def exact_family_counts(rows: Iterable[dict[str, str]]) -> list[dict[str, str]]:
    token_counts = Counter(row["token"] for row in rows if row["target_status"] == "exact")
    output: list[dict[str, str]] = []
    for family, tokens in EXACT_FAMILIES.items():
        total = sum(token_counts[token] for token in tokens)
        row: dict[str, str] = {"family": family, "total": str(total)}
        for token in tokens:
            row[token] = str(token_counts[token])
        output.append(row)
    return output


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def render_counter_table(title: str, counter: Counter[str]) -> list[str]:
    lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
    for key, value in counter.most_common():
        lines.append(f"|{key}|{value}|")
    lines.append("")
    return lines


def render_matrix(title: str, table: dict[str, Counter[str]]) -> list[str]:
    lines = [f"### {title}", "", "|item|ar|al|or|ol|total|", "|---|---:|---:|---:|---:|---:|"]
    for key in sorted(table):
        counts = table[key]
        total = sum(counts.values())
        lines.append(
            f"|{key}|{counts['ar']}|{counts['al']}|{counts['or']}|{counts['ol']}|{total}|"
        )
    lines.append("")
    return lines


def format_result(result: ChiSquareResult, p_value: float | None = None) -> str:
    base = f"chi2={result.statistic:.3f}, df={result.degrees_of_freedom}, cramers_v={result.cramers_v:.4f}"
    if p_value is not None:
        base += f", shuffle_p<={p_value:.4f}"
    return base


def write_markdown(
    path: Path,
    source_csv: Path,
    rows: list[dict[str, str]],
    key_results: list[dict[str, str]],
    exact_rows: list[dict[str, str]],
) -> None:
    suffix_counts = Counter(row["suffix"] for row in rows)
    locus_table = contingency(rows, "locus_kind")
    prefix_table = contingency(rows, "prefix")
    position_table = contingency(rows, "line_position")

    lines: list[str] = [
        "# Rota 2: controles estatisticos da matriz",
        "",
        "Este relatorio testa se a distribuicao de `ar/al/or/ol` permanece estruturada quando observada por locus, prefixo e posicao de linha. Ele nao atribui significado aos eixos; apenas mede se o padrao parece aleatorio sob controles simples.",
        "",
        f"Fonte: `{source_csv}`.",
        "",
        f"Candidatos analisados: {len(rows)}.",
        "",
        "## Resultados-chave",
        "",
        "|controle|resultado|interpretacao|",
        "|---|---|---|",
    ]
    for result in key_results:
        lines.append(f"|{result['control']}|{result['result']}|{result['interpretation']}|")
    lines.append("")
    lines.extend(render_counter_table("Sufixos", suffix_counts))
    lines.extend(render_matrix("Locus x sufixo", locus_table))
    lines.extend(render_matrix("Prefixo x sufixo", prefix_table))
    lines.extend(render_matrix("Posicao x sufixo", position_table))
    lines.extend(
        [
            "### Pares exatos",
            "",
            "|familia|total|formas|",
            "|---|---:|---|",
        ]
    )
    for row in exact_rows:
        forms = ", ".join(f"{k}={v}" for k, v in row.items() if k not in {"family", "total"})
        lines.append(f"|{row['family']}|{row['total']}|{forms}|")
    lines.extend(
        [
            "",
            "## Leitura provisoria",
            "",
            "- A associacao entre locus e sufixo precisa sobreviver ao controle por prefixo para interessar como camada funcional.",
            "- Se o controle por prefixo ainda mostrar desvio, a matriz nao e explicada apenas por familias como `ch`, `sh`, `ok`, `ot` e `qok`.",
            "- O proximo passo e escolher alguns folios/loci onde o desvio e forte e passar para anotacao visual manual.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_csv", help="Context CSV from build_matrix_context_table.py")
    parser.add_argument(
        "--out-dir",
        default=str(ROOT / "data" / "derived"),
        help="Directory for CSV control outputs",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "rota_2_controles_estatisticos.md"),
        help="Markdown report output path",
    )
    parser.add_argument("--iterations", type=int, default=500, help="Shuffle iterations")
    parser.add_argument("--seed", type=int, default=408, help="Deterministic shuffle seed")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    input_csv = Path(args.input_csv)
    out_dir = Path(args.out_dir)
    rows = read_rows(input_csv)

    controls = [
        ("locus_vs_suffix", "locus_kind", "Testa se P/L/C/R tem distribuicoes diferentes de ar/al/or/ol."),
        ("prefix_vs_suffix", "prefix", "Testa se familias de prefixo preferem bordas diferentes."),
        ("line_position_vs_suffix", "line_position", "Testa se inicio/meio/fim de linha afeta a borda."),
    ]
    key_results: list[dict[str, str]] = []
    summary_rows: list[dict[str, str]] = []
    for name, row_key, interpretation in controls:
        table = contingency(rows, row_key)
        result = chi_square_independence(table)
        p_value = shuffled_p_value(rows, row_key, result.statistic, args.iterations, args.seed)
        rendered = format_result(result, p_value)
        key_results.append({"control": name, "result": rendered, "interpretation": interpretation})
        summary_rows.append(
            {
                "control": name,
                "chi_square": f"{result.statistic:.6f}",
                "degrees_of_freedom": str(result.degrees_of_freedom),
                "cramers_v": f"{result.cramers_v:.6f}",
                "shuffle_iterations": str(args.iterations),
                "shuffle_p_value_upper_bound": f"{p_value:.6f}",
            }
        )

    observed_locus = contingency(rows, "locus_kind")
    expected_locus = expected_suffix_by_locus_given_prefix(rows)
    prefix_controlled = chi_square_against_expected(observed_locus, expected_locus)
    key_results.append(
        {
            "control": "locus_vs_suffix_given_prefix",
            "result": format_result(prefix_controlled),
            "interpretation": "Compara locus x sufixo depois de controlar a mistura de prefixos.",
        }
    )
    summary_rows.append(
        {
            "control": "locus_vs_suffix_given_prefix",
            "chi_square": f"{prefix_controlled.statistic:.6f}",
            "degrees_of_freedom": str(prefix_controlled.degrees_of_freedom),
            "cramers_v": f"{prefix_controlled.cramers_v:.6f}",
            "shuffle_iterations": "0",
            "shuffle_p_value_upper_bound": "",
        }
    )

    exact_rows = exact_family_counts(rows)
    write_csv(
        out_dir / "matrix_control_summary_zl3b.csv",
        summary_rows,
        [
            "control",
            "chi_square",
            "degrees_of_freedom",
            "cramers_v",
            "shuffle_iterations",
            "shuffle_p_value_upper_bound",
        ],
    )
    write_csv(
        out_dir / "matrix_exact_pairs_zl3b.csv",
        exact_rows,
        ["family", "total"] + sorted({token for tokens in EXACT_FAMILIES.values() for token in tokens}),
    )
    write_markdown(Path(args.md), input_csv, rows, key_results, exact_rows)
    print(f"rows={len(rows)} controls={len(summary_rows)}")
    print(f"summary={out_dir / 'matrix_control_summary_zl3b.csv'}")
    print(f"exact_pairs={out_dir / 'matrix_exact_pairs_zl3b.csv'}")
    print(f"md={args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
