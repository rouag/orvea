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

class WizardAttendanceSummary(models.TransientModel):
    _name = 'wizard.attendance.summary'

    date_from = fields.Date(string='التاريخ من',  required=1)
    date_to = fields.Date(string='إلى', required=1)
    employee_id = fields.Many2one('hr.employee', string='موظف')
    department_id = fields.Many2one('hr.department', string='قسم')

    #===========================================================================
    # def print_report(self, data):
    #     data = self.pre_print_report(data)
    #     data['form'].update(self.read(['date_from', 'date_to', 'employee_id', 'department_id'])[0])
    #     return self.env['report'].with_context(landscape=True).get_action(self, 'smart_hr.report_attendance_summary', data=data)
    #===========================================================================

    @api.multi
    def print_report(self):
        report_action = self.env['report'].get_action(self, 'smart_hr.report_attendance_summary')
        data = {'ids': [],'form': self.read([])[0]}
        report_action['data'] = data
        return report_action


