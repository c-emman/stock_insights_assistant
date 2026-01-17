"""
Tests for formatters.
"""

import pytest
from app.utils.formatters import format_stock_data, format_insight


def test_format_stock_data():
    """Test stock data formatting."""
    data = {"symbol": "AAPL", "price": 150.0}
    result = format_stock_data(data)
    assert result == data


def test_format_insight():
    """Test insight formatting."""
    insight = "Test insight"
    result = format_insight(insight)
    assert result == insight
