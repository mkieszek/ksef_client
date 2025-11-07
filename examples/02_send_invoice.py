"""
Example: Send Invoice to KSeF

This example demonstrates how to submit an invoice to the KSeF system.
"""

import os
import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ksef_client import KSeFAPIError, KSeFAuthError, KSeFClient

# IMPORTANT: This is a simplified example invoice XML for demonstration purposes only.
# Real invoices MUST follow the official FA_VAT schema published by the Polish Ministry of Finance.
# Before production use:
# 1. Validate your invoice XML against the official FA_VAT XSD schema
# 2. Ensure all required fields are properly filled
# 3. Add proper digital signatures if required
# 4. Calculate and include the SHA-256 hash
# See: https://www.gov.pl/web/kas/krajowy-system-e-faktur for official documentation
SAMPLE_INVOICE_XML = """<?xml version="1.0" encoding="UTF-8"?>
<Faktura xmlns="http://crd.gov.pl/wzor/2023/06/29/12648/">
    <Naglowek>
        <KodFormularza kodSystemowy="FA (2)" wersjaSchemy="1-0E">FA</KodFormularza>
        <WariantFormularza>2</WariantFormularza>
        <DataWytworzeniaFa>2024-01-15T10:00:00</DataWytworzeniaFa>
        <SystemInfo>KSeF Client Example</SystemInfo>
    </Naglowek>
    <Podmiot1>
        <DaneIdentyfikacyjne>
            <NIP>1234567890</NIP>
            <Nazwa>Example Seller Ltd.</Nazwa>
        </DaneIdentyfikacyjne>
        <Adres>
            <KodKraju>PL</KodKraju>
            <AdresL1>ul. Example 1</AdresL1>
            <AdresL2>00-000 Warsaw</AdresL2>
        </Adres>
    </Podmiot1>
    <Podmiot2>
        <DaneIdentyfikacyjne>
            <NIP>9876543210</NIP>
            <Nazwa>Example Buyer Ltd.</Nazwa>
        </DaneIdentyfikacyjne>
        <Adres>
            <KodKraju>PL</KodKraju>
            <AdresL1>ul. Buyer 2</AdresL1>
            <AdresL2>00-001 Warsaw</AdresL2>
        </Adres>
    </Podmiot2>
    <Fa>
        <P_1>2024-01-15</P_1>
        <P_2>INV-001-2024</P_2>
        <P_13_1>1000.00</P_13_1>
        <P_14_1>230.00</P_14_1>
        <P_15>1230.00</P_15>
    </Fa>
    <FaWiersz>
        <NrWierszaFa>1</NrWierszaFa>
        <P_7>Consulting Services</P_7>
        <P_8A>1</P_8A>
        <P_9A>unit</P_9A>
        <P_11>1000.00</P_11>
        <P_12>23</P_12>
    </FaWiersz>
</Faktura>
"""


def main():
    """Submit an invoice to KSeF."""
    # Get credentials from environment variables
    nip = os.getenv("KSEF_NIP", "")
    token = os.getenv("KSEF_TOKEN", "")

    if not nip or not token:
        print("Error: Please set KSEF_NIP and KSEF_TOKEN environment variables")
        print("\nExample:")
        print("  export KSEF_NIP='1234567890'")
        print("  export KSEF_TOKEN='your-auth-token'")
        sys.exit(1)

    # Create KSeF client
    client = KSeFClient(base_url="https://ksef-demo.mf.gov.pl/api")

    try:
        print("Step 1: Authenticating...")
        session_token = client.authenticate_interactive(nip=nip, token=token)
        print(f"✓ Authenticated with session ID: {session_token.session_id}")

        print("\nStep 2: Submitting invoice...")
        print(f"Invoice size: {len(SAMPLE_INVOICE_XML)} bytes")

        # Submit the invoice
        response = client.submit_invoice(invoice_xml=SAMPLE_INVOICE_XML)

        print("\n✓ Invoice submitted successfully!")
        print(f"  Reference Number: {response.reference_number}")
        print(f"  Processing Code: {response.processing_code}")
        print(f"  Timestamp: {response.timestamp}")

        print("\nNote: This is a sample invoice. For real submissions, ensure:")
        print("  - Invoice XML follows the official FA_VAT schema")
        print("  - All required fields are properly filled")
        print("  - Invoice is digitally signed if required")

        # Terminate session
        print("\nStep 3: Terminating session...")
        client.terminate_session()
        print("✓ Session terminated")

    except KSeFAuthError as e:
        print(f"\n✗ Authentication failed: {e}")
        sys.exit(1)
    except KSeFAPIError as e:
        print(f"\n✗ API error: {e}")
        if e.response_data:
            print(f"  Details: {e.response_data}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
