# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class SaveSettingsFields(models.Model):
    _inherit = 'res.company'

    epx_notification = fields.Selection(string="Document Expiry Notification To:", selection=[('employee', 'Employee Him/Herself'), ('hr', 'HR Employee'), ], required=False, )
    hr_employee = fields.Many2one(comodel_name="hr.employee", string="HR Employee", required=False, )

class SettingsFields(models.TransientModel):
    _inherit = 'res.config.settings'
    _description = 'Updated Employees Module'

    portal_allow_api_keys = fields.Char()
    epx_notification = fields.Selection(related='company_id.epx_notification', string="Document Expiry Notification To:", readonly=False)
    hr_employee = fields.Many2one(comodel_name="hr.employee", related='company_id.hr_employee', string="HR Employee", readonly=False)