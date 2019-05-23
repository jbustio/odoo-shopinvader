# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import api, fields
from odoo.addons.shopinvader.tests.test_notification import CommonCase


class TestSaleOrder(CommonCase):
    """
    Tests for sale.order
    """

    def setUp(self):
        super(TestSaleOrder, self).setUp()
        self.sale_obj = self.env["sale.order"]
        self.sale = self.env.ref("shopinvader.sale_order_2")
        self.template = self.env.ref(
            "shopinvader_cart_reminder."
            "mail_template_shopinvader_sale_reminder"
        )
        self.backend.write(
            {
                "quotation_reminder": 1,
                "quotation_reminder_mail_template_id": self.template.id,
            }
        )

    def test_reminder1(self):
        """
        Test the reminder
        For this case, the sale should have a reminder
        :return:
        """
        # Ensure not already a reminder
        self.assertFalse(self.sale.last_reminder)

        @api.model
        def _get_reminder_date(self, backend):
            return fields.Datetime.from_string(fields.Datetime.now())

        now = fields.Datetime.from_string(fields.Datetime.now())
        self.sale_obj._patch_method("_get_reminder_date", _get_reminder_date)
        self.addCleanup(self.sale_obj._revert_method, "_get_reminder_date")
        self.sale_obj.launch_reminder()
        self.assertGreaterEqual(
            fields.Datetime.from_string(self.sale.last_reminder), now
        )
        return

    def test_reminder2(self):
        """
        Test the reminder
        For this case, the sale shouldn't have a reminder
        :return:
        """
        # Ensure not already a reminder
        self.assertFalse(self.sale.last_reminder)

        @api.model
        def _get_reminder_date(self, backend):
            tomorrow = fields.Datetime.from_string(fields.Datetime.now())
            tomorrow -= timedelta(days=4)
            return tomorrow

        self.sale_obj._patch_method("_get_reminder_date", _get_reminder_date)
        self.addCleanup(self.sale_obj._revert_method, "_get_reminder_date")
        self.sale_obj.launch_reminder()
        self.assertFalse(self.sale.last_reminder)
        return

    def test_reminder3(self):
        """
        Test the reminder
        For this case, the sale already have a reminder and shouldn't be
        updated
        :return:
        """
        now = fields.Datetime.now()
        self.sale.write({"last_reminder": now})

        @api.model
        def _get_reminder_date(self, backend):
            return fields.Datetime.from_string(fields.Datetime.now())

        self.sale_obj._patch_method("_get_reminder_date", _get_reminder_date)
        self.addCleanup(self.sale_obj._revert_method, "_get_reminder_date")
        self.sale_obj.launch_reminder()
        self.assertEquals(self.sale.last_reminder, now)
        return

    def test_reminder4(self):
        """
        Test the reminder
        For this case, the sale is not a cart (but a "normal" sale)
        :return:
        """
        self.sale.write({"typology": "sale"})
        values_before = self.sale.read()[0]

        @api.model
        def _get_reminder_date(self, backend):
            return fields.Datetime.from_string(fields.Datetime.now())

        self.sale_obj._patch_method("_get_reminder_date", _get_reminder_date)
        self.addCleanup(self.sale_obj._revert_method, "_get_reminder_date")
        self.sale_obj.launch_reminder()
        values_after = self.sale.read()[0]
        # Nothing should change
        self.assertDictEqual(values_after, values_before)
        return

    def test_reminder5(self):
        """
        Test the reminder
        For this case, the partner of the sale is the anonymous user
        (so no email)
        :return:
        """
        self.sale.write({"partner_id": self.backend.anonymous_partner_id.id})
        values_before = self.sale.read()[0]

        @api.model
        def _get_reminder_date(self, backend):
            return fields.Datetime.from_string(fields.Datetime.now())

        self.sale_obj._patch_method("_get_reminder_date", _get_reminder_date)
        self.addCleanup(self.sale_obj._revert_method, "_get_reminder_date")
        self.sale_obj.launch_reminder()
        values_after = self.sale.read()[0]
        # Nothing should change
        self.assertDictEqual(values_after, values_before)
        return
