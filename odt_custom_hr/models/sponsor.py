# -*- coding: utf-8 -*-

from odoo import api, fields, models, _


class HrEmployee(models.Model):
    _name = 'hr.sponsor'
    _rec_name = 'name'

    name = fields.Char(string="Sponsor Name", required=True)