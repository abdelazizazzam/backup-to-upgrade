# !/usr/bin/env python
# -*- coding: utf-8 -*-
{
    'name': 'Odootec Allowances',
    'version': '17.5',
    'author': 'odootec',
    'description': """
    """,
    'website': 'https://www.odootec.com/',
    'depends': [
        'base',
        'hr',
        'hr_payroll',
        'hr_holidays',
        'odt_hr_loan',

    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/mail_activity_data.xml',
        'data/data.xml',

        'views/hr_employee_views.xml',
        'views/allowance_type_views.xml',
        'views/hr_allowance_views.xml',
    ],
}
