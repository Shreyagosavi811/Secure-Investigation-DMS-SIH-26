<div align="center">
  
  <h1>🛡️ OmniGuard DMS</h1>
  <p><b>Secure Digital Document Management System for Law Enforcement & Intelligence</b></p>
  <p><i>Developed for the Ministry of Home Affairs | Smart India Hackathon 2026 (Problem Statement: SIH26190)</i></p>
</div>

---

## 📖 Overview
OmniGuard DMS is an enterprise-grade, case-centric digital evidence platform engineered specifically to solve the SIH26190 problem statement. Moving beyond basic digitized storage, OmniGuard provides an intelligent **Interactive Evidence Board**, real-time **Cryptographic Tamper Detection**, and absolute **Role-Based Access Control (RBAC)**.

When critical intelligence (FIRs, witness testimonies, forensic logs) is uploaded, OmniGuard ensures the data remains untampered, mathematically verified, and strictly isolated on a need-to-know basis.

---

## 🚀 Key Innovations

Generic document management systems simply upload files to a cloud. OmniGuard is built to solve the specific workflow pain points of real investigative units:

### 1. 🕸️ Interactive Cryptographic Evidence Board
Instead of a traditional, inefficient file explorer, investigators use a **React Flow Node Graph** to visually map out cases. Pinned documents act as interactive nodes on an infinite canvas, with animated cryptographic linkages automatically connecting them back to their central Case File hub. This radically streamlines collaboration and evidence tracking.

### 2. 🚨 Real-Time SHA-256 Tamper Detection (Physical Integrity)
Legal documents require strict evidentiary validity. Every document is cryptographically hashed upon upload. 
* **Live Demo Feature:** We built a "Simulate Cyber Attack" button that actively alters the physical file on the hard drive. OmniGuard immediately intercepts this, flashing a full-screen **Red Alert Modal** displaying the hash mismatch and instantly locking down the compromised evidence.

### 3. 🧠 Permission-Aware RAG (AI Document Search)
To solve the difficulty of locating documents quickly, we integrated a **Retrieval-Augmented Generation (RAG)** pipeline backed by Qdrant. Unlike standard AI, our RAG operates strictly *downstream* of the authorization layer—it is mathematically impossible for the AI to retrieve or summarize documents the user does not have explicit clearance to see.

### 4. 📊 Security Analytics & Zero-Trust Audit Trail
Top-level administrators receive instant overviews of total active cases, document loads, and the exact count of intercepted tampering attempts. Every user action is logged in an immutable, chronological database for full regulatory compliance.

---

## 🛠️ Architecture & Tech Stack

OmniGuard is designed as a **local-first, on-premise capable** system to ensure 100% uptime and data sovereignty for sensitive government data, even if internet connectivity drops.

### Frontend Application
| Technology | Purpose |
| :--- | :--- |
| **React 18 + Vite** | Provides lightning-fast rendering and an optimized build pipeline. |
| **Tailwind CSS** | Implements a custom "Human Touch" glassmorphism design system for a premium UI. |
| **React Flow** | Powers the advanced physics-based node graph engine for the Interactive Evidence Board. |
| **Recharts** | Delivers real-time, interactive security analytics dashboards for administrators. |

### Backend Server & Security
| Technology | Purpose |
| :--- | :--- |
| **FastAPI (Python)** | High-performance, asynchronous REST APIs capable of handling production-scale throughput. |
| **SQLite + SQLAlchemy** | Persistent tracking of RBAC and chronological audit logs (instantly swappable to PostgreSQL). |
| **Qdrant Vector DB** | Facilitates scalable, lightning-fast semantic AI search across massive case files. |
| **Cryptography** | Utilizes native `hashlib` SHA-256 for real-time evidentiary integrity and tamper detection. |

---

## ⚙️ Local Setup & Installation

Because real police data is highly classified, we built a custom synthetic generation engine to seed hyper-realistic Indian case data for demo testing.

### 1. Start the Secure Backend
```bash
cd backend
python -m venv .venv
# Activate virtual environment:
# Windows: .\.venv\Scripts\activate
# Mac/Linux: source .venv/bin/activate

pip install -r requirements.txt

# Seed the DB with 50+ localized, realistic cases and mock files
python generate_mass_data.py 

# Launch the FastAPI Server
uvicorn app.main:app --port 8000
```

### 2. Start the Frontend Application
```bash
cd frontend
npm install
npm run dev
```

The system will now be running on `http://localhost:5173`.

---

## 🔐 Role-Based Access Control (RBAC)
Login using the following simulated demo accounts to test absolute permission isolation:
- **admin** (Password: *admin*) - Full access to System Analytics, Audit Logs, and Global Security.
- **investigator** (Password: *inv*) - Standard access to assigned case files, Evidence Board, and restricted RAG.
- **guest** (Password: *guest*) - Heavily restricted, read-only access.

---

<div align="center">
  <p><b>OmniGuard DMS &copy; 2026</b></p>
</div>
