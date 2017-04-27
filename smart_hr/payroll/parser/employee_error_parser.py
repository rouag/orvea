# -*- coding: utf-8 -*-
from openerp.osv import osv
from openerp.report import report_sxw
from umalqurra.hijri_date import HijriDate
from openerp import fields
from openerp.addons.smart_base.util.umalqurra import *


class ReportHrErrorEmployee(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(ReportHrErrorEmployee, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,

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


class HrErrorEmployeeReport(osv.AbstractModel):
    _name = 'report.smart_hr.report_hr_error_employee_run'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_hr_error_employee_run'
    _wrapped_report_class = ReportHrErrorEmployee



    
