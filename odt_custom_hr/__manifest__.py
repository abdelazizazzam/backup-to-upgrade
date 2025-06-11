{
    'name': 'Hr Customizations',
    'summary': """   """,
    'version': '17.0.7.0.2',
    'description': """
    hr custom module
    """,
    'author': 'Odootec',
    'website': 'http://www.odootec.com',
    'depends': ['base', 'hr', 'hr_contract', 'hr_payroll', 'account', 'odt_contract_termination_link'],
    'data':[
        'security/ir.model.access.csv',
        'views/hr_department.xml',
        'views/hr_job.xml',
        'views/hr_employee_views.xml',
        'views/res_settings_views.xml',
        'views/hr_contract.xml',
        'data/hr_allowance_data.xml',

    ],
    'installable' : True,
}
