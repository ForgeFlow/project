This module adds a planned start and a planned end date to tasks.

They are plain, stored dates that planning views (timeline, Gantt, calendar) and
schedulers can share: a module that shows the tasks on a time scale reads them,
a module that plans the tasks writes them. The module itself has no view of
its own and no planning logic, so that any of these modules can depend on it.

- *Planned Dates* in the task form (a date range) and optional columns in the
  task list.
- Filters *Planned*, *Not Planned* and *Planned Start*, and a group by planned
  start (week), in the task search.
- Without a planned end, it is computed from the planned start and the
  allocated time, on the working hours of the task's company. An end set by a
  user or by another module is never overwritten.
