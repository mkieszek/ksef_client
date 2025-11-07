# KSeF Client

A modern Python client library for the Polish National e-Invoicing System (Krajowy System e-Faktur - KSeF).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)

## 📋 Overview

KSeF Client is a Python library that provides a clean, modern interface to interact with the Polish National e-Invoicing System (KSeF). It simplifies authentication, invoice submission, and invoice querying operations through a well-designed API.

### Key Features

- 🔐 **Interactive Authentication** - Secure session management with token-based authentication
- 📄 **Invoice Submission** - Easy-to-use methods for submitting invoices to KSeF
- 🔍 **Invoice Querying** - Query and retrieve incoming invoices with filtering and pagination
- 🛠️ **Modern Python** - Built with modern Python practices (type hints, Pydantic models, async-ready)
- 📦 **Easy Installation** - Installable via pip with minimal dependencies
- 🧪 **Demo & Production** - Support for both demo and production KSeF environments

## 🚀 Quick Start

### Installation

#### Using uv (Recommended)

[uv](https://github.com/astral-sh/uv) is a fast Python package installer and resolver.

```bash
# Install uv if you haven't already
pip install uv

# Create a new project and install ksef-client
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e .
```

#### Using pip

```bash
# Install from source
pip install -e .

# Or install from PyPI (once published)
pip install ksef-client
```

### Basic Usage

```python
from ksef_client import KSeFClient

# Create client (demo environment)
client = KSeFClient(base_url="https://ksef-demo.mf.gov.pl/api")

# Authenticate
session = client.authenticate_interactive(
    nip="1234567890",
    token="your-auth-token"
)

# Submit an invoice
response = client.submit_invoice(invoice_xml="<invoice>...</invoice>")
print(f"Invoice submitted: {response.reference_number}")

# Query invoices
invoices = client.query_invoices(
    page_size=10,
    date_from="2025-01-01",
    date_to="2025-01-31"
)

# Terminate session
client.terminate_session()
client.close()
```

## 📚 Documentation

### Environment Setup

Before using the KSeF client, you need to set up your credentials:

```bash
export KSEF_NIP="your-company-nip"
export KSEF_TOKEN="your-authentication-token"
```

### API Environments

**Demo Environment (for testing):**
```python
client = KSeFClient(base_url="https://ksef-demo.mf.gov.pl/api")
```

**Production Environment:**
```python
client = KSeFClient(base_url="https://ksef.mf.gov.pl/api")
```

### Examples

The `examples/` directory contains ready-to-run scripts demonstrating common use cases:

#### 1. Authentication (`examples/01_authenticate.py`)

```bash
python examples/01_authenticate.py
```

Demonstrates how to:
- Authenticate with KSeF using NIP and token
- Manage session lifecycle
- Handle authentication errors

#### 2. Send Invoice (`examples/02_send_invoice.py`)

```bash
python examples/02_send_invoice.py
```

Shows how to:
- Submit an invoice to KSeF
- Handle the submission response
- Process reference numbers

#### 3. Query Invoices (`examples/03_query_invoices.py`)

```bash
python examples/03_query_invoices.py
```

Demonstrates:
- Querying incoming invoices
- Filtering by date range
- Pagination handling
- Processing invoice lists

## 🏗️ Project Structure

```
ksef_client/
├── src/
│   └── ksef_client/
│       ├── __init__.py          # Package initialization
│       ├── client.py            # Main KSeF API client
│       ├── models.py            # Pydantic data models
│       └── exceptions.py        # Custom exceptions
├── examples/
│   ├── 01_authenticate.py       # Authentication example
│   ├── 02_send_invoice.py       # Invoice submission example
│   └── 03_query_invoices.py    # Invoice querying example
├── tests/                       # Test suite (to be expanded)
├── pyproject.toml              # Project configuration
├── LICENSE                     # MIT License
└── README.md                   # This file
```

## 🛠️ Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/mkieszek/ksef_client.git
cd ksef_client

# Install uv
pip install uv

# Create virtual environment and install dependencies
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv pip install -e ".[dev]"
```

### Code Quality Tools

This project uses modern Python tooling:

#### Ruff (Linting & Formatting)

```bash
# Check code style
ruff check .

# Format code
ruff format .

# Fix auto-fixable issues
ruff check --fix .
```

#### Type Checking with mypy

```bash
mypy src/ksef_client
```

#### Running Tests

```bash
# Run tests with coverage
pytest

# Run tests with verbose output
pytest -v

# Run specific test file
pytest tests/test_client.py
```

### Configuration

All tool configurations are centralized in `pyproject.toml`:
- Ruff rules and formatting options
- Pytest settings
- Mypy type checking configuration
- Package metadata

## 📖 API Reference

### KSeFClient

The main client class for interacting with KSeF API.

#### Methods

##### `__init__(base_url, timeout, verify_ssl)`
Initialize the KSeF client.

**Parameters:**
- `base_url` (str): Base URL for KSeF API
- `timeout` (float): Request timeout in seconds (default: 30.0)
- `verify_ssl` (bool): Whether to verify SSL certificates (default: True)

##### `authenticate_interactive(nip, token)`
Authenticate using interactive session credentials.

**Parameters:**
- `nip` (str): Tax identification number
- `token` (str): Authentication token

**Returns:** `SessionToken` object

##### `submit_invoice(invoice_xml)`
Submit an invoice to KSeF.

**Parameters:**
- `invoice_xml` (str): XML content of the invoice

**Returns:** `InvoiceSubmissionResponse` object

##### `query_invoices(page_size, page_offset, date_from, date_to)`
Query incoming invoices.

**Parameters:**
- `page_size` (int): Number of invoices per page (default: 10)
- `page_offset` (int): Page offset for pagination (default: 0)
- `date_from` (str): Start date (format: YYYY-MM-DD)
- `date_to` (str): End date (format: YYYY-MM-DD)

**Returns:** `InvoiceListResponse` object

##### `terminate_session()`
Terminate the current session.

**Returns:** Response data from session termination

##### `close()`
Close the HTTP client connection.

### Exception Classes

- `KSeFError` - Base exception for all KSeF errors
- `KSeFAuthError` - Authentication-related errors
- `KSeFAPIError` - API request errors

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 style guide (enforced by Ruff)
- Add type hints to all functions
- Write tests for new features
- Update documentation as needed
- Run linters before committing

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Resources

- [KSeF Official Documentation](https://www.gov.pl/web/kas/krajowy-system-e-faktur)
- [KSeF Demo Environment](https://ksef-demo.mf.gov.pl/)
- [KSeF OpenAPI Specification](https://ksef-demo.mf.gov.pl/docs/v2/openapi.json)

## ⚠️ Disclaimer

This is an unofficial client library and is not affiliated with or endorsed by the Polish Ministry of Finance. Use at your own risk and ensure compliance with all applicable regulations.

## 🆘 Support

For issues, questions, or contributions:
- Open an issue on [GitHub](https://github.com/mkieszek/ksef_client/issues)
- Check existing documentation and examples
- Review the KSeF official documentation

## 🗺️ Roadmap

- [ ] Add comprehensive test suite
- [ ] Implement async/await support
- [ ] Add invoice validation utilities
- [ ] Support for additional KSeF endpoints
- [ ] CLI tool for common operations
- [ ] Publish to PyPI
- [ ] Add more examples and tutorials
- [ ] Docker container for easy deployment