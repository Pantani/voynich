from scripts.prepare_ready_visual_annotation_highres_ai_assist import (
    GUARDRAIL,
    build_ai_assist_rows,
    summarize_ai_assist_rows,
)


def highres_row(route42_id="R42-005", route32_id="R32-005", folio="f84r"):
    return {
        "route42_id": route42_id,
        "route32_id": route32_id,
        "route28_id": "R28-023",
        "folio": folio,
        "priority_level": "P1",
        "locus_kind": "P",
        "token_counts": "okal=1|otar=1",
        "top_loci": f"{folio}.24,+P0|{folio}.29,+P0",
        "yale_image_id": "1006226",
        "manifest_label": "84r",
        "yale_iiif_jpg_url": "https://collections.library.yale.edu/iiif/2/1006226/full/full/0/default.jpg",
        "yale_catalog_url": "https://collections.library.yale.edu/catalog/2002046?child_oid=1006226",
        "yale_width": "2753",
        "yale_height": "3745",
        "local_image_path": "images/raw/yale_iiif_r32/f84r_1006226.jpg",
        "manual_annotation_status": "",
        "manual_visual_notes": "",
    }


def test_build_ai_assist_rows_preserves_manual_blanks_and_guardrail():
    rows = build_ai_assist_rows([highres_row()])

    assert rows[0]["route42a_id"] == "R42A-001"
    assert rows[0]["route42_id"] == "R42-005"
    assert rows[0]["route32_id"] == "R32-005"
    assert rows[0]["folio"] == "f84r"
    assert rows[0]["manual_annotation_status"] == ""
    assert rows[0]["manual_visual_notes"] == ""
    assert rows[0]["chain_status"] == "blocked_waiting_human_r32_entry"
    assert rows[0]["semantic_guardrail"] == GUARDRAIL


def test_build_ai_assist_rows_uses_folio_specific_visual_observations():
    rows = build_ai_assist_rows(
        [
            highres_row("R42-002", "R32-002", "f1r"),
            highres_row("R42-006", "R32-006", "f88v"),
            highres_row("R42-008", "R32-008", "f99r"),
        ]
    )

    assert rows[0]["image_quality_assist"] == "medium_faint"
    assert rows[0]["target_region_locatable_assist"] == "partial"
    assert rows[1]["target_region_locatable_assist"] == "partial_composite_page"
    assert rows[1]["suggested_manual_review_action"] == "crop_composite_foldout_recipe_rows"
    assert rows[2]["target_region_locatable_assist"] == "yes_region"
    assert rows[2]["exact_token_decision_assist"] == "not_determined_requires_human_zoom"


def test_summarize_ai_assist_rows_counts_quality_and_actions():
    rows = build_ai_assist_rows(
        [
            highres_row("R42-002", "R32-002", "f1r"),
            highres_row("R42-005", "R32-005", "f84r"),
            highres_row("R42-008", "R32-008", "f99r"),
        ]
    )

    summary = summarize_ai_assist_rows(rows)

    assert summary["image_quality_assist"]["high"] == 2
    assert summary["image_quality_assist"]["medium_faint"] == 1
    assert summary["target_region_locatable_assist"]["yes_region"] == 2
    assert summary["chain_status"]["blocked_waiting_human_r32_entry"] == 3
