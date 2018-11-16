# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ShopinvaderVariant(models.Model):
    _inherit = ['shopinvader.variant', 'se.binding']
    _name = 'shopinvader.variant'
    _description = 'Shopinvader Variant'

    index_id = fields.Many2one(
        compute="_compute_index",
        store=True,
        required=False)

    @api.depends('backend_id.se_backend_id')
    def _compute_index(self):
        for record in self:
            se_backend = record.backend_id.se_backend_id
            if se_backend:
                record.index_id = self.env['se.index'].search([
                    ('backend_id', '=', se_backend.id),
                    ('model_id.model', '=', record._name),
                    ('lang_id', '=', record.lang_id.id)
                    ], limit=1)

    @api.multi
    def _get_values_recompute_json(self, mapper, force_export=False):
        """
        Inherit the values dict to fill the seo_title if the backend
        has the website_public_name filled.
        If the seo_title is already defined, do not update it.
        :param mapper: export mapper
        :param force_export: bool
        :return: dict
        """
        values = super(ShopinvaderVariant, self)._get_values_recompute_json(
            mapper, force_export=force_export)
        if not self.seo_title and self.backend_id.website_public_name:
            name = self._build_seo_product_name()
            values.update({
                'seo_title': name,
            })
        return values

    @api.mutli
    def _build_seo_product_name(self):
        """
        Build the SEO product name
        :return: str
        """
        return self.name + " | " + self.backend_id.website_public_name
