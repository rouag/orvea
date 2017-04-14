# -*- coding: utf-8 -*-


from openerp import models, fields, api, tools, _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from openerp.addons.smart_base.util.time_util import days_between
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra
from tempfile import TemporaryFile
import base64
from openerp.exceptions import UserError
from openerp.exceptions import ValidationError


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    error_ids = fields.One2many('hr.payslip.run.error', 'payslip_run_id', string='تقرير الموظفين المسثنين من المسير الجماعي', readonly=1)
   # type_ids = fields.One2many('salary.grid.type', 'typ_id', string='تقرير الموظفين المسثنين من المسير الجماعي', readonly=1)

    @api.multi
    def compute_sheet(self):
        super(HrPayslipRun, self).compute_sheet()
        self.compute_error()

    @api.multi
    def compute_error(self):
        res = self.onchange_department_level()
        all_employees_ids = res['domain']['employee_ids'][0][2]
        employee_not_include_ids = list(set(all_employees_ids) - set(self.employee_ids.ids))
        error_ids = []
        for employee_id in employee_not_include_ids:
            error_ids.append({'payslip_run_id': self.id, 'employee_id': employee_id, 'type': 'not_include'})
        #self
        # موظفين:  تم إيقاف رتبهم
        employee_stop_lines = self.env['hr.payslip.stop.line'].search([('stop_period', '=', True), ('period_id', '=', self.period_id.id), ('payslip_id.state', '=', 'done')])
        employee_stop_ids = [line.payslip_id.employee_id.id for line in employee_stop_lines]
        for employee_id in employee_stop_ids:
            error_ids.append({'payslip_run_id':self.id,'employee_id':employee_id,'type':'stop'})
        # موظفين:  طي القيد
        employee_termination_lines = self.env['hr.termination'].search([('state','=','done'),('date_termination', '>', self.period_id.date_start),('date_termination', '<', self.period_id.date_stop)])
        employee_termination_ids = [line.employee_id.id for line in employee_termination_lines]
        for employee_id in employee_termination_ids:
            error_ids.append({'payslip_run_id':self.id,'employee_id':employee_id,'type':'termination'})

        self.error_ids = error_ids
        return True




class HrPayslipRunError(models.Model):
    _name = 'hr.payslip.run.error'

    payslip_run_id = fields.Many2one('hr.payslip.run', string='المسير', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='الموظف')
    type = fields.Selection([('not_include', u'الموظفين الذين لم يدخلوا الاعداد'),
                             ('termination', u'موظفين:  طي القيد'),
                             ('stop', u'موظفين:  تم إيقاف رتبهم'),
                            ], required=1, string='السبب')
