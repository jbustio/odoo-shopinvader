# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class AccountTax(models.Model):

    _inherit = "account.tax"

    # odoo backport from 10.0
    @api.model
    def _fix_tax_included_price_company(
        self, price, prod_taxes, line_taxes, company_id
    ):
        if company_id:
            # To keep the same behavior as in _compute_tax_id
            prod_taxes = prod_taxes.filtered(
                lambda tax: tax.company_id == company_id
            )
            line_taxes = line_taxes.filtered(
                lambda tax: tax.company_id == company_id
            )
        return self._fix_tax_included_price(price, prod_taxes, line_taxes)
