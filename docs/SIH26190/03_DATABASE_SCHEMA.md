# 03. Database Schema

## Implementation Note
**VERIFIED:** The schema documented below matches the exact SQLAlchemy implementation in `backend/app/models.py`.

## Entity-Relationship Diagram
```mermaid
erDiagram
    USERS ||--o{ CASE_ACCESS : "has"
    USERS {
        Integer id PK
        String username "unique, index"
        String hashed_password
        String role "Admin, Senior Officer, Investigator"
        String full_name
    }

    CASES ||--o{ DOCUMENTS : "contains"
    CASES ||--o{ CASE_ACCESS : "assigned to"
    CASES {
        String case_id PK "e.g. CASE-2026-001"
        String title
        Text description
        String classification
        String status
        DateTime created_at
    }

    DOCUMENTS ||--o{ DOCUMENT_VERSIONS : "tracks"
    DOCUMENTS {
        String document_id PK
        String case_id FK
        String title
        String document_type
        String classification
        String owner
        String uploaded_by
        DateTime created_at
        DateTime updated_at
    }

    DOCUMENT_VERSIONS {
        String version_id PK
        String document_id FK
        Integer version_number
        String file_path
        String sha256_hash
        String created_by
        DateTime created_at
        Text change_description
    }

    CASE_ACCESS {
        Integer id PK
        Integer user_id FK
        String case_id FK
    }

    AUDIT_EVENTS {
        Integer id PK
        DateTime timestamp
        String username
        String role
        String action "VIEW_DOCUMENT, LOGIN, SEARCH, etc."
        String document_id "nullable"
        String case_id "nullable"
        Integer version "nullable"
        String result "SUCCESS, ACCESS_DENIED, INTEGRITY_VERIFIED, TAMPER_DETECTED"
        String ip_address "nullable"
    }
```

## Tables Explained

### User
Tracks system actors. Passwords are mathematically hashed with bcrypt. 

### Case
The primary container for documents. Authorization is granted at the Case level.

### CaseAccess
The mapping table granting specific Users access to specific Cases.

### Document
The logical representation of a file. It acts as an umbrella for its physical versions.

### DocumentVersion
The immutable representation of a physical file at a point in time. It stores the exact `sha256_hash` used for tamper detection and the `file_path` on the storage drive.

### AuditEvent
An immutable ledger tracking every significant action performed in the system, specifically recording `ACCESS_DENIED` and `TAMPER_DETECTED` events for security review.
