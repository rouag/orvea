# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.addons.smart_base.util.time_util import float_time_convert


class ResumeHoldaysReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ResumeHoldaysReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_lines': self._get_lines,
            'format_time': self._format_time,
            'get_current_date': self._get_current_date,
        })

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
        domain = [('date', '>=', date_from), ('date', '<=', date_to), ('state', '=', 'done')]
        if employee_id:
            domain.append(('employee_id', '=', employee_id))
       
        holidays_obj = self.pool.get('hr.holidays')
        summary_ids = holidays_obj.search(self.cr, self.uid, domain)
        return holidays_obj.browse(self.cr, self.uid, summary_ids)


class ReportResumeHolidays(osv.AbstractModel):
    _name = 'report.smart_hr.report_resume_holidays'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_resume_holidays'
    _wrapped_report_class = ResumeHoldaysReport
