# -*- coding: utf-8 -*-
{
    'name': "Compute Leave Balance",

    'summary': """""",

    'description': """
        Long description of module's purpose
    """,

    'author': "OdooTec",
    'website': "http://www.odootec.com",

    'category': 'hr',
    'version': '17.0',

    # any module necessary for this one to work correctly
    'depends': ['hr', 'hr_holidays','account','hr_contract','hr_payroll','odt_hr_leave'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/hr_termination_sequence.xml',
        'views/termination_view.xml',
        'views/hr_payslip.xml',
        'views/hr_holiday.xml',
        'views/report.xml',
        'views/hr_leave_type.xml',
    ],

}
