"""Authentication layer for KSeF.

Provides interfaces for loading certificates/keys and generating authorization tokens
based on KSeF challenge-response specification.

Public API is intentionally minimal at this stage.
"""

from __future__ import annotations

import base64
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime

import requests
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

_logger = logging.getLogger(__name__)

# KSeF API endpoints
KSEF_DEMO_BASE_URL = "https://ksef-demo.mf.gov.pl/api/online"
KSEF_PROD_BASE_URL = "https://ksef.mf.gov.pl/api/online"


class KsefAuthError(Exception):
    """Generic authentication error for KSeF operations."""


@dataclass
class CertificateMaterial:
    """Container for cryptographic materials.

    Parameters:
        cert_data: Binary data of the certificate (.pem or .cer).
        key_data: Binary data of the private key (.pem or .key).
        passphrase: Optional passphrase protecting the key.
    """

    cert_data: bytes
    key_data: bytes
    passphrase: str | None = None


@dataclass
class AuthToken:
    """Container for KSeF session token with metadata.

    Parameters:
        token: Session token string.
        valid_to: Expiration datetime of the token.
    """

    token: str
    valid_to: datetime


class KsefAuthClient:
    """KSeF authentication helper.

    Responsibility:
        - Load cryptographic materials (certificate and private key).
        - Perform challenge-response authentication flow with KSeF API.
        - Generate and return session tokens.
    """

    def __init__(
        self,
        materials: CertificateMaterial,
        nip: str,
        environment: str = "demo",
        timeout: int = 30,
    ):
        """Initialize KSeF authentication client.

        Parameters:
            materials: Certificate and key materials.
            nip: Tax identification number (NIP) of the taxpayer.
            environment: KSeF environment ('demo' or 'prod').
            timeout: HTTP request timeout in seconds.

        Raises:
            ValueError: If NIP is empty or environment is invalid.
        """
        if not nip:
            raise ValueError("NIP cannot be empty")
        if environment not in ("demo", "prod"):
            raise ValueError("Environment must be 'demo' or 'prod'")

        self._materials = materials
        self._nip = nip
        self._environment = environment
        self._timeout = timeout
        self._base_url = (
            KSEF_DEMO_BASE_URL if environment == "demo" else KSEF_PROD_BASE_URL
        )

    def authenticate(self) -> AuthToken:
        """Perform full authentication flow with KSeF.

        Returns:
            AuthToken containing session token and expiration time.

        Raises:
            KsefAuthError: If authentication fails at any stage.
        """
        try:
            # Step 1: Get authorization challenge
            challenge = self._get_challenge()
            _logger.info("Received authorization challenge from KSeF")

            # Step 2: Sign challenge with private key
            signature = self._sign_challenge(challenge)
            _logger.info("Challenge signed successfully")

            # Step 3: Exchange signed challenge for session token
            token = self._init_token(challenge, signature)
            _logger.info("Session token obtained successfully")

            return token

        except requests.RequestException as e:
            _logger.error("HTTP error during authentication: %s", e)
            raise KsefAuthError(f"Network error during authentication: {e}") from e
        except Exception as e:
            _logger.error("Unexpected error during authentication: %s", e)
            raise KsefAuthError(f"Authentication failed: {e}") from e

    def _get_challenge(self) -> str:
        """Request authorization challenge from KSeF.

        Returns:
            Challenge string from KSeF API.

        Raises:
            KsefAuthError: If challenge request fails.
        """
        url = f"{self._base_url}/Session/AuthorisationChallenge"
        headers = {"Content-Type": "application/json"}
        payload = {"contextIdentifier": {"type": "onip", "identifier": self._nip}}

        _logger.debug("Requesting challenge from: %s", url)
        response = requests.post(
            url, json=payload, headers=headers, timeout=self._timeout
        )

        if response.status_code != 200:
            _logger.error(
                "Challenge request failed with status %s: %s",
                response.status_code,
                response.text,
            )
            raise KsefAuthError(
                f"Failed to get challenge: HTTP {response.status_code}"
            )

        data = response.json()
        challenge = data.get("challenge")
        if not challenge:
            raise KsefAuthError("Challenge not found in response")

        return challenge

    def _sign_challenge(self, challenge: str) -> str:
        """Sign challenge with private key.

        Parameters:
            challenge: Challenge string from KSeF.

        Returns:
            Base64-encoded signature.

        Raises:
            KsefAuthError: If signing fails.
        """
        try:
            # Load private key
            passphrase_bytes = (
                self._materials.passphrase.encode()
                if self._materials.passphrase
                else None
            )
            private_key = serialization.load_pem_private_key(
                self._materials.key_data, password=passphrase_bytes
            )

            # SHA256 hash of challenge
            challenge_hash = hashlib.sha256(challenge.encode()).digest()

            # Sign using RSA with PKCS1v15 padding and SHA256
            signature = private_key.sign(
                challenge_hash, padding.PKCS1v15(), hashes.SHA256()
            )

            # Encode to base64
            signature_b64 = base64.b64encode(signature).decode()
            _logger.debug("Challenge signed, signature length: %s", len(signature_b64))

            return signature_b64

        except Exception as e:
            _logger.error("Failed to sign challenge: %s", e)
            raise KsefAuthError(f"Signing failed: {e}") from e

    def _init_token(self, challenge: str, signature: str) -> AuthToken:
        """Exchange signed challenge for session token.

        Parameters:
            challenge: Original challenge from KSeF.
            signature: Base64-encoded signature of the challenge.

        Returns:
            AuthToken with session token and expiration.

        Raises:
            KsefAuthError: If token initialization fails.
        """
        url = f"{self._base_url}/Session/InitToken"
        headers = {"Content-Type": "application/json"}

        # Load certificate to extract serial number
        cert = x509.load_pem_x509_certificate(self._materials.cert_data)
        cert_serial = format(cert.serial_number, "x").upper()

        payload = {
            "contextIdentifier": {"type": "onip", "identifier": self._nip},
            "contextName": {
                "type": "SubjectSerialNumber",
                "identifier": cert_serial,
                "credentialsIdentifier": {"type": "onip", "identifier": self._nip},
            },
            "authorisationChallenge": {
                "challenge": challenge,
                "signatureValue": {
                    "type": "plain",
                    "value": signature,
                    "algorithm": "RSA",
                },
            },
        }

        _logger.debug("Requesting session token from: %s", url)
        response = requests.post(
            url, json=payload, headers=headers, timeout=self._timeout
        )

        if response.status_code != 201:
            _logger.error(
                "Token init failed with status %s: %s",
                response.status_code,
                response.text,
            )
            raise KsefAuthError(f"Failed to init token: HTTP {response.status_code}")

        data = response.json()
        session_token = data.get("sessionToken", {}).get("token")
        timestamp = data.get("timestamp")

        if not session_token:
            raise KsefAuthError("Session token not found in response")

        # Parse timestamp to datetime (KSeF returns ISO format)
        try:
            valid_to = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except Exception as e:
            _logger.warning("Failed to parse token expiration: %s", e)
            # Default to current time if parsing fails
            valid_to = datetime.now()

        return AuthToken(token=session_token, valid_to=valid_to)
