# -*- coding: utf-8 -*-
# Copyright 2019 Camptocamp (http://www.camptocamp.com).
# @author Simone Orsi <simone.orsi@camptocamp.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from werkzeug.exceptions import NotFound

from odoo.osv import expression

from odoo.addons.base_rest import restapi
from odoo.addons.base_rest.components.service import to_int
from odoo.addons.component.core import Component


class WishlistService(Component):
    _name = "shopinvader.wishlist.service"
    _inherit = "base.shopinvader.service"
    _usage = "wishlist"
    _expose_model = "product.set"

    # The following method are 'public' and can be called from the controller.
    # All params are untrusted so please check it !

    @restapi.method(
        [(["/<int:_id>/", "/<int:_id>/get/"], "GET")],
        input_param=restapi.CerberusValidator("_validator_empty"),
        output_param=restapi.CerberusValidator("_wishlist_output_schema"),
    )
    def get(self, _id):
        record = self._get(_id)
        return self._to_json_one(record)

    @restapi.method(
        [(["/", "/search/"], "GET")],
        input_param=restapi.CerberusValidator("_validator_search"),
        output_param=restapi.CerberusValidator("_validator_search_output"),
    )
    def search(self, **params):
        return self._paginate_search(**params)

    # pylint: disable=method-required-super
    @restapi.method(
        [(["/", "/create/"], "POST")],
        input_param=restapi.CerberusValidator("_validator_create"),
        output_param=restapi.CerberusValidator("_validator_create_output"),
    )
    def create(self, **params):
        vals = self._prepare_params(params.copy())
        record = self.env[self._expose_model].create(vals)
        self._post_create(record)
        return {"data": self._to_json_one(record)}

    @restapi.method(
        [(["/<int:_id>"], "PUT")],
        input_param=restapi.CerberusValidator("_validator_update"),
        output_param=restapi.CerberusValidator("_validator_search_output"),
    )
    def update(self, _id, **params):
        record = self._get(_id)
        record.write(self._prepare_params(params.copy(), mode="update"))
        self._post_update(record)
        return self.search()

    @restapi.method(
        [(["/<int:_id>"], "DELETE")],
        input_param=restapi.CerberusValidator("_validator_search"),
        output_param=restapi.CerberusValidator("_validator_search_output"),
    )
    def delete(self, _id):
        self._get(_id).unlink()
        return self.search()

    @restapi.method(
        [(["/<int:_id>/add_to_cart/"], "POST")],
        input_param=restapi.CerberusValidator("_validator_empty"),
        output_param=restapi.CerberusValidator("_validator_sale"),
    )
    def add_to_cart(self, _id):
        record = self._get(_id)
        cart_service = self.component(usage="cart")
        cart = cart_service._get()
        wizard = self.env["product.set.add"].create(
            {
                "order_id": cart.id,
                "partner_id": self.partner_user.id,
                "product_set_id": record.id,
                "skip_existing_products": True,
            }
        )
        wizard.add_set()
        # return new cart
        return cart_service._to_json(cart)

    @restapi.method(
        [(["/<int:_id>/add_item/"], "POST")],
        input_param=restapi.CerberusValidator("_validator_add_item"),
        output_param=restapi.CerberusValidator("_wishlist_output_schema"),
    )
    def add_item(self, _id, **params):
        record = self._get(_id)
        self._add_item(record, params)
        return self._to_json_one(record)

    @restapi.method(
        [(["/<int:_id>/update_item/"], "POST")],
        input_param=restapi.CerberusValidator("_validator_update_item"),
        output_param=restapi.CerberusValidator("_wishlist_output_schema"),
    )
    def update_item(self, _id, **params):
        record = self._get(_id)
        self._update_item(record, params)
        return self._to_json_one(record)

    @restapi.method(
        [(["/<int:_id>/delete_item/"], "POST")],
        input_param=restapi.CerberusValidator("_validator_delete_item"),
        output_param=restapi.CerberusValidator("_wishlist_output_schema"),
    )
    def delete_item(self, _id, **params):
        record = self._get(_id)
        self._delete_item(record, params)
        return self._to_json_one(record)

    @restapi.method(
        [(["/<int:_id>/move_item/"], "POST")],
        input_param=restapi.CerberusValidator("_validator_move_item"),
        output_param=restapi.CerberusValidator("_wishlist_output_schema"),
    )
    def move_item(self, _id, **params):
        record = self._get(_id)
        self._move_item(record, params)
        return self._to_json_one(record)

    def _post_create(self, record):
        pass

    def _post_update(self, record):
        pass

    def _validator_empty(self):
        return {}

    def _validator_get(self):
        return self._validator_empty()

    def _validator_search(self):
        return {
            "id": {"coerce": to_int, "type": "integer"},
            "per_page": {
                "coerce": to_int,
                "nullable": True,
                "type": "integer",
            },
            "page": {"coerce": to_int, "nullable": True, "type": "integer"},
            "scope": {"type": "dict", "nullable": True},
        }

    def _validator_search_output(self):
        return {
            "size": {"type": "integer", "required": True, "nullable": False},
            "data": {
                "type": "list",
                "schema": {"schema": self._wishlist_output_schema()},
            },
        }

    def _validator_create(self):
        return self._wishlist_input_schema()

    def _wishlist_line_input_schema(self):
        return {
            "product_id": {"type": "integer", "required": True},
            "quantity": {"type": "float", "required": True},
        }

    def _wishlist_line_output_schema(self):
        # coupled with _json_parser_line
        res = self._wishlist_line_input_schema()
        res["id"] = {"type": "integer", "required": True}
        res["sequence"] = {"type": "integer", "required": True}
        return res

    def _partner_input_schema(self):
        return {
            "type": "integer",
            "coerce": to_int,
            "required": False,
            "nullable": True,
        }

    def _partner_output_schema(self):
        return {
            "id": {"type": "integer", "required": True},
            "name": {"type": "string", "required": True},
        }

    def _wishlist_base_schema(self):
        return {
            "name": {"type": "string", "required": True},
            "ref": {"type": "string", "required": False, "nullable": True},
            "typology": {
                "type": "string",
                "required": False,
                "nullable": True,
            },
        }

    def _wishlist_input_schema(self):
        res = self._wishlist_base_schema()
        res["partner_id"] = self._partner_input_schema()
        res["lines"] = {
            "type": "list",
            "required": True,
            "nullable": False,
            "schema": {
                "type": "dict",
                "schema": self._wishlist_line_input_schema(),
            },
        }
        return res

    def _wishlist_output_schema(self):
        res = self._wishlist_base_schema()
        res["partner"] = {
            "type": "dict",
            "schema": self._partner_output_schema(),
        }
        res["lines"] = {
            "type": "list",
            "required": True,
            "nullable": False,
            "schema": {
                "type": "dict",
                "schema": self._wishlist_line_output_schema(),
            },
        }
        res["id"] = {"type": "integer", "required": True, "nullable": False}
        return res

    def _validator_create_output(self):
        return {
            "data": {"type": "dict", "schema": self._wishlist_output_schema()}
        }

    def _validator_update(self):
        res = self._validator_create()
        for key in res:
            if "required" in res[key]:
                del res[key]["required"]
        return res

    def _validator_add_to_cart(self):
        return {"id": {"coerce": to_int, "type": "integer"}}

    def _validator_add_item(self):
        return {
            "product_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            },
            "quantity": {"coerce": float, "type": "float", "default": 1.0},
        }

    def _validator_update_item(self):
        return self._validator_add_item()

    def _validator_move_item(self):
        return {
            "product_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            },
            "move_to_wishlist_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            },
        }

    def _validator_sale(self):
        return self._sale_output_schema()

    def _sale_output_schema(self):
        # coupled with _convert_one_sale
        # TODO: this should be moved to relevant service
        return {
            "id": {"type": "integer"},
            "state": {"type": "string"},
            "state_label": {"type": "string"},
            "name": {"type": "string"},
            "date": {"type": "string"},
            "step": {"type": "dict"},
            "lines": {"type": "dict"},
            "amount": {"type": "dict"},
            "shipping": {"type": "dict"},
            "invoicing": {"type": "dict"},
            "note": {"type": "string"},
        }

    def _validator_delete_item(self):
        return {
            "product_id": {
                "coerce": to_int,
                "required": True,
                "type": "integer",
            }
        }

    def _get_base_search_domain(self):
        if not self._is_logged_in():
            return expression.FALSE_DOMAIN
        return [
            ("shopinvader_backend_id", "=", self.shopinvader_backend.id),
            ("partner_id", "=", self.partner_user.id),
        ]

    def _prepare_params(self, params, mode="create"):
        if mode == "create":
            params["shopinvader_backend_id"] = self.shopinvader_backend.id
            if not params.get("partner_id"):
                params["partner_id"] = self.partner_user.id
        if not params.get("typology"):
            params["typology"] = "wishlist"
        params["set_line_ids"] = [
            (0, 0, line) for line in params.pop("lines", [])
        ]
        return params

    def _to_json(self, records):
        return records.jsonify(self._json_parser())

    def _to_json_one(self, records):
        values = self._to_json(records)
        if len(records) == 1:
            values = values[0]
        return values

    def _json_parser(self):
        return [
            "id",
            "name",
            "typology",
            "ref",
            ("partner_id:partner", ["id", "name"]),
            ("set_line_ids:lines", self._json_parser_line()),
        ]

    def _json_parser_line(self):
        return [
            "id",
            "sequence",
            "quantity",
            ("shopinvader_variant_id:product_id", lambda s, fn: s[fn].id),
        ]

    def _json_parser_product(self):
        # TODO: might be better to use product's index data
        # to avoid further computation, conversion
        # and mismatch between indexed data and current data.
        parser = [
            "id",
            "name",
            "default_code:sku",
            "url_key",
            "price",
            "object_id:objectID",
        ]
        if "images" in self.env["shopinvader.variant"]._fields:
            # avoid hard dependency on shopinvader_image
            parser.append("images")
        return parser

    def _get_existing_line(self, record, params, raise_if_not_found=False):
        product_id = params["product_id"]
        line = record.get_line_by_product(product_id=product_id)
        if not line and raise_if_not_found:
            raise NotFound(
                "No product found with id %s" % params["product_id"]
            )
        return line

    def _add_item(self, record, params):
        existing = self._get_existing_line(record, params)
        if existing:
            # update qty
            existing.quantity += params["quantity"]
        else:
            self.env["product.set.line"].create(
                self._prepare_item(params, record)
            )

    def _update_item(self, record, params):
        existing = self._get_existing_line(
            record, params, raise_if_not_found=True
        )
        if existing:
            # update qty
            existing.quantity += params["quantity"]
        else:
            self.env["product.set.line"].create(
                self._prepare_item(params, record)
            )

    def _move_item(self, record, params):
        existing = self._get_existing_line(
            record, params, raise_if_not_found=True
        )
        record2 = self._get(params["move_to_wishlist_id"])
        self.env["product.set.line"].create(
            self._prepare_item(params, record2)
        )
        existing.unlink()

    def _prepare_item(self, params, record):
        return {
            "product_set_id": record.id,
            "product_id": params["product_id"],
            "quantity": params.get("quantity") or 1,
        }

    def _delete_item(self, record, params):
        existing = self._get_existing_line(
            record, params, raise_if_not_found=True
        )
        if existing:
            existing.unlink()
