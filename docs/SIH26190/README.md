# SIH26190 — Secure Digital Document Management System for Legal and Investigation Documents

## Problem Statement
Secure management of sensitive legal and investigation documents with controlled access, integrity verification, versioning, auditability, search, and document-grounded AI assistance.

## Current Status
**P0 DEMO READY / VERIFIED**

## Documentation Index
- [01 Project Overview](01_PROJECT_OVERVIEW.md)
- [02 System Architecture](02_SYSTEM_ARCHITECTURE.md)
- [03 Database Schema](03_DATABASE_SCHEMA.md)
- [04 Security & RBAC](04_SECURITY_RBAC.md)
- [05 Document Integrity](05_DOCUMENT_INTEGRITY.md)
- [06 Version Control](06_VERSION_CONTROL.md)
- [07 Search and RAG](07_SEARCH_AND_RAG.md)
- [08 Audit Trail](08_AUDIT_TRAIL.md)
- [09 Demo Data](09_DEMO_DATA.md)
- [10 API Reference](10_API_REFERENCE.md)
- [11 Demo Workflow](11_DEMO_WORKFLOW.md)
- [12 Testing and Verification](12_TESTING_AND_VERIFICATION.md)
- [13 SIH26189 to SIH26190 Migration](13_SIH26189_TO_SIH26190_MIGRATION.md)

## Technology Stack

### Frontend
- React
- Vite
- Existing TailwindCSS / Custom UI components (Migrated from SIH26189)

### Backend
- FastAPI
- Python
- SQLAlchemy
- SQLite
- JWT
- bcrypt

### Storage
- **Filesystem**: Document storage (`backend/storage/`)
- **SQLite**: Metadata, relationships, roles, and audit trails (`backend/sih26190.db`)
- **Qdrant**: Vector storage for semantic retrieval

### AI/RAG
- Existing retrieval architecture adapted for document retrieval
- **VERIFIED:** Actual embedding mechanism currently uses a deterministic MockEncoder fallback due to local disk space limitations (preventing `sentence-transformers` installation). The retrieval pipeline successfully interfaces natively with Qdrant storage despite this local fallback.

### Testing
- Automated E2E verification (`verify_e2e.py`)
- Focused security/integrity tests (tampering, access denial, DB hash validation) actually present and verified.
