# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from openerp import fields
from dateutil.relativedelta import relativedelta
from umalqurra.hijri_date import HijriDate


class MessierSalaires(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(EmployeeTransfert, self).__init__(cr, uid, name, context=context)
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

   

class ReportMessierSalaires(osv.AbstractModel):
    _name = 'report.smart_hr.report_hr_messier_salaries'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_hr_messier_salaries'
    _wrapped_report_class = MessierSalaires

