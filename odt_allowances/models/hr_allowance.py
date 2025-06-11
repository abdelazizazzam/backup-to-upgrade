from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
import json
from datetime import date


class Allowance(models.Model):
    _name = 'hr.allowance'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    def get_emp(self):
        user = self.env.user.id
        result = self.env['hr.employee'].search([('user_id.id', '=', user)])
        return result

    # employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True,
    #                               default=lambda self: self.get_emp(), store=True)
    employee_id = fields.Many2one(comodel_name='hr.employee', string='Employee', required=True,
                                  tracking=True, default=lambda self: self.env.user.employee_id)
    employee_id_domain = fields.Char(
        compute="_compute_employee_id_domain",
        readonly=True,
        store=False,
    )
    name = fields.Char('Name', default='NEW', readonly=True)
    transaction_date = fields.Date('Transaction Date', readonly=True, default=lambda self: date.today())

    @api.depends('employee_id')
    def _compute_employee_id_domain(self):
        for rec in self:
            # rec = rec._origin
            if self.env.user.has_group('hr.group_hr_manager'):
                items = self.env['hr.employee'].search([])
                rec.employee_id_domain = json.dumps([(('id', 'in', items.ids))])
            else:
                items = self.env['hr.employee'].search([('user_id', '=', rec.env.user.id)])
                rec.employee_id_domain = json.dumps(
                    [('id', 'in', items.ids)]
                )

    allowance_type_id = fields.Many2one('allowance.type',tracking=True)
    need_to_add_quantity = fields.Boolean(related='allowance_type_id.need_to_add_quantity')
    quantity = fields.Integer(default='1',tracking=True)
    date = fields.Date(required=True,tracking=True)
    description = fields.Text()

    state = fields.Selection(
        [
            ('draft', 'Draft'),
            ('to_approve', 'Waiting For Approval'),
            ('hr_department', 'HR Approved'),
            ('approved', 'Approved'),
            ('rejected', 'Refused')
        ],
        'Status', default='draft', tracking=True)

    @api.constrains('description')
    def chatt(self):
        self.message_post(body=f"Description Updated -> {self.description}")

    # ####### approver #############
    def activity_done(self):
        for rec in self.activity_ids:
            rec.action_done()

    def sent(self):
        self.activity_done()
        # Sending Notification TO manager
        parent_id = self.employee_id.parent_id.user_id
        # coach_id = employee.coach_id.user_id
        # manager = self.sudo().employee_id.allowance_manager_id
        if parent_id:
            self.activity_schedule(
                activity_type_id=self.env.ref('odt_allowances.mail_activity_allowance_request').id,
                summary=_('New Allowance Request Needs Approve'), user_id=parent_id.id)
            self.message_subscribe(partner_ids=[parent_id.id])
        self.state = 'to_approve'

    def approve_direct_manager(self):
        if self.env.user != self.employee_id.parent_id.user_id:
            raise UserError(_("Only Employee Manager can approve ."))
        self.state = 'hr_department'
        for user in self.env['res.users'].search([]):
            if user.has_group('hr.group_hr_user'):
                self.activity_schedule(
                    activity_type_id=self.env.ref('odt_allowances.mail_activity_allowance_request').id,
                    summary=_('Review Allowance Request'), user_id=user.id)
                self.message_subscribe(partner_ids=[user.id])

        self.activity_done()

    def hr_department_button(self):
        self.state = 'approved'
        self.activity_done()

    def refuse(self):
        self.state = 'rejected'
        self.activity_done()

    def refuse_manager(self):
        if self.env.user != self.employee_id.parent_id.user_id:
            raise UserError(_("Only Employee Manager can Reject ."))
        self.state = 'rejected'
        self.activity_done()

    def set_to_draft(self):
        self.state = 'draft'
        self.activity_done()

    # ####### approver #############

    def name_get(self):
        result = []
        for rec in self:
            employee_id = rec.employee_id
            allowance_type_id = rec.allowance_type_id
            result.append((rec.id, _("%s : %s ( %s )") % (
                employee_id.name or employee_id, allowance_type_id.name or allowance_type_id, rec.date or " ")))
        return result

    @api.onchange('allowance_type_id')
    def set_qtytozero(self):
        self.quantity = 1

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('allowances_sequence_code') or 'NEW'
        return super(Allowance, self).create(vals)

    def unlink(self):
        for record in self:
            if record.env.user.has_group('base.group_user'):
                raise UserError(_('You cannot remove the record has group User in HR!'))
        return super(Allowance, self).unlink()
