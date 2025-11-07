"""
Data models for KSeF API requests and responses.
"""

from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel, Field


class SessionToken(BaseModel):
    """Session token response from authentication."""

    token: str
    context_identifier: str = Field(alias="contextIdentifier")
    session_id: str = Field(alias="sessionId")
    timestamp: datetime


class AuthenticationRequest(BaseModel):
    """Authentication request for interactive session."""

    identifier: str
    password: str


class InvoiceHeader(BaseModel):
    """Invoice header information."""

    invoice_number: str = Field(alias="invoiceNumber")
    issue_date: str = Field(alias="issueDate")
    seller_nip: str = Field(alias="sellerNip")
    buyer_nip: str = Field(alias="buyerNip")
    amount_gross: float = Field(alias="amountGross")


class Invoice(BaseModel):
    """Full invoice data."""

    invoice_header: InvoiceHeader = Field(alias="invoiceHeader")
    invoice_xml: str = Field(alias="invoiceXml")


class InvoiceSubmissionResponse(BaseModel):
    """Response from invoice submission."""

    reference_number: str = Field(alias="referenceNumber")
    timestamp: datetime
    processing_code: int = Field(alias="processingCode")


class InvoiceQueryRequest(BaseModel):
    """Request parameters for querying invoices."""

    page_size: int = Field(default=10, alias="pageSize")
    page_offset: int = Field(default=0, alias="pageOffset")
    invoice_type: Optional[str] = Field(default=None, alias="invoiceType")
    date_from: Optional[str] = Field(default=None, alias="dateFrom")
    date_to: Optional[str] = Field(default=None, alias="dateTo")


class InvoiceListItem(BaseModel):
    """Single item in invoice list."""

    reference_number: str = Field(alias="referenceNumber")
    invoice_number: str = Field(alias="invoiceNumber")
    issue_date: str = Field(alias="issueDate")
    seller_name: str = Field(alias="sellerName")
    buyer_name: str = Field(alias="buyerName")
    amount_gross: float = Field(alias="amountGross")


class InvoiceListResponse(BaseModel):
    """Response containing list of invoices."""

    invoices: list[InvoiceListItem]
    total_count: int = Field(alias="totalCount")
    page_size: int = Field(alias="pageSize")
    page_offset: int = Field(alias="pageOffset")


class ErrorResponse(BaseModel):
    """Error response from API."""

    error_code: str = Field(alias="errorCode")
    error_message: str = Field(alias="errorMessage")
    timestamp: datetime
    details: Optional[dict[str, Any]] = None
