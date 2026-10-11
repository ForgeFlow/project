# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (https://www.gnu.org/licenses/lgpl).

from unittest.mock import patch

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from odoo.addons.base.tests.common import BaseCommon

dt = fields.Datetime.to_datetime


@tagged("post_install", "-at_install")
class TestProjectTaskPlannedDate(BaseCommon):
    _test_user_groups = ("base.group_user", "project.group_project_manager")

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.calendar = (
            cls.env["resource.calendar"]
            .sudo()
            .create(
                {
                    "name": "Standard 40 hours/week",
                    "attendance_ids": [
                        (
                            0,
                            0,
                            {
                                "dayofweek": str(day),
                                "hour_from": 8,
                                "hour_to": 16,
                            },
                        )
                        for day in range(5)
                    ],
                }
            )
        )
        cls.env.company.sudo().write(
            {"resource_calendar_id": cls.calendar.id, "tz": "UTC"}
        )
        cls.project = cls.env["project.project"].create({"name": "Planned"})
        cls.Task = cls.env["project.task"]

    def _task(self, **vals):
        return self.Task.create({"name": "Task", "project_id": self.project.id, **vals})

    def test_no_dates_by_default(self):
        task = self._task(allocated_hours=4)
        self.assertFalse(task.planned_date_start)
        self.assertFalse(task.planned_date_end)

    def test_end_from_allocated_hours_on_working_time(self):
        # Monday 2026-10-05 14:00 + 4 h on an 8-16 calendar: Tuesday 10:00
        task = self._task(
            planned_date_start=dt("2026-10-05 14:00:00"), allocated_hours=4
        )
        self.assertEqual(task.planned_date_end, dt("2026-10-06 10:00:00"))

    def test_end_filled_when_start_set_later(self):
        task = self._task(allocated_hours=2)
        task.planned_date_start = dt("2026-10-05 08:00:00")
        self.assertEqual(task.planned_date_end, dt("2026-10-05 10:00:00"))

    def test_end_without_allocated_time_stays_empty(self):
        task = self._task(planned_date_start=dt("2026-10-05 08:00:00"))
        self.assertFalse(task.planned_date_end)

    def test_given_end_is_kept(self):
        end = dt("2026-10-09 16:00:00")
        task = self._task(
            planned_date_start=dt("2026-10-05 08:00:00"),
            planned_date_end=end,
            allocated_hours=2,
        )
        self.assertEqual(task.planned_date_end, end)
        task.allocated_hours = 6
        self.assertEqual(task.planned_date_end, end)

    def test_end_without_calendar(self):
        self.env.company.sudo().resource_calendar_id = False
        task = self._task(
            planned_date_start=dt("2026-10-03 22:00:00"), allocated_hours=4
        )
        self.assertEqual(task.planned_date_end, dt("2026-10-04 02:00:00"))

    def test_end_before_start_is_refused(self):
        task = self._task(planned_date_start=dt("2026-10-05 08:00:00"))
        with self.assertRaises(ValidationError):
            task.planned_date_end = dt("2026-10-04 08:00:00")

    def test_copy_does_not_keep_dates(self):
        start, end = dt("2026-10-05 08:00:00"), dt("2026-10-05 09:00:00")
        task = self._task(planned_date_start=start, planned_date_end=end)
        copy = task.copy()
        # Other modules may fill the dates of the copy (e.g. from its
        # assignation), never with the dates of the original
        self.assertNotEqual(copy.planned_date_start, start)
        self.assertNotEqual(copy.planned_date_end, end)

    def test_feed_context(self):
        task = self._task()
        self.assertFalse(task._is_planned_date_feed())
        seen = []
        original_write = type(task).write

        def write(records, vals):
            seen.append(records._is_planned_date_feed())
            return original_write(records, vals)

        with patch.object(type(task), "write", write):
            task._write_planned_dates(
                {
                    "planned_date_start": dt("2026-10-05 08:00:00"),
                    "planned_date_end": dt("2026-10-05 12:00:00"),
                }
            )
        self.assertEqual(seen, [True])
        self.assertEqual(task.planned_date_end, dt("2026-10-05 12:00:00"))

    def test_calendar_hook(self):
        task = self._task(allocated_hours=8)
        self.assertEqual(task._get_planned_date_calendar(), self.calendar)
