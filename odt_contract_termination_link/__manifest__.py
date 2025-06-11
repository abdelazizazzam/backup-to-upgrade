# -*- coding: utf-8 -*-
{
    'name': "Links Termination and Contracts",

    'summary': """""",

    'description': """
        Long description of module's purpose
    """,

    'author': "OdooTec",
    'website': "http://www.odootec.com",

    'category': 'hr',
    'version': '17.0',

    # any module necessary for this one to work correctly
    'depends': ['base', 'hr_contract'],

    # always loaded
    'data': [
        'views/hr_contract_views.xml',
    ],

}
