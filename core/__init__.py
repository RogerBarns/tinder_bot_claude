"""
Core module initialization
"""

# Import the API selector function instead of direct imports
from .api_selector import get_api_client

# Make the function available at module level
__all__ = ['get_api_client']

# For backwards compatibility, create a dynamic TinderAPIClient
def TinderAPIClient(account_id="main"):
    """
    Backwards compatibility wrapper
    Returns the appropriate API client based on configuration
    """
    return get_api_client(account_id)