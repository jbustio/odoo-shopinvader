# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Auth Api Key",
    "summary": """
        Shopinvader API_KEY Authentication""",
    "version": "10.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["shopinvader", "auth_api_key"],
    "data": ["views/shopinvader_backend_view.xml"],
    "demo": [
        "demo/auth_api_key_demo.xml",
        "demo/shopinvader_backend_demo.xml",
    ],
}
