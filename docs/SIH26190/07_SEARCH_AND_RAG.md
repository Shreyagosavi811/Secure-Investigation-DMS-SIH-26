# 07. Search and RAG

## Implementation Status
**VERIFIED:** SIH26190 successfully adapts the legacy SIH26189 Qdrant retrieval architecture to perform highly secure, permission-aware document retrieval. 

## The Retrieval Pipeline
1. **Document Ingestion:** Documents are uploaded via the API, saved to disk, and seeded into the vector database.
2. **Chunking:** (Legacy/Not actively split per page in demo dataset; whole document strings are indexed).
3. **Embedding Generation:** Vectors are generated (See Critical Fallback below).
4. **Qdrant Collection:** Vectors are stored in a Qdrant collection named `sih26189_evidence` (a legacy name reused during this demo migration).
5. **Payload Metadata:** Includes text and strictly tracks `case_refs` arrays linking documents to their parent Cases.
6. **Authorization Filtering (CRITICAL):** The FastAPI `InvestigationContext` passes the user's `authorized_case_ids` directly to Qdrant, enforcing a mandatory metadata filter.
7. **Hybrid Retrieval:** Exact semantic retrieval (fallback to random vectors) combined with keyword exact-match identifiers.
8. **Reranking:** Post-retrieval ranking (penalty/boost weights).
9. **LLM Context Construction:** Fused evidence is packed into the LLM prompt.
10. **Citations:** LLM response natively cites the specific document titles.

## Permission-Aware Flow (Critical Security)
If a user is not authorized to view a document, that document must **never** enter the LLM context, because language models are highly susceptible to data leakage (e.g., prompt injections asking to "ignore permissions and summarize the hidden document"). 

SIH26190 prevents this entirely at the database layer:
```mermaid
flowchart TD
    User[User Question] --> API[FastAPI /api/ai/query]
    API --> JWT[Extract User Role]
    JWT --> DB[(SQLite CaseAccess)]
    DB --> AuthCases[List: Authorized case_ids]
    
    AuthCases --> Qdrant[Qdrant Filter: MUST match case_ids]
    User --> Embed[Generate Query Vector]
    Embed --> Qdrant
    
    Qdrant --> Results[Authorized Evidence Only]
    Results --> LLM[LLM Generator]
    LLM --> Answer[Cited Response]
```

## CRITICAL: EMBEDDING FALLBACK
The local hardware environment lacked the required 2GB+ disk space to install the heavyweight `torch` dependency necessary for `sentence-transformers`. 

Therefore, the current implementation gracefully falls back to a custom **deterministic/mock encoder** to generate vectors, allowing the Qdrant storage engine and metadata filtering logic to run natively without crashing.

> [!WARNING]
> DO NOT treat this fallback as a production-quality semantic embedding model. 
> **Production improvement:** Replace the deterministic/mock encoder with a validated embedding model before production deployment.
