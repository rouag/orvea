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
            'get_salary_net': self._get_salary_net,


        })

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
        print deduction_ids
        return deduction_ids

    def _get_sum_allowances(self, line_ids):
        sum = 0
        for line in line_ids:
            if line.category == 'allowance':
                sum += line.amount
        return sum

    def _get_sum_deductions(self, line_ids):
        sum = 0
        for line in line_ids:
            if line.category == 'deduction':
                sum += line.amount
        return sum
    
    def _get_salary_net(self, line_ids):
        sum = 0
        for line in line_ids:
            if line.category == 'salary_net':
                sum = line.amount
        return sum
    
    
    
    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day))
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
            'get_sum_allowances': self._get_sum_allowances,
            'get_sum_deductions': self._get_sum_deductions,
            'get_salary_net': self._get_salary_net,
            'get_total_allowances': self._get_total_allowances,
            'get_total_deductions': self._get_total_deductions,
            'get_total_salary_net': self._get_total_salary_net,
            'get_all_types': self._get_all_types,
            'get_all_employees': self._get_all_employees,



        })

    def _get_all_types(self):
        type_pbj = self.pool.get('salary.grid.type')
        search_ids = type_pbj.search(self.cr, self.uid, [])
        return type_pbj.browse(self.cr, self.uid, search_ids)

    def _get_all_employees(self, type_id, slip_ids):
        payslip = []
        for rec in slip_ids:
            if rec.employee_id.type_id.id == type_id:
                payslip.append(rec)
        return payslip


    def _get_sum_allowances(self, line_ids):
        sum = 0
        for rec in line_ids:
            if rec.category == 'allowance':
                    sum += rec.amount
        return sum

    def _get_sum_deductions(self, line_ids):
        sum = 0
        for rec in line_ids:
            if rec.category == 'deduction':
                    sum += rec.amount
        return sum

    def _get_salary_net(self, line_ids):
        sum = 0
        for line in line_ids:
            if line.category == 'salary_net':
                sum += line.amount
        return sum

    def _get_total_allowances(self, type_id , slip_ids):
        total = 0
        for line in slip_ids :
            if line.employee_id.type_id.id == type_id:
                sum = 0
                for rec in line.line_ids:
                    if rec.category == 'allowance':
                        sum += rec.amount
                total = total + sum
        return total

    def _get_total_deductions(self,type_id, slip_ids):
        total = 0
        for line in slip_ids :
            if line.employee_id.type_id.id == type_id:
                sum = 0
                for rec in line.line_ids:
                    if rec.category == 'deduction':
                        sum += rec.amount
                total = total + sum
        return total

    def _get_total_salary_net(self, type_id,slip_ids):
        total = 0
        for line in slip_ids :
            if line.employee_id.type_id.id == type_id:
                sum = 0
                for rec in line.line_ids:
                    if rec.category == 'salary_net':
                        sum += rec.amount
                total = total + sum
        return total
    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day))
        return None


class PayslipExtensionReport(osv.AbstractModel):
    _name = 'report.smart_hr.report_payslip_extension'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_payslip_extension'
    _wrapped_report_class = ReportPayslipExtension

class ReportHrErrorEmployee(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ReportHrErrorEmployee, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
            'get_all_employees': self._get_all_employees,
            'get_error_employees':self._get_error_employees,
            'get_termination_employees':self._get_termination_employees,

        })

    def _get_all_employees(self, month):

        payslip_pbj = self.pool.get('hr.payslip')
        search_ids = payslip_pbj.search(self.cr, self.uid, [('month','=',month),('salary_net','=',0.0)])
        return payslip_pbj.browse(self.cr, self.uid, search_ids)

    def _get_error_employees(self, month):
        domain = []
        employe_pbj = self.pool.get('hr.employee')
        payslip_pbj = self.pool.get('hr.payslip')
        search_empl_ids = employe_pbj.search(self.cr, self.uid, [('employee_state', '=', 'employee')])
        search_ids = []
        for rec in search_empl_ids:
            temp = payslip_pbj.search(self.cr, self.uid, [('month','=',month),('employee_id','=',rec)])
            search_ids += temp
        domain.append(search_ids)
        payslip_pbj= payslip_pbj.browse(self.cr, self.uid, search_ids)
        emp_ids = [rec.employee_id.id for rec in payslip_pbj]
        emp_ids = set(emp_ids)
        result=[]
        result = set(search_empl_ids) - emp_ids
        return employe_pbj.browse(self.cr, self.uid, list(result))


    def _get_termination_employees(self, month):
        date_from = get_hijri_month_start(HijriDate, Umalqurra,month)
        date_to = get_hijri_month_end(HijriDate, Umalqurra,month)
        domain = []
        termination_pbj = self.pool.get('hr.termination')
        payslip_pbj = self.pool.get('hr.payslip')
        search_empl_ids = termination_pbj.search(self.cr, self.uid, [('date_termination', '>', date_from),('date_termination', '<', date_to)])
        search_ids = []
        for rec in  search_empl_ids:
            temp = payslip_pbj.search(self.cr, self.uid, [('month','=',month),('employee_id','=',rec.employee_id)])
            search_ids += temp
        domain.append(search_ids)
        return payslip_pbj.browse(self.cr, self.uid, domain[0])

    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day))
        return None


class HrErrorEmployeeReport(osv.AbstractModel):
    _name = 'report.smart_hr.report_hr_error_employee'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_hr_error_employee'
    _wrapped_report_class = ReportHrErrorEmployee
    
    
    
