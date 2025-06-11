# -*- encoding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2013-Present Odootec .
#     (<http://odootec.com>).
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

{
    'name': "Odootec End of Service",
    'version': '17.0',
    'category': 'Hr',
    'description': """Add option to define end of service for termination
    Creation of end of service type.
    """,
    'author': "OdooTec",
    'website': "www.odootec.com",
    "depends": ['base', 'odt_contract_termination_link', 'hr', 'hr_payroll', 'account', 'hr_holidays', 'odt_leave_termination', 'odt_employee_name'],
    "data": [
        'data/hr_payroll_eos_data.xml',
        'views/termination_view.xml',
        'views/hr_termination_sequence.xml',
        'views/hr_employee.xml',
        'views/hr_holidays_view.xml',
        'views/termination_report.xml',
        'views/hr_payroll.xml',
        'security/ir.model.access.csv',
        ],
    "active": False,
    "installable": True,
}
