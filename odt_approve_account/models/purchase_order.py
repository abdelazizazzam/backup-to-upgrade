from odoo import api, Command, fields, models, _
import json

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"



    def action_create_invoice(self):
        po = super(PurchaseOrder, self).action_create_invoice()
        for order in self:
            activity_id = self.env.ref('odt_approve_account.mail_activity_rfq_notify')
            beneficiary_group = self.env.ref('odt_approve_account.access_approve_group')

            for user in beneficiary_group.users:
                order.activity_schedule(
                    activity_type_id=activity_id.id,
                    summary="Bill created from RFQ",
                    note=f"A new bill has been created from an RFQ: {order.name}",
                    user_id=user.id,
                    date_deadline=fields.Date.context_today(self)  # Set a deadline (today's date by default)
                )
            return po

    def write(self, vals):
        beneficiary_group = self.env.ref('odt_approve_account.access_approve_group')
        purchase_group = self.env.ref('purchase.group_purchase_user')

        activity_id = self.env.ref('odt_approve_account.mail_activity_rfq_notify')
        track_fields = {'product_id', 'product_qty', 'price_unit', 'taxes_id', 'discount', 'analytic_distribution'}


        for order in self:
            modified_lines = []
            if 'order_line' in vals:
                for operation, line_id, line_vals in vals['order_line']:
                    if operation == 1:  # Update existing line
                        line = order.order_line.filtered(lambda l: l.id == line_id)
                        if line:
                            changes = []

                            for field in track_fields:
                                if field in line_vals:
                                    old_value = getattr(line, field, None)
                                    new_value = line_vals[field]

                                    # Special handling for 'analytic_distribution' JSON field
                                    if field == 'analytic_distribution':
                                        if old_value and new_value:
                                            if json.dumps(old_value, sort_keys=True) != json.dumps(new_value,
                                                                                                   sort_keys=True):
                                                old_analytic_names = {
                                                    self.env['account.analytic.account'].browse(int(k)).name: v
                                                    for k, v in old_value.items()
                                                }
                                                new_analytic_names = {
                                                    self.env['account.analytic.account'].browse(int(k)).name: v
                                                    for k, v in new_value.items()
                                                }

                                                changes.append(
                                                    f"(Name: Analytic Distribution) changed From {old_analytic_names} → To {new_analytic_names}")
                                        elif old_value != new_value:
                                            new_analytic_names = {
                                                self.env['account.analytic.account'].browse(int(k)).name: v
                                                for k, v in new_value.items()
                                            }
                                            changes.append(
                                                f"(Name: Analytic Distribution) changed To {new_analytic_names}")

                                    # For all other fields: Show "From → To"
                                    elif old_value != new_value:
                                        changes.append(
                                            f"(Name: {field.replace('_', ' ').title()}) changed From {old_value} → To {new_value}")

                            if changes:
                                modified_lines.append(f"Line {line.product_id.display_name}:\n" + "\n".join(changes))

            if modified_lines:
                users_to_notify = beneficiary_group.users | purchase_group.users
                for user in users_to_notify:
                    order.activity_schedule(
                        activity_type_id=activity_id.id,
                        summary="Purchase Order Line Updated",
                        note="The following changes were made:\n" + "\n".join(modified_lines),
                        user_id=user.id,
                        date_deadline=fields.Date.context_today(self)
                    )

        return super(PurchaseOrder, self).write(vals)