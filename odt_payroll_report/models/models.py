from odoo import api, fields, models,_
from datetime import date
from odoo.exceptions import UserError
import dateutil.parser
from datetime import date


class PAyroll(models.Model):
    _inherit = 'hr.payslip'

    def action_print_payslip_report(self) :
        return self.env.ref('odt_payroll_report.report_payroll_employee').report_action(self)

class ResCompany(models.Model):
    _inherit = "res.company"

    footer = fields.Binary('Footer')

    