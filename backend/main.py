import json
import os
import subprocess
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel

from ingest import ingest_docs
from rag_pipeline import VectorStore, mock_llm_answer

app = FastAPI(title="Docs Platform RAG API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

store = VectorStore()

DEFAULT_DOCS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "docs")


@app.get("/")
def read_root():
    return {"status": "ok"}


@app.get("/api/docs/structure")
def get_docs_structure():
    docs_json_path = os.path.join(DEFAULT_DOCS_PATH, "docs.json")
    with open(docs_json_path, encoding="utf-8") as f:
        return json.load(f)


@app.get("/api/docs/content", response_class=PlainTextResponse)
def get_doc_content(path: str):
    docs_root = os.path.realpath(DEFAULT_DOCS_PATH)
    requested = os.path.realpath(os.path.join(docs_root, path))
    if not (requested == docs_root or requested.startswith(docs_root + os.sep)):
        raise HTTPException(status_code=400, detail="path escapes the docs directory")
    if not os.path.isfile(requested):
        raise HTTPException(status_code=404, detail=f"doc not found: {path}")
    with open(requested, encoding="utf-8") as f:
        return f.read()


class IngestRequest(BaseModel):
    docs_path: Optional[str] = None
    repo_path: Optional[str] = None


class IngestResponse(BaseModel):
    chunks_ingested: int


class QueryRequest(BaseModel):
    question: str
    top_k: int = 3


class SourceCitation(BaseModel):
    file_path: str
    heading: Optional[str]
    git_commit_hash: str
    last_updated: str


class QueryResponse(BaseModel):
    answer: str
    sources: list[SourceCitation]


@app.post("/ingest", response_model=IngestResponse)
def ingest(request: IngestRequest):
    docs_path = request.docs_path or DEFAULT_DOCS_PATH
    if not os.path.isdir(docs_path):
        raise HTTPException(
            status_code=400,
            detail=f"docs_path does not exist or is not a directory: {docs_path}",
        )
    store.clear()
    try:
        records = ingest_docs(docs_path, store, repo_path=request.repo_path)
    except subprocess.CalledProcessError as exc:
        raise HTTPException(
            status_code=400,
            detail=f"Failed to read git commit hash (is repo_path a git repository?): {exc}",
        ) from exc
    return IngestResponse(chunks_ingested=len(records))


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    top_chunks = store.retrieve_top_k(request.question, k=request.top_k)
    answer = mock_llm_answer(request.question, top_chunks)
    sources = [
        SourceCitation(
            file_path=chunk["file_path"],
            heading=chunk["heading"],
            git_commit_hash=chunk["git_commit_hash"],
            last_updated=chunk["last_updated"],
        )
        for chunk in top_chunks
    ]
    return QueryResponse(answer=answer, sources=sources)


@app.on_event("startup")
def ingest_on_startup():
    if not os.path.isdir(DEFAULT_DOCS_PATH):
        return
    store.clear()
    try:
        ingest_docs(DEFAULT_DOCS_PATH, store)
    except subprocess.CalledProcessError:
        pass
