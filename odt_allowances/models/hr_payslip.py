from odoo import api, fields, models, _


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'


    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee_allowance(self):
        self._onchange_allowance()
        # self._onchange_employee()

    def _onchange_allowance(self):
        for rec in self:
            rec.write({'input_line_ids': [(5, 0, 0)]})
            allowance_obj = self.env['hr.allowance']
            employee_id = rec.employee_id.id
            allowance_ids = allowance_obj.search(
                [('employee_id', '=', employee_id),
                 ('state', '=', 'approved'),
                 ('date', '>=', rec.date_from),
                 ('date', '<=', rec.date_to)
                 ])


            if allowance_ids:
                allowance_types = allowance_ids.mapped('allowance_type_id')
                input_lines_vals = []
                for type in allowance_types:
                    allowance_total = sum([(allowance.quantity * allowance.allowance_type_id.amount) if allowance.allowance_type_id == type else 0 for allowance in allowance_ids])

                    input_lines_vals.append((0, 0, {
                        'amount': allowance_total,
                        'input_type_id': type.other_input_type_id.id
                    }))
                rec.write({'input_line_ids': input_lines_vals})
