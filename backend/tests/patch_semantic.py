
from app.services.rag_retrieval_service import rag_retrieval_service
original_retrieve = rag_retrieval_service.retrieve
def semantic_only_retrieve(*args, **kwargs):
    kwargs['use_entity_expansion'] = False
    kwargs['use_rerank'] = False
    return original_retrieve(*args, **kwargs)
rag_retrieval_service.retrieve = semantic_only_retrieve
import app.main
