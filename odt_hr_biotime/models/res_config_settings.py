# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    biotime_url = fields.Char("Biotime URL")
    biotime_token = fields.Char("Biotime Token")
    biotime_user = fields.Char("Biotime User")
    biotime_password = fields.Char("Biotime Password")
    
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        biotime_url = ir_config.get_param('biotime_url')
        biotime_token = ir_config.get_param('biotime_token')
        biotime_user = ir_config.get_param('biotime_user')
        biotime_password = ir_config.get_param('biotime_password')
        res.update(
            biotime_url=biotime_url,
            biotime_token=biotime_token,
            biotime_user=biotime_user,
            biotime_password=biotime_password,
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        ir_config = self.env['ir.config_parameter'].sudo()
        ir_config.set_param("biotime_url", self.biotime_url or "")
        ir_config.set_param("biotime_token", self.biotime_token or "")
        ir_config.set_param("biotime_user", self.biotime_user or "")
        ir_config.set_param("biotime_password", self.biotime_password or "")