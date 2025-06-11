# -*- coding: utf-8 -*-
from odoo import Command, models, fields, api, _

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    @api.model
    def create(self, vals):
        payment = super(AccountPayment, self).create(vals)

        if payment.payment_type == 'outbound':
            activity_id = self.env.ref('odt_approve_account.mail_activity_payment_notify')

            for user in self.env['res.users'].search([]):
                if user.has_group('odt_approve_account.access_approve_group'):
                    payment.activity_schedule(
                        activity_type_id=activity_id.id,
                        summary="Register Payment created",
                        note=f"A new Register Payment has been created from Vendor Bill: {payment.ref}",
                        user_id=user.id,
                        date_deadline=fields.Date.context_today(payment)  # Set a deadline (today's date by default)
                    )

        return payment