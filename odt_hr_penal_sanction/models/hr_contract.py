
from odoo import models, fields, api

class HrContract(models.Model):
    _inherit = 'hr.contract'

    on_sanction = fields.Boolean(string="On Sanction",default=False,track_visibility='onchange',  )

