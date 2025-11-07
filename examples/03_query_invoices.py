"""
Example: Query Incoming Invoices from KSeF

This example demonstrates how to query and retrieve a list of incoming invoices.
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ksef_client import KSeFAPIError, KSeFAuthError, KSeFClient


def main():
    """Query incoming invoices from KSeF."""
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

        print("\nStep 2: Querying incoming invoices...")

        # Query invoices from the last 30 days
        date_to = datetime.now().strftime("%Y-%m-%d")
        date_from = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        print(f"  Date range: {date_from} to {date_to}")
        print("  Page size: 10")

        # Query invoices
        invoice_list = client.query_invoices(
            page_size=10,
            page_offset=0,
            date_from=date_from,
            date_to=date_to,
        )

        print("\n✓ Query successful!")
        print(f"  Total invoices found: {invoice_list.total_count}")
        print(f"  Showing page {invoice_list.page_offset + 1} (size: {invoice_list.page_size})")

        if invoice_list.invoices:
            print("\nInvoice List:")
            print("-" * 80)
            for idx, invoice in enumerate(invoice_list.invoices, 1):
                print(f"\n{idx}. Invoice: {invoice.invoice_number}")
                print(f"   Reference: {invoice.reference_number}")
                print(f"   Issue Date: {invoice.issue_date}")
                print(f"   Seller: {invoice.seller_name}")
                print(f"   Buyer: {invoice.buyer_name}")
                print(f"   Amount: {invoice.amount_gross:.2f} PLN")
        else:
            print("\nNo invoices found in the specified date range.")
            print("\nTip: Try adjusting the date range or check if there are any invoices")
            print("     in your KSeF account.")

        # Demonstrate pagination if there are more invoices
        if invoice_list.total_count > invoice_list.page_size:
            print("\n" + "=" * 80)
            print("More invoices available. To fetch the next page, use:")
            print("  client.query_invoices(page_size=10, page_offset=10)")
            print("\nExample pagination loop:")
            print("  for page in range(0, total_count, page_size):")
            print("      invoices = client.query_invoices(page_offset=page)")

        # Terminate session
        print("\n" + "=" * 80)
        print("Step 3: Terminating session...")
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
        import traceback

        traceback.print_exc()
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
