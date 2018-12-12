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

    @api.depends('backend_id.se_backend_id',
                 'backend_id.se_backend_id.index_ids')
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
        Inherit the function to get the seo_title from mapper who fill the
        data key.
        If the seo_title is already defined, do not update it.
        :param mapper: export mapper
        :param force_export: bool
        :return: dict
        """
        values = super(ShopinvaderVariant, self)._get_values_recompute_json(
            mapper, force_export=force_export)
        if not self.seo_title and self.backend_id.website_public_name:
            seo_title = values.get('data', {}).get('seo_title', False)
            # If the seo_title has been updated, update it also on the product.
            # The logic to re-build the seo_title should come from the
            # mapper for this case
            if self.seo_title != seo_title:
                values.update({
                    'seo_title': seo_title,
                })
        return values

    @api.multi
    def _build_seo_product_name(self):
        """
        Build the SEO product name
        :return: str
        """
        return u"{} | {}".format(
            self.name or u"", self.backend_id.website_public_name or u"")
