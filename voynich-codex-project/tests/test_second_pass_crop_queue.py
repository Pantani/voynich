from scripts.prepare_second_pass_crop_queue import (
    build_second_pass_rows,
    missing_token_count,
    priority_bucket,
    second_pass_focus,
    summarize_queue,
)


def test_missing_token_count_splits_non_empty_tokens():
    assert missing_token_count("oteedar oteeeor") == 2
    assert missing_token_count("dol") == 1
    assert missing_token_count("") == 0


def test_priority_bucket_ranks_operator_missing_tokens_first():
    ot_row = {"prefix_family": "ot", "missing_group_tokens": "oteedar"}
    ch_row = {"prefix_family": "ch", "missing_group_tokens": "chedar"}
    standalone_row = {"prefix_family": "standalone", "missing_group_tokens": ""}

    assert priority_bucket(ot_row) == "P0_operator_missing_tokens"
    assert priority_bucket(ch_row) == "P1_core_missing_tokens"
    assert priority_bucket(standalone_row) == "P3_tighten_existing_region"


def test_second_pass_focus_distinguishes_missing_from_tightening():
    missing = {"missing_group_tokens": "dol"}
    complete = {"missing_group_tokens": ""}

    assert second_pass_focus(missing) == "locate_missing_group_tokens"
    assert second_pass_focus(complete) == "tighten_existing_matched_tokens"


def test_build_second_pass_rows_filters_pending_without_coordinates_and_sorts():
    rows = [
        {
            "route10_id": "R10-009",
            "manual_review_id": "R9-009",
            "crop_id": "R7-002",
            "source_review_id": "R6-002",
            "folio": "f67r1",
            "locus": "f67r1.5,@Cc",
            "prefix_family": "standalone",
            "group_tokens": "ar ol",
            "missing_group_tokens": "",
            "consolidation_outcome": "pending_manual_review",
            "coordinate_status": "no_manual_coordinates",
            "evidence_status": "no_glyph_confirmation",
            "axis_test_eligibility": "not_eligible",
        },
        {
            "route10_id": "R10-002",
            "manual_review_id": "R9-002",
            "crop_id": "R7-010",
            "source_review_id": "R6-010",
            "folio": "f70v2",
            "locus": "f70v2.21,@Cc",
            "prefix_family": "ot",
            "group_tokens": "otar oteedar oteeeor",
            "missing_group_tokens": "oteedar oteeeor",
            "consolidation_outcome": "pending_manual_review",
            "coordinate_status": "no_manual_coordinates",
            "evidence_status": "no_glyph_confirmation",
            "axis_test_eligibility": "not_eligible",
        },
        {
            "route10_id": "R10-012",
            "manual_review_id": "R9-012",
            "crop_id": "R7-012",
            "source_review_id": "R6-012",
            "folio": "f70v2",
            "locus": "f70v2.33,@Cc",
            "prefix_family": "ot",
            "group_tokens": "otar otor",
            "missing_group_tokens": "",
            "consolidation_outcome": "confirmed_tighter_region",
            "coordinate_status": "manual_coordinates_complete",
            "evidence_status": "tighter_region_confirmed",
            "axis_test_eligibility": "eligible_after_manual_review",
        },
    ]

    queue = build_second_pass_rows(rows)

    assert [row["route10_id"] for row in queue] == ["R10-002", "R10-009"]
    assert queue[0]["route11_id"] == "R11-001"
    assert queue[0]["missing_token_count"] == "2"
    assert queue[0]["second_pass_focus"] == "locate_missing_group_tokens"
    assert queue[0]["semantic_guardrail"] == "no_axis_meaning_from_queue_position"


def test_summarize_queue_counts_priority_and_focus():
    rows = [
        {
            "priority_bucket": "P0_operator_missing_tokens",
            "second_pass_focus": "locate_missing_group_tokens",
            "crop_strategy": "search_single_missing_token_then_redraw_crop",
            "prefix_family": "ot",
        },
        {
            "priority_bucket": "P3_tighten_existing_region",
            "second_pass_focus": "tighten_existing_matched_tokens",
            "crop_strategy": "tighten_current_svg_region",
            "prefix_family": "standalone",
        },
    ]

    summary = summarize_queue(rows)

    assert summary["priority_bucket"]["P0_operator_missing_tokens"] == 1
    assert summary["second_pass_focus"]["tighten_existing_matched_tokens"] == 1
    assert summary["prefix_family"]["standalone"] == 1
