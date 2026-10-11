# Copyright 2026 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tools.sql import column_exists


def migrate(cr, version):
    """Move the planned dates of the timeline to the date_planned_* columns of
    project_task_planned_date (installed before this module)."""
    if not column_exists(cr, "project_task", "planned_date_start"):
        return
    cr.execute(
        "ALTER TABLE project_task "
        "ADD COLUMN IF NOT EXISTS date_planned_start timestamp, "
        "ADD COLUMN IF NOT EXISTS date_planned_end timestamp"
    )
    cr.execute(
        """
        UPDATE project_task
        SET date_planned_start = planned_date_start
        WHERE date_planned_start IS NULL
        AND planned_date_start IS NOT NULL
        """
    )
    cr.execute(
        """
        UPDATE project_task
        SET date_planned_end = planned_date_end
        WHERE date_planned_end IS NULL
        AND planned_date_end IS NOT NULL
        """
    )
