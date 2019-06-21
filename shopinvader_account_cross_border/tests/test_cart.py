from odoo.addons.shopinvader.tests.test_cart import CommonConnectedCartCase

from .common import CrossBorderCommonCase


class CrossBorderCartCase(CommonConnectedCartCase, CrossBorderCommonCase):
    def test_set_shipping_address(self):
        vals = {
            "order_id": self.cart.id,
            "product_id": self.product.id,
            "product_uom_qty": 3.0,
            "product_uom": self.ref("product.product_uom_unit"),
            "price_unit": 800.0,
        }
        line = self.env["sale.order.line"].create(vals)
        self.service.dispatch(
            "update", params={"shipping": {"address": {"id": self.address.id}}}
        )
        cart = self.cart
        self.assertEquals(cart.fiscal_position_id, self.fiscal_france)
        self.assertEquals(self.tax_france, line.tax_id)
