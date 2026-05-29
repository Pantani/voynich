from pathlib import Path

from scripts.prepare_active_tool_dashboard import (
    ACTIVE_TOOL_PAGES,
    OBSOLETE_HTML_TOOLS,
    render_dashboard_html,
    remove_obsolete_html_tools,
)


def test_render_dashboard_lists_only_unique_active_tools():
    html = render_dashboard_html()

    assert "Ferramentas ativas" in html
    assert "use a R42K" in html
    assert "R42M - Captura fina" in html
    for page in ACTIVE_TOOL_PAGES:
        assert page.filename in html
        assert page.title in html

    for obsolete in OBSOLETE_HTML_TOOLS:
        assert obsolete not in html


def test_remove_obsolete_html_tools_is_idempotent(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    for page in ACTIVE_TOOL_PAGES:
        (docs_dir / page.filename).write_text("ativa", encoding="utf-8")
    for obsolete in OBSOLETE_HTML_TOOLS:
        (docs_dir / obsolete).write_text("antiga", encoding="utf-8")

    first = remove_obsolete_html_tools(docs_dir)
    second = remove_obsolete_html_tools(docs_dir)

    assert sorted(first.removed) == sorted(OBSOLETE_HTML_TOOLS)
    assert second.removed == []
    assert sorted(second.already_absent) == sorted(OBSOLETE_HTML_TOOLS)
    assert sorted(path.name for path in docs_dir.glob("*.html")) == sorted(
        page.filename for page in ACTIVE_TOOL_PAGES
    )


def test_workspace_docs_contains_only_active_html_tools():
    docs_dir = Path(__file__).resolve().parents[1] / "docs" / "tools"

    html_files = sorted(path.name for path in docs_dir.glob("*.html"))

    assert html_files == sorted(page.filename for page in ACTIVE_TOOL_PAGES)
