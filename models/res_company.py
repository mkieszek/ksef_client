"""Extension of res.company model for KSeF configuration."""

import base64
import logging

from odoo import _, fields, models
from odoo.exceptions import UserError

# Import ksef client modules lazily inside methods to avoid import-time errors
# that would prevent Odoo from loading the module (missing deps in environment).

_logger = logging.getLogger(__name__)


class ResCompany(models.Model):
    """Extend res.company with KSeF configuration and authentication."""

    _inherit = "res.company"

    # KSeF Configuration Fields
    ksef_environment = fields.Selection(
        [("demo", "Demo (Test)"), ("prod", "Production")],
        string="KSeF Environment",
        default="demo",
        help="Select the KSeF environment to use for e-invoicing.",
    )

    ksef_auth_cert = fields.Binary(
        string="Authentication Certificate",
        help="Upload your KSeF certificate file (.pem or .cer).",
        attachment=True,
    )

    ksef_auth_cert_filename = fields.Char(string="Certificate Filename")

    ksef_auth_key = fields.Binary(
        string="Private Key",
        help="Upload your private key file (.pem or .key).",
        attachment=True,
    )

    ksef_auth_key_filename = fields.Char(string="Private Key Filename")

    ksef_auth_key_password = fields.Char(
        string="Private Key Password",
        help="Password for the private key if it is encrypted.",
    )

    ksef_auth_token = fields.Char(
        string="Session Token",
        readonly=True,
        help="Current KSeF session token (automatically obtained).",
    )

    ksef_token_valid_to = fields.Datetime(
        string="Token Valid Until",
        readonly=True,
        help="Expiration date and time of the current session token.",
    )

    def action_ksef_test_connection(self):
        """Test KSeF connection and authenticate.

        This method performs the full authentication flow:
        1. Validates that certificate and key are provided.
        2. Calls KSeF API to obtain session token.
        3. Saves token and expiration in the company record.

        Raises:
            UserError: If authentication fails or configuration is incomplete.
        """
        self.ensure_one()

        # Validate configuration
        if not self.ksef_auth_cert:
            raise UserError(_("Please upload an authentication certificate."))

        if not self.ksef_auth_key:
            raise UserError(_("Please upload a private key."))

        if not self.vat:
            raise UserError(
                _("Company VAT/NIP is required for KSeF authentication. "
                  "Please configure it in company settings.")
            )

        # Extract NIP from VAT (remove country prefix if present)
        nip = self.vat
        if nip.startswith("PL"):
            nip = nip[2:]

        # Provide a fallback name for static analysis; real class is imported lazily below.
        KsefAuthError = Exception

        try:
            # Import KSeF client lazily — this avoids import-time failures when
            # running Odoo in environments where ksef_api_client deps aren't
            # available (for example during initial module loading in CI).
            try:
                from ksef_api_client.auth import (
                    CertificateMaterial,
                    KsefAuthClient,
                    KsefAuthError,
                )
            except Exception as e:
                _logger.exception("KSeF client import failed: %s", e)
                raise UserError(
                    _(
                        "KSeF client dependencies are not available in this environment: %s"
                    )
                    % str(e)
                ) from e

            # Decode binary fields
            cert_data = base64.b64decode(self.ksef_auth_cert)
            key_data = base64.b64decode(self.ksef_auth_key)

            # Create certificate materials
            materials = CertificateMaterial(
                cert_data=cert_data,
                key_data=key_data,
                passphrase=self.ksef_auth_key_password or None,
            )

            # Initialize auth client
            auth_client = KsefAuthClient(
                materials=materials,
                nip=nip,
                environment=self.ksef_environment,
            )

            # Perform authentication
            _logger.info(
                "Starting KSeF authentication for company %s (NIP: %s, env: %s)",
                self.name,
                nip,
                self.ksef_environment,
            )
            token = auth_client.authenticate()

            # Save token and expiration
            self.write(
                {
                    "ksef_auth_token": token.token,
                    "ksef_token_valid_to": token.valid_to,
                }
            )

            _logger.info(
                "KSeF authentication successful for company %s. Token valid until: %s",
                self.name,
                token.valid_to,
            )

            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "title": _("Success"),
                    "message": _(
                        "Successfully authenticated with KSeF. "
                        "Token valid until: %s"
                    )
                    % token.valid_to.strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "success",
                    "sticky": False,
                },
            }

        except KsefAuthError as e:
            _logger.error("KSeF authentication failed: %s", e)
            raise UserError(
                _("KSeF authentication failed: %s\n\n"
                  "Please check your certificate, private key, and password.")
                % str(e)
            ) from e
        except Exception as e:
            _logger.error("Unexpected error during KSeF authentication: %s", e)
            raise UserError(
                _("An unexpected error occurred during authentication: %s") % str(e)
            ) from e
