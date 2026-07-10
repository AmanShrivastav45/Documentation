import subprocess

from ingest import (
    chunk_by_headings,
    get_git_commit_hash,
    ingest_docs,
    strip_frontmatter,
    strip_jsx,
)
from rag_pipeline import VectorStore


def test_strip_frontmatter_removes_leading_yaml_block():
    text = "---\ntitle: Test\n---\n# Heading\n\nBody text.\n"
    result = strip_frontmatter(text)
    assert "title: Test" not in result
    assert "# Heading" in result


def test_strip_jsx_removes_component_tags_and_exports():
    text = (
        "export const meta = { title: 'X' }\n"
        "import Callout from '../components/Callout.jsx'\n"
        "# Title\n\n<Callout type=\"warning\">Careful</Callout>\n\nRest of body.\n"
    )
    result = strip_jsx(text)
    assert "<Callout" not in result
    assert "export const meta" not in result
    assert "Rest of body." in result


def test_strip_jsx_preserves_text_content_inside_wrapping_components():
    text = (
        "# Title\n\n"
        "<Callout type=\"warning\">\n"
        "  **Breaking change:** the /search endpoint was renamed to /query.\n"
        "</Callout>\n\n"
        "Rest of body.\n"
    )
    result = strip_jsx(text)
    assert "<Callout" not in result
    assert "</Callout>" not in result
    assert "Breaking change" in result
    assert "renamed to /query" in result
    assert "Rest of body." in result


def test_strip_jsx_still_removes_self_closing_components_entirely():
    text = "# Title\n\n<LiveMetricPreview threshold={80} />\n\nRest of body.\n"
    result = strip_jsx(text)
    assert "LiveMetricPreview" not in result
    assert "Rest of body." in result


def test_chunk_by_headings_splits_on_each_heading():
    text = "# Title\n\nIntro text.\n\n## Section One\n\nBody one.\n\n## Section Two\n\nBody two.\n"
    chunks = chunk_by_headings(text)
    assert [c["heading"] for c in chunks] == ["Title", "Section One", "Section Two"]
    assert "Body one." in chunks[1]["content"]
    assert "Body two." in chunks[2]["content"]


def test_chunk_by_headings_keeps_preamble_without_heading():
    text = "Preamble before any heading.\n\n# Title\n\nBody.\n"
    chunks = chunk_by_headings(text)
    assert chunks[0]["heading"] is None
    assert "Preamble" in chunks[0]["content"]


def test_get_git_commit_hash_returns_current_head(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    (tmp_path / "file.txt").write_text("hello")
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)

    commit_hash = get_git_commit_hash(str(tmp_path))
    assert len(commit_hash) == 40


def test_ingest_docs_produces_records_with_metadata(tmp_path):
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "sample.mdx").write_text(
        "---\ntitle: Sample\n---\n# Sample\n\n## First\n\nContent A.\n", encoding="utf-8"
    )
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)

    store = VectorStore()
    records = ingest_docs(str(docs_dir), store, repo_path=str(tmp_path))

    assert len(records) == 2
    assert records[0]["file_path"] == "sample.mdx"
    assert len(records[0]["git_commit_hash"]) == 40
    assert records[0]["last_updated"]
    assert len(store.all()) == 2
