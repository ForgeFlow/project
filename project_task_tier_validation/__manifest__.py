# Copyright 2025 ForgeFlow S.L.
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
{
    "name": "Project Tier Validation",
    "summary": "Extends the functionality of Projects to "
    "support a tier validation process.",
    "version": "18.0.1.0.0",
    "category": "Projects",
    "website": "https://github.com/OCA/project",
    "author": "ForgeFlow, Odoo Community Association (OCA)",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["project", "base_tier_validation"],
    "data": ["views/project_task_view.xml"],
}
