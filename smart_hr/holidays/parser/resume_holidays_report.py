# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.addons.smart_base.util.time_util import float_time_convert
from openerp import fields
from umalqurra.hijri_date import HijriDate


class ResumeHoldaysReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ResumeHoldaysReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_lines': self._get_lines,
            'get_employee': self._get_employee,
            'get_hijri_date': self._get_hijri_date,
            'get_years':self._get_years,
            'get_recrute_employee':self._get_recrute_employee,
            'get_partie1_employee':self._get_partie1_employee,
        })

    def _get_hijri_date(self, date, separator):
        '''
        convert georging date to hijri date
        :return hijri date as a string value
        '''
        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return  str(int(hijri_date.day))  + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.year))
        return None

    def _get_years(self, date, separator):

        if date:
            date = fields.Date.from_string(date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return str(int(hijri_date.year))
        return None

    def _get_lines(self, data):
        date_from = data['date_from']
        date_to = data['date_to']
        employee_id = data['employee_id'] and data['employee_id'][0] or False
        domain = [('date_from', '<=', date_to), ('date_to', '>=', date_from),('state', 'in',['done','cut'])]
        if employee_id:
            domain.append(('employee_id', '=', employee_id))
        holidays_obj = self.pool.get('hr.holidays')
        summary_ids = holidays_obj.search(self.cr, self.uid, domain)
        partie = len(summary_ids)
        print"partioee",partie
        partie1 = partie/2
        print"partiee",partie1
        print"summary_ids",summary_ids
        if summary_ids:
            return holidays_obj.browse(self.cr, self.uid, summary_ids)
        else:
            return []
    def _get_partie1_employee(self, data):
        summary_ids = self._get_lines(data)
        partie = len(summary_ids)
        print"summary_ids",summary_ids
        partie1 = partie/2
        for rec in summary_ids[partie1] :
            holidays_obj = self.pool.get('hr.holidays').browse(self.cr, self.uid, rec)
        return holidays_obj

    def _get_employee(self, data):
        employee_id = data['employee_id'] and data['employee_id'][0] or False
        emp_obj = self.pool.get('hr.employee').browse(self.cr, self.uid, employee_id)
        return emp_obj

    def _get_recrute_employee(self, data,date, separator):
        employee_id = data['employee_id'] and data['employee_id'][0] or False
        emp_obj = self.pool.get('hr.employee').browse(self.cr, self.uid, employee_id)
        if emp_obj.recruiter_date:
            date = fields.Date.from_string(emp_obj.recruiter_date)
            hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
            return  str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day)) 
        return None


class ReportResumeHolidays(osv.AbstractModel):
    _name = 'report.smart_hr.report_resume_holidays'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_resume_holidays'
    _wrapped_report_class = ResumeHoldaysReport
