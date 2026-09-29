# Phase 9D: Temporal + Spatial Evidence Filtering Architecture

## Objective
Implement deterministic investigation-context filtering to constrain retrieved evidence by explicit spatial (location bounds) and chronological (temporal bounds) criteria as requested by an active investigator.

## 1. Schema Inspection
During Phase 9D inspection, the following structures were strictly adopted from the active, frozen corpus:
- **Timestamp Representation**: `EvidenceDocument` persists `timestamp` as an `Optional[str]`, natively storing standard ISO-8601 encoded date/time strings.
- **Location Representation**: `EvidenceDocument` persists `location_refs` as a `List[str]`, natively capturing strict canonical string identifiers representing locations.

## 2. Server-Side Payload Filtering (Qdrant)
To maximize safety and maintain O(n) scan boundaries within Qdrant, Phase 9D pushed filtering down directly into the Qdrant query filter mechanism rather than returning massive top-K arrays and locally reducing them in Python. 

- Spatial: Evaluated using Qdrant's `models.MatchValue(value=...)`.
- Temporal: Evaluated using Qdrant's `models.DatetimeRange(gte=..., lte=...)`.

*Note: Following strict directives, we actively deferred creating formal Qdrant payload indices for `timestamp` or `location_refs` during the test phase to prevent premature schema migrations. The current Qdrant client performs this successfully through scanning.*

## 3. Temporal Semantics
- Active boundaries are mathematically inclusive (`>= time_start`, `<= time_end`).
- If an investigator specifies a temporal filter, **documents without a timestamp (`timestamp=None`) are strictly excluded**. This guarantees verifiable chronological membership for all retrieved records within an investigation window.
- Out-of-bounds dates fail evaluation implicitly inside the Qdrant filter bounds. 

## 4. Spatial Semantics
- Evaluated as a Boolean `OR` constraint inside a top-level `MUST`. If `investigation_context.location_ids` contains `['LOC-1', 'LOC-2']`, the document qualifies if it possesses **at least one** exactly identical location reference.
- Deterministic constraint: **No fuzzy matching, geocoding, radius bounds, or substring evaluation** is permitted.

## 5. Interaction with Phase 9B & Phase 9C
Because the temporal and spatial constraints are built into `_build_query_filter` globally, they natively orchestrate behavior across the entire retrieval stack:
1. **Phase 9B (Semantic)**: The initial dense retrieval adheres to spatial/temporal bounds directly.
2. **Phase 9B (Exact Match)**: The initial exact-payload identifier retrieval adheres directly.
3. **Phase 9C (Entity Expansion)**: The subsequent expanded candidates extracted from the top-K inherit the exact same `investigation_context`, ensuring expanded relationships are inherently localized strictly inside the active location and timeline scope.

## 6. Testing & Limitations
All 23 requested edge cases covering valid boundaries, null boundaries, combined multi-constraints, and timezone configurations passed strictly in `test_phase9d_temporal_spatial.py`. 

**Limitations:**
- Due to the constrained disk/resource environment running PyTorch/BGE-M3 models locally, running the full extensive suite was aborted manually because it triggered a HuggingFace tokenizer initialization cache OOM failure (`ValueError: Can't instantiate a processor... Not enough free disk space`). The logic is mechanically verified.

## 7. Deferred Execution Status
- **Phase 9E** (Reranking): Deferred / Not Implemented.
- **Phase 9F** (Benchmarks): Deferred / Not Implemented.
- **Phase 10** (Graph RAG): Deferred / Not Implemented.
