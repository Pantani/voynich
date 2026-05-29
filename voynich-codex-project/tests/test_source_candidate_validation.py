from scripts.validate_missing_source_candidates import (
    apply_validated_sources_to_manifest,
    build_source_validation_rows,
    parse_args,
    summarize_source_validation_rows,
)


def source_row(route29_id="R29-001", folio="f113v", commons_page="", image_url=""):
    return {
        "route29_id": route29_id,
        "route28_id": route29_id.replace("R29", "R28"),
        "route27_id": route29_id.replace("R29", "R27"),
        "folio": folio,
        "locus_kind": "P",
        "priority_level": "P1",
        "gap_rows": "12",
        "unique_loci": "9",
        "token_counts": "otar=6|okar=4",
        "search_query": f"Voynich Manuscript {folio}",
        "candidate_commons_page": commons_page,
        "candidate_image_url": image_url,
        "source_notes": "",
        "semantic_guardrail": "missing_source_queue_not_visual_evidence",
    }


def test_build_source_validation_rows_keeps_blank_candidates_pending():
    rows = build_source_validation_rows([source_row()])

    assert rows[0]["route30_id"] == "R30-001"
    assert rows[0]["route29_id"] == "R29-001"
    assert rows[0]["source_validation_status"] == "pending_blank_source_candidate"
    assert rows[0]["apply_status"] == "skipped_blank_source_candidate"
    assert rows[0]["candidate_source_valid"] == "no"
    assert rows[0]["validation_reason"] == "candidate_fields_blank"
    assert rows[0]["semantic_guardrail"] == "source_validation_not_visual_evidence"


def test_build_source_validation_rows_accepts_structurally_valid_commons_source():
    rows = build_source_validation_rows(
        [
            source_row(
                commons_page="https://commons.wikimedia.org/wiki/File:Voynich_Manuscript_(200).jpg",
                image_url="https://upload.wikimedia.org/wikipedia/commons/a/aa/Voynich_Manuscript_%28200%29.jpg",
            )
        ]
    )

    assert rows[0]["source_validation_status"] == "valid_candidate_source"
    assert rows[0]["apply_status"] == "manifest_row_appended"
    assert rows[0]["candidate_source_valid"] == "yes"


def test_build_source_validation_rows_rejects_non_commons_or_non_upload_urls():
    rows = build_source_validation_rows(
        [
            source_row(
                commons_page="https://example.test/File:Voynich_Manuscript.jpg",
                image_url="https://example.test/image.jpg",
            )
        ]
    )

    assert rows[0]["source_validation_status"] == "invalid_candidate_source"
    assert rows[0]["apply_status"] == "skipped_invalid_source_candidate"
    assert rows[0]["candidate_source_valid"] == "no"


def test_apply_validated_sources_to_manifest_appends_only_valid_new_folios():
    manifest_rows = [
        {
            "folio": "f1r",
            "theme": "text/opening herbal",
            "commons_page": "https://commons.wikimedia.org/wiki/File:Voynich_Manuscript_(3).jpg",
            "image_url": "https://upload.wikimedia.org/wikipedia/commons/3/37/Voynich_Manuscript_%283%29.jpg",
            "why_included": "already present",
            "license_note": "Commons",
        }
    ]
    validation_rows = build_source_validation_rows(
        [
            source_row(
                folio="f113v",
                commons_page="https://commons.wikimedia.org/wiki/File:Voynich_Manuscript_(200).jpg",
                image_url="https://upload.wikimedia.org/wikipedia/commons/a/aa/Voynich_Manuscript_%28200%29.jpg",
            ),
            source_row(route29_id="R29-002", folio="f114r"),
        ]
    )

    updated = apply_validated_sources_to_manifest(manifest_rows, validation_rows)

    assert len(updated) == 2
    assert updated[1]["folio"] == "f113v"
    assert updated[1]["theme"] == "route30 verified source"
    assert "R30-001" in updated[1]["why_included"]


def test_summarize_source_validation_rows_counts_statuses_and_apply_results():
    rows = build_source_validation_rows(
        [
            source_row(),
            source_row(
                route29_id="R29-002",
                folio="f113v",
                commons_page="https://commons.wikimedia.org/wiki/File:Voynich_Manuscript_(200).jpg",
                image_url="https://upload.wikimedia.org/wikipedia/commons/a/aa/Voynich_Manuscript_%28200%29.jpg",
            ),
        ]
    )

    summary = summarize_source_validation_rows(rows)

    assert summary["source_validation_status"]["pending_blank_source_candidate"] == 1
    assert summary["source_validation_status"]["valid_candidate_source"] == 1
    assert summary["apply_status"]["manifest_row_appended"] == 1
    assert summary["candidate_source_valid"]["yes"] == 1


def test_parse_args_keeps_input_manifest_separate_from_derived_manifest():
    args = parse_args(["sources.csv", "manifest.csv"])

    assert args.manifest_csv == "manifest.csv"
    assert "commons_image_sources_after_source_validation_zl3b.csv" in args.derived_manifest_csv
