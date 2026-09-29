import json
import hashlib
from typing import List, Optional, Tuple, Set, Any
from datetime import datetime
from pydantic import BaseModel, Field, field_validator, model_validator

ALLOWED_SOURCE_TYPES = {
    "fiu_str_alerts",
    "cbs_bank_transactions",
    "tower_dumps",
    "field_intelligence_notes",
    "toll_anpr_logs",
    "telecom_cdr_logs",
    "kyc_caf_records",
    "cctns_fir_records",
    "criminal_history",
    "osint_social_media"
}

class InvestigationContext(BaseModel):
    investigation_id: str
    case_ids: List[str] = Field(default_factory=list)
    # scenario_ids: hard isolation constraint — always applied as MUST, never SHOULD.
    # Identifies which scenario instance(s) to search within.
    scenario_ids: List[str] = Field(default_factory=list)
    entity_ids: List[str] = Field(default_factory=list)
    person_ids: List[str] = Field(default_factory=list)
    phone_ids: List[str] = Field(default_factory=list)
    vehicle_ids: List[str] = Field(default_factory=list)
    account_ids: List[str] = Field(default_factory=list)
    location_ids: List[str] = Field(default_factory=list)
    known_entity_refs: List[str] = Field(default_factory=list)
    authorized_case_ids: List[str] = Field(default_factory=list)
    
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    
    source_type_filters: List[str] = Field(default_factory=list)
    investigator_query: str = ""
    
    @field_validator("case_ids", "scenario_ids", "entity_ids", "person_ids",
                     "vehicle_ids", "account_ids", "location_ids",
                     "known_entity_refs", "source_type_filters", "authorized_case_ids", mode="before")
    @classmethod
    def _normalize_list(cls, v: Any) -> List[str]:
        if not v:
            return []
        if isinstance(v, str):
            v = [v]
        # Remove duplicates preserving order (determinism)
        seen: Set[str] = set()
        return [str(x) for x in v if not (x in seen or seen.add(x))]

    @field_validator("source_type_filters")
    @classmethod
    def _validate_source_types(cls, v: List[str]) -> List[str]:
        for src in v:
            if src not in ALLOWED_SOURCE_TYPES:
                raise ValueError(f"Invalid source type: {src}")
        return v

    @model_validator(mode="after")
    def _validate_time_range(self):
        if self.time_start and self.time_end:
            if self.time_start > self.time_end:
                raise ValueError("time_start cannot be after time_end")
        return self

    def serialize(self) -> str:
        """
        Produce a deterministic JSON string suitable for hashing/caching.
        Lists are explicitly sorted for serialization determinism, even if the runtime
        model preserves insertion order.
        """
        def dt_to_str(dt: Optional[datetime]) -> Optional[str]:
            return dt.isoformat() if dt else None

        data = {
            "investigation_id": self.investigation_id,
            "case_ids": sorted(self.case_ids),
            "scenario_ids": sorted(self.scenario_ids),
            "entity_ids": sorted(self.entity_ids),
            "person_ids": sorted(self.person_ids),
            "phone_ids": sorted(self.phone_ids),
            "vehicle_ids": sorted(self.vehicle_ids),
            "account_ids": sorted(self.account_ids),
            "location_ids": sorted(self.location_ids),
            "known_entity_refs": sorted(self.known_entity_refs),
            "authorized_case_ids": sorted(self.authorized_case_ids),
            "time_start": dt_to_str(self.time_start),
            "time_end": dt_to_str(self.time_end),
            "source_type_filters": sorted(self.source_type_filters),
            "investigator_query": self.investigator_query
        }
        return json.dumps(data, separators=(',', ':'), sort_keys=True)
