# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, fields, models


class ProductPricelist(models.Model):

    _inherit = "product.pricelist"

    discount_policy = fields.Selection(
        [
            ("with_discount", "Discount included in the price"),
            (
                "without_discount",
                "Show public price & discount to the customer",
            ),
        ],
        default="with_discount",
    )

    @api.multi
    def get_product_price_rule(
        self, product, quantity, partner=None, date=False, uom_id=False
    ):
        """ For a given pricelist, return price and rule for a given product
            Method signature backported from odoo 10.0
        """
        self.ensure_one()
        partner_id = partner.id if partner else None
        res = self.price_rule_get(product.id, quantity, partner_id)
        return res[self.id]
