import base64

from odoo import models, fields, api
from odoo import models, fields, api, _
from datetime import datetime, date, timedelta
from odoo.exceptions import ValidationError
from dateutil import relativedelta



class CRMLead(models.Model):
    _inherit = "crm.lead"

    purchase_order_count = fields.Integer(compute="_compute_purchase_order_count", string="Purchase Count")

    def _compute_purchase_order_count(self):
        for rec in self:
            rec.purchase_order_count = self.env['purchase.order'].search_count([
                ('crm_lead_id', '=', rec.id)])

    def action_create_rfq(self):
        return {
            'name': "RFQ",
            'type': 'ir.actions.act_window',
            'res_model': 'purchase.order',
            'target': 'current',
            'views': [[False, 'form']],
            'context': {
                'default_crm_lead_id': self.id,
            },
        }


    def unlink(self):
        for lead in self:
            purchase_orders = self.env['purchase.order'].search_count([('crm_lead_id', '=', lead.id)])
            if purchase_orders:
                raise ValidationError(_('You cannot delete a lead/opportunity with existing purchase orders.'))
        return super(CRMLead, self).unlink()

    def action_view_purchase_orders(self):
        self.ensure_one()
        source_orders = self.env['purchase.order'].search([('crm_lead_id', '=', self.id)])
        result = self.env['ir.actions.act_window']._for_xml_id('purchase.purchase_form_action')
        if len(source_orders) > 1:
            result['domain'] = [('id', 'in', source_orders.ids)]
        elif len(source_orders) == 1:
            result['views'] = [(self.env.ref('purchase.purchase_order_form', False).id, 'form')]
            result['res_id'] = source_orders.id
        else:
            result = {'type': 'ir.actions.act_window_close'}
        return result

    def activity_done(self):
        for rec in self.activity_ids:
            rec.action_done()

    @api.model
    def create(self, vals):
        lead = super(CRMLead, self).create(vals)

        # # Send a log (for instance, to the current user)
        # lead.message_post(

        user_id = lead.user_id if lead.user_id else False
        activity_id = self.env.ref('odt_crm_purchase.mail_activity_crm_lead_notify')

        if user_id:
            lead.activity_schedule(
                activity_type_id=activity_id.id,
                summary="Lead created",
                note=f"A new lead has been created: {lead.name}",
                user_id=user_id.id,
                date_deadline=fields.Date.context_today(self)  # Set a deadline (today's date by default)
            )
        return lead

    def write(self, vals):
        if 'stage_id' in vals:
            for lead in self:
                activity_id = self.env.ref('odt_crm_purchase.mail_activity_crm_lead_notify')
                user_id = lead.user_id if lead.user_id else False

                stage = self.env['crm.stage'].browse(vals.get('stage_id'))

                if user_id and stage:
                    # Schedule an activity
                    lead.activity_schedule(
                        activity_type_id=activity_id.id,  # Type of activity, e.g., To-Do
                        summary="Lead stage updated",
                        note=f"The lead stage has been changed to: {stage.name}",
                        user_id=user_id.id,  # Assign to the current user or specify a different user ID
                        date_deadline=fields.Date.context_today(self)  # Set a deadline (today's date by default)
                    )
        return super(CRMLead, self).write(vals)
