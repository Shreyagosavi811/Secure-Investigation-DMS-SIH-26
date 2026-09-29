# PHASE 8C: Vectorization & Qdrant Indexing Layer

## Architecture
Phase 8C establishes the foundation for semantic retrieval by embedding the `OBSERVED` Phase 8B RAG corpus using dense vectors and persisting them in a Qdrant index.

### CPU-First Design
The pipeline is designed to execute locally on CPUs without requiring CUDA or GPUs. Model initialization dynamically detects the target device (`cpu`, `cuda`, `mps`) and batch sizes are constrained (default 8) to maintain low RAM overhead while streaming the 1.159M-document dataset.

### Embedding Model: BAAI/bge-m3
- **Selection:** `BAAI/bge-m3` is utilized for multilingual and high-density investigative text retrieval.
- **Model Revision:** Latest via `sentence-transformers==6.0.1`.
- **Embedding Dimension:** `1024` (dynamically validated at runtime instead of hard-coding).
- **Distance Metric:** `Cosine Similarity`.

## Qdrant Setup
- **Version/Mode:** We leverage the local embedded version of `qdrant-client` (`QdrantLocal` via local persistent path `output/qdrant_storage`), avoiding Docker dependencies which are unavailable or unstable on standard Windows developer machines.
- **Collection Name:** `sih26189_evidence`
- **Persistence Configuration:** `/output/qdrant_storage` holds SQLite-based vector data persistently across process restarts.

### Deterministic Point IDs
- Qdrant points are mapped using `UUID5`.
- **Strategy:** `uuid5(NAMESPACE_SIH26189, document_id)`.
- This ensures that if the script halts and resumes, the exact same `document_id` yields the same `point_id`, gracefully overwriting (acting as an upsert) without generating duplicate vectors.

### Payload Schema & Indexes
- **Included Fields:** `document_id`, `scenario_instance_id`, `scenario_family`, `source_type`, `source_record_id`, `timestamp`, `entity_refs`, `location_refs`, `case_refs`, `provenance`.
- **Excluded Fields:** `normalized_text` (To save disk space, the original text is queried from the JSONL via provenance).
- **Indexes:** Keyword payload indexes were created for `source_type`, `scenario_family`, `scenario_instance_id`, `case_refs`, and `entity_refs` for rapid forensic filtering.

## Execution Resiliency
- **Resumability:** A `checkpoint.json` tracks the `last_successful_line` and total processed vectors.
- **Corpus Identity:** A `SHA-256` hash of `corpus_full.jsonl` is computed at launch and recorded in the checkpoint. The indexer strictly refuses to resume if the corpus hash, model, or dimension changes.
- **Failure Handling:** The indexing loop wraps `encode` and `upsert` in a try/except block. Failed batches are counted and reported but do not corrupt the database.

## Test Validation Results
1. **100-Document Validation:** `PASS`. Indexed 100 documents across 10 source types. Vectors successfully bounded and mapped to 100 Qdrant points.
2. **1,000-Document Validation:** `PASS`. Streamed and indexed the first 1000 documents via 125 CPU batches in ~307 seconds (Rate: 3.2 docs/sec on limited Windows CPU environment).
3. **Retrieval Smoke Test:** `PASS`. A semantic query for "large bank deposit or transfer" successfully returned highly relevant Financial Intelligence Unit (FIU) Suspicious Transaction Reports (STRs) and Field Intelligence Notes.
4. **Leakage Audit:** `PASS`. Rejects paths referencing `GROUND_TRUTH` or `ML_BENCHMARK`.
5. **Index Integrity Audit:** Included via `audit_qdrant_index.py` which streams the dataset and asserts exact count matching against Qdrant without materializing massive arrays in memory.

## Known Limitations
1. **CPU Indexing Velocity:** `bge-m3` encodes at approximately ~3 docs/second on this constrained Windows CPU environment. The full 1,159,060 corpus indexing job will require approximately ~100 CPU hours. Resumability ensures this can run incrementally.
2. **Missing Tokenizer Caching:** HuggingFace warns about symlink support on Windows `huggingface_hub` caches, but this does not compromise the pipeline's operational integrity.
3. **Storage Access Lock:** Local Qdrant mandates exclusive locking. Parallel python scripts (e.g., querying while indexing) will raise a `PermissionError` (locked `sqlite3` cache). The RAG API will need to enforce sequential access if using local mode, or migrate to a server setup.

## Phase 8D Recommendation
Proceed to **Phase 8D: Retrieval Benchmarking**. 
Now that the vector database logic is proven, Phase 8D will utilize the `ML_BENCHMARK` labels to quantify the precision/recall metrics (e.g., Hit Rate, MRR) of our embedding strategy before integrating agentic workflows.
