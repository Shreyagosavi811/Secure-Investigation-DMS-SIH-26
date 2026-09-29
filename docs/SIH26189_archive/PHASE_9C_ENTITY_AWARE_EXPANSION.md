# PHASE 9C — ENTITY-AWARE EVIDENCE EXPANSION

## Objective
Implement entity-aware evidence expansion from structured payload references to improve investigation context retrieval. This allows documents that explicitly share entity references to be surfaced deterministically.

## Pipeline

```text
Query
 ↓
Phase 9B Hybrid Retrieval
 ↓
Initial Evidence
 ↓
Extract entity_refs
 ↓
Exact entity payload lookup
 ↓
Candidate fusion
 ↓
Final Top-K
```

## Entity Source
Entity expansion uses **ONLY** the `entity_refs` array explicitly indexed within the observed evidence Qdrant payloads. 
It does not run regex on raw text, does not use NER/LLMs, and does not invent missing references.

## Matching
Entity matching enforces **exact equality only**. The deterministic payload exact-match query mechanism is used (via `Qdrant scroll`). Substrings, fuzzy matches, and semantic embeddings are not used for entity identification.

## Expansion Depth
Expansion depth is strictly: **`depth = 1`**. 
No recursive expansion or multi-hop relationship resolution is performed, effectively guaranteeing a bounded O(1) query explosion factor.

## Context Filtering
The Phase 9C entity expansion phase actively preserves and respects current contextual limits:
- `source_type_filters`
- `case_ids`

These filters are piped straight into the expansion Qdrant query to constrain expansion strictly to context-relevant files.

## Temporal Boundary
**Temporal filtering remains deferred to Phase 9D.** No timestamps were parsed or added to queries.

## Ranking
Ranking occurs deterministically following these prioritized rules:
1. `expansion_depth` ASC (Depth 0 Direct Evidence > Depth 1 Expanded Evidence)
2. `exact_match` DESC (Exact Query Identifier > Semantic Base Result)
3. `score` DESC (BGE-M3 Semantic similarity, falling back to 0.0 for pure expansion)
4. `document_id` ASC (UUID string sorting to deterministically break ties)

## Limits
To prevent query explosion, the expansion is deterministically bounded:
- **Max Expansion Entities**: Top 20 unique exact entities extracted from depth 0.
- **Max Candidates Per Entity**: Handled by passing entities in bulk and limiting exact result `scroll` to `top_k * 3`.
- **Final Result Size**: Deterministically truncated to `top_k`.
- **Index Scope**: The current pipeline is validated exclusively against the ~1090-vector test index. The full production corpus is not indexed yet.

## Security / Leakage
- **No Ground Truth**: Evaluator labels and `GROUND_TRUTH` folders are never accessed.
- **No Hidden Evidence**: The Qdrant structure depends solely on Phase 8A/8B frozen outputs.
- **No Benchmark Answers**: Runtime retrieval executes blind to validation scenarios.

## Phase Boundaries
The system operates within strict boundaries. The following features are deferred:
- 9D Temporal/Spatial Filtering: **NOT IMPLEMENTED**
- 9E Reranking: **NOT IMPLEMENTED**
- 9F Evaluation: **NOT IMPLEMENTED**
- 10 Graph-Aware RAG: **NOT IMPLEMENTED**
