# Copyright 2023 ACSONE SA/NV
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.shopinvader_api_address.schemas import (
    DeliveryAddressCreate,
    DeliveryAddressUpdate,
)
from odoo.addons.shopinvader_schema_address.schemas import DeliveryAddress


class ShippingAddressNote(DeliveryAddress, extends=DeliveryAddress):
    """
    Shipping Address
    """

    shipping_note: str | None = None

    @classmethod
    def from_res_partner(cls, odoo_rec):
        res = super().from_res_partner(odoo_rec)
        res.shipping_note = odoo_rec.shipping_note or None

        return res


class ShippingAddressNoteCreate(DeliveryAddressCreate, extends=DeliveryAddressCreate):
    """
    Creation of Shipping Address
    """

    shipping_note: str | None = None

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()

        vals["shipping_note"] = self.shipping_note

        return vals


class ShippingAddressNoteUpdate(DeliveryAddressUpdate, extends=DeliveryAddressUpdate):
    """
    Update of Shipping Address
    """

    shipping_note: str | None = None

    def to_res_partner_vals(self) -> dict:
        vals = super().to_res_partner_vals()
        shipping_note = self.shipping_note
        if shipping_note is not None:
            vals["shipping_note"] = shipping_note
        return vals
