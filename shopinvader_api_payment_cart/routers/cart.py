# Copyright 2024 ACSONE SA (https://acsone.eu).
# @author Stéphane Bidoul <stephane.bidoul@acsone.eu>
# License LGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from typing import Annotated

from fastapi import Depends

from odoo import api

from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.payment import utils as payment_utils
from odoo.addons.shopinvader_api_cart.routers import cart_router
from odoo.addons.shopinvader_api_payment.schemas import PaymentData


@cart_router.get("/payable")
def init(
    # env: Annotated[api.Environment, Depends(authenticated_partner_env)],
    env: Annotated[api.Environment, Depends(odoo_env)],
    # partner: Annotated["ResPartner", Depends(authenticated_partner)],
    uuid: str | None = None,
) -> PaymentData | None:
    """Prepare payment data for the current cart.

    This route is authenticated, so we can verify the cart
    is accessible by the authenticated partner.
    """
    # TODO: authenticated env and partner. Remove sudo
    partner_id = 26  # Brandon Freeman
    cart_sudo = env["sale.order"].sudo()._find_open_cart(partner_id, uuid)
    if not cart_sudo:
        return None

    sale_order_sudo = env["sale.order"].sudo().browse(cart_sudo.id)
    payment_data = {
        "payable": f"sale.order,{cart_sudo.id}",
        "payable_reference": sale_order_sudo.name,
        "amount": sale_order_sudo.amount_total,
        "currency_id": sale_order_sudo.currency_id.id,
        "partner_id": sale_order_sudo.partner_id.id,
        "company_id": sale_order_sudo.company_id.id,
    }
    payment_data["access_token"] = payment_utils.generate_access_token(
        *payment_data.values()  # ordering matters
    )
    return PaymentData(**payment_data)
