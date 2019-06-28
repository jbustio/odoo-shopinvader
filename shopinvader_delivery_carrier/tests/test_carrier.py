# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase


class CarrierCase(CommonConnectedCartCase):
    def setUp(self):
        super(CarrierCase, self).setUp()
        self.free_carrier = self.env.ref("delivery.free_delivery_carrier")
        self.poste_carrier = self.env.ref("delivery.delivery_carrier")
        self.product_1 = self.env.ref("product.product_product_4b")

    def extract_cart(self, response):
        self.shopinvader_session["cart_id"] = response["set_session"][
            "cart_id"
        ]
        self.assertEqual(response["store_cache"], {"cart": response["data"]})
        return response["data"]

    def add_item(self, product_id, qty):
        return self.extract_cart(
            self.service.dispatch(
                "add_item", params={"product_id": product_id, "item_qty": qty}
            )
        )

    def update_item(self, item_id, qty):
        return self.extract_cart(
            self.service.dispatch(
                "update_item", params={"item_id": item_id, "item_qty": qty}
            )
        )

    def delete_item(self, item_id):
        return self.extract_cart(
            self.service.dispatch("delete_item", params={"item_id": item_id})
        )

    def _set_carrier(self, carrier):
        response = self.service.dispatch(
            "apply_delivery_method", params={"carrier": {"id": carrier.id}}
        )
        self.assertEqual(self.cart.carrier_id.id, carrier.id)
        return response["data"]

    def _apply_carrier_and_assert_set(self):
        cart = self._set_carrier(self.poste_carrier)
        self.assertEqual(cart["shipping"]["amount"]["total"], 20)
        return cart

    def test_available_carriers(self):
        response = self.service.dispatch("get_delivery_methods")
        self.assertEqual(len(response), 2)

    def test_setting_free_carrier(self):
        cart = self._set_carrier(self.free_carrier)
        self.assertEqual(cart["shipping"]["amount"]["total"], 0)

    def test_setting_poste_carrier(self):
        cart = self._set_carrier(self.poste_carrier)
        # Check shipping amount
        cart_ship = cart.get("shipping")
        self.assertEqual(cart_ship["amount"]["total"], 20)
        self.assertEqual(cart_ship["amount"]["untaxed"], 17.39)
        self.assertEqual(cart_ship["amount"]["tax"], 2.61)

        # Check items amount
        self.assertEqual(cart["lines"]["amount"]["total"], 8555.0)
        self.assertEqual(cart["lines"]["amount"]["untaxed"], 8555.0)
        self.assertEqual(cart["lines"]["amount"]["tax"], 0)

        # Check total amount
        self.assertEqual(cart["amount"]["total"], 8575.0)
        self.assertEqual(cart["amount"]["untaxed"], 8572.39)
        self.assertEqual(cart["amount"]["tax"], 2.61)

        # Check totals without shipping prices
        cart_amount = cart.get("amount")
        total_without_shipping = (
            cart_amount["total"] - cart_ship["amount"]["total"]
        )
        untaxed_without_shipping = (
            cart_amount["untaxed"] - cart_ship["amount"]["untaxed"]
        )
        tax_without_shipping = cart_amount["tax"] - cart_ship["amount"]["tax"]
        self.assertEqual(
            cart_amount["total_without_shipping"], total_without_shipping
        )
        self.assertEqual(
            cart_amount["untaxed_without_shipping"], untaxed_without_shipping
        )
        self.assertEqual(
            cart_amount["tax_without_shipping"], tax_without_shipping
        )

    def test_reset_carrier_on_add_item(self):
        self._apply_carrier_and_assert_set()
        cart = self.add_item(self.product_1.id, 2)
        self.assertEqual(cart["shipping"]["amount"]["total"], 0)
        self.assertFalse(cart["shipping"]["selected_carrier"])

    def test_reset_carrier_on_update_item(self):
        cart = self._apply_carrier_and_assert_set()
        items = cart["lines"]["items"]
        cart = self.update_item(items[0]["id"], 1)
        self.assertEqual(cart["shipping"]["amount"]["total"], 0)
        self.assertFalse(cart["shipping"]["selected_carrier"])

    def test_reset_carrier_on_delte_item(self):
        cart = self._apply_carrier_and_assert_set()
        items = cart["lines"]["items"]
        cart = self.delete_item(items[0]["id"])
        self.assertEqual(cart["shipping"]["amount"]["total"], 0)
        self.assertFalse(cart["shipping"]["selected_carrier"])

    def test_get_cart_price_by_country1(self):
        """
        Check the service get_cart_price_by_country.
        For this case, the cart doesn't have an existing delivery line.
        :return:
        """
        french_country = self.env.ref("base.fr")
        belgium = self.env.ref("base.be")
        partner = self.cart.partner_id
        partner.write({"country_id": french_country.id})
        self.cart.write({"carrier_id": self.poste_carrier.id})
        # Force load every fields
        self.cart.read()
        cart_values_before = self.cart._convert_to_write(self.cart._cache)
        lines = {}
        for line in self.cart.order_line:
            line.read()
            lines.update({line.id: line._convert_to_write(line._cache)})
        nb_lines_before = self.env["sale.order.line"].search_count([])
        self.service.shopinvader_session.update({"cart_id": self.cart.id})
        params = {"country_id": belgium.id}
        result_get = self.service.dispatch("search")
        result = self.service.dispatch(
            "get_cart_price_by_country", params=params
        )
        self.assertEquals(self.cart.name, cart_values_before.get("name", ""))
        self.cart.read()
        cart_values_after = self.cart._convert_to_write(self.cart._cache)
        self.assertDictEqual(cart_values_before, cart_values_after)
        nb_lines_after = self.env["sale.order.line"].search_count([])
        self.assertEquals(nb_lines_after, nb_lines_before)
        # Ensure lines still ok
        self.assertEquals(len(lines), len(self.cart.order_line))
        for line_id, line_values in lines.iteritems():
            order_line = self.cart.order_line.filtered(
                lambda l, lid=line_id: l.id == lid
            )
            order_line.read()
            self.assertDictEqual(
                order_line._convert_to_write(order_line._cache), line_values
            )
        self.assertEquals(self.cart.partner_id, partner)
        self.assertEquals(french_country, partner.country_id)
        result_data, result_get_data = self._remove_allowed_differences(
            result, result_get
        )
        self.assertEquals(result_data, result_get_data)

    def _remove_allowed_differences(self, result, result_get):
        """
        Remove allowed differences between 2 given dict.
        :param result:
        :param result_get:
        :return:
        """
        # Now check the 2 results/get
        # But first remove keys who should be different
        result_data = result.get("data")
        result_get_data = result_get.get("data")
        drop_keys = ["amount", "shipping"]
        for k in drop_keys:
            result_data.pop(k, None)
            result_get_data.pop(k, None)
        invoicing_drop_keys = ["zip", "country"]
        for k in invoicing_drop_keys:
            result_data.get("invoicing", {}).get("address", {}).pop(k, None)
            result_get_data.get("invoicing", {}).get("address", {}).pop(
                k, None
            )
        return result_data, result_get_data

    def test_get_cart_price_by_country2(self):
        """
        Check the service get_cart_price_by_country.
        For this case, the cart have 1 delivery line set (who will be removed)
        :return:
        """
        french_country = self.env.ref("base.fr")
        belgium = self.env.ref("base.be")
        partner = self.cart.partner_id
        partner.write({"country_id": french_country.id})
        self.cart.write({"carrier_id": self.poste_carrier.id})
        self.cart.delivery_set()
        # Force load every fields
        self.cart.read()
        cart_values_before = self.cart._convert_to_write(self.cart._cache)
        cart_values_before.pop("order_line", None)
        lines = {}
        for line in self.cart.order_line:
            line.read()
            lines.update({line.id: line._convert_to_write(line._cache)})
        nb_lines_before = self.env["sale.order.line"].search_count([])
        self.service.shopinvader_session.update({"cart_id": self.cart.id})
        params = {"country_id": belgium.id}
        result_get = self.service.dispatch("search")
        result = self.service.dispatch(
            "get_cart_price_by_country", params=params
        )
        self.assertEquals(self.cart.name, cart_values_before.get("name", ""))
        self.cart.read()
        cart_values_after = self.cart._convert_to_write(self.cart._cache)
        cart_values_after.pop("order_line", None)
        self.assertDictEqual(cart_values_before, cart_values_after)
        nb_lines_after = self.env["sale.order.line"].search_count([])
        self.assertEquals(nb_lines_after, nb_lines_before)
        # Ensure lines still ok
        self.assertEquals(len(lines), len(self.cart.order_line))
        for line_id, line_values in lines.iteritems():
            order_line = self.cart.order_line.filtered(
                lambda l, lid=line_id: l.id == lid
            )
            # Because delivery line has changed and the ID doesn't match
            # anymore.
            # But should still similar!
            if not order_line:
                order_line = self.cart.order_line.filtered(
                    lambda l: l.is_delivery
                )
            order_line.read()
            self.assertDictEqual(
                order_line._convert_to_write(order_line._cache), line_values
            )
        self.assertEquals(self.cart.partner_id, partner)
        self.assertEquals(french_country, partner.country_id)
        result_data, result_get_data = self._remove_allowed_differences(
            result, result_get
        )
        self.assertEquals(result_data, result_get_data)
