"""
Basic tests for KSeF Client.
"""

import pytest

from ksef_client import KSeFAPIError, KSeFAuthError, KSeFClient, KSeFError


def test_client_initialization():
    """Test that KSeF client can be initialized."""
    client = KSeFClient()
    assert client.base_url == "https://ksef-demo.mf.gov.pl/api"
    assert client.timeout == 30.0
    assert client.verify_ssl is True
    client.close()


def test_client_initialization_custom():
    """Test client initialization with custom parameters."""
    client = KSeFClient(base_url="https://ksef.mf.gov.pl/api", timeout=60.0, verify_ssl=False)
    assert client.base_url == "https://ksef.mf.gov.pl/api"
    assert client.timeout == 60.0
    assert client.verify_ssl is False
    client.close()


def test_client_context_manager():
    """Test that client works as context manager."""
    with KSeFClient() as client:
        assert client is not None
        assert client.base_url == "https://ksef-demo.mf.gov.pl/api"


def test_submit_invoice_requires_authentication():
    """Test that submitting invoice requires authentication."""
    client = KSeFClient()
    with pytest.raises(KSeFAuthError, match="Authentication required"):
        client.submit_invoice("<invoice>test</invoice>")
    client.close()


def test_query_invoices_requires_authentication():
    """Test that querying invoices requires authentication."""
    client = KSeFClient()
    with pytest.raises(KSeFAuthError, match="Authentication required"):
        client.query_invoices()
    client.close()


def test_get_invoice_requires_authentication():
    """Test that getting invoice requires authentication."""
    client = KSeFClient()
    with pytest.raises(KSeFAuthError, match="Authentication required"):
        client.get_invoice("test-reference")
    client.close()


def test_terminate_session_requires_authentication():
    """Test that terminating session requires authentication."""
    client = KSeFClient()
    with pytest.raises(KSeFAuthError, match="No active session"):
        client.terminate_session()
    client.close()


def test_exception_hierarchy():
    """Test that exception hierarchy is correct."""
    assert issubclass(KSeFAuthError, KSeFError)
    assert issubclass(KSeFAPIError, KSeFError)
    assert issubclass(KSeFError, Exception)


def test_api_error_with_status_code():
    """Test KSeFAPIError can store status code and response data."""
    error = KSeFAPIError("Test error", status_code=400, response_data={"error": "bad request"})
    assert error.status_code == 400
    assert error.response_data == {"error": "bad request"}
    assert str(error) == "Test error"


def test_headers_without_token():
    """Test headers are correct without authentication."""
    client = KSeFClient()
    headers = client._get_headers()
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"
    assert "SessionToken" not in headers
    client.close()


def test_headers_with_token():
    """Test headers include token when authenticated."""
    client = KSeFClient()
    client._session_token = "test-token-123"
    headers = client._get_headers()
    assert headers["SessionToken"] == "test-token-123"
    client.close()
