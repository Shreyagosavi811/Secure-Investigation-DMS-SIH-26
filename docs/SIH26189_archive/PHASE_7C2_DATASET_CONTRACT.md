# PHASE 7C.2: DATASET + RAG INGESTION CONTRACT

## 1. Dataset Overview
The SIH26189 Investigation Dataset is a procedurally generated graph of multi-hop financial, telecom, and intelligence records. The Phase 7C Final Dataset consists of approximately 1.14M observed records spanning 100 scenario instances (from 10 distinct topological families).

## 2. Frozen Architecture
The generator pipeline is now strictly **FROZEN**.
- **No Regeneration**: The final 1.14M records are the permanent Phase 7C artifact.
- **No Topology Modifications**: The ground truth edges and noise mechanisms are locked.
- **No Payload Alteration**: RAG preprocessing must occur downstream (in ingestion memory) without modifying the static JSON/CSV artifacts.

## 3. GROUND_TRUTH vs OBSERVED vs BENCHMARK
The dataset physically separates data into three domains:
- `OBSERVED/`: The sole permissible data source for the RAG index. Contains messy, noisy, and disconnected source records (JSON/CSV/TXT).
- `GROUND_TRUTH/`: **Strictly off-limits** to RAG. Contains the hidden topological graphs, true identities, and evaluation metadata.
- `ML_BENCHMARK/`: **Strictly off-limits** to RAG. Contains formatted Q&A pairs for the 7 benchmark tasks with explicit answers.

## 4. Scenario Family vs Scenario Instance
- **Scenario Family (e.g., S01, S04)**: The topological blueprint (e.g., "Person-Centric", "Financial Multi-Hop").
- **Scenario Instance (e.g., S11, S21)**: The uniquely seeded manifestation of a family. S11 maps to S01's topology but contains distinct names, accounts, timestamps, and distractors. They are globally disjoint graphs.

## 5. Global ID Strategy
To ensure global uniqueness across the 1.14M records without modifying the raw data, the RAG indexer must construct deterministic IDs:
**Format:** `{scenario_instance_id}::{source_type}::{source_record_id}`
**Example:** `S11::cbs_bank_transactions::CBS-S11-00001`
*(Note: Some raw IDs like FIR numbers (`FIR-100/2026/NE`) are not globally unique on their own and require this prepended scope).*

## 6. Canonical Entity Namespace Strategy
**The Collision Issue:** `S01` and `S11` currently share internal ground-truth string labels like `PER-S01-000` due to frozen topological code, even though they represent physically disjoint instances.
**The Solution:** The ingestion and benchmarking normalization layer must dynamically rewrite references as `{scenario_instance_id}::{canonical_id_hidden}`.
**Example:** `S11::PER-S01-000` is distinct from `S01::PER-S01-000`.

## 7. Record Schema
See `PHASE_7C2_RAG_SCHEMA.json` for the precise RAG document JSON Schema. The 10 source types provide variable structured payloads that must be preserved.

## 8. Provenance Schema
Every RAG chunk/document MUST store provenance:
- `source_path` (e.g., `OBSERVED/S11/telecom_cdr_logs.csv`)
- `document_id` (The deterministic global ID)
- `scenario_instance_id` (e.g., `S11`)
- `scenario_family` (e.g., `S01`)

## 9. Temporal Metadata
Raw timestamps (`2026-08-15T14:30:00Z`) must be extracted into a dedicated `timestamp` metadata index to support strict temporal filtering. Records without explicit timestamps (e.g., some criminal history rows mapped only by `case_year`) should omit this metadata or log a standardized null, rather than fabricating dates.

## 10. Spatial Metadata
Location attributes (e.g., `tower_id`, `toll_plaza`, `district`) should be extracted into a `location_refs` metadata array. This enables spatial bounding in future graph retrieval.

## 11. Entity Reference Metadata
Names, MSISDNs, and Bank Accounts present in the text should be duplicated into a structured `entity_refs` array (e.g., `["919876543210", "AC-999123"]`). This is purely for lexical lookup and must **not** involve peeking at `GROUND_TRUTH` canonical IDs.

## 12. Source-Specific Considerations
- **Field Notes**: Unstructured text; must be parsed by regex `\[FNOTE-.*?\]` to extract IDs.
- **Tower Dumps**: Contains arrays of MSISDNs. A single dump record may need to be expanded or specifically embedded to avoid semantic dilution.

## 13. Raw Evidence Preservation
**Decision: One logical evidence document with multiple representations.**
RAG must never discard the raw record. The architecture must store:
- `raw_content`: The original JSON/CSV row.
- `normalized_text`: A templated string for LLM readability (e.g., *"On [Date], FIR [No] was filed..."*).
- `embedding`: The semantic vector.
*(Replacing raw data with LLM summaries destroys evidentiary provenance and compromises court-admissible simulation realism).*

## 14. RAG Ingestion Boundary
Only files residing physically within `output/FINAL_EVALUATION/output/OBSERVED/` may cross the ingestion boundary.

## 15. Chunking Recommendations
Do **not** apply naive token-based chunking (e.g., LangChain 512-token chunks).
- **1-to-1 Mapping**: FIRs, CAFs, social media posts, and field notes should be 1 Document = 1 Record.
- **Aggregated Mapping**: CDRs and Bank Transactions should be aggregated temporally (e.g., "All transactions for Account X on Date Y") to prevent vector DB pollution with millions of microscopic vectors.

## 16. Hybrid Retrieval Requirements
The index must support:
- **Vector Search**: For semantic queries ("suspicious offshore transfer").
- **BM25 Lexical**: For exact MSISDN or account number matching.
- **Metadata Filtering**: Hard pre-filtering by `timestamp` bounds and `scenario_instance_id`.

## 17. Leakage Prevention
Audit script `scripts/audit_rag_boundary.py` confirmed 0 suspicious hidden labels (`canonical_id_hidden`, `ground_truth`) are present in the `OBSERVED` dataset. 

## 18. Evaluation Boundary
The RAG system's output is evaluated against `ML_BENCHMARK/`. The system must ingest `OBSERVED`, process the benchmark query, and output a response. The evaluation script then scores the response against the hidden benchmark `label`.

## 19. Example Normalized Record
```json
{
  "document_id": "S11::telecom_caf_kyc::CAF-S11-0001",
  "scenario_instance_id": "S11",
  "source_type": "telecom_caf_kyc",
  "timestamp": "2026-07-01T10:00:00Z",
  "normalized_text": "Subscriber Arjun Kumar activated phone number 919876543210 on 2026-07-01 in New Delhi.",
  "entity_refs": ["919876543210", "Arjun Kumar"],
  "provenance": {
    "source_path": "OBSERVED/S11/telecom_caf_kyc.json"
  }
}
```

## 20. RAG Readiness Checklist
- [x] OBSERVED dataset isolated
- [x] Deterministic Global IDs designed
- [x] Canonical Namespace strategy defined
- [x] Temporal/Spatial metadata identified
- [x] Zero ground truth leakage verified
- [x] Schema contract formalized
