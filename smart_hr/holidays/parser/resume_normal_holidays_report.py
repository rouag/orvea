# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.addons.smart_base.util.time_util import float_time_convert


class ResumeNormalHoldaysReport(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ResumeNormalHoldaysReport, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_normal_holiday': self._get_normal_holiday,
            'get_employee': self._get_employee,
            'get_sum_holiday': self._get_sum_holiday,
            'get_current_stock': self._get_current_stock,
        })

    def _get_normal_holiday(self, data):
        date_from = data['date_from']
        date_to = data['date_to']
        employee_id = data['employee_id'] and data['employee_id'][0] or False
        domain = [('date_from', '<=', date_to), ('date_to', '>=', date_from),('state', 'in',['done','cutoff']),
                  ('holiday_status_id','=', self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'smart_hr', 'data_hr_holiday_status_normal')[1])]
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

    def _get_sum_holiday(self, data):
        holidays = self._get_normal_holiday(data)
        sum = 0
        for holiday in holidays:
            sum += holiday.duration
        return sum

    def _get_current_stock(self, data):
        employee_id = data['employee_id'] and data['employee_id'][0] or False
        hol_stock_obj = self.pool.get('hr.employee.holidays.stock')
        holiday_status_normal = self.pool.get('ir.model.data').get_object_reference(self.cr, self.uid, 'smart_hr', 'data_hr_holiday_status_normal')[1]
        holiday_balance = hol_stock_obj.search(self.cr, self.uid,[('employee_id', '=', employee_id),
                                                           ('holiday_status_id', '=', holiday_status_normal),
                                                                         ], limit=1)
        if holiday_balance:
            return hol_stock_obj.browse(self.cr, self.uid, holiday_balance).holidays_available_stock
        else:
            return 0
    
class ReportResumeNormalHolidays(osv.AbstractModel):
    _name = 'report.smart_hr.report_normal_resume_holidays'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_normal_resume_holidays'
    _wrapped_report_class = ResumeNormalHoldaysReport
