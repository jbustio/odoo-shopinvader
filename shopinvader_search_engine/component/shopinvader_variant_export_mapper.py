# -*- coding: utf-8 -*-
# © 2018 Akretion (http://www.akretion.com)
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class ShopinvaderVariantExportMapper(Component):
    _name = 'shopinvader.variant.json.export.mapper'
    _inherit = 'json.export.mapper'
    _apply_on = ['shopinvader.variant']
    _usage = 'se.export.mapper'

    def _apply(self, map_record, options=None):
        values = super(ShopinvaderVariantExportMapper, self)._apply(
            map_record=map_record, options=options)
        values.update(self._add_seo_title(map_record.source))
        return values

    def _add_seo_title(self, record):
        """
        Add the seo_title to export
        :param record: mapped recordset
        :return: dict
        """
        seo_title = record.seo_title
        if not seo_title and record.backend_id.website_public_name:
            seo_title = record._build_seo_product_name()
        return {'seo_title': seo_title}
