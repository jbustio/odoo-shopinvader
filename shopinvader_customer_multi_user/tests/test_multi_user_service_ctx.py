# Copyright 2020 Camptocamp SA
# Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.addons.shopinvader.controllers.main import InvaderController
from odoo.addons.website.tools import MockRequest

from .common import TestMultiUserCommon


class TestMultiUserServiceCtx(TestMultiUserCommon):
    """Test interaction with service component context.
    """

    # TODO: would be nice to have this in core module (or base_rest)
    # to allow full testing of the service stack w/out using HttpTestCase
    def _get_mocked_request(self, partner):
        mocked_request = MockRequest(self.env)
        mocked_request.request["httprequest"]["environ"][
            "HTTP_PARTNER_EMAIL"
        ] = partner.email
        mocked_request.request[
            "auth_api_key_id"
        ] = self.backend.auth_api_key_id.id
        return mocked_request

    def test_cart_assignment_default_multi_disabled(self):
        ctrl = InvaderController()
        with self._get_mocked_request(self.company):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.company)
        self.assertEqual(ctx["partner"], self.company)

        with self._get_mocked_request(self.invader_user.record_id):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.invader_user.record_id)
        self.assertEqual(ctx["partner"], self.invader_user.record_id)

    def test_cart_assignment_default_multi_enabled(self):
        self.backend.customer_multi_user = True
        ctrl = InvaderController()
        with self._get_mocked_request(self.company):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.company)
        self.assertEqual(ctx["partner"], self.company)

        with self._get_mocked_request(self.invader_user.record_id):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.invader_user.record_id)
        self.assertEqual(
            ctx["partner"], self.invader_user.main_partner_id.record_id
        )

    def test_cart_assignment_default_multi_enabled_user_partner(self):
        self.backend.customer_multi_user = True
        self.backend.multi_user_profile_policy = "user_partner"
        ctrl = InvaderController()
        with self._get_mocked_request(self.company):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.company)
        self.assertEqual(ctx["partner"], self.company)

        with self._get_mocked_request(self.invader_user.record_id):
            ctx = ctrl._get_component_context()
        self.assertEqual(ctx["partner_user"], self.invader_user.record_id)
        self.assertEqual(ctx["partner"], self.invader_user.record_id)
