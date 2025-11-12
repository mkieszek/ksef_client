# Initialize KSeF client module

import contextlib

with contextlib.suppress(ImportError):
    # Allow module to be imported without Odoo for testing
    from . import models  # noqa: F401
