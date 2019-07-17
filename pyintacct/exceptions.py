class IntacctException(Exception):
    """Base exception for Intacct API errors"""


class IntacctServerError(IntacctException):
    """Raised when a 500-level response is received"""
