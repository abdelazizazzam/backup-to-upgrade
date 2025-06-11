# -*- coding: utf-8 -*-

from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # leave_temp_date_from = fields.Date(string="Date From", required=False, )
    # leave_temp_date_to = fields.Date(string="Date To", required=False, )
    # leave_days_temp = fields.Float(string="Leave Days", required=False)
    holiday_line_ids = fields.One2many('hr.employee.leave.line', 'employee_id', 'Holiday Lines',
                                       groups="hr.group_hr_user", copy=True)


#
#     remaining_allocate_leaves = fields.Float(
#         compute='_compute_allocate_leaves', string='Remaining Legal Leaves',
#         help='Total number of legal leaves allocated to this employee, change this value to create allocation/leave '
#              'request. '
#              'Total based on all the leave types on allocation Leaves.')
#
#     def _compute_allocate_leaves(self):
#         for employee in self:
#             print('employee',employee)
#             leaves = employee.holiday_line_ids.mapped('leave_status_id').ids
#             leave_request = self.env['hr.leave'].search(
#                 [('employee_id', '=', employee.id), ('state', '=', 'validate'), ('holiday_status_id', 'in', leaves)])
#             leave_allocate = self.env['hr.leave.allocation'].search(
#                 [('employee_id', '=', employee.id), ('state', '=', 'validate'), ('holiday_status_id', 'in', leaves)])
#             allocate_days = sum(leave_allocate.mapped('number_of_days'))
#             print('allocate_days',allocate_days)
#             request_days = sum(leave_request.mapped('number_of_days'))
#             days = allocate_days - request_days
#             employee.remaining_allocate_leaves = days if days > 0.0 else 0.0
#
#
class HrEmployeeLeaveLineAuto(models.Model):
    _name = 'hr.employee.leave.line'

    leave_status_id = fields.Many2one('hr.leave.type', 'Leave Type', required=True)
    type_allocation = fields.Selection(string="Type", selection=[('under_five', 'Under Five Years'),
                                                                 ('over_five', 'Over Five Years'), ],
                                       default='under_five', required=True, )
    allocation_range = fields.Selection([('month', 'Month'), ('year', 'Year')],
                                        'Allocate automatic leaves every', required=True,
                                        help="Periodicity on which you want automatic allocation of leaves to eligible employees.")
    days_to_allocate = fields.Float('Days to Allocate',
                                    help="In automatic allocation of leaves, " \
                                         "given days will be allocated every month / year.")
    employee_id = fields.Many2one('hr.employee', ondelete='cascade')
