# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo.addons.component.core import Component


class CartService(Component):
    _inherit = "shopinvader.cart.service"

    def _validator_update(self):
        validator = super(CartService, self)._validator_update()
        validator.update({
            'delivery_note': {
                "type": "string",
            },
        })
        return validator

    def _prepare_delivery_note(self, delivery_note, params):
        """
        Put the given delivery note into params dict (used to create the
        sale.order).
        :param delivery_note: str or bool
        :param params: dict
        :return: bool
        """
        if delivery_note:
            params.update({
                'delivery_note': delivery_note,
            })
        return True

    def _prepare_update(self, cart, params):
        params = super(CartService, self)._prepare_update(cart, params)
        self._prepare_delivery_note(params.pop('delivery_note', False), params)
        return params
