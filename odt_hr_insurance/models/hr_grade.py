from odoo import fields, models


class Grade(models.Model):
    _inherit = 'hr.grade'

    medical_insurance_id = fields.Many2one('insurance.categ', 'Medical Insurance Category')
