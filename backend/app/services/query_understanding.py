"""
query_understanding.py

Deterministic query understanding layer for investigative queries.
Extracts entities, temporal information, spatial context, and intent
WITHOUT using an LLM — pure regex + heuristics for speed and determinism.
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Entity patterns matching the corpus (Phase 9B identifier patterns)
# ---------------------------------------------------------------------------

# Person IDs
PERSON_ID_PATTERN = re.compile(r'\bP-\d+\b')

# Phone numbers (India)
PHONE_PATTERN = re.compile(r'\+91-\d{10}|\b91\d{10}\b|\b\d{10}\b(?=\s|$|[,.])')
PHONE_ID_PATTERN = re.compile(r'\bPHONE-\d+\b')

# Contextual phone: bare 10-digit number preceded by phone-related keyword.
# This is triggered ONLY by explicit context; isolated numbers are never captured.
PHONE_RAW_PATTERN = re.compile(
    r'(?:phone|mobile|cell|CDR|contact|number|no\.?|#)'
    r'[:\s]*'
    r'(\d{10})'
    r'(?=\s|$|[,.])',
    re.IGNORECASE
)

# Account IDs: explicit ACC-xxx OR contextual numeric triggered by keyword.
# Numbers preceded by date/amount/count words are NEVER captured.
ACCOUNT_ID_PATTERN = re.compile(r'\bACC-\d+\b')
ACCOUNT_CONTEXT_PATTERN = re.compile(
    r'(?:account|acc(?:ount)?(?:\s+no\.?|\.?|\s+number|\s+#)?|a/c)'
    r'[:\s]+'
    r'(\d{4,12})'
    r'(?=\s|$|[,.])',
    re.IGNORECASE
)

# Vehicles: VEH-xxx or Indian license plates (e.g. DL05CF1567)
VEHICLE_PATTERN = re.compile(
    r'\bVEH-[\w-]+\b|'
    r'\b[A-Z]{2}\d{2}[A-Z]{1,2}\d{4}\b'
)

# Bank accounts (numeric or ACC-xxx)
ACCOUNT_PATTERN = re.compile(r'\bACC-\d+\b|\b\d{5,12}\b')

# FIR numbers
FIR_PATTERN = re.compile(r'\bFIR-[\d/\w]+\b')

# Source record IDs (CBS, CDR, FIU, FIN, OSINT, CH, ANPR, CAF, FNOTE, CRIM, TDUMP)
RECORD_ID_PATTERN = re.compile(
    r'\b(?:FIU|CAF|CBS|CDR|FIN|OSINT|CH|ANPR|FNOTE|CRIM|TDUMP)-[\w/-]+\b'
)

# Case references 
CASE_REF_PATTERN = re.compile(r'\b[A-Z]{2,6}-\d{3,}/\d{4}/[A-Z]{2}\b')

# Location / tower references
TOWER_PATTERN = re.compile(r'\bTOWER-[A-Z]{2}-[A-Z]{2}-\d+\b')
BRANCH_PATTERN = re.compile(r'\bBR-\d+\b')

# ---------------------------------------------------------------------------
# Temporal extraction
# ---------------------------------------------------------------------------

ISO_DATE_PATTERN = re.compile(
    r'\b(\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}Z?)?)\b'
)

RELATIVE_DATE_PATTERN = re.compile(
    r'(last\s+\d+\s+(?:days?|hours?|weeks?|months?))|'
    r'(past\s+\d+\s+(?:days?|hours?|weeks?|months?))|'
    r'(within\s+\d+\s+(?:days?|hours?|weeks?|months?))|'
    r'(before\s+[\w\s,]+\d{4})|'
    r'(after\s+[\w\s,]+\d{4})',
    re.IGNORECASE
)

MONTH_YEAR_PATTERN = re.compile(
    r'\b(january|february|march|april|may|june|july|august|september|october|november|december)\s+(\d{4})\b',
    re.IGNORECASE
)

MONTH_ABBR = {
    'january': 1, 'february': 2, 'march': 3, 'april': 4,
    'may': 5, 'june': 6, 'july': 7, 'august': 8,
    'september': 9, 'october': 10, 'november': 11, 'december': 12
}

# ---------------------------------------------------------------------------
# Location keywords (based on corpus)
# ---------------------------------------------------------------------------

LOCATION_KEYWORDS = [
    'connaught place', 'kherki daula', 'vasant kunj', 'dwarka',
    'noida', 'gurugram', 'south delhi', 'west delhi', 'east delhi',
    'north delhi', 'new delhi', 'delhi ncr', 'ncr'
]

POLICE_STATION_PATTERN = re.compile(r'\bPS-[\w\s]+|police station\s+[\w\s]+', re.IGNORECASE)

# ---------------------------------------------------------------------------
# Intent classification
# ---------------------------------------------------------------------------

INTENT_KEYWORDS = {
    'find_connections': [
        'find connections', 'connections of', 'links between', 'linked to',
        'related to', 'associated with', 'associates of', 'network of'
    ],
    'financial_links': [
        'financial', 'bank', 'transaction', 'transfer', 'payment',
        'account', 'hawala', 'money trail', 'funds', 'cbs', 'fiu', 'str'
    ],
    'communication_links': [
        'call', 'communication', 'phone', 'cdr', 'contact', 'message',
        'telecom', 'called', 'spoke', 'received'
    ],
    'location_movement': [
        'location', 'movement', 'traveled', 'route', 'tower', 'anpr',
        'toll', 'area', 'place', 'station', 'visited', 'seen at'
    ],
    'identity': [
        'who is', 'identify', 'identification', 'kyc', 'caf', 'registered',
        'name', 'subscriber', 'owner of'
    ],
    'criminal_history': [
        'criminal', 'history', 'record', 'prior', 'previous', 'fir',
        'case', 'accused', 'convicted', 'bail', 'absconding'
    ],
    'summarize_evidence': [
        'summarize', 'summary', 'overview', 'what evidence', 'all records',
        'show evidence', 'list records', 'explain'
    ],
    'investigate_timeline': [
        'timeline', 'chronological', 'sequence', 'when', 'before', 'after',
        'during', 'at what time', 'order of events'
    ],
}


@dataclass
class QueryUnderstanding:
    """
    Structured output of the query understanding layer.
    All fields are deterministically extracted from the query text.
    """
    original_query: str

    # Entity identifiers found in query
    person_ids: List[str] = field(default_factory=list)
    phone_ids: List[str] = field(default_factory=list)
    vehicle_ids: List[str] = field(default_factory=list)
    account_ids: List[str] = field(default_factory=list)
    fir_ids: List[str] = field(default_factory=list)
    case_ids: List[str] = field(default_factory=list)
    record_ids: List[str] = field(default_factory=list)
    tower_ids: List[str] = field(default_factory=list)
    branch_ids: List[str] = field(default_factory=list)

    # All entity references combined (for exact Qdrant lookup)
    all_entity_refs: List[str] = field(default_factory=list)

    # Temporal window
    time_start: Optional[datetime] = None
    time_end: Optional[datetime] = None
    has_temporal_constraint: bool = False

    # Location context
    location_refs: List[str] = field(default_factory=list)
    has_spatial_constraint: bool = False

    # Intent classification
    intents: List[str] = field(default_factory=list)
    primary_intent: str = 'general_investigation'

    # Semantic query (original minus extracted IDs for embedding)
    semantic_query: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            'original_query': self.original_query,
            'person_ids': self.person_ids,
            'phone_ids': self.phone_ids,
            'vehicle_ids': self.vehicle_ids,
            'account_ids': self.account_ids,
            'fir_ids': self.fir_ids,
            'case_ids': self.case_ids,
            'record_ids': self.record_ids,
            'all_entity_refs': self.all_entity_refs,
            'time_start': self.time_start.isoformat() if self.time_start else None,
            'time_end': self.time_end.isoformat() if self.time_end else None,
            'has_temporal_constraint': self.has_temporal_constraint,
            'location_refs': self.location_refs,
            'has_spatial_constraint': self.has_spatial_constraint,
            'intents': self.intents,
            'primary_intent': self.primary_intent,
            'semantic_query': self.semantic_query,
        }


class QueryUnderstandingService:
    """
    Deterministic query understanding service.
    Extracts structured information from investigative natural language queries.
    """

    def __init__(self):
        logger.info("QueryUnderstandingService initialized (deterministic mode)")

    def parse(self, query: str) -> QueryUnderstanding:
        """
        Parse an investigative query into structured understanding.
        """
        if not query or not query.strip():
            return QueryUnderstanding(
                original_query=query or "",
                semantic_query=query or "",
                primary_intent='general_investigation'
            )

        qu = QueryUnderstanding(original_query=query)
        q = query.strip()

        # 1. Extract entities
        qu.person_ids = self._extract_unique(PERSON_ID_PATTERN, q)

        # Phone IDs: explicit PHONE-xxx prefix
        phone_ids_explicit = self._extract_unique(PHONE_ID_PATTERN, q)
        # Formatted Indian numbers (+91-..., 91..., 10-digit with boundary)
        phone_ids_formatted = self._extract_unique(PHONE_PATTERN, q)
        # Bare 10-digit numbers ONLY when preceded by phone/CDR/mobile context keyword
        phone_ids_contextual = self._extract_unique(PHONE_RAW_PATTERN, q)
        seen_phones: set = set()
        qu.phone_ids = []
        for p in phone_ids_explicit + phone_ids_formatted + phone_ids_contextual:
            if p not in seen_phones:
                seen_phones.add(p)
                qu.phone_ids.append(p)

        qu.vehicle_ids = self._extract_unique(VEHICLE_PATTERN, q)
        qu.fir_ids = self._extract_unique(FIR_PATTERN, q)
        qu.record_ids = self._extract_unique(RECORD_ID_PATTERN, q)
        qu.case_ids = self._extract_unique(CASE_REF_PATTERN, q)
        qu.tower_ids = self._extract_unique(TOWER_PATTERN, q)
        qu.branch_ids = self._extract_unique(BRANCH_PATTERN, q)

        # Account IDs: explicit ACC-xxx format OR contextual 'account 3189' style.
        # Bare numbers not preceded by an account keyword are NEVER captured.
        account_explicit = self._extract_unique(ACCOUNT_ID_PATTERN, q)
        account_contextual = self._extract_unique(ACCOUNT_CONTEXT_PATTERN, q)
        seen_accounts: set = set()
        qu.account_ids = []
        for a in account_explicit + account_contextual:
            if a not in seen_accounts:
                seen_accounts.add(a)
                qu.account_ids.append(a)

        # Combine all for Qdrant exact lookup
        all_refs = (
            qu.person_ids + qu.phone_ids + qu.vehicle_ids + qu.account_ids +
            qu.fir_ids + qu.case_ids + qu.record_ids + qu.tower_ids + qu.branch_ids
        )
        seen = set()
        qu.all_entity_refs = [r for r in all_refs if not (r in seen or seen.add(r))]

        # 2. Extract temporal information
        qu.time_start, qu.time_end = self._extract_temporal(q)
        qu.has_temporal_constraint = qu.time_start is not None or qu.time_end is not None

        # 3. Extract spatial context
        qu.location_refs = self._extract_locations(q)
        qu.has_spatial_constraint = len(qu.location_refs) > 0

        # 4. Classify intent
        qu.intents = self._classify_intents(q)
        qu.primary_intent = qu.intents[0] if qu.intents else 'general_investigation'

        # 5. Build semantic query (remove matched IDs for cleaner embedding)
        qu.semantic_query = self._build_semantic_query(q, qu)

        logger.debug(
            "Query understood: entities=%d, temporal=%s, spatial=%d, intent=%s",
            len(qu.all_entity_refs), qu.has_temporal_constraint,
            len(qu.location_refs), qu.primary_intent
        )

        return qu

    def _extract_unique(self, pattern: re.Pattern, text: str) -> List[str]:
        """Extract unique matches from text using pattern."""
        matches = pattern.findall(text)
        seen = set()
        result = []
        for m in matches:
            # findall may return tuples for groups
            val = m[0] if isinstance(m, tuple) else m
            val = val.strip()
            if val and val not in seen:
                seen.add(val)
                result.append(val)
        return result

    def _extract_temporal(
        self, query: str
    ) -> Tuple[Optional[datetime], Optional[datetime]]:
        """
        Extract temporal window from query.
        Returns (time_start, time_end) tuple.
        """
        now = datetime.now(tz=timezone.utc)

        # ISO date extraction
        iso_dates = []
        for m in ISO_DATE_PATTERN.finditer(query):
            date_str = m.group(1)
            try:
                if 'T' in date_str:
                    dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                else:
                    dt = datetime.strptime(date_str, '%Y-%m-%d').replace(tzinfo=timezone.utc)
                iso_dates.append(dt)
            except ValueError:
                pass

        if len(iso_dates) == 1:
            # Single date: use ±1 day window
            d = iso_dates[0]
            return (
                d.replace(hour=0, minute=0, second=0),
                d.replace(hour=23, minute=59, second=59)
            )
        elif len(iso_dates) >= 2:
            iso_dates.sort()
            return iso_dates[0], iso_dates[-1]

        # Month + year
        m = MONTH_YEAR_PATTERN.search(query)
        if m:
            month_name = m.group(1).lower()
            year = int(m.group(2))
            month_num = MONTH_ABBR.get(month_name, 1)
            try:
                start = datetime(year, month_num, 1, tzinfo=timezone.utc)
                # End of month
                if month_num == 12:
                    end = datetime(year + 1, 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
                else:
                    end = datetime(year, month_num + 1, 1, tzinfo=timezone.utc) - timedelta(seconds=1)
                return start, end
            except ValueError:
                pass

        # Relative: "last 7 days", "past 24 hours"
        relative_match = re.search(
            r'(last|past|within)\s+(\d+)\s+(days?|hours?|weeks?|months?)',
            query, re.IGNORECASE
        )
        if relative_match:
            n = int(relative_match.group(2))
            unit = relative_match.group(3).lower()
            if 'hour' in unit:
                delta = timedelta(hours=n)
            elif 'week' in unit:
                delta = timedelta(weeks=n)
            elif 'month' in unit:
                delta = timedelta(days=n * 30)
            else:
                delta = timedelta(days=n)
            return now - delta, now

        return None, None

    def _extract_locations(self, query: str) -> List[str]:
        """Extract location references from query."""
        locations = []
        q_lower = query.lower()

        for loc in LOCATION_KEYWORDS:
            if loc in q_lower:
                locations.append(loc.title())

        # Police station references
        ps_matches = POLICE_STATION_PATTERN.findall(query)
        for ps in ps_matches:
            ps = ps.strip()
            if ps and ps not in locations:
                locations.append(ps)

        # Tower IDs as locations
        tower_matches = TOWER_PATTERN.findall(query)
        for t in tower_matches:
            if t not in locations:
                locations.append(t)

        return locations

    def _classify_intents(self, query: str) -> List[str]:
        """Classify investigative intent from query."""
        q_lower = query.lower()
        matched = []

        for intent, keywords in INTENT_KEYWORDS.items():
            for kw in keywords:
                if kw in q_lower:
                    matched.append(intent)
                    break

        if not matched:
            matched = ['general_investigation']

        return matched

    def _build_semantic_query(self, original: str, qu: QueryUnderstanding) -> str:
        """
        Build semantic query by keeping the full original query.
        The RetrievalAPI's _extract_identifiers handles ID removal internally.
        We keep the full query for embedding because context helps semantic search.
        """
        return original


# Singleton instance
query_understanding_service = QueryUnderstandingService()
