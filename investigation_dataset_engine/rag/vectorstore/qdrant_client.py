import uuid
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models

# A strict namespace for deterministic UUID5 generation for this project
NAMESPACE_SIH26189 = uuid.uuid5(uuid.NAMESPACE_DNS, "sih26189.investigation.dataset")

def generate_point_uuid(document_id: str) -> str:
    """
    Generates a deterministic UUID5 from the document_id.
    """
    return str(uuid.uuid5(NAMESPACE_SIH26189, document_id))

class QdrantEvidenceClient:
    def __init__(self, path: str = "output/qdrant_storage", collection_name: str = "sih26189_evidence"):
        self.client = QdrantClient(path=path)
        self.collection_name = collection_name
        
    def ensure_collection(self, vector_size: int, distance=models.Distance.COSINE):
        """
        Creates the collection if it doesn't exist, using the provided vector_size.
        """
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=vector_size,
                    distance=distance
                )
            )
            # Create payload indexes for forensic filtering
            self.client.create_payload_index(self.collection_name, "source_type", field_schema=models.PayloadSchemaType.KEYWORD)
            self.client.create_payload_index(self.collection_name, "scenario_family", field_schema=models.PayloadSchemaType.KEYWORD)
            self.client.create_payload_index(self.collection_name, "scenario_instance_id", field_schema=models.PayloadSchemaType.KEYWORD)
            self.client.create_payload_index(self.collection_name, "case_refs", field_schema=models.PayloadSchemaType.KEYWORD)
            self.client.create_payload_index(self.collection_name, "entity_refs", field_schema=models.PayloadSchemaType.KEYWORD)
            
    def prepare_payload(self, doc_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepares a lean payload by dropping fields that shouldn't be inside Qdrant.
        """
        payload = {
            "document_id": doc_dict.get("document_id"),
            "scenario_instance_id": doc_dict.get("scenario_instance_id"),
            "scenario_family": doc_dict.get("scenario_family"),
            "source_type": doc_dict.get("source_type"),
            "source_record_id": doc_dict.get("source_record_id"),
            "timestamp": doc_dict.get("timestamp"),
            "entity_refs": doc_dict.get("entity_refs", []),
            "location_refs": doc_dict.get("location_refs", []),
            "case_refs": doc_dict.get("case_refs", []),
            "provenance": doc_dict.get("provenance", {})
        }
        # Explicitly ensure no raw text/content is stored unnecessarily
        return payload

    def upsert_batch(self, documents: List[Dict[str, Any]], embeddings: List[List[float]]):
        """
        Upserts a batch of documents into Qdrant.
        """
        points = []
        for doc, emb in zip(documents, embeddings):
            point_id = generate_point_uuid(doc["document_id"])
            payload = self.prepare_payload(doc)
            
            points.append(models.PointStruct(
                id=point_id,
                vector=emb,
                payload=payload
            ))
            
        self.client.upsert(
            collection_name=self.collection_name,
            points=points
        )

    # ---------------------------------------------------------------------------
    # Identifier type routing (Guardrail 2)
    # ---------------------------------------------------------------------------

    @staticmethod
    def _route_identifier(identifier: str) -> List[str]:
        """
        Return the Qdrant payload fields to search for this identifier,
        based on its type prefix (corpus audit findings).

        BR-xxx       -> branch ID  -> location_refs (primary), entity_refs, source_record_id
        FIR-xxx      -> FIR/case   -> case_refs, source_record_id, scenario_instance_id
        PHONE-/+91-  -> phone      -> entity_refs
        10-digit raw -> phone      -> entity_refs
        FNOTE/CBS/CDR/... -> record ID -> source_record_id
        Everything else -> entity_refs + source_record_id (safe default)
        """
        import re
        if re.match(r'^BR-', identifier):
            return ["location_refs", "entity_refs", "source_record_id"]
        if re.match(r'^FIR-', identifier) or re.match(r'^[A-Z]{2,6}-\d{3,}/\d{4}/', identifier):
            return ["case_refs", "source_record_id", "scenario_instance_id"]
        if re.match(r'^(?:PHONE-|\+91-|91)\d', identifier) or re.match(r'^\d{10}$', identifier):
            return ["entity_refs"]
        if re.match(r'^(?:FNOTE|CBS|CDR|FIU|FIN|OSINT|CAF|CH|ANPR|CRIM|TDUMP)-', identifier):
            return ["source_record_id"]
        # Generic: ACC-xxx, P-xxx, VEH-xxx, tower IDs, bare account numbers
        return ["entity_refs", "source_record_id"]

    def _build_query_filter(
        self,
        filters: Optional[Dict[str, str]] = None,
        investigation_context: Optional[Any] = None,
        exact_identifiers: Optional[List[str]] = None,
        has_exact_identifier: bool = False,
    ) -> Optional[models.Filter]:
        """
        Build a Qdrant filter from investigation context and/or exact identifiers.

        Guardrail 1 — Scenario isolation (ALWAYS MUST):
          scenario_ids → standalone MUST on scenario_instance_id.
          This is never relaxed, never SHOULD.

        Guardrail 2 — Typed identifier routing:
          Exact identifiers are routed to typed payload fields based on prefix,
          not blindly checked against all fields.

        Spatial contract:
          When exact identifiers are also present, location_ids become SHOULD
          so that FNOTE/FIU records (which have empty location_refs) are not
          excluded. Pure-spatial queries (no exact ids) retain strict MUST.
        """
        must_conditions = []
        should_conditions = []

        if filters:
            for k, v in filters.items():
                must_conditions.append(models.FieldCondition(
                    key=k, match=models.MatchValue(value=v)
                ))

        if investigation_context:
            # --- GUARDRAIL 1: Scenario isolation — ALWAYS hard MUST ---
            if investigation_context.scenario_ids:
                scenario_conds = [
                    models.FieldCondition(
                        key="scenario_instance_id",
                        match=models.MatchValue(value=sid),
                    )
                    for sid in investigation_context.scenario_ids
                ]
                # MUST(SHOULD) = must match at least one scenario
                must_conditions.append(models.Filter(should=scenario_conds))

            # Source type filter (hard MUST when explicitly requested)
            if investigation_context.source_type_filters:
                source_conds = [
                    models.FieldCondition(
                        key="source_type", match=models.MatchValue(value=src)
                    )
                    for src in investigation_context.source_type_filters
                ]
                must_conditions.append(models.Filter(should=source_conds))

            # Case IDs: investigative FIR/case references
            # These are NOT the same as scenario_ids.
            if investigation_context.case_ids:
                case_conds = []
                for case_id in investigation_context.case_ids:
                    case_conds.append(models.FieldCondition(
                        key="case_refs", match=models.MatchValue(value=case_id)
                    ))
                    case_conds.append(models.FieldCondition(
                        key="source_record_id", match=models.MatchValue(value=case_id)
                    ))
                must_conditions.append(models.Filter(should=case_conds))

            # --- GUARDRAIL 3: RBAC Authorization ---
            if hasattr(investigation_context, 'authorized_case_ids') and investigation_context.authorized_case_ids:
                auth_case_conds = [
                    models.FieldCondition(
                        key="case_refs", match=models.MatchValue(value=case_id)
                    ) for case_id in investigation_context.authorized_case_ids
                ]
                must_conditions.append(models.Filter(should=auth_case_conds))

            if investigation_context.location_ids:
                loc_conds = [
                    models.FieldCondition(
                        key="location_refs", match=models.MatchValue(value=loc_id)
                    )
                    for loc_id in investigation_context.location_ids
                ]
                if has_exact_identifier or (exact_identifiers and len(exact_identifiers) > 0):
                    # Soft boost: location narrows preference but does NOT exclude
                    # evidence records that don't populate location_refs (FNOTE, FIU).
                    should_conditions.extend(loc_conds)
                else:
                    # Pure-spatial query: apply strict MUST to respect investigator intent.
                    must_conditions.append(models.Filter(should=loc_conds))

            if investigation_context.time_start or investigation_context.time_end:
                dt_kwargs = {}
                if investigation_context.time_start:
                    dt_kwargs["gte"] = investigation_context.time_start.isoformat()
                if investigation_context.time_end:
                    dt_kwargs["lte"] = investigation_context.time_end.isoformat()
                must_conditions.append(models.FieldCondition(
                    key="timestamp", range=models.DatetimeRange(**dt_kwargs)
                ))

        # GUARDRAIL 2: Typed identifier routing
        if exact_identifiers:
            for identifier in exact_identifiers:
                target_fields = self._route_identifier(identifier)
                for field_name in target_fields:
                    should_conditions.append(models.FieldCondition(
                        key=field_name, match=models.MatchValue(value=identifier)
                    ))

        if not must_conditions and not should_conditions:
            return None

        return models.Filter(
            must=must_conditions if must_conditions else None,
            should=should_conditions if should_conditions else None,
        )

    def search(
        self, 
        query_vector: List[float], 
        top_k: int = 10, 
        filters: Optional[Dict[str, str]] = None,
        investigation_context: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Searches for semantically similar evidence.
        """
        query_filter = self._build_query_filter(filters=filters, investigation_context=investigation_context)
        
        results = self.client.query_points(
            collection_name=self.collection_name,
            query=query_vector,
            query_filter=query_filter,
            limit=top_k
        )
        
        return [{"id": hit.id, "score": hit.score, "payload": hit.payload} for hit in results.points]

    def search_exact(
        self,
        identifiers: List[str],
        top_k: int = 10,
        filters: Optional[Dict[str, str]] = None,
        investigation_context: Optional[Any] = None
    ) -> List[Dict[str, Any]]:
        """
        Searches exactly for identifiers using Qdrant scroll API.
        """
        query_filter = self._build_query_filter(
            filters=filters, 
            investigation_context=investigation_context,
            exact_identifiers=identifiers
        )
        
        results, _ = self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=query_filter,
            limit=top_k
        )
        
        # Scrolled records have no score, so we assign 0.0. 
        # Ranking handles exact match sorting anyway.
        return [{"id": hit.id, "score": 0.0, "payload": hit.payload} for hit in results]
        
    def count(self) -> int:
        """Returns the number of points in the collection."""
        return self.client.count(collection_name=self.collection_name).count
