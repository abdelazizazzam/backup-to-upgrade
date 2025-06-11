from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError


class AccountMove(models.Model):
    _inherit='account.move'

    employee = fields.Many2one('hr.employee')

    # def read(self, fields=None, load='_classic_read'):

    #     for move in self:
    #         for line in move.line_ids:
    #             line.partner_id = self.employee.address_home_id

    #     return super(AccountMove, self).read(fields=fields, load=load)

class HRPayslip(models.Model):
    _inherit='hr.payslip'

    def update_moves(self):
        slips = self.filtered(lambda x: x.move_id)
        for rec in slips:
            rec.move_id.employee = rec.employee_id
            for line in rec.move_id.line_ids:
                line.partner_id = rec.employee_id.address_home_id
    
    
    def action_payslip_done(self):
        
        res=super(HRPayslip,self).action_payslip_done()
        for rec in self:
            rec.move_id.employee = rec.contract_id.employee_id
            for line in rec.move_id.line_ids:
                line.partner_id = rec.contract_id.employee_id.address_home_id
        return res


