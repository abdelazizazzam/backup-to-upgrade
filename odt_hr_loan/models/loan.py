from odoo import models, api, fields
import time
from odoo.tools.translate import _
import math
from datetime import datetime
from odoo.exceptions import UserError
import warnings


class AccountMove(models.Model):
    _inherit = 'account.move'

    loan_id = fields.Many2one('hr.loan', 'Loan', help='Loan Record')


def get_next_month(date):
    try:
        return date.replace(date.year, date.month + 1, 1)
    except ValueError:
        if date.month == 12:
            return date.replace(date.year + 1, 1, 1)


class Employee(models.Model):
    _inherit = "hr.employee"

    loan_ids = fields.One2many('hr.loan', 'employee_id', string='Loans')

    loans_count = fields.Integer(
        compute='_compute_loans_count', string='Loans')

    def _compute_loans_count(self):
        for employee in self:
            employee.loans_count = len(employee.loan_ids)


class HrLoan(models.Model):
    _name = "hr.loan"
    _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char('Name', readonly=True, help='Sequence of loan', tracking=True)
    employee_id = fields.Many2one(
        'hr.employee',
        'Employee',
        required=True,
        help='Employee Name',
        tracking=True,
        default=lambda self: self._get_default_employee()
    )
    amount = fields.Float('Amount', required=True, help='Amount of loan', tracking=True)
    balance = fields.Float(
        'Balance', compute='_compute_balance_amount', help='Balance of loan', tracking=True)
    date = fields.Date('Date', default=fields.Date.context_today, tracking=True)
    start_date = fields.Date('Start Date', required=True, help='date to Start the loan', tracking=True,
                             default=fields.Date.context_today)
    end_date = fields.Date(string='End Date', store=True, tracking=True,
                           compute='_compute_balance_amount', help='End of loan')
    reason = fields.Text('Reason', help='Reason of loan', tracking=True)
    is_exceed = fields.Boolean(
        'Exceed the Maximum', help='True if the amount exceed the limit for employee', tracking=True)
    payment_method = fields.Many2one(
        'loan.payments', 'Payment Method', help='Payment method for loan', tracking=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('submit', 'Submit'), ('cancel', 'Cancel'), ('approved1', 'First Approved'),
         ('approved', 'Second Approved'), ('approved2', 'Final Approved'),
         ('terminated', 'Terminated')], 'Status', default='draft', tracking=True)
    move_id = fields.Many2one(
        'account.move', 'Journal Entry', help='Journal Entry for loan', tracking=True)
    move_ids = fields.Many2many('account.move', 'account_move_loan_rel', 'employee_id', 'loan_id',
                                'Journal Entries', help='Journal entries related to this loan',
                                tracking=True)
    depart_id = fields.Many2one(
        'hr.department', 'Department', help='Department of employee', tracking=True)

    loan_line_ids = fields.One2many('hr.loan.line', 'loan_id', 'Loan Lines', tracking=True,
                                    help='When to pay the loan and amount of each date')
    deduction_type = fields.Selection(string="Deduction Type", selection=[('amount', 'Amount'), ('installment', 'Installments'), ], required=False, )
    no_of_months = fields.Integer('No of Months', default=1, tracking=True)
    amount_per_month = fields.Integer('Amount Per Month', default=lambda self: self.amount, tracking=True)
    no_of_delay = fields.Integer('No of Months Delay', default=0, tracking=True)
    journal_id = fields.Many2one('account.journal', 'Journal', domain=[('type', 'in', ['bank', 'cash'])],
                                 help='Journal for journal entry', tracking=True)
    company_id = fields.Many2one(comodel_name="res.company", string="Company", related='employee_id.company_id',
                                 tracking=True)
    loan_account = fields.Many2one(comodel_name="account.account", string="Loan Account", required=False,
                                   tracking=True)
    journal_miscellaneous = fields.Boolean(string="Journal Miscellaneous", tracking=True,
                                           related="payment_method.journal_miscellaneous")
    is_opening = fields.Boolean(string='Is Opening', default=False)
    loan_amount = fields.Float('Loan Amount')
    total_paid = fields.Float('Total Paid')
    loan_no = fields.Char('loan no')
    dis_no = fields.Char('Dis no')
    payment_method_type = fields.Selection(string='Payment Method Type',
                                           selection=[('loan', 'Loan'), ('install', 'Installment')],
                                           related='payment_method.loan_type')
    attachment_ids = fields.Many2many('ir.attachment', string="Attachment")
    can_edit_employee = fields.Boolean(
        compute="_compute_can_edit_employee", store=False,
        default=lambda self: self.env.user.has_group('hr.group_hr_user') or \
                             self.env.user.has_group('account.group_account_invoice')
    )

    @api.constrains('amount', 'loan_amount', 'total_paid')
    def check_opening_amounts(self):
        for rec in self:
            if rec.is_opening:
                if rec.loan_amount != (rec.total_paid + rec.amount):
                    raise UserError(_("Loan Amount must be equal Total Paid and Current Amount"))

    @api.onchange('is_opening')
    def opening_change(self):
        for rec in self:
            rec.loan_amount = rec.total_paid = 0

    @api.constrains('loan_line_ids', 'amount')
    def check_amount(self):
        for line in self:
            if line.loan_line_ids:
                total = 0
                for loan in line.loan_line_ids:
                    total += loan.amount
                if total != line.amount:
                    raise UserError(_("Total Loan Line not equal amount value."))

    @api.onchange('payment_method')
    def _onchange_payment_method(self):
        if self.payment_method.journal_miscellaneous == True:
            self.journal_id = False
            return {'domain': {'journal_id': [('type', '=', 'general'), ('company_id', '=', self.company_id.id)]}}
        else:
            return {'domain': {'journal_id': [('type', '!=', 'general'), ('company_id', '=', self.company_id.id)]}}

    # @api.one
    def _compute_balance_amount(self):
        for record in self:
            balance = 0
            if record.loan_line_ids:
                record.end_date = record.loan_line_ids[-1].discount_date
                amounts = record.loan_line_ids.filtered(
                    lambda pay: pay.paid == False).mapped('amount')
                for line in amounts:
                    balance += float(line)
            record.balance = balance

    def _compute_can_edit_employee(self):
        for record in self:
            record.can_edit_employee = self.env.user.has_group('hr.group_hr_user') or \
                                       self.env.user.has_group('account.group_account_invoice')

    # @api.multi
    def create_payment(self):
        view_ref = self.env['ir.model.data'].check_object_reference('odt_hr_loan',
                                                                  'loan_payment_view')
        view_id = view_ref and view_ref[1] or False,
        return {
            'type': 'ir.actions.act_window',
            'name': 'Make Payment',
            'res_model': 'hr.loan.payment',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_payment_method': self.payment_method.id},
            'view_id': view_id,
            'nodestroy': True,
        }

    @api.onchange('employee_id')
    def _onchange_employee(self):
        self.depart_id = self.employee_id.sudo().department_id.id


    # @api.multi
    def unlink(self):
        for loan in self:
            if loan.move_ids:
                raise UserError(
                    _('You Can not Delete Loan/s that have Journal Entries .'))
            if loan.state in ['approved1', 'approved2']:
                raise UserError(
                    _('You Can not Delete Loan/s that is Approved State .'))
        res = super(HrLoan, self).unlink()
        return res

    # @api.multi
    def validate_loan(self):

        if not self.env.user.has_group('odt_hr_loan.approve2_group'):
            raise UserError(_("You can't Validate Loan."))
        if self.payment_method:
            move_pool = self.env['account.move']
            timenow = time.strftime('%Y-%m-%d')

            line_ids = []
            name = _('Loan for ') + self.employee_id.name
            move = {
                'narration': name,
                'move_type': 'entry',
                'ref': self.name or 'Loan',
                'date': timenow,
                # 'company_id':self.company_id,
                'loan_id': self.id,
                'journal_id': self.journal_id.id,
            }

            amount = self.amount
            if self.payment_method.loan_type == 'install':
                credit_account_id = self.payment_method.credit_account_id.id or False
            else:
                credit_account_id = self.loan_account.id or self.payment_method.credit_account_id.id
            debit_account_id = self.payment_method.debit_account_id.id or False
            # credit_account_id = self.journal_id.default_credit_account_id.id or False
            analytic_account_id = self.payment_method.analytic_account_id.id or False
            if not self.payment_method:
                raise UserError(_('Please Set payment method'))

            if amount <= 0:
                raise UserError(_('Please Set Amount'))

            if not self.journal_id:
                raise UserError(_('Please Set Journal'))

            if not self.employee_id.address_id:
                raise UserError(_('Please Set Related Partner For Employee'))

            if not credit_account_id or not debit_account_id:
                raise UserError(_('Please Set credit/debit account '))
            partner_id = False
            if self.employee_id.address_id:
                partner_id = self.employee_id.address_id.id
            if debit_account_id:
                debit_line = (0, 0, {
                    'name': 'Loan',
                    'date': timenow,
                    'partner_id': partner_id,
                    'account_id': debit_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': amount,
                    'credit': 0.0,
                    # 'analytic_account_id': analytic_account_id,
                })
                line_ids.append(debit_line)

            if credit_account_id:
                credit_line = (0, 0, {
                    'name': 'Loan',
                    'date': timenow,
                    'partner_id': False,
                    'account_id': credit_account_id,
                    'journal_id': self.journal_id.id,
                    'debit': 0.0,
                    'credit': amount,
                    # 'analytic_account_id': False,
                })
                line_ids.append(credit_line)

                move.update({'line_ids': line_ids})
                move_id = move_pool.create(move)
                move_ids = [move_id.id]
                for move_rec in self.move_ids:
                    move_ids.append(move_rec.id)

                loan_name = self.name
                if not self.name:
                    loan_name = self.env['ir.sequence'].get('hr.loan')

                self.write(
                    {'move_id': move_id.id, 'move_ids': [(6, 0, move_ids)],
                     'state': 'approved2', 'name': loan_name})
                self.activity_done()
                # move_id.post()
        else:
            loan_name = self.name
            if not self.name:
                loan_name = self.env['ir.sequence'].get('hr.loan')
            self.write({'state': 'approved2', 'name': loan_name})
            self.activity_done()
        return True

    # @api.multi
    def create_inverse_entry(self, line_ids, move_id):
        move_line_obj = self.env['account.move.line']
        move_obj = self.env['account.move']
        timenow = time.strftime('%Y-%m-%d')

        res = {'move_id': False, 'line_ids': []}

        inv_move_id = move_obj.create({
            'journal_id': move_id.journal_id.id,
            'narration': _('Inverse: ') + move_id.narration,
            'move_type': 'entry',
            'date': timenow,
            'ref': move_id.ref,
            'loan_id': move_id.loan_id.id,
        })
        res['move_id'] = inv_move_id
        for line in line_ids:
            analytic_account = False
            if line.analytic_account_id:
                analytic_account = line.analytic_account_id.id
            new_move_line = move_line_obj.create({
                'name': line.name,
                'date': timenow,
                'partner_id': False,
                'account_id': line.account_id.id,
                'journal_id': line.journal_id.id,
                'debit': line.credit,
                'credit': line.debit,
                'move_id': inv_move_id.id,
                # 'analytic_account_id': analytic_account,
            })
            res['line_ids'].append(new_move_line)

        inv_move_id.post()
        return res

    # @api.multi
    def cancel_loan(self):
        if not self.env.user.has_group('odt_hr_loan.cancel_group'):
            raise UserError(_("You can't Cancel Loan."))
        move_line_obj = self.env['account.move.line']
        move_obj = self.env['account.move']
        for loan_slip in self:
            if loan_slip.move_id:
                line_ids = move_line_obj.search(
                    [('move_id', '=', loan_slip.move_id.id)])
                data = self.create_inverse_entry(line_ids, loan_slip.move_id)
                move_ids = []
                move_ids.append(data['move_id'])
                for move_rec in loan_slip.move_ids:
                    move_ids.append(move_rec.id)
                loan_slip.write(
                    {'move_ids': [(6, 0, move_ids)], 'state': 'cancel'})
            loan_slip.state = 'cancel'
            self.activity_done()

    # @api.multi
    def draft_loan(self):
        for loan_slip in self:
            self.write({'state': 'draft'})
            self.activity_done()
        return True

    # @api.multi
    def submit_loan(self):
        for loan_slip in self:
            self.write({'state': 'submit'})
            for user in self.env['res.users'].search([]):
                if user.has_group('odt_hr_loan.approve1_group'):
                    self.activity_schedule(
                        activity_type_id=self.env.ref('odt_hr_loan.mail_act_hr_loan').id,
                        summary=_('HR Loan Needs Approve'), user_id=user.id)
        return True

    # @api.multi
    def approve_loan(self):
        if not self.env.user.has_group('odt_hr_loan.approve1_group'):
            raise UserError(_("You can't Approve Loan."))
        for loan_slip in self:
            self.write({'state': 'approved1'})
            self.activity_done()
            for user in self.env['res.users'].search([]):
                if user.has_group('odt_hr_loan.approve_group'):
                    self.activity_schedule(
                        activity_type_id=self.env.ref('odt_hr_loan.mail_act_hr_loan').id,
                        summary=_('HR Loan Needs Approve'), user_id=user.id)
        return True

    def approve2_loan(self):
        if not self.env.user.has_group('odt_hr_loan.approve_group'):
            raise UserError(_("You can't Second Approve Loan."))
        for loan_slip in self:
            if self.payment_method_type == 'loan':
                self.write({'state': 'approved'})
                self.activity_done()
                for user in self.env['res.users'].search([]):
                    if user.has_group('odt_hr_loan.approve2_group'):
                        self.activity_schedule(
                            activity_type_id=self.env.ref('odt_hr_loan.mail_act_hr_loan').id,
                            summary=_('HR Loan Needs to be Validated'), user_id=user.id)
            elif self.payment_method_type == 'install':
                self.journal_id = self.payment_method.journal_id.id 
                self.write({'state': 'approved'})
                self.activity_done()
        return True

    # @api.multi
    def delay_loan(self):
        for loan_slip in self:
            lines = loan_slip.loan_line_ids.filtered(
                lambda pay: pay.paid == False)
            if lines:
                start_date = lines[0].discount_date
                date = datetime.strptime(str(start_date), '%Y-%m-%d')
                for i in range(0, self.no_of_delay):
                    date = get_next_month(date)
                for line in lines:
                    line.write({'discount_date': date})
                    date = get_next_month(date)
        self.no_of_delay = 0
        return True


    def delay_loan(self):
        for loan_slip in self:
            lines = loan_slip.loan_line_ids.filtered(
                lambda pay: pay.paid == False)
            if lines:
                start_date = lines[0].discount_date
                date = datetime.strptime(str(start_date), '%Y-%m-%d')
                for i in range(0, self.no_of_delay):
                    date = get_next_month(date)
                for line in lines:
                    line.write({'discount_date': date})
                    date = get_next_month(date)
        self.no_of_delay = 0
        return True

    def pay_off_loan(self):
        if not self.attachment_ids:
            raise UserError(_('Please Provide the demanded attachments'))
        self.balance = 0.0
        for loan in self.loan_line_ids:
            loan.paid = True
        return True    


    @api.model
    def create(self, vals):
        print("I am here")
        print("I am eher",vals) # error
        employee = self.env['hr.employee'].browse(vals['employee_id'])
        contract_id = employee._get_contracts(
            vals['start_date'], vals['start_date'])
        if contract_id:
            contract = contract_id[0]
            if not contract.date_end or str(contract.date_end) > str(vals['start_date']):
                pass
            else:
                raise UserError(_('The Employee Out Of Work'))

        res = super(HrLoan, self).create(vals)
        return res

    @api.model
    def _get_default_employee(self):
        employee = self.env['hr.employee'].sudo().search([('user_id', '=', self.env.uid)], limit=1).id
        return employee

    @api.onchange('amount', 'no_of_months', 'deduction_type', 'amount_per_month', 'start_date')
    def _onchange_amount(self):
        entries = []
        if self.amount:
            if self.deduction_type == 'installment':
                contract_id = self.employee_id._get_contracts(
                    self.start_date, self.start_date)
                if contract_id:
                    if contract_id.date_end and contract_id.date_end < self.start_date:
                        raise UserError(_('The Employee Out Of Work'))
                    employee_salary = contract_id.wage
                    loan_percentage = (
                            contract_id.sudo().structure_type_id.loan_percentage * 0.01)

                    # if self.amount > (employee_salary * loan_percentage):
                    #     print("if self.is_exceed",self.is_exceed)
                    #     # warning = {
                    #     #     'title': _('Warning!'),
                    #     #     'message': _('Amount is Above the Maximum limits with Max. percentage loan ' + str(
                    #     #         contract_id.structure_type_id.loan_percentage))
                    #     # }
                    #     # return {'value': {'is_exceed': True, }, 'warning': warning}
                    #
                    #     warnings.warn('Amount is Above the Maximum limits with Max. percentage loan ' + str(
                    #             contract_id.structure_type_id.loan_percentage))
                    if self.amount:
                        print("elseee 2")
                        start_date = self.start_date
                        date = datetime.strptime(str(start_date), '%Y-%m-%d')
                        for i in range(0, self.no_of_months):
                            data = {
                                'discount_date': str(date),
                                'amount': self.amount / self.no_of_months
                            }
                            date = get_next_month(date)
                            entries.append((0, 0, data))
                else:
                    raise UserError(
                        _('No Contract for This Employee or Check the Starting Date in Contract'))
            elif self.deduction_type == 'amount':
                contract_id = self.employee_id._get_contracts(
                    self.start_date, self.start_date)
                if contract_id:
                    if contract_id.date_end and contract_id.date_end < self.start_date:
                        raise UserError(_('The Employee Out Of Work'))
                    employee_salary = contract_id.wage
                    loan_percentage = (
                            contract_id.sudo().structure_type_id.loan_percentage * 0.01)

                    if self.amount > (employee_salary * loan_percentage) and not self.is_exceed:
                        print("22 self.is_exceed", self.is_exceed)
                        # warning = {
                        #     'title': _('Warning!'),
                        #     'message': _('Amount is Above the Maximum limits with Max. percentage loan ' + str(
                        #         contract_id.structure_type_id.loan_percentage))
                        # }
                        # return {'value': {'is_exceed': True, }, 'warning': warning}

                        warnings.warn('Amount is Above the Maximum limits with Max. percentage loan ' + str(
                                contract_id.structure_type_id.loan_percentage))
                    else:
                        start_date = self.start_date
                        date = datetime.strptime(str(start_date), '%Y-%m-%d')
                        fraction = self.amount % self.amount_per_month
                        if not fraction:
                            months_lines = int(self.amount / self.amount_per_month)
                            for i in range(0, months_lines):
                                data = {
                                    'discount_date': str(date),
                                    'amount': self.amount_per_month
                                }
                                date = get_next_month(date)
                                entries.append((0, 0, data))
                        else:
                            months_lines = math.trunc(self.amount / self.amount_per_month)
                            for i in range(0, months_lines):
                                data = {
                                    'discount_date': str(date),
                                    'amount': self.amount_per_month
                                }
                                date = get_next_month(date)
                                entries.append((0, 0, data))
                            lines_in_table = 0
                            for entry in entries:
                                lines_in_table += 1
                            last_month_amount = self.amount - (self.amount_per_month * lines_in_table)
                            data = {
                                'discount_date': str(date),
                                'amount': last_month_amount
                            }
                            entries.append((0, 0, data))
                else:
                    raise UserError(
                        _('No Contract for This Employee or Check the Starting Date in Contract'))

        if self.state != 'draft':
            self.loan_line_ids = False
            self.is_exceed = False
            self.update({'loan_line_ids': entries})

    def check_amount_totals(self, vals, type_op):
        if not self.state == 'draft':
            if type_op == 'create':
                if vals.get('loan_line_ids', False):
                    amount_total = 0.0
                    for line in vals['loan_line_ids']:
                        amount_total += line[2]['amount']
                    if abs(amount_total - vals['amount']) > 1.00:
                        raise UserError(_('Total of Lines not equel to amount'))
            else:
                loan_line_obj = self.env['hr.loan.line']
                amount_total = 0.0
                loan_amount = self.amount
                # if vals.has_key('amount'):
                if ('amount') in vals:
                    loan_amount = vals['amount']
                # if vals.has_key('loan_line_ids'):
                if ('loan_line_ids') in vals:
                    for line in vals['loan_line_ids']:
                        if type(line[2]) is dict and ('amount') in line[2]:
                            amount_total += line[2]['amount']
                        elif line[0] != 2:
                            amount_total += loan_line_obj.browse(
                                line[1]).amount
                else:
                    for line in self.loan_line_ids:
                        amount_total += line.amount
                if abs(amount_total - loan_amount) < 1.00:
                    pass
                else:
                    raise UserError(_('Total of Lines not equal to amount'))

    def write(self, vals):
        for loan in self:
            if ('loan_line_ids') in vals or ('amount') in vals:
                equel = loan.check_amount_totals(vals, 'write')

            if vals.get('start_date'):
                contract_id = loan.employee_id._get_contracts(
                    loan.start_date, loan.start_date)
                if contract_id:
                    contract = contract_id[0]

                    date = datetime.strptime(str(vals['start_date']), '%Y-%m-%d')
                    if not contract.date_end or contract.date_end > date.date():
                        pass
                    else:
                        raise UserError(_('The Employee Out Of Work'))

            if vals.get('amount', False):
                contract_id = loan.employee_id._get_contracts(
                    loan.start_date, loan.start_date)
                if contract_id:
                    contract = contract_id[0]
                    loan_percentage = (
                            contract.structure_type_id.loan_percentage * 0.01)
                    employee_salary = contract.wage
                    exceed = vals['is_exceed'] if 'is_exceed' in vals else loan.is_exceed
                    if vals['amount'] > (employee_salary * loan_percentage) and not exceed:
                        raise UserError(_('Amount is Above the Maximum limits with Max. percentage loan ' + str(
                            contract.structure_type_id.loan_percentage)))
        return super(HrLoan, self).write(vals)

    def open_entries(self):
        self.ensure_one()
        return {
            "type": "ir.actions.act_window",
            "res_model": "account.move",
            "views": [[False, "tree"], [False, "form"]],
            "domain": [['id', 'in', self.move_ids.ids]],
            'name': _('Journal Entries'),
        }

    # set all current running activities to done
    def activity_done(self):
        for rec in self.activity_ids:
            rec.action_done()


class HrLoanLines(models.Model):
    _name = "hr.loan.line"

    loan_id = fields.Many2one('hr.loan', 'Loan')
    discount_date = fields.Date(
        'Date', required=True, help='Date for discount the amount')
    amount = fields.Float('Amount', required=True,
                          help='Amount of each payment')
    paid = fields.Boolean('Paid')
    payslip_id = fields.Many2one('hr.payslip')

    @api.onchange('amount')
    def _onchange_amount(self):
        if self.amount:
            if self.paid:
                raise UserError(
                    _('You can not change amount which is already paid'))

    # @api.multi
    def unlink(self):
        for line in self:
            if line.paid:
                raise UserError(_('You can not delete a line which is already paid'))
        return super(HrLoanLines, self).unlink()


class HrPayrollStructure(models.Model):
    _inherit = "hr.payroll.structure.type"

    loan_percentage = fields.Integer('Max Loan Percentage (%)', required=True,
                                     help='Maximum percentage of loan for each structure')


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    # def compute_sheet(self):
    #     self._onchange_loan_ids()
    #     self._onchange_install_ids()
    #     res = super(HrPayslip, self).compute_sheet()
    #     return res

    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee(self):
        self._onchange_loan_ids()
        self._onchange_install_ids()
        self._onchange_eos_id()
        self._onchange_eos_compensate()
        self._onchange_eos_leave()
        self._onchange_eos_add()

    def _onchange_install_ids(self):
        for rec in self:
            loan_obj = self.env['hr.loan']
            loan_line_obj = self.env['hr.loan.line']
            employee_id = rec.employee_id.id
            # Install Loans
            install_ids = loan_obj.search(
                [('employee_id', '=', employee_id), ('state', '=', 'approved2'), ('payment_method_type', '=', 'install'), ])
            # For Installment Payment
            if install_ids and rec.credit_note != True:
                install_amounts = {}
                for install_id in install_ids:
                    install_input_type_id = install_id.payment_method.other_input_type_id
                    install_input_type_name = install_id.payment_method.other_input_type_id.name

                    line_ids = loan_line_obj.search([('loan_id', '=', install_id.id),
                                                     ('paid', '=', False),
                                                     ('discount_date', '>=', rec.date_from),
                                                     ('discount_date', '<=', rec.date_to)])
                    if line_ids:
                        for line in line_ids:
                            amount = line.amount
                            if amount > 0:
                                # To add similar types
                                if install_input_type_name in install_amounts.keys():
                                    amount += install_amounts[install_input_type_name]
                                    install_amounts.update({install_input_type_name: amount})
                                else:
                                    install_amounts.update({install_input_type_name: amount})

                        # to avoid repetition
                        lines_to_delete = self.input_line_ids.filtered(lambda x: x.input_type_id == install_input_type_id)

                        input_values = [(3, input_line.id, 0) for input_line in lines_to_delete]

                        input_values.append((0, 0, {
                            'amount': amount,
                            'input_type_id': install_input_type_id.id
                        }))

                        self.write({'input_line_ids': input_values})

            elif install_ids and rec.credit_note == True:
                install_amounts = {}
                for install_id in install_ids:
                    install_input_type_id = install_id.payment_method.other_input_type_id
                    install_input_type_name = install_id.payment_method.other_input_type_id.name

                    line_ids = loan_line_obj.search([('loan_id', '=', install_id.id),
                                                     ('paid', '=', True),
                                                     ('discount_date',
                                                      '>=', rec.date_from),
                                                     ('discount_date', '<=', rec.date_to)])
                    if line_ids:
                        for line in line_ids:
                            amount = line.amount
                            if amount > 0:
                                # To add similar types
                                if install_input_type_name in install_amounts.keys():
                                    amount += install_amounts[install_input_type_name]
                                    install_amounts.update({install_input_type_name: amount})
                                else:
                                    install_amounts.update({install_input_type_name: amount})

                        # to avoid repetition
                        lines_to_delete = self.input_line_ids.filtered(lambda x: x.input_type_id == install_input_type_id)

                        input_values = [(3, input_line.id, 0) for input_line in lines_to_delete]

                        input_values.append((0, 0, {
                            'amount': amount,
                            'input_type_id': install_input_type_id.id
                        }))

                        self.write({'input_line_ids': input_values})

    def _onchange_loan_ids(self):
        expense_type = self.env.ref(
            'odt_hr_loan.loan_other_input', raise_if_not_found=False)
        if not expense_type:
            return
        for rec in self:
            loan_obj = self.env['hr.loan']
            loan_line_obj = self.env['hr.loan.line']
            employee_id = rec.employee_id.id
            # Normal Loans
            loan_ids = loan_obj.search(
                [('employee_id', '=', employee_id), ('state', '=', 'approved2'), ('payment_method_type', '=', 'loan'),])

            loan_total = 0.0
            if loan_ids and rec.credit_note != True:
                for loan_id in loan_ids:
                    line_ids = loan_line_obj.search([('loan_id', '=', loan_id.id),
                                                     ('paid', '=', False),
                                                     ('discount_date',
                                                      '>=', rec.date_from),
                                                     ('discount_date', '<=', rec.date_to)])
                    if line_ids:
                        for loan in line_ids:
                            loan_total += loan.amount

            elif loan_ids and rec.credit_note == True:
                for loan_id in loan_ids:
                    line_ids = loan_line_obj.search([('loan_id', '=', loan_id.id),
                                                     ('paid', '=', True),
                                                     ('discount_date',
                                                      '>=', rec.date_from),
                                                     ('discount_date', '<=', rec.date_to)])
                    if line_ids:
                        for loan in line_ids:
                            loan_total += loan.amount
            if not loan_total:
                return

            # lines_to_keep = rec.input_line_ids.filtered(
            #     lambda x: x.input_type_id != expense_type)
            # input_lines_vals = [(5, 0, 0)] + [(4, line.id, False)
            #                                   for line in lines_to_keep]
            #
            # input_lines_vals.append((0, 0, {
            #     'amount': loan_total,
            #     'input_type_id': expense_type.id
            # }))
            # rec.update({'input_line_ids': input_lines_vals})
            input_lines_vals = []
            test_loan = 0
            for line in rec.input_line_ids:
                if line.input_type_id.name == expense_type.name:
                    test_loan = 1

            if test_loan == 1:
                for line in rec.input_line_ids:
                    if line.input_type_id.name == expense_type.name:
                        line.amount = loan_total
            else:
                input_lines_vals.append((0, 0, {
                    'amount': loan_total,
                    'input_type_id': expense_type.id
                }))
                rec.write({'input_line_ids': input_lines_vals})

    def _onchange_eos_id(self):
        expense_type = self.env.ref(
            'odt_end_of_service.eos_amount_other_input', raise_if_not_found=False)
        if not expense_type:
            return
        for rec in self:
            employee_id = rec.employee_id.id
            eos_obj = self.env['hr.termination'].search([('employee_id', '=', employee_id), ('state', '=', 'approved2'), ('job_ending_date', '>=', rec.date_from), ('job_ending_date', '<=', rec.date_to), ('is_paid_payslip', '=', False)], limit=1)
            eos_total = 0.0
            if eos_obj:
                if eos_obj.total_deserve:
                    eos_total = eos_obj.total_deserve

            if not eos_total:
                return
            input_lines_vals = []
            test_eos = 0
            for line in rec.input_line_ids:
                if line.input_type_id.name == expense_type.name:
                    test_eos = 1

            if test_eos == 1:
                for line in rec.input_line_ids:
                    if line.input_type_id.name == expense_type.name:
                        line.amount = eos_total
            else:
                input_lines_vals.append((0, 0, {
                    'amount': eos_total,
                    'input_type_id': expense_type.id
                }))
                rec.write({'input_line_ids': input_lines_vals})

    def _onchange_eos_compensate(self):
        expense_type = self.env.ref(
            'odt_end_of_service.eos_compensate_other_input', raise_if_not_found=False)
        if not expense_type:
            return
        for rec in self:
            employee_id = rec.employee_id.id
            eos_obj = self.env['hr.termination'].search([('employee_id', '=', employee_id), ('state', '=', 'approved2'), ('job_ending_date', '>=', rec.date_from), ('job_ending_date', '<=', rec.date_to), ('is_paid_payslip', '=', False)], limit=1)
            eos_total = 0.0
            if eos_obj:
                if eos_obj.compensatory_bonus:
                    eos_total = eos_obj.compensatory_bonus

            if not eos_total:
                return
            input_lines_vals = []
            test_eos = 0
            for line in rec.input_line_ids:
                if line.input_type_id.name == expense_type.name:
                    test_eos = 1

            if test_eos == 1:
                for line in rec.input_line_ids:
                    if line.input_type_id.name == expense_type.name:
                        line.amount = eos_total
            else:
                input_lines_vals.append((0, 0, {
                    'amount': eos_total,
                    'input_type_id': expense_type.id
                }))
                rec.write({'input_line_ids': input_lines_vals})

    def _onchange_eos_leave(self):
        expense_type = self.env.ref(
            'odt_end_of_service.eos_leave_other_input', raise_if_not_found=False)
        if not expense_type:
            return
        for rec in self:
            employee_id = rec.employee_id.id
            eos_obj = self.env['hr.termination'].search([('employee_id', '=', employee_id), ('state', '=', 'approved2'), ('job_ending_date', '>=', rec.date_from), ('job_ending_date', '<=', rec.date_to), ('is_paid_payslip', '=', False)], limit=1)
            eos_total = 0.0
            if eos_obj:
                if eos_obj.deserve_salary_amount:
                    eos_total = eos_obj.deserve_salary_amount

            if not eos_total:
                return
            input_lines_vals = []
            test_eos = 0
            for line in rec.input_line_ids:
                if line.input_type_id.name == expense_type.name:
                    test_eos = 1

            if test_eos == 1:
                for line in rec.input_line_ids:
                    if line.input_type_id.name == expense_type.name:
                        line.amount = eos_total
            else:
                input_lines_vals.append((0, 0, {
                    'amount': eos_total,
                    'input_type_id': expense_type.id
                }))
                rec.write({'input_line_ids': input_lines_vals})

    def _onchange_eos_add(self):
        expense_type = self.env.ref(
            'odt_end_of_service.eos_add_other_input', raise_if_not_found=False)
        if not expense_type:
            return
        for rec in self:
            employee_id = rec.employee_id.id
            eos_obj = self.env['hr.termination'].search([('employee_id', '=', employee_id), ('state', '=', 'approved2'), ('job_ending_date', '>=', rec.date_from), ('job_ending_date', '<=', rec.date_to), ('is_paid_payslip', '=', False)], limit=1)
            eos_total = 0.0
            if eos_obj:
                if eos_obj.add_value:
                    eos_total = eos_obj.add_value

            if not eos_total:
                return
            input_lines_vals = []
            test_eos = 0
            for line in rec.input_line_ids:
                if line.input_type_id.name == expense_type.name:
                    test_eos = 1

            if test_eos == 1:
                for line in rec.input_line_ids:
                    if line.input_type_id.name == expense_type.name:
                        line.amount = eos_total
            else:
                input_lines_vals.append((0, 0, {
                    'amount': eos_total,
                    'input_type_id': expense_type.id
                }))
                rec.write({'input_line_ids': input_lines_vals})

    # @api.multi
    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        loan_obj = self.env['hr.loan']
        loan_line_obj = self.env['hr.loan.line']
        for record in self:
            eos_obj = self.env['hr.termination'].search([('employee_id', '=', record.employee_id.id), ('state', '=', 'approved2'), ('job_ending_date', '>=', record.date_from), ('job_ending_date', '<=', record.date_to), ('is_paid_payslip', '=', False)], limit=1)
            eos_obj.is_paid_payslip = True
            eos_obj.contract_id.is_paid_payslip = True
            loan_ids = loan_obj.search(
                [('employee_id', '=', record.employee_id.id), ('state', '=', 'approved2') ])
            if loan_ids and record.credit_note == False:
                for loan_id in loan_ids:
                    line_ids = loan_line_obj.search([('loan_id', '=', loan_id.id),
                                                     ('paid', '=', False),
                                                     ('discount_date',
                                                      '>=', record.date_from),
                                                     ('discount_date', '<=', record.date_to)])
                    if line_ids:
                        for line in line_ids:
                            line.paid = True
                            line.payslip_id = self
            elif loan_ids and record.credit_note == True:
                for loan_id in loan_ids:
                    line_ids = loan_line_obj.search([('loan_id', '=', loan_id.id),
                                                     ('paid', '=', True),
                                                     ('discount_date',
                                                      '>=', record.date_from),
                                                     ('discount_date', '<=', record.date_to)])
                    if line_ids:
                        for line in line_ids:
                            line.paid = False
        return res


class LoansPayments(models.Model):
    _name = "loan.payments"

    name = fields.Char('Name', required=True, help='Payment name')
    company_id = fields.Many2one(comodel_name="res.company", string="Company")
    debit_account_id = fields.Many2one('account.account', 'Debit Account',
                                       help='Debit account for journal entry')
    credit_account_id = fields.Many2one('account.account', 'Credit Account',
                                        help='Credit account for journal entry')
    analytic_account_id = fields.Many2one('account.analytic.account', 'Analytic Account',
                                          help='Analytic account for journal entry')
    journal_miscellaneous = fields.Boolean(string="Journal Miscellaneous", )
    loan_type = fields.Selection(string="Loan Type", selection=[('loan', 'Loan'), ('install', 'Installment')],
                                 default='loan', required=True)
    other_input_type_id = fields.Many2one('hr.payslip.input.type', string='Other Input Type')

    journal_id = fields.Many2one('account.journal', 'Journal', domain=[('type', 'in', ['general'])],
                                 help='Journal for journal entry', tracking=True)
