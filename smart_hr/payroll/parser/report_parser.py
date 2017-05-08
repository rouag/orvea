# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp.report import report_sxw
from openerp import fields
from dateutil.relativedelta import relativedelta
from umalqurra.hijri_date import HijriDate
from xmllib import _S
from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
import time as time_date
from datetime import datetime
from openerp.addons.smart_base.util.time_util import days_between
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra


class MessierSalaires(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(MessierSalaires, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
            'get_allowances': self._get_allowances,
            'get_deductions': self._get_deductions,
            'get_sum_alowances': self._get_sum_allowances,
            'get_sum_deductions': self._get_sum_deductions,
            'get_basic_salary': self._get_basic_salary,
            'get_salary_net': self._get_salary_net,
            'get_float': self._get_float,


        })

    def _get_float(self, number):
        return format(number, '.2f')

    def _get_basic_salary(self, employee_id):
        salary_grid_id, basic_salary = employee_id.get_salary_grid_id(False)
        return format(basic_salary, '.2f')

    def _get_allowances(self, line_ids):
        allowance_ids = []
        for line in line_ids:
            if line.category == 'allowance':
                allowance_ids.append(line)
        return allowance_ids

    def _get_deductions(self, line_ids):
        deduction_ids = []
        for line in line_ids:
            if line.category == 'deduction':
                deduction_ids.append(line)
        return deduction_ids

    def _get_sum_allowances(self, line_ids):
        sum = 0
        for line in line_ids:
            if line.category == 'allowance':
                sum += line.amount
        return format(sum, '.2f')

    def _get_sum_deductions(self, line_ids):
        sum = 0.0
        for line in line_ids:
            if line.category == 'deduction':
                sum += line.amount
        return format(sum, '.2f')

    def _get_salary_net(self, line_ids):
        sum = 0
        for line in line_ids:
            if line.category == 'salary_net':
                sum = line.amount
        return format(sum, '.2f')

    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.day)).zfill(2) + separator + str(int(hijri_date.month)).zfill(2) + separator + str(int(hijri_date.year))
        return None


class ReportMessierSalaires(osv.AbstractModel):
    _name = 'report.smart_hr.report_hr_messier_salaries'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_hr_messier_salaries'
    _wrapped_report_class = MessierSalaires
    

class ReportPayslipExtension(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ReportPayslipExtension, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
            'get_all_types': self._get_all_types,
            'get_all_employees': self._get_all_employees,
        })

    def _get_all_types(self):
        type_pbj = self.pool.get('salary.grid.type')
        search_ids = type_pbj.search(self.cr, self.uid, [])
        return type_pbj.browse(self.cr, self.uid, search_ids)

    def _get_all_employees(self, type_id, slip_no_zero_ids):
        payslips = []
        for payslip in slip_no_zero_ids:
            if payslip.employee_id.type_id.id == type_id:
                payslips.append(payslip)
        return payslips

    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.day)).zfill(2) + separator + str(int(hijri_date.month)).zfill(2) + separator + str(int(hijri_date.year))
        return None


class PayslipExtensionReport(osv.AbstractModel):
    _name = 'report.smart_hr.report_payslip_extension'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_payslip_extension'
    _wrapped_report_class = ReportPayslipExtension


class ReportPayslipChangement(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ReportPayslipChangement, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
            'get_lines': self._get_lines,
            'get_float': self._get_float,
        })

    def _get_float(self, number):
        return format(number, '.2f')

    def _get_lines(self, slip_ids, month):
        res = []
        for rec in slip_ids:
            if (rec.salary_net - rec.employee_id.net_salary) != 0:
                line_ids = rec.line_ids.search([('slip_id', '=', rec.id), ('category', 'in', ['changing_allowance', 'difference', 'deduction'])])
                res.append({'employee_name': rec.employee_id.display_name,
                            'number': rec.employee_id.number,
                            'department_name': rec.employee_id.department_id.name,
                            'employee_net_salary': rec.employee_id.net_salary,
                            'payslip_net_salary': rec.salary_net,
                            'diff': rec.salary_net - rec.employee_id.net_salary,
                            'payslip_lines': line_ids,
                            })
        return res

    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.day)).zfill(2) + separator + str(int(hijri_date.month)).zfill(2) + separator + str(int(hijri_date.year))
        return None


class PayslipChangementReport(osv.AbstractModel):
    _name = 'report.smart_hr.report_hr_payslip_changement'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_hr_payslip_changement'
    _wrapped_report_class = ReportPayslipChangement
