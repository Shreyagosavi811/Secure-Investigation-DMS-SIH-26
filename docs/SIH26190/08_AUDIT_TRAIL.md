# 08. Audit Trail

## Overview
**VERIFIED:** The SIH26190 system implements a backend-enforced immutable ledger to track all critical security events. 

## AuditEvent Model
The `AuditEvent` SQLite model records:
- `timestamp`: UTC time of the event
- `username`: The actor performing the event
- `role`: The role of the actor at the time
- `action`: The category of the event
- `document_id`: (Optional) The specific document involved
- `case_id`: (Optional) The specific case involved
- `version`: (Optional) The specific document version involved
- `result`: Outcome of the event (e.g. `SUCCESS`, `ACCESS_DENIED`)
- `ip_address`: (Optional / Not populated in current demo)

## Tracked Actions
The following events are actively implemented and triggered server-side:
- `LOGIN`: When a user authenticates.
- `VIEW_DOCUMENT`: When a user requests to read a file.
- `VERIFY_INTEGRITY`: When the cryptographic verification endpoint is hit.
- `TAMPER_DETECTED`: A specific result flagged when a verification fails.
- `CREATE_VERSION`: When a new file version is uploaded.
- `UPLOAD_DOCUMENT`: (Legacy action, conceptually merged with CREATE_VERSION).
- `ACCESS_DENIED`: A specific result triggered when a user hits a `403` restriction wall.

*(Note: `DOWNLOAD_DOCUMENT`, `SEARCH`, and `AI_QUERY` are currently NOT explicitly tracked in the Audit table for the P0 demo scope).*

## Role of Audit Logging
In this prototype, the audit log allows Administrators to identify malicious insiders (e.g. an Investigator attempting to access unauthorized cases repeatedly resulting in `ACCESS_DENIED` blocks) or detect physical storage compromise (`TAMPER_DETECTED`). 

> [!CAUTION]
> Do not claim legal-grade immutable logging (e.g., blockchain-based or WORM storage) unless such storage layers are integrated in the future. The current ledger is a standard relational SQL table.
