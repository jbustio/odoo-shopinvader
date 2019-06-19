# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
from odoo.addons.shopinvader.tests.common import CommonCase


class SaleCase(CommonCase):

    def _create_fiscal_position(self):
        self.france = self.env.ref('base.fr')
        self.fiscal_position_tax_model = self.env[
            'account.fiscal.position.tax']
        self.tax_model = self.env['account.tax']
        vals = {
            'name': 'Cross Border France',
        }
        self.fiscal_france = self.env['account.fiscal.position'].create(vals)
        self.local_tax = self.env['account.tax'].search([
            ('type_tax_use', '=', 'sale'),
            ('price_include', '=', True),
        ], limit=1)

        self.tax_france = self.tax_model.create(
            dict(name="Include tax",
                 amount='20.00',
                 price_include=True,
                 type_tax_use='sale'))

        self.tax_fiscal_position_fr = self.fiscal_position_tax_model.create(
            dict(position_id=self.fiscal_france.id,
                 tax_src_id=self.local_tax.id,
                 tax_dest_id=self.tax_france.id))

    def _new_sale(self):
        self.partner = self.env.ref('shopinvader.partner_1')
        vals = {
            'partner_id': self.partner.id,
            'partner_invoice_id': self.partner.id,
            'partner_shipping_id': self.partner.id,
            'shopinvader_backend_id': self.backend.id,
            'user_id': self.env.user.id,
            'pricelist_id': self.ref('product.list0'),
            'typology': 'cart',
        }
        self.sale = self.env['sale.order'].create(vals)

    def _add_tax_mapping(self):
        self.backend.write({
            'tax_mapping_ids': [(0, 0, {
                'country_id': self.france.id,
                'fiscal_position_id': self.fiscal_france.id,
            })]
        })

    def _assign_product_tax(self):
        self.product.taxes_id = self.local_tax

    def setUp(self, *args, **kwargs):
        super(SaleCase, self).setUp(*args, **kwargs)
        self.product = self.env.ref('product.product_product_24')
        self._create_fiscal_position()
        self._assign_product_tax()
        self._new_sale()
        self._add_tax_mapping()

    def test_sale(self):
        # Create a sale line
        # Simulate the onchange on the shipping partner and
        # the onchange on fiscal position
        vals = {
            'order_id': self.sale.id,
            'product_id': self.product.id,
            'product_uom_qty': 3.0,
            'product_uom': self.ref('product.product_uom_unit'),
            'price_unit': 800.0,
        }
        line = self.env['sale.order.line'].create(vals)
        self.sale.onchange_partner_shipping_id()
        self.sale._compute_tax_id()
        self.assertEquals(
            self.sale.fiscal_position_id,
            self.fiscal_france
        )
        self.assertEquals(
            self.tax_france,
            line.tax_id,
        )
