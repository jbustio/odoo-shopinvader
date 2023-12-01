# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    shopinvader_email_verified = fields.Boolean()

    @api.model
    def _create_partner_from_payload(self, payload):
        return self.create(
            {
                "name": payload.get("name"),
                "email": payload.get("email"),
                "shopinvader_email_verified": payload.get("email_verified", False),
            }
        )
