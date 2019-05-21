# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models


class ProductAttributeValue(models.Model):

    _inherit = "product.attribute.value"

    # backport from odoo 10
    @api.multi
    def _variant_name(self, variable_attributes):
        return ", ".join(
            [
                v.name
                for v in self.sorted(key=lambda r: r.attribute_id.name)
                if v.attribute_id in variable_attributes
            ]
        )
