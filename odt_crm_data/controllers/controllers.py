from odoo.http import request, Controller, route
from odoo import http
import base64

class WebFormController(Controller):
    @http.route('/thank-you-page', type='http', auth='public', website=True)
    def thank_you_page(self, **kwargs):
        return request.render('odt_crm_data.thank_you_page')

    @http.route('/webform', auth='public', website=True)
    def web_form(self, **kwargs):
        priority_countries = request.env['res.country'].sudo().with_context(lang='ar_001').search([
            ('is_priority', '=', True)
        ], order='name asc')

        other_countries = request.env['res.country'].sudo().with_context(lang='ar_001').search([
            ('is_priority', '=', False)
        ], order='name asc')

        country_list = []

        country_list.extend([{'id': c.id, 'name': c.name} for c in priority_countries])

        country_list.extend([{'id': c.id, 'name': c.name} for c in other_countries])

        country_list.append({'id': 9999, 'name': 'Other (غير ذلك)'})

        return request.render('odt_crm_data.web_form_crm', {
            'countries': country_list
        })

    @http.route('/test', type='http', auth='public', website=True, methods=['POST'])
    def web_form_submit(self, **post):
        print('------>', post)
        try:
            attachment1 =  request.httprequest.files.get('loan_attachment_1')
            print("==============================================")
            print(attachment1)
            attachment1_data= False
            if attachment1:
                attachment1_data = base64.b64encode(attachment1.read())
                print("==============================================")
                print(attachment1_data)

            attachment2 = request.httprequest.files.get('loan_attachment_2')
            attachment2_data = False
            if attachment2:
                attachment2_data = base64.b64encode(attachment2.read())

            attachment3 = request.httprequest.files.get('loan_attachment_3')
            attachment3_data = False
            if attachment3:
                attachment3_data = base64.b64encode(attachment3.read())

            attachment4 = request.httprequest.files.get('loan_attachment_4')
            attachment4_data = False
            if attachment4:
                attachment4_data = base64.b64encode(attachment4.read())

            income_doc = request.httprequest.files.get('income_doc')
            income_doc_data = False
            if income_doc:
                income_doc_data = base64.b64encode(income_doc.read())

            annual_rent_doc = request.httprequest.files.get('annual_rent_doc')
            annual_rent_doc_data = False
            if annual_rent_doc:
                annual_rent_doc_data = base64.b64encode(annual_rent_doc.read())

            insurance_doc = request.httprequest.files.get('insurance_doc')
            insurance_doc_data = False
            if insurance_doc:
                insurance_doc_data = base64.b64encode(insurance_doc.read())

            recent_medical_report_read = request.httprequest.files.get('recent_medical_report')
            recent_medical_report_data = False
            if recent_medical_report_read:
                recent_medical_report_data = base64.b64encode(recent_medical_report_read.read())

            national_id_image_read = request.httprequest.files.get('national_id_image')
            national_id_image_data = False
            if national_id_image_read:
                national_id_image_data = base64.b64encode(national_id_image_read.read())

            # Getting partner id
            customer_name = post.get('name')
            partner = request.env['res.partner'].sudo().search([('name', '=', customer_name)], limit=1)
            if not partner:
                partner_vals = {'name': customer_name, 'mobile': post.get('mobile')}
                partner = request.env['res.partner'].sudo().create(partner_vals)
                child_partner_vals = {'name' : post.get('contact_name'), 'mobile': post.get('contact_mobile'), 'parent_id': partner.id}
                request.env['res.partner'].sudo().create(child_partner_vals)

            partner_id = partner.id

            # getting the nationality
            nationality = post.get('nationality')
            if nationality == "9999":
                nationality = post.get('other_nationality')

            vals = {
                'name': post.get('national_id') if post.get('national_id') else post.get('name'),
                'personal_email': post.get('email'),
                'partner_id': partner_id,
                'full_name': post.get('name'),
                'civil_registry': post.get('national_id'),
                'nationality': nationality,
                'birth_date': post.get('date') if post.get('date') else False,
                'age': post.get('age'),
                'personal_mobile': post.get('mobile'),
                'gender': post.get('gender'),
                'profession': post.get('profession'),
                'job_title': post.get('job_title'),
                'education_level': post.get('education_level'),
                'emergency_contact_name': post.get('contact_name'),
                'emergency_contact_mobile': post.get('contact_mobile'),
                'emergency_contact_relation': post.get('relation'),

                #     number2
                'marital_status': post.get('marital'),
                'family_members': post.get('family_member'),
                'working_members': post.get('working_member'),
                'students': post.get('students_number'),
                'primary_provider': post.get('primary_provider'),
                'provider_name': post.get('provider_name'),
                'provider_relation': post.get('provider_relation'),

            #     number3
                'residence_area': post.get('residence_area'),
                'residence_city': post.get('residence_city'),
                'residence_district': post.get('residence_district'),
                'residence_type': post.get('residence_type'),
                'residence_ownership': post.get('residence_ownership'),
                'annual_rent': post.get('annual_rent'),
                'annual_rent_doc': annual_rent_doc_data,

            #    number 4
                'income_source': post.get('income_source'),
                'monthly_income': post.get('monthly_income'),
                'income_doc': income_doc_data,

                'loan_purpose_1': post.get('loan_purpose_1'),
                'loan_amount_1': post.get('loan_amount_1'),
                'loan_monthly_payment_1': post.get('loan_monthly_payment_1'),
                'loan_remaining_payments_1': post.get('loan_remaining_payments_1'),
                'loan_attachment_1': attachment1_data,

                'loan_purpose_2': post.get('loan_purpose_2'),
                'loan_amount_2': post.get('loan_amount_2'),
                'loan_monthly_payment_2': post.get('loan_monthly_payment_2'),
                'loan_remaining_payments_2': post.get('loan_remaining_payments_2'),
                'loan_attachment_2': attachment2_data,

                'loan_purpose_3': post.get('loan_purpose_3'),
                'loan_amount_3': post.get('loan_amount_3'),
                'loan_monthly_payment_3': post.get('loan_monthly_payment_3'),
                'loan_remaining_payments_3': post.get('loan_remaining_payments_3'),
                'loan_attachment_3':attachment3_data,

                'loan_purpose_4': post.get('loan_purpose_4'),
                'loan_amount_4': post.get('loan_amount_4'),
                'loan_monthly_payment_4': post.get('loan_monthly_payment_4'),
                'loan_remaining_payments_4': post.get('loan_remaining_payments_4'),
                'loan_attachment_4': attachment4_data,

                # number 5
                'health_status': post.get('health_status'),
                'insurance_exists': post.get('insurance_exists'),
                'insurance_doc': insurance_doc_data,
                'insurance_coverage': post.get('insurance_coverage'),
                'required_action': post.get('required_action'),
                'medical_condition_description': post.get('medical_condition_description'),
                'other_diseases': post.get('other_diseases'),
                'chronic_diseases': post.get('chronic_diseases'),
                'recent_medical_report': recent_medical_report_data,
                'national_id_image': national_id_image_data,
                'notes': post.get('notes'),
                'body_mass_index': float(post.get('body_mass_index')) if post.get('body_mass_index') else 0.0,

            }
            print('vals >>>>>>>>>>>>>>>',vals)

            crm = request.env['crm.lead'].sudo().create(vals)
            print('crm >>>>>>>>>>>>>>',crm)
            return request.render('odt_crm_data.thank_you_page',{})

        except Exception as e:
            print('================> ',e)
            return request.render('odt_crm_data.web_form_crm', {
                'error': str(e),
            })
