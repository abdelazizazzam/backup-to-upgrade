from odoo import api, fields, models, _, exceptions


class HrJob(models.Model):
    _inherit = 'hr.job'

    job_code = fields.Char(string="Code")

    @api.constrains('job_code')
    def _check_code_unique(self):
        code_counts = self.search_count([('job_code', '=', self.job_code), ('id', '!=', self.id)])
        if code_counts > 0:
            raise exceptions.ValidationError("Code must be unique!")