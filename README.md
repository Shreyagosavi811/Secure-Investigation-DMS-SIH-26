<div align="center">
  <img src="https://img.shields.io/badge/SIH_2026-Project_SIH26190-orange?style=for-the-badge" alt="SIH 2026" />
  <img src="https://img.shields.io/badge/Status-Hackathon_Ready-success?style=for-the-badge" alt="Status" />
  <img src="https://img.shields.io/badge/Tech-React_Flow%20%7C%20FastAPI-blue?style=for-the-badge" alt="Tech Stack" />
  
  <br />
  <br />

  <h1>🛡️ OmniGuard DMS</h1>
  <p><b>Secure Digital Document Management System for Law Enforcement & Intelligence</b></p>
  <p><i>Developed for the Smart India Hackathon 2026 (Problem Statement: SIH26190)</i></p>
</div>

---

## 📖 Overview
OmniGuard DMS is an enterprise-grade, case-centric digital evidence platform. Built specifically for investigative organizations, it moves beyond basic storage by providing an intelligent **Interactive Evidence Board**, real-time **Cryptographic Tamper Detection**, and absolute **Role-Based Access Control (RBAC)**.

When critical intelligence like FIRs, witness testimonies, or forensic logs are uploaded, OmniGuard ensures they remain untampered, mathematically verified, and strictly isolated on a need-to-know basis.

---

## 🚀 Key Innovation (The "Wow" Factors)

### 1. 🕸️ Interactive Cryptographic Evidence Board
Instead of a standard file explorer, investigators use a **React Flow Node Graph** to visually map out cases. Pinned documents act as interactive nodes on an infinite canvas, with animated cryptographic linkages automatically connecting them back to their central Case File hub.

### 2. 🚨 Real-time SHA-256 Tamper Detection
Every document uploaded is cryptographically hashed. We have built-in a physical **Simulate Cyber Attack** feature for demo purposes:
- Click a button to physically alter the raw file on the hard drive.
- The system instantly triggers a full-screen **Red Alert Modal**, displaying the mismatch between the *Expected Hash* and the *Compromised Hash*, locking down the evidence.

### 3. 📊 Security Analytics Dashboard
A real-time metrics dashboard powered by `Recharts` that provides top-level administrators with instant overviews of total active cases, document loads, and the exact count of intercepted tampering attempts across the agency.

---

## 🛠️ Architecture & Tech Stack

**Frontend (Client)**
- **React 18 + Vite:** Lightning-fast rendering and Hot Module Replacement.
- **Tailwind CSS:** Fully custom "Human Touch" design system featuring glassmorphism and tactile UI.
- **React Flow (`@xyflow/react`):** Advanced physics-based node graph engine for the Evidence Board.

**Backend (Server & Security)**
- **FastAPI (Python):** High-performance, asynchronous REST APIs.
- **SQLite + SQLAlchemy ORM:** Persistent, relational tracking of RBAC, document metadata, and chronological Audit Logs.
- **Cryptography:** Native `hashlib` SHA-256 integrity verification.

---

## ⚙️ Local Setup & Installation

### 1. Start the Secure Backend
```bash
cd backend
python -m venv .venv
.\.venv\Scripts\activate   # (Windows) or source .venv/bin/activate (Mac/Linux)
pip install -r requirements.txt
python generate_mass_data.py # Seed the DB with 50+ realistic Indian cases
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
Login using the following simulated demo accounts to test permission isolation:
- **admin** (Password: *admin*) - Full access to System Analytics and global security logs.
- **investigator** (Password: *inv*) - Standard access to case files and the Evidence Board.
- **guest** (Password: *guest*) - Heavily restricted, read-only access.

---

<div align="center">
  <p><b>Built with ❤️ for the Smart India Hackathon 2026</b></p>
</div>
