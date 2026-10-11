The fields are `planned_date_start` and `planned_date_end` (`Datetime`, stored,
not copied), the names used by the existing planning modules, so a database
that already has these columns keeps its values when this module is installed:
the module creates the columns only when they do not exist and computes
nothing over the existing tasks.

Hooks of `project.task`:

- `_get_planned_date_calendar()`: the working hours used for the default end
  (the company's by default; e.g. return the assignee's calendar);
- `_get_planned_date_end_default()`: the default end for the planned start, or
  `False` (planned start plus the allocated time by default);
- `_compute_planned_date_end()`: the compute of the planned end, which only fills
  an empty end; override it to change when the end is filled (a module that
  fills it from another date can replace it);
- `_write_planned_dates(vals)` and `_is_planned_date_feed()`: a module that feeds
  the dates (a scheduler, an import) writes them with
  `tasks._write_planned_dates({"planned_date_start": ..., "planned_date_end": ...})`;
  the write runs with the context key `project_task_planned_date_feed`, so that
  other modules (e.g. one that treats a manual change as a constraint) can tell a
  fed value from a change made by a user with `self._is_planned_date_feed()`.

Example: a module that starts tasks when they are assigned, without touching the
default end:

```python
class ProjectTask(models.Model):
    _inherit = "project.task"

    planned_date_start = fields.Datetime(
        compute="_compute_planned_date_start", store=True, readonly=False
    )

    @api.depends("date_assign")
    def _compute_planned_date_start(self):
        for task in self.filtered(lambda t: not t.planned_date_start and t.date_assign):
            task.planned_date_start = task.date_assign
```
