# 01. Project Overview

## 1. Problem
Managing sensitive legal and investigation documents requires strict security, proof of integrity, and heavily restricted access. General-purpose AI tools or unsecured file systems expose these documents to data leaks, tampering, and unauthorized viewing.

## 2. SIH26190 Objective
To build a Secure Digital Document Management System designed explicitly for legal and investigation teams, ensuring that document access is heavily guarded, tampered files are detected cryptographically, and AI assistance is strictly bound by the user's role.

## 3. Proposed Solution
A secure, role-based document vault using SQLite for immutable audit and metadata tracking, a local filesystem for artifact storage with active SHA-256 integrity verification, and a Qdrant-backed Retrieval-Augmented Generation (RAG) system protected by mandatory Access Control Lists (ACLs) to prevent data spillage.

## 4. Core Demo Capabilities
- **Authentication**: VERIFIED
- **RBAC (Role-Based Access Control)**: VERIFIED
- **Case Management**: VERIFIED
- **Document Management**: VERIFIED
- **Document Versioning**: VERIFIED
- **SHA-256 Integrity Verification**: VERIFIED
- **Tamper Detection**: VERIFIED
- **Search**: VERIFIED
- **Permission-Aware RAG**: VERIFIED
- **Citations**: VERIFIED
- **Audit Trail**: VERIFIED

## 5. Target Users
- **Admin**: Full system visibility, audit oversight.
- **Senior Officer**: Broad case visibility across multiple jurisdictions.
- **Investigator**: Restricted visibility limited only to their assigned cases.

## 6. Security Goals
1. Ensure users cannot read documents they do not own.
2. Ensure the LLM AI cannot ingest or summarize documents the user does not own.
3. Ensure that if a malicious actor modifies a physical document on the server, the system alerts investigators to the tampering.

## 7. AI/RAG Role
The AI operates as a secure assistant to quickly summarize case files, answer questions about evidence, and locate references across massive documents. However, it operates strictly *downstream* of the authorization layer. It only "sees" what the user is legally allowed to see.

## 8. Demo Limitations
> [!IMPORTANT]
> This is a synthetic hackathon prototype and does not connect to real police/government databases.
> The AI retrieval embeddings currently fallback to a deterministic mock generator due to disk space constraints, though the architecture natively supports heavy embedding models.
