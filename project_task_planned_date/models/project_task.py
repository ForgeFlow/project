# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from datetime import UTC, timedelta

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools.sql import column_exists, create_column

# Context key set by the modules that feed the planned dates (a scheduler,
# an import): other modules can tell a fed value from a manual change.
PLANNED_DATE_FEED_KEY = "project_task_planned_date_feed"


class ProjectTask(models.Model):
    _inherit = "project.task"

    planned_date_start = fields.Datetime(
        string="Planned Start",
        copy=False,
        index=True,
        help="When the work on the task is planned to start.",
    )
    planned_date_end = fields.Datetime(
        string="Planned End",
        compute="_compute_planned_date_end",
        store=True,
        readonly=False,
        precompute=True,
        copy=False,
        index=True,
        help="When the work on the task is planned to end. Without a value, it "
        "is computed from the planned start and the allocated time, on the "
        "working hours of the company.",
    )

    def _auto_init(self):
        # Create the columns empty on install: no computation over the
        # existing tasks, and the values of a database that already has them
        # (e.g. from another module) are kept.
        cr = self.env.cr
        for column in ("planned_date_start", "planned_date_end"):
            if not column_exists(cr, self._table, column):
                create_column(cr, self._table, column, "timestamp")
        return super()._auto_init()

    @api.depends("planned_date_start", "allocated_hours")
    def _compute_planned_date_end(self):
        """Default end: the planned start plus the allocated time. Only fills
        an empty end, so a value set by a user or another module is kept."""
        for task in self:
            if task.planned_date_end or not task.planned_date_start:
                continue
            end = task._get_planned_date_end_default()
            if end:
                task.planned_date_end = end

    def _get_planned_date_calendar(self):
        """Working hours used to turn the allocated time into an end date.
        Hook: e.g. the calendar of the assignee or of a team."""
        self.ensure_one()
        return (self.company_id or self.env.company).resource_calendar_id

    def _get_planned_date_end_default(self):
        """End date for the planned start and the allocated time, or False.
        Hook for another rule (fixed duration, a duration field...)."""
        self.ensure_one()
        hours = self.allocated_hours
        if not self.planned_date_start or not hours or hours <= 0:
            return False
        start = self.planned_date_start.replace(tzinfo=UTC)
        calendar = self._get_planned_date_calendar()
        end = calendar and calendar.plan_hours(hours, start)
        if not end:
            end = start + timedelta(hours=hours)
        return end.astimezone(UTC).replace(tzinfo=None)

    @api.constrains("planned_date_start", "planned_date_end")
    def _check_planned_dates(self):
        for task in self:
            if (
                task.planned_date_start
                and task.planned_date_end
                and task.planned_date_end < task.planned_date_start
            ):
                raise ValidationError(
                    self.env._(
                        "The planned end of task “%s” cannot be before its "
                        "planned start.",
                        task.display_name,
                    )
                )

    # ------------------------------------------------------------------
    # Feeding the dates from another module
    # ------------------------------------------------------------------

    def _write_planned_dates(self, vals):
        """Write planned dates computed by a module (a scheduler, an
        import) rather than typed by a user. The values are written with
        the feed context key, so that other modules can tell them apart
        (see ``_is_planned_date_feed``)."""
        return self.with_context(**{PLANNED_DATE_FEED_KEY: True}).write(vals)

    def _is_planned_date_feed(self):
        """True while the planned dates are being fed by a module."""
        return bool(self.env.context.get(PLANNED_DATE_FEED_KEY))
