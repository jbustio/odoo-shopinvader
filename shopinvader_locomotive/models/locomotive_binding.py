# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from openerp import api, models
from openerp.addons.connector.queue.job import job
from openerp.addons.connector.session import ConnectorSession


class LocomotiveBinding(models.AbstractModel):
    _name = "locomotive.binding"
    # Your model must also have _inherit = 'shopinvader.binding'

    @api.multi
    def export_record(self, _fields=None):
        self.ensure_one()
        with self.backend_id.work_on(self._name) as work:
            exporter = work.component(usage="record.exporter")
            return exporter.run(self)

    @api.model
    def export_delete_record(self, backend, external_id):
        with backend.work_on(self._name) as work:
            deleter = work.component(usage="record.exporter.deleter")
            return deleter.run(external_id)

    @api.multi
    def _jobify_export_record(self, _fields):
        session = ConnectorSession.from_env(self.env)
        return shopinvader_do_export_record.delay(
            session, self._name, self.ids, _fields
        )

    @api.multi
    def _jobify_export_delete_record(self, external_id):
        session = ConnectorSession.from_env(self.env)
        return shopinvader_do_export_delete_record.delay(
            session, self._name, self.id, external_id
        )

    _sql_constraints = [
        (
            "locomotive_uniq",
            "unique(backend_id, external_id)",
            "A binding already exists with the same Locomotive ID.",
        )
    ]


@job(default_channel="root.shopinvader")
def shopinvader_do_export_record(session, model_name, _ids, _fields):
    return session.env[model_name].browse(_ids).export_record(_fields)


@job(default_channel="root.shopinvader")
def shopinvader_do_export_delete_record(session, model_name, _id, external_id):
    record = session.env[model_name].browse(_id)
    return record.export_delete_record(record.backend_id, external_id)
