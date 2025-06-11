from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from odoo.tools.misc import format_date


class HrPayslipInputType(models.Model):
    _inherit = "hr.payslip.input.type"

    def unlink(self):
        vals = ["quarterly", "anually", "semi_anually"]
        payslip_inputs = self.env["hr.payslip.input"]
        for rec in self:
            types = payslip_inputs.search([("input_type_id", "=", rec.id)])
            if types:
                raise AccessError("Input Type linked to Payslip Cannot be Deleted")
            elif rec.code in vals:
                raise AccessError("Cannot Delete this Input Type")
        return super().unlink()


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    state = fields.Selection(
        [
            ("draft", "Draft"),
            ("verify", "Waiting"),
            ("confirmed", "Confirmed"),
            ("done", "Done"),
            ("paid", "Paid"),
            ("cancel", "Rejected"),
        ],
        string="Status",
        index=True,
        readonly=True,
        copy=False,
        default="draft",
        tracking=True,
        help="""* When the payslip is created the status is \'Draft\'
                    \n* If the payslip is under verification, the status is \'Waiting\'.
                    \n* If the payslip is confirmed then status is set to \'Done\'.
                    \n* When user cancel payslip the status is \'Rejected\'.""",
    )

    @api.depends('employee_id', 'struct_id', 'date_from')
    def _compute_name(self):
        for slip in self.filtered(lambda p: p.employee_id and p.date_from):
            lang = slip.employee_id.sudo().address_id.lang or self.env.user.lang
            context = {'lang': lang}
            payslip_name = slip.struct_id.payslip_name or _('Salary Slip')
            del context

            slip.name = '%(payslip_name)s - %(employee_name)s - %(dates)s' % {
                'payslip_name': payslip_name,
                'employee_name': slip.employee_id.name,
                'dates': format_date(self.env, slip.date_to, date_format="MMMM y", lang_code=lang)
            }

    def action_payslip_draft(self):
        return self.write({"state": "draft"})

    def compute_sheet(self):
        payslips = self.filtered(lambda slip: slip.state in ["draft", "verify"])
        # delete old payslip lines
        payslips.line_ids.unlink()
        for payslip in payslips:
            number = payslip.number or self.env["ir.sequence"].next_by_code(
                "salary.slip"
            )
            lines = [(0, 0, line) for line in payslip._get_payslip_lines()]
            payslip.write(
                {
                    "line_ids": lines,
                    "number": number,
                    "state": "verify",
                    "compute_date": fields.Date.today(),
                }
            )
        return True

    def action_payslip_confirm(self):
        if any(slip.state != "verify" for slip in self):
            raise UserError(_("Cannot confirm payslip if not verified."))
        self.write({"state": "confirmed"})

    # def action_payslip_done(self):
    #     invalid_payslips = self.filtered(
    #         lambda p: p.contract_id
    #         and (
    #             p.contract_id.date_start > p.date_to
    #             or (p.contract_id.date_end and p.contract_id.date_end < p.date_from)
    #         )
    #     )
    #     if invalid_payslips:
    #         raise ValidationError(
    #             _(
    #                 "The following employees have a contract outside of the payslip period:\n%s",
    #                 "\n".join(invalid_payslips.mapped("employee_id.name")),
    #             )
    #         )
    #     if any(slip.contract_id.state == "cancel" for slip in self):
    #         raise ValidationError(
    #             _("You cannot valide a payslip on which the contract is cancelled")
    #         )
    #     if any(slip.state == "cancel" for slip in self):
    #         raise ValidationError(_("You can't validate a cancelled payslip."))
    #     self.write({"state": "done"})
    #
    #     line_values = self._get_line_values(["NET"])
    #
    #     self.filtered(
    #         lambda p: not p.credit_note and line_values["NET"][p.id]["total"] < 0
    #     ).write({"has_negative_net_to_report": True})
    #     self.mapped("payslip_run_id").action_close()
    #     # Validate work entries for regular payslips (exclude end of year bonus, ...)
    #     regular_payslips = self.filtered(
    #         lambda p: p.struct_id.type_id.default_struct_id == p.struct_id
    #     )
    #     work_entries = self.env["hr.work.entry"]
    #     for regular_payslip in regular_payslips:
    #         work_entries |= self.env["hr.work.entry"].search(
    #             [
    #                 ("date_start", "<=", regular_payslip.date_to),
    #                 ("date_stop", ">=", regular_payslip.date_from),
    #                 ("employee_id", "=", regular_payslip.employee_id.id),
    #             ]
    #         )
    #     if work_entries:
    #         work_entries.action_validate()
    #
    #     if self.env.context.get("payslip_generate_pdf"):
    #         if self.env.context.get("payslip_generate_pdf_direct"):
    #             self._generate_pdf()
    #         else:
    #             self.write({"queued_for_pdf": True})
    #             payslip_cron = self.env.ref(
    #                 "hr_payroll.ir_cron_generate_payslip_pdfs", raise_if_not_found=False
    #             )
    #             if payslip_cron:
    #                 payslip_cron._trigger()

    def action_payslip_cancel(self):
        if not self.env.user._is_system() and self.filtered(
                lambda slip: slip.state == "done"
        ):
            raise UserError(_("Cannot cancel a payslip that is done."))
        self.write({"state": "cancel"})
        self.mapped("payslip_run_id").action_close()

    def action_payslip_paid(self):
        if any(slip.state != "done" for slip in self):
            raise UserError(_("Cannot mark payslip as paid if not confirmed."))
        self.write({"state": "paid"})

    @api.onchange(
        "employee_id", "struct_id", "contract_id", "date_from", "date_to", "number"
    )
    def _onchange_employees(self):
        self.get_settlement_lines()
        self.get_housing_allowance()

    def get_settlement_lines(self):
        settlement_lines = self.env["hr.settlement.line"]
        settlement_recs = settlement_lines.search(
            [
                ("employee_id", "=", self.employee_id.id),
                ("settlement_id.state", "=", "approve2"),
                ("is_paid", "=", False),
                ("settlement_id.transaction_date", ">=", self.date_from),
                ("settlement_id.transaction_date", "<=", self.date_to),
            ]
        )
        input_values = []

        if settlement_recs:
            line_types = [type_id for type_id in settlement_recs.type_id]

            lines_to_delete = self.input_line_ids.filtered(
                lambda x: x.input_type_id in line_types
            )
            input_values = [(3, line.id, 0) for line in lines_to_delete]
            total = 0
            for rec in settlement_recs:
                total += rec.amount
            input_values.append(
                (0, 0, {"amount": total, "input_type_id": rec.type_id.id})
            )
        self.write({"input_line_ids": input_values})

    def get_housing_allowance(self):
        allowance_lines = self.env["hr.allowance.lines"]
        allowance_recs = allowance_lines.search(
            [
                ("allowance_line_ids.employee_id", "=", self.employee_id.id),
                ("status", "=", "unpaid"),
                ("date", ">=", self.date_from),
                ("date", "<=", self.date_to),
            ]
        )
        input_type = ""
        if allowance_recs:
            input = allowance_recs[0]["housing_allowance_type"]
            input_type = self.env.ref(f"odt_custom_hr.{input}")
        lines_to_delete = self.input_line_ids.filtered(
            lambda x: x.input_type_id == input_type
        )
        input_values = [(3, input_line.id, 0) for input_line in lines_to_delete]
        if len(allowance_recs) > 0:
            for rec in allowance_recs:
                input_values.append(
                    (0, 0, {"amount": rec.amount, "input_type_id": input_type.id})
                )
        self.write({"input_line_ids": input_values})

    def action_payslip_done(self):
        res = super(HrPayslip, self).action_payslip_done()
        allowance_lines = self.env["hr.allowance.lines"]
        settlement_lines = self.env["hr.settlement.line"]
        for payslip in self:
            allowance_recs = allowance_lines.search(
                [
                    ("allowance_line_ids.employee_id", "=", payslip.employee_id.id),
                    ("status", "=", "unpaid"),
                    ("date", ">=", payslip.date_from),
                    ("date", "<=", payslip.date_to),
                ]
            )
            settlement_recs = settlement_lines.search(
                [
                    ("employee_id", "=", payslip.employee_id.id),
                    ("is_paid", "=", False),
                    ("settlement_id.transaction_date", ">=", payslip.date_from),
                    ("settlement_id.transaction_date", "<=", payslip.date_to),
                ]
            )
            for rec in allowance_recs:
                rec.status = "paid"

            for rec in settlement_recs:
                rec.is_paid = True
        return res
