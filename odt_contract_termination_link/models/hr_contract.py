# -*- coding: utf-8 -*-

import time
from odoo import models, fields, api, _


class HrContract(models.Model):
    _inherit = "hr.contract"

    end_of_service = fields.Date('Original End Date')
    is_terminated = fields.Boolean('Terminated')
    is_paid_payslip = fields.Boolean('Is Paid Payslip for Termination')
    trial_date_start = fields.Date()
    working_hours = fields.Float()