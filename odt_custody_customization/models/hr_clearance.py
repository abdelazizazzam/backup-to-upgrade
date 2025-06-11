# -*- coding: utf-8 -*-

from odoo import models, fields, api


class EmployeeAssetExpense(models.Model):
    _inherit = 'hr.clearance'

    is_custody1 = fields.Boolean(default=False, )
    is_custody2 = fields.Boolean(default=False, )
    is_custody3 = fields.Boolean(default=False, )
    is_custody4 = fields.Boolean(default=False, )
    is_custody5 = fields.Boolean(default=False, )
    is_custody6 = fields.Boolean(default=False, )
    is_custody7 = fields.Boolean(default=False, )
    is_custody8 = fields.Boolean(default=False, )
    custody_line_ids1 = fields.One2many('hr.custody.line', 'clearance_id1', 'Employee Custody', )
    custody_line_ids2 = fields.One2many('hr.custody.line', 'clearance_id2', 'Employee Custody', )
    custody_line_ids3 = fields.One2many('hr.custody.line', 'clearance_id3', 'Employee Custody', )
    custody_line_ids4 = fields.One2many('hr.custody.line', 'clearance_id4', 'Employee Custody', )
    custody_line_ids5 = fields.One2many('hr.custody.line', 'clearance_id5', 'Employee Custody', )
    custody_line_ids6 = fields.One2many('hr.custody.line', 'clearance_id6', 'Employee Custody', )
    custody_line_ids7 = fields.One2many('hr.custody.line', 'clearance_id7', 'Employee Custody', )

    def action_section1(self):
        self.is_custody1 = True
        self._onchange_is_custody()

    def action_section2(self):
        self.is_custody2 = True
        self._onchange_is_custody()

    def action_section3(self):
        self.is_custody3 = True
        self._onchange_is_custody()

    def action_section4(self):
        self.is_custody4 = True
        self._onchange_is_custody()

    def action_section5(self):
        self.is_custody5 = True
        self._onchange_is_custody()

    def action_section6(self):
        self.is_custody6 = True
        self._onchange_is_custody()

    def action_section7(self):
        self.is_custody7 = True
        self._onchange_is_custody()

    def action_section8(self):
        self.is_custody8 = True
        self._onchange_is_custody()

    @api.onchange('is_custody1', 'is_custody2', 'is_custody3', 'is_custody4', 'is_custody5', 'is_custody6',
                  'is_custody7')
    def _onchange_is_custody(self):
        if self.is_custody1 and self.is_custody2 and self.is_custody3 and self.is_custody4 and self.is_custody5 and self.is_custody6 and self.is_custody7 and self.is_custody8:
            self.update({'state': 'done'})

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        self.custody_line_ids1 = False
        self.custody_line_ids2 = False
        self.custody_line_ids3 = False
        self.custody_line_ids4 = False
        self.custody_line_ids5 = False
        self.custody_line_ids6 = False
        self.custody_line_ids7 = False
        self.custody_ids = False
        list1 = []
        list2 = []
        list3 = []
        list4 = []
        list5 = []
        list6 = []
        list7 = []
        list8 = []
        employees = self.env['hr.custody'].search([('employee_id', '=', self.employee_id.id)])
        for employee in employees:
            if employee.custody_category == 'section1':
                print('bgdfg')
                for line in employee.custody_line:
                    vals= {'type_custody':line.type_custody,
                           'asset_id': line.asset_id.id,
                           'product_id': line.product_id.id,
                           'state_custody': line.state_custody,
                          }
                    list1.append((0,0,vals))
            elif employee.custody_category == 'section2':
                for line in employee.custody_line:
                    vals = {'type_custody': line.type_custody,
                            'asset_id': line.asset_id.id,
                            'product_id': line.product_id.id,
                            'state_custody': line.state_custody,
                            }
                    list2.append((0, 0, vals))
            elif employee.custody_category == 'section3':
                for line in employee.custody_line:
                    vals = {'type_custody': line.type_custody,
                            'asset_id': line.asset_id.id,
                            'product_id': line.product_id.id,
                            'state_custody': line.state_custody,
                            }
                    list3.append((0, 0, vals))
            elif employee.custody_category == 'section4':
                for line in employee.custody_line:
                    vals = {'type_custody': line.type_custody,
                            'asset_id': line.asset_id.id,
                            'product_id': line.product_id.id,
                            'state_custody': line.state_custody,
                            }
                    list4.append((0, 0, vals))
            elif employee.custody_category == 'section5':
                for line in employee.custody_line:
                    vals = {'type_custody': line.type_custody,
                            'asset_id': line.asset_id.id,
                            'product_id': line.product_id.id,
                            'state_custody': line.state_custody,
                            }
                    list5.append((0, 0, vals))
            elif employee.custody_category == 'section6':
                for line in employee.custody_line:
                    vals = {'type_custody': line.type_custody,
                            'asset_id': line.asset_id.id,
                            'product_id': line.product_id.id,
                            'state_custody': line.state_custody,
                            }
                    list6.append((0, 0, vals))
            elif employee.custody_category == 'section7':
                for line in employee.custody_line:
                    vals = {'type_custody': line.type_custody,
                            'asset_id': line.asset_id.id,
                            'product_id': line.product_id.id,
                            'state_custody': line.state_custody,
                            }
                    list7.append((0, 0, vals))
            elif employee.custody_category == 'section8':
                for line in employee.custody_line:
                    vals = {'type_custody': line.type_custody,
                            'asset_id': line.asset_id.id,
                            'product_id': line.product_id.id,
                            'state_custody': line.state_custody,
                            }
                    list8.append((0, 0, vals))
        self.custody_line_ids1 = list1
        self.custody_line_ids2 = list2
        self.custody_line_ids3 = list3
        self.custody_line_ids4 = list4
        self.custody_line_ids5 = list5
        self.custody_line_ids6 = list6
        self.custody_line_ids7 = list7
        self.custody_ids = list8

