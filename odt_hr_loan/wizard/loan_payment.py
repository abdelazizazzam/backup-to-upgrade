# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from datetime import datetime, timedelta
from odoo.exceptions import UserError
import time


class LoanPAyment(models.TransientModel):
    _name = 'hr.loan.payment'

    @api.model
    def _get_name(self):
        context = dict(self._context or {})
        active_id = context.get('active_id', False)
        if active_id:
            loan = self.env['hr.loan'].browse(active_id)
            return loan.name
        return ''

    name = fields.Char('Loan', default=_get_name)
    amount = fields.Float('Amount', required=True)
    journal_id = fields.Many2one('account.journal', 'Journal', domain=[('type', 'in', ['bank', 'cash'])],
                                 help='Journal for journal entry')
    payment_method = fields.Many2one(
        'loan.payments', 'Payment Method', help='Payment method for loan')

    @api.onchange('amount')
    def _onchange_amount(self):
        context = dict(self._context or {})
        if self.amount:
            active_id = context.get('active_id', False)
            loan = self.env['hr.loan'].browse(active_id)
            if self.amount > loan.amount:
                self.amount = False
                raise UserError(_('Incorrect Amount'))

    # @api.one
    def create_payment(self):
        loan_id = self._context.get('active_id', False)
        amount = self.amount
        loan = self.env['hr.loan'].browse(loan_id)
        if self.amount:
            if self.amount > loan.amount:
                self.amount = False
                raise UserError(_('Amount will not greater than loan amount'))
        if loan_id:
            loan_line_ids = self.env['hr.loan.line'].search([('loan_id', '=', loan_id), ('paid', '=', False)],
                                                            order='discount_date')
            for line in loan_line_ids:
                if amount:
                    if line.amount <= amount:
                        line.write({'paid': True})
                        amount -= line.amount
                    else:
                        line.copy({'amount': amount, 'paid': True})
                        line.write({'amount': line.amount - amount})
                        amount -= amount
            if self.payment_method and self.journal_id:
                move_obj = self.env['account.move']
                today = fields.date.today()

                line_ids = []
                # prepare account move data
                name = _('Payment for ') + self.name
                move = {
                    'narration': name,
                    'move_type': 'entry',
                    'ref': loan.name or 'Loan',
                    'loan_id': loan.id,
                    'date': today,
                    'journal_id': self.journal_id.id,
                }

                amount = self.amount
                debit_account_id = self.journal_id.default_account_id.id or False
                credit_account_id = self.payment_method.credit_account_id.id or False
                analytic_account_id = self.payment_method.analytic_account_id.id or False
                if amount <= 0:
                    raise UserError(_('Please Set Amount'))

                if not self.journal_id:
                    raise UserError(_('Please Set Journal'))

                if not credit_account_id or not debit_account_id:
                    raise UserError(_('Please Set credit/debit account '))
                partner_id = loan.employee_id.address_home_id.id if loan.employee_id.address_home_id else False
                if debit_account_id:
                    debit_line = (0, 0, {
                        'name': 'Loan',
                        'date': today,
                        'partner_id': partner_id,
                        'account_id': debit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': amount,
                        'credit': 0.00,
                        'analytic_account_id': analytic_account_id,
                    })
                    line_ids.append(debit_line)

                if credit_account_id:
                    credit_line = (0, 0, {
                        'name': 'Loan',
                        'date': today,
                        'partner_id': partner_id,
                        'account_id': credit_account_id,
                        'journal_id': self.journal_id.id,
                        'debit': 0.0,
                        'credit': amount,
                        'analytic_account_id': False,
                    })
                    line_ids.append(credit_line)

                    move.update({'line_ids': line_ids})
                    move_id = move_obj.create(move)
                    move_id.post()
                    move_ids = [move_id.id]
                    for move_rec in loan.move_ids:
                        move_ids.append(move_rec.id)
                    loan.write(
                    {'move_ids': [(6, 0, move_ids)]})
        return True
