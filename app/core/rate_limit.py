"""Rate limiting configuration for Barber CRM API."""
from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

# Default rate limits
DEFAULT_RATE_LIMIT = "100/minute"
STRICT_RATE_LIMIT = "10/minute"
GENEROUS_RATE_LIMIT = "1000/minute"

# Specific endpoint limits
CREATE_RATE_LIMIT = "30/minute"
UPDATE_RATE_LIMIT = "60/minute"
DELETE_RATE_LIMIT = "20/minute"
LIST_RATE_LIMIT = "100/minute"


def get_limiter() -> Limiter:
    """Get the rate limiter instance."""
    return Limiter(key_func=get_remote_address)
