# 02. System Architecture

## Architecture Overview
SIH26190 is designed with a strictly enforced boundary between the presentation layer and the data layer. Authorization occurs strictly at the backend API layer. 

The architecture guarantees that:
1. Metadata and roles are managed by SQLite (immutable source of truth).
2. Document physical storage relies on the server filesystem.
3. The AI RAG system receives mandatory authorization lists before interacting with Qdrant.

## Diagram
```mermaid
flowchart TD
    subgraph Frontend
        User((User))
        React[React Frontend]
    end

    subgraph Backend API [FastAPI API]
        Auth[Authentication / RBAC]
        Endpoints[API Routes]
    end

    subgraph Database [SQLite]
        Users[(Users)]
        Cases[(Cases)]
        CaseAccess[(CaseAccess)]
        Documents[(Documents)]
        Versions[(DocumentVersions)]
        Audit[(AuditEvents)]
    end

    subgraph Storage [Filesystem Storage]
        Files[Document files]
    end

    subgraph AI Pipeline [RAG Engine]
        Chunking[Chunking / Retrieval]
        Qdrant[(Qdrant)]
        Perms[Permission-aware retrieval]
        Rerank[Reranking]
        LLM[LLM]
        Output[Cited response]
    end

    User --> React
    React --> Auth
    Auth --> Endpoints
    Endpoints --> Database
    Endpoints --> Files
    Endpoints --> Chunking
    
    Chunking --> Qdrant
    Qdrant --> Perms
    Perms --> Rerank
    Rerank --> LLM
    LLM --> Output
```

## Security Boundary
**VERIFIED:** Authorization is strictly enforced in the FastAPI backend via the `require_case_access` and `get_authorized_cases` dependencies. 
Frontend visibility (e.g. hiding a document from the React dashboard) is **not** the security boundary. Direct API calls using an unauthorized JWT will result in a `403 Forbidden` response and an `ACCESS_DENIED` entry in the `AuditEvents` table.
