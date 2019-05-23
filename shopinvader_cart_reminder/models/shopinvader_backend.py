# -*- coding: utf-8 -*-
# Copyright 2019 ACSONE SA/NV (<http://acsone.eu>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from odoo import _, api, exceptions, fields, models


class ShopinvaderBackend(models.Model):
    _inherit = "shopinvader.backend"

    quotation_reminder = fields.Integer(
        string="Quotation reminder (hours)",
        help="Determine after how many hours the customer should receive a "
        "reminder to confirm his sale. Let 0 (or less) to disable the "
        "feature.",
        default=0,
    )
    quotation_reminder_mail_template_id = fields.Many2one(
        comodel_name="mail.template",
        string="Quotation reminder e-mail template",
    )

    @api.multi
    @api.constrains(
        "quotation_reminder_mail_template_id", "quotation_reminder"
    )
    def _constrains_quotation_reminder(self):
        """
        Constrain function to ensure that the email template is filled
        if the quotation reminder is > 0
        :return:
        """
        bad_records = self.filtered(
            lambda r: r.quotation_reminder > 0
            and not r.quotation_reminder_mail_template_id
        )
        if bad_records:
            details = "\n- ".join(bad_records.mapped("display_name"))
            message = (
                _(
                    "Please define an email template to send reminder for "
                    "these backends:\n- %s"
                )
                % details
            )
            raise exceptions.ValidationError(message)
