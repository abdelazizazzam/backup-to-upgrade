# -*- coding: utf-8 -*-
{
    'name': "OdooTec Employee Name",
    'summary': """ HR Management""",
    'description': """
        Add fields for employee First name, Second name, Third name and Last name.
 """,
    'author': "OdooTec",
    'website': "www.odootec.com",
    'category': 'Hr',
    'version': '17.0',
    'depends': [
        'hr'
    ],
    'data': [
        # 'data/sequence.xml',
        'views/hr_employee_view.xml',

    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': True,
}
