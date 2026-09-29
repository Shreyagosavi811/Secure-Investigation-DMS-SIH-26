# Phase 8B: RAG Normalization & Corpus Generation

## Overview
Phase 8B implements the data preparation layer for the SIH26189 RAG architecture. It transforms the 1.139M noisy, frozen `OBSERVED` records into a deterministic, leakage-audited JSONL corpus formatted for downstream vectorization. 

> **IMPORTANT:** The RAG corpus is strictly derived from the `OBSERVED` dataset. The `GROUND_TRUTH` and `ML_BENCHMARK` directories remain completely isolated for evaluation only.

## 1. Architecture
The architecture streams individual files without exhausting system memory. It coordinates the 10 Phase 8A source adapters to emit standard `EvidenceDocument` objects, which are then explicitly checked for duplication and target leakage before serialization.
- **`rag/corpus/builder.py`**: Iterates across scenarios and source files. Coordinates memory-efficient streams.
- **`rag/corpus/writer.py`**: Performs real-time serialization, ID tracking (duplicate prevention), and structured leakage audits.
- **`scripts/build_rag_corpus.py`**: CLI orchestrator providing `--small-scale` validations and full corpus generation.

## 2. RAG Document Contract
The serialized representation matches the Phase 7C.2 `EvidenceDocument` schema exactly:
- `document_id`: Deterministic global identifier.
- `scenario_instance_id` & `scenario_family`: Routing logic contexts.
- `source_type` & `source_record_id`: Origin tracing.
- `timestamp`: Event chronology when applicable.
- `normalized_text`: Formatted human-readable deterministic strings mapping observed values exactly.
- `raw_content`: The literal JSON/CSV row from the frozen dataset to ensure zero loss of evidence.
- `entity_refs` & `location_refs`: Observable reference graphs.
- `provenance`: Originating path string tracing back to the `OBSERVED` scenario file.

## 3. Normalization Rules & Source Mappings
Normalization represents data cleaning ONLY in the context of deterministic JSON extraction. Typos, missing fields, and noisy parameters are intentionally preserved exactly as observed. 
- Example: Name variants (`Rahul Sharma` vs `Rahul Sharna`) in CCTNS FIRs are never repaired with ground truth.
- The format concatenates schema keys into English readable phrases (e.g. `FIR {X} registered at {Y} on {Z}. Complainant: {A}. Accused: {B}.`) which is highly resilient and dense for embedding models.

## 4. ID & Provenance Strategy
- **IDs** follow a strict deterministic format ensuring reproducible generation: `{scenario_instance_id}::{source_type}::{source_record_id}`.
- **Provenance** logs the cross-platform normalized (forward-slash) path back to the exact JSON/CSV from which it was extracted (e.g. `output/FINAL_EVALUATION/output/OBSERVED/S01/cctns_fir_records.json`).

## 5. Streaming Strategy
The builder streams files sequentially. Because individual files inside `OBSERVED/{scenario_id}/` are small (max 5-10MB), parsing occurs memory-efficiently per file, yielding a stream of records to the JSONL writer which immediately flushes to disk. This achieved peak generation across 1.139M documents in just ~366 seconds.

## 6. Leakage Protection
Leakage auditing explicitly inspects the *structured* fields (schema keys, provenance paths) for suspicious terms like `ground_truth`, `gold`, `benchmark`, `is_criminal`, and `oracle`. 
- Ordinary terms appearing inside `raw_content` values or `normalized_text` are safely ignored, preventing false positives for innocent evidence (e.g. "Suspect used a gold watch as benchmark.").
- Zero occurrences of structured leakage were detected in the final corpus.

## 7. Full Corpus Generation Statistics
| Metric | Value |
|--------|-------|
| **Total Documents** | 1,159,060 |
| **Output File** | `output/RAG_CORPUS/corpus_full.jsonl` |
| **Processing Time** | 366.55 seconds |
| **Output Size** | 1014.85 MB |

**Source Distribution:**
- `cbs_bank_transactions`: 466,620
- `cctns_fir_records`: 15,000
- `cell_tower_dumps`: 50,000
- `criminal_history_db`: 10,000
- `field_intelligence_notes`: 20,100
- `fiu_str_alerts`: 15,000
- `osint_social_posts`: 25,000
- `telecom_caf_kyc`: 171,330
- `telecom_cdr_logs`: 311,010
- `toll_anpr_logs`: 75,000

## 8. Validation Results
- **Deduplication:** 0 duplicate document IDs detected.
- **Structured Leakage:** 0 violations detected.
- **Missing Data Check:** 0 documents had missing normalized_text, raw_content, or provenance fields.

## 9. Known Limitations
- The RAG corpus is intentionally identical in noise profile to the frozen dataset. OCR and typos remain.
- There is no semantic deduplication. Multiple field notes reflecting the same event remain independent documents in the index.

## 10. Phase 8C Recommendations
- Implement chunking (if necessary) though most documents fall neatly under LLM token limits natively.
- Provision a Qdrant or similar vector database.
- Utilize a standard text embedding model (e.g. sentence-transformers, nomic-embed-text) to index the `normalized_text` fields.
- Append structured filters on `source_type`, `scenario_instance_id`, `timestamp`, and `entity_refs` as vector payload tags to allow hybrid-search queries.
