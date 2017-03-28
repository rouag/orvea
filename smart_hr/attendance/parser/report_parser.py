# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.addons.smart_base.util.time_util import float_time_convert
from openerp import fields
from umalqurra.hijri_date import HijriDate


class AttendanceSummaryReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(AttendanceSummaryReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_lines': self._get_lines,
            'format_time': self._format_time,
            'get_current_date': self._get_current_date,
            'get_hijri_date':self._get_hijri_date,
        })

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


    def _get_current_date(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")

    def _format_time(self, time_float):
        hour, minn = float_time_convert(time_float)
        return '%s:%s' % (str(hour).zfill(2), str(minn).zfill(2))

    def _get_lines(self, data):
        date_from = data['date_from']
        date_to = data['date_to']
        employee_id = data['employee_id'] and data['employee_id'][0] or False
        department_id = data['department_id'] and data['department_id'][0] or False
        domain = [('date', '>=', date_from), ('date', '<=', date_to)]
        if employee_id:
            domain.append(('employee_id', '=', employee_id))
        if department_id:
            domain.append(('department_id', '=', department_id))
        attendance_summary_obj = self.pool.get('hr.attendance.summary')
        summary_ids = attendance_summary_obj.search(self.cr, self.uid, domain)
        return attendance_summary_obj.browse(self.cr, self.uid, summary_ids)


class ReportAttendanceSummary(osv.AbstractModel):
    _name = 'report.smart_hr.report_attendance_summary'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_attendance_summary'
    _wrapped_report_class = AttendanceSummaryReport


class MonthlySummaryReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(MonthlySummaryReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'format_time': self._format_time,
            'get_current_date': self._get_current_date,
            'get_hijri_date':self._get_hijri_date,
        })

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

    def _get_current_date(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")

    def _format_time(self, time_float):
        hour, minn = float_time_convert(time_float)
        return '%s:%s' % (str(hour).zfill(2), str(minn).zfill(2))


class ReportMonthlySummary(osv.AbstractModel):
    _name = 'report.smart_hr.report_monthly_summary'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_monthly_summary'
    _wrapped_report_class = MonthlySummaryReport


class MonthlySummaryReportAll(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(MonthlySummaryReportAll, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'format_time': self._format_time,
            'get_current_date': self._get_current_date,
            'get_hijri_date':self._get_hijri_date,
        })

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
    
    def _get_current_date(self):
        now = datetime.datetime.now()
        return now.strftime("%Y-%m-%d")

    def _format_time(self, time_float):
        hour, minn = float_time_convert(time_float)
        return '%s:%s' % (str(hour).zfill(2), str(minn).zfill(2))


class ReportMonthlySummaryAll(osv.AbstractModel):
    _name = 'report.smart_hr.report_monthly_summary_all'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_monthly_summary_all'
    _wrapped_report_class = MonthlySummaryReportAll
