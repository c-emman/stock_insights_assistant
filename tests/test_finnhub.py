"""
Tests for Finnhub client.
"""

import pytest
from app.services.finnhub import FinnhubClient
from app.core.models import StockQuote, CompanyProfile


@pytest.fixture
def mock_finnhub_client(mocker):
    """Create a mock Finnhub client."""
    mock_finnhub_module = mocker.patch("app.services.finnhub.finnhub")
    mock_client = mocker.Mock()
    mock_finnhub_module.Client.return_value = mock_client
    client = FinnhubClient(api_key="test_key")
    client.client = mock_client
    return client, mock_client


def test_finnhub_client_init(mock_finnhub_client):
    """Test FinnhubClient initialization."""
    client, _ = mock_finnhub_client
    assert client.api_key == "test_key"
    assert client.client is not None


def test_get_quote_success(mock_finnhub_client):
    """Test successful quote retrieval."""
    client, mock_client = mock_finnhub_client
    mock_client.quote.return_value = {
        "c": 182.52,
        "d": 2.42,
        "dp": 1.34,
        "h": 183.20,
        "l": 179.80,
        "o": 180.10,
        "pc": 180.10,
        "t": 1234567890,
    }

    quote = client.get_quote("AAPL")
    assert quote is not None
    assert isinstance(quote, StockQuote)
    assert quote.symbol == "AAPL"
    assert quote.current_price == 182.52
    assert quote.change == 2.42
    assert quote.change_percent == 1.34
    mock_client.quote.assert_called_once_with("AAPL")


def test_get_quote_empty_response(mock_finnhub_client):
    """Test quote retrieval with empty response."""
    client, mock_client = mock_finnhub_client
    mock_client.quote.return_value = {}

    quote = client.get_quote("AAPL")
    assert quote is None


def test_get_quote_none_response(mock_finnhub_client):
    """Test quote retrieval with None response."""
    client, mock_client = mock_finnhub_client
    mock_client.quote.return_value = None

    quote = client.get_quote("AAPL")
    assert quote is None


def test_get_quote_exception(mock_finnhub_client):
    """Test quote retrieval with exception."""
    client, mock_client = mock_finnhub_client
    mock_client.quote.side_effect = Exception("API Error")

    quote = client.get_quote("AAPL")
    assert quote is None


def test_get_company_profile_success(mock_finnhub_client):
    """Test successful company profile retrieval."""
    client, mock_client = mock_finnhub_client
    mock_client.company_profile2.return_value = {
        "name": "Apple Inc",
        "country": "US",
        "currency": "USD",
        "exchange": "NASDAQ",
        "marketCapitalization": 2800000000000,
    }

    profile = client.get_company_profile("AAPL")
    assert profile is not None
    assert isinstance(profile, CompanyProfile)
    assert profile.symbol == "AAPL"
    assert profile.name == "Apple Inc"
    assert profile.country == "US"
    mock_client.company_profile2.assert_called_once_with(symbol="AAPL")


def test_get_company_profile_empty_response(mock_finnhub_client):
    """Test company profile retrieval with empty response."""
    client, mock_client = mock_finnhub_client
    mock_client.company_profile2.return_value = None

    profile = client.get_company_profile("AAPL")
    assert profile is None


def test_get_company_profile_exception(mock_finnhub_client):
    """Test company profile retrieval with exception."""
    client, mock_client = mock_finnhub_client
    mock_client.company_profile2.side_effect = Exception("API Error")

    profile = client.get_company_profile("AAPL")
    assert profile is None


def test_get_quote_multiple(mock_finnhub_client):
    """Test getting quotes for multiple symbols."""
    client, mock_client = mock_finnhub_client

    def mock_quote(symbol):
        return {
            "AAPL": {
                "c": 182.52,
                "d": 2.42,
                "dp": 1.34,
                "h": 183.20,
                "l": 179.80,
                "o": 180.10,
                "pc": 180.10,
            },
            "TSLA": {
                "c": 248.50,
                "d": 5.10,
                "dp": 2.10,
                "h": 250.00,
                "l": 245.00,
                "o": 243.40,
                "pc": 243.40,
            },
        }.get(symbol, {})

    mock_client.quote.side_effect = mock_quote

    results = client.get_quote_multiple(["AAPL", "TSLA"])
    assert len(results) == 2
    assert "AAPL" in results
    assert "TSLA" in results
    assert isinstance(results["AAPL"], StockQuote)
    assert isinstance(results["TSLA"], StockQuote)
