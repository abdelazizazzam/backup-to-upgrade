# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError

class EmployeeAssetExpense(models.Model):
    _inherit = 'hr.custody'

    custody_category = fields.Selection(string="Custody Category", selection=[('section1', 'Section 1'),
                                                                              ('section2', 'Section 2'),
                                                                              ('section3', 'Section 3'),
                                                                              ('section4', 'Section 4'),
                                                                              ('section5', 'Section 5'),
                                                                              ('section6', 'Section 6'),
                                                                              ('section7', 'Section 7'),
                                                                              ('section8', 'Section 8'), ])

    state = fields.Selection(selection_add=[('manager_approve', 'Manager Approval'), ('section_approve', 'Section Approval'),])

    def submit(self):
        self.write({'state': 'manager_approve'})

    def manager_approve(self):
        if self.env.user != self.employee_id.department_id.manager_id.user_id:
            raise UserError(_("You can't take this action, You're not this employee manager"))
        else:
            self.write({'state': 'section_approve'})

    def section_approve(self):
        section_number = self.custody_category[-1]
        aprove_group = f"group_section{section_number}_manager"
        group_dest= 'odt_custody_customization.' + aprove_group
        approvers = []
        for user in self.env['res.users'].search([]):
            if user.has_group(group_dest):
                approvers.append(user)
        if self.env.user not in approvers:
            raise UserError(_("You can't take this action, You're not this Section Manager"))
        else:
            self.write({'state': 'confirm'})


class EmployeeAssetExpense(models.Model):
    _inherit = 'hr.custody.line'

    section = fields.Selection(related='custody_id.custody_category', string='Section')
    custody_line_id = fields.Many2one(comodel_name="hr.clearance", string="Custody", required=False, )
    clearance_id1 = fields.Many2one(comodel_name="hr.clearance", string="Custody", required=False, )
    clearance_id2 = fields.Many2one(comodel_name="hr.clearance", string="Custody", required=False, )
    clearance_id3 = fields.Many2one(comodel_name="hr.clearance", string="Custody", required=False, )
    clearance_id4 = fields.Many2one(comodel_name="hr.clearance", string="Custody", required=False, )
    clearance_id5 = fields.Many2one(comodel_name="hr.clearance", string="Custody", required=False, )
    clearance_id6 = fields.Many2one(comodel_name="hr.clearance", string="Custody", required=False, )
    clearance_id7 = fields.Many2one(comodel_name="hr.clearance", string="Custody", required=False, )
