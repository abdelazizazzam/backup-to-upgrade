# -*- coding: utf-8 -*-

from xml.dom import ValidationErr
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    sponsor = fields.Many2one(comodel_name="hr.sponsor", string="Sponsor", required=False, groups="hr.group_hr_user")
    national_id = fields.Char(string="ID", required=False, groups="hr.group_hr_user")
    iqama_number = fields.Char(string="IQAMA", required=False, groups="hr.group_hr_user")
    country_code = fields.Char(string="", required=False, groups="hr.group_hr_user")

    @api.onchange('country_id')
    def _onchange_country_id(self):
        self.country_code = self.country_id.code
        print(self.country_code)

    # @api.constrains("iqama_number", "identification_id")
    # def _check_iqama_number_length(self):
    #     for rec in self:
    #         if rec.country_id.code != "SA":
    #             if (not rec.iqama_number) or  len(rec.iqama_number) != 10:
    #                 raise ValidationError(_("Iqama number must be 10 digits"))
    #         else:
    #             if (not rec.identification_id) or  len(rec.identification_id) != 10:
    #                 raise ValidationError(_("ID number must be 10 digits"))
    
    # @api.constrains("identification_id")
    # def _check_id_number_length(self):
    #     for rec in self:
    #         print("rec", rec)
    #         if len(rec.identification_id) != 10:
    #             raise ValidationError(_("National Id number must be 10 digits"))


# class HrEmployeePublic(models.Model):
#     _inherit = 'hr.employee.public'
#
#     sponsor = fields.Many2one(comodel_name="hr.sponsor", string="Sponsor", required=False)
#     national_id = fields.Char(string="ID", required=False, )
#     iqama_number = fields.Char(string="IQAMA", required=False, )
#     country_code = fields.Char(string="", required=False, )
#     branch_id = fields.Many2one('res.branch', string="Branch", domain="[('company_id', '=', company_id)]")
#
