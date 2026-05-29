from scripts.analyze_same_context_pairs import (
    axis_coverage,
    comparable_groups,
    prefix_family,
    visual_lookup,
)


def test_prefix_family_separates_standalone_values():
    assert prefix_family({"target_status": "standalone", "prefix": "", "token": "ar"}) == "standalone"
    assert prefix_family({"target_status": "exact", "prefix": "ok", "token": "okar"}) == "ok"
    assert prefix_family({"target_status": "broad", "prefix": "", "token": "xar"}) == "(blank)"


def test_axis_coverage_marks_which_axes_are_testable():
    assert axis_coverage({"ar", "al"}) == "rl"
    assert axis_coverage({"ar", "or"}) == "ao"
    assert axis_coverage({"ar", "ol"}) == "ao+rl"
    assert axis_coverage({"ar"}) == "none"


def test_comparable_groups_require_same_context_and_two_suffixes():
    rows = [
        {
            "folio": "f67r1",
            "locus": "f67r1.5,@Cc",
            "locus_kind": "C",
            "visual_context": "circular text",
            "token": "okar",
            "target_status": "exact",
            "prefix": "ok",
            "suffix": "ar",
            "line_position": "middle",
        },
        {
            "folio": "f67r1",
            "locus": "f67r1.5,@Cc",
            "locus_kind": "C",
            "visual_context": "circular text",
            "token": "okal",
            "target_status": "exact",
            "prefix": "ok",
            "suffix": "al",
            "line_position": "middle",
        },
        {
            "folio": "f67r1",
            "locus": "f67r1.5,@Cc",
            "locus_kind": "C",
            "visual_context": "circular text",
            "token": "otar",
            "target_status": "exact",
            "prefix": "ot",
            "suffix": "ar",
            "line_position": "middle",
        },
    ]
    annotations = visual_lookup(
        [
            {
                "folio": "f67r1",
                "locus": "f67r1.5,@Cc",
                "token": "okar",
                "visual_zone": "circular text",
                "object_nearby": "central face",
                "annotation_confidence": "medium",
            }
        ]
    )

    groups = comparable_groups(rows, annotations)

    assert len(groups) == 1
    assert groups[0]["folio"] == "f67r1"
    assert groups[0]["prefix_family"] == "ok"
    assert groups[0]["suffixes_present"] == "al ar"
    assert groups[0]["axis_coverage"] == "rl"
    assert groups[0]["ar"] == "1"
    assert groups[0]["al"] == "1"
    assert groups[0]["annotated_tokens"] == "1"
    assert groups[0]["visual_zones"] == "circular text"
