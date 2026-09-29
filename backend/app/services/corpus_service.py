"""
corpus_service.py

Corpus service for loading and querying the investigation corpus.
Supports CORPUS_MODE=small (default, 100 records) or CORPUS_MODE=full.

Design: Corpus is loaded once into memory at startup. For the small corpus
(100 records, ~96KB), this is perfectly fine. For the full corpus (1GB+),
Qdrant vector retrieval is used instead — this service is only the fallback.
"""

import os
import json
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class CorpusService:
    _instance = None
    _records: List[Dict[str, Any]] = []
    _corpus_mode: str = "small"
    _corpus_path: str = ""

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CorpusService, cls).__new__(cls)
            cls._instance._loaded = False
        return cls._instance

    def _load_corpus(self):
        if self._loaded:
            return

        self._loaded = True
        self._corpus_mode = os.environ.get("CORPUS_MODE", "small").lower()

        # Calculate path dynamically
        base_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(base_dir, "../../../"))

        if self._corpus_mode == "full":
            filename = "corpus_full.jsonl"
        else:
            filename = "corpus_small.jsonl"

        corpus_path = os.path.join(
            project_root,
            "investigation_dataset_engine",
            "output",
            "RAG_CORPUS",
            filename
        )

        # Allow override via env
        env_corpus = os.environ.get("CORPUS_PATH", "")
        if env_corpus:
            corpus_path = env_corpus

        self._corpus_path = corpus_path

        if not os.path.exists(corpus_path):
            raise RuntimeError(
                f"Corpus file missing at {corpus_path}. "
                f"Set CORPUS_MODE=small to use the small corpus or "
                f"CORPUS_PATH to specify a custom path."
            )

        logger.info("Loading corpus from %s (mode=%s)", corpus_path, self._corpus_mode)

        count = 0
        with open(corpus_path, "r", encoding="utf-8") as f:
            for line in f:
                if not line.strip():
                    continue
                record = json.loads(line)

                # Guardrail: Never load ground truth
                if "GROUND_TRUTH" in record.get("provenance", {}).get("source_path", ""):
                    raise RuntimeError("Data leakage error: GROUND_TRUTH record detected.")

                # Sanitize provenance paths (keep only filename, not full path)
                if "provenance" in record and "source_path" in record["provenance"]:
                    raw_path = record["provenance"]["source_path"]
                    filename_only = os.path.basename(raw_path)
                    record["provenance"]["source_path"] = f"Redacted / {filename_only}"

                self._records.append(record)
                count += 1

        logger.info("Corpus loaded: %d records (mode=%s)", count, self._corpus_mode)

        # Warn if small corpus count is unexpected
        if self._corpus_mode == "small" and count != 100:
            logger.warning(
                "Small corpus has %d records (expected 100). "
                "This may indicate a corrupted corpus file.",
                count
            )

    def _ensure_loaded(self):
        if not self._loaded:
            self._load_corpus()

    def get_all_records(self) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        return self._records

    def get_corpus_info(self) -> Dict[str, Any]:
        self._ensure_loaded()
        return {
            'corpus_mode': self._corpus_mode,
            'corpus_path': os.path.basename(self._corpus_path),
            'records': len(self._records),
        }

    def get_scenarios(self) -> Dict[str, int]:
        self._ensure_loaded()
        scenarios = {}
        for r in self._records:
            sid = r.get("scenario_instance_id")
            if sid:
                scenarios[sid] = scenarios.get(sid, 0) + 1
        return scenarios

    def get_records(
        self,
        scenario_id: Optional[str] = None,
        source_type: Optional[str] = None,
        entity_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        self._ensure_loaded()
        filtered = self._records

        if scenario_id:
            filtered = [r for r in filtered if r.get("scenario_instance_id") == scenario_id]
        if source_type:
            filtered = [r for r in filtered if r.get("source_type") == source_type]
        if entity_id:
            eid_lower = entity_id.lower()
            filtered = [
                r for r in filtered
                if any(eid_lower == str(er).lower() for er in r.get("entity_refs", []))
            ]

        return filtered[offset:offset + limit]

    def get_record_by_id(self, source_record_id: str) -> Optional[Dict[str, Any]]:
        """Look up a single record by source_record_id."""
        self._ensure_loaded()
        for r in self._records:
            if r.get("source_record_id") == source_record_id:
                return r
        return None

    def search_records(
        self,
        query: str,
        scenario_id: Optional[str] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Simple keyword search for fallback retrieval."""
        self._ensure_loaded()
        filtered = self._records
        if scenario_id:
            filtered = [r for r in filtered if r.get("scenario_instance_id") == scenario_id]

        q_lower = query.lower()
        results = []

        for r in filtered:
            score = 0
            text = str(r.get("normalized_text", "")).lower()
            if q_lower in text:
                score += 1

            for ent in r.get("entity_refs", []):
                if q_lower in str(ent).lower():
                    score += 2

            for loc in r.get("location_refs", []):
                if q_lower in str(loc).lower():
                    score += 1

            if q_lower in str(r.get("source_type", "")).lower():
                score += 1

            if score > 0:
                results.append((score, r))

        results.sort(key=lambda x: x[0], reverse=True)
        return [r for score, r in results[:limit]]


# Create a singleton — lazy loading (no longer validates 100 records at import time)
corpus_service = CorpusService()
