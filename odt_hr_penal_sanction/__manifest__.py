# -*- coding: utf-8 -*-
{
    'name': "Penal Sanction",

    'summary': """
    Penal Sanction
        """,

    'description': """
        Penal Sanction
    """,

    'author': "OdooTec",
    'website': "http://www.odootec.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'hr',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr', 'hr_payroll', 'hr_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/hr_sanction_view.xml',
        'views/hr_contract_view.xml',
        'data/hr_payroll_data.xml',
    ],
}
