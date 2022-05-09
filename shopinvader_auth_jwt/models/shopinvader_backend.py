# -*- coding: utf-8 -*-
# Copyright 2021 ACSONE SA/NV (http://acsone.eu)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import logging

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    jwt_aud = fields.Char(
        string="JWT audience",
        help="Use this backend when the JWT aud claim matches this.",
    )

    @api.model
    def _get_jwt_aud_domain(self, aud_list):
        return [("jwt_aud", "in", aud_list)]

    @api.model
    def _get_jwt_aud_from_domain(self, domain, aud_list):
        return self.search(domain)

    @api.model
    def _get_from_jwt_aud(self, aud):
        if not aud:
            return self.browse([])
        if isinstance(aud, str):
            aud = [aud]
        domain = self._get_jwt_aud_domain(aud)
        backends = self._get_jwt_aud_from_domain(domain, aud)
        if len(backends) != 1:
            _logger.warning(
                "%d backends found for JWT aud %r", len(backends), aud
            )
            return self.browse([])
        return backends
