from scripts.prepare_missing_source_image_queue import (
    build_missing_source_rows,
    render_html_card,
    summarize_missing_source_rows,
)


def package_row(route28_id, package_status, folio="f113v", locus_kind="P"):
    return {
        "route28_id": route28_id,
        "route27_id": route28_id.replace("R28", "R27"),
        "folio": folio,
        "locus_kind": locus_kind,
        "priority_level": "P1",
        "gap_rows": "12",
        "unique_loci": "9",
        "token_counts": "otar=6|okar=4",
        "top_loci": f"{folio}.1,+P0|{folio}.2,+P0",
        "section_notes": "star paragraph",
        "image_source_status": "not_in_manifest",
        "workstream": "source_image_required",
        "package_status": package_status,
        "semantic_guardrail": "visual_annotation_package_not_evidence",
    }


def test_build_missing_source_rows_filters_blocked_package_items_only():
    rows = build_missing_source_rows(
        [
            package_row("R28-001", "ready_for_manual_visual_annotation", folio="f99v"),
            package_row("R28-002", "blocked_pending_source_image", folio="f113v"),
        ]
    )

    assert len(rows) == 1
    assert rows[0]["route29_id"] == "R29-001"
    assert rows[0]["route28_id"] == "R28-002"
    assert rows[0]["folio"] == "f113v"
    assert rows[0]["source_resolution_status"] == "pending_public_source_verification"
    assert rows[0]["candidate_commons_page"] == ""
    assert rows[0]["candidate_image_url"] == ""
    assert rows[0]["manifest_action"] == "do_not_update_manifest_until_url_verified"
    assert rows[0]["semantic_guardrail"] == "missing_source_queue_not_visual_evidence"


def test_build_missing_source_rows_creates_non_evidentiary_search_links():
    rows = build_missing_source_rows([package_row("R28-002", "blocked_pending_source_image", folio="f113v")])

    assert rows[0]["search_query"] == "Voynich Manuscript f113v"
    assert "commons.wikimedia.org" in rows[0]["commons_search_url"]
    assert "f113v" in rows[0]["commons_search_url"]


def test_summarize_missing_source_rows_counts_status_priority_and_locus():
    rows = build_missing_source_rows(
        [
            package_row("R28-002", "blocked_pending_source_image", folio="f113v"),
            package_row("R28-003", "blocked_pending_source_image", folio="fRos", locus_kind="C"),
        ]
    )

    summary = summarize_missing_source_rows(rows)

    assert summary["source_resolution_status"]["pending_public_source_verification"] == 2
    assert summary["priority_level"]["P1"] == 2
    assert summary["locus_kind"]["C"] == 1
    assert summary["folio"]["fRos"] == 1


def test_render_html_card_keeps_candidate_fields_blank_until_verified():
    row = build_missing_source_rows([package_row("R28-002", "blocked_pending_source_image", folio="f113v")])[0]

    html = render_html_card(row)

    assert "Voynich Manuscript f113v" in html
    assert "candidate_image_url" in html
    assert "missing_source_queue_not_visual_evidence" in html
