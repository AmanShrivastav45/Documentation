import os
import re
import subprocess
from datetime import datetime, timezone

from rag_pipeline import mock_embed

HEADING_RE = re.compile(r"^(#{1,6})\s+(.*)$", re.MULTILINE)
FRONTMATTER_RE = re.compile(r"\A---\n.*?\n---\n", re.DOTALL)
SELF_CLOSING_JSX_RE = re.compile(r"<[A-Z][A-Za-z0-9]*(?:\s[^>]*)?/>")
OPEN_CLOSE_JSX_RE = re.compile(
    r"<([A-Z][A-Za-z0-9]*)(?:\s[^>]*)?>(.*?)</\1>", re.DOTALL
)
EXPORT_OR_IMPORT_RE = re.compile(r"^(export|import)\s.*$", re.MULTILINE)


def strip_frontmatter(text):
    return FRONTMATTER_RE.sub("", text, count=1)


def strip_jsx(text):
    text = SELF_CLOSING_JSX_RE.sub("", text)
    text = OPEN_CLOSE_JSX_RE.sub(r"\2", text)
    text = EXPORT_OR_IMPORT_RE.sub("", text)
    return text


def chunk_by_headings(text):
    matches = list(HEADING_RE.finditer(text))
    chunks = []
    if not matches:
        stripped = text.strip()
        if stripped:
            chunks.append({"heading": None, "content": stripped})
        return chunks

    if matches[0].start() > 0:
        preamble = text[: matches[0].start()].strip()
        if preamble:
            chunks.append({"heading": None, "content": preamble})

    for i, match in enumerate(matches):
        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        chunks.append(
            {"heading": match.group(2).strip(), "content": text[start:end].strip()}
        )
    return chunks


def get_git_commit_hash(repo_path):
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=repo_path,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def get_last_updated(file_path):
    mtime = os.path.getmtime(file_path)
    return datetime.fromtimestamp(mtime, tz=timezone.utc).isoformat()


def load_mdx_files(docs_path):
    paths = []
    for root, _, files in os.walk(docs_path):
        for name in files:
            if name.endswith(".mdx"):
                paths.append(os.path.join(root, name))
    return sorted(paths)


def ingest_docs(docs_path, store, repo_path=None):
    """Read every .mdx file under docs_path, strip JSX/frontmatter, chunk by
    heading, embed each chunk, and add it to store. Returns the list of
    ingested chunk records (without the embedding vector)."""
    repo_path = repo_path or docs_path
    commit_hash = get_git_commit_hash(repo_path)
    records = []
    for file_path in load_mdx_files(docs_path):
        with open(file_path, encoding="utf-8") as f:
            raw = f.read()
        cleaned = strip_jsx(strip_frontmatter(raw))
        last_updated = get_last_updated(file_path)
        for chunk in chunk_by_headings(cleaned):
            record = {
                "file_path": os.path.relpath(file_path, docs_path).replace("\\", "/"),
                "heading": chunk["heading"],
                "content": chunk["content"],
                "git_commit_hash": commit_hash,
                "last_updated": last_updated,
            }
            store.add(record, mock_embed(record["content"]))
            records.append(record)
    return records
