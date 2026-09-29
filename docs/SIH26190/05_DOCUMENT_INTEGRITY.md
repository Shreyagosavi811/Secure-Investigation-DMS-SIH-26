# 05. Document Integrity

## Overview
**VERIFIED:** SIH26190 detects malicious tampering of physical case files by storing and recalculating cryptographic hashes (SHA-256) of document contents.

## Complete Actual Flow
```mermaid
flowchart TD
    Upload[File upload via API]
    HashCalc1[Backend calculates SHA-256 of bytes]
    DBStore[Store hash in DocumentVersion (SQLite)]
    FSStore[Store file in backend/storage/]
    
    VerifyReq[Verification request: /api/documents/{id}/verify]
    ReadFS[Read physical file from disk]
    HashCalc2[Recalculate SHA-256 of disk file]
    Compare{Compare disk hash to DB hash}
    
    Res1[INTEGRITY_VERIFIED]
    Res2[TAMPER_DETECTED]
    
    Audit[Write AuditEvent]

    Upload --> HashCalc1
    HashCalc1 --> DBStore
    HashCalc1 --> FSStore
    
    VerifyReq --> ReadFS
    ReadFS --> HashCalc2
    HashCalc2 --> Compare
    
    Compare -- Matches --> Res1
    Compare -- Mismatch --> Res2
    
    Res1 --> Audit
    Res2 --> Audit
```

## Storage Mechanisms
- **Files are stored:** On the local filesystem under `backend/storage/{case_id}/{document_id}_v{version}.txt`
- **Hashes are stored:** In the SQLite database `document_versions` table.

## Verification API
Endpoint: `GET /api/documents/{document_id}/verify`
This endpoint reads the file from disk, hashes it on the fly, and matches it against the database. 

## Auditing
Whether the result is `INTEGRITY_VERIFIED` or `TAMPER_DETECTED`, the action is immediately recorded in the `audit_events` ledger with the exact version number tested. 

## Demonstrating Tampering
During the demo, a file in `backend/storage/CASE-2026-001/` is manually altered (e.g., via a text editor). Pressing the "Verify" button on the UI immediately triggers the `TAMPER_DETECTED` warning since the live recalculation no longer matches the immutable SQLite hash. 

## Prototype Scope
> [!WARNING]  
> The current prototype uses cryptographic hash comparison for integrity detection. Do NOT claim that SHA-256 alone provides non-repudiation or a complete digital-signature system (which would require Public Key Infrastructure / PKI).
