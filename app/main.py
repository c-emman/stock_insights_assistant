"""
Main application entry point.
"""

import os
from contextlib import asynccontextmanager

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.api.routes import router
from app.core.orchestrator import Orchestrator

# Load environment variables
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize resources on startup."""
    # Initialize orchestrator once on startup
    finnhub_key = os.getenv("FINNHUB_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")

    if not finnhub_key or not openai_key:
        raise ValueError(
            "Missing required environment variables: FINNHUB_API_KEY and/or OPENAI_API_KEY"
        )

    app.state.orchestrator = Orchestrator(
        finnhub_api_key=finnhub_key,
        openai_api_key=openai_key,
    )
    yield


app = FastAPI(
    title="Stock Insights Assistant",
    description="AI-powered stock insights using natural language queries",
    version="1.0.0",
    lifespan=lifespan,
)

# Include API routes
app.include_router(router, prefix="/api")

# Mount static files for web UI
app.mount("/static", StaticFiles(directory="app/web"), name="static")


@app.get("/")
async def serve_ui():
    """Serve the main web interface."""
    return FileResponse("app/web/index.html")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
