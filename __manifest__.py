# ruff: noqa: B018 - Odoo requires a top-level dict literal in __manifest__.py
{
    "name": "KSeF Client for Odoo 18",
    "version": "18.0.1.0.0",
    "summary": "Integration with the Polish National e-Invoicing System (KSeF)",
    "author": "mkieszek",
    "license": "LGPL-3",
    "website": "https://github.com/mkieszek/ksef_client",
    "category": "Accounting",
    "depends": ["base", "account"],
    "data": [
        "views/res_company_views.xml",
    ],
    "demo": [],
    "installable": True,
    "application": False,
}
