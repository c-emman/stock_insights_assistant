"""
API routes for the application.
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Hello World"}
