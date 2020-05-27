# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_one_sale(self, sale):
        values = super(AbstractSaleService, self)._convert_one_sale(sale)
        values.update(
            {
                "customer_status": sale.online_customer_status,
                "customer_comment": sale.customer_comment,
                "vendor_comment": sale.vendor_comment,
            }
        )
        return values
