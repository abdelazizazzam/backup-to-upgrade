# -*- coding: utf-8 -*-
##############################################################################


{
    'name': 'Hr Loan',
    'version': '17.0',
    'category': 'HR',
    'author': 'odootec',
    'website': 'http://www.odootec.com',
    'description': """
        Manage loan of employees.
        Loan will deduct from salary
    """,

    'author': 'MNP',
    'depends': ['base','hr', 'hr_payroll', 'account','odt_end_of_service'],

    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'wizard/loan_payment_view.xml',
        'views/loan.xml',
        'wizard/mass_delay.xml',
        'data/loan_sequence.xml',
        'data/hr_payroll_loan_data.xml',

    ],
    'installable': True,
}
