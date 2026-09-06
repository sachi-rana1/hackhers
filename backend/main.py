from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from ai_explainability.graph_rag import explain_price_movement

app = FastAPI(
    title="APIx High-Performance REST Core Gateway",
    description="Calculated Indian airfare CPI tracker API feeds.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def gateway_index():
    return {"status": "Online", "service": "APIx Core Platform Gateway"}

@app.get("/api/v1/explain")
def query_graph_explain(date: str = Query(..., description="Query target date YYYY-MM-DD")):
    """
    Exposes GraphRAG explanation lookups as a REST endpoint.
    """
    analysis = explain_price_movement(date)
    if "error" in analysis:
        raise HTTPException(status_code=400, detail=analysis["error"])
    return {
        "date": date,
        "explanation": analysis["explanation"],
        "classifications": analysis["categories"]
    }
