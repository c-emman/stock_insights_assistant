# Stock Insights Assistant

An AI-powered stock insights application that lets users query real-time stock data using natural language. Built for the Balderton Capital Data Engineer take-home assignment.

## Features

- **Natural language queries** - Ask about stocks in plain English
- **Stock quotes** - Get real-time prices for any stock
- **Company comparisons** - Compare multiple stocks side-by-side
- **Top movers** - Find top gainers/losers by industry sector
- **AI-powered** - Intelligent query parsing and response formatting

## Quick Start (Docker)

```bash
# 1. Clone the repository
git clone <repo-url>
cd stock_insights_assistant

# 2. Create environment file with your API keys
cp .env.example .env
# Edit .env and add your FINNHUB_API_KEY and OPENAI_API_KEY

# 3. Run with Docker
docker compose up --build

# 4. Open http://localhost:8000
```

## Local Development Setup

### Prerequisites
- Python 3.10+
- Poetry ([install guide](https://python-poetry.org/docs/#installation))

### Installation

```bash
# 1. Install dependencies
poetry install

# 2. Set up environment variables
cp .env.example .env
# Add your API keys to .env

# 3. Run the application
poetry run uvicorn app.main:app --reload

# 4. Open http://localhost:8000
```

### Running Tests

```bash
poetry run pytest              # Run all tests
poetry run pytest -v           # Verbose output
poetry run ruff check .        # Lint code
poetry run ruff format .       # Format code
```

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Web Browser                              │
│                    (http://localhost:8000)                       │
└─────────────────────────────────┬───────────────────────────────┘
                                  │
                                  ▼
┌─────────────────────────────────────────────────────────────────┐
│                         FastAPI Server                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐  │
│  │  Web UI      │  │  /api/query  │  │  /api/health         │  │
│  │  (index.html)│  │  (POST)      │  │  (GET)               │  │
│  └──────────────┘  └──────┬───────┘  └──────────────────────┘  │
└─────────────────────────────┼───────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Orchestrator                              │
│  - Routes queries based on intent                                │
│  - Coordinates between services                                  │
│  - Formats final responses                                       │
└───────────────┬─────────────────────────────┬───────────────────┘
                │                             │
                ▼                             ▼
┌───────────────────────────┐   ┌───────────────────────────────┐
│      OpenAI Client        │   │       Finnhub Client          │
│  - Query parsing          │   │  - Stock quotes               │
│  - Intent extraction      │   │  - Company profiles           │
│  - Response formatting    │   │  - Rate limit handling        │
│  - Name→Symbol conversion │   │  - Retry logic                │
└─────────────┬─────────────┘   └─────────────┬─────────────────┘
              │                               │
              ▼                               ▼
       ┌─────────────┐                 ┌─────────────┐
       │  OpenAI API │                 │ Finnhub API │
       │  (gpt-4.1)  │                 │             │
       └─────────────┘                 └─────────────┘
```

### Key Components

| Component | Purpose |
|-----------|---------|
| `app/main.py` | FastAPI app initialization, lifespan management |
| `app/api/routes.py` | HTTP endpoints with error handling |
| `app/core/orchestrator.py` | Business logic coordinator |
| `app/core/models.py` | Pydantic models and enums |
| `app/services/finnhub.py` | Finnhub API client with rate limiting |
| `app/services/openai_client.py` | OpenAI client for NLP |
| `app/web/index.html` | Single-page web interface |

## Trade-offs & Decisions

### 1. Curated Industry Lists vs Dynamic Lookup
**Decision**: Used hardcoded lists of ~20 stocks per industry sector.

**Why**: Finnhub's free tier doesn't provide an endpoint to query stocks by industry. The alternatives were:
- Screen scraper (brittle, slow)
- Premium API (cost)
- Curated lists (simple, reliable)

For internal tooling, curated lists of major stocks provide 90% of the value.

### 2. AI for Name→Symbol Conversion
**Decision**: Let GPT convert company names ("Apple") to symbols ("AAPL") rather than using a lookup API.

**Why**: GPT-4 reliably knows major company tickers. Adding a symbol lookup API would add latency and complexity. Invalid symbols get caught when Finnhub returns no data—implicit validation.

### 3. News Feature (Considered, Not Implemented)
**Decision**: Scoped out market news functionality.

**Why**: Initially explored adding news via `get_market_news()`, but:
- News is general, not stock-specific
- Didn't directly answer queries like "top gainers in tech"
- Added complexity without core value

Focused on reliable quote/compare/movers features instead.

### 4. Response Verbosity
**Decision**: Tuned AI prompts to output 2-3 sentence responses.

**Why**: Initial responses were too verbose. Matched the concise style shown in the task examples.

### 5. Rate Limiting Strategy
**Decision**: Implemented retry with exponential backoff (2 retries, 1s→2s delay).

**Why**: Simple but effective. For internal tooling, this handles transient rate limits without over-engineering (no request queuing, no persistent rate tracking).

## What I'd Improve With More Time

1. **Caching** - Add Redis/memory cache for quotes (TTL ~60s) to reduce API calls
2. **WebSocket** - Real-time price updates instead of request/response
3. **More industries** - Expand curated lists, possibly add custom watchlists
4. **Historical data** - Add price charts using Finnhub candle endpoint
5. **Better error UX** - More specific error messages in the UI
6. **Logging** - Structured logging with correlation IDs
7. **Metrics** - Track query latency, error rates, popular queries

## AI Tools Used

This project was built with assistance from Cursor IDE:

- **Architecture planning** - Discussed trade-offs, scoping decisions
- **Code generation** - Assisted with boilerplate/speed
- **Debugging** - Fixed JSON serialization, rate limiting, SDK usage
- **Code review** - Identified edge cases, suggested improvements

The AI helped accelerate development while I made all architectural/business logic decisions and reviewed/modified generated code.

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Web interface |
| `/api/health` | GET | Health check |
| `/api/query` | POST | Process natural language query |

### Example Request

```bash
curl -X POST http://localhost:8000/api/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How is Apple doing today?"}'
```

### Example Response

```json
{
  "response": "Apple (AAPL) is trading at $182.52, up 1.3% today. Opened at $180.10 with a day range of $179.80 - $183.20.",
  "symbols": ["AAPL"],
  "top_gainers": null
}
```

## License

MIT
