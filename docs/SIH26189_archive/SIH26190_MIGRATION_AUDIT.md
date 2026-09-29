# SIH26190 Migration Audit

## Overview
This document outlines the migration from the SIH26189 AI-Powered Criminal Network Analysis System to the SIH26190 Secure Digital Document Management System for Legal and Investigation Documents. This is a demo-first migration.

## 1. Frontend
**Classification:** REUSE WITH MODIFICATION

**Why:** The existing React/Vite setup is solid and provides a modern, fast development environment. The core layout components (Sidebar, TopBar) can be reused. However, the existing pages (CrimeTrackerDashboard, SuspectDossiers, InvestigationCanvas) are deeply tied to criminal network analysis and must be removed/replaced.
* **KEEP AS-IS:** Build configuration (`vite.config.js`, `package.json`, Tailwind config), core API client setup.
* **REUSE WITH MODIFICATION:** `App.jsx`, `Layout.jsx`, common UI components, styling base.
* **REPLACE:** All domain-specific pages with `Dashboard`, `Cases`, `Documents`, `Search`, `Audit Trail`, and `Security`.
* **REMOVE / DEPRECATE:** Network visualization, suspect dossiers, CDR analysis UI.

## 2. Backend
**Classification:** REUSE WITH MODIFICATION

**Why:** The FastAPI framework provides a strong foundation. Existing project structure and conventions should be maintained.
* **KEEP AS-IS:** Server config, CORS middleware, environment setup, error handling patterns.
* **REUSE WITH MODIFICATION:** API routing structure. RAG endpoints will need to be wrapped with RBAC.
* **REPLACE:** Existing mock endpoints for network retrieval and entity lookup.
* **REMOVE / DEPRECATE:** Network building services, criminal entity logic.

## 3. Authentication & Security
**Classification:** REPLACE (NEW IMPLEMENTATION)

**Why:** The previous system had minimal/mock authentication. The new requirements demand a strict RBAC system (Investigator, Senior Officer, Admin), authenticated sessions, and backend authorization.
* **NEW:** Simple JWT or session-based demo authentication, role-aware middleware, and an audit trail event logger. 

## 4. RAG / Search System
**Classification:** REUSE WITH MODIFICATION

**Why:** The hybrid retrieval architecture (Vector + Exact) and LLM generation service are valuable and proven. They just need to pivot from "entities/networks" to "documents".
* **KEEP AS-IS:** Vector embedding logic (BGE-M3), LLM calling service (Grok/etc.), re-ranking mechanisms.
* **REUSE WITH MODIFICATION:** Retrieval service must be modified to apply **Permission Filtering BEFORE** handing context to the LLM. 
* **REMOVE / DEPRECATE:** Complex entity expansion and spatial/temporal filters that do not apply to plain documents.

## 5. Investigation Dataset Engine
**Classification:** REMOVE / DEPRECATE

**Why:** The old engine generated massive, complex criminal networks. We only need a small synthetic dataset for the demo (3-5 cases, 20-40 documents). A lightweight seed script will replace this massive generator.

## 6. Architecture & Documentation
**Classification:** REPLACE

**Why:** Old architecture documents detail criminal networks and dataset pipelines. New documents must focus on secure document management, RBAC, integrity hashing, and RAG access control.

## 7. Data Models
**Classification:** REPLACE

**Why:** The old models were Entity/Relationship based. The new models are hierarchical: Case -> Document -> Document Version. 
* **NEW:** Models for `Case`, `Document`, `DocumentVersion` (with SHA-256 hashing for integrity), and `AuditLog`.

## 8. Tests
**Classification:** REUSE WITH MODIFICATION

**Why:** Existing test infrastructure (pytest) should be kept, but the actual test cases must be rewritten to target the new document models, RBAC enforcement, and integrity verification.
