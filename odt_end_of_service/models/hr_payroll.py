# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from odoo.exceptions import UserError

from datetime import datetime, timedelta


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


    @api.model
    def create(self, values):
        res = super(HrPayslip, self).create(values)
        if res.date_from and res.contract_id and res.contract_id.is_paid_payslip and res.date_to:
            if res.date_from <= res.date_to:
                raise UserError(_('You Can not Create Payslip , This Employee %s Is Terminated') % (res.employee_id.name))
        return res

    def write(self, values):
        res = super(HrPayslip, self).write(values)
        for record in self:
            if record.date_from and record.contract_id and record.contract_id.is_paid_payslip and record.date_to:
                if record.date_from <= record.date_to:
                    raise UserError(
                        _('You Can not Create Payslip , This Employee %s Is Terminated') % (record.employee_id.name))
        return res