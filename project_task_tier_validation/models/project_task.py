# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class ProjectTask(models.Model):
    _name = "project.task"
    _inherit = ["project.task", "tier.validation"]
    _state_from = ["01_in_progress", "02_changes_requested", "04_waiting_normal"]
    _state_to = ["approved", "1_done", "1_canceled"]
    _tier_validation_manual_config = False
