The fields are `date_planned_start` and `date_planned_end` (`Datetime`, stored,
not copied). They are not named `planned_date_start` and `planned_date_end`
because the project planning of the Enterprise edition defines a non-stored
`planned_date_start` that writes the deadline of the task. The module creates
the columns only when they do not exist and computes nothing over the existing
tasks, so a database that already has them keeps its values.

Hooks of `project.task`:

- `_get_planned_date_calendar()`: the working hours used for the default end
  (the company's by default; e.g. return the assignee's calendar);
- `_get_planned_date_end_default()`: the default end for the planned start, or
  `False` (planned start plus the allocated time by default);
- `_compute_date_planned_end()`: the compute of the planned end, which only fills
  an empty end; override it to change when the end is filled (a module that
  fills it from another date can replace it);
- `_write_planned_dates(vals)` and `_is_planned_date_feed()`: a module that feeds
  the dates (a scheduler, an import) writes them with
  `tasks._write_planned_dates({"date_planned_start": ..., "date_planned_end": ...})`;
  the write runs with the context key `project_task_planned_date_feed`, so that
  other modules (e.g. one that treats a manual change as a constraint) can tell a
  fed value from a change made by a user with `self._is_planned_date_feed()`.

Example: a module that starts tasks when they are assigned, without touching the
default end:

```python
class ProjectTask(models.Model):
    _inherit = "project.task"

    date_planned_start = fields.Datetime(
        compute="_compute_date_planned_start", store=True, readonly=False
    )

    @api.depends("date_assign")
    def _compute_date_planned_start(self):
        for task in self.filtered(lambda t: not t.date_planned_start and t.date_assign):
            task.date_planned_start = task.date_assign
```
