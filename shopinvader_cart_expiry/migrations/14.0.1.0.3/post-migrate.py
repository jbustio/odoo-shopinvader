# Copyright 2024 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import timedelta

from odoo import SUPERUSER_ID, api, fields

_logger = logging.getLogger(__name__)


def migrate(cr, version):
    _logger.info("Upgrade shopinvader_cart_expiry: delete old carts")
    if not version:
        return
    with api.Environment.manage():
        env = api.Environment(cr, SUPERUSER_ID, {})
        domain = [("cart_expiry_delay", ">", 0)]
        for backend in env["shopinvader.backend"].search(domain):
            backend = backend.with_company(backend.company_id.id).sudo_tech()
            expiry_date = fields.Datetime.from_string(fields.Datetime.now())
            delta_arg = {backend.cart_expiry_delay_unit: backend.cart_expiry_delay}
            expiry_date -= timedelta(**delta_arg)
            domain = [
                ("shopinvader_backend_id", "=", backend.id),
                ("typology", "=", "cart"),
                ("state", "=", "draft"),
                ("last_external_update_date", "=", False),
            ]
            cart_expired = backend.env["sale.order"].search(domain)
            if cart_expired:
                if backend.cart_expiry_policy == "cancel":
                    cart_expired.action_cancel()
                else:
                    cart_expired.unlink()
    return
