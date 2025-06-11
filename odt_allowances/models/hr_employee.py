from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    allowance_manager_id = fields.Many2one('res.users', string='Allowance', groups="hr.group_hr_user")