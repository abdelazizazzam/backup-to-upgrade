# -*- coding: utf-8 -*-

from odoo import api, fields, models, _  # type: ignore
from odoo.exceptions import UserError, ValidationError  # type: ignore
import requests
from datetime import date, time, datetime, timedelta


class LinkUser(models.TransientModel):
    _name = "link.user"
    _description = "Link user in Biotime"

    employee_ids = fields.Many2many("hr.employee", string='Employees', readonly=False, copy=False, required=True)
    from_date = fields.Date(string='From Date')

    def create_users_zk(self):
        attendance_obj = self.env["hr.attendance"]
        host_url = self.env["ir.config_parameter"].sudo().get_param("biotime_url") or False
        username = self.env["ir.config_parameter"].sudo().get_param("biotime_user") or False
        password = self.env["ir.config_parameter"].sudo().get_param("biotime_password") or False
        jwt = attendance_obj._get_auth_token(host_url, username, password)
        token = jwt
        if not token:
            return
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"JWT {token}",
        }
        punch_dates = dict()
        for employee in self.employee_ids:
            if employee.zknumber:
                emp_code = employee.zknumber
                # last_check = attendance_obj.search(
                #     [('biotime_id', '=', emp_code)], order="biotime_id desc", limit=1
                # )
                # last_datetime = last_check.check_out or last_check.check_in
                # if last_datetime:
                #     url = f"http://{host_url}/iclock/api/transactions/?emp_code={emp_code}&start_time={last_datetime}"
                # else:
                if self.from_date:
                    url = f"http://{host_url}/iclock/api/transactions/?emp_code={emp_code}&start_time={self.from_date}"
                else:
                    url = f"http://{host_url}/iclock/api/transactions/?emp_code={emp_code}"
                response = requests.get(url, headers=headers)
                jsonResponse = response.json()
                _data = jsonResponse["data"]
                _next = jsonResponse['next']
                while _data:
                    for rec in _data:
                        punch_time = rec["punch_time"]
                        punch_time = datetime.strptime(punch_time, "%Y-%m-%d %H:%M:%S")

                        punch = rec["punch_state"]
                        biotime_id = rec["id"]

                        # Update punch_dates with best data (employee,punch_state,punch_date)
                        key = (employee.id, punch, punch_time.date())
                        if punch == "0":
                            if punch_dates.get(key) and punch_dates[key][0] <= punch_time:
                                continue
                            punch_dates[key] = (punch_time, biotime_id)
                        elif punch == "1":
                            if punch_dates.get(key) and punch_dates[key][0] >= punch_time:
                                continue
                            punch_dates[key] = (punch_time, biotime_id)
                    if _next:
                        response = requests.get(_next, headers=headers)
                        jsonResponse = response.json()
                        _next = jsonResponse["next"]
                        _data = jsonResponse["data"]
                    else:
                        break

        for key, value in punch_dates.items():
            employee_id = key[0]
            punch = key[1]
            punch_time = value[0]
            punch_time -= timedelta(hours=3)
            biotime_id = value[1]
            if punch == "0":
                attendance_id = attendance_obj.search(
                    [("in_biotime_id", "=", biotime_id)]
                )
                if attendance_id:
                    continue
                attendance_time = attendance_obj.search(
                    [("employee_id", "=", employee_id),
                     ("check_in", "=", punch_time), ]
                )
                if attendance_time: continue
                attendance_ids = attendance_obj.search(
                    [
                        ("employee_id", "=", employee_id),
                        ("check_in", "=", False),
                    ],
                )
                oof = True
                for id in attendance_ids:
                    if (
                        id.check_out
                        and id.check_out.date() == punch_time.date()
                        and id.check_out > punch_time
                    ):
                        id.write({"check_in": punch_time, "in_biotime_id": biotime_id, })
                        oof = False
                        break
                if oof:
                    # count += 1
                    attendance_obj.create(
                        {
                            "check_in": punch_time,
                            "employee_id": employee_id,
                            "in_biotime_id": biotime_id,
                        }
                    )
            elif punch == "1":
                attendance_id = attendance_obj.search(
                    [("out_biotime_id", "=", biotime_id)]
                )
                if attendance_id:
                    continue
                attendance_ids = attendance_obj.search(
                    [
                        ("employee_id", "=", employee_id),
                        ("check_out", "=", False),
                    ],
                )
                oof = True
                for id in attendance_ids:
                    if (
                            id.check_in
                            and id.check_in.date() == punch_time.date()
                            and id.check_in < punch_time
                    ):
                        id.write({"check_out": punch_time, "out_biotime_id": biotime_id})
                        oof = False
                if oof:
                    attendance_obj.create(
                        {
                            "check_out": punch_time,
                            "employee_id": employee_id,
                            "out_biotime_id": biotime_id,
                        }
                    )
        return
