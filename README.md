# Docs Platform

A documentation platform combining client-side-compiled MDX (React + Vite + Tailwind)
with a live RAG Q&A backend (FastAPI) serving docs over an API.

## Frontend

```bash
cd frontend
npm install
npm run dev      # http://localhost:5173
npm test         # Vitest + React Testing Library
npm run build    # static production build
```

## Backend

```bash
cd backend
python -m venv .venv
source .venv/Scripts/activate   # Windows Git Bash; use .venv\Scripts\Activate.ps1 in PowerShell
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
pytest tests/ -v
```

## How it fits together

- Doc content and structure live in `backend/docs/` (`.mdx` files plus a
  `docs.json` tree). The frontend has no doc content of its own — it fetches
  everything over the API.
- `GET /api/docs/structure` returns `docs.json` verbatim; the sidebar renders
  it recursively, with per-folder expand/collapse and auto-expansion of the
  active doc's ancestor folders.
- `GET /api/docs/content?path=...` returns a doc's raw `.mdx` text, guarded
  against path traversal. The frontend compiles it in the browser via
  `@mdx-js/mdx`'s `evaluate()`, supplying `Callout`/`CodeTabs`/
  `LiveMetricPreview` as a components map — no build-time MDX compilation
  happens anymore.
- `POST /ingest` reads the same `backend/docs/` files, chunks by heading, and
  stores mock embeddings with `{file_path, heading, git_commit_hash,
  last_updated}` metadata. The backend also auto-ingests on startup, so the
  chat panel works immediately without a manual `/ingest` call — though
  `/ingest` is still there to re-index after content edits.
- `POST /query` retrieves the top matching chunks and returns a templated
  answer plus source citations, so every answer is traceable back to a
  reviewed doc version.
- `validate_docs.py` (run manually, or wire into your own CI) checks that
  every `.mdx` file under `backend/docs/` has a `docs.json` entry and vice
  versa.
- The `ChatPanel` component is unchanged by this refactor: still separate
  from doc rendering, still renders answers with `react-markdown` (never the
  MDX compiler), since RAG output is untrusted runtime content.

Mock embeddings and a mock LLM call are used for scaffolding. Swapping in a
real vector store (Chroma/pgvector) and LLM client only requires changing
`rag_pipeline.py` — the `VectorStore` and `mock_llm_answer` call sites stay
the same.
