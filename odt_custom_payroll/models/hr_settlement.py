from odoo import _, api, fields, models
from odoo.exceptions import AccessError
from datetime import date, timedelta, datetime
from dateutil.relativedelta import relativedelta


class HrSettlement(models.Model):
    _name = "hr.settlement"
    _description = "A model for Employee settlement to be used in payslips"
    _rec_name = "transaction_date"

    name = fields.Char(default="New")
    date_from = fields.Date(
        string='From', readonly=False, required=True,
        default=lambda self: fields.Date.to_string(date.today().replace(day=1)), )
    # states={'done': [('readonly', True)], 'paid': [('readonly', True)], 'cancel': [('readonly', True)]})
    date_to = fields.Date(
        string='To', readonly=False, required=True,
        precompute=True, compute="_compute_date_to", store=True, )
    # states={'done': [('readonly', True)], 'paid': [('readonly', True)], 'cancel': [('readonly', True)]})

    transaction_date = fields.Date("Transaction Date", related='date_from')
    type_id = fields.Many2one("hr.payslip.input.type")
    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("approve1", "First Approval"),
            ("approve2", "Second Approval"),
        ],
        default="draft",
    )

    settlement_line_ids = fields.One2many("hr.settlement.line", "settlement_id")

    @api.depends('date_from')
    def _compute_date_to(self):
        next_month = relativedelta(months=+1, day=1, days=-1)
        for payslip in self:
            payslip.date_to = payslip.date_from and payslip.date_from + next_month

    def action_set_draft(self):
        self.ensure_one()

        return self.write({"state": "draft"})

    def action_approve1(self):
        self.ensure_one()

        return self.write({"state": "approve1"})

    def action_approve2(self):
        self.ensure_one()

        return self.write({"state": "approve2"})

    def unlink(self):

        if self.state == "approve2":
            raise AccessError("Cannot Delete Settlement in State Second Approval")
        return super().unlink()

    @api.model
    def create(self, vals):
        if vals.get("name", "New") == "New":
            vals["name"] = self.env["ir.sequence"].next_by_code("hr.settlement") or "New"
        return super(HrSettlement, self).create(vals)

    def compute_attendance(self):
        self.settlement_line_ids.unlink()
        end_dt = self.date_to
        start_dt = self.date_from
        EMPLOYESS = self.env['hr.employee'].search([])
        LEAVES = self.env['hr.leave'].search([('request_date_from', '<', end_dt),
                                              ('request_date_from', '>', start_dt)])
        my_list = []
        for employee in EMPLOYESS:
            search_domain = [
                ('employee_id', '=', employee.id),
                ('check_in', '<', end_dt),
                ('check_out', '>', start_dt), ('is_weekend', '!=', True), ('is_public_leave', '!=', True)
                # We ignore attendances which don't have a check_out
            ]
            attendances = self.env['hr.attendance'].sudo().search(search_domain)

            for attendance in attendances:

                time_object = datetime.strptime('16::00::00', '%H::%M::%S').time()
                out_time = datetime.combine(attendance.check_out.date(), time_object)
                ksa_check_out = attendance.check_out + timedelta(
                    hours=3) if attendance.check_out.time() <= time_object else out_time
                ksa_check_in = attendance.check_in + timedelta(hours=3)
                hours, remainder = divmod((ksa_check_out - ksa_check_in).seconds, 3600)

                if hours < 7:
                    leave_id = LEAVES.search(
                        [('employee_id', '=', employee.id), ('request_date_from', '<=', attendance.check_in.date()),
                         ('request_date_from', '>=', attendance.check_in.date())], limit=1)
                    my_list.append((0, 0, {'employee_id': employee.id,
                                           'date': attendance.check_in.date(),
                                           'leave_id': leave_id.id,
                                           'amount': 7 - hours,
                                           }))
        if my_list:
            self.settlement_line_ids = my_list


class HrSettlementLine(models.Model):
    _name = "hr.settlement.line"
    name = fields.Char()
    date = fields.Date()
    leave_id = fields.Many2one("hr.leave")
    settlement_id = fields.Many2one("hr.settlement")
    employee_id = fields.Many2one("hr.employee", "Employee")
    amount = fields.Float("Amount")
    type_id = fields.Many2one("hr.payslip.input.type", related="settlement_id.type_id")
    is_paid = fields.Boolean("Paid", default=False)
