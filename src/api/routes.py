from fastapi import APIRouter
from pydantic import BaseModel

from src.rag.rag_engine import AssessmentRecommendationEngine

router = APIRouter()

engine = None

class RecommendRequest(BaseModel):
    query: str

@router.on_event("startup")
def startup():
    global engine
    # Initialize the RAG engine (loads FAISS index and LLM)
    engine = AssessmentRecommendationEngine()

@router.get("/health")
def health():
    return {"status": "healthy"}

@router.post("/recommend")
def recommend(req: RecommendRequest):
    # Get explanation/recommendation from LLM
    explanation = engine.recommend(req.query)
    
    # Get raw search results for the list
    docs = engine.search(req.query, k=10)
    
    results = []
    for doc in docs:
        meta = doc.metadata
        # Handle test_type splitting if it's a string
        test_type = meta.get("test_type", "")
        if isinstance(test_type, str):
            test_type = test_type.split(",")
            
        results.append({
            "url": meta.get("url", ""),
            "name": meta.get("name", ""),
            "description": meta.get("description", ""),
            "test_type": test_type,
            "duration": meta.get("duration", 0),
            "remote_support": meta.get("remote_support", "Yes"),
            "adaptive_support": meta.get("adaptive_support", "No")
        })

    return {
        "recommended_assessments": results,
        "explanation": explanation
    }
