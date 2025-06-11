# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class EmployeeAssetExpense(models.Model):
    _name = 'hr.custody'
    _rec_name = 'employee_id'
    _description = 'New Custody'

    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=True, )
    invoice_id = fields.Many2one(comodel_name="account.move", string="Invoice", required=False, )
    custody_line = fields.One2many(comodel_name="hr.custody.line", inverse_name="custody_id", string="Custody",
                                   required=False, )
    state = fields.Selection(string="Status", selection=[('draft', 'Draft'), ('manager_approve', 'Manager Approval'), ('section_approve', 'Section Approval'), ('confirm', 'Confirm'), ], default='draft',
                             required=False, )

    employee_transfer = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False, )
    custody_transfer = fields.Many2many(comodel_name="hr.custody.line", relation="asset_expense_custody_line",
                                        string="Custody", required=False, )
    custody_reserve = fields.Many2many(comodel_name="hr.custody.line", relation="asset_expense_custody_reserve",
                                       string="Custody", required=False, )
    date_transfer = fields.Date(string="Date", required=False, )
    date_reserve = fields.Date(string="Date", required=False, )



    # def action_confirm(self):
    #     self.write({'state': 'confirm'})

    def action_transfer(self):
        custody_line = self.env['hr.custody.line']
        if self.custody_transfer:
            for line in self.custody_transfer:
                if self.employee_transfer and self.date_transfer:
                    if self.date_transfer < line.date_from:
                        raise UserError(_('You Could not assign date less than delivered date'))
                    custody = self.search([('employee_id', '=', self.employee_transfer.id)])
                    line.write({'date_to': self.date_transfer, 'state_custody': 'transfer'})
                    if custody:
                        vals = {
                            'name': line.name,
                            'custody_id': custody.id,
                            'asset_id': line.asset_id.id,
                            'product_id': line.product_id.id,
                            'type_custody': line.type_custody,
                            'date_from': self.date_transfer,
                            'state_custody': 'deliver',
                        }
                        custody_line.create(vals)
                    else:
                        custody_id = self.create({
                            'employee_id': self.employee_transfer.id,
                        })
                        line.write({'date_to': self.date_transfer, 'state_custody': 'transfer'})
                        vals = {
                            'name': line.name,
                            'custody_id': custody_id.id,
                            'asset_id': line.asset_id.id,
                            'product_id': line.product_id.id,
                            'type_custody': line.type_custody,
                            'date_from': self.date_transfer,
                            'state_custody': 'deliver',
                        }
                        custody_line.create(vals)
        self.employee_transfer = self.custody_transfer = self.date_transfer = False

    def action_reserve(self):
        if self.custody_reserve:
            for line in self.custody_reserve:
                if self.date_reserve:
                    if self.date_reserve < line.date_from:
                        raise UserError(_('You Could not assign date less than delivered date'))
                    line.write({'date_to': self.date_reserve, 'state_custody': 'reserve'})

        self.custody_reserve = self.date_reserve = False


class EmployeeAssetExpenseLine(models.Model):
    _name = 'hr.custody.line'
    _rec_name = 'name'
    _description = 'New Custody Line'

    name = fields.Char(string="Name", required=False, store=True)
    is_not_visible = fields.Boolean(string="Visible", )
    employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee", required=False,
                                  related='custody_id.employee_id', store=True)
    custody_id = fields.Many2one(comodel_name="hr.custody", string="Custody", required=False)
    custody_line_id = fields.Many2one(comodel_name="hr.clearance", string="Custody", required=False, )
    asset_id = fields.Many2one(comodel_name="account.asset", string="Asset", required=False)
    product_id = fields.Many2one(comodel_name="product.product", domain=[('type', '=', 'consu')], string="Expense",
                                 required=False, )
    type_custody = fields.Selection(string="Type",
                                    selection=[('asset', 'Asset'), ('expense', 'Expense'), ('other', 'Other')],
                                    default='asset', required=False, )
    date_from = fields.Date(string="Date From", required=True, )
    date_to = fields.Date(string="Date To", required=False, )
    model = fields.Char(string="Code", required=False, related='asset_id.model', store=True)
    description = fields.Text(string="Description", required=False, related='asset_id.notes', store=True)
    notes = fields.Text(string="Notes", required=False, )
    state_custody = fields.Selection(string="Custody Status", selection=[('sold', 'IS Sold'),
                                                                         ('deliver', 'On Handed'),
                                                                         ('reserve', 'Is Reserved'),
                                                                         ('transfer', 'Is Transfered'),
                                                                         ('scrap', 'Is Scrapped'), ], required=False,
                                     default='deliver')

    @api.onchange('type_custody')
    def _onchange_type_custody(self):
        self.asset_id = False
        self.product_id = False

    @api.model
    def create(self, values):
        res = super(EmployeeAssetExpenseLine, self).create(values)
        if res.product_id:
            products = self.search([('product_id', '=', res.product_id.id), ('state_custody', '=', 'deliver')])
            if len(products) > 1:
                raise UserError(_('You Cannot assign Expense To More Employee'))
            res.name = res.product_id.name
        elif res.asset_id:
            assets = self.search([('asset_id', '=', res.asset_id.id), ('state_custody', '=', 'deliver')])
            if len(assets) > 1:
                raise UserError(_('You Cannot assign Asset To More Employee'))
            res.name = res.asset_id.name
        return res

    def write(self, values):
        if values.get('asset_id'):
            asset = self.env['account.asset'].browse(values.get('asset_id'))
            values['name'] = asset.name
        elif values.get('product_id'):
            product = self.env['product.product'].browse(values.get('product_id'))
            values['name'] = product.name
        return super(EmployeeAssetExpenseLine, self).write(values)

    def create_custody(self):
        for rec in self:
            if not rec.asset_id:
                raise UserError(_("Has Not Asset."))
            custody = self.env['hr.custody'].search([('employee_id', '=', rec.employee_id.id)], limit=1)
            if custody:
                rec.custody_id = custody.id
            else:
                custody_id = self.env['hr.custody'].create({
                    'employee_id': rec.employee_id.id,
                })
                rec.custody_id = custody_id.id
        return True

    @api.model
    def default_get(self, fields):
        rec = super(EmployeeAssetExpenseLine, self).default_get(fields)
        active_id = self._context.get('active_id')

        # Check for selected invoices ids
        if active_id:
            asset_id = self.env['account.asset'].search([('invoice_id', '=', active_id)])
            invoice_id = self.env['account.move'].browse(active_id)
            rec.update({
                'asset_id': asset_id.id,
                'date_from': invoice_id.invoice_date,

            })
        return rec
