# Copyright (C) 2025
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl-3.0.en.html).

MANIFEST = {
    "name": "KSeF Client for Odoo 18",
    "version": "18.0.1.0.0",
    "summary": "Integracja z Krajowym Systemem e-Faktur (KSeF)",
    "author": "mkieszek",
    "license": "LGPL-3",
    "website": "https://github.com/mkieszek/ksef_client",
    "category": "Accounting",
    "depends": ["base", "account"],
    "data": [],
    "demo": [],
    "installable": True,
    "application": False,
}

# Odoo expects a dict at module import time named "manifest" or a literal; we expose MANIFEST.
manifest = MANIFEST  # type: ignore
