from odoo import models, api, fields, Command
import logging
_logger = logging.getLogger(__name__)


class PayslipOverTime(models.Model):
    _inherit = 'hr.payslip'

    overtime_ids = fields.Many2many('hr.overtime')


    # ########################## to call compute input line ids ##############
    @api.onchange('employee_id', 'struct_id', 'contract_id', 'date_from', 'date_to')
    def _onchange_employee_overtime(self):
        self._calc_overtime()
    # ########################## to call compute input line ids ##############
    def _calc_overtime(self):
        input_data = []
        overtime_type = self.env.ref('ent_ohrms_overtime.hr_salary_rule_overtime')
        overtime_input_type = self.env.ref('ent_ohrms_overtime.input_overtime_payroll')

        contract = self.contract_id
        overtime_id = self.env['hr.overtime'].search([('employee_id', '=', self.employee_id.id),
                                                      ('contract_id', '=', self.contract_id.id),
                                                      ('state', '=', 'approved'),('date', '<=', self.date_to),
                                                      ('payslip_paid', '=', False)])

        hrs_amount = overtime_id.mapped('cash_hrs_amount')
        day_amount = overtime_id.mapped('cash_day_amount')
        cash_amount = sum(hrs_amount) + sum(day_amount)
        old_input_rec = self.input_line_ids.filtered(lambda r: r.input_type_id.id == overtime_input_type.id)

        if old_input_rec:
            for rec in old_input_rec:
                self.input_line_ids = [(2, rec.id, 0)]

        if overtime_id and self.struct_id and cash_amount > 0:
            self.overtime_ids = overtime_id

            input_data.append((0, 0, {
                'name': overtime_type.name,
                'amount': cash_amount,
                'input_type_id': overtime_input_type.id if overtime_input_type else 1
            }))
            # input_data = {
            #     'name': overtime_type.name,
            #     'code': overtime_type.code,
            #     'amount': cash_amount,
            #     'contract_id': contract.id,
            #     'input_type_id': self.env.ref('ent_ohrms_overtime.input_overtime_payroll').id if self.env.
            #     ref('ent_ohrms_overtime.input_overtime_payroll').id else 1
            # }
            # res.append(input_data)

            self.update({'input_line_ids': input_data})

    @api.model_create_multi
    def create(self, vals_list):
        payslips = super().create(vals_list)
        draft_slips = payslips.filtered(lambda p: p.employee_id and p.state == 'draft')
        for slip in draft_slips:
            slip._onchange_employee()
        return payslips

    # ####################base module #######################################################
    # @api.model
    # def _compute_input_line_ids(self):
    #     print("enter::::::::::::")
    #     """
    #     function used for writing overtime record in payslip
    #     input tree.
    #
    #     """
    #     input_data = []
    #     res = super(PayslipOverTime, self)._compute_input_line_ids()
    #     overtime_type = self.env.ref('ent_ohrms_overtime.hr_salary_rule_overtime')
    #     overtime_input_type = self.env.ref('ent_ohrms_overtime.input_overtime_payroll')
    #     print("overtime_type::", overtime_type)
    #     print("overtime_input_type::", overtime_input_type)
    #
    #     contract = self.contract_id
    #     overtime_id = self.env['hr.overtime'].search([('employee_id', '=', self.employee_id.id),
    #                                                   ('contract_id', '=', self.contract_id.id),
    #                                                   ('state', '=', 'approved'),
    #                                                   ('payslip_paid', '=', False)])
    #     print("overtime_id::", overtime_id)
    #
    #     hrs_amount = overtime_id.mapped('cash_hrs_amount')
    #     day_amount = overtime_id.mapped('cash_day_amount')
    #     cash_amount = sum(hrs_amount) + sum(day_amount)
    #     print("cash_amount::", cash_amount)
    #     old_input_rec = self.input_line_ids.filtered(lambda r: r.input_type_id.id == overtime_input_type.id)
    #
    #     if old_input_rec:
    #         print("old_input_rec",old_input_rec)
    #         for rec in old_input_rec:
    #             self.input_line_ids = [(2, rec.id, 0)]
    #
    #     print("overtime_id::", overtime_id)
    #     print("self.struct_id::", self.struct_id)
    #     print("overtime_input_type::", overtime_input_type)
    #     print("self.struct_id.input_line_type_ids::", self.struct_id.input_line_type_ids)
    #
    #     if overtime_id and self.struct_id and overtime_input_type in self.struct_id.input_line_type_ids:
    #         self.overtime_ids = overtime_id
    #         input_data.append(Command.create({
    #             'name': overtime_type.name,
    #             'amount': cash_amount,
    #             'input_type_id': overtime_input_type.id if overtime_input_type else 1
    #         }))
    #         # input_data = {
    #         #     'name': overtime_type.name,
    #         #     'code': overtime_type.code,
    #         #     'amount': cash_amount,
    #         #     'contract_id': contract.id,
    #         #     'input_type_id': self.env.ref('ent_ohrms_overtime.input_overtime_payroll').id if self.env.
    #         #     ref('ent_ohrms_overtime.input_overtime_payroll').id else 1
    #         # }
    #         # res.append(input_data)
    #         print("input_data::", input_data)
    #         self.update({'input_line_ids': input_data})
    #     return res

    def action_payslip_done(self):
        """
        function used for marking paid overtime
        request.

        """
        for recd in self.overtime_ids:
            if recd.type == 'cash':
                recd.payslip_paid = True
        return super(PayslipOverTime, self).action_payslip_done()
