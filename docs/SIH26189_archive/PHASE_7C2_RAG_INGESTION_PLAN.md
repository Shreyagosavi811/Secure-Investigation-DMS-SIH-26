# PHASE 7C.2 RAG INGESTION PLAN

## 1. Pipeline Architecture
The Phase 8 ingestion pipeline will strictly follow this unidirectional data flow:

```mermaid
flowchart TD
    A[OBSERVED Data (1.14M records)] --> B[Source Adapters]
    B --> C[Normalization & Metadata Enrichment]
    C --> D[Document Construction (JSON Schema)]
    D --> E{Hybrid Indexing Layer}
    E --> F[Vector Index (Embeddings)]
    E --> G[Lexical Index (BM25)]
    E --> H[Metadata Index (Time/Space/Graph)]
    
    I[User Query / Benchmark Query] --> J[Query Rewriting & Temporal Scoping]
    J --> K[Hybrid Retrieval]
    K --> L[Cross-Encoder Reranking]
    L --> M[LLM Reasoning Layer]
    M --> N[Citation / Provenance Response]
```

## 2. Ingestion Steps
1. **Source Adapters**: Specialized parsers for the 10 data formats. (e.g., CSV reader for CDRs, JSON reader for CAF, Regex parser for TXT Field Notes).
2. **Normalization**: Extracting timestamps into ISO-8601, extracting latent surface entities (phones, accounts) into `entity_refs`.
3. **Chunking/Aggregation**: 
   - 1:1 Mapping: FIRs, CAFs, OSINT, Field Notes.
   - Aggregated Mapping: CDRs (group by `caller_phone` per day), CBS (group by `account_id` per day).
4. **Embedding Generation**: Converting `normalized_text` to dense semantic vectors.
5. **Storage**: Committing the JSON document, BM25 tokens, and Vector to the Hybrid Database.

## 3. Technology Stack Recommendation (Phase 8)
- **Vector Database**: **Qdrant** or **Milvus** (Local Docker). 
  - *Why*: Open-source, offline capability, explicitly supports Hybrid Retrieval (BM25 + dense vectors) in a single query, easily handles 1.14M records locally.
- **Embeddings**: **BGE-M3** (`BAAI/bge-m3`).
  - *Why*: Supports dense, sparse (lexical), and multi-vector representations natively. Lightweight enough to run locally without immense GPU overhead.
- **Reranker**: **BGE-Reranker-v2-m3**.
  - *Why*: Highly efficient cross-encoder for boosting top-k precision on needle-in-a-haystack tasks.
- **LLM/Reasoning**: **Llama-3 (8B/70B)** or **Mistral** via `vLLM` / `Ollama`.
  - *Why*: Offline, highly capable of graph-traversal reasoning prompts when fed sufficient context.

## 4. Query & Retrieval Strategy
- **Stage 1 (Filtering)**: Filter vector search space by `scenario_instance_id` (Crucial: prevents searching across 100 scenarios for a single investigation query) and `timestamp` bounds.
- **Stage 2 (Hybrid Search)**: BM25 grabs exact phone numbers/names; Dense embeddings grab semantic context ("suspicious transaction").
- **Stage 3 (Reranking)**: Cross-encoder re-sorts top 100 documents to top 20 context window fitting chunks.
- **Stage 4 (Synthesis)**: LLM answers with forced citations back to `document_id`.
