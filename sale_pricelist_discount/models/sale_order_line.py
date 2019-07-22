# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).
# flake8: noqa

# backport from odoo 10.0

from openerp import _, api, fields, models


class SaleOrderLine(models.Model):

    _inherit = "sale.order.line"

    @api.onchange("product_uom", "product_uom_qty")
    def product_uom_change(self):
        res = super(SaleOrderLine, self).product_uom_change()
        if not self.product_uom or not self.product_id:
            return res
        if self.order_id.pricelist_id and self.order_id.partner_id:
            product = self.product_id.with_context(
                lang=self.order_id.partner_id.lang,
                partner=self.order_id.partner_id.id,
                quantity=self.product_uom_qty,
                date=self.order_id.date_order,
                pricelist=self.order_id.pricelist_id.id,
                uom=self.product_uom.id,
                fiscal_position=self.env.context.get("fiscal_position"),
            )
            self.price_unit = self.env[
                "account.tax"
            ]._fix_tax_included_price_company(
                self._get_display_price(product),
                product.taxes_id,
                self.tax_id,
                self.company_id,
            )
        return res

    @api.multi
    @api.onchange("product_id")
    def product_id_change(self):
        res = super(SaleOrderLine, self).product_id_change()

        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
        )

        if self.order_id.pricelist_id and self.order_id.partner_id:
            self.price_unit = self.env[
                "account.tax"
            ]._fix_tax_included_price_company(
                self._get_display_price(product),
                product.taxes_id,
                self.tax_id,
                self.company_id,
            )
        return res

    @api.multi
    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        if not product:
            return 0.0
        if self.order_id.pricelist_id.discount_policy == "with_discount":
            return product.with_context(
                pricelist=self.order_id.pricelist_id.id
            ).price
        product_context = dict(
            self.env.context,
            partner_id=self.order_id.partner_id.id,
            date=self.order_id.date_order,
            uom=self.product_uom.id,
        )
        final_price, rule_id = self.order_id.pricelist_id.with_context(
            product_context
        ).get_product_price_rule(
            self.product_id,
            self.product_uom_qty or 1.0,
            self.order_id.partner_id,
        )
        base_price, currency_id = self.with_context(
            product_context
        )._get_real_price_currency(
            product,
            rule_id,
            self.product_uom_qty,
            self.product_uom,
            self.order_id.pricelist_id.id,
        )
        if currency_id != self.order_id.pricelist_id.currency_id.id:
            base_price = (
                self.env["res.currency"]
                .browse(currency_id)
                .with_context(product_context)
                .compute(base_price, self.order_id.pricelist_id.currency_id)
            )
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    @api.multi
    def _get_real_price_currency(
        self, product, rule_id, qty, uom, pricelist_id
    ):
        """Retrieve the price before applying the pricelist
            :param obj product: object of current product record
            :parem float qty: total quentity of product
            :param tuple price_and_rule: tuple(price, suitable_rule) coming from pricelist computation
            :param obj uom: unit of measure of current order line
            :param integer pricelist_id: pricelist id of sale order"""
        PricelistItem = self.env["product.pricelist.item"]
        field_name = "lst_price"
        currency_id = None
        product_currency = None
        if rule_id:
            pricelist_item = PricelistItem.browse(rule_id)
            if (
                pricelist_item.pricelist_id.discount_policy
                == "without_discount"
            ):
                while (
                    pricelist_item.base == "pricelist"
                    and pricelist_item.base_pricelist_id
                    and pricelist_item.base_pricelist_id.discount_policy
                    == "without_discount"
                ):
                    price, rule_id = pricelist_item.base_pricelist_id.with_context(
                        uom=uom.id
                    ).get_product_price_rule(
                        product, qty, self.order_id.partner_id
                    )
                    pricelist_item = PricelistItem.browse(rule_id)

            if pricelist_item.base == "standard_price":
                field_name = "standard_price"
            if (
                pricelist_item.base == "pricelist"
                and pricelist_item.base_pricelist_id
            ):
                field_name = "price"
                product = product.with_context(
                    pricelist=pricelist_item.base_pricelist_id.id
                )
                product_currency = pricelist_item.base_pricelist_id.currency_id
            currency_id = pricelist_item.pricelist_id.currency_id

        product_currency = (
            product_currency
            or (product.company_id and product.company_id.currency_id)
            or self.env.user.company_id.currency_id
        )
        if not currency_id:
            currency_id = product_currency
            cur_factor = 1.0
        else:
            if currency_id.id == product_currency.id:
                cur_factor = 1.0
            else:
                cur_factor = currency_id._get_conversion_rate(
                    product_currency, currency_id
                )

        product_uom = self.env.context.get("uom") or product.uom_id.id
        if uom and uom.id != product_uom:
            # the unit price is in a different uom
            uom_factor = uom._compute_price(1.0, product.uom_id)
        else:
            uom_factor = 1.0

        return product[field_name] * uom_factor * cur_factor, currency_id.id

    @api.onchange(
        "product_id", "price_unit", "product_uom", "product_uom_qty", "tax_id"
    )
    def _onchange_discount(self):
        if not (
            self.product_id
            and self.product_uom
            and self.order_id.partner_id
            and self.order_id.pricelist_id
            and self.order_id.pricelist_id.discount_policy
            == "without_discount"
            and self.env.user.has_group("sale.group_discount_per_so_line")
        ):
            return

        self.discount = 0.0
        product = self.product_id.with_context(
            lang=self.order_id.partner_id.lang,
            partner=self.order_id.partner_id.id,
            quantity=self.product_uom_qty,
            date=self.order_id.date_order,
            pricelist=self.order_id.pricelist_id.id,
            uom=self.product_uom.id,
            fiscal_position=self.env.context.get("fiscal_position"),
        )

        product_context = dict(
            self.env.context,
            partner_id=self.order_id.partner_id.id,
            date=self.order_id.date_order,
            uom=self.product_uom.id,
        )

        price, rule_id = self.order_id.pricelist_id.with_context(
            product_context
        ).get_product_price_rule(
            self.product_id,
            self.product_uom_qty or 1.0,
            self.order_id.partner_id,
        )
        new_list_price, currency_id = self.with_context(
            product_context
        )._get_real_price_currency(
            product,
            rule_id,
            self.product_uom_qty,
            self.product_uom,
            self.order_id.pricelist_id.id,
        )

        if new_list_price != 0:
            if self.order_id.pricelist_id.currency_id.id != currency_id:
                # we need new_list_price in the same currency as price, which is in the SO's pricelist's currency
                new_list_price = (
                    self.env["res.currency"]
                    .browse(currency_id)
                    .with_context(product_context)
                    .compute(
                        new_list_price, self.order_id.pricelist_id.currency_id
                    )
                )
            discount = (new_list_price - price) / new_list_price * 100
            if discount > 0:
                self.discount = discount
