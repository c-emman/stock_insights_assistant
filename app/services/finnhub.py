"""
Finnhub API client.
"""

import time

import finnhub

from app.core.models import CompanyProfile, StockQuote

# Curated industry symbol lists
INDUSTRY_SYMBOLS = {
    "technology": [
        "AAPL",
        "MSFT",
        "GOOGL",
        "GOOG",
        "AMZN",
        "META",
        "NVDA",
        "TSLA",
        "NFLX",
        "CRM",
        "ORCL",
        "ADBE",
        "INTC",
        "AMD",
        "CSCO",
        "IBM",
        "NOW",
        "SNOW",
        "PLTR",
        "ZM",
        "UBER",
        "LYFT",
    ],
    "finance": [
        "JPM",
        "BAC",
        "WFC",
        "C",
        "GS",
        "MS",
        "BLK",
        "SCHW",
        "AXP",
        "COF",
        "PYPL",
        "SQ",
        "V",
        "MA",
    ],
    "healthcare": [
        "JNJ",
        "UNH",
        "PFE",
        "ABT",
        "TMO",
        "ABBV",
        "LLY",
        "MRK",
        "BMY",
        "GILD",
        "AMGN",
        "BIIB",
        "REGN",
    ],
    "energy": [
        "XOM",
        "CVX",
        "COP",
        "SLB",
        "EOG",
        "MPC",
        "VLO",
        "PSX",
    ],
    "consumer": [
        "WMT",
        "TGT",
        "HD",
        "LOW",
        "NKE",
        "SBUX",
        "MCD",
        "YUM",
    ],
}

# Rate limiting constants
MAX_RETRIES = 2
RETRY_DELAY_BASE = 1.0  # seconds


class RateLimitError(Exception):
    """Raised when Finnhub rate limit is exceeded."""

    pass


class FinnhubClient:
    """Client for interacting with Finnhub API using the official SDK with rate limiting support."""

    def __init__(self, api_key: str):
        """Initialize Finnhub client.

        Args:
            api_key: Finnhub API key
        """
        self.api_key = api_key
        self._client = finnhub.Client(api_key=api_key)

    def _call_with_retry(self, func, *args, **kwargs):
        """Execute API call with retry logic for rate limits.

        Args:
            func: The API function to call
            *args, **kwargs: Arguments to pass to the function

        Returns:
            API response

        Raises:
            RateLimitError: If rate limit exceeded after retries
            Exception: For other errors
        """
        last_error = None

        for attempt in range(MAX_RETRIES + 1):
            try:
                return func(*args, **kwargs)
            except finnhub.FinnhubAPIException as e:
                # Check for rate limit (429)
                if "429" in str(e) or "rate limit" in str(e).lower():
                    last_error = e
                    if attempt < MAX_RETRIES:
                        delay = RETRY_DELAY_BASE * (2**attempt)
                        print(
                            f"Rate limited, retrying in {delay}s (attempt {attempt + 1}/{MAX_RETRIES})"
                        )
                        time.sleep(delay)
                        continue
                    raise RateLimitError(
                        "Finnhub rate limit exceeded. Please try again later."
                    ) from e
                raise
            except Exception as e:
                # For connection errors, retry once
                if attempt < MAX_RETRIES and (
                    "connection" in str(e).lower() or "timeout" in str(e).lower()
                ):
                    delay = RETRY_DELAY_BASE
                    print(f"Connection error, retrying in {delay}s...")
                    time.sleep(delay)
                    continue
                raise

        raise last_error or Exception("Max retries exceeded")

    def get_quote(self, symbol: str) -> StockQuote | None:
        """Get real-time quote for a stock symbol.

        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')

        Returns:
            StockQuote object or None if not found/error
        """
        try:
            quote_data = self._call_with_retry(self._client.quote, symbol.upper())

            if not quote_data or quote_data.get("c") is None or quote_data.get("c") == 0:
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
        except RateLimitError:
            raise
        except Exception as e:
            print(f"Error fetching quote for {symbol}: {e}")
            return None

    def get_company_profile(self, symbol: str) -> CompanyProfile | None:
        """Get company profile information.

        Args:
            symbol: Stock symbol (e.g., 'AAPL', 'TSLA')

        Returns:
            CompanyProfile object or None if not found/error
        """
        try:
            profile_data = self._call_with_retry(
                self._client.company_profile2, symbol=symbol.upper()
            )

            if not profile_data or not profile_data.get("name"):
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
        except RateLimitError:
            raise
        except Exception as e:
            print(f"Error fetching profile for {symbol}: {e}")
            return None

    def get_quote_multiple(self, symbols: list[str]) -> dict[str, StockQuote | None]:
        """Get quotes for multiple symbols.

        Args:
            symbols: List of stock symbols

        Returns:
            Dictionary mapping symbol to StockQuote or None
        """
        results = {}
        for symbol in symbols:
            try:
                results[symbol.upper()] = self.get_quote(symbol)
            except RateLimitError:
                # If rate limited, return what we have so far
                print(f"Rate limited while fetching {symbol}, returning partial results")
                break
        return results

    def get_top_movers_by_industry(
        self,
        industry: str,
        direction: str = "gainers",
        limit: int = 3,
    ) -> list[dict]:
        """Get top gainers or losers by industry.

        Args:
            industry: Industry name (e.g., 'technology', 'finance')
            direction: 'gainers' or 'losers'
            limit: Number to return

        Returns:
            List of dicts with symbol and quote data, sorted by change_percent
        """
        symbols = INDUSTRY_SYMBOLS.get(industry.lower(), [])
        if not symbols:
            return []

        # Get quotes for all symbols
        quotes = self.get_quote_multiple(symbols)

        # Filter valid quotes
        valid_quotes = []
        for symbol, quote in quotes.items():
            if quote is not None and quote.change_percent is not None:
                valid_quotes.append(
                    {
                        "symbol": symbol,
                        "quote": quote,
                        "change_percent": quote.change_percent,
                    }
                )

        # Sort by change_percent
        reverse = direction == "gainers"
        sorted_quotes = sorted(valid_quotes, key=lambda x: x["change_percent"], reverse=reverse)

        # Format and return top N
        return [
            {
                "symbol": item["symbol"],
                "current_price": item["quote"].current_price,
                "change": item["quote"].change,
                "change_percent": item["quote"].change_percent,
                "high": item["quote"].high,
                "low": item["quote"].low,
            }
            for item in sorted_quotes[:limit]
        ]
