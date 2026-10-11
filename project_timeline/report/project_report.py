# Copyright 2024 Tecnativa - Carlos López
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models
from odoo.tools import SQL


class ReportProjectTaskUser(models.Model):
    _inherit = "report.project.task.user"

    date_planned_start = fields.Datetime(readonly=True)
    date_planned_end = fields.Datetime(readonly=True)

    def _select(self):
        return SQL("%s, t.date_planned_start, t.date_planned_end", super()._select())

    def _group_by(self):
        return SQL("%s, t.date_planned_start, t.date_planned_end", super()._group_by())
