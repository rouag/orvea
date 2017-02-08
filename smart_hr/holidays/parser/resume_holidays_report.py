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
            'get_employee': self._get_employee,
        })

    def _get_lines(self, data):
        date_from = data['date_from']
        date_to = data['date_to']
        employee_id = data['employee_id'] and data['employee_id'][0] or False
        domain = [('date_from', '<=', date_to), ('date_to', '>=', date_from),('state', 'in',['done','cut'])]
        if employee_id:
            domain.append(('employee_id', '=', employee_id))
        holidays_obj = self.pool.get('hr.holidays')
        summary_ids = holidays_obj.search(self.cr, self.uid, domain)
        if summary_ids:
            return holidays_obj.browse(self.cr, self.uid, summary_ids)
        else:
            return []
        
    def _get_employee(self, data):
        employee_id = data['employee_id'] and data['employee_id'][0] or False
        emp_obj = self.pool.get('hr.employee').browse(self.cr, self.uid, employee_id)
        return emp_obj


class ReportResumeHolidays(osv.AbstractModel):
    _name = 'report.smart_hr.report_resume_holidays'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_resume_holidays'
    _wrapped_report_class = ResumeHoldaysReport
