# Copyright 2024 ACSONE SA (https://acsone.eu).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo.addons.shopinvader_api_payment.schemas import (
    TransactionProcessingValues as BaseTransactionProcessingValues,
)


class TransactionProcessingValues(BaseTransactionProcessingValues, extends=True):
    payment_info_form_html: str | None = None
