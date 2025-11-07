"""
Custom exceptions for KSeF Client.
"""

from __future__ import annotations


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
        status_code: int | None = None,
        response_data: dict | None = None,
    ):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class KSeFValidationError(KSeFError):
    """Exception raised for validation errors."""

    pass
