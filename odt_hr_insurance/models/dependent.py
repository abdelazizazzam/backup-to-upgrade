from odoo import api, fields, models
from odoo.exceptions import ValidationError
from datetime import datetime


class Dependent(models.Model):
    _name = 'dependent'
    _description = 'Dependent Data'
    _rec_name = 'english_name'

    arabic_name = fields.Char(string="الاسم بالعربية", required=True, )
    english_name = fields.Char(string="English Name", required=True, )
    id_number = fields.Char(string="ID Number", required=True, )
    relative_relation = fields.Selection(string="Relative Relation", required=True,
                                         selection=[('son', 'Son'),
                                                    ('daughter', 'Daughter'),
                                                    ('husband', 'Husband'),
                                                    ('wife', 'Wife'),
                                                    ('father', 'Father'),
                                                    ('mother', 'Mother')])
    date_of_birth = fields.Date(string="Date of Birth", required=True, default=fields.Date.context_today)
    gender = fields.Selection(string="Gender", selection=[('male', 'Male'), ('female', 'Female'), ], required=True, )
    addition_date = fields.Date(string="Addition Date", required=True, default=fields.Date.context_today)
    phone_number = fields.Char(string="Phone Number", required=False, )
    related_employee_id = fields.Many2one(comodel_name="hr.employee", string="Employee")
    insurance_add_id = fields.Many2one(comodel_name="insurance.add.delete", string="Add or Delete insurance")
    has_insurance = fields.Boolean('Has Insurance')
    last_add_insurance = fields.Date('Last Add Insurance Date')
    last_delete_insurance = fields.Date('Last Delete Insurance Date')
    attachment = fields.Binary('Attachment', required=True)
    attachment_link = fields.Text("Docs Link on Drive", required=False, help="Please upload the documents on Google Drive and Paste the Link here.")

    @api.constrains('date_of_birth')
    def max_date_of_birth(self):
        for rec in self:
            if rec.date_of_birth > datetime.date(datetime.today()):
                raise ValidationError('Date of birth must be less than today date !')

    # @api.constrains('addition_date', 'create_date')
    # def max_addition_date(self):
    #     for rec in self:
    #         if rec.addition_date > datetime.date(rec.create_date):
    #             raise ValidationError('Addition date must be less than or equal Transaction date!')
