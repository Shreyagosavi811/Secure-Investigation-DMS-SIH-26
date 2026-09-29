# SIH26189 Master Dataset Generation Architecture

## Executive Summary

This project defines the complete dataset generation architecture, schemas, noise models, ground-truth graph, validation rules, and prompt engineering pipeline for **SIH26189: AI-Powered Criminal Investigation & Intelligence-Analysis System**.

---

## 1. Overall System Architecture
- **Graph-First Synthetic Data Engineering Pipeline (GF-SDEP)**
- $G_{gt} = (V, E, W, T)$ (Hidden canonical ground truth)
- $R_{obs} = \left( \bigcup_{s \in S} \pi_s(G_{gt}) \right) \cup R_{noise}$ (Observed record layer across 10 sources)

```text
+-------------------------------------------------------------------------+
|                  1. SCENARIO & GRAPH TOPOLOGY ENGINE                    |
|       Generates multi-hop network graphs with hidden connections        |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                2. TEMPORAL & ATTRIBUTE BINDING ENGINE                   |
|   Attaches timestamps, geolocations, names, IPC sections, identifiers  |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                 3. NOISE & DISTRACTOR INJECTION ENGINE                  |
|    Injects spatial overlap, name collisions, typos, stale numbers       |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                  4. FACETED SOURCE RECORD SERIALIZER                    |
|   Transforms graph nodes/edges into 10 fragmented, realistic databases  |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|                5. CONSISTENCY & ANTI-LEAKAGE AUDITOR                    |
|  Validates physical limits, speed, temporal causality, label leakage    |
+-------------------------------------------------------------------------+
                                     |
                                     v
+-------------------------------------------------------------------------+
|              6. INVESTIGATION QUERY & BENCHMARK EXPORTER                |
|     Outputs multi-source record files + hidden ground truth + Q&A pairs |
+-------------------------------------------------------------------------+
```

---

## 2. Entity Schema (12 Canonical Entities)
- `PERSON`: Full name, aliases, DOB, Aadhaar hash, PAN, father's name, address.
- `FIR_CASE`: FIR number, police station, district, state, IPC sections, incident date, complaint text.
- `PHONE`: MSISDN, IMEI, IMSI, carrier, activation date.
- `VEHICLE`: Reg number, chassis no, engine no, make/model, owner entity.
- `ACCOUNT`: Account number, bank name, IFSC, account type, CIF.
- `TRANSACTION`: Txn UTR, debit acc, credit acc, amount, timestamp, channel, remarks.
- `LOCATION`: Location name, type, lat/long, cell LAC/CID, address.
- `ORGANIZATION`: Company name, CIN, GSTIN, type, address.
- `SOCIAL_ACCOUNT`: Platform, handle, linked phone/email.
- `EVENT`: Event type, start/end timestamp, location ID, summary.
- `EVIDENCE`: Evidence type, seizure date, officer, hash.
- `COMMUNICATION`: Caller MSISDN, receiver MSISDN, call type, timestamp, duration, cell ID.

---

## 3. Source-Record Schemas (10 Fragmented Databases)
1. `cctns_fir_records.json` (CCTNS FIRs)
2. `criminal_history_db.json` (Prior Criminal History & MO)
3. `telecom_cdr_logs.csv` (Cellular CDR Call Detail Records)
4. `telecom_caf_kyc.json` (Subscriber CAF KYC Records)
5. `cbs_bank_transactions.csv` (Core Banking Ledger)
6. `fiu_str_alerts.json` (FIU Suspicious Transaction Reports)
7. `toll_anpr_logs.csv` (Highway ANPR Toll Cameras)
8. `cell_tower_dumps.json` (Cell Tower Dumps at Crime Scenes)
9. `osint_social_posts.json` (OSINT Social Media Chatter)
10. `field_intelligence_notes.txt` (Surveillance Notes & Daily Diary entries)

---

## 4. Hidden Ground Truth Schema (`ground_truth_manifest.json`)
- Graph Node Manifest with canonical entity IDs & roles (`MASTERMIND`, `MULE`, `SPOTTER`).
- Graph Edge Manifest with relationship types, evidence record paths, temporal validity, and confidence scores.
- Chronological Master Timeline of all physical and digital events.

---

## 5. Controlled Noise Strategy
1. **Spatial Overlap Noise**: High-density cell tower / toll plaza logs of uninvolved commuters.
2. **Identity Collisions**: Common Indian names ("Rajesh Kumar", "Amit Sharma").
3. **Data Entry / OCR Errors**: Digit transpositions in plate numbers (`MH02AB1234` vs `1243`).
4. **Recycled Telecom Numbers**: Numbers reassigned after 90 days of inactivity.
5. **Benign Financial Noise**: Surround micro-layering with legitimate payroll & UPI payments.
6. **Distractor Subgraphs**: Parallel benign convoys/events mirroring suspect movements.

---

## 6. 10 Core Investigation Scenarios
1. Person-Centric Investigation
2. FIR-Centric Getaway Vehicle Tracking
3. Phone-Centric Co-location & IMEI Swapping
4. Financial-Network Multi-Tier Layering
5. Vehicle Cloned Plate Detection
6. Location Cell Tower Dump Noise Filtering
7. Multi-Hop Criminal Syndicate (4-hop link)
8. Cross-Case Relationship Linkage Across Districts
9. 72-Hour Minute-by-Minute Timeline Reconstruction
10. False-Positive Discrimination (Taxi Driver vs Co-conspirator)

---

## 7. Investigation Query & Expected Answer Schema
- Query Schema: `query_id`, `scenario_id`, `query_type`, `starting_entity`, `search_parameters`, `investigation_prompt`.
- Expected Answer Schema: `query_id`, `target_primary_suspect`, `key_entities_in_chain`, `relationship_graph`, `chronological_timeline`, `intelligence_summary`, `expected_confidence_score`.

---

## 8. Data Generation Pipeline & Validation Rules
- Pipeline: 6-Stage modular execution engine.
- Validation Rules: Spatial Speed Constraint ($\le 120$ km/h), Temporal Causality, Financial Balance, Physical Co-location, Evidence Reachability.

---

## 9. Recommended Dataset Sizes
- **MVP**: 5 Scenarios, ~50 GT Entities, ~2,000 Records (~10MB)
- **Demo**: 25 Scenarios, ~350 GT Entities, ~25,000 Records (~150MB)
- **Final Evaluation**: 100 Scenarios, ~2,500 GT Entities, ~500,000 Records (~2.5GB)

---

## 10. Multi-Stage Controlled Prompt Architecture
- Stage 1: Topology Prompt ($G_{gt}$ JSON graph)
- Stage 2: Demographic Binding Prompt (Indian demography & legal sections)
- Stage 3: Serializer Narrative Prompt (CCTNS FIR summaries without label leakage)
- Stage 4: Automated Verification & Repair Prompt (Rule audit loop)
