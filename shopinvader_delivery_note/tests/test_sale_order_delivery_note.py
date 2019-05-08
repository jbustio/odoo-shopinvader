# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from uuid import uuid4
from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class TestSaleOrderDeliveryNote(CommonConnectedCartCase):
    """
    Tests about the delivery note provided by the customer.
    This field should by passed into the related picking.
    """

    def setUp(self):
        super(TestSaleOrderDeliveryNote, self).setUp()

    def test_update_delivery_note1(self):
        """
        Execute some update on existing cart.
        :return:
        """
        delivery_notes = [
            str(uuid4()),
            str(uuid4()),
            False,
            False,
            str(uuid4()),
            str(uuid4()),
        ]
        for delivery_note in delivery_notes:
            params = {
                "delivery_note": delivery_note,
            }
            self.service.dispatch("update", params=params)
            self.assertEqual(self.cart.delivery_note, delivery_note)
        return
