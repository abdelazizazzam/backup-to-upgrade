from odoo import api, fields, models, _
from odoo.exceptions import UserError
import json


class AddDeleteInsurance(models.Model):
    _name = 'insurance.add.delete'
    _description = 'Add or Delete insurance from employee'
    _rec_name = 'emp_id'
    _order = 'id desc'

    code = fields.Char(string='رقم الطلب', readonly=True, copy=False)
    emp_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True,
                             states={'cancel': [('readonly', True)], 'done': [('readonly', True)],
                                     'open': [('readonly', True)]})
    insurance_policy = fields.Many2one(comodel_name="insurance.policy", string="Insurance Policy", required=True, domain=[('state', '=', 'active')])
    request_type = fields.Selection(string="Request Type", selection=[('add', 'Add'), ('delete', 'Delete')],
                                    required=True,
                               states={'cancel': [('readonly', True)], 'done': [('readonly', True)],
                                       'open': [('readonly', True)]})
    request_date = fields.Date(string="Request Date", required=True, default=fields.Date.context_today,
                               states={'cancel': [('readonly', True)], 'done': [('readonly', True)]})
    sending_date = fields.Date(string="Sending Date", required=True, default=fields.Date.context_today,
                               states={'cancel': [('readonly', True)], 'done': [('readonly', True)],
                                       'open': [('readonly', True)]})
    dependent_ids = fields.Many2many("dependent", string="Dependents")
    is_dependent = fields.Boolean('Dependent', states={'cancel': [('readonly', True)], 'done': [('readonly', True)],
                                                       'open': [('readonly', True)]})
    medical_insurance_id_domain = fields.Char(compute="_medical_insurance_id_domain", readonly=True, store=False,)
    medical_insurance_id = fields.Many2one('insurance.categ', string='Medical Category', domain=medical_insurance_id_domain)
    state = fields.Selection([
        ('draft', 'Unsent'), ('cancel', 'Cancelled'),
        ('open', 'Requested'), ('done', 'Added')],
        string='Status', default='draft', readonly=True, copy=False)

    @api.depends('insurance_policy')
    def _medical_insurance_id_domain(self):
        for rec in self:
            domain_ids = []
            for line in rec.insurance_policy.insurance_pricing_ids:
                domain_ids.append(line.insurance_categ_id.id)
            rec.medical_insurance_id_domain = json.dumps([('id', 'in', domain_ids)])

    def action_request(self):
        add_for_emp = self.env['insurance.add.delete'].search([('emp_id','=',self.emp_id.id),('request_type','=','add'),('state','=','done')])
        delete_for_emp = self.env['insurance.add.delete'].search([('emp_id','=',self.emp_id.id),('request_type','=','delete'),('state','=','done')])
        diff = len(add_for_emp) - len(delete_for_emp)
        print(diff)
        if self.request_type == 'delete' and diff <= 0:
            raise UserError('This Employee Does not have a running Insurance')
        if self.request_type == 'add' and diff >= 1:
            raise UserError('This Employee already has running Insurance')
        if self.insurance_policy.policy_start_date <= self.request_date and self.insurance_policy.policy_end_date >= self.request_date:
            self.state = 'open'
        else:
            raise UserError('Request Date is out of the chosen Insurance Policy range')

    def action_cancel(self):
        self.state = 'cancel'

    def action_confirm(self):
        for res in self:
            res.state = 'done'
            res.code = self.env['ir.sequence'].next_by_code('add.number')
            if res.dependent_ids and res.request_type == 'add' and res.is_dependent:
                res.emp_id.has_insurance = True
                res.emp_id.last_add_insurance = res.request_date
                res.emp_id.last_medical_insurance_id = res.medical_insurance_id.id

                for rec in res.dependent_ids:
                    rec.has_insurance = True
                    rec.last_add_insurance = res.request_date

            elif res.request_type == 'add' and not res.is_dependent:

                res.emp_id.has_insurance = True
                res.emp_id.last_medical_insurance_id = res.medical_insurance_id.id
                res.emp_id.last_add_insurance = res.request_date

            elif res.dependent_ids and res.request_type == 'delete' and res.is_dependent:

                if not res.emp_id.has_insurance:
                    raise UserError(
                        _('No Insurance for this Employee'))
                res.emp_id.has_insurance = False
                res.emp_id.last_delete_insurance = res.request_date
                for rec in res.dependent_ids:
                    rec.has_insurance = False
                    rec.last_delete_insurance = res.request_date
            elif res.request_type == 'delete' and not res.is_dependent:
                if not res.emp_id.has_insurance:
                    raise UserError(
                        _('No Insurance for this Employee'))
                else:
                    if res.emp_id.dependent_ids:
                        for rec in res.emp_id.dependent_ids:
                            rec.has_insurance = False
                            rec.last_delete_insurance = res.request_date
                    res.emp_id.has_insurance = False
                    res.emp_id.last_delete_insurance = res.request_date

    def set_draft(self):
        self.state = 'draft'

    @api.onchange('emp_id')
    def _compute_medical_category(self):
        for rec in self:
            if rec.medical_insurance_id:
                continue
            if rec.emp_id.last_medical_insurance_id:
                rec.medical_insurance_id = rec.emp_id.last_medical_insurance_id.id

                continue
            else:

                rec.medical_insurance_id = False

    @api.onchange('emp_id', 'request_date')
    def _compute_policy(self):
        for rec in self:
            if rec.insurance_policy:
                insurance = rec.insurance_policy
            else:

                insurance = self.env['insurance.policy'].search(
                    [('policy_start_date', '<=', rec.request_date), ('policy_end_date', '>=', rec.request_date)],
                    limit=1)

            if insurance:

                rec.insurance_policy = insurance.id

    # https://www.odoo.com/forum/help-1/change-the-domain-of-a-many2one-field-depending-on-other-field-value-160477
    @api.onchange('request_type', 'emp_id')
    def onchange_request_type(self):
        self.write({
            'dependent_ids': [(5, 0, 0)]
        })
        if self.emp_id.dependent_ids:
            if self.request_type == 'add':
                self.write({'dependent_ids': [(4, x.id) for x in self.emp_id.dependent_ids if not x.has_insurance]})
            elif self.request_type == 'delete':
                self.write({'dependent_ids': [(4, x.id) for x in self.emp_id.dependent_ids if x.has_insurance]})
