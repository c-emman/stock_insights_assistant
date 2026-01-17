"""
Tests for core data models.
"""

from app.core.models import (
    CompanyProfile,
    QueryRequest,
    QueryResponse,
    StockQuote,
)


def test_stock_quote_creation():
    """Test StockQuote model creation."""
    quote = StockQuote(
        symbol="AAPL",
        current_price=182.52,
        change=2.42,
        change_percent=1.34,
        high=183.20,
        low=179.80,
        open_price=180.10,
        previous_close=180.10,
    )
    assert quote.symbol == "AAPL"
    assert quote.current_price == 182.52
    assert quote.change_percent == 1.34


def test_company_profile_creation():
    """Test CompanyProfile model creation."""
    profile = CompanyProfile(
        symbol="AAPL",
        name="Apple Inc",
        country="US",
        currency="USD",
        exchange="NASDAQ",
        market_capitalization=2800000000000,
    )
    assert profile.symbol == "AAPL"
    assert profile.name == "Apple Inc"
    assert profile.country == "US"


def test_query_request():
    """Test QueryRequest model."""
    request = QueryRequest(query="How is AAPL doing?")
    assert request.query == "How is AAPL doing?"


def test_query_response():
    """Test QueryResponse model."""
    response = QueryResponse(
        response="Apple is doing well", symbols=["AAPL"]
    )
    assert response.response == "Apple is doing well"
    assert response.symbols == ["AAPL"]
