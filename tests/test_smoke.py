"""Minimal smoke tests independent of Odoo runtime.

These serve as a quick PASS gate in CI and provide a scaffold for future tests.
"""

from ksef_api_client.auth import CertificateMaterial, KsefAuthClient


def test_auth_token_stub_generates():
    materials = CertificateMaterial(cert_path="/dev/null", key_path="/dev/null")
    client = KsefAuthClient(materials)
    token = client.generate_auth_token("abc12345-challenge")
    assert token.startswith("stub-token-for-")


def test_auth_token_empty_challenge_raises():
    materials = CertificateMaterial(cert_path="/dev/null", key_path="/dev/null")
    client = KsefAuthClient(materials)
    try:
        client.generate_auth_token("")
    except ValueError:
        # expected
        return
    raise AssertionError("Expected ValueError")
