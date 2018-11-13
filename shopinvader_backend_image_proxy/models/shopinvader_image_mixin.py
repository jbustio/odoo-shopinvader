# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import api, models


class ShopinvaderImageMixin(models.AbstractModel):
    _inherit = 'shopinvader.image.mixin'

    @api.multi
    def _get_image_data_for_record(self):
        """
        Inherit to replace the url if necessary
        :return: list of dict
        """
        self.ensure_one()
        result = super(
            ShopinvaderImageMixin, self)._get_image_data_for_record()
        # We have to ensure that the current recordset has a backend_id field
        if 'backend_id' not in self._fields:
            return result
        if result and self.backend_id.image_proxy_url:
            self._replace_image_url(result)
        return result

    @api.multi
    def _replace_image_url(self, result):
        """
        Into the given result, replace the url ("src" key of dict) by the
        image_proxy_url set on the backend
        :param result: list of dict
        :return: list of dict
        """
        # Structure of given "result":
        # (cfr compute 'images' field of shopinvader.image.mixin)
        # [
        #     {
        #         'size1': {
        #             'src': 'an_url',
        #             'alt': 'a_string',
        #         },
        #         'size2': {
        #             'src': 'an_url',
        #             'alt': 'a_string',
        #         },
        #         ...
        #     },
        #     ...
        # ]
        self.ensure_one()
        url_key = "src"
        # Extract every sub-dict (to avoid loop in loop)
        image_data = []
        for data in [r.values() for r in result]:
            image_data.extend([d for d in data if d.get(url_key)])
        for image_dict in image_data:
            url = image_dict.get(url_key)
            new_url = self.backend_id._replace_by_proxy(url)
            if url != new_url:
                image_dict.update({
                    url_key: new_url,
                })
        return result
