# KSeF Client Examples

This directory contains example scripts demonstrating how to use the KSeF Client library.

## Prerequisites

Before running the examples, make sure you have:

1. Installed the ksef-client package:
   ```bash
   uv pip install -e ..
   # or
   pip install -e ..
   ```

2. Set up your KSeF credentials as environment variables:
   ```bash
   export KSEF_NIP="your-company-nip"
   export KSEF_TOKEN="your-authentication-token"
   ```

   On Windows:
   ```cmd
   set KSEF_NIP=your-company-nip
   set KSEF_TOKEN=your-authentication-token
   ```

## Examples

### 01_authenticate.py - Interactive Authentication

Demonstrates how to authenticate with the KSeF API and manage sessions.

```bash
python 01_authenticate.py
```

**What it does:**
- Authenticates using NIP and token
- Displays session information
- Terminates the session

### 02_send_invoice.py - Send Invoice

Shows how to submit an invoice to the KSeF system.

```bash
python 02_send_invoice.py
```

**What it does:**
- Authenticates with KSeF
- Submits a sample invoice
- Displays the submission response with reference number

**Note:** The example uses a simplified sample invoice. Real invoices must follow the official FA_VAT schema.

### 03_query_invoices.py - Query Incoming Invoices

Demonstrates how to query and retrieve incoming invoices.

```bash
python 03_query_invoices.py
```

**What it does:**
- Authenticates with KSeF
- Queries invoices from the last 30 days
- Displays invoice list with pagination info
- Shows how to handle pagination for large result sets

## Tips

- All examples use the **demo environment** (`https://ksef-demo.mf.gov.pl/api`)
- For production use, update the `base_url` parameter in the examples
- Check the main README.md for more detailed documentation
- Error handling is included in all examples for reference

## Getting Demo Credentials

To test with the KSeF demo environment:

1. Visit the [KSeF Demo Portal](https://ksef-demo.mf.gov.pl/)
2. Register a test account
3. Obtain your demo NIP and authentication token
4. Use these credentials in the examples

## Troubleshooting

**"Authentication failed" error:**
- Verify your NIP and token are correct
- Check if you're using demo credentials with the demo environment
- Ensure environment variables are set correctly

**"Module not found" error:**
- Make sure you've installed the package: `pip install -e ..`
- Check that you're in the correct directory
- Verify your Python path includes the src directory

**SSL/Certificate errors:**
- Set `verify_ssl=False` in KSeFClient initialization (not recommended for production)
- Update your system's CA certificates

## Next Steps

After running these examples:

1. Review the code to understand the API flow
2. Modify the examples for your specific use case
3. Check the API documentation for additional endpoints
4. Implement proper error handling in your production code
5. Add invoice validation before submission
