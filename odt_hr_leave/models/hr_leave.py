# -*- coding:utf-8 -*-

from odoo import api, fields, models, _
from odoo.exceptions import AccessError, UserError, ValidationError
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from pytz import timezone, UTC
from odoo.tools import float_compare


class HolidaysRequest(models.Model):
    _inherit = 'hr.leave'

    extend = fields.Boolean('Is Extend')
    parent_id = fields.Many2one('hr.leave', string='Parent Leave')
    leave_type_extend = fields.Boolean(related='holiday_status_id.extend', readonly=True)

    @api.onchange('parent_id')
    def get_from_date(self):
        if self.parent_id:
            self.request_date_from = self.parent_id.request_date_to + timedelta(days=1)

    def _get_start_year(self, holiday):
        contract_start_date = holiday.employee_id.sudo().contract_id.date_start
        years_difference = relativedelta(holiday.request_date_from, contract_start_date)
        start_date = contract_start_date
        if years_difference.years:
            start_date = contract_start_date + relativedelta(years=years_difference.years)
        return start_date

    @api.constrains('number_of_days', 'holiday_status_id')
    def _check_max_min_days(self):
        for holiday in self:
            if holiday.holiday_type != 'employee' or not holiday.employee_id or holiday.holiday_status_id.requires_allocation == 'no' or holiday.holiday_status_id.leave_type != 'normal':
                continue
            if holiday.number_of_days < holiday.holiday_status_id.min_days:
                raise ValidationError(_("min_days"))
            if holiday.holiday_status_id.max_days > 0:
                if holiday.number_of_days > holiday.holiday_status_id.max_days:
                    raise ValidationError(_("max_days."))

    @api.constrains('employee_id', 'holiday_status_id')
    def _check_number_of_requests(self):
        """ check number of request & days / year """
        for holiday in self:
            if holiday.holiday_status_id.leave_type == 'normal':
                if holiday.employee_id.sudo().contract_id:
                    start_date = self._get_start_year(holiday)

                    user_requests_last_year = self.search(
                        [('holiday_status_id', '=', holiday.holiday_status_id.id),
                         ('id', '!=', holiday.id),
                         ('employee_id', '=', holiday.employee_id.id),
                         ('state', 'not in', ('refuse', 'draft', 'cancel')),
                         ('request_date_from', '>=', start_date)]
                    )

                    if len(user_requests_last_year.filtered(
                            lambda r: r.extend == False)) > holiday.holiday_status_id.request_per_year:
                        raise ValidationError(_("Maximum requests per year exceeded"))
                    if (sum(user_requests_last_year.mapped(
                            'number_of_days')) + holiday.number_of_days) > holiday.holiday_status_id.max_years:
                        raise ValidationError(_("max days per years."))
                    if holiday.extend:
                        print('holiday.holiday_status_id.max_extend', holiday.holiday_status_id.max_extend,
                              len(user_requests_last_year),
                              user_requests_last_year.filtered(lambda x: x.extend == True))

                        if len(user_requests_last_year.filtered(
                                lambda x: x.extend == True)) > holiday.holiday_status_id.max_extend:
                            raise ValidationError(_("you over max extend."))


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    leave_type = fields.Selection([('normal', 'Normal'), ('corona ', 'Corona'), ('exception', 'Exception'),
                                   ('sick', 'Sick')],
                                  string='Leave Type', default='normal')
    min_days = fields.Integer('Minimum Days')
    max_days = fields.Integer('Maximum Days')
    max_years = fields.Integer('Maximum Days per Year')
    request_per_year = fields.Integer('Requests Per Year')
    posting_balance = fields.Integer('Posting Balance')
    years_posting = fields.Integer('Years Posting')
    extend = fields.Boolean('Allow Extend')
    max_extend = fields.Integer('Number of Extends per year')
    percentage30 = fields.Integer('Percentage For First 30 days (%)')
    percentage90 = fields.Integer('Percentage From 31 to 90 days (%)')
    percentage120 = fields.Integer('Percentage From 91 to 120 days (%)')
    posting_date = fields.Date()

    @api.constrains('min_days', 'max_days', 'max_years', 'request_per_year')
    def _check_values(self):
        for rec in self:
            if rec.leave_type == 'normal':
                if rec.min_days <= 0.0 or rec.max_days <= 0.0 or rec.max_years <= 0.0 or rec.request_per_year <= 0.0:
                    raise UserError(_('Values should not be zero.'))
