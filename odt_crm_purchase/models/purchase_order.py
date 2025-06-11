from odoo import api, Command, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"


    state = fields.Selection(selection_add=[('account', 'المحاسب'),
                                            ('finance_manager', 'المدير مالي'),
                                            ('ceo', 'المدير التنفيذي'), ('purchase', )])




    crm_lead_id = fields.Many2one('crm.lead')

    # ########### related to crm ############
    coverage = fields.Selection([
        ('association', 'الجمعية الخيرية'),
        ('donors', 'المتبرع')
    ], string="التغطية", related='crm_lead_id.coverage')
    donor = fields.Char(string="Donor", related='crm_lead_id.donor')
    donor_name = fields.Char(string="Donor Name", related='crm_lead_id.donor')
    transfer_depart = fields.Char(string="التحويل للقسم")
    inv_pro_name = fields.Char(string='Individual/ Project name',related='crm_lead_id.inv_pro_name')
    type_inv_pro_name = fields.Selection([
        ('individual', 'Individual'),
        ('project', 'Project')
    ], string="Type",related='crm_lead_id.type_inv_pro_name')
    # Primary/ Personal Information
    full_name = fields.Char(string="Full Name", related='crm_lead_id.full_name')
    civil_registry_iqama = fields.Char(string="السجل المدني / الإقامة", related='crm_lead_id.civil_registry')
    age = fields.Integer(string="Age", related='crm_lead_id.age')
    phone_number = fields.Char(string="Phone Number", related='crm_lead_id.personal_email')
    personal_email = fields.Char(string="البريد الإلكتروني",related='crm_lead_id.personal_email')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female')], string="Gender",
                              related='crm_lead_id.gender')
    job_title = fields.Char(string="مسمى الوظيفة"  ,  related='crm_lead_id.job_title')

    other_contacts = fields.Char(string="اسم شخص آخر يمكن الأتصال به", related='crm_lead_id.emergency_contact_name')
    contact_phone_number = fields.Char(string="رقم جواله", related='crm_lead_id.emergency_contact_mobile')
    contact_relation = fields.Char(string="صلة القرابة", related='crm_lead_id.emergency_contact_relation'  )

    nationality = fields.Char(string="الجنسية" ,related='crm_lead_id.nationality' )
    birth_date = fields.Date(string="تاريخ الميلاد", related='crm_lead_id.birth_date' )
    profession = fields.Selection([
        ('child', 'طفل'),
        ('employee', 'موظف'),
        ('other', 'أخرى')
    ], string="المهنة" ,   related='crm_lead_id.profession')
    education_level = fields.Selection([
        ('illiterate', 'امي'),
        ('primary', 'ابتدائي'),
        ('read_write', 'يقراء ويكنب'),
        ('secondary', 'ثانوي'),
        ('university', 'جامعي'),
        ('other', 'أخرى')
    ], string= "المستوى التعليمي" , related='crm_lead_id.education_level' )

    # Economic Information
    requested_procedure = fields.Char(string="Requested Procedure", related='crm_lead_id.requested_procedure')
    medical_description = fields.Text(string="Medical Description", related='crm_lead_id.medical_description')

    # --
    income_source = fields.Selection([
        ('salary', 'راتب شهري'),
        ('social', 'ضمان اجتماعى'),
        ('bouns', 'مكافأة حماعية'),
        ('help', 'اعانه خيرية'),
        ('account', 'حساب مواطن'),
        ('account', 'حساب مواطن'),
        ('free', 'أعمال تجارية او حرة'),
        ('other', 'أخرى')
    ], string="مصدر الدخل",related='crm_lead_id.income_source')
    monthly_income = fields.Float(string="الدخل الشهري لك أو لمن يعولك" ,related='crm_lead_id.monthly_income')
    income_doc = fields.Binary(string="اثبات الدخل الشهرى")
    income_doc_name = fields.Char()

    # تفاصيل القروض
    loan_purpose_1 = fields.Char(string="الغرض من القرض ١" ,related='crm_lead_id.loan_purpose_1')
    loan_amount_1 = fields.Char(string="مبلغ القرض الكلي ١" ,related='crm_lead_id.loan_amount_1')
    loan_monthly_payment_1 = fields.Char(string="مبلغ السداد الشهري ١" ,related='crm_lead_id.loan_monthly_payment_1')
    loan_remaining_payments_1 = fields.Char(string="عدد الدفعات المتبقية ١" ,related='crm_lead_id.loan_remaining_payments_1')
    loan_attachment_1 = fields.Binary(string="مرفق ١")
    loan_attachment_1_name = fields.Char()

    loan_purpose_2 = fields.Char(string= "الغرض من القرض ٢", related='crm_lead_id.loan_purpose_2')
    loan_amount_2 = fields.Char(string="مبلغ القرض الكلي ٢" ,related='crm_lead_id.loan_amount_2')
    loan_monthly_payment_2 = fields.Char(string="مبلغ السداد الشهري ٢"  ,related='crm_lead_id.loan_monthly_payment_2')
    loan_remaining_payments_2 = fields.Char(string="عدد الدفعات المتبقية ٢"  ,related='crm_lead_id.loan_remaining_payments_2')
    loan_attachment_2 = fields.Binary(string="مرفق ٢")
    loan_attachment_2_name = fields.Char()

    loan_purpose_3 = fields.Char(string="الغرض من القرض ٣"  ,related='crm_lead_id.loan_purpose_3')
    loan_amount_3 = fields.Char(string="مبلغ القرض الكلي ٣"  ,related='crm_lead_id.loan_amount_3')
    loan_monthly_payment_3 = fields.Char(string="مبلغ السداد الشهري ٣"  ,related='crm_lead_id.loan_monthly_payment_3')
    loan_remaining_payments_3 = fields.Char(string="عدد الدفعات المتبقية ٣"  ,related='crm_lead_id.loan_remaining_payments_3')
    loan_attachment_3 = fields.Binary(string="مرفق ٣")
    loan_attachment_3_name = fields.Char()

    loan_purpose_4 = fields.Char(string="الغرض من القرض ٤"  ,related='crm_lead_id.loan_purpose_4')
    loan_amount_4 = fields.Char(string="مبلغ القرض الكلي ٤"  ,related='crm_lead_id.loan_amount_4')
    loan_monthly_payment_4 = fields.Char(string="مبلغ السداد الشهري ٤"  ,related='crm_lead_id.loan_monthly_payment_4')
    loan_remaining_payments_4 = fields.Char(string="عدد الدفعات المتبقية ٤"  ,related='crm_lead_id.loan_remaining_payments_4')
    loan_attachment_4 = fields.Binary(string="مرفق ٤")
    loan_attachment_4_name = fields.Char()

    #  Marital status----------------
    marital_status = fields.Selection([
        ('child', 'طفل'),
        ('single', 'أعزب'),
        ('married', 'متزوج'),
        ('divorced', 'مطلق'),
        ('widowed', 'أرمل'),
        ('other', 'أخرى'),
    ], string="الحالة الاجتماعية"  ,related='crm_lead_id.marital_status')
    family_members = fields.Char(string="عدد أفراد الأسرة"  ,related='crm_lead_id.family_members')
    working_members = fields.Char(string="عدد الأفراد العاملين"  ,related='crm_lead_id.working_members')
    students = fields.Char(string="عدد الطلاب"  ,related='crm_lead_id.students')
    primary_provider = fields.Selection([
        ('self', 'مقدم الطلب نفسه'),
        ('other', 'غيره')
    ], string="المعيل الأساسي"  ,related='crm_lead_id.primary_provider')
    provider_name = fields.Char(string="اسم المعيل"  ,related='crm_lead_id.provider_name')
    provider_relation = fields.Char(string="صلة القرابة"  ,related='crm_lead_id.provider_relation')

    # Housing status
    residence_area = fields.Selection([
        ('central', 'الوسطى'),
        ('north', 'الشمالية'),
        ('south', 'الجنوبية')
    ], string="منطقة السكن" ,related='crm_lead_id.residence_area')
    residence_city = fields.Char(string="مدينة السكن" ,related='crm_lead_id.residence_city')
    residence_district = fields.Char(string="الحي" ,related='crm_lead_id.residence_district')
    residence_type = fields.Selection([
        ('villa', 'فيلا'),
        ('apartment', 'شقة'),
        ('other', 'أخرى')
    ], string="نوع السكن" ,related='crm_lead_id.residence_type')
    residence_ownership = fields.Selection([
        ('owned', 'ملك'),
        ('rented', 'إيجار'),
        ('other', 'أخرى')
    ], string="ملكية السكن" ,related='crm_lead_id.residence_ownership')
    annual_rent = fields.Float(string="الإيجار السنوي إن وجد" ,related='crm_lead_id.annual_rent')

    # health
    health_status = fields.Selection([
        ('emergency', 'طارئة'),
        ('normal', 'عادية')
    ], string="الحالة الصحية" ,related='crm_lead_id.health_status')

    insurance_exists = fields.Selection([
        ('yes', 'يوجد'),
        ('no', 'لا يوجد')
    ], string="هل يوجد تأمين" ,related='crm_lead_id.insurance_exists')

    insurance_coverage = fields.Float(string= "نسبة تغطية التأمين" ,related='crm_lead_id.insurance_coverage')
    # required_action = fields.Selection([
    #     ('operation', 'عملية'),
    #     ('medication', 'أدوية'),
    #     ('other', 'جهاز')
    # ], string= "الأجراء المطلوب"  ,related='crm_lead_id.required_action')

    required_action = fields.Char(string="الأجراء المطلوب", related='crm_lead_id.required_action.name')

    medical_condition_description = fields.Text(string="وصف الحالة الطبية" ,related='crm_lead_id.medical_condition_description')
    other_diseases = fields.Text(string="أمراض اخرى" ,related='crm_lead_id.other_diseases')
    body_mass_index = fields.Float(string="كتلة الجسم" ,related='crm_lead_id.body_mass_index')
    chronic_diseases = fields.Text(string= "الأمراض المزمنة" ,related='crm_lead_id.chronic_diseases')
    recent_medical_report = fields.Binary(string="تقرير طبي حديث بصيغة")
    recent_medical_report_name = fields.Char()
    national_id_image = fields.Binary(string="الهوية الوطنية" )
    national_id_image_name = fields.Char()
    notes = fields.Text(string="ملاحظة" ,related='crm_lead_id.notes')

    state_account_date = fields.Date('State Account Date')
    state_finance_manager_date = fields.Date('State Finance Manager Date')
    state_ceo_date = fields.Date('State CEO Date')

    
    def button_confirm(self):
        super().button_confirm()
        for order in self:
            if order.state not in ['draft', 'sent','ceo']:
                continue
            order.order_line._validate_analytic_distribution()
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True

    def action_account(self):
        self.state = 'account'

    def action_finance_manager(self):
        self.state = 'finance_manager'

    def action_ceo(self):
        self.state = 'ceo'


    @api.onchange('crm_lead_id')
    def _onchange_file(self):
        if self.crm_lead_id:
            self.income_doc = self.crm_lead_id.income_doc
            self.income_doc_name = self.crm_lead_id.income_doc_name

            self.loan_attachment_1_name = self.crm_lead_id.loan_attachment_1_name
            self.loan_attachment_1 = self.crm_lead_id.loan_attachment_1

            self.loan_attachment_2_name = self.crm_lead_id.loan_attachment_2_name
            self.loan_attachment_2 = self.crm_lead_id.loan_attachment_2

            self.loan_attachment_3_name = self.crm_lead_id.loan_attachment_3_name
            self.loan_attachment_3 = self.crm_lead_id.loan_attachment_3

            self.loan_attachment_4_name = self.crm_lead_id.loan_attachment_4_name
            self.loan_attachment_4 = self.crm_lead_id.loan_attachment_4

            self.recent_medical_report = self.crm_lead_id.recent_medical_report
            self.recent_medical_report_name = self.crm_lead_id.recent_medical_report_name

            self.national_id_image = self.crm_lead_id.national_id_image
            self.national_id_image_name = self.crm_lead_id.national_id_image_name

    # ----------------
    def get_billing_users(self):
        billing_group = self.env.ref('account.group_account_invoice')

        accountant_group = self.env.ref('account.group_account_user')
        manager_group = self.env.ref('account.group_account_manager')

        billing_users = billing_group.users

        pure_billing_users = billing_users.filtered(
            lambda user: not (
                    user.id in accountant_group.users.ids or
                    user.id in manager_group.users.ids))

        return pure_billing_users

    @api.model
    def create(self, vals):
        po = super(PurchaseOrder, self).create(vals)

        user_id = po.user_id if po.user_id else False
        activity_id = self.env.ref('odt_crm_purchase.mail_activity_rfq_notify')
        if po.crm_lead_id:
            if user_id:
                po.activity_schedule(
                    activity_type_id=activity_id.id,
                    summary="RFQ created",
                    note=f"A new RFQ has been created from an opportunity: {po.name}",
                    user_id=user_id.id,
                    date_deadline=fields.Date.context_today(self)  # Set a deadline (today's date by default)
                )

            billing_users = self.get_billing_users()

            for user in billing_users:
                po.activity_schedule(
                    activity_type_id=activity_id.id,
                    summary="RFQ created",
                    note=f"A new RFQ has been created from an opportunity: {po.name}",
                    user_id=user.id,
                    date_deadline=fields.Date.context_today(self)  # Set a deadline (today's date by default)
                )
        return po


    def write(self, vals):
        print(f'vals: {vals}')
        if 'state' in vals:
            if vals['state'] != self.state:
                if vals['state'] == 'account':
                    vals['state_account_date'] = fields.Date.today()
                if vals['state'] == 'finance_manager':
                    vals['state_finance_manager_date'] = fields.Date.today()
                if vals['state'] == 'ceo':
                    vals['state_ceo_date'] = fields.Date.today()

            for po in self:
                activity_id = self.env.ref('odt_crm_purchase.mail_activity_rfq_notify')
                user_id = po.user_id if po.user_id else False
                if po.crm_lead_id:
                    if user_id:
                        # Schedule an activity
                        po.activity_schedule(
                            activity_type_id=activity_id.id,  # Type of activity, e.g., To-Do
                            summary="Purchase state updated",
                            note=f"The Purchase state has been changed to: {vals.get('state')}",
                            user_id=user_id.id,  # Assign to the current user or specify a different user ID
                            date_deadline=fields.Date.context_today(self)  # Set a deadline (today's date by default)
                        )

                    billing_users = self.get_billing_users()

                    for user in billing_users:
                        po.activity_schedule(
                            activity_type_id=activity_id.id,
                            summary="Purchase state updated",
                            note=f"The Purchase state has been changed to: {vals.get('state')}",
                            user_id=user.id,
                            date_deadline=fields.Date.context_today(self)  # Set a deadline (today's date by default)
                        )
        return super(PurchaseOrder, self).write(vals)


    def _prepare_invoice(self):
        res = super(PurchaseOrder, self)._prepare_invoice()
        res['type_inv_pro_name'] = self.type_inv_pro_name
        res['inv_pro_name'] = self.inv_pro_name
        return res

    def action_create_invoice(self):
        po = super(PurchaseOrder, self).action_create_invoice()

        for order in self:
            activity_id = self.env.ref('odt_crm_purchase.mail_activity_rfq_notify')
            manager_group = self.env.ref('account.group_account_manager')

            for user in manager_group.users:
                order.activity_schedule(
                    activity_type_id=activity_id.id,
                    summary="Bill created from RFQ",
                    note=f"A new bill has been created from an RFQ: {order.name}",
                    user_id=user.id,
                    date_deadline=fields.Date.context_today(self)  # Set a deadline (today's date by default)
                )
            return po