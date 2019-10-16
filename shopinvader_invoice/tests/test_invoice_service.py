# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from .common import CommonInvoiceCase


class TestInvoiceServiceAnonymous(CommonInvoiceCase):
    def setUp(self, *args, **kwargs):
        super(TestInvoiceServiceAnonymous, self).setUp(*args, **kwargs)
        self.partner = self.env.ref("base.res_partner_2").copy()

    def test_get_invoice_anonymous(self):
        """
        Test the get on guest mode (using anonymous user).
        It should not return any result, even if the anonymous user has some
        invoices
        :return:
        """
        # Check first without invoice related to the anonymous user
        result = self.service_guest.dispatch("search")
        data = result.get("data", [])
        self.assertFalse(data)
        # Then create a invoice related to the anonymous user
        invoice = self._create_invoice(
            partner=self.backend.anonymous_partner_id, validate=True
        )
        self.assertEquals(
            invoice.partner_id, self.backend.anonymous_partner_id
        )
        result = self.service_guest.dispatch("search")
        data = result.get("data", [])
        self.assertFalse(data)
        return


class TestInvoiceService(CommonInvoiceCase):
    def test_get_invoice_logged(self):
        """
        Test the get on a logged user.
        In the first part, the user should have any invoice.
        But to the second, he should have one.
        :return:
        """
        # Check first without invoice related to the partner
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self.assertFalse(data)
        # Then create a invoice related to partner
        invoice = self._confirm_and_invoice_sale(self.sale, payment=False)
        self.assertEquals(invoice.partner_id, self.service.partner)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, invoice)
        self._make_payment(invoice)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, invoice)
        return

    def test_get_multi_invoice(self):
        """
        Test the get on a logged user.
        In the first part, the user should have any invoice.
        But to the second, he should have one.
        :return:
        """
        sale2 = self.sale.copy()
        sale3 = self.sale.copy()
        sale4 = self.sale.copy()
        invoice1 = self._confirm_and_invoice_sale(self.sale)
        invoice2 = self._confirm_and_invoice_sale(sale2)
        invoice3 = self._confirm_and_invoice_sale(sale3)
        invoice4 = self._confirm_and_invoice_sale(sale4)
        invoices = invoice1 | invoice2 | invoice3 | invoice4
        self.assertEquals(invoice1.partner_id, self.service.partner)
        self.assertEquals(invoice2.partner_id, self.service.partner)
        self.assertEquals(invoice3.partner_id, self.service.partner)
        self.assertEquals(invoice4.partner_id, self.service.partner)
        result = self.service.dispatch("search")
        data = result.get("data", [])
        self._check_data_content(data, invoices)
        return
