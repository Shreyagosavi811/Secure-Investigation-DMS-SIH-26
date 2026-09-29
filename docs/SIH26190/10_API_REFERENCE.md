# 10. API Reference

## Implementation Note
**VERIFIED:** The following endpoints reflect the actual FastAPI routers implemented in the SIH26190 backend. No planned or theoretical endpoints are listed.

---

### Authentication

**METHOD:** `POST`  
**PATH:** `/api/auth/login`  
**AUTHENTICATION:** None  
**ROLE/PERMISSION:** Public  
**REQUEST:** `OAuth2PasswordRequestForm` (username, password)  
**RESPONSE:** `{ "access_token": string, "token_type": "bearer", "role": string, "full_name": string }`  
**PURPOSE:** Validates credentials against bcrypt hashes and issues a JWT.

---

### Cases

**METHOD:** `GET`  
**PATH:** `/api/cases/`  
**AUTHENTICATION:** JWT Required  
**ROLE/PERMISSION:** Any authenticated user  
**RESPONSE:** `{ "cases": [ { case_id, title, description, classification, status } ] }`  
**PURPOSE:** Returns only the cases the user is authorized to view (derived via `CaseAccess`).

**METHOD:** `GET`  
**PATH:** `/api/cases/{case_id}`  
**AUTHENTICATION:** JWT Required  
**ROLE/PERMISSION:** User must be mapped to `case_id` in `CaseAccess` (Admins bypass).  
**RESPONSE:** Case details + List of nested document IDs.  
**PURPOSE:** Fetch specific case details. Triggers `403` if unauthorized.

---

### Documents & Versions

**METHOD:** `GET`  
**PATH:** `/api/documents/{document_id}`  
**AUTHENTICATION:** JWT Required  
**ROLE/PERMISSION:** User must have access to the parent `case_id`.  
**RESPONSE:** Document metadata + array of historical `versions` (including `sha256_hash`).  
**PURPOSE:** View document history and details.

**METHOD:** `POST`  
**PATH:** `/api/documents/{document_id}/versions`  
**AUTHENTICATION:** JWT Required  
**ROLE/PERMISSION:** User must have access to the parent `case_id`.  
**REQUEST:** `multipart/form-data` (file)  
**RESPONSE:** `{ "status": "SUCCESS", "version_id": string, "version_number": int }`  
**PURPOSE:** Uploads a physical file, calculates its SHA-256 hash, and immutably appends it as the newest version of the document.

---

### Integrity Verification

**METHOD:** `GET`  
**PATH:** `/api/documents/{document_id}/verify`  
**AUTHENTICATION:** JWT Required  
**ROLE/PERMISSION:** User must have access to the parent `case_id`.  
**RESPONSE:** `{ "status": "INTEGRITY_VERIFIED" | "TAMPER_DETECTED", "expected_hash": string, "actual_hash": string, "version_number": int }`  
**PURPOSE:** Physically reads the file from disk, recalculates the hash, and compares it to the database to detect tampering.

---

### Audit

**METHOD:** `GET`  
**PATH:** `/api/audit/`  
**AUTHENTICATION:** JWT Required  
**ROLE/PERMISSION:** `Admin` only.  
**RESPONSE:** Array of `AuditEvent` objects.  
**PURPOSE:** Retrieves the global immutable ledger of all system security events.

---

### AI / RAG

**METHOD:** `POST`  
**PATH:** `/api/ai/query`  
**AUTHENTICATION:** JWT Required  
**ROLE/PERMISSION:** Any authenticated user (Results are tightly filtered by authorized cases).  
**REQUEST:** `{ "query": string }`  
**RESPONSE:** `{ "status": string, "llm_response": { "answer": string, "citations": [] } ... }`  
**PURPOSE:** Executes a Permission-Aware RAG pipeline against Qdrant and the LLM strictly using authorized context.
