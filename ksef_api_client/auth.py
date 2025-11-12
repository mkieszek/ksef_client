"""Authentication layer for KSeF.

Provides interfaces for loading certificates/keys and generating authorization tokens
based on KSeF challenge-response specification using API v2.

Public API is intentionally minimal at this stage.
"""

from __future__ import annotations

import base64
import hashlib
import logging
from dataclasses import dataclass
from datetime import datetime
from xml.etree import ElementTree as ET

import requests
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding

_logger = logging.getLogger(__name__)

# KSeF API v2 endpoints (based on OpenAPI spec)
KSEF_DEMO_BASE_URL = "https://ksef-demo.mf.gov.pl/api/v2"
KSEF_PROD_BASE_URL = "https://ksef.mf.gov.pl/api/v2"


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
        """Perform full authentication flow with KSeF API v2.

        Returns:
            AuthToken containing session token and expiration time.

        Raises:
            KsefAuthError: If authentication fails at any stage.
        """
        try:
            # Step 1: Get authorization challenge
            challenge, timestamp = self._get_challenge()
            _logger.info("Received authorization challenge from KSeF")

            # Step 2: Create XAdES-signed XML document
            signed_xml = self._create_xades_document(challenge)
            _logger.info("Created XAdES-signed authentication document")

            # Step 3: Submit XAdES signature for authentication
            auth_token, ref_number = self._submit_xades_auth(signed_xml)
            _logger.info(
                "Authentication initiated successfully, reference: %s", ref_number
            )

            # Step 4: Redeem authentication token for access token
            token = self._redeem_token(auth_token)
            _logger.info("Access token obtained successfully")

            return token

        except requests.RequestException as e:
            _logger.error("HTTP error during authentication: %s", e)
            raise KsefAuthError(f"Network error during authentication: {e}") from e
        except Exception as e:
            _logger.error("Unexpected error during authentication: %s", e)
            raise KsefAuthError(f"Authentication failed: {e}") from e

    def _get_challenge(self) -> tuple[str, str]:
        """Request authorization challenge from KSeF API v2.

        Returns:
            Tuple of (challenge string, timestamp) from KSeF API.

        Raises:
            KsefAuthError: If challenge request fails.
        """
        url = f"{self._base_url}/auth/challenge"
        headers = {"Content-Type": "application/json"}

        _logger.debug("Requesting challenge from: %s", url)
        response = requests.post(url, headers=headers, timeout=self._timeout)

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
        timestamp = data.get("timestamp")

        if not challenge:
            raise KsefAuthError("Challenge not found in response")
        if not timestamp:
            raise KsefAuthError("Timestamp not found in response")

        return challenge, timestamp

    def _create_xades_document(self, challenge: str) -> str:
        """Create XAdES-signed XML authentication document.

        Parameters:
            challenge: Challenge string from KSeF.

        Returns:
            XAdES-signed XML document as string.

        Raises:
            KsefAuthError: If document creation or signing fails.
        """
        try:
            # Load certificate
            cert = x509.load_pem_x509_certificate(self._materials.cert_data)

            # Load private key
            passphrase_bytes = (
                self._materials.passphrase.encode()
                if self._materials.passphrase
                else None
            )
            private_key = serialization.load_pem_private_key(
                self._materials.key_data, password=passphrase_bytes
            )

            # Create XML namespaces
            ns_auth = "http://ksef.mf.gov.pl/auth/token/2.0"
            ns_ds = "http://www.w3.org/2000/09/xmldsig#"

            # Register namespaces
            ET.register_namespace("", ns_auth)
            ET.register_namespace("ds", ns_ds)

            # Create AuthTokenRequest element
            root = ET.Element(f"{{{ns_auth}}}AuthTokenRequest")

            # Add Challenge element
            challenge_elem = ET.SubElement(root, f"{{{ns_auth}}}Challenge")
            challenge_elem.text = challenge

            # Add ContextIdentifier with NIP
            context_elem = ET.SubElement(root, f"{{{ns_auth}}}ContextIdentifier")
            nip_elem = ET.SubElement(context_elem, f"{{{ns_auth}}}Nip")
            nip_elem.text = self._nip

            # Add SubjectIdentifierType
            subject_type_elem = ET.SubElement(
                root, f"{{{ns_auth}}}SubjectIdentifierType"
            )
            subject_type_elem.text = "certificateSubject"

            # Convert to string for signing
            xml_str = ET.tostring(root, encoding="utf-8", xml_declaration=True)

            # Sign the XML (simplified XAdES - using detached signature)
            # For production, a full XAdES library should be used
            canonical_xml = xml_str.decode("utf-8")

            # Calculate digest
            digest = hashlib.sha256(canonical_xml.encode()).digest()
            digest_b64 = base64.b64encode(digest).decode()

            # Sign the digest
            signature = private_key.sign(digest, padding.PKCS1v15(), hashes.SHA256())
            signature_b64 = base64.b64encode(signature).decode()

            # Add signature to XML
            sig_elem = ET.SubElement(root, f"{{{ns_ds}}}Signature")
            sig_elem.set("Id", "Signature-1")

            signed_info = ET.SubElement(sig_elem, f"{{{ns_ds}}}SignedInfo")

            # CanonicalizationMethod
            canon_method = ET.SubElement(
                signed_info, f"{{{ns_ds}}}CanonicalizationMethod"
            )
            canon_method.set("Algorithm", "http://www.w3.org/TR/2001/REC-xml-c14n-20010315")

            # SignatureMethod
            sig_method = ET.SubElement(signed_info, f"{{{ns_ds}}}SignatureMethod")
            sig_method.set("Algorithm", "http://www.w3.org/2001/04/xmldsig-more#rsa-sha256")

            # Reference
            reference = ET.SubElement(signed_info, f"{{{ns_ds}}}Reference")
            reference.set("URI", "")

            # DigestMethod
            digest_method = ET.SubElement(reference, f"{{{ns_ds}}}DigestMethod")
            digest_method.set("Algorithm", "http://www.w3.org/2001/04/xmlenc#sha256")

            # DigestValue
            digest_value = ET.SubElement(reference, f"{{{ns_ds}}}DigestValue")
            digest_value.text = digest_b64

            # SignatureValue
            sig_value = ET.SubElement(sig_elem, f"{{{ns_ds}}}SignatureValue")
            sig_value.text = signature_b64

            # KeyInfo
            key_info = ET.SubElement(sig_elem, f"{{{ns_ds}}}KeyInfo")
            x509_data = ET.SubElement(key_info, f"{{{ns_ds}}}X509Data")

            # X509Certificate
            x509_cert_elem = ET.SubElement(x509_data, f"{{{ns_ds}}}X509Certificate")
            cert_b64 = base64.b64encode(cert.public_bytes(serialization.Encoding.DER)).decode()
            x509_cert_elem.text = cert_b64

            # X509SerialNumber
            x509_serial = ET.SubElement(x509_data, f"{{{ns_ds}}}X509SerialNumber")
            x509_serial.text = str(cert.serial_number)

            # Convert final XML to string
            final_xml = ET.tostring(root, encoding="utf-8", xml_declaration=True)

            _logger.debug("XAdES document created, size: %d bytes", len(final_xml))
            return final_xml.decode("utf-8")

        except Exception as e:
            _logger.error("Failed to create XAdES document: %s", e)
            raise KsefAuthError(f"XAdES document creation failed: {e}") from e

    def _submit_xades_auth(self, signed_xml: str) -> tuple[str, str]:
        """Submit XAdES-signed document for authentication.

        Parameters:
            signed_xml: XAdES-signed XML document.

        Returns:
            Tuple of (authentication_token, reference_number).

        Raises:
            KsefAuthError: If authentication submission fails.
        """
        url = f"{self._base_url}/auth/xades-signature"
        headers = {"Content-Type": "application/xml"}

        _logger.debug("Submitting XAdES authentication to: %s", url)
        response = requests.post(
            url, data=signed_xml.encode("utf-8"), headers=headers, timeout=self._timeout
        )

        if response.status_code != 200:
            _logger.error(
                "XAdES authentication failed with status %s: %s",
                response.status_code,
                response.text,
            )
            raise KsefAuthError(
                f"Failed to authenticate with XAdES: HTTP {response.status_code}"
            )

        data = response.json()
        auth_token = data.get("authenticationToken", {}).get("token")
        ref_number = data.get("referenceNumber")

        if not auth_token:
            raise KsefAuthError("Authentication token not found in response")
        if not ref_number:
            raise KsefAuthError("Reference number not found in response")

        return auth_token, ref_number

    def _redeem_token(self, auth_token: str) -> AuthToken:
        """Redeem authentication token for access token.

        Parameters:
            auth_token: Authentication token from XAdES authentication.

        Returns:
            AuthToken with access token and expiration.

        Raises:
            KsefAuthError: If token redemption fails.
        """
        url = f"{self._base_url}/auth/token/redeem"
        headers = {
            "Content-Type": "application/json",
            "AuthenticationToken": auth_token,
        }

        _logger.debug("Redeeming authentication token at: %s", url)
        response = requests.post(url, headers=headers, timeout=self._timeout)

        if response.status_code != 200:
            _logger.error(
                "Token redemption failed with status %s: %s",
                response.status_code,
                response.text,
            )
            raise KsefAuthError(
                f"Failed to redeem token: HTTP {response.status_code}"
            )

        data = response.json()
        access_token = data.get("accessToken", {}).get("token")
        valid_until = data.get("accessToken", {}).get("validUntil")

        if not access_token:
            raise KsefAuthError("Access token not found in response")

        # Parse expiration timestamp
        try:
            valid_to = datetime.fromisoformat(valid_until.replace("Z", "+00:00"))
        except Exception as e:
            _logger.warning("Failed to parse token expiration: %s", e)
            # Default to current time if parsing fails
            valid_to = datetime.now()

        return AuthToken(token=access_token, valid_to=valid_to)
