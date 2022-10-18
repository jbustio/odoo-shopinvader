# Copyright 2022 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _increase_rank(self, field, n=1):
        res = super()._increase_rank(field, n=n)
        if self.ids and field == "customer_rank":
            self._event("on_increase_rank").notify(self)
        return res
