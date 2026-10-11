# Copyright 2017 Tecnativa - Carlos Dauden
# Copyright 2021 Open Source Integrators - Daniel Reis
# Copyright 2016-2024 Tecnativa - Pedro M. Baeza
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProjectTask(models.Model):
    _inherit = "project.task"

    # The fields, their constraint and their UI come from
    # project_task_planned_date; the timeline fills them from the assignation
    # and the done dates.
    planned_date_start = fields.Datetime(
        compute="_compute_planned_date_start",
        store=True,
        readonly=False,
        precompute=True,
    )

    @api.depends("date_assign")
    def _compute_planned_date_start(self):
        """Put the assignation date as the planned start if not other value is
        previously set, avoiding to trigger the constraint.
        """
        for record in self.filtered(
            lambda x: not x.planned_date_start and x.date_assign
        ):
            if (
                not record.planned_date_end
                or record.planned_date_end >= record.date_assign
            ):
                record.planned_date_start = record.date_assign

    @api.depends("date_end")
    def _compute_planned_date_end(self):
        """Put the done date as the planned end if not other value is previously set,
        avoiding to trigger the constraint. Without a done date, the default end
        of project_task_planned_date applies (planned start plus allocated time).
        """
        for record in self.filtered(lambda x: not x.planned_date_end and x.date_end):
            if (
                not record.planned_date_start
                or record.planned_date_start <= record.date_end
            ):
                record.planned_date_end = record.date_end
        return super()._compute_planned_date_end()
