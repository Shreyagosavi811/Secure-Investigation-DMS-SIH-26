# 11. Demo Workflow

## Overview
This is the official 5–7 minute demo sequence designed to showcase the complete feature set of SIH26190 to judges, focusing on security, integrity, and AI capabilities.

---

### Step 1: Login
- **Presenter Action:** Logs in as `investigator123` via the authentication screen.
- **Judge Sees:** The dashboard immediately loads, heavily restricted to only two cases.
- **Demonstrates:** Secure JWT authentication and RBAC initialization.

### Step 2: Dashboard
- **Presenter Action:** Explains the case list constraint. 
- **Judge Sees:** `CASE-2026-001` and `CASE-2026-002` are the only cases visible.
- **Demonstrates:** The backend API actively filtering records based on the SQLite `CaseAccess` mappings.

### Step 3: Open Case
- **Presenter Action:** Clicks into `CASE-2026-001`.
- **Judge Sees:** The case view opens, revealing a list of 7 nested documents (e.g., FIRs, Investigation Reports).
- **Demonstrates:** Hierarchical data navigation.

### Step 4: Open Document & Show Metadata
- **Presenter Action:** Clicks to open `DOC-001-001` and points out the metadata panel.
- **Judge Sees:** Document attributes, creator, classification (`CONFIDENTIAL`), and current file version.
- **Demonstrates:** Granular metadata tracking.

### Step 5: Verify Integrity
- **Presenter Action:** Clicks the "Verify Integrity" button on the document viewer.
- **Judge Sees:** The system quickly responds with a green `INTEGRITY_VERIFIED` badge.
- **Demonstrates:** The backend physically reading the disk file, recalculating the SHA-256 hash, and verifying it against the immutable DB hash.

### Step 6: Show Version History
- **Presenter Action:** Opens the version history panel.
- **Judge Sees:** A chronologically ordered list of immutable versions, each with its own timestamp and distinct SHA-256 hash.
- **Demonstrates:** Append-only version control.

### Step 7: Search & Ask AI Question
- **Presenter Action:** Opens the Floating AI Assistant and asks: *"Summarize the forensic findings in CASE-2026-001."*
- **Judge Sees:** The AI processes the query and returns a structured response.
- **Demonstrates:** The hybrid retrieval engine pulling semantic and exact-match vectors from Qdrant.

### Step 8: Show Cited Sources
- **Presenter Action:** Expands the evidence/citations attached to the AI response.
- **Judge Sees:** Exact document IDs and titles from the current case directly referenced by the LLM.
- **Demonstrates:** Document-grounded RAG (Anti-hallucination).

### Step 9: Attempt Unauthorized Access & Show 403
- **Presenter Action:** Explains they will now try to hack the system by manually forcing the API to fetch a restricted document (e.g., typing `/api/documents/DOC-004-001` or restricted case URL).
- **Judge Sees:** A hard `403 Forbidden` / Access Denied error.
- **Demonstrates:** Frontend visibility is not the security boundary; the backend strictly guards the API.

### Step 10: Open Audit Trail
- **Presenter Action:** Logs out, logs back in as `admin123`, and opens the Audit Trail dashboard.
- **Judge Sees:** A global ledger of events, explicitly highlighting the Investigator's recent `ACCESS_DENIED` violation.
- **Demonstrates:** Immutable accountability and surveillance of system actors.

### Step 11: Modify a Demo File
- **Presenter Action:** Opens the project backend folder (`backend/storage/CASE-2026-001/DOC-001-001_v1.txt`) and manually types "TAMPERED" into the text file.
- **Judge Sees:** Physical modification of the server's storage outside the application.
- **Demonstrates:** Simulating an insider threat or storage compromise.

### Step 12: Show TAMPER DETECTED
- **Presenter Action:** Returns to the UI and clicks "Verify Integrity" on that document again.
- **Judge Sees:** A red `TAMPER_DETECTED` alert instantly appears.
- **Demonstrates:** Cryptographic hash mismatches catching unauthorized physical alterations.

### Step 13: Restore File & Verify
- **Presenter Action:** Reverts the text file back to its original state and verifies again.
- **Judge Sees:** The badge returns to `INTEGRITY_VERIFIED`.
- **Demonstrates:** Hash consistency.
