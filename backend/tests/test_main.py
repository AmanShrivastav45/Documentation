import json
import subprocess

from fastapi.testclient import TestClient

import main
from main import app, store

client = TestClient(app)


def _init_git_repo_with_docs(tmp_path):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "getting-started.mdx").write_text(
        "---\ntitle: Getting Started\n---\n"
        "export const meta = { title: 'Getting Started' }\n"
        "# Getting Started\n\nInstall the CLI first.\n\n"
        "## Installation\n\nRun `npm install` to get started.\n",
        encoding="utf-8",
    )
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)
    return docs_dir


def test_root_returns_ok_status():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_then_query_returns_answer_with_sources(tmp_path):
    docs_dir = _init_git_repo_with_docs(tmp_path)

    ingest_response = client.post("/ingest", json={"docs_path": str(docs_dir)})
    assert ingest_response.status_code == 200
    assert ingest_response.json()["chunks_ingested"] > 0

    query_response = client.post("/query", json={"question": "How do I install it?"})
    assert query_response.status_code == 200
    body = query_response.json()
    assert "install" in body["answer"].lower()
    assert len(body["sources"]) > 0
    source = body["sources"][0]
    assert source["file_path"] == "getting-started.mdx"
    assert len(source["git_commit_hash"]) == 40


def test_query_with_no_ingested_docs_returns_fallback_answer():
    store.clear()
    response = client.post("/query", json={"question": "anything?"})
    assert response.status_code == 200
    assert "couldn't find" in response.json()["answer"].lower()


def test_ingest_with_nonexistent_docs_path_returns_400(tmp_path):
    response = client.post("/ingest", json={"docs_path": str(tmp_path / "does-not-exist")})
    assert response.status_code == 400


def test_get_docs_structure_returns_docs_json_contents(tmp_path, monkeypatch):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "docs.json").write_text(
        json.dumps({"tree": [{"id": "x", "label": "X", "path": "x.mdx"}]}), encoding="utf-8"
    )
    monkeypatch.setattr(main, "DEFAULT_DOCS_PATH", str(docs_dir))

    response = client.get("/api/docs/structure")

    assert response.status_code == 200
    assert response.json() == {"tree": [{"id": "x", "label": "X", "path": "x.mdx"}]}


def test_get_doc_content_returns_raw_mdx_text(tmp_path, monkeypatch):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "sample.mdx").write_text("# Sample\n\nHello.\n", encoding="utf-8")
    monkeypatch.setattr(main, "DEFAULT_DOCS_PATH", str(docs_dir))

    response = client.get("/api/docs/content", params={"path": "sample.mdx"})

    assert response.status_code == 200
    assert response.text == "# Sample\n\nHello.\n"
    assert response.headers["content-type"].startswith("text/plain")


def test_get_doc_content_returns_404_for_missing_file(tmp_path, monkeypatch):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    monkeypatch.setattr(main, "DEFAULT_DOCS_PATH", str(docs_dir))

    response = client.get("/api/docs/content", params={"path": "missing.mdx"})

    assert response.status_code == 404


def test_get_doc_content_rejects_path_traversal(tmp_path, monkeypatch):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "safe.mdx").write_text("# Safe\n", encoding="utf-8")
    (tmp_path / "secret.txt").write_text("do not leak", encoding="utf-8")
    monkeypatch.setattr(main, "DEFAULT_DOCS_PATH", str(docs_dir))

    response = client.get("/api/docs/content", params={"path": "../secret.txt"})

    assert response.status_code == 400


def test_ingest_without_docs_path_uses_default(tmp_path, monkeypatch):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "sample.mdx").write_text("# Sample\n\nHello.\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)
    monkeypatch.setattr(main, "DEFAULT_DOCS_PATH", str(docs_dir))

    response = client.post("/ingest", json={})

    assert response.status_code == 200
    assert response.json()["chunks_ingested"] == 1


def test_startup_event_ingests_the_configured_docs_path(tmp_path, monkeypatch):
    docs_dir = tmp_path / "docs"
    docs_dir.mkdir()
    (docs_dir / "sample.mdx").write_text("# Sample\n\nHello world.\n", encoding="utf-8")
    subprocess.run(["git", "init"], cwd=tmp_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=tmp_path, check=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=tmp_path, check=True)
    subprocess.run(["git", "add", "."], cwd=tmp_path, check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=tmp_path, check=True, capture_output=True)
    monkeypatch.setattr(main, "DEFAULT_DOCS_PATH", str(docs_dir))

    with TestClient(main.app) as startup_client:
        response = startup_client.post("/query", json={"question": "hello"})

    assert response.status_code == 200
    assert len(response.json()["sources"]) > 0
