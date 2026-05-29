from scripts.prepare_glyph_review_queue import (
    build_review_queue,
    exact_glyph_status,
    matching_annotations,
    missing_tokens,
)


def test_exact_glyph_status_detects_not_isolated_notes():
    annotations = [
        {"visual_notes": "exact glyph position not isolated", "annotation_confidence": "medium"},
        {"visual_notes": "same layer visible", "annotation_confidence": "medium"},
    ]

    assert exact_glyph_status(annotations) == "needs_exact_glyph_isolation"


def test_matching_annotations_and_missing_tokens_are_token_specific():
    pair = {"folio": "f67r1", "locus": "f67r1.6,+Cc", "tokens": "dal dar dol"}
    annotations = [
        {"folio": "f67r1", "locus": "f67r1.6,+Cc", "token": "dal"},
        {"folio": "f67r1", "locus": "f67r1.6,+Cc", "token": "dar"},
        {"folio": "f67r1", "locus": "f67r1.5,@Cc", "token": "dol"},
    ]

    matched = matching_annotations(pair, annotations)

    assert [row["token"] for row in matched] == ["dal", "dar"]
    assert missing_tokens(pair, matched) == ["dol"]


def test_build_review_queue_filters_to_directly_annotated_groups():
    pairs = [
        {
            "priority_score": "59",
            "folio": "f67r1",
            "locus": "f67r1.6,+Cc",
            "locus_kind": "C",
            "prefix_family": "d",
            "suffixes_present": "al ar ol",
            "axis_coverage": "ao+rl",
            "tokens": "dal dar dol",
            "annotated_tokens": "2",
            "visual_zones": "circular text",
            "object_nearby": "central face",
            "annotation_confidence": "medium",
        },
        {
            "priority_score": "79",
            "folio": "fRos",
            "locus": "fRos.20,@Cc",
            "locus_kind": "C",
            "prefix_family": "standalone",
            "suffixes_present": "al ar ol or",
            "axis_coverage": "ao+rl",
            "tokens": "al ar ol or",
            "annotated_tokens": "0",
            "visual_zones": "",
            "object_nearby": "",
            "annotation_confidence": "",
        },
    ]
    annotations = [
        {
            "folio": "f67r1",
            "locus": "f67r1.6,+Cc",
            "token": "dal",
            "image_file_or_url": "images/raw/commons_f67r1_r2.jpg",
            "visual_zone": "circular text",
            "object_nearby": "central face",
            "visual_notes": "exact glyph position not isolated",
            "annotation_confidence": "medium",
        }
    ]

    queue = build_review_queue(pairs, annotations)

    assert len(queue) == 1
    assert queue[0]["review_id"] == "R6-001"
    assert queue[0]["matched_annotation_tokens"] == "dal"
    assert queue[0]["missing_group_tokens"] == "dar dol"
    assert queue[0]["exact_glyph_status"] == "needs_exact_glyph_isolation"
    assert queue[0]["image_files"] == "images/raw/commons_f67r1_r2.jpg"
