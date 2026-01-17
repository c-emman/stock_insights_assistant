"""
API routes for the application.
"""

from fastapi import APIRouter, HTTPException, Request
from pydantic import ValidationError

from app.core.models import QueryRequest, QueryResponse
from app.services.finnhub import RateLimitError

router = APIRouter()

# Constants
MAX_QUERY_LENGTH = 500


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
    # Validate query
    if not query.query or not query.query.strip():
        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty"
        )

    if len(query.query) > MAX_QUERY_LENGTH:
        raise HTTPException(
            status_code=400,
            detail=f"Query too long. Maximum {MAX_QUERY_LENGTH} characters."
        )

    orchestrator = request.app.state.orchestrator

    try:
        response = orchestrator.process_query(query.query.strip())
        return response

    except RateLimitError as e:
        raise HTTPException(
            status_code=429,
            detail="Rate limit exceeded. Please wait a moment and try again."
        )

    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail="Invalid query format"
        )

    except Exception as e:
        # Log the error for debugging
        print(f"Error processing query: {e}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your query. Please try again."
        )
