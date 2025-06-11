# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime


class HrSanction(models.Model):
    _name = 'hr.penal.sanction'
    _rec_name = 'employee_id'
    _description = 'New Sanction'

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True)
    emp_id = fields.Char(string="Employee ID", related='employee_id.employee_id', required=False, )
    department_id = fields.Many2one(comodel_name="hr.department", string="Department",
                                    related='employee_id.department_id')
    date = fields.Date(string="Date", required=True)
    reason = fields.Text(string="Reason", required=False)
    amount = fields.Float(string="Amount", required=False, )
    days = fields.Float(string="Days", required=False, )
    type = fields.Selection([('amount', _('Amount')),
                             ('days', _('Days')),
                             ('both', _('Both')),
                             ], _('Type'), default='amount',
                            help=_("Gives the Sanction"))
    state = fields.Selection([('draft', _('Draft')),
                              ('cancel', _('Cancelled')),
                              ('submit', _('Submit')),
                              ('confirm', _('Approved'))
                              ], _('Status'), default='draft',
                             help=_("Gives the status"))

    # @api.multi
    def button_submit(self):
        for employee in self:
            contract = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('date_start', '<=', self.date), '|',
                 ('date_end', '>=', self.date), ('date_end', '=', False)])
            for record in contract:
                record.write({'on_sanction': True})
        self.state = 'submit'

    # @api.multi
    def button_confirm(self):
        contract = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('date_start', '<=', self.date), '|',
             ('date_end', '>=', self.date), ('date_end', '=', False)])
        for record in contract:
            record.write({'on_sanction': False})
        self.state = 'confirm'

    # @api.multi
    def button_cancel(self):
        contract = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('date_start', '<=', self.date), '|',
             ('date_end', '>=', self.date), ('date_end', '=', False)])
        for record in contract:
            record.write({'on_sanction': False})
        self.state = 'cancel'
