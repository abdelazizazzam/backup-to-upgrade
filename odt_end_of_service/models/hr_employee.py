# -*- coding: utf-8 -*-


from odoo import models, fields, api, _
from datetime import datetime, timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    total_eos_leaves = fields.Float('No of Leaves Depend EOS', )
    joining_date = fields.Date(string='Joining Date',groups="hr.group_hr_user", help="Employee joining date computed from the contract start date")

    @api.depends('contract_id')
    def compute_joining(self):
        if self.contract_id:
            date = min(self.contract_id.mapped('date_start'))
            self.joining_date = date
        else:
            self.joining_date = False

    # def _compute_eos_leaves(self):
    #     for record in self :
    #         record._cr.execute("""SELECT
    #                 sum(h.number_of_days) as days,
    #                 h.employee_id
    #             from
    #                 hr_leave h
    #                 join hr_leave_type s on (s.id=h.holiday_status_id)
    #             where
    #                 h.state='validate' and
    #                 s.is_depend_eos=True and
    #                 h.employee_id in %s
    #             group by h.employee_id""", (tuple(record.ids),))
    #
    #         res = record._cr.dictfetchall()
    #         for re in res:
    #             record.browse(re['id']).total_eos_leaves = -re['days']
