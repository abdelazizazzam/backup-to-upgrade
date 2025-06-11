# -*- coding: utf-8 -*-
{
    'name': "Approval level in Vendor bill",

    'summary': "Add approval level in Vendor bill",

    'description': """
       Add approval level in Vendor bill
    """,

    'author': "odootec",

    'category': 'account',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','purchase'],

    # always loaded
    'data': [
        'security/group.xml',

        'data/mail_activity_data.xml',

        'views/account_move_views.xml',
    ],

}

