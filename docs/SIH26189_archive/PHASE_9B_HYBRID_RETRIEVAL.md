# PHASE 9B — DETERMINISTIC HYBRID RETRIEVAL

## Overview
Phase 9B successfully upgrades the existing retrieval infrastructure to support **Hybrid Retrieval** by deterministically fusing semantic vector search with exact Qdrant payload identifier matching, while preserving 100% backward compatibility for Phase 8D evaluation baseline.

## Architecture

The architecture implements candidate fusion via independent retrieval pipelines:

```text
Query
 ↓
ID extraction (Regex)
 ↓
Semantic retrieval (BGE-M3) + Exact payload retrieval (Qdrant scroll)
 ↓
Candidate fusion (Deduplication by document_id)
 ↓
Context filtering (source_type, case_ids)
 ↓
Deterministic ranking
 ↓
Top-K
```

## Supported Identifiers

Through rigorous inspection of the `rag/adapters/` and the frozen `OBSERVED` & `GROUND_TRUTH` corpuses, the following identifier formats have been implemented for deterministic extraction:

- **Person IDs**: `P-\d+`
- **Phone IDs**: `PHONE-\d+` or `\+91-\d{10}` (e.g. +91-9836352800)
- **Vehicle IDs**: `VEH-[\w-]+` or standard Indian license plates like `[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}` (e.g. DL05CF1567)
- **Account IDs**: `ACC-\d+` 
- **FIR IDs**: `FIR-[\d-]+`
- **Source Record IDs**: Standard project prefixes `FIU|CAF|CBS|CDR|FIN|OSINT|CH|ANPR-[\w-]+`

## Payload Fields

The following actual Qdrant payload fields are used during hybrid retrieval:

**For Exact Matching:**
- `entity_refs` (Keyword Index)
- `case_refs` (Keyword Index)
- `source_record_id`

**For Context Filtering:**
- `source_type` (Keyword Index)
- `case_refs` (Keyword Index)

## Ranking

When results from the semantic query and exact ID query are fused, ranking is deterministic and prioritizes explicit matches:

1. **Exact-Match Tier**: Any document matched via exact payload identifier is boosted to the top of the list (`exact_match=True`).
2. **Semantic Score**: Within the exact-match tier (or non-exact tier), candidates are ordered by their `bge-m3` semantic similarity score descending.
3. **Document ID**: Tie-breaker sort by `document_id` ascending.

## Backward Compatibility

The default signature for `RetrievalAPI.search()` remains `retrieval_mode="semantic"`. This ensures existing scripts (such as Phase 8D benchmark) execute entirely semantic retrieval without regex ID extraction, protecting the semantic evaluation metrics.

Hybrid retrieval must be explicitly requested via `retrieval_mode="hybrid"`.

## Temporal Boundary

**Temporal filtering is intentionally deferred to Phase 9D.**
While `InvestigationContext` provides `time_start` and `time_end`, these are NOT injected into Qdrant queries. Qdrant payload `timestamp` is preserved as a string; attempting ad-hoc date parsing inside Phase 9B is structurally forbidden.

## Limitations

- **No Lexical Engines**: Elasticsearch, OpenSearch, Whoosh, and BM25 were intentionally excluded. "Lexical retrieval" is strictly exact payload matching.
- **No Entity Resolution**: Extracted identifiers must strictly match indexed payload arrays.
- **No Approximate Strings**: Fuzzy substring matching is unsupported.
- **No Graph / Reranking**: Graph traversal and LLM reranking are out of scope.
- **Index Scope**: The current pipeline is validated exclusively against the ~1,090-vector test index. The 1,159,060-document full production corpus remains intentionally deferred.

## Phase Boundary Constraints Confirmed

- 9C Entity-Aware Expansion: **NOT IMPLEMENTED**
- 9D Temporal/Spatial Filtering: **NOT IMPLEMENTED**
- 9E Reranking: **NOT IMPLEMENTED**
- 9F Phase 9 Evaluation: **NOT IMPLEMENTED**
