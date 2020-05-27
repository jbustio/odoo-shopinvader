# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.common import CommonCase


class TestCart(CommonCase):
    def setUp(self):
        super(TestCart, self).setUp()
        self.cart = self.env.ref("shopinvader.sale_order_2")
        self.shopinvader_session = {"cart_id": self.cart.id}
        self.partner = self.env.ref("shopinvader.partner_1")
        self.address = self.env.ref("shopinvader.partner_1_address_1")
        with self.work_on_services(
            partner=self.partner, shopinvader_session=self.shopinvader_session
        ) as work:
            self.service = work.component(usage="cart")

    def test_cart_to_quotation(self):
        customer_comment = "CUSTOMER TEST"
        vendor_comment = "VENDOR TEST"
        params = {
            "vendor_comment": vendor_comment,
            "customer_comment": customer_comment,
        }
        self.service.dispatch("update", params=params)
        # Vendor comment should never be updated from the front
        self.assertFalse(self.cart.vendor_comment)
        self.assertEqual(self.cart.customer_comment, customer_comment)
        self.assertEqual(self.cart.typology, "cart")
        self.service.dispatch("request_quotation", params={})
        self.assertEqual(self.cart.typology, "quotation")
        quotation = self.service.search()["data"]
        self.assertFalse(quotation["vendor_comment"])
        self.assertEqual(quotation["customer_comment"], customer_comment)
