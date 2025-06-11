{
    'name': 'Enterprise Open HRMS Overtime',
    'version': '17.0',
    'summary': 'Manage Employee Overtime',
    'description': """
        Helps you to manage Employee Overtime.
        """,
    'category': 'Generic Modules/Human Resources',
    'author': "Mustafa Elian",
    'depends': [
        'hr', 'hr_contract', 'hr_attendance', 'hr_holidays', 'project', 'hr_payroll',
    ],
    'external_dependencies': {
        'python': ['pandas']
    },
    'data': [
        'data/overtime_activity.xml',
        'data/e_data.xml',

        'security/security.xml',
        'security/ir.model.access.csv',

        'views/e_overtime_request_view.xml',
        'views/e_overtime_type.xml',
        'views/e_hr_contract.xml',
        'views/e_hr_payslip.xml',

    ],
    'demo': ['data/e_hr_overtime_demo.xml'],
    'images': ['static/description/banner.png'],
    'license': 'OPL-1',
    'installable': True,
    'auto_install': False,
    'application': True,
}
