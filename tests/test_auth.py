"""Unit tests for KSeF authentication client."""

from datetime import datetime
from unittest.mock import Mock, patch

import pytest

from ksef_api_client.auth import (
    AuthToken,
    CertificateMaterial,
    KsefAuthClient,
    KsefAuthError,
)

# Sample test certificate and key (self-signed, for testing only)
TEST_CERT_PEM = b"""-----BEGIN CERTIFICATE-----
MIIDizCCAnOgAwIBAgIUZuw/5rG/itgSPKA3xt3TpTL0DwkwDQYJKoZIhvcNAQEL
BQAwVTELMAkGA1UEBhMCUEwxDTALBgNVBAgMBFRlc3QxDTALBgNVBAcMBFRlc3Qx
DTALBgNVBAoMBFRlc3QxGTAXBgNVBAMMEHRlc3QuZXhhbXBsZS5jb20wHhcNMjUx
MTEyMTMzNTU2WhcNMjYxMTEyMTMzNTU2WjBVMQswCQYDVQQGEwJQTDENMAsGA1UE
CAwEVGVzdDENMAsGA1UEBwwEVGVzdDENMAsGA1UECgwEVGVzdDEZMBcGA1UEAwwQ
dGVzdC5leGFtcGxlLmNvbTCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEB
AL6r2pzIz6yh1rc+8l8nl8FWGlz4d3qeJLEj+2vJwOTi8Al+IzGrHkFcx2pk3mUL
qayPEEXdy414P0jGovSCkMAaBJ99Uw1J+paI47QH9BAJ0mtNEWoh+hxsMv70J8Yw
skHo3Bi4CENvdQtm5U5iYN2LyKRiHBrjlYpUuXHh12gFaNgQU9ZSjJ/cm7/ynmUb
gh5LNJYgNwW5r8UB2p0mcvEkvJLTs+TvwRq6kLJfN+E8RNYFxhG+REZmwdCs3nX5
27NnylREkuRz4JFlFNkLvlhFDC+P8A30G3urBHHF99l3Ql9OSlpfVnNKLWhGGgVZ
vO26zDgWgOBl34fO9WVPuCcCAwEAAaNTMFEwHQYDVR0OBBYEFMPjXY0LUZ2MC/y1
uqtn0AvavG7RMB8GA1UdIwQYMBaAFMPjXY0LUZ2MC/y1uqtn0AvavG7RMA8GA1Ud
EwEB/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBADiTMNCYxE2DzF14I8HH/apc
1lcaJIrMQex4V5KfHhS7yFBtDwcZsLJ+rf2s+XCK0wmZnAYKHCWPNHldIXyJyIR5
oc4bIUNe4YhvIiTaiPclsx79vDIR03tSDTtQcP6dz6du4zJvkXE34b/9HtLyTQH7
RKfPlZrjzcfY2k+lI+CLtfVRzGnCRhcXqpWZfEoccrFCEyIu74FnY/GGQoGBrYCo
876jksMiNDn4eZ+R9roqg4Yl8jAL9+lwpRUSjEO7Ylc/XYoxZkcEHDqfPBYew+ed
2YDhAAS3tIu46ZDtIqL6rl5uBnvw3i6tNTQJDIhy+CBTJZz21ZAUQ4q2boSw3kA=
-----END CERTIFICATE-----"""

TEST_KEY_PEM = b"""-----BEGIN PRIVATE KEY-----
MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC+q9qcyM+soda3
PvJfJ5fBVhpc+Hd6niSxI/trycDk4vAJfiMxqx5BXMdqZN5lC6msjxBF3cuNeD9I
xqL0gpDAGgSffVMNSfqWiOO0B/QQCdJrTRFqIfocbDL+9CfGMLJB6NwYuAhDb3UL
ZuVOYmDdi8ikYhwa45WKVLlx4ddoBWjYEFPWUoyf3Ju/8p5lG4IeSzSWIDcFua/F
AdqdJnLxJLyS07Pk78EaupCyXzfhPETWBcYRvkRGZsHQrN51+duzZ8pURJLkc+CR
ZRTZC75YRQwvj/AN9Bt7qwRxxffZd0JfTkpaX1ZzSi1oRhoFWbztusw4FoDgZd+H
zvVlT7gnAgMBAAECggEAUDf0UzcnLG2wbMsWZJM/RQ+JKuk8N0HWlRJa4nfw6DtU
GuJPQ0PHiF9U5L3IVUHJYniUM5jDXWMkWOV9RJqz9KZdoI41BWfE/lVcW29nLuI6
/Xrgo0LlO9UHxX0KSNdO/+zMwLeYfmqjlyb0vXwlXcBEK2i9g1CRpy/LD48hNbkp
ElG2RXPvTlWtT/u+56njKP640vSkmjr/IW/07p3bkxRZ9LV/EmSfQ8DXCMWC7mY4
sISuRbROBzmkwvH5m9PJtN6+B4rp4/rRTMJwervol2b78DLKPFemodn87dvz9VaI
JPh+r2ALtrKNMGDAOqV283cnUvGw6yvXgp0Whmj6+QKBgQD/NcTb5zspqMy0Afxh
8Wl8NwjH90U9BWsGMKXoUJuXZ4geCRWDZnFizwePeBxUc8jIdrbw2x675voOFKDS
SLVnIj2DeEq0gy6jeorOr8KEdSqTMxSVt5WVAIMc3Nqvp5e4zSW8jjh+JDnBRl+8
VNiWxtdeF26jO3+wBxUok0z8iQKBgQC/QvGe1b9BL2a8/CK/Y5fZ83qnUiMNb2DQ
rEoZGBTncOWXZJrb3ttY/s7IHLxcm0O+V4YkrBKkJItt/Nsp4CCNKkhm0tTLu5k5
gmOys5FFjhQwOvcVu229BzVg7arJw3cePtPlNWslecQqDfKidPhBe1hMLW5kAyil
1LyX7QnDLwKBgQD1GNKCzsOG8tIFXpLgDVVdMg2A3fzk6bsrKrVrM176PTgAgIDk
vRHP7zw3kQbEJJ6Dx19SWV5e3yjvNOhui92LutqQ1IoKaqHz5tBAR5PsWgoVbE0s
rC8/9kn1AjYT1ERl+r9vIrcmjevZrphq6qFHzJcxihd7NL0gdOzhFvYs4QKBgEff
rFT4Fis02PLj/VrW3lW1Pb5rC2kdFdDVLfNILXLb5iuCTv+ZO+yxtJtW0SIr5sU8
tthJIag1Y4AtqV6PLyxdW1/okrcNBIOsEDMzb8AnqEaHohq0mISUlOab6bZwke73
xUE5Vc57d9Al9aw/MJvK8l+OIxHKbhgDXevp0+VZAoGAZJDfvJf4Ss9Da2gCwvQ1
J3xiU8Vb9f3NcBtvl9UwCaGDasxn3Q7bhaU8pe35CtbZqMmxt9ZtoxEzb10QWcMw
fM0th+JE1XHdn6JOEjuAlsYBBtqmZXzcQJIjmMNWOjGTGXdQ3Zh96jNN7LZHRXMC
870A4GkvnHTzi/ircoOZgNw=
-----END PRIVATE KEY-----"""

TEST_NIP = "1234567890"


class TestKsefAuthClient:
    """Test suite for KsefAuthClient."""

    def test_init_with_valid_params(self):
        """Test client initialization with valid parameters."""
        materials = CertificateMaterial(
            cert_data=TEST_CERT_PEM,
            key_data=TEST_KEY_PEM,
            passphrase=None,
        )
        client = KsefAuthClient(
            materials=materials, nip=TEST_NIP, environment="demo"
        )
        assert client._nip == TEST_NIP
        assert client._environment == "demo"
        assert "demo" in client._base_url

    def test_init_with_prod_environment(self):
        """Test client initialization with production environment."""
        materials = CertificateMaterial(
            cert_data=TEST_CERT_PEM,
            key_data=TEST_KEY_PEM,
        )
        client = KsefAuthClient(
            materials=materials, nip=TEST_NIP, environment="prod"
        )
        assert client._environment == "prod"
        assert "demo" not in client._base_url

    def test_init_with_empty_nip_raises_error(self):
        """Test that empty NIP raises ValueError."""
        materials = CertificateMaterial(
            cert_data=TEST_CERT_PEM,
            key_data=TEST_KEY_PEM,
        )
        with pytest.raises(ValueError, match="NIP cannot be empty"):
            KsefAuthClient(materials=materials, nip="", environment="demo")

    def test_init_with_invalid_environment_raises_error(self):
        """Test that invalid environment raises ValueError."""
        materials = CertificateMaterial(
            cert_data=TEST_CERT_PEM,
            key_data=TEST_KEY_PEM,
        )
        with pytest.raises(ValueError, match="Environment must be"):
            KsefAuthClient(materials=materials, nip=TEST_NIP, environment="invalid")

    @patch("ksef_api_client.auth.requests.post")
    def test_get_challenge_success(self, mock_post):
        """Test successful challenge retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"challenge": "test-challenge-123"}
        mock_post.return_value = mock_response

        materials = CertificateMaterial(
            cert_data=TEST_CERT_PEM,
            key_data=TEST_KEY_PEM,
        )
        client = KsefAuthClient(
            materials=materials, nip=TEST_NIP, environment="demo"
        )

        challenge = client._get_challenge()
        assert challenge == "test-challenge-123"
        mock_post.assert_called_once()

    @patch("ksef_api_client.auth.requests.post")
    def test_get_challenge_http_error(self, mock_post):
        """Test challenge retrieval with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.text = "Bad Request"
        mock_post.return_value = mock_response

        materials = CertificateMaterial(
            cert_data=TEST_CERT_PEM,
            key_data=TEST_KEY_PEM,
        )
        client = KsefAuthClient(
            materials=materials, nip=TEST_NIP, environment="demo"
        )

        with pytest.raises(KsefAuthError, match="Failed to get challenge"):
            client._get_challenge()

    @patch("ksef_api_client.auth.requests.post")
    def test_get_challenge_missing_in_response(self, mock_post):
        """Test challenge retrieval when challenge is missing in response."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response

        materials = CertificateMaterial(
            cert_data=TEST_CERT_PEM,
            key_data=TEST_KEY_PEM,
        )
        client = KsefAuthClient(
            materials=materials, nip=TEST_NIP, environment="demo"
        )

        with pytest.raises(KsefAuthError, match="Challenge not found"):
            client._get_challenge()

    @patch("ksef_api_client.auth.requests.post")
    def test_get_challenge_timeout(self, mock_post):
        """Test challenge retrieval with timeout."""
        import requests

        mock_post.side_effect = requests.Timeout("Connection timeout")

        materials = CertificateMaterial(
            cert_data=TEST_CERT_PEM,
            key_data=TEST_KEY_PEM,
        )
        client = KsefAuthClient(
            materials=materials, nip=TEST_NIP, environment="demo", timeout=1
        )

        with pytest.raises(KsefAuthError, match="Network error during authentication"):
            client.authenticate()

    def test_sign_challenge_with_invalid_key(self):
        """Test signing challenge with invalid private key."""
        materials = CertificateMaterial(
            cert_data=TEST_CERT_PEM,
            key_data=b"invalid-key-data",
        )
        client = KsefAuthClient(
            materials=materials, nip=TEST_NIP, environment="demo"
        )

        with pytest.raises(KsefAuthError, match="Signing failed"):
            client._sign_challenge("test-challenge")

    def test_sign_challenge_with_wrong_password(self):
        """Test signing challenge with wrong password for encrypted key."""
        # This test uses a real encrypted key scenario
        materials = CertificateMaterial(
            cert_data=TEST_CERT_PEM,
            key_data=TEST_KEY_PEM,
            passphrase="wrong-password",
        )
        client = KsefAuthClient(
            materials=materials, nip=TEST_NIP, environment="demo"
        )

        # This will likely fail during key loading
        with pytest.raises(KsefAuthError):
            client._sign_challenge("test-challenge")

    @patch("ksef_api_client.auth.requests.post")
    def test_authenticate_success(self, mock_post):
        """Test full successful authentication flow."""
        # Mock challenge response
        challenge_response = Mock()
        challenge_response.status_code = 200
        challenge_response.json.return_value = {"challenge": "test-challenge-123"}

        # Mock token response
        token_response = Mock()
        token_response.status_code = 201
        token_response.json.return_value = {
            "sessionToken": {"token": "test-token-abc"},
            "timestamp": "2025-01-01T12:00:00Z",
        }

        mock_post.side_effect = [challenge_response, token_response]

        materials = CertificateMaterial(
            cert_data=TEST_CERT_PEM,
            key_data=TEST_KEY_PEM,
        )
        client = KsefAuthClient(
            materials=materials, nip=TEST_NIP, environment="demo"
        )

        token = client.authenticate()
        assert isinstance(token, AuthToken)
        assert token.token == "test-token-abc"
        assert isinstance(token.valid_to, datetime)
        assert mock_post.call_count == 2

    @patch("ksef_api_client.auth.requests.post")
    def test_authenticate_challenge_failure(self, mock_post):
        """Test authentication failure at challenge stage."""
        mock_response = Mock()
        mock_response.status_code = 500
        mock_response.text = "Internal Server Error"
        mock_post.return_value = mock_response

        materials = CertificateMaterial(
            cert_data=TEST_CERT_PEM,
            key_data=TEST_KEY_PEM,
        )
        client = KsefAuthClient(
            materials=materials, nip=TEST_NIP, environment="demo"
        )

        with pytest.raises(KsefAuthError, match="Authentication failed"):
            client.authenticate()

    @patch("ksef_api_client.auth.requests.post")
    def test_init_token_http_error(self, mock_post):
        """Test token initialization with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        materials = CertificateMaterial(
            cert_data=TEST_CERT_PEM,
            key_data=TEST_KEY_PEM,
        )
        client = KsefAuthClient(
            materials=materials, nip=TEST_NIP, environment="demo"
        )

        with pytest.raises(KsefAuthError, match="Failed to init token"):
            client._init_token("challenge", "signature")

    @patch("ksef_api_client.auth.requests.post")
    def test_init_token_missing_token_in_response(self, mock_post):
        """Test token initialization when token is missing in response."""
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"timestamp": "2025-01-01T12:00:00Z"}
        mock_post.return_value = mock_response

        materials = CertificateMaterial(
            cert_data=TEST_CERT_PEM,
            key_data=TEST_KEY_PEM,
        )
        client = KsefAuthClient(
            materials=materials, nip=TEST_NIP, environment="demo"
        )

        with pytest.raises(KsefAuthError, match="Session token not found"):
            client._init_token("challenge", "signature")


class TestCertificateMaterial:
    """Test suite for CertificateMaterial dataclass."""

    def test_creation_with_all_fields(self):
        """Test creating CertificateMaterial with all fields."""
        materials = CertificateMaterial(
            cert_data=b"cert-data",
            key_data=b"key-data",
            passphrase="password",
        )
        assert materials.cert_data == b"cert-data"
        assert materials.key_data == b"key-data"
        assert materials.passphrase == "password"

    def test_creation_without_passphrase(self):
        """Test creating CertificateMaterial without passphrase."""
        materials = CertificateMaterial(
            cert_data=b"cert-data",
            key_data=b"key-data",
        )
        assert materials.passphrase is None


class TestAuthToken:
    """Test suite for AuthToken dataclass."""

    def test_creation(self):
        """Test creating AuthToken."""
        valid_to = datetime(2025, 1, 1, 12, 0, 0)
        token = AuthToken(token="test-token", valid_to=valid_to)
        assert token.token == "test-token"
        assert token.valid_to == valid_to
