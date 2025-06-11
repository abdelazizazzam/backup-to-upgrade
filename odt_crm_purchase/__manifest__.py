# -*- coding: utf-8 -*-
{
    'name': "Odootec CRM Purchase",
    'description': """Odootec CRM Purchase""",
    'author': "Odootec: Mustafa Elian",
    'website': 'https://www.odootec.com/',
    'version': '17.1',
    'depends': ['base', 'crm', 'sale_crm', 'purchase', 'account','odt_crm_data'],
    'data': [
        # 'security/ir.model.access.csv',
        'security/group.xml',
        'data/mail_activity_data.xml',

        'views/crm_lead_views.xml',
        'views/purchase_order_views.xml',
        'views/account_move_views.xml',

        'report/purchase_order_report.xml',
    ],
}
