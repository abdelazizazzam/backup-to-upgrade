# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
import datetime


class InsuranceWizard(models.TransientModel):
    _name = 'insurance.wizard'

    employee = fields.Many2one('hr.employee', string='الموظف')
    insurance_policy = fields.Many2one('insurance.policy', string='رقم الوثيقة')
    all_company = fields.Boolean(string='الشركة', default=False,
                                 help="Check this box if you wish to have report for the entire company employees.")

    @api.onchange('employee')
    def _onchange_employee(self):
        if self.employee:
            self._cr.execute(
                '''SELECT id, request_type
                FROM insurance_add_delete
                Where emp_id = {employee_id}
                and state = 'done'
                Order By create_date DESC
                Limit 1
                '''.format(employee_id=self.employee.id))
            ins_list = self._cr.fetchall()
            if ins_list:
                ins_type = ins_list[0][1]
                if ins_type == 'add':
                    ins_id = ins_list[0][0]
                    insurance_id = self.env['insurance.add.delete'].browse(ins_id)
                    self.insurance_policy = insurance_id.insurance_policy
                else:
                    self.write({'insurance_policy': ''})
            else:
                self.write({'insurance_policy': ''})

    def do_print(self):
        if self.all_company:
            data = self.print_all_company_report()
            return self.env.ref('odt_hr_insurance.action_report_company_insurances_pdf').report_action(self, data=data)
        else:
            data = self.print_employee_report()
            return self.env.ref('odt_hr_insurance.action_report_insurance_pdf').report_action(self, data=data)

    def print_all_company_report(self):
        # get all insurances for employee and his dependants
        employees_insurances = self.env['insurance.add.delete'].search([
            ('insurance_policy', '=', self.insurance_policy.id),
        ], order='id desc')

        data = {}

        # to keep track of single (last) insurance to each employee
        marked_insurances = []
        insurances = []
        for insurance in employees_insurances:
            if insurance.emp_id.id not in marked_insurances:
                marked_insurances.append(insurance.emp_id.id)
                insurances.append(self.get_insurance_values(insurance))

        data['insurances'] = insurances
        return data

    def print_employee_report(self):
        # get all insurances for employee and his dependants
        employee_insurances = self.env['insurance.add.delete'].search([
            ('emp_id', '=', self.employee.id),
            ('insurance_policy', '=', self.insurance_policy.id),
        ], order='id desc')

        # get all insurance categories for specific employee
        categories = self.env['insurance.add.delete'].search([
            ('emp_id', '=', self.employee.id),
            ('insurance_policy', '=', self.insurance_policy.id),
        ], order='id desc').mapped('medical_insurance_id.name')

        # get dependants insurances and permenantly deleted insurances
        dependants_insurances = self.env['insurance.add.delete'].search([
            ('emp_id', '=', self.employee.id),
            ('insurance_policy', '=', self.insurance_policy.id),
            ('is_dependent', '=', True)
        ], order='id desc')

        data = {}
        stages = []
        total = 0.0
        is_last_category = False
        for index, category in enumerate(categories):
            is_last_category = True if index == 0 else False
            insurances = self.filter_insurances(employee_insurances, category, True, is_last_category)
            stages.append({
                'category': category,
                'name': self.employee.name,
                'insurances': [insurances[-1]] if len(insurances) > 0 else [],
                # take the first date only as he is added with his dependants again
                'dependants': self.filter_insurances(dependants_insurances, category, False, is_last_category),
            })
        data['stages'], total = self.get_insurance_cost(stages)
        data['total'] = total

        return data

    def get_insurance_values(self, insurance):
        self.employee = insurance.emp_id
        cost = self.print_employee_report()['total']
        return {
            'name': insurance.emp_id.name,
            'gender': insurance.emp_id.gender,
            'start_date': self.env['insurance.add.delete'].search(
                [('emp_id', '=', insurance.emp_id.id), ('insurance_policy', '=', self.insurance_policy.id),
                 ], order='id asc', limit=1).request_date,
            'end_date': insurance.request_date if insurance.request_type == 'delete' else 'Present',
            'cost': cost,
            'type': insurance.request_type
        }

    def filter_insurances(self, insurances, category, parent=False, is_last_category=False):
        # get insurances by category
        insurances = insurances.filtered(lambda r: r.medical_insurance_id.name == category)
        data = []
        deleted_insurance = None
        termination_date = None
        total_cost = 0.0
        # if employee
        if parent:
            for index, insurance in enumerate(insurances):
                end_date = deleted_insurance.request_date if deleted_insurance else 'Present'
                if insurance.request_type == 'delete' and is_last_category:
                    # check with sherif if earliest insurance date or first entry
                    return [
                        {
                            'name': self.employee.name,
                            'gender': self.employee.gender,
                            'start_date': insurances[len(insurances) - 1].request_date,
                            'end_date': insurance.request_date,
                            'type': insurance.request_type
                        }
                    ]
                # promoted insurance
                elif insurance.request_type == 'delete':
                    deleted_insurance = insurance

                else:
                    if insurance.request_type == 'add':
                        data.append(
                            {
                                'name': self.employee.name,
                                'gender': self.employee.gender,
                                'start_date': insurances[len(insurances) - 1].request_date,
                                'end_date': deleted_insurance.request_date if deleted_insurance else 'Present',
                                'type': insurance.request_type

                            }
                        )
                        # if dependant
        else:
            for index, insurance in enumerate(insurances):
                # deleted insurance
                if insurance.request_type == 'delete' and is_last_category:
                    termination_date = insurance.request_date
                    for insurance in insurances:
                        if insurance.request_type == 'add':
                            data.append(
                                {
                                    'name': insurance.dependent_ids.mapped('arabic_name')[0],
                                    'relation': insurance.dependent_ids.mapped('relative_relation')[0],
                                    'start_date': insurance.request_date,
                                    'end_date': termination_date,
                                    'type': insurance.request_type
                                }
                            )
                # promoted insurance
                elif insurance.request_type == 'delete':
                    deleted_insurance = insurance

                # other addition in deleted promotion (skip)
                elif insurance.request_type == 'add' and is_last_category and index > 0:
                    continue
                    # added dependants
                else:
                    end_date = deleted_insurance.request_date if deleted_insurance else 'Present'

                    for insurance in insurances:
                        if insurance.request_type == 'add':
                            data.append(
                                {
                                    'name': insurance.dependent_ids.mapped('arabic_name')[0],
                                    'relation': insurance.dependent_ids.mapped('relative_relation')[0],
                                    'start_date': insurance.request_date,
                                    'end_date': end_date,
                                    'type': insurance.request_type
                                }
                            )
        return data

    def get_insurance_cost(self, categories, include_dependants=True):
        # son, daughter, husband, wife, father, mother
        category_total = 0.0
        total = 0.0
        cost = 0.0
        for category in categories:
            category_total = 0.0
            category_id = self.env['insurance.categ'].search([
                ('name', '=', category['category']),
            ], limit=1)

            pricing = self.env['insurance.pricing'].search([
                ('insurance_categ_id', '=', category_id.id),
            ], limit=1)

            # employee cost
            gender = category['insurances'][0]['gender'] if category['insurances'][0]['gender'] else 'male'
            employee_cost = pricing.male_categ_cost if gender == 'male' else pricing.female_categ_cost
            employee_end_date = category['insurances'][0]['end_date'] if category['insurances'][0][
                                                                             'end_date'] != 'Present' else datetime.datetime.now().date()
            category['insurances'][0]['cost'] = round(
                employee_cost * (employee_end_date - category['insurances'][0]['start_date']).days / 365, 2)

            if include_dependants:
                # dependants cost
                for dependant in category['dependants']:
                    if dependant['relation'] == 'son':
                        cost = pricing.male_cost
                    if dependant['relation'] == 'daughter':
                        cost = pricing.female_cost
                    if dependant['relation'] == 'father':
                        cost = pricing.father_cost
                    if dependant['relation'] == 'mother':
                        cost = pricing.mother_cost

                    end_date = dependant['end_date'] if dependant[
                                                            'end_date'] != 'Present' else datetime.datetime.now().date()
                    dependant['cost'] = round(cost * (end_date - dependant['start_date']).days / 365, 2)
                    category_total += dependant['cost']

            category_total += category['insurances'][0]['cost']
            category['category_cost'] = category_total

            total += category_total

        return categories, total
