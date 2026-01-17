"""
OpenAI API client.
"""


class OpenAIClient:
    """Client for interacting with OpenAI API."""
    
    def __init__(self, api_key: str):
        """Initialize OpenAI client."""
        self.api_key = api_key
    
    def generate_insight(self, prompt: str):
        """Generate insight from prompt."""
        pass
