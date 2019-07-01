# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from contextlib import contextmanager

from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component
from odoo.exceptions import UserError
from odoo.tools.translate import _


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def get_delivery_methods(self, **params):
        """
        This service will return all possible delivery methods for the
        current cart (depending on country/zip)
        The cart is not updated with the given country/zip. The change is done
        only in memory.
        :param params: dict
        :return: dict
        """
        cart = self._get()
        country = self._load_country(params)
        zip_code = self._load_zip_code(params)
        if country or zip_code:
            with self._simulate_delivery_cost(cart):
                # Edit country and zip
                # Even if some info are not provided, we have to fill them
                # Ex: if the zip code is not provided, we have to do the
                # simulation with an empty zip code on the partner. Because his
                # current zip could be related to another country and simulate
                # a wrong price.
                cart.partner_id.update(
                    {"country_id": country.id, "zip": zip_code}
                )
                result = self._get_available_carrier(cart)
        else:
            result = self._get_available_carrier(cart)
        return result

    def apply_delivery_method(self, **params):
        """
            This service will apply the given delivery method to the current
            cart
        :param params: Dict containing delivery method to apply
        :return:
        """
        cart = self._get()
        if not cart:
            raise UserError(_("There is not cart"))
        else:
            self._set_carrier(cart, params["carrier"]["id"])
            return self._to_json(cart)

    @contextmanager
    def _simulate_delivery_cost(self, cart):
        """
        Change the env mode (draft) to avoid real update on the partner.
        Then, restore the cart with previous values.
        As the delivery_set function create a new sale.order.line related to
        the current cart, we have to remove it (by _delivery_unset).
        So if the cart already had a delivery line, this one will be removed!
        :param cart: sale.order recordset
        :return:
        """
        partner = cart.partner_id or self.partner
        partner_values = partner._convert_to_write(partner._cache)
        with partner.env.do_in_draft():
            yield
            partner.update(partner_values)

    # Validator
    def _validator_apply_delivery_method(self):
        return {
            "carrier": {
                "type": "dict",
                "schema": {
                    "id": {
                        "coerce": int,
                        "nullable": True,
                        "required": True,
                        "type": "integer",
                    }
                },
            }
        }

    def _validator_get_delivery_methods(self):
        return {
            "country_id": {
                "coerce": to_int,
                "required": False,
                "type": "integer",
            },
            "zip_code": {"required": False, "type": "string"},
        }

    # internal methods
    def _load_country(self, params):
        """
        Load the country from given params
        :param params: dict
        :return: res.country recordset
        """
        country_id = params.pop("country_id", 0)
        return self.env["res.country"].browse(country_id)

    def _load_zip_code(self, params):
        """
        Load the country from given params
        :param params: dict
        :return: str
        """
        return params.pop("zip_code", "")

    def _add_item(self, cart, params):
        res = super(CartService, self)._add_item(cart, params)
        self._unset_carrier(cart)
        return res

    def _update_item(self, cart, params, item=False):
        res = super(CartService, self)._update_item(cart, params, item)
        self._unset_carrier(cart)
        return res

    def _delete_item(self, cart, params):
        res = super(CartService, self)._delete_item(cart, params)
        self._unset_carrier(cart)
        return res

    def _set_carrier(self, cart, carrier_id):
        if carrier_id not in [
            x["id"] for x in self._get_available_carrier(cart)
        ]:
            raise UserError(
                _("This delivery method is not available for you order")
            )
        cart.write({"carrier_id": carrier_id})
        cart.delivery_set()

    def _unset_carrier(self, cart):
        cart.write({"carrier_id": False})
        cart._delivery_unset()
