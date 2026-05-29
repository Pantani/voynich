from scripts.build_exact_form_context_table import (
    EXACT_FORMS,
    build_exact_form_rows,
    summarize_exact_form_rows,
    visual_annotation_index,
)


def test_exact_forms_are_limited_to_ok_ot_matrix_forms():
    assert EXACT_FORMS == ("okar", "okal", "okor", "okol", "otar", "otal", "otor", "otol")


def test_visual_annotation_index_uses_folio_locus_token_key():
    visual_rows = [
        {
            "folio": "f67r1",
            "locus": "f67r1.6,+Cc",
            "token": "otar",
            "visual_zone": "circular text",
            "object_nearby": "central face",
        }
    ]

    index = visual_annotation_index(visual_rows)

    assert index[("f67r1", "f67r1.6,+Cc", "otar")]["visual_zone"] == "circular text"


def test_build_exact_form_rows_filters_only_exact_forms_and_preserves_text_context():
    context_rows = [
        {
            "source": "ZL3b-n.txt",
            "folio": "f67r1",
            "locus": "f67r1.6,+Cc",
            "locus_kind": "C",
            "locus_code": "C",
            "visual_context": "circular text",
            "note": "Cosmological section",
            "token": "otar",
            "target_status": "exact",
            "prefix": "ot",
            "suffix": "ar",
            "line_position": "start",
            "token_index": "1",
            "line_token_count": "3",
            "previous_token": "",
            "next_token": "chedy",
            "line_tokens": "otar chedy okal",
        },
        {
            "source": "ZL3b-n.txt",
            "folio": "f67r1",
            "locus": "f67r1.6,+Cc",
            "token": "qokar",
            "target_status": "exact",
            "prefix": "qok",
            "suffix": "ar",
        },
    ]
    visual_rows = [
        {
            "folio": "f67r1",
            "locus": "f67r1.6,+Cc",
            "token": "otar",
            "image_file_or_url": "images/raw/commons_f67r1_r2.jpg",
            "visual_zone": "circular text",
            "ring": "outer",
            "sector": "",
            "radius": "",
            "object_nearby": "central face",
            "annotation_confidence": "medium",
        }
    ]

    rows = build_exact_form_rows(context_rows, visual_rows)

    assert len(rows) == 1
    assert rows[0]["route26_id"] == "R26-0001"
    assert rows[0]["token"] == "otar"
    assert rows[0]["section_note"] == "Cosmological section"
    assert rows[0]["line_position"] == "start"
    assert rows[0]["visual_zone"] == "circular text"
    assert rows[0]["object_nearby"] == "central face"
    assert rows[0]["visual_match_status"] == "matched_visual_annotation"


def test_build_exact_form_rows_marks_missing_visual_annotation_without_inference():
    context_rows = [
        {
            "source": "ZL3b-n.txt",
            "folio": "f1r",
            "locus": "f1r.1,@P0",
            "locus_kind": "P",
            "locus_code": "P",
            "visual_context": "paragraph/text line",
            "note": "Text page",
            "token": "okal",
            "target_status": "exact",
            "prefix": "ok",
            "suffix": "al",
            "line_position": "middle",
            "token_index": "2",
            "line_token_count": "5",
            "previous_token": "qokedy",
            "next_token": "ar",
            "line_tokens": "qokedy okal ar",
        }
    ]

    rows = build_exact_form_rows(context_rows, [])

    assert rows[0]["visual_zone"] == ""
    assert rows[0]["object_nearby"] == ""
    assert rows[0]["visual_match_status"] == "no_visual_annotation"
    assert rows[0]["semantic_guardrail"] == "exact_form_context_not_decipherment"


def test_summarize_exact_form_rows_counts_core_dimensions():
    rows = [
        {
            "token": "otar",
            "prefix": "ot",
            "suffix": "ar",
            "folio": "f67r1",
            "locus_kind": "C",
            "line_position": "start",
            "visual_match_status": "matched_visual_annotation",
        },
        {
            "token": "okal",
            "prefix": "ok",
            "suffix": "al",
            "folio": "f1r",
            "locus_kind": "P",
            "line_position": "middle",
            "visual_match_status": "no_visual_annotation",
        },
    ]

    summary = summarize_exact_form_rows(rows)

    assert summary["token"]["otar"] == 1
    assert summary["prefix"]["ok"] == 1
    assert summary["suffix"]["al"] == 1
    assert summary["visual_match_status"]["no_visual_annotation"] == 1
