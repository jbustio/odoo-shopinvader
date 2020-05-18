# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrder(models.Model):

    _inherit = "sale.order"

    online_customer_status = fields.Html(
        help="Fill in this field to provide your customer more information "
        "on his online account"
    )
    customer_comment = fields.Text()
    vendor_comment = fields.Text()
