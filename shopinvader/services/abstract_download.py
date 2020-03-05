# -*- coding: utf-8 -*-
# Copyright 2020 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
import mimetypes

from odoo import _
from odoo.addons.base_rest.components.service import (
    skip_secure_response,
    to_int,
)
from odoo.addons.component.core import AbstractComponent
from odoo.exceptions import MissingError
from odoo.http import content_disposition, request


class AbstractDownload(AbstractComponent):
    """
    Class used to define behaviour to generate and download a document.
    You only have to inherit this AbstractComponent and implement the function
    _get_report_action(...).

    Example for invoice service:
    Class InvoiceService(Component):
        _inherit = [
            "base.shopinvader.service",
            "abstract.shopinvader.download",
        ]
        _name = "shopinvader.invoice.service"

        def _get_report_action(self, target):
            return target.invoice_print()
    """

    _name = "abstract.shopinvader.download"

    # This function should be overwritten
    def _get_report_action(self, target):
        """
        Get the action/dict to generate the report
        :param target: recordset
        :return: dict/action
        """
        raise NotImplementedError()

    def _validator_download(self):
        return {"id": {"type": "integer", "required": True, "coerce": to_int}}

    @skip_secure_response
    def download(self, _id, **params):
        """
        Get target file. This method is also callable by HTTP GET
        """
        target = self._get(_id)
        headers, content = self._get_binary_content(target)
        if not content:
            raise MissingError(_("No content found for %s") % _id)
        response = request.make_response(content, headers)
        response.status_code = 200
        return response

    def _get_binary_content(self, target):
        """
        Generate the report for the given target
        :param target:
          :returns: (headers, content)
        """
        # ensure the report is generated
        target_report_def = self._get_report_action(target)
        report_name = target_report_def.get("report_name")
        report_type = target_report_def.get("report_type")
        content, file_format = self.env["ir.actions.report.xml"].render_report(
            res_ids=target.ids,
            name=report_name,
            data={"report_type": report_type},
        )
        report = self._get_report(report_name, report_type)
        filename = self._get_binary_content_filename(
            target, report, file_format
        )
        mimetype = mimetypes.guess_type(filename)
        if mimetype:
            mimetype = mimetype[0]
        headers = [
            ("Content-Type", mimetype),
            ("X-Content-Type-Options", "nosniff"),
            ("Content-Disposition", content_disposition(filename)),
            ("Content-Length", len(content)),
        ]
        return headers, content

    def _get_report(self, report_name, report_type):
        """
        Load the report recordset
        :param report_name: str
        :param report_type: str
        :return: ir.actions.report.xml recordset
        """
        domain = [
            ("report_type", "=", report_type),
            ("report_name", "=", report_name),
        ]
        return self.env["ir.actions.report.xml"].search(domain, limit=1)

    def _get_binary_content_filename(self, target, report, format):
        """
        Build the filename
        :param target: recordset
        :param report: ir.actions.report.xml recordset
        :param format: str
        :return: str
        """
        return "{}.{}".format(report.name, format)
