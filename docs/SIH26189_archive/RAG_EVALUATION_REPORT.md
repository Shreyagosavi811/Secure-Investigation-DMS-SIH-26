# RAG Evaluation Report

## 1. Environment
- Qdrant Status: AVAILABLE
- Collection: sih26189_evidence
- Embedding Model: BAAI/bge-m3
- Corpus Mode: small

## 2. Metrics Comparison

| Metric | Keyword | Semantic | Hybrid |
|--------|---------|----------|--------|
| Recall@5 | 0.9 | 0.72 | 0.72 |
| Recall@10 | 0.96 | 0.72 | 0.72 |
| MRR | 0.908 | 0.7 | 0.7 |
| HitRate@10 | 0.96 | 0.72 | 0.72 |
| AvgSourceDiversity | 2.6 | 2.12 | 2.12 |

### Improvements
- **Recall@5**:
  - Hybrid over Keyword: -20.0%
  - Semantic over Keyword: -20.0%
  - Hybrid over Semantic: 0.0%
- **Recall@10**:
  - Hybrid over Keyword: -25.0%
  - Semantic over Keyword: -25.0%
  - Hybrid over Semantic: 0.0%
- **MRR**:
  - Hybrid over Keyword: -22.9%
  - Semantic over Keyword: -22.9%
  - Hybrid over Semantic: 0.0%
- **HitRate@10**:
  - Hybrid over Keyword: -25.0%
  - Semantic over Keyword: -25.0%
  - Hybrid over Semantic: 0.0%
- **AvgSourceDiversity**:
  - Hybrid over Keyword: -18.5%
  - Semantic over Keyword: -18.5%
  - Hybrid over Semantic: 0.0%

## 3. Per-query Failures (Misses)

### Keyword Misses
- **GQ-003**: suspicious money transfers and UPI payments
  - Expected IDs: 1 (R@10: 0.0)

### Semantic Misses
- **GQ-001**: bank transactions involving account 3189
  - Expected IDs: 3 (R@10: 0.0)
- **GQ-003**: suspicious money transfers and UPI payments
  - Expected IDs: 1 (R@10: 0.0)
- **GQ-005**: invoice settlement NEFT transfer
  - Expected IDs: 1 (R@10: 0.0)
- **GQ-012**: cell tower Connaught Place devices logged
  - Expected IDs: 2 (R@10: 0.0)
- **GQ-017**: all records related to account 3189 financial activity
  - Expected IDs: 2 (R@10: 0.0)
- **GQ-022**: informant meeting Noida Sector 18 ATM identities unclear
  - Expected IDs: 1 (R@10: 0.0)
- **GQ-024**: BR-001042 branch banking transactions
  - Expected IDs: 3 (R@10: 0.0)

### Hybrid Misses
- **GQ-001**: bank transactions involving account 3189
  - Expected IDs: 3 (R@10: 0.0)
- **GQ-003**: suspicious money transfers and UPI payments
  - Expected IDs: 1 (R@10: 0.0)
- **GQ-005**: invoice settlement NEFT transfer
  - Expected IDs: 1 (R@10: 0.0)
- **GQ-012**: cell tower Connaught Place devices logged
  - Expected IDs: 2 (R@10: 0.0)
- **GQ-017**: all records related to account 3189 financial activity
  - Expected IDs: 2 (R@10: 0.0)
- **GQ-022**: informant meeting Noida Sector 18 ATM identities unclear
  - Expected IDs: 1 (R@10: 0.0)
- **GQ-024**: BR-001042 branch banking transactions
  - Expected IDs: 3 (R@10: 0.0)

## 4. Conclusion

The RAG architecture is NOT YET PROVEN.
