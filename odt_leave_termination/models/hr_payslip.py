from odoo import api, fields, models, _
from datetime import date
from odoo.exceptions import UserError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    paid_annual_leave = fields.Boolean(
        string=' paid annual leave', readonly=True)

    # def _onchange_employee(self):
    #     res = super(HrPayslip, self)._onchange_employee()
    #     self.get_employee_time_off()
    #
    #     return res

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def get_employee_time_off(self):
        leave_obj = self.env['hr.leave']
        payroll_pays_recs = leave_obj.search([('state', '=', 'validate'),
                                              ('employee_id', '=', self.employee_id.id),
                                              ('is_reconciled', '=', True), '|', '|',
                                              '&',
                                              ('request_date_from', '>=', self.date_from),
                                              ('request_date_from', '<=', self.date_to),
                                              '&',
                                              ('request_date_from', '<=', self.date_from),
                                              ('request_date_to', '>=', self.date_to),
                                              '&',
                                              ('request_date_to', '>=', self.date_from),
                                              ('request_date_to', '<=', self.date_to)])

        if payroll_pays_recs:
            self.write({'paid_annual_leave': True})
