from odoo import fields, models, api, _  # type: ignore
from odoo.exceptions import UserError, ValidationError  # type: ignore
from datetime import date, datetime, timedelta
import requests


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in = fields.Datetime(string="Check In", default="", required=False)
    biotime_id = fields.Integer()
    in_biotime_id = fields.Integer()
    out_biotime_id = fields.Integer()
    attendance_date = fields.Date(compute='get_attendance_date', store=True)

    @api.depends('check_in', 'check_out')
    def get_attendance_date(self):
        for rec in self:
            if rec.check_in:
                rec.attendance_date = rec.check_in.date()
            elif rec.check_out:
                rec.attendance_date = rec.check_out.date()

    @api.depends("check_in", "check_out")
    def _compute_worked_hours(self):
        for attendance in self:
            if attendance.check_in and attendance.check_out:
                delta = attendance.check_out - attendance.check_in
                attendance.worked_hours = delta.total_seconds() / 3600.0

    @api.constrains('check_in', 'check_out', 'employee_id')
    def _check_validity(self):
        """ Verifies the validity of the attendance record compared to the others from the same employee.
            For the same employee we must have :
                * maximum 1 "open" attendance record (without check_out)
                * no overlapping time slices with previous employee records
        """
        pass

    def _get_auth_token(self, uri, username, password):
        url = f"http://{uri}/jwt-api-token-auth/"
        username = username
        password = password
        headers = {
            "Content-Type": "application/json",
        }
        body = {
            'username': username,
            'password': password
        }
        response = requests.post(url, json=body, headers=headers)
        data = response.json()
        return data.get('token')
    
    @api.model
    def _cron_fetch_attendance(self):
        url = self.env["ir.config_parameter"].sudo().get_param("biotime_url") or False
        username = self.env["ir.config_parameter"].sudo().get_param("biotime_user") or False
        password = self.env["ir.config_parameter"].sudo().get_param("biotime_password") or False
        jwt = self._get_auth_token(url, username, password)
        token = jwt
        if not token:
            return
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"JWT {token}",
        }
        startday = datetime.today() - timedelta(days=2)
        url = f"http://{url}/iclock/api/transactions/?start_time={startday.date()} 00:00:00"
        # print("URL:", url)
        response = requests.get(url, headers=headers)
        jsonResponse = response.json()
        _data = jsonResponse["data"]
        _next = jsonResponse["next"]

        # key: (employee_id.id,punch,punch_date)
        # value: (punch_time, biotime_id)
        punch_dates = dict()
        attendance_obj = self.env["hr.attendance"]
        # last_biotime = attendance_obj.search([], limit=1
        #                                      ).biotime_id
        while _data:
            # Don't process data if already processed before
            # if _data[-1]["id"] > last_biotime:
            for rec in _data:
                # if rec["id"] <= last_biotime:
                #     continue

                employee_id = self.env["hr.employee"].search(
                    [("zknumber", "=", rec["emp_code"])]
                )
                if not employee_id:
                    continue

                punch_time = rec["punch_time"]
                punch_time = datetime.strptime(punch_time, "%Y-%m-%d %H:%M:%S")

                punch = rec["punch_state"]
                biotime_id = rec["id"]
                key = (employee_id.id, punch, punch_time.date())
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
                # print("Welcome to creating")
                # count = 0
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
