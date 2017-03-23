# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra


class WizardPayslipChangement(models.TransientModel):
    _name = 'wizard.payslip.changement'
    _description = u'تقرير لحصر الموظفين الذين طرأ تغيير في مسيرهم'

    @api.multi
    def get_default_month(self):
        return get_current_month_hijri(HijriDate)

    month = fields.Selection(MONTHS, string='الشهر', required=1, default=get_default_month)
    department_level1_id = fields.Many2one('hr.department', string='الفرع')
    department_level2_id = fields.Many2one('hr.department', string='القسم')
    department_level3_id = fields.Many2one('hr.department', string='الشعبة')
    salary_grid_type_id = fields.Many2one('salary.grid.type', string='الصنف')
    employee_ids = fields.Many2many('hr.employee', string='الموظفين', required=1)

    @api.onchange('department_level1_id', 'department_level2_id', 'department_level3_id', 'salary_grid_type_id')
    def onchange_department_level(self):
        dapartment_obj = self.env['hr.department']
        employee_obj = self.env['hr.employee']
        department_level1_id = self.department_level1_id and self.department_level1_id.id or False
        department_level2_id = self.department_level2_id and self.department_level2_id.id or False
        department_level3_id = self.department_level3_id and self.department_level3_id.id or False
        employee_ids = []
        dapartment_id = False
        if department_level3_id:
            dapartment_id = department_level3_id
        elif department_level2_id:
            dapartment_id = department_level2_id
        elif department_level1_id:
            dapartment_id = department_level1_id
        if dapartment_id:
            dapartment = dapartment_obj.browse(dapartment_id)
            employee_ids += [x.id for x in dapartment.member_ids]
            for child in dapartment.all_child_ids:
                employee_ids += [x.id for x in child.member_ids]
        result = {}
        if not employee_ids:
            # get all employee
            employee_ids = employee_obj.search([('employee_state', '=', 'employee')]).ids
        # filter by type
        if self.salary_grid_type_id:
            employee_ids = employee_obj.search([('id', 'in', employee_ids), ('type_id', '=', self.salary_grid_type_id.id)]).ids
        result.update({'domain': {'employee_ids': [('id', 'in', list(set(employee_ids)))]}})
        return result

    @api.multi
    def print_report(self):
        report_action = self.env['report'].get_action(self, 'smart_hr.report_hr_payslip_changement')
        data = {'ids': [], 'form': self.read([])[0]}
        report_action['data'] = data
        return report_action
