from scripts.analyze_matrix_axes import ao_axis, axis_table, rl_axis, summary_rows


def test_axis_mapping_matches_matrix_layout():
    assert ao_axis("ar") == "a"
    assert ao_axis("al") == "a"
    assert ao_axis("or") == "o"
    assert ao_axis("ol") == "o"

    assert rl_axis("ar") == "r"
    assert rl_axis("or") == "r"
    assert rl_axis("al") == "l"
    assert rl_axis("ol") == "l"


def test_axis_table_counts_selected_dimension():
    rows = [
        {"visual_zone": "label", "suffix": "ar"},
        {"visual_zone": "label", "suffix": "ol"},
        {"visual_zone": "circular text", "suffix": "al"},
    ]

    ao_table = axis_table(rows, "visual_zone", "ao")
    rl_table = axis_table(rows, "visual_zone", "rl")

    assert ao_table["label"]["a"] == 1
    assert ao_table["label"]["o"] == 1
    assert rl_table["label"]["r"] == 1
    assert rl_table["label"]["l"] == 1
    assert ao_table["circular text"]["a"] == 1


def test_summary_rows_emit_both_axes_with_statistics():
    rows = [
        {"locus_kind": "P", "suffix": "ar"},
        {"locus_kind": "P", "suffix": "al"},
        {"locus_kind": "C", "suffix": "or"},
        {"locus_kind": "C", "suffix": "ol"},
    ]

    output = summary_rows(rows, ["locus_kind"])

    assert {row["axis"] for row in output} == {"ao", "rl"}
    assert any(
        row["axis"] == "ao"
        and row["value"] == "P"
        and row["a"] == "2"
        and row["o"] == "0"
        for row in output
    )
    assert all("chi_square_for_dimension_axis" in row for row in output)
