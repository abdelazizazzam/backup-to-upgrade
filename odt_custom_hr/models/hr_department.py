# -*- coding: utf-8 -*-

from odoo import api, fields, models, _, exceptions

class HrDepartment(models.Model):
    _inherit = 'hr.department'

    name = fields.Char(translate=True)
    department_code = fields.Char(string="Department Code")
    default_analytic_account_id = fields.Many2one('account.analytic.account', string='Default Analytic Account')

    @api.constrains('department_code')
    def _check_code_unique(self):
        code_counts = self.search_count([('department_code', '=', self.department_code), ('id', '!=', self.id)])
        if code_counts > 0:
            raise exceptions.ValidationError("Department Code must be unique!")