from fastapi import APIRouter, Query
from ai_explainability.graph_rag import explain_price_movement

router = APIRouter(tags=["GraphRAG Explainability"])

@router.get("/explain")
def query_graph_explain(date: str = Query(..., description="Query date format: YYYY-MM-DD")):
    """
    Fetches real-time GraphRAG explanations for specified pricing peaks.
    """
    return explain_price_movement(date)
