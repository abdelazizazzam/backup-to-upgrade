{
    'name': 'Hr Payroll Customizations',
    'summary': """ Customization for HR Payroll Module """,
    'description': """
    hr custom module
    """,
    'version': '17.0.2.0.0',
    'author': 'Odootec',
    'website': 'http://www.odootec.com',
    'depends': ['hr', 'hr_contract', 'hr_payroll', 'odt_custom_hr', 'hr_payroll_account','hr_contract_sign'],
    'data': [
        'security/ir.model.access.csv',
        'security/hr_payroll_security.xml',
        'views/settlement_view.xml',
        'views/server_action.xml',

    ],
    'installable': True,
}
