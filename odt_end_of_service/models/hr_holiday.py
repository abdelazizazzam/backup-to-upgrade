# -*- coding: utf-8 -*-


from odoo import models, fields, api, _


class HrHoliday(models.Model):
    _inherit = "hr.leave"

    emp_code = fields.Char(related='employee_id.employee_id', string='Employee Code')


class HrHolidaysStatus(models.Model):
    _inherit = "hr.leave.type"
    is_depend_eos = fields.Boolean('Is depend End of Service.')
