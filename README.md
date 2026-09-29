# 🎯 OmniGuard DMS – Our SIH 2026 Solution

A secure, case-centric digital evidence platform developed during **Smart India Hackathon 2026** under the problem statement by **Ministry of Home Affairs**, focused on a **Secure Digital Document Management System for Legal and Investigation Documents** (SIH26190).

--- 

## 🚀 Problem Statement

> Develop a Secure Digital Document Management System (DMS) that enables law enforcement agencies, legal institutions, and investigative departments to securely store, organize, manage, retrieve, and share sensitive legal and investigation documents while preserving legal validity and evidentiary integrity.

---

## 👤 Target Users

- Law enforcement agencies (Police)
- Investigative departments (CBI, CID)
- Courts and legal institutions
- Intelligence analysts and forensic teams
- System Administrators / Ministry of Home Affairs

---

## 🧠 Solution Overview

We developed a **Cryptographically-Secured Case Vault**:
- **Role-Based Access Control (RBAC)** to enforce strict, zero-trust data isolation.
- **Interactive Evidence Board** mapping cases visually on an infinite node graph canvas.
- **Permission-Aware RAG (AI)** to semantically search massive charge sheets without data leaks.
- Real-time **SHA-256 Tamper Detection** to intercept and block unauthorized file modifications.

---

## 🧪 Key Innovations (Our Hackathon Edge)

| Feature | Description |
|--------|-------|
| **Evidence Board** | React Flow node graph linking FIRs, suspects, and forensic logs visually. |
| **Tamper Detection** | Instant "Red Alert" lockdown if a physical file hash mismatch is detected. |
| **Secure AI Search** | Qdrant-backed semantic search bounded entirely by the user's Access Control List. |
| **Zero-Trust Audit** | Immutable SQLite ledger tracking every single user action and tampering attempt. |

✅ **Tested on:** 50+ hyper-realistic synthetic Indian cases generated for demo  
📈 **Performance:** High-throughput FastAPI asynchronous backend  
📦 **Deployment:** Fully local-first, on-premise capable design ensuring 100% data sovereignty  

---

## 🛠 Tech Stack

- **Frontend:** React 18, Vite, Tailwind CSS, React Flow, Recharts  
- **Backend:** Python, FastAPI, SQLite, SQLAlchemy ORM  
- **AI & Security:** Qdrant Vector DB, Native `hashlib` SHA-256 Cryptography  

---

## ⚙️ Local Setup & Installation

**1. Start the Secure Backend:**
```bash
cd backend
python -m venv .venv
# Activate: Windows `.\.venv\Scripts\activate` | Mac/Linux `source .venv/bin/activate`
pip install -r requirements.txt
python generate_mass_data.py # Seed realistic cases
uvicorn app.main:app --port 8000
```

**2. Start the Frontend Application:**
```bash
cd frontend
npm install
npm run dev
```
System runs on `http://localhost:5173`.

---

## 🔐 RBAC Demo Accounts

Use these simulated accounts to test permission isolation:
- **Admin:** `admin` / `admin` (Full access & Security Analytics)
- **Investigator:** `investigator` / `inv` (Standard case access & Evidence Board)
- **Guest:** `guest` / `guest` (Restricted read-only)

---
