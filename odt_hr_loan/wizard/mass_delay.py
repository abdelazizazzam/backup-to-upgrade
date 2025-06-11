# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime


def get_next_month_wiz(date):
    try:
        return date.replace(date.year, date.month + 1, 1)
    except ValueError:
        if date.month == 12:
            return date.replace(date.year + 1, 1, 1)


class PrintPayslip(models.TransientModel):
    _name = 'mass.delay.loan'

    months_delay = fields.Integer('No of Months Delay', default=0)
    loan_ids = fields.Many2many(comodel_name="hr.loan", string="Loans")

    def mass_delay(self):
        if self.months_delay < 1:
            raise UserError(_('Please enter number of months to delay'))
        else:
            if self.loan_ids:
                print(self.loan_ids)
                for loan in self.loan_ids:
                    for loan_slip in loan:
                        lines = loan_slip.loan_line_ids.filtered(
                            lambda pay: pay.paid == False)
                        if lines:
                            start_date = lines[0].discount_date
                            date = datetime.strptime(str(start_date), '%Y-%m-%d')
                            for i in range(0, self.months_delay):
                                date = get_next_month_wiz(date)
                            for line in lines:
                                line.write({'discount_date': date})
                                date = get_next_month_wiz(date)
                    loan.no_of_delay = 0
                return True
            else:
                raise UserError(_('Please select the loans you want to delay'))

