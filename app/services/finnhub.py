"""
Finnhub API client.
"""

import finnhub
from typing import Optional
from app.core.models import StockQuote, CompanyProfile


class FinnhubClient:
    """Client for interacting with Finnhub API using the official SDK."""

    def __init__(self, api_key: str):
        """Initialize Finnhub client.

        Args:
            api_key: Finnhub API key
        """
        self.api_key = api_key
        self.client = finnhub.Client(api_key=api_key)

    def get_quote(self, symbol: str) -> Optional[StockQuote]:
        """Get real-time quote for a stock symbol.

        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')

        Returns:
            StockQuote object or None if error
        """
        try:
            quote_data = self.client.quote(symbol)
            if not quote_data or quote_data.get("c") is None:
                return None

            return StockQuote(
                symbol=symbol.upper(),
                current_price=quote_data.get("c", 0.0),
                change=quote_data.get("d", 0.0),
                change_percent=quote_data.get("dp", 0.0),
                high=quote_data.get("h", 0.0),
                low=quote_data.get("l", 0.0),
                open_price=quote_data.get("o", 0.0),
                previous_close=quote_data.get("pc", 0.0),
                timestamp=quote_data.get("t"),
            )
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None

    def get_company_profile(self, symbol: str) -> Optional[CompanyProfile]:
        """Get company profile information.

        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')

        Returns:
            CompanyProfile object or None if error
        """
        try:
            profile_data = self.client.company_profile2(symbol=symbol)
            if not profile_data:
                return None

            return CompanyProfile(
                symbol=symbol.upper(),
                name=profile_data.get("name", ""),
                country=profile_data.get("country"),
                currency=profile_data.get("currency"),
                exchange=profile_data.get("exchange"),
                ipo=profile_data.get("ipo"),
                market_capitalization=profile_data.get("marketCapitalization"),
                share_outstanding=profile_data.get("shareOutstanding"),
                logo=profile_data.get("logo"),
                phone=profile_data.get("phone"),
                weburl=profile_data.get("weburl"),
                finnhub_industry=profile_data.get("finnhubIndustry"),
            )
        except Exception as e:
            print(f"Error fetching profile for {symbol}: {e}")
            return None

    def get_quote_multiple(self, symbols: list[str]) -> dict[str, Optional[StockQuote]]:
        """Get quotes for multiple symbols.

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary mapping symbol to StockQuote or None
        """
        results = {}
        for symbol in symbols:
            results[symbol.upper()] = self.get_quote(symbol)
        return results
