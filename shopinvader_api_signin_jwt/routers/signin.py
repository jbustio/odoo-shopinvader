# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from odoo import api, models

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi.dependencies import odoo_env
from odoo.addons.fastapi_auth_jwt.dependencies import (
    Payload,
    auth_jwt_authenticated_payload,
    auth_jwt_optionally_authenticated_partner,
)

signin_router = APIRouter(tags=["signin"])


@signin_router.post("/signin", status_code=200)
def signin(
    env: Annotated[api.Environment, Depends(odoo_env)],
    partner: Annotated[Partner, Depends(auth_jwt_optionally_authenticated_partner)],
    payload: Annotated[Payload, Depends(auth_jwt_authenticated_payload)],
    response: Response,
) -> None:
    if not partner:
        env[
            "shopinvader_api_signin_jwt.signin_router.helper"
        ]._create_partner_from_payload(payload)
        response.status_code = status.HTTP_201_CREATED


class ShopinvaderApSigninJwtRouterHelper(models.AbstractModel):
    _name = "shopinvader_api_signin_jwt.signin_router.helper"
    _description = "ShopInvader API Signin Jwt Router Helper"

    @api.model
    def _get_partner_vals(self, payload: Payload):
        return {"name": payload.get("name"), "email": payload.get("email")}

    @api.model
    def _create_partner_from_payload(self, payload: Payload):
        return self.env["res.partner"].browse(
            self.env["res.partner"].sudo().create(self._get_partner_vals(payload)).id
        )
