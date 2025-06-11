from dateutil import relativedelta
import pandas as pd
from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.addons.resource.models.utils import HOURS_PER_DAY
from datetime import datetime
from datetime import date


class HrOverTime(models.Model):
    _name = 'hr.overtime'
    _description = "HR Overtime"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = "id desc"

    def _get_employee_domain(self):
        employee = self.env['hr.employee'].search(
            [('user_id', '=', self.env.user.id)], limit=1)
        domain = [('id', '=', employee.id)]
        if self.env.user.has_group('hr.group_hr_user'):
            domain = []
        return domain

    def _default_employee(self):
        return self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)

    @api.onchange('days_no_tmp')
    def _onchange_days_no_tmp(self):
        self.days_no = self.days_no_tmp

    name = fields.Char('Name', readonly=True)
    employee_id = fields.Many2one('hr.employee', string='Employee',
                                  domain=_get_employee_domain, default=lambda self: self.env.user.employee_id.id,
                                  required=True)
    department_id = fields.Many2one('hr.department', string="Department",
                                    related="employee_id.department_id")
    job_id = fields.Many2one('hr.job', string="Job", related="employee_id.job_id")
    manager_id = fields.Many2one('res.users', string="Manager",
                                 related="employee_id.parent_id.user_id", store=True)
    current_user = fields.Many2one('res.users', string="Current User",
                                   related='employee_id.user_id',
                                   default=lambda self: self.env.uid,
                                   store=True)
    current_user_boolean = fields.Boolean()
    project_id = fields.Many2one('project.project', string="Project")
    project_manager_id = fields.Many2one('res.users', string="Project Manager")
    contract_id = fields.Many2one('hr.contract', string="Contract",
                                  related="employee_id.contract_id",
                                  )
    date = fields.Date(compute='get_date',store=True)
    date_from = fields.Datetime('Date From')
    date_to = fields.Datetime('Date to')
    days_no_tmp = fields.Float('Hours', compute="_get_days", store=True)
    days_no = fields.Float('No. of Days', store=True)
    desc = fields.Text('Description')
    state = fields.Selection([('draft', 'Draft'),
                              ('f_approve', 'Waiting'),
                              ('hr_approve', 'HR Approved'),
                              ('approved', 'Approved'),
                              ('refused', 'Refused')], string="state",
                             default="draft")
    cancel_reason = fields.Text('Refuse Reason')
    leave_id = fields.Many2one('hr.leave.allocation',
                               string="Leave ID")
    attchd_copy = fields.Binary('Attach A File')
    attchd_copy_name = fields.Char('File Name')
    type = fields.Selection([('cash', 'Cash'), ('leave', 'leave')], default="cash", required=True, string="Type")
    overtime_type_id = fields.Many2one('overtime.type', domain="[('type','=',type),('duration_type','=', "
                                                               "duration_type)]", required=False, default=False)
    public_holiday = fields.Char(string='Public Holiday', readonly=True)
    attendance_ids = fields.Many2many('hr.attendance', string='Attendance')
    work_schedule = fields.One2many(
        related='employee_id.resource_calendar_id.attendance_ids')
    global_leaves = fields.One2many(
        related='employee_id.resource_calendar_id.global_leave_ids')
    duration_type = fields.Selection([('hours', 'Hour'), ('days', 'Days')], string="Duration Type", default="hours",
                                     required=True)
    cash_hrs_amount = fields.Float(string='Overtime Amount', readonly=True)
    cash_day_amount = fields.Float(string='Overtime Amount', readonly=True)
    payslip_paid = fields.Boolean('Paid in Payslip', readonly=True)

    # ########################## Mustafa Elian ###################
    is_weekend = fields.Boolean(string='Is Weekend', compute='_compute_is_weekend', store=True)
    is_public_holday = fields.Boolean(string='Is PUBLIC HOLIDAY')
    description = fields.Text()
    transaction_date = fields.Date('Transaction Date', readonly=True, default=lambda self: date.today())

    @api.constrains('description')
    def chatt(self):
        self.message_post(body=f"Description Updated -> {self.description}")

    @api.depends('date_from', 'date_to')
    def get_date(self):
        for rec in self:
            if rec.date_from:
                rec.date = rec.date_from.date()

    # ########################## way 1 ###########################
    # @api.depends('date_from')
    # def _compute_is_weekend(self):
    #     for record in self:
    #         if record.date_from:
    #             # #####################################################
    #             found_day = False
    #             dayofweek = record.date_from.strftime('%A')
    #             for day in record.employee_id.resource_calendar_id.attendance_ids:
    #                 if dayofweek == dict(day._fields['dayofweek'].selection).get(day.dayofweek) and not found_day:
    #                     found_day = True
    #
    #         if not found_day:
    #             record.is_weekend = True
    #         else:
    #             record.is_weekend = False

    # ########################## way 2 ###########################
    @api.depends('date_from')
    def _compute_is_weekend(self):
        for record in self:
            if record.date_from:
                day_of_week = record.date_from.weekday()
                working_days_list = record.employee_id.resource_calendar_id.attendance_ids.mapped('dayofweek')
                working_days = [int(i) for i in working_days_list]
                record.is_weekend = day_of_week not in working_days
            else:
                record.is_weekend = False

    # ########################## Mustafa Elian ###################

    @api.onchange('employee_id')
    def _get_defaults(self):
        for sheet in self:
            if sheet.employee_id:
                sheet.update({
                    'department_id': sheet.employee_id.department_id.id,
                    'job_id': sheet.employee_id.job_id.id,
                    'manager_id': sheet.sudo().employee_id.parent_id.user_id.id,
                })

    @api.depends('project_id')
    def _get_project_manager(self):
        for sheet in self:
            if sheet.project_id:
                sheet.update({
                    'project_manager_id': sheet.project_id.user_id.id,
                })

    @api.depends('date_from', 'date_to')
    def _get_days(self):
        for recd in self:
            if recd.date_from and recd.date_to:
                if recd.date_from > recd.date_to:
                    raise ValidationError('Start Date must be less than End Date')
        for sheet in self:
            if sheet.date_from and sheet.date_to:
                start_dt = fields.Datetime.from_string(sheet.date_from)
                finish_dt = fields.Datetime.from_string(sheet.date_to)
                s = finish_dt - start_dt
                difference = relativedelta.relativedelta(finish_dt, start_dt)
                hours = difference.hours
                minutes = difference.minutes
                days_in_mins = s.days * 24 * 60
                hours_in_mins = hours * 60
                days_no = ((days_in_mins + hours_in_mins + minutes) / (24 * 60))

                diff = sheet.date_to - sheet.date_from
                days, seconds = diff.days, diff.seconds
                hours = days * 24 + seconds // 3600
                sheet.update({
                    'days_no_tmp': hours if sheet.duration_type == 'hours' else days_no,
                })

    @api.onchange('overtime_type_id', 'date_from', 'date_to')
    def _get_hour_amount(self):
        if self.overtime_type_id.rule_line_ids and self.duration_type == 'hours':
            for recd in self.overtime_type_id.rule_line_ids:
                if recd.from_hrs < self.days_no_tmp <= recd.to_hrs and self.contract_id:
                    if self.contract_id.over_hour:
                        # cash_amount = self.contract_id.over_hour * recd.hrs_amount
                        # ######### edit by glal ################
                        if self.is_weekend or self.is_public_holday:
                            cash_amount = self.contract_id.over_hour * 2 * self.days_no_tmp
                        else:
                            cash_amount = self.contract_id.over_hour * recd.hrs_amount * self.days_no_tmp
                        # ######### edit by glal ################3

                        self.cash_hrs_amount = cash_amount
                    else:
                        raise UserError(_("Hour Overtime Needs Hour Wage in Employee Contract."))
        elif self.overtime_type_id.rule_line_ids and self.duration_type == 'days':
            for recd in self.overtime_type_id.rule_line_ids:
                if recd.from_hrs < self.days_no_tmp <= recd.to_hrs and self.contract_id:
                    if self.contract_id.over_day:
                        cash_amount = self.contract_id.over_day * recd.hrs_amount
                        self.cash_day_amount = cash_amount
                    else:
                        raise UserError(_("Day Overtime Needs Day Wage in Employee Contract."))

    def submit_to_f(self):
        # notification to employee
        recipient_partners = [(4, self.current_user.partner_id.id)]
        body = "Your OverTime Request Waiting Finance Approve .."
        msg = _(body)

        # notification to manager :
        manager_id = self.manager_id

        if manager_id:
            self.activity_schedule(
                activity_type_id=self.env.ref('ent_ohrms_overtime.mail_act_hr_overtime').id,
                summary=_('HR Overtime Needs Approve'), user_id=manager_id.id)

        # notification to finance :
        group = self.env.ref('account.group_account_invoice', False)
        recipient_partners = []

        body = "You Get New Time in Lieu Request From Employee : " + str(
            self.employee_id.name)
        msg = _(body)
        return self.sudo().write({
            'state': 'f_approve'
        })

    def approve(self):
        manager_id = self.manager_id
        if self.env.user.id != manager_id.id:
            raise UserError(_("Only Manager can approve Overtime Request."))

        return self.sudo().write({
            'state': 'hr_approve',
        })

    def hr_approve_button(self):
        if self.overtime_type_id.type == 'leave':
            if self.duration_type == 'days':
                holiday_vals = {
                    'name': 'Overtime',
                    'holiday_status_id': self.overtime_type_id.leave_type.id,
                    'number_of_days': self.days_no_tmp,
                    'notes': self.description,
                    'holiday_type': 'employee',
                    'employee_id': self.employee_id.id,
                    'state': 'confirm',
                }
            else:
                day_hour = self.days_no_tmp / HOURS_PER_DAY
                holiday_vals = {
                    'name': 'Overtime',
                    'holiday_status_id': self.overtime_type_id.leave_type.id,
                    'number_of_days': day_hour,
                    'notes': self.description,
                    'holiday_type': 'employee',
                    'employee_id': self.employee_id.id,
                    'state': 'confirm',
                }
            holiday = self.env['hr.leave.allocation'].sudo().create(
                holiday_vals)
            holiday.action_confirm()
            self.leave_id = holiday.id

        # notification to employee :
        recipient_partners = [(4, self.current_user.partner_id.id)]
        body = "Request Has been Approved ..."
        msg = _(body)
        return self.sudo().write({
            'state': 'approved',
        })

    def reject(self):
        self.state = 'refused'

    def set_to_draft(self):
        if self.payslip_paid:
            raise UserError("You can`t draft paid request")
        if not self.env.user.has_group('hr.group_hr_manager') and self.state == 'approved':
            raise UserError(_("Only HR Manager Can Draft ."))
        self.state = 'draft'

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        for req in self:
            domain = [
                ('date_from', '<=', req.date_to),
                ('date_to', '>=', req.date_from),
                ('employee_id', '=', req.employee_id.id),
                ('id', '!=', req.id),
                ('state', 'not in', ['refused']),
            ]
            nholidays = self.search_count(domain)
            if nholidays:
                raise ValidationError(_(
                    'You can not have 2 Overtime requests that overlaps on same day!'))

    @api.model
    def create(self, values):
        seq = self.env['ir.sequence'].next_by_code('hr.overtime') or '/'
        values['name'] = seq
        return super(HrOverTime, self.sudo()).create(values)

    def unlink(self):
        # for overtime in self.filtered(
        #         lambda overtime: overtime.state != 'draft'):
        raise UserError(
                _('You cannot delete TIL request which is not in draft state.'))
        return super(HrOverTime, self).unlink()

    @api.onchange('date_from', 'date_to', 'employee_id')
    def _onchange_date(self):
        holiday = False
        if self.contract_id and self.date_from and self.date_to:
            for leaves in self.contract_id.resource_calendar_id.global_leave_ids:
                leave_dates = pd.date_range(leaves.date_from, leaves.date_to).date
                overtime_dates = pd.date_range(self.date_from, self.date_to).date
                for over_time in overtime_dates:
                    for leave_date in leave_dates:
                        if leave_date == over_time:
                            holiday = True
            if holiday:
                self.is_public_holday = True
                self.write({
                    'public_holiday': 'You have Public Holidays in your Overtime request.',
                    'is_public_holday': True,
                })
            else:
                self.write({'public_holiday': ' '})

            hr_attendance = self.env['hr.attendance'].search(
                ['|', ('attendance_date', '=', self.date_from.date()),
                 ('attendance_date', '=', self.date_to.date()),
                 ('employee_id', '=', self.employee_id.id)])
            self.update({
                'attendance_ids': [(6, 0, hr_attendance.ids)]
            })

class HrOverTimeType(models.Model):
    _name = 'overtime.type'
    _description = "HR Overtime Type"

    name = fields.Char('Name')
    type = fields.Selection([('cash', 'Cash'),
                             ('leave', 'Leave ')],
                            default="cash")

    duration_type = fields.Selection([('hours', 'Hour'), ('days', 'Days')], string="Duration Type", default="hours",
                                     required=True)
    leave_type = fields.Many2one('hr.leave.type', string='Leave Type', domain="[('id', 'in', leave_compute)]")
    leave_compute = fields.Many2many('hr.leave.type', compute="_get_leave_type")
    rule_line_ids = fields.One2many('overtime.type.rule', 'type_line_id')

    @api.onchange('duration_type')
    def _get_leave_type(self):
        dur = ''
        ids = []
        if self.duration_type:
            if self.duration_type == 'days':
                dur = 'day'
            else:
                dur = 'hour'
            leave_type = self.env['hr.leave.type'].search([('request_unit', '=', dur)])
            for recd in leave_type:
                ids.append(recd.id)
            self.leave_compute = ids


class HrOverTimeTypeRule(models.Model):
    _name = 'overtime.type.rule'
    _description = "HR Overtime Type Rule"

    type_line_id = fields.Many2one('overtime.type', string='Over Time Type')
    name = fields.Char('Name', required=True)
    from_hrs = fields.Float('From', required=True)
    to_hrs = fields.Float('To', required=True)
    hrs_amount = fields.Float('Rate', required=True)
