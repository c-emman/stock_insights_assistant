"""
OpenAI API client.
"""

import json

from openai import OpenAI

from app.core.models import Intent, ParsedQuery


class OpenAIClient:
    """Client for interacting with OpenAI API."""

    def __init__(self, api_key: str):
        """Initialize OpenAI client.

        Args:
            api_key: OpenAI API key
        """
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)

    def parse_query(self, query: str) -> dict:
        """Parse user query to extract intent, industry, and symbols.

        Args:
            query: User's natural language query

        Returns:
            Dictionary with 'intent', 'industry', 'symbols', 'direction'
        """
        system_prompt = """
            You are a financial query parser for a stock insights assistant.

            This assistant can ONLY help with:
            1. Top gainers/losers by industry (technology, finance, healthcare, energy, consumer)
            2. Stock quotes for specific companies/symbols
            3. Comparing two or more stocks

            Extract the following from user queries:
            - intent: One of 'top_gainers', 'top_losers', 'quote', 'compare', 'unsupported'
            - industry: One of 'technology', 'finance', 'healthcare', 'energy', 'consumer', or null
            - symbols: List of stock ticker symbols (ALWAYS convert company names to their stock symbols)
            - direction: 'gainers' or 'losers' if applicable, otherwise null

            IMPORTANT: Always convert company names to their stock ticker symbols:
            - Apple, Apple Inc -> AAPL
            - Tesla, Tesla Inc -> TSLA
            - Microsoft -> MSFT
            - Google, Alphabet -> GOOGL
            - Amazon -> AMZN
            - Meta, Facebook -> META
            - Netflix -> NFLX
            - Nvidia -> NVDA

            Use 'unsupported' intent for ANY request that is:
            - Not related to stocks/finance (e.g., weather, jokes, general knowledge)
            - Asking for something the assistant cannot do (e.g., trading, predictions, news)
            - Vague or unclear about what stock information is needed

            Examples:
            - "What are the top gainers in tech?" -> top_gainers, industry: technology
            - "How is Apple doing?" -> quote, symbols: ["AAPL"]
            - "How is AAPL doing?" -> quote, symbols: ["AAPL"]
            - "Compare Tesla and Apple" -> compare, symbols: ["TSLA", "AAPL"]
            - "Compare MSFT and GOOGL" -> compare, symbols: ["MSFT", "GOOGL"]
            - "What's the weather?" -> unsupported
            - "What stocks should I buy?" -> unsupported
        """

        try:
            response = self.client.responses.parse(
                model="gpt-4.1",
                input=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query},
                ],
                text_format=ParsedQuery,
            )

            # Return the parsed response directly
            # The model handles unsupported queries by setting intent=unsupported
            return response.output_parsed

        except Exception as e:
            print(f"Error parsing query: {e}")
            # Fallback - treat as unsupported
            return ParsedQuery(intent=Intent.UNSUPPORTED)

    def format_response(
        self,
        intent: str,
        data: dict,
        industry: str | None = None,
    ) -> str:
        """Format response using AI based on intent and data.

        Args:
            intent: Query intent (top_gainers, quote, etc.)
            data: Data to format (gainers, quotes, news, etc.)
            industry: Industry name if applicable

        Returns:
            Formatted response string
        """
        if intent == "top_gainers" or intent == "top_losers":
            return self._format_movers_response(data, industry, intent)

        elif intent == "quote":
            return self._format_quote_response(data)

        elif intent == "compare":
            return self._format_compare_response(data)

        elif intent == "unsupported":
            return self._format_unsupported_response()

        else:
            return self._format_unsupported_response()

    def _format_movers_response(
        self, movers: list, industry: str | None, intent: str
    ) -> str:
        """Format top gainers/losers response."""
        direction = "gainers" if intent == "top_gainers" else "losers"
        industry_text = f" in {industry.title()}" if industry else ""

        prompt = f"""Format this {direction} data{industry_text} as a brief response (2-3 sentences max):

            {json.dumps(movers, indent=2)}

            Format like: Top {direction}{industry_text}: SYMBOL at $XX.XX (+X.X%), SYMBOL at $XX.XX (+X.X%)...
            Be concise - just list the stocks with prices and % changes.
        """

        try:
            response = self.client.responses.create(
                model="gpt-4.1-mini",
                input=[{"role": "user", "content": prompt}],
            )
            return response.output_text
        except Exception as e:
            print(f"Error formatting movers response: {e}")
            return self._fallback_format_movers(movers, industry, direction)

    def _format_quote_response(self, data: dict) -> str:
        """Format single stock quote response."""

        prompt = f"""Format this stock data as a brief response (2-3 sentences max):

            {json.dumps(data, indent=2)}

            Format like: "Company (SYMBOL) is trading at $XX.XX, up/down X.X% today. Opened at $XX.XX with a day range of $XX.XX - $XX.XX."
            Be concise - no commentary, just the key facts.
        """

        try:
            response = self.client.responses.create(
                model="gpt-4.1-mini",
                input=[{"role": "user", "content": prompt}],
            )
            return response.output_text
        except Exception as e:
            print(f"Error formatting quote response: {e}")
            quote = data.get("quote", {})
            return f"{data.get('symbol')} is trading at ${quote.get('current_price', 0):.2f} ({quote.get('change_percent', 0):+.2f}%)"

    def _format_compare_response(self, data: dict) -> str:
        """Format comparison response."""
        symbols = list(data.keys())
        
        if len(symbols) < 2:
            return "Unable to fetch comparison data for the requested stocks."
        
        prompt = f"""Format this stock comparison as a brief response (3-4 lines max):

            {json.dumps(data, indent=2)}

            Format like:
            "{symbols[0]} vs {symbols[1]} comparison:
            - SYMBOL: $XX.XX (+X.X%), Market Cap: $XXB
            - SYMBOL: $XX.XX (+X.X%), Market Cap: $XXB
            One sentence summary of which is performing better."

            Be concise - bullet points with key metrics, brief conclusion.
        """

        try:
            response = self.client.responses.create(
                model="gpt-4.1-mini",
                input=[{"role": "user", "content": prompt}],
            )
            return response.output_text
        except Exception as e:
            print(f"Error formatting compare response: {e}")
            return "Comparison data available."

    def _format_unsupported_response(self) -> str:
        """Format response for unsupported queries."""
        return (
            "I'm a stock insights assistant and can only help with:\n\n"
            "• **Top gainers/losers** - e.g., \"What are the top gainers in tech?\"\n"
            "• **Stock quotes** - e.g., \"How is AAPL doing?\" or \"Get me the TSLA quote\"\n"
            "• **Stock comparisons** - e.g., \"Compare MSFT and GOOGL\"\n\n"
            "Please try one of these queries!"
        )

    def _fallback_format_movers(
        self, movers: list, industry: str | None, direction: str
    ) -> str:
        """Fallback formatting for movers if AI fails."""
        industry_text = f" in {industry}" if industry else ""
        lines = [f"Top {direction}{industry_text}:"]
        for mover in movers:
            lines.append(
                f"- {mover['symbol']}: ${mover['current_price']:.2f} ({mover['change_percent']:+.2f}%)"
            )
        return "\n".join(lines)
