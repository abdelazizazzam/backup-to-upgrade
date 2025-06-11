# -*- coding: utf-8 -*-
{
    'name': "Hr Insurance",

    'summary': """ OdooTec HR Insurance""",

    'description': """
        OdooTec HR Insurance
    """,

    'author': "OdooTec",
    'website': "https://www.odootec.com/",

    'category': 'HR',
    'version': '0.1',

    'depends': ['base', 'hr'],

    'data': [
        'security/ir.model.access.csv',
        'data/sequence.xml',
        'data/cron_task.xml',
        'views/categories_insurance.xml',
        'views/insurance_menu_root.xml',
        'views/company_insurance.xml',
        'views/pricing_insurance.xml',
        'views/employee_dependent.xml',
        'views/policy_insurance.xml',
        'views/add_delete_insurance.xml',
        'views/employee_policy.xml',
        'views/promote_insurance.xml',
        # This needs odt_hr_base_but it is not needed in the project
        # 'views/hr_grade_views.xml',
        'views/dependent.xml',
        'report/project_report_pdf_view.xml',
        'wizard/report_wizard.xml',
        'report/report_company_insurances_pdf_view.xml',

    ],

}
