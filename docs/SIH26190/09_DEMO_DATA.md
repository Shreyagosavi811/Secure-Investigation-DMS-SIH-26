# 09. Demo Data

## Current Target / Verified State
The database is systematically seeded using `backend/scripts/seed_demo_data.py`. All numbers below have been physically verified against the runtime.

- **3** Users
- **4** Cases
- **28** Documents (7 per case)
- **28** Initial Document Versions
- **28** Qdrant Vectors

## Demo Roles & Case Visibility
1. **Admin** (`admin` / `admin123`)
   - **Visibility:** All cases (`CASE-2026-001`, `002`, `003`, `004`).
   - **Privilege:** Full Audit Trail access.
2. **Senior Officer** (`officer` / `officer123`)
   - **Visibility:** All cases (`CASE-2026-001`, `002`, `003`, `004`).
   - **Privilege:** No Audit Trail access.
3. **Investigator** (`investigator` / `investigator123`)
   - **Visibility:** Restricted to `CASE-2026-001` and `CASE-2026-002`.
   - **Privilege:** Explicitly blocked from `CASE-2026-003` and `CASE-2026-004`.

## Synthetic Document Types
Documents simulate standard law enforcement/legal files (e.g., "Investigation Report", "FIR").
All physical `.txt` files corresponding to these documents are dynamically generated and placed in `backend/storage/{case_id}/` during the seed process, with real SHA-256 hashes computed on the fly.

> [!IMPORTANT]
> All demo data is strictly synthetic. No real investigation records, personally identifiable information (PII), or live government datasets are used in this system.
