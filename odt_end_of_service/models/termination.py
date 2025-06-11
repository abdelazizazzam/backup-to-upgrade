from __future__ import division
from odoo.exceptions import UserError, ValidationError

import time
from datetime import datetime

from odoo import models, fields, api, _
from .. import utils


class AccountMove(models.Model):
    _inherit = 'account.move'

    termination_id = fields.Many2one('hr.termination', 'Termination', help='Termination Record')


class Termination(models.Model):
    _name = 'hr.termination'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _rec_name = 'termination_code'

    def get_contracts(self):
        contract_obj = self.env['hr.contract']
        contract_ids = []
        for termination in self:
            date_to = termination.job_ending_date
            date_from = termination.employee_id.contract_id.date_start
            employee = termination.employee_id
            clause_1 = ['&', ('date_end', '<=', date_to), ('date_end', '>=', date_from)]
            # OR if it starts between the given dates
            clause_2 = ['&', ('date_start', '<=', date_to), ('date_start', '>=', date_from)]
            # OR if it starts before the date_from and finish after the date_end (or never finish)
            clause_3 = ['&', ('date_start', '<=', date_from), '|', ('date_end', '=', False),
                        ('date_end', '>=', date_to)]
            clause_final = [('employee_id', '=', employee.id), ('state', '=', 'open'), '|',
                            '|'] + clause_1 + clause_2 + clause_3
            contract_ids = contract_obj.search(clause_final)
        return contract_ids

    def calculate_vacation(self):
        holiday_obj = self.env['hr.leave']
        holiday_records = holiday_obj.search([('employee_id', '=', self.employee_id.id),
                                              ('state', '=', 'validate')])
        total_leave = 0
        total_leave_taken = 0
        if holiday_records:
            for holiday in holiday_records:
                total_leave_taken += holiday.number_of_days
        if total_leave > total_leave_taken:
            return total_leave - total_leave_taken
        else:
            return 0

    is_paid_payslip = fields.Boolean(string="Payslip Paid", default=False, store=True)
    is_clearance = fields.Boolean(string="Is Clearance", track_visibility='onchange', store=True)
    termination_code = fields.Char('Termination NO', readonly=True, states={'draft': [('readonly', False)]},
                                   default='Termination', track_visibility='onchange')
    date = fields.Date('Application Date', readonly=True, states={'draft': [('readonly', False)]},
                       default=fields.Date.today(), track_visibility='onchange')
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', required=True, readonly=False,
                                  track_visibility='onchange',
                                  states={'draft': [('readonly', False)]})
    # resignation_request_id = fields.Many2one(comodel_name="resignation.request", string="Employee Resignation Request",
    #                                          readonly=True, store=True)
    company_id = fields.Many2one('res.company', 'Company', track_visibility='onchange',
                                 related='employee_id.company_id')
    employee_code = fields.Char(related='employee_id.name')
    contract_id = fields.Many2one('hr.contract', 'Contract', required=True, readonly=False, track_visibility='onchange',
                                  states={'draft': [('readonly', False)]})
    current_salary_amount = fields.Float(string="Current Salary Amount", required=False, tracking=True, )
    job_id = fields.Many2one('hr.job', 'Job Title', readonly=True, track_visibility='onchange',
                             states={'draft': [('readonly', False)]})
    job_ending_date = fields.Date('Job Ending Date', track_visibility='onchange')
    hire_date = fields.Date('Hire Date', readonly=False, track_visibility='onchange',
                            states={'draft': [('readonly', False)]})
    approved_by = fields.Many2one('res.users', 'Approved By', track_visibility='onchange', readonly=True,
                                  states={'draft': [('readonly', False)]})
    approval_date = fields.Date('Approval Date', readonly=True, track_visibility='onchange',
                                states={'draft': [('readonly', False)]},
                                default=fields.Date.today())

    ded_value = fields.Float('Deduction Value', readonly=True, track_visibility='onchange',
                             states={'draft': [('readonly', False)]}, )
    add_value = fields.Float('Addition Value', readonly=True, track_visibility='onchange',
                             states={'draft': [('readonly', False)]}, )
    add_value_housing = fields.Float('In-kind housing allowance', readonly=True, track_visibility='onchange',
                                     states={'draft': [('readonly', False)]}, )
    total_deserve = fields.Float('End Of Service Amount', store=True, track_visibility='onchange',
                                 compute='_calculate_severance', readonly=True,
                                 help="Calculation By Basic Salary + Housing Allowance + Transportation Allowance")
    total_deserve_amount = fields.Float('Total Deserved', track_visibility='onchange',
                                        compute='_compute_total_deserve_amount', readonly=True)
    from_years = fields.Float('From Years', readonly=True, track_visibility='onchange',
                              states={'draft': [('readonly', False)]})
    to_years = fields.Float('To Years', readonly=True, track_visibility='onchange',
                            states={'draft': [('readonly', False)]})
    basic_salary = fields.Float('Total Salary', readonly=True, track_visibility='onchange', store=True,
                                states={'draft': [('readonly', False)]})
    min_months = fields.Float('Min Months', readonly=True, track_visibility='onchange',
                              states={'draft': [('readonly', False)]})
    calc_type = fields.Selection(selection=[('contract', 'Contract Based'),
                                            ('manual', 'Manual')],
                                 readonly=True, track_visibility='onchange', states={'draft': [('readonly', False)]},
                                 string='Period Type',
                                 default='contract', required=True)
    years_val = fields.Float(string='No.Years', track_visibility='onchange', required=True)
    months_val = fields.Float(string='No.Months', track_visibility='onchange', required=True)
    days_val = fields.Float(string='No.Days', track_visibility='onchange', required=True)

    working_period = fields.Float('Working Period', track_visibility='onchange', readonly=True,
                                  states={'draft': [('readonly', False)]})
    period_in_years = fields.Float('Period in Years', track_visibility='onchange', readonly=True,
                                   states={'draft': [('readonly', False)]})
    vacation_days = fields.Float('Vacation Days', track_visibility='onchange', readonly=True,
                                 states={'draft': [('readonly', False)]})
    salary_amount = fields.Float('Salary Amount', track_visibility='onchange', readonly=True,
                                 states={'draft': [('readonly', False)]})
    salary_amount_leave = fields.Float('Salary Amount', track_visibility='onchange', readonly=True,
                                       states={'draft': [('readonly', False)]})
    absence_amount = fields.Float('Absence Days', track_visibility='onchange', readonly=True,
                                  compute='_get_amount_values')
    absence_amount_val = fields.Float('Absence Amount', track_visibility='onchange')
    notice_period_value = fields.Float(string="Notice Period Value", store=True)
    notice_period = fields.Selection(string="Notice Period",
                                     selection=[('1', 'Add Month'), ('2', 'Add 2 Months'), ('3', 'Add 3 Months'),
                                                ('-1', 'Deduct 1 Month'), ('-2', 'Deduct 2 Months'),
                                                ('-3', 'Deduct 3 Months')])
    unpaid_amount = fields.Float('Unpaid Days', readonly=True, track_visibility='onchange',
                                 compute='_get_amount_values')
    unpaid_amount_val = fields.Float('Unpaid Amount', track_visibility='onchange')
    deserve_salary_amount = fields.Float('Leaves Amount', readonly=True, track_visibility='onchange',
                                         states={'draft': [('readonly', False)]},
                                         help="Calculation By (Total Salary - Transportation Allowance)/ 30 ")
    move_id = fields.Many2one('account.move', 'Journal Entry', track_visibility='onchange',
                              help='Journal Entry for Termination')
    payment_method = fields.Many2one(comodel_name='termination.payments', track_visibility='onchange',
                                     string='Payment Method EOS',
                                     help='Payment method for termination')
    payment_method_leave = fields.Many2one(comodel_name='termination.leave.payments', track_visibility='onchange',
                                           string='Payment Method of Leaves',
                                           help='Payment method for termination ')
    journal_id = fields.Many2one('account.journal', 'Journal', track_visibility='onchange',
                                 help='Journal for journal entry')
    notes = fields.Text(string="Notes", required=False, )
    notes_add = fields.Text(string="Notes Additional", required=False, )
    notes_deduction = fields.Text(string="Notes Deduction", required=False, )
    state = fields.Selection([('draft', _('Draft')),
                              ('review', _('Review')),
                              ('cancel', _('Cancelled')),
                              ('approved', _('First Approve')),
                              ('approved2', _('Second Approve'))
                              ], _('Status'), readonly=True, copy=False, default='draft', track_visibility='onchange',
                             help=_("Gives the status of the Termination"), select=True)

    eos_reason = fields.Selection([('1', 'Expiration of the contract'),
                                   ('10', 'Contract termination agreement between the employee and the employer'),
                                   ('11', 'Contract terminated by the employer'),
                                   ('12', 'Employee leaving the work for one of the cases mentioned in Article (81)'),
                                   ('13', 'Employee leaving the work as a result of force majeure'),
                                   ('14',
                                    'Female employee termination of an employment contract within 6 months of the marriage contract'),
                                   ('15',
                                    'Female employee termination of an employment contract within 3 months of the birth giving'),
                                   ('2',
                                    'Contract terminated by the employer for one of the cases mentioned in Article (80)'),
                                   ('20', 'Contract termination by the employee'),
                                   ('21', 'Leaving work for cases other than those mentioned in Article (81)'),
                                   ('77', 'Contract terminated according to Article (77)'),
                                   ('3', 'Employee resignation')], string='EOS Reason', readonly=False,
                                  track_visibility='onchange')

    currency_id = fields.Many2one('res.currency', string='Currency')
    basic_wage = fields.Monetary(string="Basic Salary", related="employee_id.contract_id.wage")
    emp_last_return_date = fields.Date(string="Return Date", readonly=True)

    compensatory_bonus = fields.Float('Additional (compensatory) bonus', store=True,
                                      compute='_calculate_severance', readonly=True)

    # @api.onchange('employee_id')
    # def get_resignation_request(self):
    #     if self.employee_id:
    #         resign_req = self.env['resignation.request'].search(
    #             [('employee_id', '=', self.employee_id.id), ('state', '=', 'approve')], limit=1)
    #         if resign_req:
    #             self.resignation_request_id = resign_req.id
    #     if self.resignation_request_id:
    #         self.job_ending_date = self.resignation_request_id.last_working_date
    #         self.eos_reason = self.resignation_request_id.resignation_type.eos_reason

    @api.onchange('notice_period')
    def _get_notice_period(self):
        for rec in self:
            if rec.notice_period:
                if rec.notice_period == '1':
                    rec.notice_period_value = rec.basic_salary * 1
                if rec.notice_period == '2':
                    rec.notice_period_value = rec.basic_salary * 2
                if rec.notice_period == '3':
                    rec.notice_period_value = rec.basic_salary * 3
                if rec.notice_period == '-1':
                    rec.notice_period_value = rec.basic_salary * -1
                if rec.notice_period == '-2':
                    rec.notice_period_value = rec.basic_salary * -2
                if rec.notice_period == '-3':
                    rec.notice_period_value = rec.basic_salary * -3

    def _calculate_loan_value(self):
        for termination in self:
            total = 0
            if termination.employee_id:
                loans = self.env['hr.loan'].search(
                    [('employee_id', '=', termination.employee_id.id), ('state', '=', 'approved2')])
                if loans:
                    loan_lines = loans.mapped('balance')
                    for line in loan_lines:
                        total += line
            termination.loan_value = total

    loan_value = fields.Float('Loan Value', compute='_calculate_loan_value', readonly=True)

    # @api.onchange('employee_id', 'job_ending_date')
    # def _compute_current_salary(self):
    #     for rec in self:
    #         payslip_obj = self.env["hr.payslip"].search(
    #             [
    #                 ('employee_id', '=', rec.employee_id.id),
    #                 ('date_from', '<=', rec.job_ending_date),
    #                 ('date_to', '>=', rec.job_ending_date),
    #                 ('state', '=', 'done'),
    #             ]
    #         )
    #
    #         payslip_lines = payslip_obj.line_ids
    #         print(payslip_obj)
    #         if payslip_lines:
    #             print(payslip_lines)
    #             net_salary_line = payslip_lines.filtered(lambda x: x.category_id.code == 'NET')
    #             print(net_salary_line)
    #             rec.current_salary_amount = net_salary_line.total

    @api.depends('employee_id', 'contract_id')
    def _get_amount_values(self):
        for rec in self:
            payslip_obj = self.env["hr.payslip"].search(
                [
                    ('employee_id', '=', rec.employee_id.id),
                    ('date_from', '<=', rec.job_ending_date),
                    ('date_to', '>=', rec.job_ending_date),
                    ('state', '=', 'done'),
                ]
            )
            payslip_lines = payslip_obj.line_ids
            if payslip_lines:
                net_salary_line = payslip_lines.filtered(lambda x: x.category_id.code == 'NET')
                rec.current_salary_amount = net_salary_line.total

            if rec.employee_id and rec.contract_id:
                plus_unpaid = sum(
                    self.env['hr.payslip.worked_days'].search([('payslip_id.employee_id', '=', rec.employee_id.id),
                                                               ('payslip_id.state', '=', 'done'),
                                                               ('payslip_id.contract_id', '=',
                                                                rec.employee_id.contract_id.id),
                                                               ('payslip_id.credit_note', '=', False),
                                                               ('work_entry_type_id.code', 'in',
                                                                ['LEAVE90', 'UNPAID'])]).mapped('number_of_days')) or 0
                mins_unpaid = sum(
                    self.env['hr.payslip.worked_days'].search([('payslip_id.employee_id', '=', rec.employee_id.id),
                                                               ('payslip_id.state', '=', 'done'),
                                                               ('payslip_id.credit_note', '=', True),
                                                               ('payslip_id.contract_id', '=',
                                                                rec.employee_id.contract_id.id),
                                                               ('work_entry_type_id.code', 'in',
                                                                ['LEAVE90', 'UNPAID'])]).mapped(
                        'number_of_days')) * -1 or 0
                leaves = self.env['hr.leave'].search([('emp_code', '=', self.employee_id.employee_id)])
                unpaid_days = 0
                for leave in leaves:
                    if leave.holiday_status_id.is_depend_eos and leave.state == 'validate':
                        unpaid_days += leave.number_of_days
                rec.unpaid_amount = unpaid_days
                # rec.unpaid_amount = plus_unpaid + mins_unpaid
                absence_plus = sum(
                    self.env['hr.payslip.worked_days'].search([('payslip_id.employee_id', '=', rec.employee_id.id),
                                                               ('payslip_id.state', '=', 'done'),
                                                               ('payslip_id.credit_note', '=', False),
                                                               ('payslip_id.contract_id', '=',
                                                                rec.employee_id.contract_id.id),
                                                               ('work_entry_type_id.code', 'in',
                                                                ['ABSENCE'])]).mapped('number_of_days')) or 0
                absence_mins = sum(
                    self.env['hr.payslip.worked_days'].search([('payslip_id.employee_id', '=', rec.employee_id.id),
                                                               ('payslip_id.state', '=', 'done'),
                                                               ('payslip_id.credit_note', '=', True),
                                                               ('payslip_id.contract_id', '=',
                                                                rec.employee_id.contract_id.id),
                                                               ('work_entry_type_id.code', 'in',
                                                                ['ABSENCE'])]).mapped('number_of_days')) * -1 or 0
                rec.absence_amount = absence_plus + absence_mins
            else:
                rec.unpaid_amount = 0
                rec.absence_amount = 0

    @api.constrains('years_val', 'months_val', 'days_val', 'calc_type')
    def constraint_manual_calc(self):
        for rec in self:
            if rec.calc_type == 'manual' and not rec.years_val and not rec.months_val and not rec.days_val:
                raise UserError(_("You can't set calc to manual and not adding any periods"))

    @api.depends('total_deserve', 'deserve_salary_amount', 'absence_amount_val', 'add_value', 'unpaid_amount_val',
                 'add_value_housing', 'current_salary_amount',
                 'ded_value')
    def _compute_total_deserve_amount(self):
        for termination in self:
            termination.total_deserve_amount = termination.total_deserve + termination.deserve_salary_amount + termination.current_salary_amount + termination.add_value + termination.add_value_housing - termination.loan_value - termination.absence_amount_val - termination.unpaid_amount_val - termination.ded_value

    @api.model
    def create(self, vals):
        termination_code = self.env['ir.sequence'].get('hr.termination.code')
        vals['termination_code'] = termination_code
        return super(Termination, self).create(vals)

    def get_employee_balance_leave(self):
        for holiday in self:
            leave_days = 0.0
            if holiday.employee_id.first_contract_date and holiday.job_ending_date:
                today = datetime.strptime(str(holiday.job_ending_date), '%Y-%m-%d')
                join_date = datetime.strptime(str(holiday.employee_id.first_contract_date), '%Y-%m-%d')
                # last_allocation_date = datetime.strptime(str(holiday.employee_id.last_allocation_date), '%Y-%m-%d')
                diff = today.date() - join_date.date()
                # allocation_days = (today.date() - last_allocation_date.date()).days
                service_period = round((diff.days / 365) * 12, 2)
                # allocation_method = holiday.employee_id.allocation_method
                day_allocate_lt = 0.0
                day_allocate_gt = 0.0
                day_allocate_eq = 0.0
                # if allocation_method:
                #     if allocation_method.type_state == 'two':
                #         day_allocate_lt = allocation_method.first_year / (365 - allocation_method.first_year)
                #         day_allocate_gt = allocation_method.second_year / (365 - allocation_method.second_year)
                #         # if allocation_days:
                #         #     if service_period <= 60:
                #         #         leave_days = allocation_days * day_allocate_lt
                #         #     else:
                #         #
                #         #         allocate_days = (last_allocation_date.date() - join_date.date()).days
                #         #         if allocate_days >= 1825:
                #         #             leave_days = allocation_days * day_allocate_gt
                #         #         else:
                #         #             day_to = 0
                #         #             for n in range(0, allocation_days + 1):
                #         #
                #         #                 if allocate_days <= 1825:
                #         #                     allocate_days += 1
                #         #                     day_to += 1
                #         #                 else:
                #         #
                #         #                     days_gt = allocation_days - day_to
                #         #                     leave_days = (days_gt * day_allocate_gt) + (day_to * day_allocate_lt)
                #         #                     break
                #     if allocation_method.type_state == 'all':
                #         day_allocate_eq = allocation_method.all_year / (365 - allocation_method.all_year)
                # if allocation_days:
                #     leave_days = allocation_days * day_allocate_eq
            return leave_days

    @api.onchange('job_ending_date')
    def onchange_ending_date(self):
        if self.employee_id:
            remaining_vacation = self.employee_id.remaining_leaves + self.get_employee_balance_leave()
            self.vacation_days = remaining_vacation

    @api.onchange('employee_id', 'job_ending_date')
    def onchange_employee_id(self):
        if self.employee_id:
            clearance = self.env['hr.clearance'].search([('employee_id', '=', self.employee_id.id)])
            for clear in clearance:
                if clear.state == 'done':
                    self.is_clearance = True
                else:
                    self.is_clearance = False
                    break
            vals = {'domain': {'contract_id': False}}
            self.job_id = self.employee_id.job_id.id
            self.hire_date = self.employee_id.first_contract_date
            remaining_vacation = self.employee_id.remaining_leaves + self.get_employee_balance_leave()
            self.vacation_days = remaining_vacation
            contracts = self.env['hr.contract'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')])
            li = []
            if contracts:
                for i in contracts:
                    li.append(i.id)
                vals['domain'].update({'contract_id': [('id', 'in', li)]})
            return vals

    @api.onchange('contract_id', 'employee_id', 'eos_reason', 'payment_method_leave', 'payment_method')
    def _onchange_contract_id(self):
        for record in self:
            salary_amount_leave = 0.0
            salary_amount = 0.0
            if record.contract_id and record.payment_method_leave:
                basic = record.contract_id.wage
                for field in record.payment_method_leave.field_ids:
                    if field.name == 'wage':
                        salary_amount_leave += record.contract_id[field.name]
                    elif field.name == 'allowance':
                        salary_amount_leave += record.contract_id.allowance
                    elif field.name == 'allowance2':
                        salary_amount_leave += record.contract_id.allowance2
                    elif field.name == 'allowance3':
                        salary_amount_leave += record.contract_id.allowance3
                    elif field.name == 'allowance4':
                        salary_amount_leave += record.contract_id.allowance4
                    elif field.name == 'transportation_value':
                        salary_amount_leave += record.contract_id.transportation_value
                    elif field.name == 'housing_monthly_allowance':
                        salary_amount_leave += record.contract_id.housing_monthly_allowance
                    elif field.name == 'mobile_allowance':
                        salary_amount_leave += record.contract_id.mobile_allowance
                    elif field.name == 'overtime_allowance':
                        salary_amount_leave += record.contract_id.overtime_allowance
                    elif field.name == 'work_allowance':
                        salary_amount_leave += record.contract_id.work_allowance
                    elif field.name == 'reward':
                        salary_amount_leave += record.contract_id.reward
                    elif field.name == 'fuel_car':
                        salary_amount_leave += record.contract_id.fuel_car
                    elif field.name == 'ticket_amount':
                        salary_amount_leave += record.contract_id.ticket_amount
                    elif field.name == 'food_allowance':
                        salary_amount_leave += record.contract_id.food_allowance
                    elif field.name == 'other_allowance':
                        salary_amount_leave += record.contract_id.other_allowance
            if record.contract_id and record.payment_method:
                basic = record.contract_id.wage
                for field in record.payment_method.field_ids:
                    if field.name == 'wage':
                        salary_amount += record.contract_id[field.name]
                    elif field.name == 'allowance':
                        salary_amount_leave += record.contract_id.allowance
                    elif field.name == 'allowance2':
                        salary_amount_leave += record.contract_id.allowance2
                    elif field.name == 'allowance3':
                        salary_amount_leave += record.contract_id.allowance3
                    elif field.name == 'allowance4':
                        salary_amount_leave += record.contract_id.allowance4
                    elif field.name == 'transportation_value':
                        salary_amount += record.contract_id.transportation_value
                    elif field.name == 'housing_monthly_allowance':
                        salary_amount += record.contract_id.housing_monthly_allowance
                    elif field.name == 'mobile_allowance':
                        salary_amount += record.contract_id.mobile_allowance
                    elif field.name == 'overtime_allowance':
                        salary_amount += record.contract_id.overtime_allowance
                    elif field.name == 'work_allowance':
                        salary_amount += record.contract_id.work_allowance
                    elif field.name == 'reward':
                        salary_amount += record.contract_id.reward
                    elif field.name == 'fuel_car':
                        salary_amount += record.contract_id.fuel_car
                    elif field.name == 'ticket_amount':
                        salary_amount += record.contract_id.ticket_amount
                    elif field.name == 'food_allowance':
                        salary_amount += record.contract_id.food_allowance
                    elif field.name == 'other_allowance':
                        salary_amount += record.contract_id.other_allowance

            record.salary_amount_leave = salary_amount_leave
            record.salary_amount = salary_amount
            record.basic_salary = salary_amount
            remaining_vacation = record.employee_id.remaining_leaves + record.get_employee_balance_leave()
            record.vacation_days = remaining_vacation
            record.deserve_salary_amount = (salary_amount_leave / 30) * remaining_vacation

    @api.onchange('vacation_days')
    def _onchange_vacation(self):
        if self.vacation_days:
            self.deserve_salary_amount = (self.salary_amount / 30) * self.vacation_days

    @api.onchange('job_ending_date', 'hire_date', 'calc_type', 'months_val', 'years_val', 'days_val')
    def _onchange_dates(self):
        if self.calc_type == 'contract':
            if self.job_ending_date and self.hire_date:
                start_date = datetime.strptime(str(self.hire_date), '%Y-%m-%d')
                end_date = datetime.strptime(str(self.job_ending_date), '%Y-%m-%d')
                months = utils.months_between(start_date, end_date)
                years = utils.years_between(start_date, end_date)
                self.working_period = months
                self.period_in_years = years
        else:
            months_total = self.months_val + self.years_val * 12 + self.days_val / 30
            self.working_period = months_total

    @api.depends('working_period', 'eos_reason', 'basic_salary', 'salary_amount')
    def _calculate_severance(self):
        total_severance = 0
        pass_duration = 0
        for rec in self:
            rec.compensatory_bonus = 0
            if rec.eos_reason in ['2', '20', '21']:  # for the zeros issues
                rec.total_deserve = 0
            elif rec.eos_reason in ['1', '10', '11', '12', '13', '14', '15']:  # for the normal issues
                if rec.working_period < 60:
                    rec.total_deserve = rec.working_period * 1 / 24 * rec.salary_amount
                else:
                    total_severance = 60 * 1 / 24 * rec.salary_amount
                    pass_duration = rec.working_period - 60
                    total_severance = total_severance + (pass_duration * 1 / 12 * rec.salary_amount)
                    rec.total_deserve = total_severance
            elif rec.eos_reason == '77':

                if rec.working_period < 60:
                    if rec.working_period < 36:
                        rec.total_deserve = (rec.working_period * 1 / 24 * rec.salary_amount) + (2 * rec.salary_amount)
                    else:
                        rec.compensatory_bonus = (rec.working_period / 12) * 0.5 * rec.salary_amount
                        rec.total_deserve = (rec.working_period * 1 / 24 * rec.salary_amount)
                else:
                    total_severance = 60 * 1 / 24 * rec.salary_amount
                    pass_duration = rec.working_period - 60
                    total_severance = total_severance + (pass_duration * 1 / 12 * rec.salary_amount)
                    rec.compensatory_bonus = (rec.working_period / 12) * 0.5 * rec.salary_amount
                    rec.total_deserve = total_severance

            elif rec.eos_reason == '3':  # Worst case resignation
                if rec.working_period < 24:
                    rec.total_deserve = 0
                elif rec.working_period < 60:
                    rec.total_deserve = rec.working_period * 1 / 24 * 1 / 3 * rec.salary_amount
                elif rec.working_period < 120:
                    total_severance = 60 * 1 / 24 * 2 / 3 * rec.salary_amount
                    pass_duration = rec.working_period - 60
                    rec.total_deserve = total_severance + (pass_duration * 1 / 12 * 2 / 3 * rec.salary_amount)
                else:
                    total_severance = 60 * 1 / 24 * rec.salary_amount
                    pass_duration = rec.working_period - 60
                    rec.total_deserve = total_severance + (pass_duration * 1 / 12 * rec.salary_amount)

    def button_review(self):
        if self.is_clearance:
            self.state = 'review'
        else:
            clearance = self.env['hr.clearance'].search([('employee_id', '=', self.employee_id.id)])
            for clear in clearance:
                if clear.state == 'done':
                    self.is_clearance = True
                    self.state = 'review'
                else:
                    self.is_clearance = False
                    raise ValidationError(_('You cannot create termination request for an employee with no clearance'))
            # if self.env['hr.clearance'].search([('employee_id', '=', self.employee_id.id)], limit=1).state == 'done':
            #     raise ValidationError(_('You cannot create termination request for an employee with no clearance'))
            # else:
            #     self.is_clearance = True
            #     self.state = 'review'

    def button_approve(self):
        self.approved_by = self.env.user.id
        self.state = 'approved2'
        self.contract_id.end_of_service = self.contract_id.date_end
        self.contract_id.date_end = self.job_ending_date
        self.contract_id.is_terminated = True

    def button_cancel(self):
        if self.state not in ['approved', 'approved2']:
            self.state = 'cancel'
        elif self.move_id and self.move_id.state == 'draft':
            self.contract_id.date_end = self.contract_id.end_of_service
            self.contract_id.is_terminated = False
            self.contract_id.end_of_service = False
            self.move_id.unlink()
            self.state = 'cancel'
        elif self.state in ['approved']:
            self.contract_id.date_end = self.contract_id.end_of_service
            self.contract_id.is_terminated = False
            self.state = 'cancel'
        else:
            raise UserError(_('You cannot delete a termination document'
                              ' which is posted Entries!'))

    def unlink(self):
        for termination in self:
            if termination.state not in ['draft', 'review', 'cancel']:
                raise UserError(_('You cannot delete a termination document'
                                  ' which is not draft or review or cancelled!'))
        return super(Termination, self).unlink()

    def validate_termination(self):
        for rec in self:
            rec.employee_id.active = False

        if self.is_clearance != True:
            raise ValidationError(_('Clearance Required first'))
        if self.payment_method:
            move_obj = self.env['account.move']
            timenow = time.strftime('%Y-%m-%d')

            line_ids = []
            name = _('Termination for ') + self.employee_id.name
            move = {
                'narration': name,
                'ref': self.termination_code,
                'date': self.approval_date or timenow,
                'termination_id': self.id,
                'journal_id': self.journal_id.id,
            }

            total_amount = self.total_deserve_amount
            eos_amount = self.total_deserve
            leave_amount = self.deserve_salary_amount
            absence_amount = self.absence_amount_val
            unpaid_amount = self.unpaid_amount_val
            add_amount = self.add_value
            loan_amount = self.loan_value
            ded_amount = self.ded_value
            debit_account_id = self.payment_method.debit_account_id.id or False
            credit_account_id = self.payment_method.credit_account_id.id or False
            loan_debit_account_id = self.payment_method.loan_debit_account_id.id or False
            loan_credit_account_id = self.payment_method.loan_credit_account_id.id or False
            leave_debit_account_id = self.payment_method.leave_debit_account_id.id or False
            leave_credit_account_id = self.payment_method.leave_credit_account_id.id or False
            absence_debit_account_id = self.payment_method.no_leave_debit_account_id.id or False
            absence_credit_account_id = self.payment_method.no_leave_credit_account_id.id or False

            unpaid_debit_account_id = self.payment_method.unpaid_leave_debit_account_id.id or False
            unpaid_credit_account_id = self.payment_method.unpaid_leave_credit_account_id.id or False

            ded_debit_account_id = self.payment_method.ded_debit_account_id.id or False
            ded_credit_account_id = self.payment_method.ded_credit_account_id.id or False
            add_debit_account_id = self.payment_method.add_debit_account_id.id or False
            add_credit_account_id = self.payment_method.add_credit_account_id.id or False

            if not self.payment_method:
                raise UserError(_('Please Set payment method'))

            if total_amount <= 0:
                raise UserError(_('Please Set Amount'))

            if not self.journal_id:
                raise UserError(_('Please Set Journal'))
            if not self.employee_id.address_home_id:
                raise UserError(_('Please Set Related Partner For Employee'))

            partner_id = False
            if self.employee_id.address_home_id:
                partner_id = self.employee_id.address_home_id.id

            if eos_amount:
                if not credit_account_id or not debit_account_id:
                    raise UserError(_('Please Set EOS credit/debit account '))
                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': 'Termination',
                        'date': self.approval_date or timenow,
                        'partner_id': partner_id,
                        'account_id': debit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': eos_amount,
                        'credit': 0.0,
                    })
                    line_ids.append(debit_line)

                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': 'Termination',
                        'date': self.approval_date or timenow,
                        'partner_id': partner_id,
                        'account_id': credit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': 0.0,
                        'credit': eos_amount,
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

            if absence_amount:
                if not absence_credit_account_id or not absence_debit_account_id:
                    raise UserError(_('Please Set Absence credit/debit account '))
                if leave_debit_account_id:
                    debit_line = (0, 0, {
                        'name': 'Absence',
                        'date': self.approval_date or timenow,
                        'partner_id': partner_id,
                        'account_id': absence_debit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': absence_amount,
                        'credit': 0.0,
                    })
                    line_ids.append(debit_line)
                if absence_credit_account_id:
                    credit_line = (0, 0, {
                        'name': 'Absence',
                        'date': self.approval_date or timenow,
                        'partner_id': partner_id,
                        'account_id': absence_credit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': 0.0,
                        'credit': absence_amount,
                    })
                    line_ids.append(credit_line)
            if unpaid_amount:
                if not unpaid_credit_account_id or not unpaid_debit_account_id:
                    raise UserError(_('Please Set Unpaid credit/debit account '))
                if leave_debit_account_id:
                    debit_line = (0, 0, {
                        'name': 'Unpaid',
                        'date': self.approval_date or timenow,
                        'partner_id': partner_id,
                        'account_id': unpaid_debit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': unpaid_amount,
                        'credit': 0.0,
                    })
                    line_ids.append(debit_line)
                if unpaid_credit_account_id:
                    credit_line = (0, 0, {
                        'name': 'Unpaid',
                        'date': self.approval_date or timenow,
                        'partner_id': partner_id,
                        'account_id': unpaid_credit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': 0.0,
                        'credit': unpaid_amount,
                    })
                    line_ids.append(credit_line)
            if add_amount:
                if not add_credit_account_id or not add_debit_account_id:
                    raise UserError(_('Please Set Addition credit/debit account '))
                if add_debit_account_id:
                    debit_line = (0, 0, {
                        'name': 'Addition',
                        'date': self.approval_date or timenow,
                        'partner_id': False,
                        'account_id': add_debit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': add_amount,
                        'credit': 0.0,
                    })
                    line_ids.append(debit_line)

                if add_credit_account_id:
                    credit_line = (0, 0, {
                        'name': 'Addition',
                        'date': self.approval_date or timenow,
                        'partner_id': False,
                        'account_id': add_credit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': 0.0,
                        'credit': add_amount,
                    })
                    line_ids.append(credit_line)
            if loan_amount:
                if not loan_credit_account_id or not loan_debit_account_id:
                    raise UserError(_('Please Set Loan credit/debit account '))
                if loan_debit_account_id:
                    debit_line = (0, 0, {
                        'name': 'Loan',
                        'date': self.approval_date or timenow,
                        'partner_id': partner_id,
                        'account_id': loan_debit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': loan_amount,
                        'credit': 0.0,
                    })
                    line_ids.append(debit_line)

                if loan_credit_account_id:
                    credit_line = (0, 0, {
                        'name': 'Loan',
                        'date': self.approval_date or timenow,
                        'partner_id': partner_id,
                        'account_id': loan_credit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': 0.0,
                        'credit': loan_amount,
                    })
                    line_ids.append(credit_line)
            if ded_amount:
                if not ded_credit_account_id or not ded_debit_account_id:
                    raise UserError(_('Please Set Deduction credit/debit account '))
                if ded_debit_account_id:
                    debit_line = (0, 0, {
                        'name': 'Deduction',
                        'date': self.approval_date or timenow,
                        'partner_id': False,
                        'account_id': ded_debit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': ded_amount,
                        'credit': 0.0,
                    })
                    line_ids.append(debit_line)

                if ded_credit_account_id:
                    credit_line = (0, 0, {
                        'name': 'Deduction',
                        'date': self.approval_date or timenow,
                        'partner_id': False,
                        'account_id': ded_credit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': 0.0,
                        'credit': ded_amount,
                    })
                    line_ids.append(credit_line)

            move.update({'line_ids': line_ids})
            move_id = move_obj.create(move)

            self.write(
                {'move_id': move_id.id, 'state': 'approved2', })
            # move_id.post()
            self.employee_id.active = False
        return True

    def open_entries(self):
        context = dict(self._context or {}, search_default_termination_id=self.ids, default_termination_id=self.ids)
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
        _name = "termination.payments"

        name = fields.Char('Name', required=True, help='Payment name')
        company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
        debit_account_id = fields.Many2one('account.account', 'EOS Debit Account', required=False,
                                           help='EOS Debit account for journal entry')
        credit_account_id = fields.Many2one('account.account', 'EOS Credit Account', required=False,
                                            help='EOS Credit account for journal entry')
        loan_debit_account_id = fields.Many2one('account.account', 'Loan Debit Account', required=False,
                                                help='Loan Debit account for journal entry')
        loan_credit_account_id = fields.Many2one('account.account', 'Loan Credit Account', required=False,
                                                 help='Loan Credit account for journal entry')
        leave_debit_account_id = fields.Many2one('account.account', 'Leave Debit Account', required=False,
                                                 help='Leave Debit account for journal entry')
        leave_credit_account_id = fields.Many2one('account.account', 'Leave Credit Account', required=False,
                                                  help='Leave Credit account for journal entry')

        unpaid_leave_debit_account_id = fields.Many2one('account.account', 'Unpaid Leave Debit Account', required=False,
                                                        help='Leave Debit account for journal entry')
        unpaid_leave_credit_account_id = fields.Many2one('account.account', 'Unpaid Leave Credit Account',
                                                         required=False,
                                                         help='Leave Credit account for journal entry')

        no_leave_debit_account_id = fields.Many2one('account.account', 'Absence Debit Account', required=False,
                                                    help='Leave Debit account for journal entry')
        no_leave_credit_account_id = fields.Many2one('account.account', 'Absence Credit Account', required=False,
                                                     help='Leave Credit account for journal entry')

        ded_debit_account_id = fields.Many2one('account.account', 'Deduction Debit Account', required=False,
                                               help='Deduction Debit account for journal entry')
        ded_credit_account_id = fields.Many2one('account.account', 'Deduction Credit Account', required=False,
                                                help='Deduction Credit account for journal entry')
        add_debit_account_id = fields.Many2one('account.account', 'Addition Debit Account', required=False,
                                               help='Addition Debit account for journal entry')
        add_credit_account_id = fields.Many2one('account.account', 'Addition Credit Account', required=False,
                                                help='Addition Credit account for journal entry')
        field_ids = fields.Many2many('ir.model.fields', 'termination_field_rel', 'termination_id', 'field_id',
                                     'Calculation Lines',
                                     domain=[('model_id', '=', 'hr.contract'), ('ttype', 'in', ['float', 'monetary']), (
                                         'name', 'in', ['wage', 'allowance', 'allowance2', 'allowance3', 'allowance4',
                                                        'transportation_value', 'housing_monthly_allowance',
                                                        'mobile_allowance', 'overtime_allowance', 'work_allowance',
                                                        'reward', 'ticket_amount', 'fuel_car', 'food_allowance',
                                                        'other_allowance'])])

    # class HrContract(models.Model):
    #     _inherit = "hr.contract"
    #
    #     end_of_service = fields.Date('Original End Date')
    #     is_terminated = fields.Boolean('Terminated')
    #     trial_date_start = fields.Date()
    #     working_hours = fields.Float()
