"""
API routes for the application.
"""

from fastapi import APIRouter, HTTPException, Request

from app.core.models import QueryRequest, QueryResponse

router = APIRouter()


@router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@router.post("/query", response_model=QueryResponse)
async def process_query(request: Request, query: QueryRequest):
    """
    Process a natural language query about stocks.

    Examples:
    - "How is Apple doing today?"
    - "Compare Tesla and Ford"
    - "What are the top gainers in tech?"
    """
    orchestrator = request.app.state.orchestrator

    try:
        response = orchestrator.process_query(query.query)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")
