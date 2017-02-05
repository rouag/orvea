# -*- coding: utf-8 -*-

import time
from openerp import api, fields, models, _


class WizardResumeHolidays(models.TransientModel):
    _name = 'wizard.resume.holidays'

    date_from = fields.Date(string='التاريخ من', default=lambda *a: time.strftime('%Y-%m-%d'), required=1)
    date_to = fields.Date(string='إلى', default=lambda *a: time.strftime('%Y-%m-%d'), required=1)
    employee_id = fields.Many2one('hr.employee', string='موظف')
   # department_id = fields.Many2one('hr.department', string='قسم')



    @api.multi
    def print_report(self):
        report_action = self.env['report'].get_action(self, 'smart_hr.report_resume_holidays')
        data = {'ids': [],'form': self.read([])[0]}
        report_action['data'] = data
        return report_action

    @api.multi
    def print_report_normal_holidays(self):
        report_action = self.env['report'].get_action(self, 'smart_hr.report_normal_resume_holidays')
        data = {'ids': [],'form': self.read([])[0]}
        report_action['data'] = data
        return report_action