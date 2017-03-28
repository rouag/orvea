# -*- coding: utf-8 -*-
import datetime
from openerp.osv import osv
from openerp.report import report_sxw
from openerp import fields
from dateutil.relativedelta import relativedelta
from umalqurra.hijri_date import HijriDate


class EmployeeTransfert(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(EmployeeTransfert, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
            'get_setting': self._get_setting,
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

    def _get_setting(self):
        setting_id = self.pool.get('hr.setting').search(self.cr, self.uid, [], limit=1)
        return self.pool.get('hr.setting').browse(self.cr, self.uid, setting_id)


class ReportEmployeeTransfert(osv.AbstractModel):
    _name = 'report.smart_hr.report_hr_employee_transfert'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_hr_employee_transfert'
    _wrapped_report_class = EmployeeTransfert


class EmployeeLend(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(EmployeeLend, self).__init__(cr, uid, name, context=context)
        self.localcontext.update({
            'get_hijri_date': self._get_hijri_date,
            'get_decision_appoint': self._get_decision_appoint,
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

    def _get_decision_appoint(self, employee_id):
        if employee_id:
            decision_appoint_id = self.pool.get('hr.decision.appoint').search(self.cr, self.uid, [('employee_id', '=', employee_id.id), ('is_started', '=', True), ('state_appoint', '=', 'active')], limit=1)
            if decision_appoint_id:
                return self.pool.get('hr.decision.appoint').browse(self.cr, self.uid, decision_appoint_id)
        return None


class ReportEmployeeLend(osv.AbstractModel):
    _name = 'report.smart_hr.report_hr_employee_lend'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_hr_employee_lend'
    _wrapped_report_class = EmployeeLend


class EmployeeAssign(report_sxw.rml_parse):

    def __init__(self, cr, uid, name, context):
        super(EmployeeAssign, self).__init__(cr, uid, name, context=context)
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


class ReportEmployeeAssign(osv.AbstractModel):
    _name = 'report.smart_hr.report_hr_employee_assign'
    _inherit = 'report.abstract_report'
    _template = 'smart_hr.report_hr_employee_assign'
    _wrapped_report_class = EmployeeAssign

