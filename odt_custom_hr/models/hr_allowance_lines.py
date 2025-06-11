from odoo import fields, models, api


class AllowanceLines(models.Model):
    _name = "hr.allowance.lines"

    allowance_line_ids = fields.Many2one("hr.contract")

    housing_allowance_type = fields.Char(compute="_get_housing_rule")
    date = fields.Date("Date")
    amount = fields.Float(
        "Amount",
    )
    status = fields.Selection(
        [("paid", "Paid"), ("unpaid", "Not Paid")], default="unpaid"
    )


    def make_paid(self):
        self.status = "paid"

    def _get_housing_rule(self):
        for rec in self:
            rec.housing_allowance_type = rec.allowance_line_ids.housing_rule