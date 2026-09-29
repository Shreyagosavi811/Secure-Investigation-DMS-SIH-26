# 06. Version Control

## Implementation Status
**VERIFIED:** SIH26190 implements an immutable, append-only version control system for documents.

## Version Structure
```text
Document (e.g. DOC-001-001)
├── Version 1 (v1: Uploaded by Admin, original hash)
├── Version 2 (v2: Uploaded by Officer, new hash)
└── Version 3 (v3: Current active version)
```

## Actual Implementation Mechanics
1. **Creation Endpoint:** `POST /api/documents/{document_id}/versions`
2. **Behavior:** Uploading a new file generates a strictly incremented `version_number`. 
3. **Storage:** The physical file is saved as `{document_id}_v{number}.txt`. Overwriting previous files is mechanically impossible.
4. **Hashing:** A distinct `sha256_hash` is calculated and bound immutably to the new version in SQLite.
5. **Metadata:** Tracks the exact `created_by` (Username) and a `change_description` (default: Uploaded filename).
6. **Integrity:** The hash of Version 1 remains completely unchanged and verifiable, even after Version 2 is published. 

## Supported vs Unsupported
- **Supported:** Viewing version history, uploading new versions, verifying the integrity of the *current* (latest) version.
- **NOT IMPLEMENTED:** Branching, merging, or explicitly reverting the active pointer to an older version (though older versions exist safely on disk).
