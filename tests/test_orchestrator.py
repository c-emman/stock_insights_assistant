"""
Tests for orchestrator.
"""

import pytest
from unittest.mock import Mock, patch
from app.core.orchestrator import Orchestrator
from app.core.models import QueryResponse, StockQuote, CompanyProfile


@pytest.fixture
def mock_orchestrator(mocker):
    """Create a mock orchestrator with mocked dependencies."""
    with patch("app.core.orchestrator.FinnhubClient") as mock_finnhub, patch(
        "app.core.orchestrator.OpenAIClient"
    ) as mock_openai:
        mock_finnhub_instance = mocker.Mock()
        mock_openai_instance = mocker.Mock()
        mock_finnhub.return_value = mock_finnhub_instance
        mock_openai.return_value = mock_openai_instance

        orchestrator = Orchestrator(
            finnhub_api_key="test_finnhub_key", openai_api_key="test_openai_key"
        )
        orchestrator.finnhub_client = mock_finnhub_instance
        orchestrator.openai_client = mock_openai_instance

        return orchestrator, mock_finnhub_instance, mock_openai_instance


def test_orchestrator_init(mock_orchestrator):
    """Test orchestrator initialization."""
    orchestrator, _, _ = mock_orchestrator
    assert orchestrator.finnhub_client is not None
    assert orchestrator.openai_client is not None


def test_process_query_top_gainers(mock_orchestrator):
    """Test processing top gainers query."""
    orchestrator, mock_finnhub, mock_openai = mock_orchestrator

    # Mock AI parsing
    mock_openai.parse_query.return_value = {
        "intent": "top_gainers",
        "industry": "technology",
        "symbols": [],
        "direction": "gainers",
    }

    # Mock Finnhub responses
    mock_finnhub.get_top_movers_by_industry.return_value = [
        {
            "symbol": "AAPL",
            "current_price": 182.52,
            "change": 5.0,
            "change_percent": 2.8,
            "high": 183.0,
            "low": 180.0,
        }
    ]

    # Mock AI formatting
    mock_openai.format_response.return_value = "Top gainers in technology: AAPL up 2.8%"

    result = orchestrator.process_query("What are the top gainers in tech?")

    assert isinstance(result, QueryResponse)
    assert "AAPL" in result.symbols
    assert result.top_gainers is not None
    mock_openai.parse_query.assert_called_once()
    mock_finnhub.get_top_movers_by_industry.assert_called_once_with(
        industry="technology", direction="gainers", limit=3
    )


def test_process_query_quote(mock_orchestrator):
    """Test processing single stock quote query."""
    orchestrator, mock_finnhub, mock_openai = mock_orchestrator

    # Mock AI parsing
    mock_openai.parse_query.return_value = {
        "intent": "quote",
        "industry": None,
        "symbols": ["AAPL"],
        "direction": None,
    }

    # Mock Finnhub responses
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
    profile = CompanyProfile(
        symbol="AAPL", name="Apple Inc", country="US", exchange="NASDAQ"
    )

    mock_finnhub.get_quote.return_value = quote
    mock_finnhub.get_company_profile.return_value = profile
    mock_openai.format_response.return_value = "AAPL is trading at $182.52, up 1.34%"

    result = orchestrator.process_query("How is AAPL doing?")

    assert isinstance(result, QueryResponse)
    assert result.symbols == ["AAPL"]
    assert "AAPL" in result.response
    mock_finnhub.get_quote.assert_called_once_with("AAPL")


def test_process_query_no_symbols(mock_orchestrator):
    """Test processing query with no symbols identified."""
    orchestrator, _, mock_openai = mock_orchestrator

    mock_openai.parse_query.return_value = {
        "intent": "quote",
        "industry": None,
        "symbols": [],
        "direction": None,
    }

    result = orchestrator.process_query("How is some stock doing?")

    assert isinstance(result, QueryResponse)
    assert "couldn't identify" in result.response.lower()
