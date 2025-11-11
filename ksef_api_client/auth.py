"""Authentication layer for KSeF.

Provides interfaces for loading certificates/keys and generating authorization tokens
based on KSeF challenge-response specification.

Public API is intentionally minimal at this stage.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass

_logger = logging.getLogger(__name__)


class KsefAuthError(Exception):
    """Generic authentication error for KSeF operations."""


@dataclass
class CertificateMaterial:
    """Container for cryptographic materials.

    Parameters:
        cert_path: Ścieżka do pliku certyfikatu (nie commitować realnych plików).
        key_path: Ścieżka do pliku klucza prywatnego.
        passphrase: Opcjonalna fraza zabezpieczająca klucz.
    """

    cert_path: str
    key_path: str
    passphrase: str | None = None


class KsefAuthClient:
    """KSeF authentication helper.

    Responsibility:
        - Wczytanie materiałów kryptograficznych (delegowane w przyszłości).
        - Generowanie podpisu challenge i tokena (stub – do implementacji).
    """

    def __init__(self, materials: CertificateMaterial):
        self._materials = materials

    def generate_auth_token(self, challenge: str) -> str:
        """Generate KSeF auth token from challenge.

        Parametry:
            challenge: Losowy ciąg otrzymany z endpointu KSeF.

        Zwraca:
            Tymczasowy token autoryzacyjny (stub string).

        Wyjątki:
            ValueError: jeśli challenge jest pusty.
            KsefAuthError: jeśli podpis nie może być wygenerowany.
        """
        if not challenge:
            raise ValueError("Challenge cannot be empty")
        try:
            # TODO(issue-link): implement digital signature + token exchange per KSeF spec.
            _logger.debug("Generating auth token (stub) for challenge length=%s", len(challenge))
            return f"stub-token-for-{challenge[:8]}"
        except Exception as exc:  # pragma: no cover - defensive
            raise KsefAuthError("Failed to generate auth token") from exc
