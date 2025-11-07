"""
Custom exceptions for KSeF Client.
"""

from typing import Optional


class KSeFError(Exception):
    """Base exception for all KSeF client errors."""

    pass


class KSeFAuthError(KSeFError):
    """Exception raised for authentication errors."""

    pass


class KSeFAPIError(KSeFError):
    """Exception raised for API errors."""

    def __init__(
        self,
        message: str,
        status_code: Optional[int] = None,
        response_data: Optional[dict] = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class KSeFValidationError(KSeFError):
    """Exception raised for validation errors."""

    pass
