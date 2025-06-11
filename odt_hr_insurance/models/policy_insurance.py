from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime


class Insurance_policy(models.Model):
    _name = 'insurance.policy'
    _rec_name = 'policy_number'
    _description = 'Insurance Policy'
    _order = 'policy_end_date desc'

    insurance_pricing_ids = fields.Many2many(comodel_name="insurance.pricing", string="Insurance Pricing",
                                             required=True)
    policy_number = fields.Char(string="Policy Number", required=True, )
    policy_start_date = fields.Date(string="Policy Start Date", required=True, default=fields.Date.context_today)
    policy_end_date = fields.Date(string="Policy End Date", required=True)
    state = fields.Selection(string="State", selection=[('draft', 'Draft'), ('active', 'Active'), ('cancel', 'Cancel')],
                             default='draft', copy=False, readonly=True)

    @api.constrains('policy_start_date', 'policy_end_date')
    def max_addition_date(self):
        if self.policy_start_date > self.policy_end_date:
            raise ValidationError('Policy start date must be less than policy end date  !')

    def action_confirm(self):
        employees = self.env['hr.employee'].search([('has_insurance', '=', True)])
        if employees:
            for employee in employees:
                if employee.dependent_ids:
                    self.env['insurance.add.delete'].create({
                        'emp_id': employee.id,
                        'request_type': 'add',
                        'is_dependent': True,
                        'request_date': self.policy_start_date,
                        'insurance_policy': self.id,
                        'dependent_ids': [(4, x.id) for x in employee.dependent_ids]
                    })
                else:
                    self.env['insurance.add.delete'].create({
                        'emp_id': employee.id,
                        'request_date': self.policy_start_date,
                        'request_type': 'add',
                        'is_dependent': True,
                        'insurance_policy': self.id,
                    })

        self.write({'state': 'active'})

    def action_cancel(self):
        self.write({'state': 'draft'})
