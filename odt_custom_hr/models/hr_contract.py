from datetime import date
from odoo import models, fields, api, _
from dateutil.relativedelta import relativedelta


class ContractType(models.Model):
    _inherit = "hr.contract.type"
    housing_allowance_percentage = fields.Float("Housing Allowance", default=25.0)


class Contract(models.Model):
    _inherit = "hr.contract"

    @api.onchange("department_id")
    def _set_analytic_account(self):
        for rec in self:
            rec.analytic_account_id = rec.default_analytic_account_id

    default_analytic_account_id = fields.Many2one(
        "account.analytic.account",
        related="department_id.default_analytic_account_id",
        string="Analytic Account",
    )
    contract_duration = fields.Selection(
        [("limited", "Limited"), ("unlimited", "Unlimited")], default="limited"
    )
    allowance = fields.Float("بدل تحصيل (خدمات المشتركين)")
    allowance2 = fields.Float(" Food Allowance.")
    allowance3 = fields.Float("بدل مقابلة جمهور (خدمات المشتركين)")
    allowance4 = fields.Float("allowance4")
    allowance5 = fields.Float("بدلات أخرى ثابته")
    allowance6 = fields.Float("بدلات أخرى متحركة")

    trial_start = fields.Date("Trial Start Date")
    trial_end = fields.Date("Trial End Date")

    has_car = fields.Boolean("Has A Car")

    housing_rule = fields.Selection(
        [
            ("monthly", "Monthly"),
            ("quarterly", "Quarterly"),
            ("semi_anually", "Semi Anually"),
            ("anually", "Anually"),
        ],
        "Housing Type",
        default="monthly",
    )

    allowance_line_ids = fields.One2many(
        "hr.allowance.lines", "allowance_line_ids", string=" "
    )

    transportation_rule = fields.Selection(
        [("percent", "Percentage"), ("amount", "Amount")],default='amount'
    )
    transportation_value = fields.Float("Transportation",default=10)
    trans_value = fields.Float(compute="_compute_allowance_transportation", readonly=True,string="بدل تصديق (خدمات المشتركين)")

    total_salary = fields.Float(
        "Total Salary", readonly=True, compute="_compute_total_salary"
    )

    housing_monthly_allowance = fields.Float(
        "Monthly Housing Allowance",
        readonly=False,
        store=True
    )
    employee_country = fields.Char(related="employee_id.country_id.code")
    housing_allowance = fields.Float(
        compute="_compute_allowance_housing", readonly=True
    )
    tickets_amount = fields.Float("Tickets")
    vacation_days = fields.Integer("Vacation Days")
    #TODO ADD ME AFTER ADDING SELF_SERVICES
    # remaining_tickets = fields.Float(
    #     "Remaining Tickets", compute="_get_remaining_tickets", readonly=True
    # )
    # def _get_remaining_tickets(self):
    #     for rec in self:
    #         ticket_requests = self.env['ticket.request'].search([('employee_id', '=', rec.employee_id.id), ('travel_ticket', '=', 'company'), ('state', '=', 'paid')])
    #         if ticket_requests:
    #             remaining_amnt = rec.tickets_amount
    #             for request in ticket_requests:
    #                 remaining_amnt -= request.tickets_value
    #             rec.remaining_tickets = remaining_amnt
    #         else:
    #             rec.remaining_tickets = rec.tickets_amount

    @api.depends("transportation_value")
    def _compute_allowance_transportation(self):
        for rec in self:
            if rec.transportation_rule == "amount":
                value = rec.transportation_value
                # value = rec.transportation_value if rec.transportation_value > 500 else 500
                rec.trans_value = value
            if rec.transportation_rule == "percent":
                rec.trans_value = (rec.transportation_value * rec.wage) / 100
                # rec.trans_value = (rec.transportation_value * rec.wage) / 100 if ((rec.transportation_value * rec.wage) / 100) > 500 else 500

    @api.depends("housing_rule")
    def _compute_allowance_housing(self):
        for rec in self:
            allowance_percent = rec.contract_type_id.housing_allowance_percentage / 100
            if rec.housing_rule == "quarterly":
                rec.housing_allowance = 3 * allowance_percent * rec.wage
            elif rec.housing_rule == "semi_anually":
                rec.housing_allowance = allowance_percent * rec.wage
            elif rec.housing_rule == "anually":
                rec.housing_allowance = allowance_percent * rec.wage

    @api.depends("housing_rule")
    def _compute_monthly_housing_allowance(self):
        for rec in self:
            allowance_percent = rec.contract_type_id.housing_allowance_percentage / 100
            if rec.housing_rule == "monthly":
                # rec.housing_monthly_allowance = allowance_percent * rec.wage
                rec.housing_monthly_allowance = (rec.wage * 3) / 12
            else:
                rec.housing_monthly_allowance = 0



    @api.depends(
        "allowance",
        "allowance2",
        "allowance3",
        "allowance4",
        "allowance5",
        "allowance6",
        "has_car",
        "transportation_rule",
        "transportation_value",
        "housing_monthly_allowance",
    )
    def _compute_total_salary(self):
        for rec in self:
            rec.total_salary = (
                rec.wage
                + rec.allowance
                + rec.allowance2
                + rec.allowance3
                + rec.allowance4
                + rec.allowance5
                + rec.allowance6
                + rec.housing_monthly_allowance
            )
            if not rec.has_car:
                if rec.transportation_rule == "percent":
                    amount = rec.wage * (rec.transportation_value / 100)
                    rec.total_salary += amount
                elif rec.transportation_rule == "amount":
                    rec.total_salary += rec.transportation_value



    # def calculate_semi_anually_housing_allowance(self):
    #     contract_start = self.date_start
    #     contract_end = self.date_end
    #     pay_month = 0
    #     months_in_contract = (contract_end.year - contract_start.year) * 12 + (
    #         contract_end.month - contract_start.month
    #     )
    #     full_half_years = months_in_contract // 6
    #     remainder_months = months_in_contract % 6
    #     vals = {}
    #     next_date = 0
    #     next_month = 0
    #     lines = []
    #     worked_months = 0
    #     advance_months = 0
    #     if contract_start.month != 1:
    #         next_month = pay_month + 6
    #         next_date = date(contract_start.year, next_month, 30)
    #         worked_months = 6 - contract_start.month + 1
    #         remainder_months += 6 - worked_months
    #         advance_months = 6
    #         full_half_years -= 1
    #     else:
    #         next_month = pay_month + 1
    #         next_date = date(contract_start.year, next_month, 31)
    #         worked_months = 6

    #     for i in range(0, full_half_years):
    #         vals["date"] = next_date
    #         vals["amount"] = (
    #             self.housing_allowance * worked_months
    #             + self.housing_allowance * advance_months
    #         )
    #         lines.append(vals.copy())
    #         next_date += relativedelta(months=6)
    #         if next_date.month == 12:
    #             next_date += relativedelta(months=1)
    #         elif next_date.month == 7:
    #             next_date -= relativedelta(months=1)
    #         worked_months = 6
    #         advance_months = 0

    #     if remainder_months > 0:
    #         if next_date > contract_end:
    #             lines[-1]["amount"] += self.housing_allowance * remainder_months
    #         else:
    #             vals["date"] = next_date
    #             vals["amount"] = self.housing_allowance * remainder_months
    #             lines.append(vals.copy())
    #     return lines

    # def calculate_yearly_housing_allowance(self):
    #     contract_start = self.date_start
    #     contract_end = self.date_end
    #     pay_month = 0
    #     months_in_contract = (contract_end.year - contract_start.year) * 12 + (
    #         contract_end.month - contract_start.month
    #     )
    #     full_years_in_contract = months_in_contract // 12
    #     vals = {}
    #     remainder_months = months_in_contract % 12
    #     next_date = 0
    #     next_month = 0
    #     lines = []
    #     worked_months = 0

    #     if contract_start.month != 1:
    #         next_month = pay_month + 6
    #         next_date = date(contract_start.year, next_month, 30)
    #         worked_months = 12 - contract_start.month
    #         remainder_months += 12 - worked_months
    #     else:
    #         next_month = pay_month + 1
    #         next_date = date(contract_start.year, next_month, 31)
    #         worked_months = 12

    #     for i in range(0, full_years_in_contract):
    #         vals["date"] = next_date
    #         vals["amount"] = self.housing_allowance * worked_months
    #         lines.append(vals.copy())
    #         next_year = contract_start.year + i + 1
    #         next_date = date(next_year, 1, 31)
    #         worked_months = 12

    #     if remainder_months > 0:
    #         vals["date"] = next_date
    #         vals["amount"] = self.housing_allowance * remainder_months
    #         lines.append(vals.copy())
    #     return lines


    def calculate_semi_anually_housing_allowance(self):
        contract_start = self.date_start
        contract_end = self.date_end
        vals = {}
        lines = []
        next_date = 0
        no_of_half_years = (contract_end.year - contract_start.year) * 2

        if contract_start.month > 1 and contract_start.month < 6:
            next_date = contract_start
            no_of_months = (6 - contract_start.month) + 1
            vals['date'] = next_date
            vals['amount'] = self.housing_allowance * no_of_months
            lines.append(vals.copy())
            next_date = date(contract_start.year, 1, 31)
        elif contract_start.month > 6:
            next_date = contract_start
            no_of_months = (12 - contract_start.month) + 1
            vals['date'] = next_date
            vals['amount'] = self.housing_allowance * no_of_months
            lines.append(vals.copy())
            next_date = date(contract_start.year, 7, 31)

        for i in range(0, no_of_half_years):
            next_date += relativedelta(months=6)
            vals['date'] = next_date
            vals['amount'] = self.housing_allowance * 6
            lines.append(vals.copy())

        return lines

    def calculate_yearly_housing_allowance(self):
        contract_start = self.date_start
        contract_end = self.date_end
        vals = {}
        lines = []
        next_date = 0
        no_of_years = contract_end.year - contract_start.year

        if contract_start.month > 1:
            next_date = contract_start
            no_of_months = (12 - contract_start.month) + 1
            vals['date'] = next_date
            vals['amount'] = self.housing_allowance * no_of_months
            lines.append(vals.copy())

        for i in range(1, no_of_years + 1):
            next_date = date(contract_start.year + i, 1, 31)
            vals['date'] = next_date
            vals['amount'] = self.housing_allowance * 12
            lines.append(vals.copy())

        return lines


    def act(self):
        contract_start = self.date_start
        contract_end = self.date_end
        values = {"allowance_line_ids": self.id}
        # next_date = self.date_start
        self.env["hr.allowance.lines"].search(
            [("allowance_line_ids", "=", self.id)]
        ).unlink()
        if self.housing_rule == "quarterly":
            values["amount"] = self.housing_allowance
            for i in range(0, 4):
                next_date = self.date_start + relativedelta(months=i * 3)
                values["date"] = next_date
                self.env["hr.allowance.lines"].create(values)
        elif self.housing_rule == "semi_anually":
            # values["amount"] = self.housing_allowance
            # for i in range(0, 2):
            #     next_date = self.date_start + relativedelta(months=i * 6)
            #     values["date"] = next_date
            lines = self.calculate_semi_anually_housing_allowance()
            for line in lines:
                values.update(line)
                self.env["hr.allowance.lines"].create(values)
        elif self.housing_rule == "anually":
            lines = self.calculate_yearly_housing_allowance()
            for line in lines:
                values.update(line)
                self.env["hr.allowance.lines"].create(values)
            # years_in_contract = contract_end.year - contract_start.year
            # months_in_contract = (contract_end.year - contract_start.year) * 12 + (
            #     contract_end.month - contract_start.month
            # )
            # months_remaining_in_contract = months_in_contract
            # months_worked_in_year = months_in_contract
            # for i in range(0, years_in_contract + 1):
            #     if months_remaining_in_contract > 12:
            #         months_worked_in_year = months_in_contract - (
            #             months_remaining_in_contract % (12 * (i+1))
            #         )

            #     print("months_worked_in_year", months_worked_in_year)
            #     print("months_remaining_in_contract", months_remaining_in_contract)
            #     if contract_start.month >= 1 and contract_start.month < 6:
            #         # next_date = self.date_start + relativedelta(months=12)
            #         values["date"] = datetime(contract_start.year, 1, 31)
            #         values["amount"] = self.housing_allowance * months_remaining_in_contract
            #         self.env["hr.allowance.lines"].create(values)
            #     else:
            #         next_date = datetime(contract_start.year, 6, 30)
            #         months_worked = (next_date.year - contract_start.year) * 12 + (
            #             next_date.month - contract_start.month
            #         )
            #         values["date"] = next_date
            #         values["amount"] = self.housing_allowance * months_remaining_in_contract
            #         self.env["hr.allowance.lines"].create(values)
            #     months_remaining_in_contract -= months_worked_in_year
