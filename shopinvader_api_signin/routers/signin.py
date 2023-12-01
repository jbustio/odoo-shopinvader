# Copyright 2023 ACSONE SA/NV
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from odoo.addons.base.models.res_partner import Partner
from odoo.addons.fastapi_auth_jwt.dependencies import (
    Payload,
    auth_jwt_authenticated_payload,
    auth_jwt_optionally_authenticated_partner,
)

signin_router = APIRouter(tags=["signin"])


@signin_router.post("/signin", status_code=200)
def signin(
    partner: Annotated[Partner, Depends(auth_jwt_optionally_authenticated_partner)],
    payload: Annotated[Payload, Depends(auth_jwt_authenticated_payload)],
    response: Response,
) -> None:
    if not partner:
        partner._create_partner_from_payload(payload)
        response.status_code = status.HTTP_201_CREATED
    # TODO: Manage anonymous cart ?
