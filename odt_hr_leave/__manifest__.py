# -*- coding: utf-8 -*-
{
    'name': "HR Leave Configuration and Extend",

    'summary': """
        HR Leave configuration and Extend""",

    'description': """
        HR Leave configuration and Extend
        
    """,

    'author': "OdooTec",
    'website': "https://www.odootec.com",
    'category': 'hr',
    'version': '17.0',

    # any module necessary for this one to work correctly
    'depends': ['hr_holidays','hr_contract'],

    # always loaded
    'data': [
        'views/hr_leave_views.xml',
    ],
}
