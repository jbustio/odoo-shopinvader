# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Api Signin",
    "summary": """This module adds a signin service.""",
    "version": "16.0.1.0.0",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["fastapi_auth_jwt"],
    "data": [
        "security/res_groups.xml",
        "security/acl_res_partner.xml",
        "views/res_partner.xml",
    ],
    "demo": [],
    "installable": True,
}
