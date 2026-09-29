# PHASE 11A — INTELLIGENCE AUDIT AND DESIGN

## 1. Executive Summary
This document serves as the audit and design foundation for Phase 11 (Investigation Intelligence Layer) of the SIH26189 project. The existing `investigation_dataset_engine` is confirmed as a robust, frozen foundation with mature dataset generation and retrieval components (Phases 1-10D). This audit verifies that we can build the Phase 11 Intelligence Layer directly on top of the existing RAG retrieval components without modifying the underlying frozen dataset pipeline or Qdrant index.

## 2. Current Repository Architecture
The main Git repository is established at the project root `SIH-26-Criminal-Network-Analysis`. All dataset and foundational retrieval code resides strictly within the `investigation_dataset_engine` directory. General repository files (README, architecture docs, .gitignore) have been elevated to the root, maintaining a clean workspace for upcoming intelligence, backend, and frontend directories.

## 3. Existing Dataset/RAG Architecture
The existing engine (`investigation_dataset_engine/`) is structured into:
- `generator/`: Generates the mock scenario records.
- `rag/`: Core semantic and exact vector storage, models, and contextual retrieval.
- `schemas/`: Defines exact data formats for canonical entities and records.
- `validation/`: Assures the correctness of generated datasets (spatial, temporal, leakage).
- `confidence/`: Contains deterministic confidence scoring logic.

## 4. Existing Retrieval Pipeline
The retrieval pipeline is highly mature, located in `rag/vectorstore/retrieval.py` (`RetrievalAPI`).
- Supports **Hybrid Search**: Combines semantic embeddings with explicit ID extraction (`_extract_identifiers`).
- Performs **Candidate Fusion**: Merges semantic and exact match results dynamically.
- Performs **Reranking**: Uses deterministic weights for semantic baseline, exact match boosting, and expansion penalties.

## 5. Existing Entity Capabilities
- `RetrievalAPI` automatically extracts entity identifiers via Regex (Phones, FIRs, Vehicles, Accounts, PAN, Aadhaar) from queries.
- Entities are embedded as `entity_refs` in Qdrant payloads, enabling exact match filtering via `QdrantEvidenceClient.search_exact`.
- Depth-1 Entity Expansion is natively supported in `RetrievalAPI.search` via the `entity_expansion` flag.

## 6. Existing Relationship Capabilities
- Implicit relationships exist via co-occurrence in `entity_refs` within retrieved `EvidenceDocument` payloads.
- **Missing**: There are no explicit graph structures (Nodes/Edges) natively built into the runtime retrieval layer. Graph mapping currently only exists in the hidden generator ground truth.

## 7. Existing Temporal Capabilities
- `InvestigationContext` natively supports `time_start` and `time_end`.
- `QdrantEvidenceClient` translates these into Qdrant `models.DatetimeRange` filters targeting the `timestamp` payload field.
- **Missing**: Complex timeline extraction or chronologically constrained multi-hop reasoning.

## 8. Existing Spatial Capabilities
- `InvestigationContext` natively supports `location_ids`.
- `QdrantEvidenceClient` filters via Qdrant `models.MatchValue` on `location_refs`.
- **Missing**: Proximity, radius, or spatial-correlation reasoning algorithms.

## 9. Existing Graph/Data Structures
- `rag/models/evidence.py`: `EvidenceDocument` effectively acts as a flat graph node containing references (`entity_refs`, `location_refs`).
- **Missing**: Dedicated structures for Investigation Graphs, Paths, and Graph Reasoning state.

## 10. Existing Confidence/Scoring
- `confidence/model.py`: `EvidenceConfidenceCalculator` dynamically calculates confidence based on:
  - Base Source Weights (e.g., CBS Bank = 0.98, Social Media = 0.50).
  - Source Diversity Bonuses.
  - Temporal and Identity consistency modifiers.

## 11. Existing Evidence/Provenance
- `rag/models/evidence.py`: `Provenance` tracking contains `source_path` and `ingestion_version`.
- `EvidenceDocument` contains `document_id`, `source_record_id`, and `scenario_instance_id`.

## 12. Existing RAG/Answer Generation
- A `query_answer_schema.json` exists in schemas.
- **Missing**: No explicit LLM-based RAG generation logic or prompt chains have been implemented yet for generating investigator explanations.

## 13. Reusable Components
- **`rag/vectorstore/retrieval.py::RetrievalAPI`**
  - *Purpose*: Core evidence retrieval engine.
  - *Input*: Text query, InvestigationContext.
  - *Output*: Ranked list of EvidenceDocuments (dicts).
  - *Phase 11 Usage*: Foundation for multi-hop graph nodes.
- **`rag/vectorstore/qdrant_client.py::QdrantEvidenceClient`**
  - *Purpose*: Low-level DB access and spatial/temporal filtering.
  - *Phase 11 Usage*: Execute targeted exact-match expansions during reasoning hops.
- **`rag/investigation/context.py::InvestigationContext`**
  - *Purpose*: Tracks investigator state (filters, timeframe).
  - *Phase 11 Usage*: State object passed from UI to Intelligence layer.
- **`confidence/model.py::EvidenceConfidenceCalculator`**
  - *Purpose*: Deterministic risk/confidence scoring.
  - *Phase 11 Usage*: Used by the intelligence layer to score the final derived investigation chains.
- **`rag/models/evidence.py::EvidenceDocument`**
  - *Purpose*: Standardized evidence representation.
  - *Phase 11 Usage*: Base data structure mapped into the Graph.

## 14. Missing Components
1. **Query Understanding module**: To parse natural language into `InvestigationContext`.
2. **Investigation Graph Builder**: To convert `List[EvidenceDocument]` into Node/Edge representations.
3. **Multi-Hop Reasoning Engine**: To trace paths across multiple entities recursively.
4. **Correlation Engine**: To detect explicit temporal sequences and spatial clusters.
5. **Answer Generation**: To translate graph insights into an intelligence report.

## 15. Proposed Phase 11 Architecture
Phase 11 will sit strictly **ABOVE** `investigation_dataset_engine`. It will act as a client consuming the `RetrievalAPI`.

```text
[ INVESTIGATOR UI ]
       │
[ PHASE 11: INTELLIGENCE API ]
  - Query Parsing
  - Graph Construction
  - Multi-Hop Reasoning
  - Correlation & Scoring
  - RAG Generation
       │
[ PHASE 1-10: DATASET ENGINE ]
  - Hybrid Retrieval
  - Qdrant Vector Store
```

## 16. Proposed Phase 11 Module Structure
```text
backend/
└── intelligence/
    ├── query/        # NL to InvestigationContext
    ├── graph/        # Investigation Graph construction
    ├── reasoning/    # Multi-hop path tracing
    ├── correlation/  # Temporal & Spatial analysis
    ├── scoring/      # Path risk and confidence evaluation
    ├── evidence/     # Chain of custody / Provenance linking
    └── answer/       # Final LLM RAG explanation
```

## 17. Data Contracts
- **Query -> Retrieval**: `InvestigationContext` passed to `RetrievalAPI.search`.
- **Retrieval -> Graph**: `List[EvidenceDocument]` mapped to `InvestigationNode` and `InvestigationEdge`.
- **Graph -> Reasoning**: Recursive queries over the Graph yielding `EvidenceChain`s.
- **Reasoning -> Answer**: Aggregated `ScoredFindings` fed to the LLM prompt.

## 18. Evidence Provenance Design
Every intelligence finding must embed an `EvidenceChain` referencing the original `document_id` and `source_record_id`s from `EvidenceDocument`.

## 19. Ground Truth Isolation
**CRITICAL RULE**: Phase 11 must **never** import from `generator/` or read from `output/GROUND_TRUTH/`. It must only interface via `rag/vectorstore/retrieval.py` and act strictly on retrieved payloads to guarantee zero label leakage.

## 20. Multi-Hop Reasoning Design
Algorithm (Breadth-First Expansion):
1. Initial Query yields Seed Evidence via Hybrid Retrieval.
2. Extract all `entity_refs` from Seed Evidence.
3. Query `RetrievalAPI.search(retrieval_mode="hybrid", query=extracted_ref)` for Hop +1.
4. Construct edges based on co-occurrence in retrieved payloads.
5. Filter paths by contextual relevance.

## 21. Temporal/Spatial Correlation Design
- **Temporal**: Sort `EvidenceChain` by payload `timestamp`. Flag intervals < 30 minutes as high-correlation.
- **Spatial**: Group events sharing identical `location_refs` and temporally adjacent occurrences.

## 22. Confidence/Scoring Design
Combine `EvidenceConfidenceCalculator` (source weights) with Graph properties:
- Path Length (longer = lower confidence).
- Redundancy (multiple independent paths = higher confidence).

## 23. Evaluation Strategy
Offline evaluation will compare the extracted `EvidenceChain`s against the hidden Ground Truth graphs (evaluated strictly outside of the runtime pipeline) using `audit_runner.py` extensions.

## 24. MVP Design
Focus on evaluating small, highly-deterministic analytical scenarios that do not require full LLM orchestration immediately. Hardcode the multi-hop reasoning rules to prove the concept before adding generative unpredictability.

## 25. Recommended 2–3 Scenarios
1. **Person → Phone → Tower → Location → Timeline**: Track an individual's movement based on cellular data.
2. **Person → Bank Account → Transaction → Person**: Establish financial linkage between two suspects.
3. **Person → Vehicle → ANPR → Location → Incident**: Correlate a suspect's vehicle to the location of a reported FIR.

## 26. Failure Modes
- **Sparse Retrieval**: If Hop 1 fails to retrieve the bridging document, the graph breaks.
- **Entity Resolution Noise**: Shared names or partial identifiers linking the wrong sub-graphs.
- **Context Window Overflow**: Passing a massive multi-hop graph to the LLM.

## 27. Security / Leakage Risks
Directly importing schemas from the generator logic could inadvertently leak ground truth relationships into the reasoning prompt. Strict data contract abstraction is required.

## 28. Phase 11 Implementation Roadmap
- **11A** — Audit / Design *(Complete)*
- **11B** — Intelligence Data Contracts
- **11C** — Investigation Graph
- **11D** — Multi-Hop Reasoning
- **11E** — Temporal / Spatial Correlation
- **11F** — Evidence + Risk Scoring
- **11G** — RAG Investigation Answer
- **11H** — Integration + Evaluation

## 29. Exact Recommended Next Step
**PHASE 11B — Intelligence Data Contracts**
Define the Python Pydantic models for the Investigation Graph, Node, Edge, and EvidenceChain that will decouple the intelligence layer from the raw vector payloads.
