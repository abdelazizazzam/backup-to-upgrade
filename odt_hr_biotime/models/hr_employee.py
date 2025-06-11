from odoo import fields, models, api


class hrEmployee(models.Model):
    _inherit = 'hr.employee'

    zknumber = fields.Char("Number zk" ,  groups="hr.group_hr_user")

    _sql_constraints = [
        (
            "zknumber_uniq",
            "unique(zknumber)",
            "zknumber must be unique across the database!",
        )
    ]
