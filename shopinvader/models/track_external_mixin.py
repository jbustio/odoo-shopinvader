# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, fields, models


class TrackExternalMixin(models.AbstractModel):
    _name = "track.external.mixin"
    _description = "Track external update"

    last_external_update_date = fields.Datetime()

    def is_rest_request(self):
        return self.env.context.get("shopinvader_request", False)

    def _fill_last_external_update_date(self, vals):
        if self.is_rest_request():
            vals.update({"last_external_update_date": fields.Datetime.now()})

    def _write(self, vals):
        self._fill_last_external_update_date(vals)
        return super()._write(vals)

    @api.model_create_multi
    def create(self, values_list):
        for vals in values_list:
            self._fill_last_external_update_date(vals)
        return super().create(values_list)
