# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from openerp import fields
from dateutil.relativedelta import relativedelta
from umalqurra.hijri_date import HijriDate


class DateHijriParser(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(DateHijriParser, self).__init__(cr, uid, name, context=context)
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
            return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day))
        return None


class ReportEmployeeTransfert(osv.AbstractModel):
    _name = 'report.smart_hr.report_hr_employee_transfert'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_hr_employee_transfert'
    _wrapped_report_class = DateHijriParser


class ReportEmployeeLend(osv.AbstractModel):
    _name = 'report.smart_hr.report_hr_employee_lend'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_hr_employee_lend'
    _wrapped_report_class = DateHijriParser
