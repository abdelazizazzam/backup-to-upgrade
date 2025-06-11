from odoo import models, fields, api

class CRMLead(models.Model):
    _inherit = 'crm.lead'

    coverage = fields.Selection([
        ('association', 'الجمعية الخيرية'),
        ('donors', 'المتبرع')
    ], string="التغطية")

    opportunity_no = fields.Char(string='Opportunity No', copy=False, readonly=True, default='New')
    inv_pro_name = fields.Char(string='Individual/ Project name')
    type_inv_pro_name = fields.Selection([
        ('individual', 'Individual'),
        ('project', 'Project')
    ], string="Type")

    @api.model
    def create(self, vals):
        vals['opportunity_no'] = self.env['ir.sequence'].next_by_code('crm.lead') or 'New'
        return super(CRMLead, self).create(vals)

    donor = fields.Char(string="Donor")
    civil_registry_iqama = fields.Char(string="Civil Registry/Iqama")

    full_name = fields.Char(string="الاسم الرباعي", required=True)
    civil_registry = fields.Char(string="السجل المدني / الإقامة")
    nationality = fields.Char(string="الجنسية")
    birth_date = fields.Date(string="تاريخ الميلاد")
    age = fields.Integer(string="العمر")
    personal_email = fields.Char(string="البريد الإلكتروني")
    personal_mobile = fields.Char(string="رقم الجوال")
    gender = fields.Selection([
        ('male', 'ذكر'),
        ('female', 'أنثى')
    ], string="الجنس")
    profession = fields.Selection([
        ('child', 'طفل'),
        ('employee', 'موظف'),
        ('other', 'أخرى')
    ], string="المهنة")
    job_title = fields.Char(string="مسمى الوظيفة")
    education_level = fields.Selection([
        ('illiterate', 'امي'),
        ('primary', 'ابتدائي'),
        ('read_write', 'يقراء ويكنب'),
        ('secondary', 'ثانوي'),
        ('university', 'جامعي'),
        ('other', 'أخرى')
    ], string="المستوى التعليمي")
    emergency_contact_name = fields.Char(string="اسم شخص آخر يمكن الأتصال به")
    emergency_contact_mobile = fields.Char(string="رقم جواله")
    emergency_contact_relation = fields.Char(string="صلة القرابة")

    # ----------------
    marital_status = fields.Selection([
        ('child', 'طفل'),
        ('single', 'أعزب'),
        ('married', 'متزوج'),
        ('divorced', 'مطلق'),
        ('widowed', 'أرمل'),
        ('other', 'أخرى'),
    ], string="الحالة الاجتماعية")
    family_members = fields.Char(string="عدد أفراد الأسرة")
    working_members = fields.Char(string="عدد الأفراد العاملين")
    students = fields.Char(string="عدد الطلاب")
    primary_provider = fields.Selection([
        ('self', 'مقدم الطلب نفسه'),
        ('other', 'غيره')
    ], string="المعيل الأساسي")
    provider_name = fields.Char(string="اسم المعيل")
    provider_relation = fields.Char(string="صلة القرابة")
    # ____________
    residence_area = fields.Selection([
        ('central', 'الوسطى'),
        ('north', 'الشمالية'),
        ('south', 'الجنوبية')
    ], string="منطقة السكن")
    residence_city = fields.Char(string="مدينة السكن")
    residence_district = fields.Char(string="الحي")
    residence_type = fields.Selection([
        ('villa', 'فيلا'),
        ('apartment', 'شقة'),
        ('other', 'أخرى')
    ], string="نوع السكن")
    residence_ownership = fields.Selection([
        ('owned', 'ملك'),
        ('rented', 'إيجار'),
        ('other', 'أخرى')
    ], string="ملكية السكن")
    annual_rent = fields.Float(string="الإيجار السنوي إن وجد")
    annual_rent_doc = fields.Binary(string="عقد الإيجار السنوي")
    annual_rent_doc_name = fields.Char()

    # --
    income_source = fields.Selection([
        ('salary', 'راتب شهري'),
        ('social', 'ضمان اجتماعب'),
        ('bouns', 'مكافأة جامعية'),
        ('help', 'اعانه خيرية'),
        ('account', 'حساب مواطن'),
        ('account', 'حساب مواطن'),
        ('free', 'اعمال تحاريه او حره'),
        ('other', 'أخرى')
    ], string="مصدر الدخل")
    monthly_income = fields.Float(string="الدخل الشهري لك أو لمن يعولك")
    income_doc = fields.Binary(string="اثبات الدخل الشهرى")
    income_doc_name = fields.Char()

    # تفاصيل القروض
    loan_purpose_1 = fields.Char(string="الغرض من القرض ١")
    loan_amount_1 = fields.Char(string="مبلغ القرض الكلي ١")
    loan_monthly_payment_1 = fields.Char(string="مبلغ السداد الشهري ١")
    loan_remaining_payments_1 = fields.Char(string="عدد الدفعات المتبقية ١")
    loan_attachment_1 = fields.Binary(string="مرفق ١")
    loan_attachment_1_name = fields.Char(string="")


    loan_purpose_2 = fields.Char(string="الغرض من القرض ٢")
    loan_amount_2 = fields.Char(string="مبلغ القرض الكلي ٢")
    loan_monthly_payment_2 = fields.Char(string="مبلغ السداد الشهري ٢")
    loan_remaining_payments_2 = fields.Char(string="عدد الدفعات المتبقية ٢")
    loan_attachment_2 = fields.Binary(string="مرفق ٢")
    loan_attachment_2_name = fields.Char(string="")

    loan_purpose_3 = fields.Char(string="الغرض من القرض ٣")
    loan_amount_3 = fields.Char(string="مبلغ القرض الكلي ٣")
    loan_monthly_payment_3 = fields.Char(string="مبلغ السداد الشهري ٣")
    loan_remaining_payments_3 = fields.Char(string="عدد الدفعات المتبقية ٣")
    loan_attachment_3 = fields.Binary(string="مرفق ٣")
    loan_attachment_3_name = fields.Char(string="")


    loan_purpose_4 = fields.Char(string="الغرض من القرض ٤")
    loan_amount_4 = fields.Char(string="مبلغ القرض الكلي ٤")
    loan_monthly_payment_4 = fields.Char(string="مبلغ السداد الشهري ٤")
    loan_remaining_payments_4 = fields.Char(string="عدد الدفعات المتبقية ٤")
    loan_attachment_4 = fields.Binary(string="مرفق ٤")
    loan_attachment_4_name = fields.Char(string="")

    # -----------------------
    health_status = fields.Selection([
        ('emergency', 'طارئة'),
        ('normal', 'عادية')
    ], string="الحالة الصحية")

    insurance_exists = fields.Selection([
        ('yes', 'يوجد'),
        ('no', 'لا يوجد')
    ], string="هل يوجد تأمين")


    insurance_doc = fields.Binary(string="وثيقة التامين الطبى")
    insurance_doc_name = fields.Char()

    insurance_coverage = fields.Float(string="نسبة تغطية التأمين")
    # required_action = fields.Selection([
    #     ('operation', 'عملية'),
    #     ('medication', 'أدوية'),
    #     ('other', 'جهاز')
    # ], string="الأجراء المطلوب")

    required_action = fields.Many2one('procedure', string="الأجراء المطلوب")

    medical_condition_description = fields.Text(string="وصف الحالة الطبية")
    other_diseases = fields.Text(string="أمراض اخرى")
    body_mass_index = fields.Float(string="كتلة الجسم")
    chronic_diseases = fields.Text(string="الأمراض المزمنة")
    recent_medical_report = fields.Binary(string="تقرير طبي حديث بصيغة")
    recent_medical_report_name = fields.Char()
    national_id_image = fields.Binary(string="الهوية الوطنية")
    national_id_image_name = fields.Char()
    notes = fields.Text(string="ملاحظة")
    # ----------------

    phone_number = fields.Char(string="Phone Number")
    other_contacts = fields.Text(string="Other Contacts")
    contact_phone_number = fields.Char(string="Contact Phone Number")
    contact_relation = fields.Char(string="Contact Relation")
    requested_procedure = fields.Char(string="Requested Procedure")
    medical_description = fields.Text(string="Medical Description")

    @api.onchange('civil_registry')
    def change_civil_registry(self):
        for i in self:
            i.name = i.civil_registry


class ResCountry(models.Model):
    _inherit = 'res.country'

    is_priority = fields.Boolean(string='Show on Top', default=False)
