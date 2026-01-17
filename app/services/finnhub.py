"""
Finnhub API client.
"""


class FinnhubClient:
    """Client for interacting with Finnhub API."""
    
    def __init__(self, api_key: str):
        """Initialize Finnhub client."""
        self.api_key = api_key
    
    def get_stock_data(self, symbol: str):
        """Get stock data for a symbol."""
        pass
