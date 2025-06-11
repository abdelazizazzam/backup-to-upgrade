from odoo import api, fields, models


class Partner(models.Model):
    _inherit = 'hr.employee'

    dependent_ids = fields.One2many("dependent", "related_employee_id", string="Dependents")
    policy_id = fields.Many2one(comodel_name="insurance.policy", string='Policy Number', groups="hr.group_hr_user")
    policy_status = fields.Boolean(string="Policy Status", default=False, groups="hr.group_hr_user")
    has_insurance = fields.Boolean('Has Insurance', copy=False, groups="hr.group_hr_user")
    last_add_insurance = fields.Date('Last Add Insurance Date', groups="hr.group_hr_user")
    last_delete_insurance = fields.Date('Last Delete Insurance Date', groups="hr.group_hr_user")
    last_medical_insurance_id = fields.Many2one('insurance.categ', groups="hr.group_hr_user")