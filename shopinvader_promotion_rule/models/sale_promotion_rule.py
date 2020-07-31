# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class SalePromotionRule(models.Model):
    _inherit = "sale.promotion.rule"

    @api.model
    def _get_restrictions(self):
        """
        Inherit add the shopinvader_backend restriction
        :return: list of str
        """
        restrictions = super(SalePromotionRule, self)._get_restrictions()
        restrictions.append("shopinvader_backend")
        return restrictions

    def _check_valid_shopinvader_backend(self, order):
        """
        Determine if promotion rule is valid for the order on a specific
        shopinvader backend.
        If no backend, it should return True.
        :param order: sale.order recordset
        :return: bool
        """
        self.ensure_one()
        # If no backend, it will return True
        return not order.shopinvader_backend_id.promotion_rule_disabled
