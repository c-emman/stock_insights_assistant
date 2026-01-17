"""
Core data models.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict


# Query parsing enums
class Industry(str, Enum):
    """Supported industries for stock queries."""

    TECHNOLOGY = "technology"
    FINANCE = "finance"
    HEALTHCARE = "healthcare"
    ENERGY = "energy"
    CONSUMER = "consumer"


class Intent(str, Enum):
    """Supported query intents."""

    TOP_GAINERS = "top_gainers"
    TOP_LOSERS = "top_losers"
    QUOTE = "quote"
    COMPARE = "compare"
    UNSUPPORTED = "unsupported"


class Direction(str, Enum):
    """Direction for top movers."""

    GAINERS = "gainers"
    LOSERS = "losers"


class ParsedQuery(BaseModel):
    """Parsed user query from AI."""

    intent: Intent
    industry: Industry | None = None
    symbols: list[str] = []
    direction: Direction | None = None


class StockQuote(BaseModel):
    """Real-time stock quote data."""

    symbol: str
    current_price: float
    change: float
    change_percent: float
    high: float
    low: float
    open_price: float
    previous_close: float
    timestamp: int | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "AAPL",
                "current_price": 182.52,
                "change": 2.42,
                "change_percent": 1.34,
                "high": 183.20,
                "low": 179.80,
                "open_price": 180.10,
                "previous_close": 180.10,
            }
        }
    )


class CompanyProfile(BaseModel):
    """Company profile information."""

    symbol: str
    name: str
    country: str | None = None
    currency: str | None = None
    exchange: str | None = None
    ipo: str | None = None
    market_capitalization: float | None = None
    share_outstanding: float | None = None
    logo: str | None = None
    phone: str | None = None
    weburl: str | None = None
    finnhub_industry: str | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "symbol": "AAPL",
                "name": "Apple Inc",
                "country": "US",
                "currency": "USD",
                "exchange": "NASDAQ",
                "market_capitalization": 2800000000000,
            }
        }
    )


class QueryRequest(BaseModel):
    """API request model for user queries."""

    query: str

    model_config = ConfigDict(json_schema_extra={"example": {"query": "How is AAPL doing today?"}})


class QueryResponse(BaseModel):
    """API response model."""

    response: str
    symbols: list[str] = []
    top_gainers: list[dict] | None = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": "Apple (AAPL) is currently trading at $182.52...",
                "symbols": ["AAPL"],
            }
        }
    )
