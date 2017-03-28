# -*- coding: utf-8 -*-

import time
from openerp import api, fields, models, _
from datetime import datetime, timedelta, time
from openerp.exceptions import ValidationError
from umalqurra.hijri_date import HijriDate
from openerp.addons.smart_base.util.time_util import float_time_convert
from openerp.addons.smart_base.util.time_util import time_float_convert
from openerp.addons.smart_base.util.time_util import float_time_convert_str
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri import Umalqurra



class WizardErrorEmployee(models.TransientModel):
    _name = 'wizard.error.employee'

    @api.multi
    def get_default_period_id(self):
        month = get_current_month_hijri(HijriDate)
        date = get_hijri_month_start(HijriDate, Umalqurra, int(month))
        period_id = self.env['hr.period'].search([('date_start', '<=', date),
                                                       ('date_stop', '>=', date),
                                                       ]
                                                      )
        return period_id

    month = fields.Many2one('hr.period', string=u'الفترة', required=1, domain=[('is_open', '=', True)], default=get_default_period_id)
    employee_id = fields.Many2one('hr.employee', string='موظف')
    department_level1_id = fields.Many2one('hr.department', string='الفرع')
    department_level2_id = fields.Many2one('hr.department', string='القسم')
    department_level3_id = fields.Many2one('hr.department', string='الشعبة')
    salary_grid_type_id = fields.Many2one('salary.grid.type', string='الصنف')


    @api.multi
    def print_report(self):
        report_action = self.env['report'].get_action(self, 'smart_hr.report_hr_error_employee')
        data = {'ids': [],'form': self.read([])[0]}
        report_action['data'] = data
        return report_action