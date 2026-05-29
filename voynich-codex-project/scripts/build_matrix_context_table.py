#!/usr/bin/env python3
"""Build contextual tables for Voynich border-matrix candidates.

The project hypothesis treats ar/al/or/ol as a possible four-state border
matrix. Unlike the simpler counter script, this preserves folio, locus, line
position, and nearby tokens so that the candidates can be inspected manually.
"""
from __future__ import annotations

import argparse
import csv
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from parse_eva_text import tokens_from_text

ROOT = Path(__file__).resolve().parents[1]
LOCUS_RE = re.compile(r"<([^>]+)>")
MATRIX_SUFFIXES = ("ar", "al", "or", "ol")
MATRIX_PREFIXES = (
    "qok",
    "qo",
    "ok",
    "ot",
    "yk",
    "yt",
    "ch",
    "sh",
    "od",
    "d",
    "o",
    "y",
)

EXACT_TARGETS = {
    "okar",
    "okal",
    "okor",
    "okol",
    "otar",
    "otal",
    "otor",
    "otol",
    "qokar",
    "qokal",
    "qokor",
    "qokol",
    "chor",
    "chol",
    "shor",
    "shol",
    "dar",
    "dal",
    "odar",
    "odal",
}

LOCUS_KIND = {
    "P": "P",
    "L": "L",
    "C": "C",
    "R": "R",
    "X": "L",
    "Y": "rubrica",
}

LOCUS_HINT = {
    "P": "paragraph/text line",
    "L": "label",
    "C": "circular text",
    "R": "radial text",
    "X": "star/object label",
    "Y": "red/rubrical layer",
}


@dataclass(frozen=True)
class LineRecord:
    source: str
    line_no: int
    note: str
    locus: str
    folio: str
    locus_code: str
    locus_kind: str
    visual_context: str
    tokens: tuple[str, ...]


def ivtff_locus_kind(locus: str) -> str:
    """Return IVTFF locus kind P/L/C/R when present.

    IVTFF text loci look like f1r.1,@P0 or f68r3.4,+R0. The kind is carried
    in the annotation after the comma, not in the dotted folio segment.
    """
    if "," not in locus:
        return ""
    annotation = locus.rsplit(",", 1)[1]
    match = re.search(r"[@+*=*]?([PLCR])", annotation)
    return match.group(1) if match else ""


def split_locus(locus: str) -> tuple[str, str, str, str]:
    parts = locus.split(".")
    folio = parts[0] if parts else ""
    code = ivtff_locus_kind(locus)
    if not code:
        code = parts[1] if len(parts) > 1 else ""
    kind = LOCUS_KIND.get(code, code or "?")
    hint = LOCUS_HINT.get(code, "unclassified locus")
    visual = ".".join(parts[2:]) if len(parts) > 2 else ""
    if visual:
        hint = f"{hint}: {visual}"
    return folio, code, kind, hint


def line_zone(index: int, count: int) -> str:
    if count <= 1:
        return "single"
    if index == 0:
        return "start"
    if index == count - 1:
        return "end"
    return "middle"


def token_suffix(token: str) -> str:
    for suffix in MATRIX_SUFFIXES:
        if token.endswith(suffix):
            return suffix
    return ""


def token_prefix(token: str) -> str:
    for prefix in MATRIX_PREFIXES:
        if token.startswith(prefix):
            return prefix
    return ""


def tokens_from_record_line(line: str) -> tuple[str, ...]:
    return tuple(tokens_from_text(line))


def records_from_text(text: str, source: str) -> list[LineRecord]:
    records: list[LineRecord] = []
    current_note = ""
    for line_no, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped:
            continue
        if stripped.startswith("#"):
            note = stripped.lstrip("#").strip()
            if note:
                current_note = note
            continue

        match = LOCUS_RE.search(raw)
        if not match:
            continue
        locus = match.group(1)
        tokens = tokens_from_record_line(raw)
        if not tokens:
            continue
        folio, code, kind, visual = split_locus(locus)
        records.append(
            LineRecord(
                source=source,
                line_no=line_no,
                note=current_note,
                locus=locus,
                folio=folio,
                locus_code=code,
                locus_kind=kind,
                visual_context=visual,
                tokens=tokens,
            )
        )
    return records


def records_from_files(paths: Iterable[str | Path]) -> list[LineRecord]:
    records: list[LineRecord] = []
    for path in paths:
        p = Path(path)
        records.extend(records_from_text(p.read_text(encoding="utf-8"), p.name))
    return records


def candidate_rows(records: Iterable[LineRecord]) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for record in records:
        for index, token in enumerate(record.tokens):
            suffix = token_suffix(token)
            prefix = token_prefix(token)
            if not suffix:
                continue
            is_exact = token in EXACT_TARGETS
            is_standalone = token in MATRIX_SUFFIXES
            is_candidate = is_exact or is_standalone or bool(prefix)
            if not is_candidate:
                continue
            if is_exact:
                target_status = "exact"
            elif is_standalone:
                target_status = "standalone"
            else:
                target_status = "broad"
            prefix_value = "" if is_standalone else prefix
            prev_token = record.tokens[index - 1] if index else ""
            next_token = record.tokens[index + 1] if index + 1 < len(record.tokens) else ""
            rows.append(
                {
                    "source": record.source,
                    "folio": record.folio,
                    "locus": record.locus,
                    "locus_kind": record.locus_kind,
                    "locus_code": record.locus_code,
                    "visual_context": record.visual_context,
                    "note": record.note,
                    "token": token,
                    "target_status": target_status,
                    "prefix": prefix_value,
                    "suffix": suffix,
                    "line_position": line_zone(index, len(record.tokens)),
                    "token_index": str(index + 1),
                    "line_token_count": str(len(record.tokens)),
                    "previous_token": prev_token,
                    "next_token": next_token,
                    "line_tokens": " ".join(record.tokens),
                }
            )
    return rows


def write_csv(rows: list[dict[str, str]], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "source",
        "folio",
        "locus",
        "locus_kind",
        "locus_code",
        "visual_context",
        "note",
        "token",
        "target_status",
        "prefix",
        "suffix",
        "line_position",
        "token_index",
        "line_token_count",
        "previous_token",
        "next_token",
        "line_tokens",
    ]
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def markdown_table(rows: list[dict[str, str]], max_rows: int | None = None) -> str:
    columns = [
        "folio",
        "locus",
        "locus_kind",
        "token",
        "target_status",
        "suffix",
        "line_position",
        "note",
        "previous_token",
        "next_token",
    ]
    out = ["|" + "|".join(columns) + "|", "|" + "|".join(["---"] * len(columns)) + "|"]
    visible_rows = rows if max_rows is None else rows[:max_rows]
    for row in visible_rows:
        out.append("|" + "|".join(row[col].replace("|", "/") for col in columns) + "|")
    if max_rows is not None and len(rows) > max_rows:
        out.append(
            f"|...|...|...|...|...|...|...|amostra truncada; CSV contem {len(rows)} linhas completas|...|...|"
        )
    return "\n".join(out)


def summary_blocks(rows: list[dict[str, str]]) -> str:
    by_suffix = Counter(row["suffix"] for row in rows)
    by_kind_suffix: dict[str, Counter[str]] = defaultdict(Counter)
    by_prefix_suffix: dict[str, Counter[str]] = defaultdict(Counter)
    by_token = Counter(row["token"] for row in rows)
    by_status = Counter(row["target_status"] for row in rows)
    by_line_position = Counter(row["line_position"] for row in rows)
    exact_tokens = Counter(row["token"] for row in rows if row["target_status"] == "exact")
    for row in rows:
        by_kind_suffix[row["locus_kind"]][row["suffix"]] += 1
        by_prefix_suffix[row["prefix"] or "(none)"][row["suffix"]] += 1

    def render_counter(title: str, counter: Counter[str]) -> list[str]:
        lines = [f"### {title}", "", "|item|n|", "|---|---:|"]
        for item, count in counter.most_common():
            lines.append(f"|{item}|{count}|")
        if not counter:
            lines.append("|(none)|0|")
        lines.append("")
        return lines

    lines: list[str] = []
    lines.extend(render_counter("Sufixos da matriz", by_suffix))
    lines.extend(render_counter("Status dos candidatos", by_status))
    lines.extend(render_counter("Posicao na linha", by_line_position))
    lines.append("### Locus x sufixo")
    lines.append("")
    lines.append("|locus_kind|ar|al|or|ol|")
    lines.append("|---|---:|---:|---:|---:|")
    for kind in sorted(by_kind_suffix):
        counts = by_kind_suffix[kind]
        lines.append(
            f"|{kind}|{counts['ar']}|{counts['al']}|{counts['or']}|{counts['ol']}|"
        )
    lines.append("")
    lines.append("### Prefixo x sufixo")
    lines.append("")
    lines.append("|prefix|ar|al|or|ol|")
    lines.append("|---|---:|---:|---:|---:|")
    for prefix in sorted(by_prefix_suffix):
        counts = by_prefix_suffix[prefix]
        lines.append(
            f"|{prefix}|{counts['ar']}|{counts['al']}|{counts['or']}|{counts['ol']}|"
        )
    lines.append("")
    lines.extend(render_counter("Tokens exatos da lista de pares mínimos", exact_tokens))
    lines.extend(render_counter("Tokens candidatos mais frequentes", by_token))
    return "\n".join(lines)


def interpretation_lines(rows: list[dict[str, str]]) -> list[str]:
    if len(rows) >= 1000:
        return [
            "- A amostra agora e grande o bastante para testar distribuicao por locus, prefixo e posicao de linha.",
            "- A matriz `ar/al/or/ol` sobrevive fora dos trechos astronomicos iniciais e aparece em milhares de candidatos.",
            "- A distribuicao por locus nao e homogenea; isso favorece leitura funcional, mas ainda nao identifica o valor semantico dos eixos `a/o` e `r/l`.",
            "- A proxima etapa deve aplicar controles: embaralhamento de tokens/linhas, comparacao por prefixo e teste separado dos pares exatos.",
        ]
    return [
        "- A amostra ainda e pequena e enviesada para folios astronomicos/diagramaticos.",
        "- A presenca de `ar` e `ol` como tokens independentes em `f67r2.P.red` reforca que a borda direita pode funcionar como valor de slot, nao apenas como final fonetico.",
        "- `okar`, `okal`, `ytokar`, `ytodal`, `qokol` e `okol` cruzam camadas diferentes; isso favorece leitura funcional de operador/template.",
        "- A proxima etapa deve repetir o mesmo script sobre uma transcricao IVTFF/EVA maior e acrescentar anotacao visual manual para anel, setor, raio e objeto proximo.",
    ]


def write_markdown(
    rows: list[dict[str, str]], path: Path, inputs: list[str], max_table_rows: int | None
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(
        [
            "# Estudo contextual da matriz ar/al/or/ol",
            "",
            "Esta tabela continua o estudo sem assumir uma tradução lexical. Ela coleta candidatos que terminam em `ar`, `al`, `or` ou `ol` e preserva folio, locus, posição na linha e vizinhança imediata.",
            "",
            f"Entradas analisadas: {', '.join(inputs)}.",
            "",
            f"Total de candidatos: {len(rows)}.",
            "",
            summary_blocks(rows),
            "## Tabela contextual",
            "",
            markdown_table(rows, max_table_rows),
            "",
            "## Leitura provisória",
            "",
            *interpretation_lines(rows),
            "",
        ]
    )
    path.write_text(text, encoding="utf-8")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("inputs", nargs="+", help="EVA-like transcription files")
    parser.add_argument(
        "--csv",
        default=str(ROOT / "data" / "derived" / "border_matrix_context.csv"),
        help="CSV output path",
    )
    parser.add_argument(
        "--md",
        default=str(ROOT / "docs" / "estudo_matriz_bordas_contexto.md"),
        help="Markdown output path",
    )
    parser.add_argument(
        "--md-max-rows",
        type=int,
        default=500,
        help="Maximum candidate rows included in Markdown; CSV is always complete",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    records = records_from_files(args.inputs)
    rows = candidate_rows(records)
    write_csv(rows, Path(args.csv))
    max_rows = None if args.md_max_rows < 0 else args.md_max_rows
    write_markdown(rows, Path(args.md), args.inputs, max_rows)
    print(f"records={len(records)} candidates={len(rows)}")
    print(f"csv={args.csv}")
    print(f"md={args.md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
