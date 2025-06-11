# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from datetime import date, timedelta

class HrHolidays(models.Model):
    _inherit = 'hr.leave'
    is_reconciled = fields.Boolean(string="Is Reconciled", readonly=True)
    is_settlement = fields.Boolean(string="Is Settlement")
    reconcile_option = fields.Selection(string="Reconciliation ?", selection=[('yes', 'Yes'), ('no', 'No'), ],
                                        required=False, )


    def _create_work_entries(self):
        work_entry_type_id = self.env.ref("odt_leave_termination.work_entry_type_leave_advance")
        number_of_days = (self.request_date_to - self.request_date_from).days
        for day in range(0, number_of_days + 1):
            week_day = str((self.request_date_from + timedelta(days=day)).weekday())
            calendar_line = self.env["resource.calendar.attendance"].search(
                        [
                            (
                                "calendar_id",
                                "=",
                                self.employee_id.resource_calendar_id.id,
                            ),
                            ("dayofweek", "=", week_day),
                        ]
                    )
            for line in calendar_line:
                res_time_from = (
                            "{0:02.0f}:{1:02.0f}".format(
                                *divmod(float(line.hour_from) * 60, 60)
                            )
                            + ":00"
                        )
                res_time_to = (
                            "{0:02.0f}:{1:02.0f}".format(
                                *divmod(float(line.hour_to) * 60, 60)
                            )
                            + ":00"
                        )
                date_from = str((self.request_date_from + timedelta(days=day))) + " " + res_time_from
                date_to = str((self.request_date_from + timedelta(days=day))) + " " + res_time_to
                self.env["hr.work.entry"].create(
                            {
                                "contract_id": self.employee_id.contract_id.id,
                                "name": "Work entry %s-%s" % (date_from, date_to),
                                "date_start": date_from,
                                "date_stop": date_to,
                                "state": "draft",
                                "employee_id": self.employee_id.id,
                                "work_entry_type_id": work_entry_type_id.id,
                                # "related_over_id": self.id,
                            }
                        )
                self.env["hr.work.entry"].sudo().search([("leave_id", "=", self.id)]).sudo().write({"state": "draft"})

    def action_validate(self):
        res = super().action_validate()
        if self.state == 'validate' and self.reconcile_option == 'yes':
            self._create_work_entries()
        return res

class LeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    _sql_constraints = [
        ('type_value',
         "CHECK( (holiday_type='employee' AND employee_id IS NOT NULL) or "
         "(holiday_type='category' AND category_id IS NOT NULL) or "
         "(holiday_type='department' AND department_id IS NOT NULL) or "
         "(holiday_type='company' AND mode_company_id IS NOT NULL))",
         "The employee, department, company or employee category of this request is missing. Please make sure that your user login is linked to an employee."),
        ('duration_check', "CHECK ( number_of_days == 0 )", "The number of days must be greater than 0."),
        ('number_per_interval_check', "CHECK(number_per_interval > 0)",
         "The number per interval should be greater than 0"),
        ('interval_number_check', "CHECK(interval_number > 0)", "The interval number should be greater than 0"),
    ]
