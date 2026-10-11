# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


def pre_init_hook(env):
    """Fill the empty planned dates of the existing tasks from the assignation
    and the done dates (the columns exist already: project_task_planned_date
    creates them), avoiding a costly computation and the constraint."""
    env.cr.execute(
        """
        UPDATE project_task
        SET planned_date_start = date_assign
        WHERE planned_date_start IS NULL
        AND date_assign IS NOT NULL
        AND COALESCE(planned_date_end, date_assign) >= date_assign
        """
    )
    env.cr.execute(
        """
        UPDATE project_task
        SET planned_date_end = date_end
        WHERE planned_date_end IS NULL
        AND date_end IS NOT NULL
        AND COALESCE(planned_date_start, date_end) <= date_end
        """
    )


def uninstall_hook(env):
    """Remove the timeline view mode from the standard act_window definitions."""
    for xml_id in [
        "project.open_view_project_all",
        "project.open_view_project_all_group_stage",
        "project.action_view_task",
        "project.action_project_task_user_tree",
        "project.project_task_action_from_partner",
        "project.act_project_project_2_project_task_all",
        "project.action_view_all_task",
        "project.action_view_task_overpassed_draft",
        "project.dblc_proj",
    ]:
        record = env.ref(xml_id)
        record.view_mode = record.view_mode.replace(",timeline", "")
