from scripts.prepare_folio_review_packets import (
    attach_manifest_fields,
    build_packet_items,
    build_packets,
    packet_goal,
    summarize_packets,
)


def test_attach_manifest_fields_adds_source_image_by_crop_id():
    queue_rows = [
        {
            "route11_id": "R11-001",
            "crop_id": "R7-010",
            "folio": "f70v2",
            "missing_token_count": "2",
            "priority_bucket": "P0_operator_missing_tokens",
            "second_pass_focus": "locate_missing_group_tokens",
            "crop_strategy": "rescan_source_image_before_new_crop",
        }
    ]
    manifest_rows = [
        {
            "crop_id": "R7-010",
            "source_image": "images/raw/commons_f70v2.jpg",
            "crop_svg": "images/derived/review_crops/R7-010_R6-010_f70v2.svg",
            "review_region": "x=138 y=106 w=1198 h=1298",
        }
    ]

    attached = attach_manifest_fields(queue_rows, manifest_rows)

    assert attached[0]["source_image"] == "images/raw/commons_f70v2.jpg"
    assert attached[0]["crop_svg"] == "images/derived/review_crops/R7-010_R6-010_f70v2.svg"


def test_packet_goal_prefers_source_image_rescan_when_needed():
    rows = [
        {"crop_strategy": "tighten_current_svg_region"},
        {"crop_strategy": "rescan_source_image_before_new_crop"},
    ]

    assert packet_goal(rows) == "review_source_image_first"


def test_build_packets_groups_by_folio_and_source_image():
    rows = [
        {
            "route11_id": "R11-001",
            "folio": "f70v2",
            "source_image": "images/raw/commons_f70v2.jpg",
            "priority_bucket": "P0_operator_missing_tokens",
            "second_pass_focus": "locate_missing_group_tokens",
            "crop_strategy": "rescan_source_image_before_new_crop",
            "missing_token_count": "2",
        },
        {
            "route11_id": "R11-007",
            "folio": "f70v2",
            "source_image": "images/raw/commons_f70v2.jpg",
            "priority_bucket": "P2_other_missing_tokens",
            "second_pass_focus": "locate_missing_group_tokens",
            "crop_strategy": "search_single_missing_token_then_redraw_crop",
            "missing_token_count": "1",
        },
        {
            "route11_id": "R11-011",
            "folio": "f84r",
            "source_image": "images/raw/commons_f84r.jpg",
            "priority_bucket": "P3_tighten_existing_region",
            "second_pass_focus": "tighten_existing_matched_tokens",
            "crop_strategy": "tighten_current_svg_region",
            "missing_token_count": "0",
        },
    ]

    packets = build_packets(rows)

    assert [packet["packet_id"] for packet in packets] == ["R12-001", "R12-002"]
    assert packets[0]["folio"] == "f70v2"
    assert packets[0]["item_count"] == "2"
    assert packets[0]["missing_token_count"] == "3"
    assert packets[0]["priority_buckets"] == "P0_operator_missing_tokens P2_other_missing_tokens"
    assert packets[0]["packet_goal"] == "review_source_image_first"
    assert packets[1]["folio"] == "f84r"


def test_build_packet_items_preserves_item_to_packet_traceability():
    packets = [
        {
            "packet_id": "R12-001",
            "folio": "f70v2",
            "source_image": "images/raw/commons_f70v2.jpg",
            "route11_ids": "R11-001 R11-007",
        }
    ]
    rows = [
        {"route11_id": "R11-001", "crop_id": "R7-010", "folio": "f70v2"},
        {"route11_id": "R11-007", "crop_id": "R7-008", "folio": "f70v2"},
    ]

    items = build_packet_items(packets, rows)

    assert [item["packet_id"] for item in items] == ["R12-001", "R12-001"]
    assert [item["route11_id"] for item in items] == ["R11-001", "R11-007"]


def test_summarize_packets_counts_goal_and_folios():
    packets = [
        {"packet_goal": "review_source_image_first", "folio": "f70v2"},
        {"packet_goal": "tighten_current_svg_regions", "folio": "f84r"},
    ]

    summary = summarize_packets(packets)

    assert summary["packet_goal"]["review_source_image_first"] == 1
    assert summary["folio"]["f84r"] == 1
