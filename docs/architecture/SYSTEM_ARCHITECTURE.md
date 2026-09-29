# SIH26190 System Architecture

This document describes the architecture and data flows of the **SIH26190 Secure Digital Document Management System**.

## 1. Overall System Architecture

```mermaid
flowchart LR
    A[Authenticated User] --> B{Authentication & RBAC}
    B -->|Authorized| C[Document Management API]
    C --> D[Case/Document Storage]
    C --> E[SHA-256 Integrity Engine]
    C --> F[Audit Logging Service]
    
    B -->|Authorized| G[Evidence Board]
    G --> C
    
    B -->|Authorized| H[AI / RAG Pipeline]
    H --> I{Permission-Aware Filter}
    I -->|Authorized Context| J[Qdrant Vector Store]
    I -->|Unauthorized| K[Access Denied]
    J --> L[Groq/Qwen LLM]
    L --> M[Grounded AI Answer]
```

## 2. Secure Document Lifecycle

```mermaid
flowchart TD
    U[Upload Document] --> M[Associate Metadata & Case]
    M --> S[Authorized Storage]
    S --> V[Create Version History]
    V --> H[Calculate SHA-256 Hash]
    H --> A[Access & Audit Logged]
    A --> E[Evidence Chain Visualization]
```

## 3. Role-Based Access Control (RBAC)

```mermaid
flowchart TD
    Admin[Admin Role] -->|Global Access| AllCases[All Cases & Documents]
    Admin -->|Full Audit Access| FullAudit[Global Audit Logs]
    
    SO[Senior Officer Role] -->|Assigned Cases| AssignedCases[Case A, B, C]
    SO -->|Full Audit Access| FullAudit
    
    Inv[Investigator Role] -->|Restricted Cases| RestCases[Case A Only]
    Inv -->|Restricted| NoAudit[No Audit Visibility]
```

## 4. Permission-Aware AI/RAG

```mermaid
flowchart TD
    Req[Investigator Query] --> Auth[Case/Document Authorization]
    Auth -->|Check User Permissions| Perms{Authorized?}
    Perms -->|Yes| Ret[Retrieve from Qdrant]
    Perms -->|No| Exclude[Exclude from Context]
    Ret --> Context[Construct Context]
    Context --> LLM[Groq/Qwen LLM]
    LLM --> Answer[Answer with Source Citations]
```

## 5. Evidence Chain

```mermaid
flowchart TD
    V1[Version 1 Uploaded] -->|Timestamp| Chain
    V2[Version 2 Uploaded] -->|Timestamp| Chain
    I1[Integrity Verified: ✓] -->|Current Session| Chain
    A1[Audit: Document Viewed] -->|Timestamp| Chain
    A2[Audit: AI Analyzed] -->|Timestamp| Chain
    Chain((Chronological Evidence Lifecycle View))
```

*Note: The internal Qdrant collection is named `sih26189_evidence` due to prototype legacy compatibility. It contains strictly SIH26190 relevant documents.*
