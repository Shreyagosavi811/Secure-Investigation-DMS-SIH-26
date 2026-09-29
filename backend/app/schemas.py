"""
schemas.py

Pydantic models for the SIH26190 backend API.
All request/response shapes are defined here for type safety and validation.
"""

from typing import List, Optional, Dict, Any, Union
from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Request Models
# ---------------------------------------------------------------------------

class AIQueryRequest(BaseModel):
    """Request body for POST /api/ai/query"""
    query: str = Field(..., min_length=1, max_length=2000, description="Investigative query")
    scenario_id: Optional[str] = Field(None, description="Scenario filter (e.g. 'S01')")
    top_k: Optional[int] = Field(None, ge=1, le=50, description="Max evidence records to retrieve")
    use_entity_expansion: bool = Field(True, description="Enable entity-aware expansion (Phase 9C)")
    use_rerank: bool = Field(True, description="Enable deterministic reranking (Phase 9E)")
    debug: bool = Field(False, description="Return debug retrieval info")

    @field_validator('query')
    @classmethod
    def query_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Query cannot be blank')
        return v.strip()


# ---------------------------------------------------------------------------
# Evidence Pack Models
# ---------------------------------------------------------------------------

class EvidencePackItem(BaseModel):
    """A single retrieved evidence record with retrieval metadata."""
    record_id: str
    document_id: str = ""
    source_type: str
    timestamp: Optional[str] = None
    entity_refs: List[str] = Field(default_factory=list)
    location_refs: List[str] = Field(default_factory=list)
    case_refs: List[str] = Field(default_factory=list)
    normalized_text: str = ""
    semantic_score: float = 0.0
    entity_match_score: float = 0.0
    combined_score: float = 0.0
    retrieval_reasons: List[str] = Field(default_factory=list)
    retrieval_mode: str = "hybrid"
    expansion_depth: int = 0


# ---------------------------------------------------------------------------
# LLM Output Models
# ---------------------------------------------------------------------------

class InvestigativeLead(BaseModel):
    description: str
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    source_record_ids: List[str] = Field(default_factory=list)


class RelationshipFound(BaseModel):
    entity_a: str
    entity_b: str
    relationship: str
    confidence: float = Field(0.0, ge=0.0, le=1.0)
    source_record_ids: List[str] = Field(default_factory=list)


class TimelineEvent(BaseModel):
    timestamp: str
    event: str
    source_record_ids: List[str] = Field(default_factory=list)


class SupportingEvidenceRef(BaseModel):
    record_id: str
    source_type: str
    reason: str


class LLMStructuredOutput(BaseModel):
    """
    Structured output from the Grok LLM, validated against retrieved evidence.
    """
    summary: str = ""
    investigative_leads: List[InvestigativeLead] = Field(default_factory=list)
    relationships: List[RelationshipFound] = Field(default_factory=list)
    timeline: List[TimelineEvent] = Field(default_factory=list)
    supporting_evidence: List[SupportingEvidenceRef] = Field(default_factory=list)
    uncertainties: List[str] = Field(default_factory=list)
    limitations: List[str] = Field(default_factory=list)
    disclaimer: str = "Investigative lead only — not proof of criminal involvement."
    confidence: str = "insufficient"  # supported | partially_supported | insufficient
    mode: str = "llm"


# ---------------------------------------------------------------------------
# Network Link Models
# ---------------------------------------------------------------------------

class NetworkLink(BaseModel):
    """A discovered entity relationship, backed by evidence."""
    source: str
    target: str
    relationship: str
    confidence: float = 0.0
    source_record_ids: List[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Retrieval Metadata Model
# ---------------------------------------------------------------------------

class RetrievalInfo(BaseModel):
    """Metadata about the retrieval process."""
    mode: str  # hybrid | semantic | keyword_fallback
    semantic_candidates: int = 0
    exact_candidates: int = 0
    final_evidence_count: int
    qdrant_available: bool = True
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Timing Model
# ---------------------------------------------------------------------------

class TimingInfo(BaseModel):
    embedding_ms: float = 0.0
    retrieval_ms: float = 0.0
    reranking_ms: float = 0.0
    llm_ms: float = 0.0
    total_ms: float = 0.0


# ---------------------------------------------------------------------------
# Full API Response
# ---------------------------------------------------------------------------

class AIQueryResponse(BaseModel):
    """Full response from POST /api/ai/query"""
    status: str = "success"
    query: str

    # LLM analysis result
    answer: Union[LLMStructuredOutput, Dict[str, Any]] = Field(default_factory=dict)

    # Retrieval metadata
    retrieval: RetrievalInfo

    # Evidence pack (subset sent to LLM)
    evidence: List[EvidencePackItem] = Field(default_factory=list)

    # Extracted entities from query
    entities: List[Dict[str, Any]] = Field(default_factory=list)

    # Network links discovered
    network_links: List[NetworkLink] = Field(default_factory=list)

    # Performance metrics
    timing: TimingInfo = Field(default_factory=TimingInfo)

    # Evidence-derived confidence score (NOT from LLM self-report)
    evidence_strength: float = 0.0

    # Backward compatibility fields
    message: str = ""
    results: List[Dict[str, Any]] = Field(default_factory=list)
    llm_response: Optional[Dict[str, Any]] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    full_name: str

