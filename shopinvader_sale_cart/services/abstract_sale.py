# -*- coding: utf-8 -*-
# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

"""
Compatibility layer to format the information for a SO woth the same structure
as the one defined into cart V2. This layer add fields without removing the
one defined in the initial implementation/
"""

from odoo.addons.component.core import AbstractComponent


class AbstractSaleService(AbstractComponent):
    _inherit = "shopinvader.abstract.sale.service"

    def _convert_one_sale(self, sale):
        info = super(AbstractSaleService, self)._convert_one_sale(sale)
        info["discount"] = self._convert_discount(sale)
        return info

    def _convert_one_line(self, line):
        info = super(AbstractSaleService, self)._convert_one_line(line)
        info["unit_price"] = self._convert_one_line_unit_price(line)
        return info

    def _convert_discount(self, sale):
        return {
            "value": sale.discount_total,
        }

    def _convert_one_line_unit_price(self, line):
        return {
            "untaxed": line.price_unit,
            "untaxed_with_discount": line.price_unit
            - line.price_unit * (line.discount or 0) / 100,
        }
