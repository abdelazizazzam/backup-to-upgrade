from odoo import models, fields, api, _, SUPERUSER_ID
from odoo.tools import get_lang


class HrEmployeeBase(models.AbstractModel):
    _inherit = "hr.employee.base"

    sick_start_date = fields.Date(string='Sick Start Date')


    def _compute_on_view(self, lang=False):
        self = self.with_context(lang=lang)
        for rec in self:
            if lang:
                rec.name = rec.get_original_name(
                    rec.first_name, rec.second_name, rec.third_name, rec.last_name, to_lang=lang
                )
    
    first_name = fields.Char(
        "First Name",
        translate=True,
        required=False,
    )
    second_name = fields.Char(
        "Father Name",
        translate=True,
        required=False,
    )
    third_name = fields.Char("Grandfather Name", translate=True, required=False)
    last_name = fields.Char(
        "Last Name",
        translate=True,
        required=False,
    )
    employee_id = fields.Char("Employee ID", copy=False)

    id_number = fields.Integer(string="Employee ID number", required=False, )


    # def init(self):
    #     super(HrEmployeeBase, self).init()
    #     self._update_employee_names()

    @api.model
    def split_name(self, name):
        name = " ".join(name.split(None)) if name else name
        if name:
            parts = name.strip().split(" ", 3)
            if len(parts) < 4:
                for i in range(0, 4 - len(parts)):
                    parts.append(False)

            return {
                "first_name": parts[0],
                "second_name": parts[1],
                "third_name": parts[2],
                "last_name": parts[3],
            }

    @api.model
    def _update_employee_names(self):
        employees = self.env["hr.employee"].search(
            ["|", ("first_name", "=", " "), ("first_name", "=", False)]
        )
        for ee in employees:
            names = self.split_name(ee.name)
            if names:
                ee.write(names)

    def _firstname_default(self):
        return " " if self.env.context.get("module") else False

    @api.model
    def name_search(self, name, args=None, operator="ilike", limit=100):
        if args is None:
            args = []
        if name:
            actions = self.search(
                ["|", ("employee_id", operator, name), ("name", operator, name)] + args,
                limit=limit,
            )
            return actions.name_get()
        return super(HrEmployeeBase, self).name_search(
            name, args=args, operator=operator, limit=limit
        )

    _sql_constraints = [
        (
            "employee_id_uniq",
            "CHECK(1=1)",
            "The Employee Code must be unique!",
        )
    ]

    @api.onchange("first_name", "second_name", "third_name", "last_name")
    def _onchange_name(self):
        self.name = self.get_original_name(
            self.first_name, self.second_name, self.third_name, self.last_name
        )

    def get_original_name(self, first_name, second_name, third_name, last_name, to_lang=False):
        if not to_lang:
            self = self.with_context(lang=get_lang(self.env).code)
        else:
            self = self.with_context(lang=to_lang)
        name = ""
        if first_name:
            name = first_name
        if second_name:
            name += " " + second_name
        if third_name:
            name += " " + third_name
        if last_name:
            name += " " + last_name
        return name
    
    @api.model
    def create(self, values):
        if values.get("employee_id", False):
            if values["employee_id"].isnumeric():
                values["id_number"] = int(values["employee_id"])
            else:
                values["id_number"] = 0
        else:
            self._cr.execute(
                '''SELECT id_number
                FROM hr_employee
                Where id_number is not null
                Order By id_number DESC
                Limit 1
                ''')
            res_list = self._cr.fetchall()
            if res_list and res_list[0][0]:
                new_emp_id = res_list[0][0] + 1
                values["id_number"] = new_emp_id
                values["employee_id"] = str(new_emp_id)
            else:
                values["id_number"] = 1
                values["employee_id"] = "1"
        res = super(HrEmployeeBase, self).create(values)
        res.name = self.get_original_name(
            res.first_name, res.second_name, res.third_name, res.last_name
        )
        if res.user_id:
            partner = res.user_id.partner_id
            res.private_street = partner.id
        # else: #TODO put it back
        #     partner = self.env['res.partner'].sudo().create(
        #         {'name': res.name})
        #     res.address_home_id = partner.id
        # if values.get("employee_id", "New") == "New":
        #     res.employee_id = self.env["ir.sequence"].next_by_code("hr.employee.id") or "New"
        return res

    def write(self, vals):
        for record in self:
            vals["name"] = self.get_original_name(
                vals.get("first_name", record.first_name),
                vals.get("second_name", record.second_name),
                vals.get("third_name", record.third_name),
                vals.get("last_name", record.last_name),
            )
            if vals.get("employee_id", False):
                if vals["employee_id"].isnumeric():
                    vals["id_number"] = int(vals["employee_id"])
                else:
                    vals["id_number"] = 0
            return super(HrEmployeeBase, self).write(vals)

class User(models.Model):
    _inherit = 'res.users'

    def write(self, vals):
        res =  super().write(vals)
        lang = vals.get('lang')
        if lang:
            emps = self.env['hr.employee'].search([])
            for emp in emps:
                emp._compute_on_view(lang=lang)
        return res