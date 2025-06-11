from odoo import api, fields, models, _

class AllowanceType(models.Model):
    _name = 'allowance.type'

    name = fields.Char()
    other_input_type_id = fields.Many2one('hr.payslip.input.type')
    amount = fields.Float()
    description = fields.Text()
    need_to_add_quantity = fields.Boolean()




