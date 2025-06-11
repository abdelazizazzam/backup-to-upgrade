
{
    'name': 'Biotime Integration',
    'version': '0.1',
    'category': 'Attendance',
    'author': 'Odootec',
    "description": """
        Integration with Biotime Attendance
    """,
    'website': 'http://www.odootec.com',
    'depends': ['hr_attendance'],
    'data': [
                'security/ir.model.access.csv',
                'wizard/link_users_wizard.xml',
                'data/biotime_online_sync.xml',
                'views/res_config_settings_views.xml',
                'views/hr_menu.xml',
                'views/hr_employee.xml',
             ],

    'installable': True,

}
