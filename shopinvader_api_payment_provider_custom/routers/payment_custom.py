# Copyright 2024 ACSONE SA (https://acsone.eu).
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import logging
from typing import Annotated, Any
from urllib.parse import urljoin

from fastapi import Depends, HTTPException

from odoo import api, models

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.payment.models.payment_transaction import PaymentTransaction
from odoo.addons.shopinvader_api_payment.routers import payment_router
from odoo.addons.shopinvader_api_payment.routers.utils import Payable
from odoo.addons.shopinvader_api_payment.schemas import TransactionProcessingValues

_logger = logging.getLogger(__name__)


@payment_router.post("/payment/providers/custom/pending")
def custom_payment_pending_msg(
    payable: str,
    transaction_id: int,
    odoo_env: Annotated[api.Environment, Depends(odoo_env)],
):
    try:
        Payable.decode(odoo_env, payable)
    except Exception as e:
        _logger.info("Could not decode payable")
        raise HTTPException(403) from e

    tx_sudo = odoo_env["payment.transaction"].sudo().browse(transaction_id)
    # TODO: since we get the transaction from its ID, we should check that
    # the transaction corresponds to the payable. How?
    tx_sudo._set_pending()
    tx_sudo._execute_callback()


class ShopinvaderApiPaymentRouterHelper(models.AbstractModel):
    _inherit = "shopinvader_api_payment.payment_router.helper"

    def _get_custom_redirect_form_html(
        self, tx_sudo: PaymentTransaction, payable: str
    ) -> str:
        shopinvader_api_payment_base_url = tx_sudo.env.context.get(
            "shopinvader_api_payment_base_url", ""
        )
        redirect_url = urljoin(shopinvader_api_payment_base_url, "custom/pending")
        return f"""\n
        <form method=\"post\"
        action=\"{redirect_url}\">\n
                    <input type=\"hidden\" name=\"Data\"
                    value=\"amount={tx_sudo.amount}|
                    currencyCode={tx_sudo.currency_id.name}|
                    pendingMsg={tx_sudo.provider_id.pending_msg}|
                    payable={payable}|
                    transactionId={tx_sudo.id}|
                    transactionReference={tx_sudo.reference}
                    \"/>\n
                          </form>"""

    def _get_tx_processing_values(
        self, tx_sudo: PaymentTransaction, **kwargs: Any
    ) -> TransactionProcessingValues:
        tx_processing_values = super()._get_tx_processing_values(tx_sudo, **kwargs)
        if tx_sudo.provider_id.code == "custom":
            tx_processing_values.redirect_form_html = (
                self._get_custom_redirect_form_html(tx_sudo, kwargs.get("payable", ""))
            )
        return tx_processing_values
