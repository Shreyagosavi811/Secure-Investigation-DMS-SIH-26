# 04. Security & RBAC

## Security Boundary
**VERIFIED:** The true security boundary is the backend API logic via FastAPI dependencies. Frontend element hiding (React) is purely for UX.

## Authentication Flow
1. **Login:** User submits credentials to `POST /api/auth/login`.
2. **Password Verification:** The backend compares the input to the `bcrypt` hashed password stored in SQLite.
3. **JWT:** A JSON Web Token (JWT) is issued with the user's role encoded, valid for 24 hours.
4. **Authenticated Request:** The React frontend attaches the JWT in the `Authorization: Bearer <token>` header for all subsequent API calls.
5. **Role/Case Authorization:** The API intercepts the request using `get_current_user` and `require_case_access` dependencies, queries SQLite to verify if the user possesses an active `CaseAccess` record for the requested resource.
6. **Resource Access:** The operation succeeds (`200 OK`) or fails (`403 Forbidden`).

## Roles & Actual Permissions

### Admin
- **Permissions:** Unrestricted access. Bypasses `CaseAccess` table logic (hardcoded in `require_case_access` to return `True` for Admin).
- **Audit Access:** Only the Admin can view the global `AuditTrail`.

### Senior Officer
- **Permissions:** Configurable access. In the demo dataset, the Senior Officer is explicitly granted access to all 4 cases via `CaseAccess` records.

### Investigator
- **Permissions:** Highly restricted. In the demo dataset, they are granted access strictly to `CASE-2026-001` and `CASE-2026-002`. Attempting to request `CASE-2026-004` (even directly via API) results in `403 FORBIDDEN`.

## Example Enforcement
- **AUTHORIZED:** Investigator requests `GET /api/documents/DOC-001-001`. The backend confirms `CaseAccess` exists for `CASE-2026-001` -> returns `200 OK`.
- **403 FORBIDDEN:** Investigator requests `GET /api/documents/DOC-004-001`. The backend observes no `CaseAccess` mapping -> returns `403 Forbidden` -> creates `ACCESS_DENIED` Audit Event.

## Enterprise Notice
This is a hackathon prototype. While `bcrypt` and JWTs are standard, the system does not claim enterprise-grade identity management (e.g., OAuth2 integration, SSO, MFA).
