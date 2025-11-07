"""
Example: Interactive Authentication with KSeF

This example demonstrates how to authenticate with the KSeF API
using interactive session credentials.
"""

import os
import sys
from pathlib import Path

# Add src to path for local development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ksef_client import KSeFAuthError, KSeFClient


def main():
    """Authenticate with KSeF using interactive session."""
    # Get credentials from environment variables
    nip = os.getenv("KSEF_NIP", "")
    token = os.getenv("KSEF_TOKEN", "")

    if not nip or not token:
        print("Error: Please set KSEF_NIP and KSEF_TOKEN environment variables")
        print("\nExample:")
        print("  export KSEF_NIP='1234567890'")
        print("  export KSEF_TOKEN='your-auth-token'")
        sys.exit(1)

    # Create KSeF client (using demo environment)
    # For production, use: base_url="https://ksef.mf.gov.pl/api"
    client = KSeFClient(base_url="https://ksef-demo.mf.gov.pl/api")

    try:
        print(f"Authenticating with NIP: {nip}")

        # Authenticate and get session token
        session_token = client.authenticate_interactive(nip=nip, token=token)

        print("\n✓ Authentication successful!")
        print(f"  Session ID: {session_token.session_id}")
        print(f"  Context Identifier: {session_token.context_identifier}")
        print(f"  Timestamp: {session_token.timestamp}")
        print(f"  Token: {session_token.token[:20]}...")

        # Session is now active and can be used for other operations
        print("\nSession is active. You can now:")
        print("  - Submit invoices")
        print("  - Query invoices")
        print("  - Retrieve invoice details")

        # Terminate session when done
        print("\nTerminating session...")
        client.terminate_session()
        print("✓ Session terminated")

    except KSeFAuthError as e:
        print(f"\n✗ Authentication failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)
    finally:
        client.close()


if __name__ == "__main__":
    main()
