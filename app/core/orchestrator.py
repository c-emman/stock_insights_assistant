"""
Orchestrator for coordinating services.
"""

import os

from app.core.models import QueryResponse
from app.services.finnhub import FinnhubClient
from app.services.openai_client import OpenAIClient


class Orchestrator:
    """Main orchestrator class."""

    def __init__(
        self,
        finnhub_api_key: str | None = None,
        openai_api_key: str | None = None,
    ):
        """Initialize orchestrator.

        Args:
            finnhub_api_key: Finnhub API key (defaults to env var)
            openai_api_key: OpenAI API key (defaults to env var)
        """
        finnhub_key = finnhub_api_key or os.getenv("FINNHUB_API_KEY")
        openai_key = openai_api_key or os.getenv("OPENAI_API_KEY")

        if not finnhub_key:
            raise ValueError("FINNHUB_API_KEY not provided or found in environment")
        if not openai_key:
            raise ValueError("OPENAI_API_KEY not provided or found in environment")

        self.finnhub_client = FinnhubClient(api_key=finnhub_key)
        self.openai_client = OpenAIClient(api_key=openai_key)

    def process_query(self, user_query: str) -> QueryResponse:
        """Process user query and return response.

        Args:
            user_query: Natural language query from user

        Returns:
            QueryResponse with formatted answer and metadata
        """
        # Step 1: Parse query with AI
        parsed = self.openai_client.parse_query(user_query)

        # Handle both Pydantic model and dict responses
        if hasattr(parsed, "intent"):
            intent = parsed.intent.value if hasattr(parsed.intent, "value") else str(parsed.intent)
            industry = parsed.industry.value if parsed.industry and hasattr(parsed.industry, "value") else parsed.industry
            symbols = parsed.symbols or []
            direction = parsed.direction.value if parsed.direction and hasattr(parsed.direction, "value") else parsed.direction
        else:
            intent = parsed.get("intent", "unsupported")
            industry = parsed.get("industry")
            symbols = parsed.get("symbols", [])
            direction = parsed.get("direction")

        # Step 2: Route based on intent
        if intent == "top_gainers":
            return self._handle_top_gainers(industry, direction)

        elif intent == "top_losers":
            return self._handle_top_losers(industry, direction)

        elif intent == "quote":
            if symbols:
                return self._handle_quote(symbols[0])
            else:
                return QueryResponse(
                    response="I couldn't identify a stock symbol in your query. Please specify a stock (e.g., 'How is AAPL doing?')",
                    symbols=[],
                )

        elif intent == "compare":
            if len(symbols) >= 2:
                return self._handle_compare(symbols[:2])
            else:
                return QueryResponse(
                    response="Please specify at least two stocks to compare (e.g., 'Compare AAPL and TSLA')",
                    symbols=[],
                )

        else:
            # Unsupported query
            unsupported_response = self.openai_client.format_response(
                intent="unsupported", data={}
            )
            return QueryResponse(
                response=unsupported_response,
                symbols=[],
            )

    def _handle_top_gainers(
        self, industry: str | None, direction: str | None
    ) -> QueryResponse:
        """Handle top gainers query."""
        if not industry:
            industry = "technology"  # Default to tech

        movers = self.finnhub_client.get_top_movers_by_industry(
            industry=industry, direction="gainers", limit=3
        )

        if not movers:
            return QueryResponse(
                response=f"Sorry, I couldn't find any gainers in {industry} at the moment.",
                symbols=[],
            )

        # Format response with AI
        response_text = self.openai_client.format_response(
            intent="top_gainers", data={"movers": movers}, industry=industry
        )

        return QueryResponse(
            response=response_text,
            symbols=[m["symbol"] for m in movers],
            top_gainers=movers,
        )

    def _handle_top_losers(
        self, industry: str | None, direction: str | None
    ) -> QueryResponse:
        """Handle top losers query."""
        if not industry:
            industry = "technology"  # Default to tech

        movers = self.finnhub_client.get_top_movers_by_industry(
            industry=industry, direction="losers", limit=3
        )

        if not movers:
            return QueryResponse(
                response=f"Sorry, I couldn't find any losers in {industry} at the moment.",
                symbols=[],
            )

        response_text = self.openai_client.format_response(
            intent="top_losers", data={"movers": movers}, industry=industry
        )

        return QueryResponse(
            response=response_text,
            symbols=[m["symbol"] for m in movers],
            top_gainers=movers,  # Reusing field name for consistency
        )

    def _handle_quote(self, symbol: str) -> QueryResponse:
        """Handle single stock quote query."""
        quote = self.finnhub_client.get_quote(symbol)
        profile = self.finnhub_client.get_company_profile(symbol)

        if not quote:
            return QueryResponse(
                response=f"Sorry, I couldn't fetch data for {symbol}.",
                symbols=[symbol],
            )

        data = {
            "symbol": symbol,
            "quote": {
                "current_price": quote.current_price,
                "change": quote.change,
                "change_percent": quote.change_percent,
                "high": quote.high,
                "low": quote.low,
                "open_price": quote.open_price,
                "previous_close": quote.previous_close,
            },
        }

        if profile:
            data["profile"] = {
                "name": profile.name,
                "market_capitalization": profile.market_capitalization,
                "exchange": profile.exchange,
            }

        response_text = self.openai_client.format_response(
            intent="quote", data=data
        )

        return QueryResponse(response=response_text, symbols=[symbol])

    def _handle_compare(self, symbols: list[str]) -> QueryResponse:
        """Handle stock comparison query."""
        quotes = self.finnhub_client.get_quote_multiple(symbols)
        profiles = {}

        for symbol in symbols:
            profile = self.finnhub_client.get_company_profile(symbol)
            if profile:
                profiles[symbol] = profile

        comparison_data = {}
        for symbol, quote in quotes.items():
            if quote:
                comparison_data[symbol] = {
                    "current_price": quote.current_price,
                    "change": quote.change,
                    "change_percent": quote.change_percent,
                    "high": quote.high,
                    "low": quote.low,
                    "open_price": quote.open_price,
                }
                if symbol in profiles:
                    p = profiles[symbol]
                    comparison_data[symbol]["name"] = p.name
                    comparison_data[symbol]["market_cap"] = p.market_capitalization

        response_text = self.openai_client.format_response(
            intent="compare", data=comparison_data
        )

        return QueryResponse(response=response_text, symbols=symbols)
