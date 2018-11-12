# -*- coding: utf-8 -*-
# Copyright 2018 Akretion (http://www.akretion.com).
# Copyright 2018 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import urlparse
from odoo import api, fields, models


class ShopinvaderBackend(models.Model):
    _inherit = 'shopinvader.backend'

    image_proxy_url = fields.Char(
        help="Replace the original url (base part) by this proxy url during "
             "export of images serialized field.\n"
             "Fill without specify the protocol and anything else than the "
             "complete website name (with subdomain if any).\n"
             "Example: my.website.com",
    )

    @api.multi
    def _replace_by_proxy(self, url):
        """
        This function is used to replace the website (into url parameter)
        by the one set on the current recordset (image_proxy_url field).
        Example:
        url = "http://subdomain.example.com/shopinvader?a=awesome"
        self.image_proxy_url = "anonymous.shopinvader.com"
        Expected result:
        "http://anonymous.shopinvader.com/shopinvader?a=myself"
        So we have to keep the protocol (http, https,...) and every arguments
        of the url (who is after the website name)
        :param url: str
        :return: str
        """
        self.ensure_one()
        if self.image_proxy_url and url:
            # We try to find the full website name
            # Example:
            # Expected result: http://subdomain.example.com
            website = urlparse.urlsplit(url).netloc
            if website:
                return url.replace(website, self.image_proxy_url, 1)
        return url
