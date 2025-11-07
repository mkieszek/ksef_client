"""
Tests for KSeF data models.
"""

from datetime import datetime

from ksef_client.models import (
    ErrorResponse,
    InvoiceHeader,
    InvoiceListItem,
    InvoiceListResponse,
    InvoiceSubmissionResponse,
    SessionToken,
)


def test_session_token_model():
    """Test SessionToken model."""
    token = SessionToken(
        token="test-token",
        contextIdentifier="test-context",
        sessionId="test-session",
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
    )
    assert token.token == "test-token"
    assert token.context_identifier == "test-context"
    assert token.session_id == "test-session"
    assert token.timestamp == datetime(2024, 1, 1, 12, 0, 0)


def test_invoice_submission_response():
    """Test InvoiceSubmissionResponse model."""
    response = InvoiceSubmissionResponse(
        referenceNumber="REF-123",
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        processingCode=200,
    )
    assert response.reference_number == "REF-123"
    assert response.timestamp == datetime(2024, 1, 1, 12, 0, 0)
    assert response.processing_code == 200


def test_invoice_header():
    """Test InvoiceHeader model."""
    header = InvoiceHeader(
        invoiceNumber="INV-001",
        issueDate="2024-01-01",
        sellerNip="1234567890",
        buyerNip="0987654321",
        amountGross=1230.50,
    )
    assert header.invoice_number == "INV-001"
    assert header.issue_date == "2024-01-01"
    assert header.seller_nip == "1234567890"
    assert header.buyer_nip == "0987654321"
    assert header.amount_gross == 1230.50


def test_invoice_list_item():
    """Test InvoiceListItem model."""
    item = InvoiceListItem(
        referenceNumber="REF-123",
        invoiceNumber="INV-001",
        issueDate="2024-01-01",
        sellerName="Test Seller",
        buyerName="Test Buyer",
        amountGross=1230.50,
    )
    assert item.reference_number == "REF-123"
    assert item.invoice_number == "INV-001"
    assert item.seller_name == "Test Seller"
    assert item.buyer_name == "Test Buyer"


def test_invoice_list_response():
    """Test InvoiceListResponse model."""
    items = [
        InvoiceListItem(
            referenceNumber="REF-123",
            invoiceNumber="INV-001",
            issueDate="2024-01-01",
            sellerName="Test Seller",
            buyerName="Test Buyer",
            amountGross=1230.50,
        )
    ]
    response = InvoiceListResponse(invoices=items, totalCount=1, pageSize=10, pageOffset=0)
    assert len(response.invoices) == 1
    assert response.total_count == 1
    assert response.page_size == 10
    assert response.page_offset == 0


def test_error_response():
    """Test ErrorResponse model."""
    error = ErrorResponse(
        errorCode="ERR-001",
        errorMessage="Test error",
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
        details={"field": "value"},
    )
    assert error.error_code == "ERR-001"
    assert error.error_message == "Test error"
    assert error.timestamp == datetime(2024, 1, 1, 12, 0, 0)
    assert error.details == {"field": "value"}


def test_error_response_without_details():
    """Test ErrorResponse model without details."""
    error = ErrorResponse(
        errorCode="ERR-001",
        errorMessage="Test error",
        timestamp=datetime(2024, 1, 1, 12, 0, 0),
    )
    assert error.error_code == "ERR-001"
    assert error.details is None
