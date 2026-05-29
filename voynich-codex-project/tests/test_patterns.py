from scripts.parse_eva_text import tokens_from_text
from scripts.build_matrix_context_table import candidate_rows, records_from_text


def test_token_cleanup():
    text = "<f67r2.P.red> sshey.syshees.qeykeey # comment\n"
    assert tokens_from_text(text) == ["sshey", "syshees", "qeykeey"]


def test_matrix_context_rows_preserve_locus_and_position():
    text = "\n".join(
        [
            "# Red middle line",
            "<f67r2.P.red> oaiin okal ar ol",
            "<f68r3.C.inner> otchody chokchy okol",
        ]
    )

    rows = candidate_rows(records_from_text(text, "fixture.eva"))

    assert [row["token"] for row in rows] == ["okal", "ar", "ol", "okol"]
    assert rows[0]["folio"] == "f67r2"
    assert rows[0]["locus_kind"] == "P"
    assert rows[0]["line_position"] == "middle"
    assert rows[0]["note"] == "Red middle line"
    assert rows[1]["target_status"] == "standalone"
    assert rows[2]["line_position"] == "end"
    assert rows[3]["locus_kind"] == "C"


def test_matrix_context_rows_parse_ivtff_locus_kind():
    text = "<f1r.1,@P0> <%>fachys.ykal.ar.ataiin\n<f68r3.4,+R0> qokol.chey\n"

    rows = candidate_rows(records_from_text(text, "ivtff.txt"))

    assert rows[0]["folio"] == "f1r"
    assert rows[0]["locus_code"] == "P"
    assert rows[0]["locus_kind"] == "P"
    assert rows[2]["locus_code"] == "R"
    assert rows[2]["locus_kind"] == "R"
