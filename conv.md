# Firm-Wide Code RAG — Architecture Discussion Summary

## Goal
Production-ready, organization/firm-wide RAG system that ingests code from GitLab repositories/namespaces into a vector database, so any team can query how something was implemented anywhere in the internal infrastructure (e.g. "how did we implement Swarm") and get relevant code back, regardless of which team wrote it.

## The core tension raised
- A pure function/chunk-based indexing approach doesn't scale cleanly when the corpus is "lakhs of repositories" — too many files and functions to search exhaustively.
- The alternative proposed (metadata-tagged namespace ingestion, retrieve-on-ask) solves scale but introduces its own problems: manually maintained metadata files decay, and not ingesting until asked undermines the discovery goal (you can't find what you don't know exists).

## Resolution: two-tier hierarchical retrieval (not either/or)
Chunk-based indexing and coarse routing aren't competing approaches — they're two layers of the same system.

**Tier 1 — Routing index (coarse)**
- One lightweight embedding per repo/namespace.
- Built from README, manifest files, folder structure, and an LLM-generated summary of "what this repo does."
- Auto-generated at ingestion time — not a manually maintained tags file (avoids staleness/coverage decay).
- A query hits this tier first and narrows candidates to the top-k relevant repos.

**Tier 2 — Chunk index (fine)**
- Function/class-level chunks, parsed via AST (e.g. tree-sitter), not arbitrary line windows.
- Each chunk keyed by stable symbol identity: `repo + file_path + symbol_name + git_blob_SHA + start/end_byte_offset` — not raw line numbers, since those drift on every commit.
- Line numbers are resolved for display at query time against the current file (or the stored blob SHA for the exact ingested version).
- Search scoped/filtered to only the repos Tier 1 surfaced — avoids exhaustive full-corpus search.

## Ingestion flow
1. **Trigger** — scheduled namespace crawl or push/webhook on a specific repo (webhook preferred long-term for freshness).
2. **Tier 1 pass** — extract README/manifests/structure → LLM-summarize → embed → store as one routing vector per repo, tagged with repo_id, namespace, team, last-ingested commit SHA.
3. **Tier 2 pass** (async / lower priority, can run lazily for cold repos) — AST-parse each file → chunk by function/class → embed code + short auto-generated docstring together (improves recall for natural-language queries) → upsert with metadata, tagged with the same repo_id.
4. **Update handling** — on new commits, diff against last-ingested SHA and only re-chunk changed files. Re-generate the Tier 1 summary only on structurally significant changes.

## Retrieval flow
1. Query comes in (natural language).
2. **Stage 1** — embed query, search Tier 1 only → top-k candidate repos/namespaces.
3. **Stage 2** — search Tier 2, filtered to `repo_id IN (top-k from Stage 1)`.
4. **Rerank (recommended)** — cross-encoder or LLM pass over top ~20-30 fused hits, since embedding similarity alone is noisy for code (e.g. a comment mentioning "swarm" vs. an actual implementation).
5. **Resolve display references** — map stored byte offsets back to current line numbers + GitLab links.
6. **Return** — code chunk(s) + repo/team attribution + link.

Open design question: whether Stage 2 should always follow Stage 1, or fall back to a full Tier 2 search when Stage 1 confidence is low (vague/cross-cutting queries that don't clearly belong to any repo).

## Vector DB: ChromaDB evaluation
- Chroma now supports dense vector search, sparse/BM25 search, full-text/regex matching, and metadata filtering combined in a single query — suitable for the hybrid search this system needs.
- Scaling caveat: comfortable up to roughly hundreds of thousands of vectors self-hosted; at "lakhs of repos" scale (potentially tens of millions of chunks), Chroma Cloud's distributed offering or alternatives (Qdrant, Weaviate, Milvus) become worth evaluating.
- Metadata filtering has a real performance cost at scale in Chroma — reinforces why the two-tier design (filter to a narrow repo set before fine-grained search) matters rather than filtering over the full chunk index.
- Recommended approach: prototype the full two-tier pipeline on Chroma now; treat the DB as swappable and revisit once real numbers (repo count, avg functions/repo, query volume) are known.

## Search mechanisms to combine
1. **Dense vector search** — semantic similarity for natural-language queries.
2. **Sparse/BM25 keyword search** — critical for code, since exact function/class/variable names and error strings need exact matching that embeddings handle poorly.
3. **Metadata filtering** — Tier 1 → Tier 2 scoping, plus language/team/last-modified filters.
4. **Hybrid fusion (Reciprocal Rank Fusion)** — combine dense + sparse result lists rather than picking one.
5. **Rerank pass** — cross-encoder or lightweight LLM over top fused results for final ordering.

# Build Prompt: FastAPI Code Ingestion Backend (ChromaDB-backed)

Use this as a spec/prompt to hand to a coding agent (or yourself) to scaffold the ingestion + retrieval backend.

---

## Objective
Build a production-oriented Python FastAPI backend that ingests GitLab repositories/namespaces into a two-tier ChromaDB vector store (coarse repo-level routing index + fine-grained function/class-level chunk index), and exposes retrieval endpoints for firm-wide code search.

## Tech stack
- **Framework:** FastAPI (async endpoints throughout)
- **Vector DB:** ChromaDB (PersistentClient or HttpClient against a running Chroma server — not in-memory)
- **Code parsing:** tree-sitter (multi-language AST parsing) for function/class-level chunk extraction
- **GitLab access:** python-gitlab SDK for repo/namespace enumeration, file fetch, webhook payload handling
- **Background jobs:** Celery or FastAPI BackgroundTasks (or an async task queue like arq) for ingestion pipelines, since ingestion should not block request/response cycles
- **Embeddings:** pluggable embedding client interface (so the embedding model/provider can be swapped without touching pipeline logic)
- **LLM summarization:** pluggable LLM client interface for Tier 1 repo summary generation and optional reranking

## Architecture to implement

### Tier 1 — Repo/namespace routing index
- Chroma collection: `repo_routing_index`
- One vector per repo, generated from: README content, manifest files (package.json, pom.xml, requirements.txt, etc.), top-level folder structure, and an LLM-generated 2-4 sentence summary of the repo's purpose/capabilities.
- Metadata per entry: `repo_id`, `namespace`, `team` (if resolvable), `gitlab_url`, `last_ingested_commit_sha`, `last_updated_at`.

### Tier 2 — Function/class chunk index
- Chroma collection: `code_chunk_index`
- One vector per function/class, extracted via tree-sitter AST parsing (not line-window chunking).
- Chunk text: the code itself + an auto-generated short docstring/summary (embed both together for better natural-language recall).
- Metadata per entry: `repo_id`, `file_path`, `symbol_name`, `symbol_type` (function/class/method), `git_blob_sha`, `start_byte`, `end_byte`, `language`, `last_ingested_commit_sha`.
- Use Chroma's sparse/BM25 support alongside dense embeddings on this collection to support hybrid search on exact symbol/keyword matches.

## Required API endpoints

### Ingestion
- `POST /ingest/namespace` — trigger ingestion for a full GitLab namespace (all repos under it). Body: `{namespace_path, force_refresh: bool}`. Enqueues background job(s); returns a job ID.
- `POST /ingest/repo` — trigger ingestion for a single repo. Body: `{repo_url_or_id, force_refresh: bool}`.
- `POST /webhooks/gitlab` — GitLab push-event webhook receiver. Validates webhook secret/token, extracts changed repo + commit SHA, enqueues incremental re-ingestion (diff-based: only re-chunk changed files).
- `GET /ingest/status/{job_id}` — poll ingestion job status (pending/running/completed/failed), with per-tier progress if possible.

### Retrieval
- `POST /query` — main retrieval endpoint. Body: `{query: str, top_k_repos: int = 15, top_k_chunks: int = 20, rerank: bool = true}`.
  - Stage 1: embed query, search `repo_routing_index`, get top-k candidate repo_ids.
  - Stage 2: search `code_chunk_index` filtered to `repo_id IN candidate_repo_ids`, combining dense + sparse (BM25) results via Reciprocal Rank Fusion.
  - Optional rerank pass over fused top results before returning.
  - If Stage 1 confidence is below a configurable threshold (all top-k routing scores weak), fall back to an unfiltered Tier 2 search across all repos and flag this in the response.
  - Response: ranked list of `{repo_id, team, file_path, symbol_name, code_snippet, resolved_line_start, resolved_line_end, gitlab_link, score}`.
- `GET /repos` — list ingested repos with last-ingested metadata (for visibility/debugging).
- `GET /repos/{repo_id}/chunks` — list/paginate chunks for a given repo (debugging/admin use).

### Admin/ops
- `DELETE /repos/{repo_id}` — remove a repo's vectors from both tiers (e.g. repo archived/deleted upstream).
- `GET /health` — liveness/readiness check including Chroma connectivity.

## Ingestion pipeline logic (per repo)
1. Clone/fetch repo at target commit (shallow clone where possible).
2. **Tier 1 update:** gather README + manifests + folder tree → call LLM summarizer → embed summary → upsert into `repo_routing_index`.
3. **Tier 2 update:**
   - If `force_refresh` or first ingestion: walk all source files, parse with tree-sitter per language, extract function/class-level chunks.
   - If incremental (webhook-triggered): diff changed files against `last_ingested_commit_sha`, re-parse only those files, delete stale chunks for removed/modified symbols, upsert new/changed chunks.
   - For each chunk: generate short docstring/summary (LLM or lightweight heuristic), embed code+summary, upsert with full metadata into `code_chunk_index`.
4. Update `last_ingested_commit_sha` and `last_updated_at` on the Tier 1 entry.
5. Emit structured logs/metrics per stage (files processed, chunks created/updated/deleted, duration) for observability.

## Non-functional requirements
- All I/O-bound operations (GitLab API calls, embedding calls, LLM calls, Chroma upserts) must be async or run in a thread/process pool if the underlying SDK is sync.
- Idempotent ingestion: re-running ingestion on an unchanged repo should be a no-op (compare commit SHA before doing work).
- Configurable via environment variables: GitLab base URL + token, Chroma host/port, embedding provider config, LLM provider config, webhook secret.
- Structured logging (JSON) with repo_id/job_id correlation for tracing ingestion jobs end to end.
- Basic auth/API key middleware on all endpoints (internal firm-wide tool, but should not be fully open).
- Unit tests for: chunk boundary extraction correctness (AST parsing), diff-based incremental re-ingestion logic, and RRF fusion ranking logic.

## Deliverable structure (suggested repo layout)
```
app/
  main.py                 # FastAPI app, router registration
  api/
    ingest.py              # ingestion endpoints
    query.py                # retrieval endpoint
    admin.py                 # admin/ops endpoints
  core/
    config.py                 # env-based settings
    chroma_client.py           # Chroma collection setup/access
  ingestion/
    gitlab_client.py            # repo/namespace fetch, webhook parsing
    ast_parser.py                 # tree-sitter chunk extraction
    tier1_pipeline.py               # repo summary + routing index update
    tier2_pipeline.py                # chunk extraction + index update
    diff_engine.py                    # commit-diff based incremental logic
  retrieval/
    router.py                          # Stage 1 repo routing search
    chunk_search.py                     # Stage 2 filtered hybrid search
    fusion.py                            # RRF combination logic
    rerank.py                             # cross-encoder/LLM rerank
  models/
    schemas.py                            # Pydantic request/response models
  workers/
    tasks.py                               # background job definitions
tests/
```
