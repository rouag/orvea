# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from openerp.addons.smart_base.util.time_util import float_time_convert
from openerp import fields
from umalqurra.hijri_date import HijriDate


class RequestTransferDelayHours(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(RequestTransferDelayHours, self).__init__(cr, uid, name, context=context)
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


class ReportRequestTransferDelayHours(osv.AbstractModel):
    _name = 'report.smart_hr.request_transfer_delay_hours_report'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.request_transfer_delay_hours_report'
    _wrapped_report_class = RequestTransferDelayHours

class RequestTransferAbsenceDays(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(RequestTransferAbsenceDays, self).__init__(cr, uid, name, context=context)
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


class ReportRequestTransferAbsenceDays(osv.AbstractModel):
    _name = 'report.smart_hr.request_transfer_absence_days_report'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.request_transfer_absence_days_report'
    _wrapped_report_class = RequestTransferAbsenceDays
    