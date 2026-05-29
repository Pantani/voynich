from scripts.prepare_visual_annotation_candidates import score_row, select_candidates


def test_visual_candidate_scoring_prioritizes_visual_exact_rows():
    row = {
        "folio": "f68r3",
        "locus": "f68r3.1,@C0",
        "locus_kind": "C",
        "visual_context": "circular text",
        "token": "qokol",
        "target_status": "exact",
        "prefix": "qok",
        "suffix": "ol",
        "line_position": "single",
        "previous_token": "",
        "next_token": "",
        "line_tokens": "qokol",
    }

    assert score_row(row, {"f68r3"}) >= 12


def test_select_candidates_adds_blank_annotation_fields():
    rows = [
        {
            "folio": "f68r3",
            "locus": "f68r3.1,@C0",
            "locus_kind": "C",
            "visual_context": "circular text",
            "token": "qokol",
            "target_status": "exact",
            "prefix": "qok",
            "suffix": "ol",
            "line_position": "single",
            "previous_token": "",
            "next_token": "",
            "line_tokens": "qokol",
        }
    ]

    selected = select_candidates(rows, {"f68r3"}, 10)

    assert len(selected) == 1
    assert selected[0]["image_checked"] == ""
    assert selected[0]["object_nearby"] == ""
