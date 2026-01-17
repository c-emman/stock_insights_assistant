"""
Tests for Finnhub client.
"""

import pytest
from app.services.finnhub import FinnhubClient, INDUSTRY_SYMBOLS
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


def test_get_top_movers_by_industry_gainers(mock_finnhub_client):
    """Test getting top gainers by industry."""
    client, mock_client = mock_finnhub_client

    # Mock quotes for tech stocks
    def mock_quote(symbol):
        quotes = {
            "AAPL": {"c": 182.52, "d": 5.0, "dp": 2.8, "h": 183.0, "l": 180.0, "o": 180.0, "pc": 177.52},
            "MSFT": {"c": 380.0, "d": 3.0, "dp": 0.8, "h": 381.0, "l": 378.0, "o": 378.0, "pc": 377.0},
            "GOOGL": {"c": 140.0, "d": 4.0, "dp": 2.9, "h": 141.0, "l": 139.0, "o": 139.0, "pc": 136.0},
        }
        return quotes.get(symbol, {})

    mock_client.quote.side_effect = mock_quote

    gainers = client.get_top_movers_by_industry("technology", direction="gainers", limit=2)
    assert len(gainers) == 2
    # Should be sorted by change_percent descending
    assert gainers[0]["change_percent"] >= gainers[1]["change_percent"]
    assert gainers[0]["symbol"] in ["AAPL", "GOOGL", "MSFT"]


def test_get_top_movers_by_industry_losers(mock_finnhub_client):
    """Test getting top losers by industry."""
    client, mock_client = mock_finnhub_client

    def mock_quote(symbol):
        quotes = {
            "AAPL": {"c": 175.0, "d": -2.0, "dp": -1.1, "h": 177.0, "l": 174.0, "o": 177.0, "pc": 177.0},
            "MSFT": {"c": 375.0, "d": -5.0, "dp": -1.3, "h": 380.0, "l": 374.0, "o": 380.0, "pc": 380.0},
        }
        return quotes.get(symbol, {})

    mock_client.quote.side_effect = mock_quote

    losers = client.get_top_movers_by_industry("technology", direction="losers", limit=2)
    assert len(losers) == 2
    # Should be sorted by change_percent ascending (most negative first)
    assert losers[0]["change_percent"] <= losers[1]["change_percent"]


def test_get_top_movers_invalid_industry(mock_finnhub_client):
    """Test getting movers for invalid industry."""
    client, _ = mock_finnhub_client
    movers = client.get_top_movers_by_industry("invalid_industry")
    assert movers == []
