# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta

class AccountMove(models.Model):
    _inherit = 'account.move'

    termination_leave_id = fields.Many2one('hr.holiday.termination', 'Settlement', help='Settlement Record')


class HolidaysType(models.Model):
    _inherit = "hr.leave.type"
    
    is_annual = fields.Boolean(string="Is Annual")


class Settlement(models.Model):
    _name = 'hr.holiday.termination'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'termination_code'
    _description = 'New Settlement'

    def get_company_domain(self):
        return [('id', 'in', self.env.user.company_ids.ids)]

    termination_code = fields.Char('Settlement NO', readonly=True, states={'draft': [('readonly', False)]},
                                   default='Settlement', tracking=True)
    date = fields.Date('Application Date', readonly=True, states={'draft': [('readonly', False)]},
                       default=fields.Date.today(), tracking=True)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, readonly=False,
                                  states={'draft': [('readonly', False)]}, tracking=True)
    employee_code = fields.Char()  # TODO
    reconcile_date = fields.Date(string="Reconcile Date", required=True)
    reconcile_type = fields.Selection(string="Reconcile Type",
                                      selection=[('request', 'Leave Request'), ('balance', 'Balance'),
                                                 ('both', 'Both'), ], required=True, default='request',
                                      tracking=True)
    balance_days = fields.Float(string="Reconcile Days", required=False, )
    employee_balance_days = fields.Float(string="Current Balance Days", required=False,
                                         compute='_compute_employee_balance_days',
                                         tracking=True, store=True)
    vacation_days = fields.Float('Vacation Days', tracking=True, required=False,
                                 compute='_get_vacation_days')
    vacation_days_comp = fields.Float('vacation days comp', tracking=True, required=False, )
    balance_days_comp = fields.Float('balance days comp', required=False, tracking=True, )
    contract_id = fields.Many2one('hr.contract', 'Contract', required=True, tracking=True,
                                  states={'draft': [('readonly', False)]})
    leave_id = fields.Many2one('hr.leave.type', 'Time Off Types', tracking=True,
                               states={'draft': [('readonly', False)]})
    is_annual = fields.Boolean(string="Is Annual", related='leave_id.is_annual')
    job_id = fields.Many2one('hr.job', 'Job Title', readonly=True, tracking=True,
                             states={'draft': [('readonly', False)]})
    company_id = fields.Many2one('res.company', 'Company', tracking=True,
                                 related='employee_id.company_id')
    approved_by = fields.Many2one('res.users', 'Approved By', tracking=True,
                                  default=lambda self: self.env.user, readonly=True,
                                  states={'draft': [('readonly', False)]})
    approval_date = fields.Date('Approval Date', readonly=True, tracking=True,
                                states={'draft': [('readonly', False)]})
    settlements_days = fields.Float('Settlements Days', readonly=True, tracking=True,
                                    states={'draft': [('readonly', False)]},
                                    compute='_onchange_contract_id')
    deduction_value = fields.Float(string="Deduction Value", required=False, )
    addition_value = fields.Float(string="Addition Value", required=False, )
    salary_amount = fields.Float('Salary Amount', readonly=True, tracking=True,
                                 states={'draft': [('readonly', False)]},
                                 compute='_onchange_contract_id')
    leave_amount = fields.Float(string="Leave Amount", required=False, tracking=True,
                                compute='_onchange_contract_id')
    ticket_amount = fields.Float(string="Ticket Amount", required=False, tracking=True, )
    current_salary_amount = fields.Float(string="Current Salary Amount", required=False, compute="_compute_current_salary", tracking=True, )
    total_amount = fields.Float(string="Total Amount", required=False, tracking=True,
                                compute='_compute_total_amount')
    move_id = fields.Many2one('account.move', 'Journal Entry', tracking=True,
                              help='Journal Entry for Settlement')
    leave_reconcile_id = fields.Many2one('hr.leave.allocation', 'Leave Reconcile', tracking=True, )
    payment_method = fields.Many2one('termination.leave.payments', 'Payment Method', tracking=True,
                                     help='payment method for Settlement')
    journal_id = fields.Many2one('account.journal', 'Journal', tracking=True,
                                 help='Journal for journal entry', domain=[('type', 'in', ['cash', 'bank'])])
    notes = fields.Text(string="Notes", required=False, tracking=True, )
    emp_member = fields.Integer(string="Family Member", tracking=True, readonly=True,
                                states={'draft': [('readonly', False)]})
    emp_city = fields.Char(string="Employee City", tracking=True, readonly=True,
                           states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', _('Draft')),
                              ('review', _('Review')),
                              ('cancel', _('Cancelled')),
                              ('approved', _('First Approve')),
                              ('approved2', _('Second Approve'))
                              ], _('Status'), readonly=True, copy=False, default='draft',
                             help=_("Gives the status of the Settlement"), select=True)

    def action_draft(self):
        self.state = 'draft'

    @api.onchange('reconcile_date')
    def _compute_current_salary(self):
        for sett in self:
            if not sett.reconcile_date:
                sett.current_salary_amount = 0.0

            payslip_obj = self.env["hr.payslip"].search(
                [
                    ('employee_id', '=', sett.employee_id.id),
                    ('date_from', '<=', sett.reconcile_date),
                    ('date_to', '>=', sett.reconcile_date),
                    ('state', '=', 'done'),
                ]
            )

            payslip_lines = payslip_obj.line_ids
            print(payslip_obj)
            if payslip_lines:
                net_salary_line = payslip_lines.filtered(lambda x: x.category_id.code == 'NET')
                sett.current_salary_amount = net_salary_line.total
            else:
                sett.current_salary_amount = 0.0


    @api.constrains('balance_days')
    def check_error(self):
        if self.balance_days > self.employee_balance_days:
            print(self.balance_days)
            print(self.employee_balance_days)
            raise UserError(_('Reconcile Days can not be above Current Balance Days.'))

    @api.model
    def create(self, values):
        res = super(Settlement, self).create(values)
        settlements = self.search([('employee_id', '=', res.employee_id.id)]).filtered(
            lambda Settl: Settl.state != 'cancel')
        for Sett in settlements:
            if Sett.id != res.id:
                if Sett.reconcile_date >= res.reconcile_date:
                    raise UserError(_('You Can not reconcile more for same Time.'))

        settlements_employee = self.search(
            [('employee_id', '=', res.employee_id.id), ('state', 'in', ['draft', 'approved'])])
        for leave in settlements_employee:
            if leave.id != res.id:
                raise UserError(_('There is other settlement for the same employee.'))
        return res

    def write(self, values):
        res = super(Settlement, self).write(values)
        settlements = self.search([('employee_id', '=', self.employee_id.id)]).filtered(
            lambda Settl: Settl.state != 'cancel')
        for Sett in settlements:
            if Sett.id != self.id:
                if Sett.reconcile_date >= self.reconcile_date:
                    raise UserError(_('You Can not reconcile more for same Time.'))
        return res

    @api.depends('leave_id')
    def _compute_employee_balance_days(self):
        for rec in self:
            rec.employee_balance_days = rec.employee_id.remaining_leaves

    @api.depends('leave_amount', 'ticket_amount', 'deduction_value', 'addition_value')
    def _compute_total_amount(self):
        for record in self:
            record.total_amount = record.leave_amount + record.ticket_amount - record.deduction_value + record.addition_value + record.current_salary_amount

    def button_review(self):
        self.write({'state': 'review'})

    def button_approve(self):
        termination_code = self.env['ir.sequence'].get('hr.termination.leave.code')
        self.write({'termination_code': termination_code, 'state': 'approved'})

    def validate_termination(self):
        self.ensure_one()
        leave_type = self.env["hr.leave.type"].search([("is_annual", '=', True)])
        self.leave_id = leave_type.id
        if self.reconcile_type in ['balance', 'both'] and self.balance_days:
            # leave_type = self.employee_id.holiday_line_ids.mapped('leave_status_id').ids[0]
            vals = {
                'name': 'Reconcile Balance Days',
                'employee_id': self.employee_id.id,
                'holiday_status_id': self.leave_id.id,
                # 'last_allocation_date': self.reconcile_date,
                # 'date_change': True,
                'number_of_days': self.balance_days * -1,
            }
            leave = self.env['hr.leave.allocation'].create(vals)
            leave.action_confirm()
            leave.action_validate()
            if leave.validation_type == 'both':
                leave.action_validate()
            self.write({'leave_reconcile_id': leave.id})

        # leave_type = self.employee_id.holiday_line_ids.mapped('leave_status_id').ids
        domain = [('holiday_status_id', '=', self.leave_id.id), ('state', '=', 'validate'),
                  ('request_date_from', '<=', self.reconcile_date),
                  ('reconcile_option', '=', 'yes'),
                  ('is_reconciled', '=', False),
                  ('employee_id', '=', self.employee_id.id)]
        leaves = self.env['hr.leave'].search(domain)
        for leave in leaves:
            # self._create_work_entries(leave)
            leave.is_reconciled = True
            
        move_obj = self.env['account.move']
        timenow = time.strftime('%Y-%m-%d')
        line_ids = []
        name = _('Settlement for ') + self.employee_id.name
        move = {
            'narration': name,
            'ref': self.termination_code,
            'date': self.approval_date or timenow,
            'termination_leave_id': self.id,
            'journal_id': self.journal_id.id,
        }

        leave_amount = self.leave_amount
        ticket_amount = self.ticket_amount
        current_salary = self.current_salary_amount
        ded_amount = self.deduction_value
        add_amount = self.addition_value
        ticket_debit_account_id = self.payment_method.ticket_debit_account_id.id or False
        ticket_credit_account_id = self.payment_method.ticket_credit_account_id.id or False
        leave_debit_account_id = self.payment_method.leave_debit_account_id.id or False
        leave_credit_account_id = self.payment_method.leave_credit_account_id.id or False
        current_debit_account_id = self.payment_method.current_debit_account_id.id or False
        current_credit_account_id = self.payment_method.current_credit_account_id.id or False
        ded_debit_account_id =  self.payment_method.ded_debit_account_id.id or False
        ded_credit_account_id = self.payment_method.ded_credit_account_id.id or False
        add_debit_account_id = self.payment_method.add_debit_account_id.id or False
        add_credit_account_id = self.payment_method.add_credit_account_id.id or False

        if not self.journal_id:
            raise UserError(_('Please Set Journal'))

        if not self.employee_id.private_street:
            raise UserError(_('Please Set Related Partner For Employee'))

        partner_id = False
        if self.employee_id.private_street:
            partner_id = self.employee_id.private_street


        if add_amount:
            if not add_debit_account_id or not add_credit_account_id:
                raise UserError(_('Please Set Leave credit/debit account '))
            if add_debit_account_id:
                debit_line = (0, 0, {
                    'name': 'Leaves',
                    'date': self.approval_date or timenow,
                    'partner_id': partner_id,
                    'account_id': add_debit_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': add_amount,
                    'credit': 0.0,
                })
                line_ids.append(debit_line)

            if add_credit_account_id:
                credit_line = (0, 0, {
                    'name': 'Leaves',
                    'date': self.approval_date or timenow,
                    'partner_id': partner_id,
                    'account_id': add_credit_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': 0.0,
                    'credit': add_amount,
                })
                line_ids.append(credit_line)

        if ded_amount:
            if not ded_debit_account_id or not ded_credit_account_id:
                raise UserError(_('Please Set Leave credit/debit account '))
            if ded_debit_account_id:
                debit_line = (0, 0, {
                    'name': 'Leaves',
                    'date': self.approval_date or timenow,
                    'partner_id': partner_id,
                    'account_id': ded_debit_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': ded_amount,
                    'credit': 0.0,
                })
                line_ids.append(debit_line)

            if ded_credit_account_id:
                credit_line = (0, 0, {
                    'name': 'Leaves',
                    'date': self.approval_date or timenow,
                    'partner_id': partner_id,
                    'account_id': ded_credit_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': 0.0,
                    'credit': ded_amount,
                })
                line_ids.append(credit_line)
        

        if current_salary:
            if not current_credit_account_id or not current_debit_account_id:
                raise UserError(_('Please Set Leave credit/debit account '))
            if current_debit_account_id:
                debit_line = (0, 0, {
                    'name': 'Leaves',
                    'date': self.approval_date or timenow,
                    'partner_id': partner_id,
                    'account_id': current_debit_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': current_salary,
                    'credit': 0.0,
                })
                line_ids.append(debit_line)

            if current_credit_account_id:
                credit_line = (0, 0, {
                    'name': 'Leaves',
                    'date': self.approval_date or timenow,
                    'partner_id': partner_id,
                    'account_id': current_credit_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': 0.0,
                    'credit': current_salary,
                })
                line_ids.append(credit_line)
        
        if leave_amount:
            if not leave_credit_account_id or not leave_debit_account_id:
                raise UserError(_('Please Set Leave credit/debit account '))
            if leave_debit_account_id:
                debit_line = (0, 0, {
                    'name': 'Leaves',
                    'date': self.approval_date or timenow,
                    'partner_id': partner_id,
                    'account_id': leave_debit_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': leave_amount,
                    'credit': 0.0,
                })
                line_ids.append(debit_line)

            if leave_credit_account_id:
                credit_line = (0, 0, {
                    'name': 'Leaves',
                    'date': self.approval_date or timenow,
                    'partner_id': partner_id,
                    'account_id': leave_credit_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': 0.0,
                    'credit': leave_amount,
                })
                line_ids.append(credit_line)
        if ticket_amount:
            if not ticket_debit_account_id or not ticket_credit_account_id:
                raise UserError(_('Please Set Ticket credit/debit account '))
            if ticket_debit_account_id:
                debit_line = (0, 0, {
                    'name': 'Ticket',
                    'date': self.approval_date or timenow,
                    'partner_id': partner_id,
                    'account_id': ticket_debit_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': ticket_amount,
                    'credit': 0.0,
                })
                line_ids.append(debit_line)

            if ticket_credit_account_id:
                credit_line = (0, 0, {
                    'name': 'Ticket',
                    'date': self.approval_date or timenow,
                    'partner_id': partner_id,
                    'account_id': ticket_credit_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': 0.0,
                    'credit': ticket_amount,
                })
                line_ids.append(credit_line)

        move.update({'line_ids': line_ids})
        move_id = move_obj.create(move)

        self.write(
            {'move_id': move_id.id, 'state': 'approved2', })
        # move_id.post()
        return True

    def button_cancel(self):
        leave_type = self.env["hr.leave.type"].search([("is_annual", '=', True)])
        self.leave_id = leave_type.id
        if self.state not in ['approved2']:
            self.state = 'cancel'
        elif self.move_id and self.move_id.state == 'draft':
            # leave_type = self.employee_id.holiday_line_ids.mapped('leave_status_id').ids
            domain = [('holiday_status_id', '=', self.leave_id.id), ('state', '=', 'validate'),
                      ('request_date_from', '<=', self.reconcile_date), ('reconcile_option', '=', 'yes'),
                      ('is_reconciled', '=', True), ('employee_id', '=', self.employee_id.id)]
            leaves = self.env['hr.leave'].search(domain)
            for l in leaves:
                l.is_reconciled = False
            if self.leave_reconcile_id:
                self.leave_reconcile_id.action_refuse()
                self.leave_reconcile_id.action_draft()
                self.leave_reconcile_id.unlink()
            self.move_id.unlink()
            self.state = 'cancel'
        else:
            raise UserError(_('You cannot delete a termination document'
                            ' which is posted Entries!'))

    @api.onchange('reconcile_type', 'reconcile_date', 'employee_id')
    def _compute_vacation_days(self):
        for line in self:
            line.balance_days_comp = self.employee_id.remaining_leaves
            leave_type = self.env["hr.leave.type"].search([("is_annual", '=', True)])
            domain = [('holiday_status_id', '=', leave_type.id), ('state', '=', 'validate'),
                      ('employee_id', '=', line.employee_id.id),
                      ('request_date_from', '<=', line.reconcile_date), ('reconcile_option', '=', 'yes'),
                      ('is_reconciled', '=', False)]
            leave = self.env['hr.leave'].search(domain)
            line.leave_id = leave_type.id
            leave_days = sum([l.number_of_days for l in leave])
            line.vacation_days_comp = leave_days

    @api.onchange('reconcile_type', 'reconcile_date')
    def _get_vacation_days(self):
        for record in self:
            # record.employee_balance_days = record.balance_days_comp
            record.vacation_days = record.vacation_days_comp

    def get_contracts(self):
        contract_obj = self.env['hr.contract']
        contract_ids = []
        for termination in self:
            employee = termination.employee_id
            clause_final = [('employee_id', '=', employee.id), ('state', '=', 'open')]
            contract_ids = contract_obj.search(clause_final)
        return contract_ids

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.contract_id = False
        if self.employee_id:
            vals = {'domain': {'contract_id': False}}
            self.job_id = self.employee_id.job_id.id
            member = 0
            # TODO if self.employee_id.family_member_ids:
            #     member = len(self.employee_id.family_member_ids)
            self.emp_member = member
            contract_ids = self.get_contracts()
            if contract_ids:
                contracts = sorted(contract_ids, key=lambda x: x.date_start, reverse=True)
                self.contract_id = contracts[0].id
            return vals

    @api.onchange('contract_id', 'employee_id', 'payment_method', 'vacation_days', 'balance_days')
    def _onchange_contract_id(self):
        for record in self:
            salary_amount = 0.0
            if record.contract_id and record.payment_method:
                basic = record.contract_id.wage
                for field in record.payment_method.field_ids:
                    if field.name == 'wage':
                        salary_amount += record.contract_id[field.name]
                    elif field.name == 'transportation_allowance':
                        salary_amount += (basic * (
                                record.contract_id.transportation_allowance / 100) if record.contract_id.is_trans else record.contract_id.transportation_allowance)
                    elif field.name == 'housing_allowance':
                        salary_amount += (basic * (
                                record.contract_id.housing_allowance / 100) if record.contract_id.is_house else record.contract_id.housing_allowance)
                    elif field.name == 'mobile_allowance':
                        salary_amount += (basic * (
                                record.contract_id.mobile_allowance / 100) if record.contract_id.is_mobile else record.contract_id.mobile_allowance)
                    elif field.name == 'overtime_allowance':
                        salary_amount += (basic * (
                                record.contract_id.overtime_allowance / 100) if record.contract_id.is_over else record.contract_id.overtime_allowance)
                    elif field.name == 'work_allowance':
                        salary_amount += (basic * (
                                record.contract_id.work_allowance / 100) if record.contract_id.is_work else record.contract_id.work_allowance)
                    elif field.name == 'reward':
                        salary_amount += (basic * (
                                record.contract_id.reward / 100) if record.contract_id.is_reward else record.contract_id.reward)
                    elif field.name == 'fuel_car':
                        salary_amount += (basic * (
                                record.contract_id.fuel_car / 100) if record.contract_id.is_fuel else record.contract_id.fuel_car)
                    elif field.name == 'ticket_allowance':
                        salary_amount += (basic * (
                                record.contract_id.ticket_allowance / 100) if record.contract_id.is_ticket else record.contract_id.ticket_allowance)
                    elif field.name == 'food_allowance':
                        salary_amount += (basic * (
                                record.contract_id.food_allowance / 100) if record.contract_id.is_food else record.contract_id.food_allowance)
                    elif field.name == 'other_allowance':
                        salary_amount += (basic * (
                                record.contract_id.other_allowance / 100) if record.contract_id.is_other else record.contract_id.other_allowance)
                    elif field.name == 'gosi':
                        if record.contract_id.employee_id.country_id.code == 'SA':
                            salary_amount -= record.contract_id.gosi
                    elif field.name == 'allowance':
                        salary_amount += record.contract_id.allowance
                    elif field.name == 'allowance2':
                        salary_amount += record.contract_id.allowance2
                    elif field.name == 'allowance3':
                        salary_amount += record.contract_id.allowance3
                    elif field.name == 'allowance4':
                        salary_amount += record.contract_id.allowance4

                    elif field.name == 'allowance5':
                        salary_amount += record.contract_id.allowance5
                    elif field.name == 'allowance6':
                        salary_amount += record.contract_id.allowance6

                    elif field.name == 'housing_monthly_allowance':
                        salary_amount += record.contract_id.housing_monthly_allowance

                    elif field.name == 'trans_value':
                        salary_amount += record.contract_id.trans_value

                    elif field.name == 'transportation_value':
                        salary_amount += record.contract_id.transportation_value

            record.salary_amount = salary_amount
            remaining_vacation = 0.0
            if record.reconcile_type == 'request':
                remaining_vacation = record.vacation_days
            elif record.reconcile_type == 'balance':
                remaining_vacation = record.balance_days
            elif record.reconcile_type == 'both':
                remaining_vacation = record.balance_days + record.vacation_days
            record.settlements_days = remaining_vacation
            record.leave_amount = (salary_amount / 30) * remaining_vacation

    def unlink(self):
        for termination in self:
            if termination.state not in ['draft', 'review', 'cancel']:
                raise UserError(_('You cannot delete a Settlement document'
                                ' which is not draft or cancelled!'))
        return super(Settlement, self).unlink()

    def open_entries(self):
        self.ensure_one()
        context = dict(self._context or {}, search_default_termination_leave_id=self.ids,
                       default_termination_leave_id=self.ids)
        return {
            'name': _('Journal Entries'),
            'view_type': 'form',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', '=', self.move_id.id)],
            'view_id': False,
            'type': 'ir.actions.act_window',
            'context': context,
        }


class TerminationsPayments(models.Model):
    _name = "termination.leave.payments"

    name = fields.Char('Name', required=True, help='Payment name')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company.id)
    ticket_debit_account_id = fields.Many2one('account.account', 'Ticket Debit Account', required=False,
                                              help='Ticket Debit account for journal entry')
    ticket_credit_account_id = fields.Many2one('account.account', 'Ticket Credit Account', required=False,
                                               help='Ticket Credit account for journal entry')
    leave_debit_account_id = fields.Many2one('account.account', 'Leave Debit Account', required=False,
                                             help='Leave Debit account for journal entry')
    leave_credit_account_id = fields.Many2one('account.account', 'Leave Credit Account', required=False,
                                              help='Leave Credit account for journal entry')

    current_credit_account_id = fields.Many2one('account.account', 'Current Salary Credit Account', required=False,
                                              help='Leave Credit account for journal entry')
    current_debit_account_id = fields.Many2one('account.account', 'Current Salary Debit Account', required=False,
                                              help='Leave Credit account for journal entry')
    ded_credit_account_id = fields.Many2one('account.account', 'Deduction Credit Account', required=False,
                                              help='Leave Credit account for journal entry')
    ded_debit_account_id = fields.Many2one('account.account', 'Deduction Debit Account', required=False,
                                              help='Leave Credit account for journal entry')
    add_debit_account_id = fields.Many2one('account.account', 'Addition Debit Account', required=False,
                                              help='Leave Credit account for journal entry')
    add_credit_account_id = fields.Many2one('account.account', 'Addition Credit Account', required=False,
                                              help='Leave Credit account for journal entry')
    leave_allocate_id = fields.Many2one(comodel_name="hr.leave.allocation", string="Allocation", required=False, )
    field_ids = fields.Many2many(comodel_name="ir.model.fields", relation="leave_field_rel", string="Leave Rules",
                                 domain=[('model_id', '=', 'hr.contract'), ('ttype', 'in', ['float', 'monetary'])])
