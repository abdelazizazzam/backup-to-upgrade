
from odoo import models, fields, api

class AccountMove(models.Model):
    _inherit = 'account.move'

    state = fields.Selection(
        selection=[
            ('draft', 'Draft'),
            ('approve', 'Approval'),
            ('posted', 'Posted'),
            ('cancel', 'Cancelled'),
        ],
        string='Status',
        required=True,
        readonly=True,
        copy=False,
        tracking=True,
        default='draft',
    )

    def action_approve(self):
        self.state = 'approve'

        activity_id = self.env.ref('odt_approve_account.mail_activity_am_new_approve_notify')
        for user in self.env['res.users'].search([]):
            if user.has_group('odt_approve_account.access_approve_group'):
                self.activity_schedule(
                    activity_type_id=activity_id.id,
                    summary="Invoice is Approved",
                    note=f"Invoice is Approved: {self.name}",
                    user_id=user.id,
                    date_deadline=fields.Date.context_today(self)  # Set a deadline (today's date by default)
                )

