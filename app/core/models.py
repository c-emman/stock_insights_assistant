"""
Core data models.
"""

from enum import Enum
from typing import Optional
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
    industry: Optional[Industry] = None
    symbols: list[str] = []
    direction: Optional[Direction] = None


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
    timestamp: Optional[int] = None

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
    country: Optional[str] = None
    currency: Optional[str] = None
    exchange: Optional[str] = None
    ipo: Optional[str] = None
    market_capitalization: Optional[float] = None
    share_outstanding: Optional[float] = None
    logo: Optional[str] = None
    phone: Optional[str] = None
    weburl: Optional[str] = None
    finnhub_industry: Optional[str] = None

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

    model_config = ConfigDict(
        json_schema_extra={"example": {"query": "How is AAPL doing today?"}}
    )


class QueryResponse(BaseModel):
    """API response model."""

    response: str
    symbols: list[str] = []
    top_gainers: Optional[list[dict]] = None

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "response": "Apple (AAPL) is currently trading at $182.52...",
                "symbols": ["AAPL"],
            }
        }
    )
