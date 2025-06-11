from odoo import api, fields, models, _

class AccountMove(models.Model):
    _inherit = "account.move"

    inv_pro_name = fields.Char(string='Individual/ Project name')
    type_inv_pro_name = fields.Selection([
        ('individual', 'Individual'),
        ('project', 'Project')
    ], string="Type")

    # def action_register_payment(self):
    #     res = super(AccountMove, self).action_register_payment()
    #
    #     for move in self:
    #         user_id = move.partner_id.user_id if move.partner_id else False
    #         activity_id = self.env.ref('odt_crm_purchase.mail_activity_am_notify')
    #
    #         if user_id:
    #             self.activity_schedule(
    #                 activity_type_id=activity_id.id,
    #                 summary="Register Payment created",
    #                 note=f"A new Register Payment has been created from Vendor Bill: {move.name}",
    #                 user_id=user_id.id,
    #                 date_deadline=fields.Date.context_today(move)  # Set a deadline (today's date by default)
    #             )
    #         return res