# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Shopinvader Search Engine Product Price",
    "summary": """
        Add the export of product prices for Shopinvader""",
    "version": "16.0.1.0.0",
    "category": "e-commerce",
    "license": "AGPL-3",
    "author": "ACSONE SA/NV",
    "website": "https://github.com/shopinvader/odoo-shopinvader",
    "depends": ["product_get_price_helper", "shopinvader_search_engine"],
    "data": ["views/se_backend.xml", "views/se_index.xml"],
    "demo": [],
    "installable": True,
    "development_status": "Alpha",
}
