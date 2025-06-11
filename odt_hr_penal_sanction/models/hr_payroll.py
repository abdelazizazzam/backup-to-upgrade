from odoo import models, fields, api, _
from odoo.exceptions import AccessError
from datetime import datetime, timedelta


class HrPayroll(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def get_inputs(self, contract_ids, date_from, date_to):
        res = super(HrPayroll, self).get_inputs(contract_ids, date_from, date_to)
        amount = 0.0
        if contract_ids:
            for contract in contract_ids:
                sanctions = self.env['hr.penal.sanction'].search(
                    [('employee_id', '=', contract.employee_id.id), ('state', '=', 'confirm'), ('date', '>=', date_from),
                     ('date', '<=', date_to)])
                for san in sanctions:
                    if san.type == 'amount':
                        amount += san.amount
                    elif san.type == 'days':
                        payday = contract.wage / 30
                        paydays = san.days * payday
                        amount += paydays
                    else:
                        pay_day = contract.wage / 30
                        pay_days = san.days * pay_day
                        pay_amount = san.amount
                        amount += (pay_days + pay_amount)

                if amount > 0.0:
                    sanction = {
                        'name': 'Sanction',
                        'code': 'SAN',
                        'amount': amount,
                        'contract_id': contract.id,
                    }
                    res += [sanction]

        return res

    @api.model
    def create(self, values):
        res = super(HrPayroll, self).create(values)
        employee =  values.get('employee_id')
        employee_id = self.env['hr.employee'].browse(employee)
        if employee_id.contract_id:
            if employee_id.contract_id.on_sanction:
                raise AccessError( _('You cannot Create Payroll  Because Employee On Sanction'))
        return res

