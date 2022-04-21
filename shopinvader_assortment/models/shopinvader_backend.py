# -*- coding: utf-8 -*-
# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.osv import expression


class ShopinvaderBackend(models.Model):

    _inherit = "shopinvader.backend"

    product_manual_binding = fields.Boolean(default=True)
    product_assortment_id = fields.Many2one(
        string="Product Assortment",
        comodel_name="ir.filters",
        help="Bind only products matching with the assortment domain",
        domain=[("is_assortment", "=", True)],
        context={"product_assortment": True},
    )

    @api.multi
    def _autobind_product_from_assortment(self, domain_product=None):
        self.ensure_one()
        domain = self.product_assortment_id._get_eval_domain()
        self._bind_products_from_assortment(domain, domain_product)
        self._unbind_products_from_assortment(domain, domain_product)

    def _fast_get_product_ids(self, domain, where_extend, where_args):
        e = expression.expression(domain, self.env["product.product"])
        where_domain, where_params = e.to_sql()
        where_clause = " AND ".join((where_domain, where_extend))
        query = """
            SELECT product_product.id
            FROM product_product, product_template as product_product__product_tmpl_id
            WHERE %s"""
        query = query % where_clause
        # pylint: disable=sql-injection  # YOLO
        self.env.cr.execute(query, tuple(where_params + where_args))
        return [x[0] for x in self.env.cr.fetchall()]

    def _bind_products_from_assortment(self, domain, domain_product=None):
        """Private method, call from _autobind_product_from_assortment."""
        # we do in SQL the equivalent of making:
        # domain_unbound = [("shopinvader_bind_ids", "=", False),
        # ("shopinvader_bind_ids.backend_id", "=", self.id)]
        # domain_to_bind = expression.AND((domain, domain_unbound))
        # to_bind_ids = self.env["product.product"].search(domain_to_bind).ids
        # because the ORM makes a horrible query whereas this should run often
        domain = (
            expression.AND((domain, domain_product))
            if domain_product
            else domain
        )
        where_unbound = """
        NOT EXISTS (
            SELECT shopinvader_variant.id
            FROM shopinvader_variant, shopinvader_product
            WHERE product_product.id = shopinvader_variant.record_id
                AND shopinvader_variant.shopinvader_product_id = shopinvader_product.id
                AND shopinvader_product.backend_id = %s
        )"""
        e = expression.expression(domain, self.env["product.product"])
        where_domain, where_params = e.to_sql()
        where_clause = " AND ".join((where_domain, where_unbound))
        query = """
            SELECT product_product.id
            FROM product_product,
                 product_template as product_product__product_tmpl_id
            WHERE %s"""
        query = query % where_clause
        # pylint: disable=sql-injection
        self.env.cr.execute(query, tuple(where_params + [self.id]))
        to_bind_ids = [x[0] for x in self.env.cr.fetchall()]

        if to_bind_ids:
            product_command = [(6, 0, to_bind_ids)]
            vals = {"backend_id": self.id, "product_ids": product_command}
            wizard_model = self.env["shopinvader.variant.binding.wizard"]
            wizard_model.create(vals).bind_products()

    def _unbind_products_from_assortment(self, domain, domain_product=None):
        """Private method, call from _autobind_product_from_assortment."""
        domain = ["!"] + expression.normalize_domain(domain)
        domain = (
            expression.AND((domain, domain_product))
            if domain_product
            else domain
        )
        e = expression.expression(domain, self.env["product.product"])
        where_domain, where_params = e.to_sql()
        query = """
SELECT shopinvader_variant.id
FROM (shopinvader_variant
INNER JOIN shopinvader_product
    ON shopinvader_variant.shopinvader_product_id = shopinvader_product.id)
WHERE shopinvader_variant.record_id IN (
    SELECT product_product.id
    FROM product_product, product_template as product_product__product_tmpl_id
    WHERE %s
)"""
        query = query % where_domain
        query += " AND shopinvader_product.backend_id = %s"
        # pylint: disable=sql-injection
        self.env.cr.execute(query, tuple(where_params + [self.id]))
        to_unbind_ids = [x[0] for x in self.env.cr.fetchall()]
        if to_unbind_ids:
            vals = {"shopinvader_variant_ids": [(6, 0, to_unbind_ids)]}
            wizard_model = self.env["shopinvader.variant.unbinding.wizard"]
            wizard_model.create(vals).unbind_products()

    @api.model
    def autobind_product_from_assortment(self, domain=None, **kwargs):
        if domain is None:
            domain = []

        domain = expression.AND(
            [domain, [("product_manual_binding", "!=", True)]]
        )

        for backend in self.search(domain):
            backend._autobind_product_from_assortment(**kwargs)

    @api.multi
    def force_recompute_all_binding_index(self):
        records = self.filtered(
            lambda r: not r.product_manual_binding and r.product_assortment_id
        )
        for record in records:
            record._autobind_product_from_assortment()
        return super(
            ShopinvaderBackend, self
        ).force_recompute_all_binding_index()
