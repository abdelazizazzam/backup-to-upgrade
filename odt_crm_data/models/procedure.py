from odoo import models, fields, api


class Procedure(models.Model):
    _name = 'procedure'

    name = fields.Char(required=True, string="Name")
    code = fields.Char(string="Code")