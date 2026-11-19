# CLAUDE.md — Production RAG Platform (Data Engineering + AI Engineering, learn-by-building)

This file tells Claude how to work in this repository. Read it fully before every task.

## 1. Who I am and why this project exists

- I am an AI engineer (2 years experience: Python, ML, deep learning, LangChain, LangGraph, RAG, n8n, LLM APIs). I learn best by building, file by file.
- I am newer to data engineering, SQL depth, system design, cloud and production engineering.
- I am building this project to show I can own the **whole path**: messy business data → clean, private, fresh data → retrieval → an agent that gives correct, cited answers → measured and monitored in production.
- Target roles: **AI Engineer, LLM/RAG Engineer, AI Data Engineer**, and AI services for my own clients.
- **The use case:** a support knowledge assistant for an online store. Sources: support tickets (Zendesk-style), policy/FAQ documents (Markdown + PDF), orders (CSV / database), and later GitHub issues. The agent answers questions like *"Where is order #1042 and can I return it?"* using a **SQL tool** (exact facts) and a **RAG tool** (policy knowledge), with citations.
- Honesty rule: this project shows **skills**, not years. On my resume I describe it as a project, not as job experience.
- My English is simple. **Reply in easy Roman Urdu mixed with English technical terms.** Short sentences.

## 2. How we build: like a house

We build like a house: first a small house that stands (simple version that runs end to end), then we add rooms, doors, locks, wiring (production features) one by one. **After every file, the project must run.**

- **Claude writes the code.** I type or paste it myself and run it.
- **But Claude explains every file fully**, so I understand it like my own code and can explain it in an interview.
- **One file at a time.** Never give two new files in one reply. Wait until I say "done" / "chal gaya" before the next file.
- When we modify an existing file later, show only the changed part, explain **what changed and why**, and show before vs after.
- After each file I write 3 lines in my own words in `docs/learning_log.md`: what I built, what problem it solves, what broke. Claude reminds me.

## 3. The per-file protocol (follow this EVERY time)

For each new file (or big change), Claude gives these parts in this order:

1. **📍 Map — where are we:** show the pipeline diagram (section 8) and mark this file with "👉 YOU ARE HERE". Say which phase and step this is, and whether it is the **DE side**, the **AI side**, or **both**.
2. **🎯 Kaam — what this file does:** 2-3 simple lines.
3. **📚 New concepts first:** before the code, explain every new concept / library / term used in this file (format in section 4). If a concept was already taught, just give a 1-line reminder.
4. **🔗 Connections:**
   - Which earlier files this file **uses** (imports / reads), and what it takes from them.
   - Which later files will **use this file**, and what they will take.
   - Input → output of the main functions (with types and a tiny example).
5. **💻 Code:** the full file, with short comments on important lines. Production quality (section 6).
6. **🔍 Walkthrough:** explain the code block by block in simple words: what each block does and why it is written this way (and what a beginner version would look like and why it is worse, when useful).
7. **▶️ Run:** the exact command to run it (or test it), and the **expected output**. Ask me to paste my real output. If my output differs, debug with me and explain the error.
8. **🧪 Chhota experiment:** one small change I should try (break something, change a value) to see how the file behaves.
9. **✅ Check:** 2-3 quick questions (easy, medium, hard). Correct my answers and explain what I missed.
10. **Next step:** one line saying which file comes next and why.

At the end of each **phase**: give a short recap (diagram of what exists now, what each file does in 1 line), remind me to **git commit** with a good message, and update the progress tracker (section 10).

## 4. How to explain a concept

1. **WHAT:** 1-2 line simple definition.
2. **WHY:** what problem it solves, what breaks without it.
3. **ANALOGY:** everyday example (shop, restaurant, post office, house, traffic, library).
4. **HOW IT WORKS:** step by step, small ASCII diagram if helpful.
5. **IN THIS PROJECT:** where and why we use it.
6. **TRADE-OFFS / MISTAKES:** when not to use it, common mistakes.
7. **INTERVIEW:** 1 question an interviewer may ask, and a good short answer.

If I say "short", give a compact version. If I say "deep", add internals and edge cases.

**Accuracy:** if unsure, or a library API, model name or cloud/LLM price may have changed, say so and point me to the official docs. Never invent facts, numbers, benchmark results or company architectures.

## 5. Build plan (phases → files, in order)

Each line = one file = one reply following the protocol in section 3. Run after each one.
**MUST** = needed for a strong resume project. **LATER** = do after the MUST phases work.

**Phase 0 — Plot (zameen tayyar):** repo setup — MUST
- 0.1 Folder, venv, `git init`
- 0.2 `pyproject.toml` (dependencies, ruff config, pytest config)
- 0.3 `.gitignore` + `.env.example`
- Concepts: git, venv, pyproject, src layout, ruff, secrets never in git

**Phase 1 — Foundation (chhota ghar jo khada ho):** ingestion runs end to end — MUST — DE side
- 1.1 `scripts/generate_fake_data.py` → creates `data/raw/tickets.jsonl`, `data/raw/docs/*.md` (policies, FAQs), `data/raw/orders.csv` (Faker, seeds, JSONL). Tickets contain fake PII on purpose.
- 1.2 `src/rag_platform/models.py` → pydantic `RawDocument`, `CleanDocument`, `Chunk`, `Lineage` (data contracts + lineage metadata)
- 1.3 `src/rag_platform/sources/base.py` + `file_source.py` → read records as a generator (Source interface)
- 1.4 `src/rag_platform/parse.py` → text from Markdown, JSONL tickets and PDF (pypdf); normalize whitespace and encoding
- 1.5 `src/rag_platform/storage.py` → write layers: `data/raw/` → `data/clean/` (JSONL first, Parquet in Phase 5)
- 1.6 `src/rag_platform/ingest_pipeline.py` → wires 1.3 → 1.4 → 1.5
- ✅ Phase end: one command ingests everything into `clean/`. Commit "v1: basic ingestion".
- Concepts: batch ingestion, raw vs clean layers (medallion: bronze/silver/gold), generators, data contracts, lineage

**Phase 2 — Privacy wall (PII redaction before the LLM sees anything):** — MUST — DE side
- 2.1 `src/rag_platform/privacy/detect.py` → regex (email, phone, card, API key) + Presidio + spaCy NER for names
- 2.2 `src/rag_platform/privacy/redact.py` → strategies: mask vs hash (with salt) vs fake replace
- 2.3 Upgrade `ingest_pipeline.py` → redact step between parse and clean
- Concepts: PII, NER, Presidio Analyzer/Anonymizer, confidence scores, pseudonymization, why redact **before** embedding (embeddings and LLM providers can leak data)

**Phase 3 — Doors and locks (data safety):** — MUST — DE side
- 3.1 `src/rag_platform/quality.py` → data quality checks (missing fields, empty text, duplicates by content hash, too-short docs)
- 3.2 `src/rag_platform/privacy/review.py` → re-scan clean output; leaks → `data/quarantine/` with reason
- 3.3 Upgrade `ingest_pipeline.py` → bad records don't crash the run; accounting check (in = clean + quarantined)
- 3.4 PII-safe error messages and a log redaction filter
- Concepts: data quality, defense in depth, quarantine / dead-letter pattern, human-in-the-loop, no silent data loss, PII-safe logging

**Phase 4 — Knowledge index (DE meets AI):** — MUST — both
- 4.1 `src/rag_platform/indexing/chunk.py` → chunking strategies (fixed size + overlap, by heading/section), chunk ids, metadata
- 4.2 `src/rag_platform/indexing/embed.py` → embedding provider interface (local sentence-transformers first; API provider optional), batching, retries
- 4.3 `src/rag_platform/indexing/vector_store.py` → Qdrant (local mode first) upsert, delete, search; payload metadata
- 4.4 `src/rag_platform/indexing/index_pipeline.py` → **incremental indexing**: content hash per chunk, embed only new/changed chunks, delete chunks of removed docs; idempotent upserts
- Concepts: chunking trade-offs, embeddings, vector DB, cosine similarity, ANN/HNSW (short), content hashing, change detection, idempotency, embedding model versioning (never mix two models in one collection)

**Phase 5 — Warehouse + SQL (structured facts):** — MUST — DE side
- 5.1 `src/rag_platform/warehouse/schema.sql` → DuckDB star schema: `dim_customer`, `dim_product`, `fact_orders`, `fact_tickets` (PII-safe ids only)
- 5.2 `src/rag_platform/warehouse/load.py` → load clean data into DuckDB; upsert by key; clean layer also written as Parquet
- 5.3 `src/rag_platform/runlog.py` → DuckDB `pipeline_runs` table (run_id, times, counts per step, leaks, quarantined, status)
- 5.4 `sql/` example queries (JOIN, GROUP BY, CTE, window functions) on orders, tickets and runs
- Concepts: OLTP vs OLAP, data modeling, star schema, facts vs dimensions, primary keys, upsert/MERGE, DuckDB, Parquet, columnar storage

**Phase 6 — Retrieval (find the right context):** — MUST — AI side
- 6.1 `src/rag_platform/retrieval/retriever.py` → vector search with metadata filters (source, doc type, date)
- 6.2 `src/rag_platform/retrieval/hybrid.py` → BM25 keyword search + vector search, merged with Reciprocal Rank Fusion
- 6.3 `src/rag_platform/retrieval/rerank.py` → cross-encoder reranker on top-k
- Concepts: dense vs sparse retrieval, hybrid search, RRF, reranking, top-k, metadata filtering, latency vs quality

**Phase 7 — Generation + agent (the brain):** — MUST — AI side
- 7.1 `src/rag_platform/llm/client.py` → LLM provider interface (Claude by default, model name from config), timeouts, retries, token + cost counting
- 7.2 `src/rag_platform/llm/prompts.py` → versioned prompt templates; answer only from context; cite chunk ids; say "I don't know" when context is missing
- 7.3 `src/rag_platform/agent/tools.py` → `search_knowledge` (RAG tool) + `query_orders` (**read-only**, parameterized SQL tool on DuckDB, allow-listed tables)
- 7.4 `src/rag_platform/agent/graph.py` → LangGraph agent: route → call tools → answer with citations; max steps limit
- 7.5 `src/rag_platform/agent/guardrails.py` → redact PII in user query, treat retrieved text as data (prompt injection defense), refuse unsafe SQL, output check for PII
- Concepts: tool calling, routing, text-to-SQL risks, grounding, citations, hallucination, prompt injection (direct + indirect), prompt versioning, cost control

**Phase 8 — Meter (evaluation):** — MUST — both
- 8.1 `golden/` → labeled sets (fake data only): `pii_golden.jsonl` (30–50 texts with known PII) + `qa_golden.jsonl` (40–60 questions with expected source chunks and reference answers, including "no answer" questions)
- 8.2 `src/rag_platform/evaluation/pii_eval.py` → precision, recall, F1 per PII type
- 8.3 `src/rag_platform/evaluation/retrieval_eval.py` → recall@k, MRR, hit rate (compare vector vs hybrid vs hybrid+rerank)
- 8.4 `src/rag_platform/evaluation/answer_eval.py` → faithfulness and answer correctness with LLM-as-judge + citation accuracy + refusal accuracy
- 8.5 `evaluation/report.py` → one eval report saved to DuckDB `eval_runs`; fail if below thresholds (regression gate)
- Concepts: offline evaluation, golden sets, why recall matters for privacy, retrieval metrics, LLM-as-judge limits, eval-driven development, regression testing

**Phase 9 — Wiring (production basics):** — MUST
- 9.1 `config/settings.yaml` + `src/rag_platform/config.py` (pydantic-settings; env vars for secrets; config hash)
- 9.2 `src/rag_platform/logging_setup.py` (structured JSON logs with run_id / request_id)
- 9.3 `src/rag_platform/cli.py` (typer: `rag ingest`, `rag index`, `rag eval`, `rag ask "..."`)
- 9.4 `src/rag_platform/api/app.py` (FastAPI: `/ask`, `/health`, `/ready`; request validation; timeouts)
- 9.5 `src/rag_platform/observability.py` → per-request trace in DuckDB `request_logs` (latency per step, tokens, cost, retrieved chunk ids, tool calls; **no raw PII**); optional Langfuse
- Concepts: config vs code, 12-factor, secrets handling, logging levels, CLI design, REST API design, health checks, tracing, latency budgets, caching (short)

**Phase 10 — Inspection (tests + CI):** — MUST
- 10.1 `tests/` unit tests per module + one end-to-end test (ingest → index → ask on tiny fixtures; LLM mocked)
- 10.2 `.pre-commit-config.yaml`
- 10.3 `.github/workflows/ci.yml` (ruff + pytest on every push; eval smoke test with mocked LLM)
- Concepts: unit vs integration vs e2e, fixtures, mocking LLMs, deterministic tests, CI/CD
- Note: write small tests **while building** each module from Phase 1; this phase completes and organizes them.

**Phase 11 — Real tenants (real data source):** — MUST (11.1–11.3), LATER (11.4)
- 11.1 `src/rag_platform/sources/github_source.py` → GitHub issues API
- 11.2 Pagination, rate limits, retries with exponential backoff
- 11.3 Incremental load with state file (`updated_at` cursor) + idempotent writes; updated issues re-indexed, closed/deleted handled
- 11.4 `src/rag_platform/sources/gdrive_source.py` → Google Drive docs (optional)
- Concepts: REST, tokens, pagination, rate limits, backoff, incremental loads, cursors, idempotency, data freshness

**Phase 12 — Moving house (packaging + orchestration):** — LATER
- 12.1 `Dockerfile` + `.dockerignore`
- 12.2 `docker-compose.yml` (api + qdrant)
- 12.3 `src/rag_platform/flows.py` → Prefect flows: `ingest → quality → index → eval` on a schedule, retries per task
- Concepts: containers, image layers, multi-service apps, orchestration, DAGs, scheduling, backfills, Prefect vs Airflow

**Phase 13 — Cloud:** — LATER (recommended)
- 13.1 Upgrade `storage.py` → AWS S3 writer for raw/clean layers (boto3), partitioned by source and date
- **Before any AWS step: warn about cost, prefer free tier, give exact shutdown/delete steps.**
- Concepts: object storage, data lake layout, partitioning, IAM least privilege, encryption at rest, lifecycle rules

**Phase 14 — Paint and nameplate (docs):** — MUST
- 14.1 `README.md` (what, why, architecture diagram, how to run, eval numbers: PII recall, retrieval recall@k, faithfulness, latency, cost per query)
- 14.2 `docs/dataset_card.md` (sources, PII handling, known limits)
- 14.3 `docs/design.md` (architecture + trade-offs: mask vs hash, regex vs NER, chunk size, vector vs hybrid, Qdrant vs pgvector, when human review)
- 14.4 `docs/adr/` (start writing ADRs from Phase 1 whenever we make a big decision; polish them here)
- Concepts: how to explain the project to a client or interviewer in 2 minutes and in 20 minutes

## 6. Production-grade standards (never lower these)

Phase 1 is simple on purpose, but code must still be clean. By the end, the project must look like work from a ~3 years experienced engineer.

**Architecture**
- **Modular:** ingestion (`sources/`, `parse.py`), validation (`models.py`, `quality.py`), privacy (`privacy/`), indexing (`indexing/`), warehouse (`warehouse/`), retrieval (`retrieval/`), generation (`llm/`, `agent/`), serving (`api/`), evaluation (`evaluation/`). Each has clear inputs/outputs. Pipeline files only wire modules; no business logic there.
- **Interfaces for swappable parts:** Source, Embedder, VectorStore, LLM client. Swapping a provider must not touch other modules.

**Data engineering**
- **Data lineage:** every clean document and chunk carries `source`, `source_record_id`, `source_url` if any, `ingested_at`, `run_id`, `pipeline_version`, `config_hash`, `content_hash`, transformations applied (e.g. `[{"type": "EMAIL", "action": "mask", "count": 2}]`), and for chunks also `embedding_model` and `chunker_version`. Never store the original PII value in lineage.
- **No silent data loss:** every input record ends in exactly one place: `clean/` or `quarantine/` (with a reason and error type). Each run checks `records_in == records_clean + records_quarantined` and fails loudly if not.
- **Idempotent and incremental:** re-running any step gives the same result with no duplicates. API sources load incrementally with a cursor. Indexing embeds only changed chunks and removes stale ones.
- Data contracts with pydantic. One bad record never crashes the run; it goes to quarantine with a reason.
- Retries with exponential backoff for every network call (APIs, embeddings, LLM).

**Privacy and security**
- PII is redacted **before** embedding, indexing, warehouse load, or any LLM call.
- Never put raw PII in logs, error messages, exceptions, traces, test output or debug prints. Log only ids, PII types, counts and positions. Add a test that scans log output for PII.
- Quarantine files hold the minimum needed for review and live in gitignored `data/`.
- SQL tool is read-only, parameterized, allow-listed tables, row limit. Never execute free-form SQL from the LLM without validation.
- Retrieved text is untrusted data, never instructions (indirect prompt injection defense).
- Config file + env vars; never hardcode or commit secrets. Fake secrets in tests must not look like real provider keys (avoid GitHub push protection); build them at runtime or use clearly fake prefixes.

**AI engineering**
- Answers are grounded: cite chunk ids; refuse or say "I don't know" when context is not enough.
- Prompts are versioned; prompt version is logged with every answer.
- Agent has a max steps limit and timeouts; tool errors are handled and reported, not hidden.
- Cost and latency are measured per request and per pipeline run.
- **Evaluation gates changes:** PII recall, retrieval recall@k and faithfulness have thresholds; CI fails on regression (mocked/small set in CI, full set locally).

**Code quality and operations**
- Type hints, small functions, clear names, docstrings on public functions.
- Logging, not print (from Phase 9; before that, print is OK and Claude says it will be replaced).
- **Observability:** structured logs + metrics per pipeline run (DuckDB `pipeline_runs`) and per request (DuckDB `request_logs`).
- **Testing:** every important transformation (parse, detect, redact, review, quality, chunk, incremental index, retrieval, SQL tool safety, lineage, idempotency) has automated tests. LLM calls are mocked in unit tests.
- pytest tests + GitHub Actions CI with ruff.
- Runs with one command, locally and in Docker.
- `data/` is gitignored.
- **Documentation:** README (setup + architecture + eval numbers) and **ADRs** in `docs/adr/`: one short file per big decision (context, decision, alternatives, consequences).

## 7. Tech stack

- **Core:** Python 3.11+, venv, ruff, pre-commit, pydantic v2 + pydantic-settings, typer, pytest
- **Data engineering:** Faker, pypdf, DuckDB, Parquet (pyarrow), httpx (GitHub REST API), Prefect, Docker, optional AWS S3 + boto3
- **Privacy:** Microsoft Presidio + spaCy
- **AI engineering:** sentence-transformers (embeddings + cross-encoder reranker), Qdrant (qdrant-client, local mode → Docker), rank-bm25, LangGraph, Anthropic SDK (Claude; model name in config, check the docs for current model ids and prices), FastAPI + uvicorn
- **Optional:** Langfuse (tracing), Google Drive API

Claude checks current library versions and APIs in official docs before using them, and says so when unsure.

## 8. Final pipeline flow

```
                        ┌──────────── OFFLINE: DATA PIPELINE (DE side) ────────────┐
Sources (files / GitHub API / Drive)
   │ 1. INGEST (incremental, idempotent)
   ▼
raw/ (as it arrived)
   │ 2. PARSE + VALIDATE (pydantic + quality checks) ── bad ──► quarantine/
   ▼
   │ 3. DETECT + REDACT PII (Presidio + regex; mask / hash)
   ▼
   │ 4. REVIEW (re-scan output) ── leak ──► quarantine/
   ▼
clean/ (Parquet) ──────────────┬──────────────────────────────┐
                               │                              │
   5a. CHUNK + EMBED           │                   5b. LOAD WAREHOUSE
   (only changed chunks)       │                   (DuckDB star schema)
        ▼                      │                              ▼
   Qdrant vector index         │                   fact_orders, fact_tickets ...
                        └──────┼──────────────────────────────┼────────────────────┘
                               │                              │
                        ┌──────┼──── ONLINE: SERVING (AI side) ┼───────────────────┐
User question → API /ask → guardrails (redact query)          │
                               ▼                              ▼
                    LangGraph agent ──► search_knowledge   query_orders (read-only SQL)
                               │        (hybrid + rerank)
                               ▼
                    Answer with citations → output check → user
                        └──────────────────────────────────────────────────────────┘

6. REPORT + OBSERVE: pipeline_runs, request_logs, eval_runs (DuckDB)
7. EVALUATE: PII P/R/F1 · retrieval recall@k, MRR · faithfulness · cost · latency
```

## 9. Final folder structure

```
rag-platform/
├── CLAUDE.md
├── README.md
├── pyproject.toml
├── .env.example
├── config/settings.yaml
├── data/                  # gitignored: raw/ clean/ quarantine/ state/ warehouse.duckdb qdrant/
├── golden/                # pii_golden.jsonl, qa_golden.jsonl (fake data only)
├── sql/                   # example SQL queries
├── docs/                  # design.md, dataset_card.md, learning_log.md, adr/
├── scripts/generate_fake_data.py
├── src/rag_platform/
│   ├── models.py  config.py  logging_setup.py  observability.py  runlog.py  storage.py
│   ├── parse.py  quality.py  ingest_pipeline.py  flows.py  cli.py
│   ├── sources/      (base.py, file_source.py, github_source.py, gdrive_source.py)
│   ├── privacy/      (detect.py, redact.py, review.py)
│   ├── indexing/     (chunk.py, embed.py, vector_store.py, index_pipeline.py)
│   ├── warehouse/    (schema.sql, load.py)
│   ├── retrieval/    (retriever.py, hybrid.py, rerank.py)
│   ├── llm/          (client.py, prompts.py)
│   ├── agent/        (tools.py, graph.py, guardrails.py)
│   ├── evaluation/   (pii_eval.py, retrieval_eval.py, answer_eval.py, report.py)
│   └── api/          (app.py)
├── tests/
├── Dockerfile
├── docker-compose.yml
└── .github/workflows/ci.yml
```

## 10. Progress tracker (Claude: update after each phase)

| Phase | Side | Status | Check scores | Weak points to revisit |
|---|---|---|---|---|
| 0 Plot | setup | not started | | |
| 1 Foundation (ingestion) | DE | not started | | |
| 2 Privacy (PII redaction) | DE | not started | | |
| 3 Safety (quality + quarantine) | DE | not started | | |
| 4 Knowledge index | DE + AI | not started | | |
| 5 Warehouse + SQL | DE | not started | | |
| 6 Retrieval | AI | not started | | |
| 7 Generation + agent | AI | not started | | |
| 8 Evaluation | DE + AI | not started | | |
| 9 Wiring (config, API, observability) | prod | not started | | |
| 10 Tests + CI | prod | not started | | |
| 11 Real source (GitHub) | DE | not started | | |
| 12 Docker + Prefect | prod | not started | | |
| 13 Cloud (S3) | DE | not started | | |
| 14 Docs | all | not started | | |

## 11. End of every reply

End every reply with **"Next step:"** and one small thing to do, run, or answer.
