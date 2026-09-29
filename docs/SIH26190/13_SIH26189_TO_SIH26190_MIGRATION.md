# 13. SIH26189 to SIH26190 Migration

## Context
The project was originally developed for SIH26189 (AI-Powered Criminal Network Analysis System) and was strictly pivoted mid-development to fulfill SIH26190 (Secure Digital Document Management System).

## Migration Table

| SIH26189 Component | → SIH26190 Replacement | → Status | → Reuse Level |
| :--- | :--- | :--- | :--- |
| **Frontend UI** | Focused Document Dashboards | VERIFIED | Low (Complete UI overhaul; generic wrappers kept) |
| **Backend Framework** | FastAPI (No change) | VERIFIED | High (Core router architecture retained) |
| **Database** | SQLite + SQLAlchemy | VERIFIED | High (New schemas injected, connection logic retained) |
| **Qdrant Vector Store** | Qdrant (No change) | VERIFIED | High (Reused entirely, with RBAC filter injected) |
| **RAG Pipeline** | RAG Pipeline (No change) | VERIFIED | High (Adapted to feed off SQLite context) |
| **Security/RBAC** | Strict JWT ACLs | VERIFIED | New (Was virtually non-existent/in-memory before) |
| **Integrity Checks** | SHA-256 Validation | VERIFIED | New (Did not exist in SIH26189) |
| **Audit Ledger** | SQLite `audit_events` | VERIFIED | New (Did not exist in SIH26189) |
| **Network Canvas UI** | *Removed* | DEPRECATED | None |
| **Link Prediction** | *Removed* | DEPRECATED | None |

## Known Deprecated Components
The following SIH26189 components physically remain in the codebase but are structurally orphaned or deprecated in the context of SIH26190:

1. `backend/app/services/network_service.py`: Previously used to build JSON graph nodes for the UI. No longer exposed to users.
2. `backend/app/services/query_understanding.py`: Contains legacy keyword classifiers for `ANPR`, `CDR`, and `Kingpin` logic. They still exist but do not negatively impact the document retrieval fallback.

*(These items were retained purely to prevent breaking downstream modular dependencies during the rapid demo pivot. They are considered non-core and can be safely ignored.)*
