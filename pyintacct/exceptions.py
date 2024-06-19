class IntacctException(Exception):
    """Base exception for Intacct API errors"""


class IntacctRequestError(IntacctException):
    """Raised when a 400-level response is received"""


class RateLimitError(IntacctRequestError):
    """Raised when a 429/rate limit response is received"""


class IntacctServerError(IntacctException):
    """Raised when a 500-level response is received"""
