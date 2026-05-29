from scripts.analyze_visual_annotations import matrix, summary_rows


def test_visual_annotation_matrix_counts_suffixes():
    rows = [
        {"visual_zone": "label", "suffix": "ar"},
        {"visual_zone": "label", "suffix": "ol"},
        {"visual_zone": "circular text", "suffix": "ar"},
    ]

    table = matrix(rows, "visual_zone")

    assert table["label"]["ar"] == 1
    assert table["label"]["ol"] == 1
    assert table["circular text"]["ar"] == 1


def test_visual_annotation_summary_rows_include_shares():
    table = {"label": {"ar": 3, "al": 1, "or": 0, "ol": 0}}

    rows = summary_rows(table, "visual_zone")

    assert rows == [
        {
            "dimension": "visual_zone",
            "value": "label",
            "total": "4",
            "ar": "3",
            "ar_share": "0.7500",
            "al": "1",
            "al_share": "0.2500",
            "or": "0",
            "or_share": "0.0000",
            "ol": "0",
            "ol_share": "0.0000",
        }
    ]
