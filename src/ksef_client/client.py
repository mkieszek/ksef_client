"""
Main KSeF API Client implementation.
"""

import logging
from typing import Any

import httpx

from ksef_client.exceptions import KSeFAPIError, KSeFAuthError
from ksef_client.models import (
    InvoiceListResponse,
    InvoiceSubmissionResponse,
    SessionToken,
)

logger = logging.getLogger(__name__)


class KSeFClient:
    """
    Client for interacting with the Polish National e-Invoicing System (KSeF) API.

    This client provides methods for:
    - Authentication (interactive and token-based)
    - Submitting invoices
    - Querying invoices
    - Managing sessions
    """

    def __init__(
        self,
        base_url: str = "https://ksef-demo.mf.gov.pl/api",
        timeout: float = 30.0,
        verify_ssl: bool = True,
    ):
        """
        Initialize KSeF client.

        Args:
            base_url: Base URL for KSeF API (defaults to demo environment)
            timeout: Request timeout in seconds
            verify_ssl: Whether to verify SSL certificates
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self._session_token: str | None = None
        self._client = httpx.Client(timeout=timeout, verify=verify_ssl)

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self):
        """Close the HTTP client."""
        self._client.close()

    def _get_headers(self) -> dict[str, str]:
        """Get request headers with authentication if available."""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self._session_token:
            headers["SessionToken"] = self._session_token
        return headers

    def _handle_response(self, response: httpx.Response) -> dict[str, Any]:
        """
        Handle API response and raise appropriate exceptions for errors.

        Args:
            response: HTTP response object

        Returns:
            Parsed JSON response data

        Raises:
            KSeFAPIError: If the API returns an error response
        """
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as e:
            error_data = None
            try:
                error_data = response.json()
            except Exception:
                pass

            error_msg = f"API request failed with status {response.status_code}"
            if error_data:
                error_msg = f"{error_msg}: {error_data}"

            raise KSeFAPIError(
                error_msg, status_code=response.status_code, response_data=error_data
            ) from e

        return response.json()

    def authenticate_interactive(self, nip: str, token: str) -> SessionToken:
        """
        Authenticate using interactive session credentials.

        Args:
            nip: Tax identification number (NIP)
            token: Authentication token

        Returns:
            SessionToken object containing session information

        Raises:
            KSeFAuthError: If authentication fails
        """
        url = f"{self.base_url}/online/Session/InitSigned"

        payload = {
            "contextIdentifier": {"type": "onip", "identifier": nip},
            "contextName": {"type": "AuthenticationToken", "value": token},
        }

        try:
            response = self._client.post(
                url,
                json=payload,
                headers=self._get_headers(),
            )
            data = self._handle_response(response)

            # Extract session token from response
            session_token = SessionToken(
                token=data.get("sessionToken", ""),
                contextIdentifier=data.get("contextIdentifier", ""),
                sessionId=data.get("sessionId", ""),
                timestamp=data.get("timestamp", ""),
            )

            self._session_token = session_token.token
            logger.info(f"Successfully authenticated with session ID: {session_token.session_id}")

            return session_token

        except KSeFAPIError as e:
            raise KSeFAuthError(f"Authentication failed: {e}") from e
        except Exception as e:
            raise KSeFAuthError(f"Authentication error: {e}") from e

    def terminate_session(self) -> dict[str, Any]:
        """
        Terminate the current session.

        Returns:
            Response data from session termination

        Raises:
            KSeFAPIError: If session termination fails
        """
        if not self._session_token:
            raise KSeFAuthError("No active session to terminate")

        url = f"{self.base_url}/online/Session/Terminate"

        response = self._client.post(url, headers=self._get_headers())
        data = self._handle_response(response)

        self._session_token = None
        logger.info("Session terminated successfully")

        return data

    def submit_invoice(self, invoice_xml: str) -> InvoiceSubmissionResponse:
        """
        Submit an invoice to KSeF.

        Args:
            invoice_xml: XML content of the invoice

        Returns:
            InvoiceSubmissionResponse with reference number and status

        Raises:
            KSeFAuthError: If not authenticated
            KSeFAPIError: If submission fails
        """
        if not self._session_token:
            raise KSeFAuthError("Authentication required. Call authenticate_interactive() first.")

        url = f"{self.base_url}/online/Invoice/Send"

        payload = {
            "invoiceHash": {
                "hashSHA": {
                    "algorithm": "SHA-256",
                    "encoding": "Base64",
                    "value": "",  # Should be calculated from invoice_xml
                },
                "fileSize": len(invoice_xml),
            },
            "invoicePayload": {"type": "plain", "invoiceBody": invoice_xml},
        }

        response = self._client.post(
            url,
            json=payload,
            headers=self._get_headers(),
        )
        data = self._handle_response(response)

        return InvoiceSubmissionResponse(
            referenceNumber=data.get("referenceNumber", ""),
            timestamp=data.get("timestamp", ""),
            processingCode=data.get("processingCode", 0),
        )

    def query_invoices(
        self,
        page_size: int = 10,
        page_offset: int = 0,
        date_from: str | None = None,
        date_to: str | None = None,
    ) -> InvoiceListResponse:
        """
        Query incoming invoices.

        Args:
            page_size: Number of invoices per page
            page_offset: Page offset for pagination
            date_from: Start date for filtering (format: YYYY-MM-DD)
            date_to: End date for filtering (format: YYYY-MM-DD)

        Returns:
            InvoiceListResponse containing list of invoices

        Raises:
            KSeFAuthError: If not authenticated
            KSeFAPIError: If query fails
        """
        if not self._session_token:
            raise KSeFAuthError("Authentication required. Call authenticate_interactive() first.")

        url = f"{self.base_url}/online/Query/Invoice/Async/Init"

        payload = {
            "queryCriteria": {
                "subjectType": "subject2",
                "type": "incremental",
                "acquisitionTimestampThreshold": date_from or "",
                "invoicingDateFrom": date_from or "",
                "invoicingDateTo": date_to or "",
            },
            "pageSize": page_size,
            "pageOffset": page_offset,
        }

        response = self._client.post(
            url,
            json=payload,
            headers=self._get_headers(),
        )
        data = self._handle_response(response)

        # Parse response into InvoiceListResponse
        invoices_data = data.get("invoiceHeaderList", [])

        return InvoiceListResponse(
            invoices=invoices_data,
            totalCount=data.get("numberOfElements", 0),
            pageSize=page_size,
            pageOffset=page_offset,
        )

    def get_invoice(self, reference_number: str) -> dict[str, Any]:
        """
        Get detailed information about a specific invoice.

        Args:
            reference_number: Invoice reference number

        Returns:
            Invoice data

        Raises:
            KSeFAuthError: If not authenticated
            KSeFAPIError: If request fails
        """
        if not self._session_token:
            raise KSeFAuthError("Authentication required. Call authenticate_interactive() first.")

        url = f"{self.base_url}/online/Invoice/Get/{reference_number}"

        response = self._client.get(url, headers=self._get_headers())
        return self._handle_response(response)
