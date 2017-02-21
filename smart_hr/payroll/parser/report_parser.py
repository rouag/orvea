# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from openerp import fields
from dateutil.relativedelta import relativedelta
from umalqurra.hijri_date import HijriDate


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
